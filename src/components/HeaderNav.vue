<script setup lang="ts">
import { BookOpen, Download, Terminal } from 'lucide-vue-next';

defineProps<{
  activeTab: 'architecture' | 'simulator' | 'code' | 'guide';
}>();

const emit = defineEmits<{
  (e: 'select-tab', tab: 'architecture' | 'simulator' | 'code' | 'guide'): void;
  (e: 'download-all'): void;
}>();
</script>

<template>
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-8">
      <!-- Zone 1: Single text element wordmark -->
      <div class="flex items-center gap-3 shrink-0">
        <div class="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
          <BookOpen class="w-5 h-5" />
        </div>
        <span class="text-base font-bold text-white tracking-tight whitespace-nowrap">
          RAG Colab Workbench
        </span>
      </div>

      <!-- Zone 2: Navigation links / tabs (single-line whitespace-nowrap) -->
      <nav class="hidden md:flex items-center gap-2">
        <button
          @click="emit('select-tab', 'architecture')"
          :class="[
            'px-3.5 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0',
            activeTab === 'architecture'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          ]"
        >
          選定理由 & アーキテクチャ
        </button>

        <button
          @click="emit('select-tab', 'simulator')"
          :class="[
            'px-3.5 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0',
            activeTab === 'simulator'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          ]"
        >
          RAG分割 & 検索テスト
        </button>

        <button
          @click="emit('select-tab', 'code')"
          :class="[
            'px-3.5 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0',
            activeTab === 'code'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          ]"
        >
          Pythonコード & Notebook
        </button>

        <button
          @click="emit('select-tab', 'guide')"
          :class="[
            'px-3.5 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0',
            activeTab === 'guide'
              ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          ]"
        >
          Colab実行手順ガイド
        </button>
      </nav>

      <!-- Zone 3: 1 primary action -->
      <div class="flex items-center gap-3 shrink-0">
        <button
          @click="emit('download-all')"
          class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg text-white bg-sky-600 hover:bg-sky-500 transition-colors whitespace-nowrap shrink-0 shadow-sm"
        >
          <Download class="w-4 h-4" />
          <span>全ファイルを保存</span>
        </button>
      </div>
    </div>
  </header>
</template>
