"""
RAG Pipeline & QA Module
検索された上位チャンクをコンテキストとして組み立て、
Gemini 2.5 Flash にプロンプトを投入して、
「章・節・ページ番号」を含めた正確な回答を生成します。

検索方式（キーワード検索 / ベクトル検索 / ハイブリッド検索）を切り替えて回答を生成できます。
"""

import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


SYSTEM_PROMPT_TEMPLATE = """あなたは「ものづくり白書（令和5年度ものづくり基盤技術の振興施策）」などの大規模公的文書に基づいて正確に回答する専門リサーチアシスタントです。

以下の【コンテキスト資料】のみを根拠として、ユーザーからの【質問】に分かりやすく論理的に回答してください。
資料に書かれていない内容については推測せず、「資料内に該当する記述が見当たりません」と正直に答えてください。
回答時には、どの章・節・ページの情報を参照したかが明確に伝わるよう、文末や該当段落に [第1章 第1節 p.X] のように参照箇所を必ず明記してください。

【コンテキスト資料】:
{context}

【質問】:
{question}

【回答】:"""


def get_llm(model_name: str = "gemini-3.8-flash", temperature: float = 0.2, api_key: str = None) -> ChatGoogleGenerativeAI:
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY が設定されていません。")
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=key
    )


def format_search_results_with_metadata(search_results: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    検索結果をLLM用テキストと、UI表示用の出典メタデータリストに整形します。
    """
    context_parts = []
    sources_meta = []

    for i, res in enumerate(search_results, 1):
        doc = res["document"]
        meta = doc.metadata
        page_num = meta.get("page", 1)
        chapter = meta.get("chapter", "")
        section = meta.get("section", "")
        chunk_id = meta.get("chunk_id", i)
        content = doc.page_content.strip()

        location_str = f"{chapter} {section} (p.{page_num})" if section else f"p.{page_num}"
        context_parts.append(f"--- [資料 {i} / {location_str} (ChunkID: {chunk_id})] ---\n{content}")

        sources_meta.append({
            "index": i,
            "chapter": chapter,
            "section": section,
            "page": page_num,
            "score": res.get("score", 0.0),
            "search_type": res.get("search_type", ""),
            "kw_rank": res.get("kw_rank"),
            "vec_rank": res.get("vec_rank"),
            "snippet": content[:120].replace("\n", " ") + "..."
        })

    formatted_context = "\n\n".join(context_parts)
    return formatted_context, sources_meta


def answer_question_with_engine(
    query: str,
    search_engine,
    search_mode: str = "hybrid",
    top_k: int = 4,
    llm = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    指定された検索方式（keyword / vector / hybrid）で検索し、Geminiで回答を生成します。
    """
    if llm is None:
        llm = get_llm(api_key=api_key)

    # 1. 検索実行
    if search_mode == "keyword":
        search_results = search_engine.keyword_engine.search(query, top_k=top_k)
    elif search_mode == "vector":
        search_results = search_engine.vector_engine.search(query, top_k=top_k)
    else:  # hybrid
        search_results = search_engine.search(query, top_k=top_k)

    if not search_results:
        return {
            "answer": "該当する資料が見つかりませんでした。別のキーワードでお試しください。",
            "sources": [],
            "search_mode": search_mode
        }

    # 2. フォーマット
    context_str, sources_meta = format_search_results_with_metadata(search_results)

    # 3. プロンプト生成とLLM呼び出し
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    answer_text = chain.invoke({
        "context": context_str,
        "question": query
    })

    return {
        "answer": answer_text,
        "sources": sources_meta,
        "search_mode": search_mode
    }
