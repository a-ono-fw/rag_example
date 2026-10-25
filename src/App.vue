<script setup lang="ts">
import { ref } from 'vue';
import HeaderNav from './components/HeaderNav.vue';
import ArchitectureView from './components/ArchitectureView.vue';
import RagSimulator from './components/RagSimulator.vue';
import CodeExplorer from './components/CodeExplorer.vue';
import ColabGuide from './components/ColabGuide.vue';
import { Download } from 'lucide-vue-next';

type Tab = 'architecture' | 'simulator' | 'code' | 'guide';
const activeTab = ref<Tab>('architecture');

async function downloadAllFiles() {
  try {
    const res = await fetch('/api/project-files');
    const data = await res.json();
    if (!data.success || !data.files) return;

    // 各ファイルを順次ダウンロード（ブラウザのBlobダウンロード）
    for (const file of data.files) {
      const blob = new Blob([file.content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      a.click();
      URL.revokeObjectURL(url);
      await new Promise(r => setTimeout(r, 120));
    }
  } catch (err) {
    console.error('Download error:', err);
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
    <!-- Header Navigation -->
    <HeaderNav
      :activeTab="activeTab"
      @select-tab="activeTab = $event"
      @download-all="downloadAllFiles"
    />

    <!-- Main Content Area -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <ArchitectureView
        v-if="activeTab === 'architecture'"
        @navigate="activeTab = $event"
      />

      <RagSimulator
        v-else-if="activeTab === 'simulator'"
      />

      <CodeExplorer
        v-else-if="activeTab === 'code'"
      />

      <ColabGuide
        v-else-if="activeTab === 'guide'"
      />
    </main>

    <!-- Quiet Footer -->
    <footer class="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-400">
      <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span>大規模文書（31MB PDF）RAG チャットボット</span>
          <span>·</span>
          <span>Google Colab &amp; GitHub</span>
        </div>
        <div class="text-[11px] text-slate-400">
          LangChain · ChromaDB · Google Gemini 2.5 Flash · Gradio · pandas
        </div>
      </div>
    </footer>
  </div>
</template>
