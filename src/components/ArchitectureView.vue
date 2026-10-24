<script setup lang="ts">
import { CheckCircle2, Layers, Cpu, Monitor, FileSpreadsheet, ArrowRight, Search, Zap, Sliders, AlertTriangle } from 'lucide-vue-next';

defineEmits<{
  (e: 'navigate', tab: 'simulator' | 'code' | 'guide'): void;
}>();
</script>

<template>
  <div class="space-y-10">
    <!-- Hero Header -->
    <div class="border-b border-slate-800 pb-8">
      <div class="flex items-center gap-2 text-xs text-slate-400 mb-2 font-mono">
        <span>課題2</span>
        <span>·</span>
        <span>2024年版ものづくり白書 (340ページ・31MB)</span>
        <span>·</span>
        <span>段階的検索アーキテクチャ設計</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">
        検索手法の段階的ロードマップ &amp; 白書チャンキング設計
      </h1>
      <p class="mt-3 text-sm text-slate-300 max-w-3xl leading-relaxed">
        ご相談いただいた「<strong>① キーワード検索 ➔ ② ベクトル検索 ➔ ③ ハイブリッド検索</strong>」の実装順序と、「<strong>1節まるごとだとボリューミーすぎる</strong>」大規模白書特有のチャンク分割課題に対する具体的な設計方針です。
      </p>
    </div>

    <!-- 白書チャンキング課題への回答: 1節がボリューミーな問題の解決策 -->
    <div class="bg-slate-900 border border-amber-500/30 rounded-xl p-6 relative overflow-hidden">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
          <AlertTriangle class="w-5 h-5" />
        </div>
        <div>
          <h2 class="text-base font-bold text-white">
            白書の「1節単位だとボリューミーすぎる」問題の解決方針
          </h2>
          <p class="text-xs text-slate-300 mt-2 leading-relaxed">
            2024年版ものづくり白書（全340ページ）は、<strong>1つの「節」が15〜25ページ（1万〜2万文字以上）</strong>に及ぶことが多く、1節をそのまま1つのチャンクにすると以下の問題が生じます：
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs">
            <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
              <div class="font-bold text-red-400 mb-1">✕ 1節まるごとチャンクの弊害</div>
              <ul class="text-[11px] text-slate-400 space-y-1 list-disc list-inside">
                <li>ベクトルの希釈化（全体の平均値になり、特定の統計や施策名が埋没）</li>
                <li>LLMへの投入トークン数が爆発し、回答精度が低下（ノイズ過多）</li>
              </ul>
            </div>

            <div class="p-3 rounded-lg bg-slate-950 border border-emerald-500/30 text-slate-300">
              <div class="font-bold text-emerald-400 mb-1">◯ 推奨アプローチ：階層メタデータ保持型チャンキング</div>
              <ul class="text-[11px] text-slate-300 space-y-1 list-disc list-inside">
                <li>大枠（第1部 第1章 第1節 見出し）を<strong>メタデータとして記録</strong></li>
                <li>節の中身を意味のある段落・中見出し単位（<strong>600〜800文字、重複150文字</strong>）に細分化</li>
              </ul>
            </div>
          </div>

          <div class="mt-4 p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-300 font-mono flex items-center gap-2">
            <span class="text-emerald-400 font-bold">検索結果の出力イメージ:</span>
            <span>「第1部 第1章 第1節 我が国ものづくり産業の現状 [p.24]」のように正確に逆引き特定可能</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 検索手法の3段階ロードマップ -->
    <div class="space-y-4">
      <h2 class="text-base font-bold text-white flex items-center gap-2">
        <Search class="w-4 h-4 text-sky-400" />
        <span>ご要望の3段階検索アーキテクチャ</span>
      </h2>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 段階 1: キーワード検索 (BM25) -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-bold">STEP 1</span>
              <span class="text-xs text-slate-500">まず実装</span>
            </div>
            <h3 class="text-base font-bold text-white mb-1">キーワード検索 (BM25)</h3>
            <p class="text-xs text-slate-400 leading-relaxed mb-4">
              文書頻度・逆文書頻度を計算するBM25アルゴリズム。<br />
              白書特有の「価格転嫁」「サプライチェーン」「省エネ補助金」などの専門用語・固有名詞をピンポイントで完全一致検索します。
            </p>

            <div class="space-y-1.5 text-xs text-slate-300 border-t border-slate-800 pt-3">
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-sky-400" />
                <span>ライブラリ: <code class="text-sky-300 font-mono">rank-bm25</code></span>
              </div>
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-sky-400" />
                <span>長所: 単語の取りこぼしがゼロ</span>
              </div>
              <div class="flex items-center gap-2 text-slate-400 text-[11px]">
                <span>短所: 「原材料高を取引先に通す」のような言い換えに弱い</span>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500">
            ※ Colab上でC言語依存なしで動く日本語2-gramトークナイザを提供済
          </div>
        </div>

        <!-- 段階 2: ベクトル検索 (ChromaDB + Gemini) -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">STEP 2</span>
              <span class="text-xs text-slate-500">次に実装</span>
            </div>
            <h3 class="text-base font-bold text-white mb-1">ベクトル検索 (Dense Embedding)</h3>
            <p class="text-xs text-slate-400 leading-relaxed mb-4">
              Google最新の多言語対応モデル <code class="text-emerald-300 font-mono">gemini-embedding-001</code> で各チャンクを高次元ベクトル化。<br />
              MRL技術により、本来3072次元のベクトルを768次元へ精度を損なわず圧縮してColab上で高速計算します。単語が一致していなくても意味の近さで検索可能です。
            </p>

            <div class="space-y-1.5 text-xs text-slate-300 border-t border-slate-800 pt-3">
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-emerald-400" />
                <span>ライブラリ: <code class="text-emerald-300 font-mono">chromadb</code></span>
              </div>
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-emerald-400" />
                <span>長所: 抽象的な問いや同義語に対応</span>
              </div>
              <div class="flex items-center gap-2 text-slate-400 text-[11px]">
                <span>短所: 正確な法律名・数値などのピンポイント特定にムラがある</span>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500">
            ※ Colab内の一時ディレクトリでインメモリ高速動作
          </div>
        </div>

        <!-- 段階 3: ハイブリッド検索 (RRF) -->
        <div class="bg-slate-900 border border-sky-500/30 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-bold">STEP 3</span>
              <span class="text-xs text-indigo-400 font-bold">1+2の統合 (最高精度)</span>
            </div>
            <h3 class="text-base font-bold text-white mb-1">ハイブリッド検索 (RRF統合)</h3>
            <p class="text-xs text-slate-400 leading-relaxed mb-4">
              BM25の順位とベクトルの順位を <strong>Reciprocal Rank Fusion (RRF)</strong> で融合。<br />
              「キーワード完全一致」と「意味的類似」の両方で高く評価されたチャンクが最上位に昇格します。
            </p>

            <div class="space-y-1.5 text-xs text-slate-300 border-t border-slate-800 pt-3">
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-indigo-400" />
                <span>アルゴリズム: <code class="text-indigo-300 font-mono">RRF (k=60)</code></span>
              </div>
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-3.5 h-3.5 text-indigo-400" />
                <span>長所: 専門用語と文脈の両面で最高精度を達成</span>
              </div>
              <div class="flex items-center gap-2 text-slate-300 text-[11px]">
                <span>白書のような公式報告書で最も推奨される構成</span>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 text-[10px] text-indigo-400 font-medium">
            ※ 本アプリとColabノートブックで3方式の比較が可能
          </div>
        </div>
      </div>
    </div>

    <!-- 検索手法の比較テーブル -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 class="text-base font-bold text-white mb-4">
        3方式の得意・不得意の比較（なぜハイブリッドが最適なのか）
      </h2>

      <div class="overflow-x-auto rounded border border-slate-800">
        <table class="w-full text-xs text-left text-slate-300">
          <thead class="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono text-[11px]">
            <tr>
              <th class="px-4 py-2.5">検索方式</th>
              <th class="px-4 py-2.5">得意な質問例</th>
              <th class="px-4 py-2.5">不得意な質問例</th>
              <th class="px-4 py-2.5">白書RAGでの評価</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/70 bg-slate-950/40 font-mono text-[11px]">
            <tr class="hover:bg-slate-800/30">
              <td class="px-4 py-3 font-bold text-sky-400">1. キーワード (BM25)</td>
              <td class="px-4 py-3">「価格転嫁率の推移」「GX推進法」など固有ワード</td>
              <td class="px-4 py-3 text-slate-400">「材料高を値段に乗せる方法」など言い換え表現</td>
              <td class="px-4 py-3 text-slate-300">単体では類義語を取りこぼすが、必須の土台</td>
            </tr>
            <tr class="hover:bg-slate-800/30">
              <td class="px-4 py-3 font-bold text-emerald-400">2. ベクトル (Chroma)</td>
              <td class="px-4 py-3">「デジタル化で中小企業が抱える悩みとは？」</td>
              <td class="px-4 py-3 text-slate-400">型番、法律の第X条、特定の略語などの完全一致</td>
              <td class="px-4 py-3 text-slate-300">ニュアンス一致に強いが、専門用語の一致率が劣る</td>
            </tr>
            <tr class="hover:bg-slate-800/30 bg-sky-950/20">
              <td class="px-4 py-3 font-bold text-indigo-400">3. ハイブリッド (RRF)</td>
              <td class="px-4 py-3 text-white">上記の両方（固有名詞＋文脈ニュアンス）</td>
              <td class="px-4 py-3 text-slate-400">なし（計算コストがわずかに増えるのみ）</td>
              <td class="px-4 py-3 text-emerald-400 font-bold">最高スコア。実運用・学習に最も推奨</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Action Button -->
      <div class="mt-6 flex flex-wrap items-center gap-3">
        <button
          @click="$emit('navigate', 'simulator')"
          class="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg text-white bg-sky-600 hover:bg-sky-500 transition-colors"
        >
          <span>ものづくり白書のデータで3方式を比較テストする</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </button>

        <button
          @click="$emit('navigate', 'code')"
          class="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
        >
          <span>更新されたPythonコード・ノートブックを見る</span>
        </button>
      </div>
    </div>
  </div>
</template>
