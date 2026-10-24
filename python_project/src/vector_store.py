"""
Vector Store Module
Googleの最新多言語テキスト埋め込みモデル（gemini-embedding-001）と
ChromaDBを用いて、ドキュメントチャンクのベクトルインデックス作成・類似度検索を行います。
※ MRL（Matryoshka Representation Learning）により、次元数を3072から768/1536などに柔軟に調整可能です。
"""

import os
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


def get_embedding_function(
    api_key: Optional[str] = None,
    model_name: str = "models/gemini-embedding-001",
    output_dimensionality: Optional[int] = 768
) -> GoogleGenerativeAIEmbeddings:
    """
    Google Geminiの最新テキスト埋め込みモデル初期化

    Args:
        api_key: Gemini APIキー (未指定時は環境変数 GEMINI_API_KEY を使用)
        model_name: 埋め込みモデル名 (デフォルト: 'models/gemini-embedding-001')
        output_dimensionality: MRL出力次元数 (デフォルト: 768。Colabのメモリと速度を最適化)
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY が設定されていません。Colabのシークレットまたは環境変数で設定してください。")

    # MRL対応パラメータ（ライブラリバージョンに応じて引数を渡す）
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
    output_dimensionality: int = 768
) -> Chroma:
    """
    チャンクからChromaDBのベクトルインデックスを作成、または既存インデックスを読み込みます。
    Google Colabでは一時ディレクトリに保存されるため、実行セッション中に高速に再利用できます。
    """
    embeddings = get_embedding_function(
        api_key=api_key,
        model_name="models/gemini-embedding-001",
        output_dimensionality=output_dimensionality
    )

    if chunks and len(chunks) > 0:
        print(f"[*] ChromaDB に {len(chunks)} 件のチャンクをベクトル化・インデックス中 (gemini-embedding-001 / {output_dimensionality}次元)...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
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
