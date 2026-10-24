"""
Gradio Web UI for Google Colab & Local Execution
2024年版ものづくり白書（全340ページ）などの大規模文書を対象に、
1. キーワード検索 (BM25)
2. ベクトル検索 (ChromaDB)
3. ハイブリッド検索 (BM25 + ベクトル RRF統合)
の3方式をリアルタイムに切り替えて比較検証できる対話チャットボットUIです。
"""

import os
import gradio as gr
import pandas as pd
from document_loader import load_and_chunk_whitepaper, summarize_chunk_stats
from vector_store import build_or_load_vector_store
from search_engine import KeywordSearchEngine, VectorSearchEngine, HybridSearchEngine
from rag_pipeline import answer_question_with_engine, get_llm


class WhitepaperRAGApp:
    def __init__(self):
        self.chunks = []
        self.df_stats = pd.DataFrame()
        self.pdf_path = None
        self.llm = None
        self.keyword_engine = None
        self.vector_engine = None
        self.hybrid_engine = None

    def initialize_system(self, pdf_file, chunk_size, chunk_overlap):
        """
        PDFを読み込み、BM25およびChromaDBのインデックスを構築
        """
        if pdf_file is None:
            if os.path.exists("data/document.pdf"):
                target_path = "data/document.pdf"
            else:
                return "❌ エラー: PDFファイルを選択またはアップロードしてください。", None, gr.update(interactive=False)
        else:
            target_path = pdf_file.name

        try:
            self.pdf_path = target_path
            # 1. 階層メタデータ付きチャンク分割
            self.chunks, self.df_stats = load_and_chunk_whitepaper(
                self.pdf_path,
                chunk_size=int(chunk_size),
                chunk_overlap=int(chunk_overlap)
            )

            # 2. キーワード検索 (BM25) エンジンの初期化
            self.keyword_engine = KeywordSearchEngine(self.chunks)

            # 3. ベクトル検索 (ChromaDB) エンジンの初期化
            vector_store = build_or_load_vector_store(
                chunks=self.chunks,
                persist_directory="./chroma_db",
                collection_name="whitepaper_rag"
            )
            self.vector_engine = VectorSearchEngine(vector_store)

            # 4. ハイブリッド検索エンジンの初期化
            self.hybrid_engine = HybridSearchEngine(self.keyword_engine, self.vector_engine)

            # 5. Gemini LLMの初期化
            self.llm = get_llm(model_name="gemini-2.5-flash")

            summary = summarize_chunk_stats(self.df_stats)
            status_msg = (
                f"✅ インデックス作成完了！\n"
                f"・総ページ数: {summary['total_pages']} ページ / 検出された節数: {summary['total_sections']} 節\n"
                f"・総チャンク数: {summary['total_chunks']} 件 (平均 {summary['avg_char_count']} 文字)\n"
                f"・BM25(キーワード) & ChromaDB(ベクトル) の両インデックスが準備完了しました。"
            )

            preview_df = self.df_stats[["chunk_id", "page", "section", "char_count", "preview"]].head(50)
            return status_msg, preview_df, gr.update(interactive=True)

        except Exception as e:
            return f"❌ 処理中にエラーが発生しました: {str(e)}", None, gr.update(interactive=False)

    def compare_searches(self, query, top_k):
        """
        同一クエリに対して、キーワード検索・ベクトル検索・ハイブリッド検索のヒット結果を一覧比較
        """
        if not self.hybrid_engine:
            return "先にPDFを解析してください。"

        k = int(top_k)
        kw_hits = self.keyword_engine.search(query, top_k=k)
        vec_hits = self.vector_engine.search(query, top_k=k)
        hy_hits = self.hybrid_engine.search(query, top_k=k)

        lines = [f"### 🔍 クエリ: 「{query}」の検索比較 (Top-{k})\n"]

        lines.append("#### 1. キーワード検索 (BM25 - 専門用語完全一致に強い)")
        for h in kw_hits:
            m = h["document"].metadata
            lines.append(f"- **[順位{h['rank']}]** {m.get('chapter', '')} {m.get('section', '')} (p.{m.get('page')}) | スコア: {h['score']:.2f}")
            lines.append(f"  > {h['document'].page_content[:90].replace(chr(10), ' ')}...\n")

        lines.append("\n#### 2. ベクトル検索 (Chroma - 意味的言い換え・類義語に強い)")
        for h in vec_hits:
            m = h["document"].metadata
            lines.append(f"- **[順位{h['rank']}]** {m.get('chapter', '')} {m.get('section', '')} (p.{m.get('page')}) | 類似度: {h['score']:.3f}")
            lines.append(f"  > {h['document'].page_content[:90].replace(chr(10), ' ')}...\n")

        lines.append("\n#### 3. ハイブリッド検索 (RRF統合 - 最高精度)")
        for h in hy_hits:
            m = h["document"].metadata
            kw_r = f"BM25順位:{h['kw_rank']}" if h['kw_rank'] else "BM25未検出"
            vec_r = f"ベクトル順位:{h['vec_rank']}" if h['vec_rank'] else "ベクトル未検出"
            lines.append(f"- **[統合順位{h['rank']}]** {m.get('chapter', '')} {m.get('section', '')} (p.{m.get('page')}) | RRF: {h['score']:.2f} ({kw_r}, {vec_r})")
            lines.append(f"  > {h['document'].page_content[:90].replace(chr(10), ' ')}...\n")

        return "\n".join(lines)

    def chat_response(self, message, history, search_mode_label, top_k):
        """
        指定された検索方式で回答生成
        """
        if not self.hybrid_engine:
            return history + [(message, "⚠️ まず上の『PDFを解析してインデックス作成』を実行してください。")], ""

        if not message.strip():
            return history, ""

        mode_map = {
            "ハイブリッド検索 (BM25 + ベクトル RRF統合) [推奨]": "hybrid",
            "キーワード検索 (BM25)": "keyword",
            "ベクトル検索 (ChromaDB)": "vector"
        }
        mode = mode_map.get(search_mode_label, "hybrid")

        try:
            result = answer_question_with_engine(
                query=message,
                search_engine=self.hybrid_engine,
                search_mode=mode,
                top_k=int(top_k),
                llm=self.llm
            )

            answer = result["answer"]
            sources = result.get("sources", [])

            citations_text = f"\n\n---\n**📚 参照した資料（検索方式: {mode}）:**\n"
            if sources:
                for s in sources:
                    loc = f"{s['chapter']} {s['section']} [p.{s['page']}]" if s.get('section') else f"[p.{s['page']}]"
                    citations_text += f"- **{loc}** (スコア: {s['score']}) — *「{s['snippet']}」*\n"
            else:
                citations_text += "- 関連資料なし\n"

            history.append((message, answer + citations_text))
            return history, ""

        except Exception as e:
            history.append((message, f"❌ 回答生成中にエラーが発生しました: {str(e)}"))
            return history, ""


def create_ui():
    app = WhitepaperRAGApp()

    with gr.Blocks(title="2024年版ものづくり白書 RAG チャットボット") as demo:
        gr.Markdown(
            """
            # 📘 2024年版ものづくり白書 RAG チャットボット (Google Colab)
            **段階的検索アーキテクチャ: ① キーワード検索(BM25) ➔ ② ベクトル検索 ➔ ③ ハイブリッド検索(RRF)**
            
            全340ページの白書から、章・節・ページ番号をメタデータとして保持しながら検索し、Geminiが出典箇所を明記して回答します。
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 1. 設定 & インデックス作成")
                pdf_input = gr.File(
                    label="白書PDF (未選択時は data/document.pdf を使用)",
                    file_types=[".pdf"]
                )
                with gr.Row():
                    chunk_size = gr.Slider(
                        minimum=300, maximum=1500, value=700, step=50,
                        label="チャンク文字数 (推奨: 600〜800)"
                    )
                    chunk_overlap = gr.Slider(
                        minimum=50, maximum=300, value=150, step=25,
                        label="オーバーラップ文字数"
                    )

                search_mode_dropdown = gr.Dropdown(
                    choices=[
                        "ハイブリッド検索 (BM25 + ベクトル RRF統合) [推奨]",
                        "キーワード検索 (BM25)",
                        "ベクトル検索 (ChromaDB)"
                    ],
                    value="ハイブリッド検索 (BM25 + ベクトル RRF統合) [推奨]",
                    label="🔍 検索エンジンの選択"
                )

                top_k_slider = gr.Slider(
                    minimum=1, maximum=10, value=4, step=1,
                    label="参照チャンク件数 (Top-K)"
                )

                build_btn = gr.Button("🚀 白書PDFを解析してインデックス作成", variant="primary")
                status_box = gr.Textbox(label="処理ステータス", interactive=False)

            with gr.Column(scale=2):
                gr.Markdown("### 💬 2. チャット対話 (章・節・ページ出典付き)")
                chatbot = gr.Chatbot(
                    label="対話履歴 (出典付き回答)",
                    height=450,
                    bubble_full_width=False
                )
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="ものづくり白書について質問 (例: 価格転嫁の進捗状況は？ 我が国の製造業DXの課題は？)",
                        label="質問入力",
                        scale=4
                    )
                    send_btn = gr.Button("送信", variant="primary", scale=1)
                clear_btn = gr.Button("チャット履歴クリア")

        with gr.Accordion("🔬 3つの検索方式（キーワード vs ベクトル vs ハイブリッド）の比較検証", open=False):
            gr.Markdown("入力した質問に対して、BM25、ベクトル、ハイブリッドがそれぞれどの節・ページを上位と判定したかを比較できます。")
            compare_query = gr.Textbox(placeholder="比較したいキーワードや質問を入力...", label="比較テストクエリ")
            compare_btn = gr.Button("3方式で同時検索してランキング比較")
            compare_output = gr.Markdown()

        with gr.Accordion("📊 チャンク分析テーブル (pandas DataFrame)", open=False):
            gr.Markdown("章・節見出しがメタデータとして付与された各チャンクの一覧です。")
            df_display = gr.Dataframe(
                headers=["chunk_id", "page", "section", "char_count", "preview"],
                label="チャンク一覧 (先頭50件)"
            )

        # イベントバインド
        build_btn.click(
            fn=app.initialize_system,
            inputs=[pdf_input, chunk_size, chunk_overlap],
            outputs=[status_box, df_display, send_btn]
        )

        send_btn.click(
            fn=app.chat_response,
            inputs=[msg_input, chatbot, search_mode_dropdown, top_k_slider],
            outputs=[chatbot, msg_input]
        )
        msg_input.submit(
            fn=app.chat_response,
            inputs=[msg_input, chatbot, search_mode_dropdown, top_k_slider],
            outputs=[chatbot, msg_input]
        )
        clear_btn.click(lambda: [], None, chatbot)

        compare_btn.click(
            fn=app.compare_searches,
            inputs=[compare_query, top_k_slider],
            outputs=[compare_output]
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=True, debug=True)
