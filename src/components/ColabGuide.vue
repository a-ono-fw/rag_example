<script setup lang="ts">
import { BookOpen, Key, HardDrive, Terminal, HelpCircle, ExternalLink, CheckCircle } from 'lucide-vue-next';
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="border-b border-slate-800 pb-6">
      <div class="text-xs text-sky-400 font-mono mb-1">STEP-BY-STEP WORKFLOW</div>
      <h2 class="text-xl sm:text-2xl font-bold text-white tracking-tight">
        Google Colab 実行・学習ガイド
      </h2>
      <p class="text-xs text-slate-400 mt-2 max-w-2xl leading-relaxed">
        Google Colabの概念整理から、APIキーの登録、31MBのPDFの配置、Gradioでの対話画面立ち上げまでの全手順を解説します。
      </p>
    </div>

    <!-- 用語と環境の整理 -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div class="flex items-center gap-2 text-xs font-bold text-sky-400 mb-2">
        <BookOpen class="w-4 h-4" />
        <span>「デプロイ」と Google Colab の位置づけの整理</span>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed">
        一般に「デプロイ（Deploy）」というと、Webサーバーやクラウド（Cloud RunやAWS等）にアプリを配置して24時間いつでもアクセスできるようにする常時公開を指すことが多いです。<br />
        一方、今回の <strong>Google Colab</strong> は「<strong>インタラクティブな実行・検証環境（Jupyter Notebook）</strong>」です。
      </p>

      <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-bold text-emerald-400 mb-1">今回の目的「学習時・試験時に動けば良い」</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            Google Colabはまさにこの用途に最適です。常時稼働のサーバー代が一切かからず、ノートブックを開いてセルを実行するだけで瞬時に環境が整います。
          </p>
        </div>

        <div class="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-bold text-sky-400 mb-1">Gradioの一時公開URL (share=True)</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            Gradioを実行すると、Colab内部だけでなく <code class="text-slate-300">https://xxxx.gradio.live</code> のような公開URLが自動発行され、PCやスマートフォンのブラウザから実際のチャットボットを操作できます。
          </p>
        </div>
      </div>
    </div>

    <!-- 31MB PDFの3つの配置方法 -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div class="flex items-center gap-2 text-xs font-bold text-white mb-4">
        <HardDrive class="w-4 h-4 text-sky-400" />
        <span>大規模文書（31MB PDF）をColabで読み込む3つの方法</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <!-- 方法1 (推奨) -->
        <div class="p-4 rounded-lg bg-slate-950 border border-sky-500/30 flex flex-col justify-between">
          <div>
            <div class="text-[10px] font-mono text-sky-400 font-bold mb-1">方法 A (推奨・即時実行)</div>
            <div class="font-bold text-white mb-2">GitHubリポジトリ または wget</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">
              GitHubに <code class="text-slate-300">data/document.pdf</code>（31MB）をコミットしてクローンするか、Colabセル上で経産省の公開PDFを1行でダウンロード取得できます：<br />
              <code class="text-sky-300 font-mono text-[10px] block mt-1 bg-slate-900 p-1 rounded">!wget https://www.meti.go.jp/report/whitepaper/mono/2024/honbun/pdf/all.pdf -O data/document.pdf</code>
            </p>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-emerald-400">
            ✓ 340ページ全文を一発取得可能
          </div>
        </div>

        <!-- 方法2 -->
        <div class="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-col justify-between">
          <div>
            <div class="text-[10px] font-mono text-slate-400 font-bold mb-1">方法 B</div>
            <div class="font-bold text-white mb-2">Google Drive をマウント</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">
              ご自身のGoogle DriveにPDFを保存し、Colabノートブック側で以下を実行してマウントします。<br />
              <code class="text-slate-300 font-mono text-[10px]">from google.colab import drive; drive.mount('/content/drive')</code>
            </p>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
            ✓ GitHubを汚したくない場合に便利
          </div>
        </div>

        <!-- 方法3 -->
        <div class="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-col justify-between">
          <div>
            <div class="text-[10px] font-mono text-slate-400 font-bold mb-1">方法 C</div>
            <div class="font-bold text-white mb-2">Colabに直接ドラッグ＆ドロップ</div>
            <p class="text-[11px] text-slate-400 leading-relaxed">
              Colabの左サイドバーにある📁「ファイル」アイコンをクリックし、ファイルを画面上にドラッグ＆ドロップするだけで即座に配置されます。
            </p>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-amber-400">
            ⚠ セッション終了時に消去されるため再投入が必要
          </div>
        </div>
      </div>
    </div>

    <!-- APIキーの安全設定手順 -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div class="flex items-center gap-2 text-xs font-bold text-white mb-3">
        <Key class="w-4 h-4 text-emerald-400" />
        <span>Gemini APIキーの安全な登録手順 (Colabシークレット機能)</span>
      </div>

      <div class="space-y-3 text-xs text-slate-300">
        <div class="flex items-start gap-2.5">
          <div class="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center shrink-0 text-[11px]">1</div>
          <div>
            <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer" class="text-sky-400 underline inline-flex items-center gap-1">
              Google AI Studio <ExternalLink class="w-3 h-3" />
            </a>
            で API キーを取得（コピー）します。
          </div>
        </div>

        <div class="flex items-start gap-2.5">
          <div class="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center shrink-0 text-[11px]">2</div>
          <div>
            Google Colabを開き、画面左メニューの <strong>🔑（シークレット）アイコン</strong> をクリックします。
          </div>
        </div>

        <div class="flex items-start gap-2.5">
          <div class="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center shrink-0 text-[11px]">3</div>
          <div>
            名前欄に <code class="text-white bg-slate-800 px-1 py-0.5 rounded font-mono font-bold">GEMINI_API_KEY</code> と入力し、値欄にコピーしたキーを貼り付けます。
          </div>
        </div>

        <div class="flex items-start gap-2.5">
          <div class="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center shrink-0 text-[11px]">4</div>
          <div>
            <strong>「ノートブックへのアクセス」スイッチを ON</strong> にします。これでノートブック内から <code class="font-mono text-sky-400">userdata.get('GEMINI_API_KEY')</code> で安全に呼び出せます。
          </div>
        </div>
      </div>
    </div>

    <!-- よくある質問・注意点 (FAQ) -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div class="flex items-center gap-2 text-xs font-bold text-white mb-4">
        <HelpCircle class="w-4 h-4 text-sky-400" />
        <span>よくあるトラブルと事前対策</span>
      </div>

      <div class="space-y-3 text-xs">
        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-semibold text-slate-200 mb-1">Q. 31MBのPDFを読み込むとColabのメモリが落ちませんか？</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            今回のコードで採用している <code class="text-slate-300">PyPDFLoader</code> はページ単位でストリーム処理するため、Colabの標準メモリ（12〜15GB）に対してわずか数百MB程度しか消費しません。安心してお使いいただけます。
          </p>
        </div>

        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-semibold text-slate-200 mb-1">Q. PDF内の文字がスキャン画像（文字選択できない）の場合は？</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            PyPDFは「テキストデータとして埋め込まれている文字」を抽出します。もしPDF全体がスキャンされた画像である場合はOCR（<code class="text-slate-300">pytesseract</code> や Gemini 2.5 Flashの画像認識機能）が必要になります。通常の電子PDFであれば問題なく動作します。
          </p>
        </div>

        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-semibold text-slate-200 mb-1">Q. 大量チャンク作成時に 429 ResourceExhausted（レートリミット）が発生しませんか？</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            Gemini APIの無料枠（Free Tier）では埋め込みリクエスト（<code class="text-slate-300">gemini-embedding-001</code>）に <strong>100回/分</strong> の上限があります。全340ページ（約1,000チャンク）を一括送信すると429エラーが発生するため、本リポジトリのコードでは <strong>50件ごとのバッチ分割・3秒ウェイト・429検知時の15秒自動待機リトライ</strong> を組み込んでいます。エラーで停止せず自動完了する安心設計です。
          </p>
        </div>

        <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
          <div class="font-semibold text-slate-200 mb-1">Q. Gradioの共有URLはずっと使えますか？</div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            <code class="text-slate-300">share=True</code> で発行される一時URLの有効期限は最大72時間です。またColabのノートブックセルを停止すると接続が切れます。試験・レビューが完了したらノートブックを停止すれば自動的にURLも無効化されるため、セキュリティ面でも安心です。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
