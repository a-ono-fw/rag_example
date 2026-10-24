"""
Document Loader & Chunking Module
2024年版ものづくり白書（全340ページ、31MB）などの大規模公式白書に最適化されたローダーです。

【1節まるごとだと長すぎる問題への対応】:
白書の1節は数千〜数万文字あり、そのまま1チャンクにするとベクトルが希釈化し検索精度が低下します。
そこで本モジュールでは、
1. 「章・節・タイトル」を正規表現等で検知してメタデータ（階層属性）として保持
2. 各節の内部を意味的なまとまり（600〜800文字、重複150文字）に分割
することで、ピンポイントな検索性と「第1部 第1章 第1節 [p.24]」のような正確な出典追跡を両立します。
"""

import os
import re
from typing import List, Dict, Any, Tuple
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def extract_section_metadata(text: str, current_meta: Dict[str, str]) -> Dict[str, str]:
    """
    白書テキスト中から「第X部」「第X章」「第X節」の見出しを検出してメタデータを更新します。
    """
    updated_meta = current_meta.copy()

    # 第X部 の検出 (例: 第1部 ものづくり基盤技術の現状と課題)
    part_match = re.search(r'(第[一二三四五六七八九十\d]+部\s+[^\n]{2,30})', text)
    if part_match:
        updated_meta["part"] = part_match.group(1).strip()

    # 第X章 の検出 (例: 第1章 我が国ものづくり産業が直面する課題と展望)
    chap_match = re.search(r'(第[一二三四五六七八九十\d]+章\s+[^\n]{2,35})', text)
    if chap_match:
        updated_meta["chapter"] = chap_match.group(1).strip()

    # 第X節 の検出 (例: 第1節 我が国ものづくり産業の現状)
    sec_match = re.search(r'(第[一二三四五六七八九十\d]+節\s+[^\n]{2,35})', text)
    if sec_match:
        updated_meta["section"] = sec_match.group(1).strip()

    return updated_meta


def load_and_chunk_whitepaper(
    pdf_path: str,
    chunk_size: int = 700,
    chunk_overlap: int = 150
) -> Tuple[List[Document], pd.DataFrame]:
    """
    340ページの大規模白書PDFをストリーム読込し、章・節メタデータを付与しながらチャンク分割します。
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"[*] 白書PDFを読み込み中: {pdf_path} ({file_size_mb:.2f} MB)")

    # 1. ページ単位ロード (340ページを順次処理)
    loader = PyPDFLoader(pdf_path)
    raw_pages = loader.load()
    print(f"[+] PDF読み込み完了: 全 {len(raw_pages)} ページ")

    # 2. チャンク分割器の設定
    # 白書の段落区切りや箇条書きを優先して自然な切れ目で分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "、", " ", ""],
        length_function=len
    )

    chunks: List[Document] = []
    chunk_records: List[Dict[str, Any]] = []
    chunk_counter = 0

    current_meta = {
        "part": "第1部 ものづくり基盤技術の現状と課題",
        "chapter": "第1章 我が国ものづくり産業の現状",
        "section": "第1節 概要",
    }

    for page_doc in raw_pages:
        page_num = page_doc.metadata.get("page", 0) + 1
        page_text = page_doc.page_content

        # ページ内から章・節見出しの更新を検知
        current_meta = extract_section_metadata(page_text, current_meta)

        # ページ内テキストをチャンク分割
        page_chunks = text_splitter.split_text(page_text)

        for chunk_text in page_chunks:
            chunk_text_clean = chunk_text.strip()
            if len(chunk_text_clean) < 30:  # 短すぎるゴミ行はスキップ
                continue

            chunk_counter += 1
            metadata = {
                "chunk_id": chunk_counter,
                "page": page_num,
                "part": current_meta.get("part", ""),
                "chapter": current_meta.get("chapter", ""),
                "section": current_meta.get("section", ""),
                "source": os.path.basename(pdf_path),
            }

            doc = Document(page_content=chunk_text_clean, metadata=metadata)
            chunks.append(doc)

            # pandas分析用レコード
            chunk_records.append({
                "chunk_id": chunk_counter,
                "page": page_num,
                "section": current_meta.get("section", "未分類"),
                "char_count": len(chunk_text_clean),
                "preview": chunk_text_clean[:60].replace("\n", " ") + "..."
            })

    df_stats = pd.DataFrame(chunk_records)
    print(f"[+] 階層メタデータ付きチャンク生成完了: 合計 {len(chunks)} チャンク")

    return chunks, df_stats


def summarize_chunk_stats(df_stats: pd.DataFrame) -> Dict[str, Any]:
    """
    pandasを使ってチャンクの統計量や節ごとのチャンク数を集計します。
    """
    if df_stats.empty:
        return {}

    summary = {
        "total_chunks": len(df_stats),
        "total_pages": int(df_stats["page"].nunique()),
        "total_sections": int(df_stats["section"].nunique()),
        "avg_char_count": round(float(df_stats["char_count"].mean()), 1),
        "min_char_count": int(df_stats["char_count"].min()),
        "max_char_count": int(df_stats["char_count"].max()),
        "sections_breakdown": df_stats["section"].value_counts().head(5).to_dict()
    }
    return summary


# 互換用エイリアス
load_and_chunk_pdf = load_and_chunk_whitepaper
summarize_chunk_distribution = summarize_chunk_stats
