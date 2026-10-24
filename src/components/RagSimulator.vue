<script setup lang="ts">
import { ref, computed } from 'vue';
import { Play, Sparkles, Sliders, FileText, CheckCircle2, AlertCircle, RefreshCw, Search, ArrowRightLeft } from 'lucide-vue-next';

// 2024年版ものづくり白書（令和5年度ものづくり基盤技術の振興施策）の実際の章・節・データに基づく精選抜粋
const SAMPLE_DOCS = [
  {
    id: 'mono_sec1',
    title: '【白書実例】第1部 第1章 第1節 我が国ものづくり産業の現状と課題 (価格転嫁・収益性)',
    text: `第1部 ものづくり基盤技術の現状と課題
第1章 我が国ものづくり産業が直面する課題と展望
第1節 我が国ものづくり産業の現状

1. 業績と収益性の動向
我が国製造業の売上高及び営業利益は、原材料価格の高騰やエネルギーコストの上昇、円安の進行などにより、業種間で二極化が進んでいる。特に中小製造業においては、原材料費や労務費の増加分を適切に取引価格へ反映させる「価格転嫁（マークアップ）」の進捗が最大の経営課題となっている。2023年度の調査によれば、価格転嫁率が5割未満にとどまる企業が全体の約4割を占めており、適正な価格交渉の促進に向けた政府の「価格交渉促進月間」のフォローアップや下請代金支払遅延等防止法（下請法）の厳格な運用が強く求められている。

2. 労働生産性と賃上げの好循環
製造業の労働生産性は過去10年間緩やかな改善傾向にあるものの、主要先進国（OECD諸国）と比較すると依然として伸び悩んでいる。構造的な人手不足が深刻化する中で、持続的な賃上げを実現するためには、単なるコスト削減にとどまらず、付加価値の高い新製品・サービスの開発や、抜本的な業務プロセスの効率化が不可欠である。`,
  },
  {
    id: 'mono_sec2',
    title: '【白書実例】第1部 第1章 第2節 ものづくり分野におけるDXの推進と課題 (デジタル人材・生成AI)',
    text: `第1部 ものづくり基盤技術の現状と課題
第1章 我が国ものづくり産業が直面する課題と展望
第2節 デジタルトランスフォーメーション（DX）の推進

1. 製造現場におけるデジタル技術活用の進展
我が国ものづくり企業におけるデジタル技術の導入は、受発注管理や会計システム等の「守りのIT」から、IoTセンサーを用いた設備の稼働状況モニタリングや予兆保全、3D CADやデジタルツインを活用した設計製造連携といった「攻めのDX」へと移行しつつある。また、近年では熟練技術者のノウハウ伝承や品質検査の自動化において、画像認識AIや生成AI（LLM）の現場適用が急速に検証されている。

2. DX推進を阻むボトルネック
一方で、中小製造業を中心として「DXを推進するための専門人材（ITアーキテクト、データサイエンティスト）の圧倒的不足」が最大の障壁として挙げられている。社内人材のリスキリング（学び直し）支援や、企業間でのデータ連携基盤（ウラノス・エコシステム等の産業データプラットフォーム）への参画が今後の競争力確保の鍵を握っている。`,
  },
  {
    id: 'mono_sec3',
    title: '【白書実例】第1部 第2章 第1節 サプライチェーン強靭化とグリーントランスフォーメーション (GX)',
    text: `第1部 ものづくり基盤技術の現状と課題
第2章 サプライチェーン強靭化とカーボンニュートラルへの対応
第1節 サプライチェーンの強靭化と脱炭素の潮流

1. 地政学リスクと調達先の多様化
半導体不足や重要鉱物の供給途絶リスク、地政学的緊張の高まりを受け、特定国への過度なサプライチェーン依存から脱却し、国内投資の回帰や同志国との強靭なサプライチェーン構築（フレンド・ショアリング）が進展している。経済安全保障推進法に基づく特定重要物資の安定供給確保が急務である。

2. カーボンニュートラル（GX）への対応
2050年カーボンニュートラル目標に向け、Scope 1、Scope 2の直接排出削減のみならず、サプライチェーン全体（Scope 3）における製品ライフサイクル全体のCO2排出量の可視化（CFP: カーボンフットプリント）が国際取引の必須要件となりつつある。省エネルギー設備の導入支援や革新的クリーンエネルギー技術の研究開発投資が加速している。`,
  },
];

const selectedDocId = ref('mono_sec1');
const customText = ref(SAMPLE_DOCS[0].text);
const chunkSize = ref(600);
const chunkOverlap = ref(120);
const searchMode = ref<'hybrid' | 'keyword' | 'vector'>('hybrid');
const query = ref('中小製造業における価格転嫁の現状と直面している課題について教えてください');

const isLoading = ref(false);
const errorMsg = ref('');
const resultData = ref<any>(null);

function selectSample(docId: string) {
  selectedDocId.value = docId;
  const target = SAMPLE_DOCS.find(d => d.id === docId);
  if (target) {
    customText.value = target.text;
  }
}

async function runSimulation() {
  if (!query.value.trim() || !customText.value.trim()) return;
  isLoading.value = true;
  errorMsg.value = '';
  resultData.value = null;

  try {
    const res = await fetch('/api/rag/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query.value,
        documentText: customText.value,
        chunkSize: chunkSize.value,
        chunkOverlap: chunkOverlap.value,
        searchMode: searchMode.value,
      }),
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || 'シミュレーション実行中にエラーが発生しました');
    }
    resultData.value = data;
  } catch (err: any) {
    errorMsg.value = err.message || '通信エラーが発生しました';
  } finally {
    isLoading.value = false;
  }
}

// 簡易ローカルチャンクプレビュー（pandas風データフレーム）
const localChunks = computed(() => {
  const text = customText.value;
  const chunks: Array<{ id: number; page: number; section: string; charCount: number; preview: string }> = [];
  let start = 0;
  let id = 1;
  const size = chunkSize.value;
  const overlap = chunkOverlap.value;
  let currentSection = '第1節 我が国ものづくり産業の現状';

  while (start < text.length) {
    const end = Math.min(start + size, text.length);
    const content = text.substring(start, end).trim();
    const secMatch = content.match(/(第[一二三四五六七八九十\d]+節\s+[^\n]{2,30})/);
    if (secMatch) {
      currentSection = secMatch[1].trim();
    }

    if (content) {
      chunks.push({
        id: id++,
        page: Math.floor(start / 700) + 1,
        section: currentSection,
        charCount: content.length,
        preview: content.slice(0, 50).replace(/\n/g, ' ') + '...',
      });
    }
    start += Math.max(size - overlap, 50);
  }
  return chunks;
});

const statsSummary = computed(() => {
  const chunks = localChunks.value;
  if (!chunks.length) return { count: 0, avg: 0, min: 0, max: 0, sections: 0 };
  const counts = chunks.map(c => c.charCount);
  const sections = new Set(chunks.map(c => c.section)).size;
  return {
    count: chunks.length,
    avg: Math.round(counts.reduce((a, b) => a + b, 0) / counts.length),
    min: Math.min(...counts),
    max: Math.max(...counts),
    sections,
  };
});
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="border-b border-slate-800 pb-6">
      <div class="text-xs text-sky-400 font-mono mb-1">INTERACTIVE 3-STAGE SEARCH BENCH</div>
      <h2 class="text-xl sm:text-2xl font-bold text-white tracking-tight">
        2024年版ものづくり白書 RAG検索シミュレータ
      </h2>
      <p class="text-xs text-slate-400 mt-2 max-w-2xl leading-relaxed">
        <strong>① キーワード検索(BM25) ➔ ② ベクトル検索 ➔ ③ ハイブリッド検索(RRF)</strong> を切り替えながら、ヒット順位の違いや、Geminiがどのように「章・節・ページ」を特定して回答するかを体験できます。
      </p>
    </div>

    <!-- Main Grid: Controls + Document / Results -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left Panel: Settings & Text (5 cols) -->
      <div class="lg:col-span-5 space-y-5">
        <!-- Search Mode Toggle (The Core of User Request) -->
        <div class="bg-slate-900 border border-sky-500/30 rounded-xl p-4 space-y-2">
          <label class="block text-xs font-bold text-white flex items-center justify-between">
            <span class="flex items-center gap-1.5">
              <Search class="w-3.5 h-3.5 text-sky-400" />
              検索方式の選択 (3段階ロードマップ)
            </span>
          </label>

          <div class="grid grid-cols-3 gap-1.5 p-1 bg-slate-950 rounded-lg border border-slate-800">
            <button
              @click="searchMode = 'keyword'"
              :class="[
                'py-2 px-2 text-[11px] font-semibold rounded transition-colors text-center',
                searchMode === 'keyword'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              ]"
            >
              ① キーワード (BM25)
            </button>

            <button
              @click="searchMode = 'vector'"
              :class="[
                'py-2 px-2 text-[11px] font-semibold rounded transition-colors text-center',
                searchMode === 'vector'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              ]"
            >
              ② ベクトル (Dense)
            </button>

            <button
              @click="searchMode = 'hybrid'"
              :class="[
                'py-2 px-2 text-[11px] font-bold rounded transition-colors text-center',
                searchMode === 'hybrid'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              ]"
            >
              ③ ハイブリッド [推奨]
            </button>
          </div>

          <div class="text-[10px] text-slate-400 leading-tight pt-1">
            <span v-if="searchMode === 'keyword'">🎯 <strong>BM25</strong>: 「価格転嫁」などの完全一致キーワードを確実に捕捉</span>
            <span v-else-if="searchMode === 'vector'">🧠 <strong>Dense Vector</strong>: 「コストの取引先への反映」など同義語・文脈類似で検索</span>
            <span v-else>🏆 <strong>Hybrid (RRF)</strong>: キーワード完全一致と意味類似の順位を統合した最高精度モード</span>
          </div>
        </div>

        <!-- Sample Selector -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <label class="block text-xs font-semibold text-slate-300 mb-2">白書の検証抜粋テキスト</label>
          <div class="space-y-2">
            <button
              v-for="doc in SAMPLE_DOCS"
              :key="doc.id"
              @click="selectSample(doc.id)"
              :class="[
                'w-full text-left p-2.5 rounded-lg text-xs transition-colors border',
                selectedDocId === doc.id
                  ? 'bg-sky-500/10 border-sky-500/30 text-white'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              ]"
            >
              {{ doc.title }}
            </button>
          </div>

          <div class="mt-3">
            <label class="block text-[11px] text-slate-400 mb-1">白書本文テキスト (章・節メタデータ付き)</label>
            <textarea
              v-model="customText"
              rows="6"
              class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-300 font-mono leading-relaxed focus:outline-none focus:border-sky-500"
            ></textarea>
          </div>
        </div>

        <!-- Chunking Sliders -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-300 flex items-center gap-2">
              <Sliders class="w-3.5 h-3.5 text-sky-400" />
              階層チャンク分割パラメータ
            </span>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-slate-400">チャンクサイズ (文字数):</span>
              <span class="font-mono text-sky-400 font-semibold">{{ chunkSize }} 文字</span>
            </div>
            <input
              v-model.number="chunkSize"
              type="range"
              min="300"
              max="1500"
              step="50"
              class="w-full accent-sky-500 cursor-pointer"
            />
            <div class="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>細粒度 (300)</span>
              <span>白書推奨 (600〜800)</span>
              <span>1節まるごと (1500+)</span>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-slate-400">オーバーラップ (重複幅):</span>
              <span class="font-mono text-sky-400 font-semibold">{{ chunkOverlap }} 文字</span>
            </div>
            <input
              v-model.number="chunkOverlap"
              type="range"
              min="50"
              max="300"
              step="25"
              class="w-full accent-sky-500 cursor-pointer"
            />
            <div class="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>最小 (50)</span>
              <span>推奨 (100〜150)</span>
              <span>広域 (300)</span>
            </div>
          </div>
        </div>

        <!-- Question Input & Submit Button -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3">
          <label class="block text-xs font-semibold text-slate-300">質問の入力</label>
          <input
            v-model="query"
            type="text"
            placeholder="ものづくり白書について質問を入力..."
            class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            @keydown.enter="runSimulation"
          />

          <!-- Quick prompt suggestions -->
          <div class="flex flex-wrap gap-1.5 pt-1">
            <button
              @click="query = '中小製造業における価格転嫁の現状と直面している課題について教えてください'"
              class="text-[10px] px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700"
            >
              # 価格転嫁の進捗
            </button>
            <button
              @click="query = '製造業におけるDX推進の現状とボトルネックは何ですか？'"
              class="text-[10px] px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700"
            >
              # DX推進と課題
            </button>
            <button
              @click="query = 'サプライチェーンの強靭化とカーボンニュートラルへの対応策は？'"
              class="text-[10px] px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700"
            >
              # サプライチェーンとGX
            </button>
          </div>

          <button
            @click="runSimulation"
            :disabled="isLoading || !query.trim()"
            class="w-full mt-2 py-2.5 px-4 rounded-lg text-xs font-bold text-white bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors shadow"
          >
            <RefreshCw v-if="isLoading" class="w-4 h-4 animate-spin" />
            <Play v-else class="w-4 h-4" />
            <span>{{ isLoading ? '検索・回答生成中...' : 'RAGパイプラインを実行' }}</span>
          </button>
        </div>
      </div>

      <!-- Right Panel: Results & Analytics (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        <!-- Error alert -->
        <div v-if="errorMsg" class="p-4 rounded-xl bg-red-950/40 border border-red-500/30 text-red-300 text-xs flex items-start gap-2">
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <span>{{ errorMsg }}</span>
        </div>

        <!-- AI Answer Card -->
        <div v-if="resultData" class="bg-slate-900 border border-sky-500/40 rounded-xl p-5 shadow-lg relative overflow-hidden">
          <div class="flex items-center justify-between text-xs font-bold text-sky-400 mb-3">
            <span class="flex items-center gap-2">
              <Sparkles class="w-4 h-4" />
              <span>Gemini 回答生成 (章・節・ページ出典付き)</span>
            </span>
            <span class="font-mono text-[10px] uppercase px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/30">
              検索モード: {{ resultData.searchMode }}
            </span>
          </div>
          <div class="text-xs text-slate-200 leading-relaxed whitespace-pre-line bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            {{ resultData.answer }}
          </div>

          <!-- 3方式の順位比較ビュー (Comparison) -->
          <div v-if="resultData.comparison" class="mt-4 pt-4 border-t border-slate-800">
            <div class="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-2">
              <ArrowRightLeft class="w-3.5 h-3.5 text-indigo-400" />
              <span>検索方式ごとの上位ヒット順位の比較</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
              <!-- BM25 top -->
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <div class="font-bold text-sky-400 mb-1">1. キーワード (BM25)</div>
                <div v-for="c in resultData.comparison.keywordTop" :key="c.id" class="text-slate-400 truncate">
                  順位{{ c.kwRank }}: {{ c.section }} (p.{{ c.page }})
                </div>
              </div>

              <!-- Vector top -->
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <div class="font-bold text-emerald-400 mb-1">2. ベクトル (Chroma)</div>
                <div v-for="c in resultData.comparison.vectorTop" :key="c.id" class="text-slate-400 truncate">
                  順位{{ c.vecRank }}: {{ c.section }} (p.{{ c.page }})
                </div>
              </div>

              <!-- Hybrid top -->
              <div class="p-2.5 rounded bg-slate-950 border border-indigo-500/40">
                <div class="font-bold text-indigo-400 mb-1">3. ハイブリッド (RRF)</div>
                <div v-for="(c, i) in resultData.comparison.hybridTop" :key="c.id" class="text-slate-200 truncate">
                  統合{{ i+1 }}: {{ c.section }} (p.{{ c.page }})
                </div>
              </div>
            </div>
          </div>

          <!-- Retrieved Chunks (Sources) -->
          <div class="mt-4 pt-4 border-t border-slate-800">
            <div class="text-xs font-semibold text-slate-400 mb-2">
              📚 回答に採用された上位チャンク (Top-{{ resultData.topChunks.length }})
            </div>
            <div class="space-y-2">
              <div
                v-for="(chunk, idx) in resultData.topChunks"
                :key="chunk.id"
                class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs flex flex-col gap-1"
              >
                <div class="flex items-center justify-between text-[11px]">
                  <span class="font-bold text-sky-400">
                    [資料{{ idx + 1 }} · {{ chunk.section }} (p.{{ chunk.page }})]
                  </span>
                  <div class="font-mono text-[10px] space-x-2">
                    <span v-if="chunk.kwScore" class="text-sky-300">BM25: 順位{{ chunk.kwRank }}</span>
                    <span v-if="chunk.vecScore" class="text-emerald-300">ベクトル: 順位{{ chunk.vecRank }}</span>
                    <span v-if="chunk.rrfScore" class="text-indigo-400 font-bold">RRF: {{ (chunk.rrfScore * 100).toFixed(2) }}</span>
                  </div>
                </div>
                <p class="text-slate-300 text-[11px] line-clamp-2 leading-tight font-mono">
                  {{ chunk.text }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State placeholder before query execution -->
        <div v-else class="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center text-xs text-slate-400 flex flex-col items-center justify-center min-h-[160px]">
          <FileText class="w-8 h-8 text-slate-600 mb-2" />
          <p class="font-semibold text-slate-300">ものづくり白書 RAGシミュレーション待機中</p>
          <p class="text-[11px] text-slate-500 mt-1 max-w-sm">
            左側の検索方式（キーワード / ベクトル / ハイブリッド）を選び、「RAGパイプラインを実行」ボタンを押すと、各方式の検索順位とGeminiによる出典付き回答が生成されます。
          </p>
        </div>

        <!-- pandas DataFrame チャンク分析プレビュー -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-xs font-bold text-white">白書チャンク分割メタデータ (pandas DataFrame 形式)</div>
              <div class="text-[11px] text-slate-400 mt-0.5">
                総チャンク数: <span class="text-sky-400 font-mono font-bold">{{ statsSummary.count }} 件</span>
                · 節数: <span class="text-sky-400 font-mono font-bold">{{ statsSummary.sections }} 節</span>
                · 平均文字数: <span class="text-sky-400 font-mono font-bold">{{ statsSummary.avg }} 文字</span>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto max-h-60 rounded border border-slate-800">
            <table class="w-full text-[11px] text-left text-slate-300 font-mono">
              <thead class="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
                <tr>
                  <th class="px-3 py-2 w-16">chunk_id</th>
                  <th class="px-3 py-2 w-16">page</th>
                  <th class="px-3 py-2 w-48">section (節見出し)</th>
                  <th class="px-3 py-2 w-20">char_count</th>
                  <th class="px-3 py-2">preview</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/60 bg-slate-950/40">
                <tr v-for="c in localChunks" :key="c.id" class="hover:bg-slate-800/40">
                  <td class="px-3 py-1.5 text-sky-400">{{ c.id }}</td>
                  <td class="px-3 py-1.5 text-slate-400">p.{{ c.page }}</td>
                  <td class="px-3 py-1.5 text-slate-300 truncate max-w-xs">{{ c.section }}</td>
                  <td class="px-3 py-1.5">{{ c.charCount }}</td>
                  <td class="px-3 py-1.5 text-slate-400 truncate max-w-xs">{{ c.preview }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
