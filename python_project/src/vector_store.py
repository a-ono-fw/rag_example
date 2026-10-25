"""
Vector Store Module
Googleの最新多言語テキスト埋め込みモデル（gemini-embedding-001）と
ChromaDBを用いて、ドキュメントチャンクのベクトルインデックス作成・類似度検索を行います。
※ MRL（Matryoshka Representation Learning）により、次元数を3072から768/1536などに柔軟に調整可能です。
※ 大規模ドキュメント時の無料枠レートリミット（100件/分）を回避する安全なバッチ分割登録機構を備えています。
"""

import os
import time
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


def get_embedding_function(
    api_key: Optional[str] = None,
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    output_dimensionality: Optional[int] = 768,
    use_local: bool = True
):
    """
    テキスト埋め込みモデル初期化。
    use_local=True の場合、Google API制限（日次1,000回等）を受けない
    完全ローカルの日本語対応モデル（sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2）を使用します。

    Args:
        api_key: Gemini APIキー (Geminiモデル使用時)
        model_name: 埋め込みモデル名
        output_dimensionality: Gemini MRL出力次元数
        use_local: ローカルモデルを使用するかどうか (デフォルト: True)
    """
    if use_local or "sentence-transformers" in model_name or "multilingual" in model_name:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings

        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True}
        )

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY が設定されていません。Colabのシークレットまたは環境変数で設定してください。")

    kwargs = {}
    if output_dimensionality:
        kwargs["output_dimensionality"] = output_dimensionality

    return GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=key,
        **kwargs
    )


def build_or_load_vector_store(
    chunks: List[Document] = None,
    persist_directory: str = "./chroma_db",
    api_key: Optional[str] = None,
    collection_name: str = "whitepaper_vectors",
    output_dimensionality: int = 768,
    batch_size: int = 10,
    sleep_seconds: float = 3.0
) -> Chroma:
    """
    チャンクからChromaDBのベクトルインデックスを作成、または既存インデックスを読み込みます。
    Google Gemini APIの無料枠レートリミット（TPM/RPM）を回避するため、
    指定サイズ（デフォルト: 10件）の小バッチに分割し、ウェイトと自動リトライ（バックオフ）を挟みながら登録します。
    また、登録済みのチャンク数を検知して未登録分から再開（レジューム）します。
    """
    embeddings = get_embedding_function(
        api_key=api_key,
        model_name="models/gemini-embedding-001",
        output_dimensionality=output_dimensionality
    )

    if chunks and len(chunks) > 0:
        total_chunks = len(chunks)

        # Chromaインスタンスを初期化
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )

        try:
            existing_count = len(vector_store.get()["ids"])
        except Exception:
            existing_count = 0

        if existing_count > 0:
            print(f"[*] 既存の登録済みチャンクを {existing_count}/{total_chunks} 件検出しました。未登録分から再開します。")

        print(f"[*] ChromaDB に全 {total_chunks} 件を {batch_size} 件ずつバッチ登録中 (gemini-embedding-001 / {output_dimensionality}次元)...")

        for i in range(existing_count, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size

            success = False
            retry_count = 0
            while not success:
                try:
                    vector_store.add_documents(batch)
                    processed_count = min(i + len(batch), total_chunks)
                    print(f"  [+] 進捗: {processed_count}/{total_chunks} 件登録完了 (バッチ {batch_num}/{total_batches})")
                    success = True
                    # レートリミット超過を防ぐインターバル
                    if processed_count < total_chunks:
                        time.sleep(sleep_seconds)
                except Exception as e:
                    err_str = str(e).lower()
                    is_rate_limit = any(k in err_str for k in ["429", "resource_exhausted", "resourceexhausted", "quota", "rate"])
                    is_transient = any(k in err_str for k in ["unavailable", "deadline", "timeout", "connection reset", "503", "500"])

                    if (is_rate_limit or is_transient) and retry_count < 10:
                        retry_count += 1
                        wait_sec = 30 * retry_count
                        print(f"  ⏳ レートリミット / 通信制限検知 ({type(e).__name__}): {e}")
                        print(f"  ⏳ {wait_sec}秒待機して自動リトライします... (試行 {retry_count}/10回目)")
                        time.sleep(wait_sec)
                    else:
                        print(f"  ❌ エラーが発生しました: {e}")
                        raise e

        print(f"[+] ベクトルインデックス構築完了: {persist_directory}")
        return vector_store
    else:
        if not os.path.exists(persist_directory):
            raise FileNotFoundError(f"保存済みインデックスが見つかりません: {persist_directory}")
        print(f"[*] 既存の ChromaDB を読み込み中: {persist_directory}")
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        return vector_store


def search_similar_chunks(
    vector_store: Chroma,
    query: str,
    top_k: int = 4
) -> List[Tuple[Document, float]]:
    """
    クエリに類似したチャンクを類似度スコア付きで検索します。
    """
    results = vector_store.similarity_search_with_relevance_scores(query, k=top_k)
    return results
