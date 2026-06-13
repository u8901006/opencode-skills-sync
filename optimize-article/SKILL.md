---
name: optimize-article
description: |
  健康／心理／知識型 SEO 文章的「一鍵全流程」優化 skill。把使用者每次都要重複交代的
  pipeline 收斂成單一指令：診斷 → SEO 十項審核 → 補洞與 FAQ → 逐條查證引用（核對正確期刊名）
  → Sugarman 文案優化 → humanizer-zh-tw 去 AI 痕跡 → 存成 -v2 新檔 → 品質閘門逐項過關 → 輸出變更表。
  使用時機：使用者要求「優化這篇文章 / 跑完整流程 / 上稿前處理 / optimize article / full pipeline /
  article pipeline / 一條龍處理這篇」，或丟一篇 .md 健康／心理長文要求整體提升時。即便只說
  「幫我把這篇處理到可以發」，只要是 SEO 導向長文皆應觸發。
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - Skill
  - TodoWrite
  - AskUserQuestion
metadata:
  trigger: 對一篇 SEO 健康/心理文章執行完整 audit→fix→verify→humanize→save pipeline
  chains: seo-article-checker, citation-verifier (or factcheck), anthropic-skills:copywriting-optimizer, humanizer-zh-tw
---

# optimize-article：SEO 文章全流程優化編排器

你是一個**流程編排器（orchestrator）**。收到一篇文章後，依序跑完七個階段，**階段之間自動傳遞產物、不中途停下來問確認**（除非缺關鍵資訊，如找不到檔案或主關鍵字無法判定）。全部跑完後，再輸出一份總結報告。

> 這支 skill 把使用者重複交代的步驟固定下來。預設行為由 `CLAUDE.md` 的 **Content Optimization Workflow** 段落定義，本 skill 是它的可執行版本。

## 核心作業原則

**Verify-then-Edit 原則**：每次呼叫 Edit 工具前，必須先用 Read 讀取目標段落的**精確原文**，改完後再確認輸出文字符合意圖。此原則適用於本 skill 的所有階段，以杜絕誤植與無意刪改。高 Edit 量下尤其重要——62 次編輯中只要一次打錯字就要多一個回合。

## 啟動

1. **確認檔案**：用 Read 讀完整篇目標 `.md`（含 YAML frontmatter）。長文必須讀完，不可抽樣。
2. **確認環境**：這是 Windows、且 `D:\blogpage` 多半**不是 git 倉庫** — 不要跑任何假設 git 的指令，不要依賴 pandoc（沒有就用 PowerShell 解 .docx）。
3. **辨識主／次關鍵字**：從 frontmatter `keywords`、`title`、首段、URL slug 萃取。判不出來才問使用者。
4. 用 TodoWrite 建立七個階段 + 品質閘門的待辦清單，逐項標記進度。

## 七階段流程（依序執行）

### 階段 1 — 診斷與 SEO 十項審核
- 呼叫 `Skill: seo-article-checker` 對全文跑十項檢核，得出 ✅/⚠️/❌ 與具體事證。
- 記下所有 ⚠️/❌ 項目，作為後續修補清單。
- 輸出診斷摘要（問題列表，含嚴重程度分級）。

### 階段 2 — 補洞與結構修整
- 依審核結果修正：合併過深的標題階層（H 標題總數盡量 ≤ 6 個 H2 區塊）、補上搜尋意圖缺口、去除離題段落。
- 每次 Edit 前先 Read 精確原文，改後確認，防止誤植（Verify-then-Edit）。
- 用**有來源**的資訊填補內容缺口；找不到可靠來源的主張，標 `（needs verification）`／`[待驗證]`，不要刪除也不要編造。

### 階段 3 — FAQ 與結構化資料
- 依長尾關鍵字加入 / 補強 FAQ 區塊，每題答案附**已查證**的學術統計或數據。
- 產出對應的 JSON-LD `FAQPage` schema（放在文末 code block 或 frontmatter 指示）。

### 階段 4 — 逐條查證引用（核心，不可略過）
- **優先**查 `D:\blogpage\citations-verified.md`：已記錄且標 VERIFIED 的來源直接沿用，不重查。新查證結果寫回該檔（含正確期刊名）。
- 呼叫 `Skill: citation-verifier`（若不可用則 `Skill: factcheck`）逐條查證**每一個**統計數字與學術引用。
- 對每條引用必須確認：作者、年份、DOI 有效性、**正確的期刊／來源名稱**，並檢查重複引用。
- **引用數 > 8 條**時，考慮用 Task 子代理並行查驗（每個子代理處理 2–3 條），合併結果表，縮短查證時間。
- 已知易錯、務必明確標示的誤植（若文中出現）：
  - Bhatt 耳鳴流行病學 → 正確期刊為 **The Laryngoscope**（非 JAMA Otolaryngology）
  - **Raichle 2001**（default mode network）→ **PNAS**
  - **Kandel 2001** → 核對正確出處後標示
- 查證遇 **403 / socket error**：self-healing fallback — ① doi.org 內容協商 → ② Crossref API `https://api.crossref.org/works/{DOI}` → ③ Google Scholar → ④ 都失敗才用內部知識並標 `[待驗證]`。
- 任何修正在變更表中**明確列出**「原誤植 → 正確來源」。

### 階段 5 — Sugarman 文案優化
- 呼叫 `Skill: anthropic-skills:copywriting-optimizer`，依 Sugarman 12 原則改寫，強化滑梯效應與可讀性。
- **衝突解決**：若 SEO／文案建議與醫療精確性衝突，**醫療精確性優先**。

### 階段 6 — 中文人味化（zh-TW）
- 呼叫 `Skill: humanizer-zh-tw` 去除 AI 寫作痕跡：破折號過度、三段式法則、否定式排比、膚淺 -ing 分析、模糊歸因、宣傳語等。
- **統一術語**（例如「神經覺」全文一致），確保專業詞彙前後一致。

### 階段 7 — 自我回歸測試（Self-Regression Check）
在存檔前，對修改後的全文執行下列快速驗證：
- **Diff 核查**：比對 v2 與原文，確認沒有意外刪除的段落或無意改動的事實陳述。
- **鏈結掃描**：找出空連結（`[]()` 或 `[text]()`）與格式損壞的 Markdown。
- **AI 痕跡殘留**：快速掃描常見 AI 句式（見 humanizer-zh-tw 的 24 個模式）；發現則回到階段 6 修正。
- **品質閘門預檢**：確認 G1–G8 全過後再存檔。
- 若有任何一項失敗，**自動修正並重跑該閘門**，不要要求使用者重新下指令。

## 品質閘門（Quality Gates）— 全部綠燈才算完成

| # | 閘門 | 通過標準 | 不過時回到 |
|---|------|----------|-----------|
| G1 | 引用可解析 | 每條引用都對得上真實第一手來源，且期刊／來源名稱正確 | 階段 4 |
| G2 | 無誤植殘留 | 已知易錯引用（Bhatt/Raichle/Kandel 等）已核對修正 | 階段 4 |
| G3 | 無 AI 寫作痕跡 | 無破折號濫用、三段式、否定式排比、模板化過渡語 | 階段 6 |
| G4 | 無佔位文字 | 無 TODO、無 `[待驗證]` 殘留**未經標示**、無 `lorem`／空連結 | 階段 2 |
| G5 | 標題階層合理 | H2 區塊數量精簡（建議 ≤ 6），無跳階 | 階段 2 |
| G6 | FAQ schema 有效 | JSON-LD `FAQPage` 語法正確、題目對應內文 | 階段 3 |
| G7 | frontmatter 完整 | title、description、keywords 齊備且與內文一致 | 階段 2 |
| G8 | 術語一致 | 全文關鍵術語用詞統一 | 階段 6 |
| G9 | 無意外改動 | Diff 核查確認無段落遺漏、無事實陳述誤改 | 階段 7 |

## 輸出

1. **存成新檔**：絕不覆寫原檔。輸出到 `<原檔名>-v2.md`（或既有慣例如 `優化版`）。保留並更新 YAML frontmatter。
2. **變更摘要表**（每次都要輸出，不可省略）：
   一張表列出每項改動 — 面向、原狀、改後、理由；引用修正獨立一列標「原誤植 → 正確來源」。
   ```
   | 面向 | 原狀 | 改後 | 理由 |
   |------|------|------|------|
   | SEO  | 缺 meta description | 已補 120 字 | 提升 SERP 點擊率 |
   | 引用 | JAMA Otolaryngology (Bhatt) | The Laryngoscope | 誤植更正 |
   ...
   ```
3. **品質閘門結果**：貼出 G1–G9 的最終綠燈清單。
4. **信心標示**：引用查證表標 **VERIFIED / HIGH / MEDIUM / LOW**。

## 批次模式

若使用者指向一個目錄或多篇文章（>5 篇）：用 `Skill: superpowers:dispatching-parallel-agents` 或 Task 子代理，每篇一個子代理獨立跑完本流程（批次 5–10 篇），最後彙整成單一 dashboard：每篇列出 SEO 改善、引用修正、未能自動完成的項目。子代理**直接 Read／Edit 檔案**，不要把內容回傳主代理再存。

## 進階模式：自主內容流水線（Autonomous Pipeline）

適用於大量生產場景（每週批次、書籍轉文章後優化）：

1. 監看 `./inbox/` 目錄，偵測新 `.md` 檔案
2. 按本 skill 七階段依序處理每篇
3. 引用查驗以並行子代理執行（每子代理 2–3 條引用）
4. 每個階段產出通過品質閘門後才進入下一階段；閘門失敗記錄到 `./pipeline-report.md` 並暫停等候確認
5. 所有中間版本與最終版本儲存到 `./output/`

啟動提示詞：
```
Build an autonomous content pipeline. Given a source file in ./inbox, sequentially:
(1) extract and restructure into article form, (2) apply the Sugarman 12-principles skill,
(3) run the SEO-optimize skill including DOI/citation verification via WebFetch,
(4) run the humanizer skill to remove AI traces.
After each stage, validate the output against that stage's checklist and only proceed
if all items pass; log any failures to ./pipeline-report.md and pause for my review.
Save all intermediate and final versions to ./output.
```
