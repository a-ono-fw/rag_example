"""
Search Engine Module
ユーザーのご要望に合わせた3段階の検索手法を実装しています。

1. キーワード検索 (BM25: Best Matching 25)
   - 「価格転嫁」「サプライチェーン」等の専門用語・固有名詞をピンポイントで完全一致検索
2. ベクトル検索 (Dense Vector Embedding: ChromaDB + gemini-embedding-001)
   - 「原材料高を取引先に反映できているか」等の意味・ニュアンスの類似性で検索
3. ハイブリッド検索 (Hybrid Search: BM25 + Vector via Reciprocal Rank Fusion / RRF)
   - キーワードとベクトルの両方の長所を統合し、ランキング順位を融合して最高精度の結果を返す
"""

import os
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def tokenize_japanese(text: str) -> List[str]:
    """
    外部Cライブラリ（MeCab等）なしでColab上で安定動作する日本語トークナイザー。
    単語（英数字・漢字カタカナ連続）抽出 + 文字バイグラム(2-gram)を組み合わせてBM25の高精度検索を実現。
    """
    clean_text = text.lower()
    # 1. 漢字・カタカナ・アルファベットの単語抽出
    words = re.findall(r'[a-zA-Z0-9]+|[一-龥]{2,}|[ァ-ンヴー]{2,}', clean_text)

    # 2. 文字バイグラム (2文字ごとの組み合わせ) で部分一致・送り仮名揺れに対応
    bigrams = [clean_text[i:i+2] for i in range(len(clean_text) - 1) if not re.match(r'\s', clean_text[i:i+2])]

    tokens = list(set(words + bigrams))
    return tokens if tokens else [clean_text]


class KeywordSearchEngine:
    """1. キーワード検索エンジン (BM25)"""
    def __init__(self, documents: List[Document]):
        self.documents = documents
        print(f"[*] BM25インデックスを作成中 ({len(documents)} チャンク)...")
        self.corpus_tokens = [tokenize_japanese(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print("[+] BM25インデックス作成完了")

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        query_tokens = tokenize_japanese(query)
        doc_scores = self.bm25.get_scores(query_tokens)

        # スコア降順にインデックスをソート
        ranked_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]

        results = []
        for rank, idx in enumerate(ranked_indices, 1):
            score = float(doc_scores[idx])
            if score <= 0.0:  # 全くヒットしないものは除外
                continue
            doc = self.documents[idx]
            results.append({
                "document": doc,
                "score": round(score, 4),
                "rank": rank,
                "search_type": "keyword (BM25)"
            })
        return results


class VectorSearchEngine:
    """2. ベクトル検索エンジン (ChromaDB + Gemini Embeddings)"""
    def __init__(self, vector_store: Chroma):
        self.vector_store = vector_store

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        # similarity_search_with_relevance_scores で 0.0〜1.0 のコサイン類似度を取得
        raw_results = self.vector_store.similarity_search_with_relevance_scores(query, k=top_k)

        results = []
        for rank, (doc, score) in enumerate(raw_results, 1):
            results.append({
                "document": doc,
                "score": round(float(score), 4) if score is not None else 0.0,
                "rank": rank,
                "search_type": "vector (Embedding)"
            })
        return results


class HybridSearchEngine:
    """3. ハイブリッド検索エンジン (Reciprocal Rank Fusion: RRF)"""
    def __init__(self, keyword_engine: KeywordSearchEngine, vector_engine: VectorSearchEngine, rrf_k: int = 60):
        self.keyword_engine = keyword_engine
        self.vector_engine = vector_engine
        self.rrf_k = rrf_k  # RRFの平滑化定数（標準値: 60）

    def search(
        self,
        query: str,
        top_k: int = 4,
        weight_keyword: float = 0.5,
        weight_vector: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        RRF (Reciprocal Rank Fusion) 計算式:
        Score(d) = weight_kw * 1/(k + rank_kw) + weight_vec * 1/(k + rank_vec)
        """
        # 候補プールとして少し多めに取得 (top_k * 2)
        fetch_k = max(top_k * 2, 8)
        kw_results = self.keyword_engine.search(query, top_k=fetch_k)
        vec_results = self.vector_engine.search(query, top_k=fetch_k)

        # ドキュメント一意識別用ハッシュマップ
        doc_scores: Dict[int, Dict[str, Any]] = {}

        # 1. キーワード検索の順位を反映
        for item in kw_results:
            chunk_id = item["document"].metadata.get("chunk_id", hash(item["document"].page_content))
            rank = item["rank"]
            rrf_score = weight_keyword * (1.0 / (self.rrf_k + rank))

            doc_scores[chunk_id] = {
                "document": item["document"],
                "rrf_score": rrf_score,
                "kw_rank": rank,
                "kw_score": item["score"],
                "vec_rank": None,
                "vec_score": None,
            }

        # 2. ベクトル検索の順位を反映 (融合)
        for item in vec_results:
            chunk_id = item["document"].metadata.get("chunk_id", hash(item["document"].page_content))
            rank = item["rank"]
            vec_rrf = weight_vector * (1.0 / (self.rrf_k + rank))

            if chunk_id in doc_scores:
                doc_scores[chunk_id]["rrf_score"] += vec_rrf
                doc_scores[chunk_id]["vec_rank"] = rank
                doc_scores[chunk_id]["vec_score"] = item["score"]
            else:
                doc_scores[chunk_id] = {
                    "document": item["document"],
                    "rrf_score": vec_rrf,
                    "kw_rank": None,
                    "kw_score": None,
                    "vec_rank": rank,
                    "vec_score": item["score"],
                }

        # 3. RRF総合スコアの降順でソート
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x["rrf_score"], reverse=True)[:top_k]

        results = []
        for final_rank, entry in enumerate(sorted_docs, 1):
            results.append({
                "document": entry["document"],
                "score": round(entry["rrf_score"] * 100, 3),  # 表示用に100倍
                "rank": final_rank,
                "kw_rank": entry["kw_rank"],
                "vec_rank": entry["vec_rank"],
                "kw_score": entry["kw_score"],
                "vec_score": entry["vec_score"],
                "search_type": "hybrid (BM25 + Vector RRF)"
            })
        return results
