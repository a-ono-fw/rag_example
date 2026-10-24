import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

app.use(express.json({ limit: '10mb' }));

// Gemini SDK Client
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      'User-Agent': 'aistudio-build',
    },
  },
});

// 1. API: プロジェクトファイル一覧とコンテンツの取得
app.get('/api/project-files', (req, res) => {
  try {
    const projectDir = path.resolve(__dirname, 'python_project');
    const files: Array<{ path: string; name: string; content: string; language: string }> = [];

    const readDirRecursive = (dir: string, base: string = '') => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        const relPath = base ? `${base}/${entry.name}` : entry.name;
        if (entry.isDirectory()) {
          readDirRecursive(fullPath, relPath);
        } else {
          let lang = 'plaintext';
          if (entry.name.endsWith('.py')) lang = 'python';
          else if (entry.name.endsWith('.ipynb')) lang = 'json';
          else if (entry.name.endsWith('.md')) lang = 'markdown';
          else if (entry.name.endsWith('.txt')) lang = 'plaintext';

          files.push({
            path: relPath,
            name: entry.name,
            content: fs.readFileSync(fullPath, 'utf-8'),
            language: lang,
          });
        }
      }
    };

    if (fs.existsSync(projectDir)) {
      readDirRecursive(projectDir);
    }

    res.json({ success: true, files });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 2. API: RAGシミュレーション（キーワードBM25 / ベクトル / ハイブリッドRRF）
app.post('/api/rag/simulate', async (req, res) => {
  try {
    const { query, documentText, chunkSize = 500, chunkOverlap = 100, searchMode = 'hybrid' } = req.body;

    if (!query || !documentText) {
      return res.status(400).json({ error: 'query and documentText are required' });
    }

    // 階層メタデータ（章・節）を考慮したチャンク分割
    const text = documentText.toString();
    const rawChunks: Array<{ id: number; page: number; section: string; text: string }> = [];
    let start = 0;
    let chunkId = 1;
    let currentSection = '第1節 我が国ものづくり産業の現状と課題';

    while (start < text.length) {
      const end = Math.min(start + chunkSize, text.length);
      const chunkContent = text.substring(start, end).trim();

      // 節見出しの検知
      const secMatch = chunkContent.match(/(第[一二三四五六七八九十\d]+節\s+[^\n]{2,30})/);
      if (secMatch) {
        currentSection = secMatch[1].trim();
      }

      if (chunkContent.length > 0) {
        const simulatedPage = Math.floor(start / 700) + 1;
        rawChunks.push({
          id: chunkId++,
          page: simulatedPage,
          section: currentSection,
          text: chunkContent,
        });
      }
      start += Math.max(chunkSize - chunkOverlap, 50);
    }

    // 1. キーワードスコア計算 (BM25近似: 単語一致 + バイグラム)
    const queryTokens = query.toLowerCase().split(/[\s,。、?!！？]+/).filter((t: string) => t.length > 1);
    const kwScored = rawChunks.map(c => {
      let count = 0;
      const lower = c.text.toLowerCase();
      for (const t of queryTokens) {
        if (lower.includes(t)) count += 1;
      }
      const score = queryTokens.length > 0 ? (count / queryTokens.length) * 10 : 0;
      return { ...c, kwScore: score };
    });

    const kwRanked = [...kwScored].sort((a, b) => b.kwScore - a.kwScore);
    const kwRankMap = new Map<number, number>();
    kwRanked.forEach((c, idx) => kwRankMap.set(c.id, idx + 1));

    // 2. ベクトル類似度計算 (意味的類似度の擬似スコア)
    // 意味関連語（DX, 価格転嫁, サプライチェーン, カーボンニュートラル等）との近さ
    const vecScored = rawChunks.map(c => {
      let semScore = 0.3;
      const lower = c.text.toLowerCase();
      const qLower = query.toLowerCase();

      // キーワード以外の意味的マッチ判定
      if (qLower.includes('価格') && (lower.includes('取引') || lower.includes('原材料') || lower.includes('コスト'))) semScore += 0.4;
      if (qLower.includes('dx') && (lower.includes('デジタル') || lower.includes('it') || lower.includes('自動化'))) semScore += 0.45;
      if (qLower.includes('脱炭素') && (lower.includes('gx') || lower.includes('エネルギー') || lower.includes('排出'))) semScore += 0.45;
      if (qLower.includes('課題') && (lower.includes('直面') || lower.includes('現状') || lower.includes('不足'))) semScore += 0.3;

      const randomJitter = (Math.sin(c.id * 9.2) + 1) * 0.1;
      const finalVecScore = Math.min(semScore + randomJitter, 0.96);
      return { ...c, vecScore: finalVecScore };
    });

    const vecRanked = [...vecScored].sort((a, b) => b.vecScore - a.vecScore);
    const vecRankMap = new Map<number, number>();
    vecRanked.forEach((c, idx) => vecRankMap.set(c.id, idx + 1));

    // 3. ハイブリッド (RRF: Reciprocal Rank Fusion) スコア
    const RRF_K = 60;
    const hybridScored = rawChunks.map(c => {
      const kwRank = kwRankMap.get(c.id) || 999;
      const vecRank = vecRankMap.get(c.id) || 999;
      const rrfScore = (1.0 / (RRF_K + kwRank)) + (1.0 / (RRF_K + vecRank));
      return {
        ...c,
        kwRank,
        vecRank,
        kwScore: (kwScored.find(x => x.id === c.id)?.kwScore || 0).toFixed(2),
        vecScore: (vecScored.find(x => x.id === c.id)?.vecScore || 0).toFixed(3),
        rrfScore,
      };
    });

    // 選択されたモードに応じたソート
    let topChunks: any[] = [];
    if (searchMode === 'keyword') {
      topChunks = [...hybridScored].sort((a, b) => a.kwRank - b.kwRank).slice(0, 4);
    } else if (searchMode === 'vector') {
      topChunks = [...hybridScored].sort((a, b) => a.vecRank - b.vecRank).slice(0, 4);
    } else {
      topChunks = [...hybridScored].sort((a, b) => b.rrfScore - a.rrfScore).slice(0, 4);
    }

    const contextForPrompt = topChunks
      .map(
        (c, idx) =>
          `[資料${idx + 1} / ${c.section} (ページ: ${c.page}, チャンクID: ${c.id})]\n${c.text}`
      )
      .join('\n\n');

    const prompt = `あなたは「2024年版ものづくり白書」の専門アシスタントです。
以下の【提供された資料】のみを根拠にして、ユーザーからの【質問】に分かりやすく回答してください。
資料に書かれていない事柄は推測せず「資料に記載がありません」と答え、回答文の末尾または該当箇所に必ず参照した節名とページ番号 [${topChunks[0]?.section || '第1節'} p.X] を明記してください。

【提供された資料】:
${contextForPrompt}

【質問】:
${query}

【回答】:`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.8-flash',
      contents: prompt,
      config: {
        temperature: 0.2,
      },
    });

    res.json({
      success: true,
      searchMode,
      answer: response.text,
      totalChunks: rawChunks.length,
      topChunks,
      comparison: {
        keywordTop: [...hybridScored].sort((a, b) => a.kwRank - b.kwRank).slice(0, 3),
        vectorTop: [...hybridScored].sort((a, b) => a.vecRank - b.vecRank).slice(0, 3),
        hybridTop: [...hybridScored].sort((a, b) => b.rrfScore - a.rrfScore).slice(0, 3),
      },
      allChunksPreview: rawChunks.slice(0, 10),
    });
  } catch (error: any) {
    console.error('RAG simulation error:', error);
    res.status(500).json({ success: false, error: error.message || 'Error executing simulation' });
  }
});

// Vite middleware or production static
async function startServer() {
  if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.resolve(__dirname, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
    });
  } else {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server listening on http://0.0.0.0:${PORT}`);
  });
}

startServer();
