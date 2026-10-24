<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Copy, Check, Download, FileCode, Folder, Terminal } from 'lucide-vue-next';

interface ProjectFile {
  path: string;
  name: string;
  content: string;
  language: string;
}

const files = ref<ProjectFile[]>([]);
const selectedFile = ref<ProjectFile | null>(null);
const copied = ref(false);
const isLoading = ref(true);

onMounted(async () => {
  try {
    const res = await fetch('/api/project-files');
    const data = await res.json();
    if (data.success && data.files.length) {
      files.value = data.files;
      // 既定で notebook または app_gradio.py を選択
      const defaultF = files.value.find(f => f.name.includes('colab')) || files.value[0];
      selectedFile.value = defaultF;
    }
  } catch (err) {
    console.error('Failed to load project files:', err);
  } finally {
    isLoading.value = false;
  }
});

function copyCode() {
  if (!selectedFile.value) return;
  navigator.clipboard.writeText(selectedFile.value.content);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
}

function downloadCurrentFile() {
  if (!selectedFile.value) return;
  const blob = new Blob([selectedFile.value.content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = selectedFile.value.name;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="border-b border-slate-800 pb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <div class="text-xs text-sky-400 font-mono mb-1">GITHUB & COLAB READY CODEBASE</div>
        <h2 class="text-xl sm:text-2xl font-bold text-white tracking-tight">
          Python ソースコード & Jupyter Notebook
        </h2>
        <p class="text-xs text-slate-400 mt-1">
          GitHubにプッシュしてGoogle Colabから即座に実行できる一式を揃えています。
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="downloadCurrentFile"
          :disabled="!selectedFile"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
        >
          <Download class="w-3.5 h-3.5" />
          <span>このファイルをダウンロード</span>
        </button>

        <button
          @click="copyCode"
          :disabled="!selectedFile"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg text-white bg-sky-600 hover:bg-sky-500 transition-colors"
        >
          <Check v-if="copied" class="w-3.5 h-3.5 text-emerald-300" />
          <Copy v-else class="w-3.5 h-3.5" />
          <span>{{ copied ? 'コピー完了！' : 'コードをコピー' }}</span>
        </button>
      </div>
    </div>

    <!-- Explorer Grid (Sidebar + Code View) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[580px]">
      <!-- File Tree Sidebar (4 cols) -->
      <div class="lg:col-span-4 border-b lg:border-b-0 lg:border-r border-slate-800 p-4 bg-slate-950/60">
        <div class="text-[11px] font-mono text-slate-400 font-semibold mb-3 flex items-center gap-1.5">
          <Folder class="w-3.5 h-3.5 text-sky-400" />
          <span>python_project /</span>
        </div>

        <div v-if="isLoading" class="text-xs text-slate-500 py-4 text-center">
          ファイルを読み込み中...
        </div>

        <div v-else class="space-y-1">
          <button
            v-for="file in files"
            :key="file.path"
            @click="selectedFile = file"
            :class="[
              'w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition-colors font-mono',
              selectedFile?.path === file.path
                ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            ]"
          >
            <div class="flex items-center gap-2 truncate">
              <FileCode class="w-4 h-4 shrink-0 text-slate-500" />
              <span class="truncate">{{ file.path }}</span>
            </div>
            <span class="text-[10px] text-slate-500 shrink-0 uppercase">{{ file.language }}</span>
          </button>
        </div>

        <!-- Git Push Quick Reminder -->
        <div class="mt-6 p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] space-y-2">
          <div class="font-bold text-slate-300 flex items-center gap-1.5">
            <Terminal class="w-3.5 h-3.5 text-sky-400" />
            <span>GitHubへのプッシュ手順</span>
          </div>
          <div class="bg-slate-950 p-2 rounded font-mono text-[10px] text-slate-400 space-y-1 overflow-x-auto">
            <div>git init</div>
            <div>git add .</div>
            <div>git commit -m "feat: setup RAG chatbot"</div>
            <div>git remote add origin &lt;URL&gt;</div>
            <div>git push -u origin main</div>
          </div>
          <p class="text-[10px] text-slate-500 leading-tight">
            ※ 31MBのPDFファイルは <code class="text-slate-300">data/document.pdf</code> に配置してコミットできます（100MB未満）。
          </p>
        </div>
      </div>

      <!-- Code Editor / Viewer (8 cols) -->
      <div class="lg:col-span-8 flex flex-col bg-slate-950">
        <!-- Editor Header Bar -->
        <div class="h-10 px-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/40">
          <span class="text-xs font-mono text-slate-300 flex items-center gap-2">
            <span class="text-sky-400 font-bold">{{ selectedFile?.path || 'No file selected' }}</span>
          </span>
          <span class="text-[10px] font-mono text-slate-500">
            {{ selectedFile ? `${selectedFile.content.split('\n').length} 行` : '' }}
          </span>
        </div>

        <!-- Code Content -->
        <div class="p-4 overflow-auto flex-1 max-h-[580px]">
          <pre
            v-if="selectedFile"
            class="text-xs font-mono text-slate-300 leading-relaxed whitespace-pre"
          ><code>{{ selectedFile.content }}</code></pre>
          <div v-else class="text-xs text-slate-500 text-center py-20">
            ファイルを選択してください
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
