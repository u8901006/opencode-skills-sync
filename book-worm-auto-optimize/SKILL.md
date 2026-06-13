---
name: book-worm-auto-optimize
description: |
  Combined pipeline: converts a book (PDF/EPUB/MOBI/AZW3) into chapter-based Traditional Chinese
  public-health articles AND automatically runs the full optimize-article pipeline on each
  generated article. Triggers on: book to optimized articles, 書籍轉優化文章, auto-optimize
  book chapters, 一條龍書籍轉 SEO 文章, book pipeline, epub pipeline with SEO, 書籍衛教優化.
  Use whenever the user wants to go from a raw book file to publish-ready, SEO-optimized,
  citation-verified, humanized articles in one autonomous run — without manual hand-offs between
  extraction and optimization.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - TodoWrite
metadata:
  trigger: "book to optimized articles, 書籍轉優化文章, auto-optimize book chapters, epub pipeline with SEO, 一條龍書籍轉 SEO 文章, book pipeline"
  chains: book-worm, optimize-article (or seo-article-checker, copywriting-optimizer, humanizer-zh-tw)
  source: "Combines book-worm (opencode skill) + optimize-article (claude skill) workflows"
---

# book-worm-auto-optimize：書籍一條龍轉製 + 優化流水線

## 概觀

從一本書（PDF / EPUB / MOBI / AZW3）出發，全自動完成：

```
[Extract] → [Configure] → [Dispatch: 生成文章] → [Auto-Optimize: 每篇跑完整優化] → [Assemble]
```

**核心原則**：不重現書中長段落；根據各章觀念撰寫原創衛教文章，再對每篇執行 SEO / 引用查證 / Sugarman / humanizer 全流程優化，直到品質閘門全綠才算完成。

---

## 第一部分：Extract（書籍萃取）

與 `book-worm` Phase 1 相同——

### 步驟 1：建立目錄

```
{book_parent_dir}/article/          ← 最終文章輸出
C:\Users褁\AppData\Local\Temp\opencode\book-worm-tmp\{book-slug}\   ← 萃取暫存
```

### 步驟 2：執行 extract.py

```bash
python "C:/Users/u8901/.config/opencode/skills/book-worm/scripts/extract.py" "<book_path>" --outdir "<tmpdir>"
```

### 步驟 3：確認萃取輸出

| 檔案 | 內容 |
|------|------|
| `full_text.txt` | 全書文字，含 `[[PAGE N]]` 分頁標記 |
| `chapters.json` | 各章元資料陣列 |
| `chapters/chapter-NN-slug.txt` | 各章文字 |

若 `chapters.json` 為空或看起來不對，請讀 `full_text.txt` 第 5–20 頁手動找目錄，列出章節標題候選讓使用者確認。

---

## 第二部分：Configure（確認設定）

向使用者確認下列預設值（使用者說 "go" 就直接採用）：

| 參數 | 預設 | 說明 |
|------|------|------|
| `output_dir` | `{book_parent_dir}/article/` | 文章輸出目錄 |
| `article_type` | `health-edu` | `health-edu` / `knowledge` / `book-review` |
| `language` | `zh-TW` | 目標語言 |
| `chapters_per_agent` | `3` | 每個子代理處理的章節數 |
| `safety_note` | `true` | 是否加入安全提醒 |
| `auto_optimize` | `true` | 生成後是否自動跑 optimize-article 流程 |
| `optimize_parallel` | `true` | 優化階段是否並行（多篇同時優化） |

---

## 第三部分：Dispatch（生成文章）

### 分批邏輯

```
num_agents = ceil(N / chapters_per_agent)
batch_i = chapters[(i*3) : ((i+1)*3)]
```

### 並行派送

用 `Task` 工具在**同一訊息**內啟動所有代理（一個 Task call 一個批次）。每個代理直接寫檔，不需回傳內容。

### 子代理提示詞範本

```
你正在為書籍各章撰寫 {language} {article_type} 衛教文章。
如果你的環境可用 seo-writing-skill、copywriting-optimizer、humanizer-zh-tw skills，請叫用。
禁止重現版權文本長段；以章節觀念為基礎撰寫原創說明文章。

處理範圍：第 {start_num}–{end_num} 章

來源檔案：
{list of chapter .txt file paths}

輸出目錄：{output_dir}

請建立下列 Markdown 新檔（不要覆寫已有檔案）：
{list of expected output filenames}

文章要求：
1. 語言：繁體中文（台灣）
2. 讀者：一般民眾、有健康需求者及家屬
3. 以書章為主要來源，以衛教語言解說，詳盡說明，不限字數
4. YAML frontmatter 需含：title、description（120–155 字）、keywords（10–15 詞）、date、tags、schema_type: "Article"、source_chapter、source_book
5. frontmatter 後緊接 H1 標題
6. 必要段落：核心觀念、章節重點、衛教說明、自我覺察練習、何時需要尋求專業協助、常見問題 FAQ（3–5 題）、參考資料
7. {safety_note_block}
8. 專業術語首次出現時提供淺白說明
9. 涉及創傷、羞恥或痛苦記憶的練習，須加入接地、節奏感與「可以停下來」的提示
10. 文末附 JSON-LD Article 與 FAQPage 區塊
11. 外部臨床資料標 [NEEDS VERIFICATION]；書籍引用格式：{book_citation}
12. 避免 AI 寫作慣用語，無過度粗體、破折號或公式化結尾

回傳：已建立的文章清單及各篇焦點簡述
```

**安全提醒範本**（safety_note=true 時）：
```
安全提醒：[topic]可能有醫療風險。本文是教育文章，不是診斷或治療。
如果症狀嚴重、快速變化，出現昏倒、胸痛、自殺意念、自傷，
或明顯異常行為，請盡快尋求醫療與心理健康專業協助。
```

---

## 第四部分：Auto-Optimize（自動優化每篇文章）

> 只有 `auto_optimize=true` 時執行此部分。這是本 skill 相對 book-worm 的核心擴充。

### 步驟 1：確認生成的文章清單

```bash
# 列出 output_dir 下所有新建的 .md 檔
Get-ChildItem "{output_dir}" -Filter "*.md" | Select-Object Name
```

### 步驟 2：對每篇文章跑完整 optimize-article 七階段

**若 `optimize_parallel=true`**：用 Task 並行啟動，每篇一個子代理：

```
optimize-article 子代理提示詞：

對以下文章執行完整優化流程（七階段 + 品質閘門 G1–G9）：
檔案：{article_path}

執行順序：
1. 診斷 + SEO 十項審核（seo-article-checker）
2. 補洞 + 結構修整（Verify-then-Edit：每次 Edit 前先 Read 精確原文）
3. FAQ + JSON-LD FAQPage schema
4. 引用逐條查證（citation-verifier → Crossref API fallback）
5. Sugarman 文案優化（copywriting-optimizer）
6. 中文人味化（humanizer-zh-tw）
7. 自我回歸測試（Diff 核查 + 鏈結掃描 + AI 痕跡掃描）

品質閘門 G1–G9 全綠後，存為 {article_stem}-v2.md。
輸出變更摘要表（面向 / 原狀 / 改後 / 理由）。
```

**若 `optimize_parallel=false`**：依序逐篇優化。

### 步驟 3：優化品質閘門（每篇）

| # | 閘門 | 標準 |
|---|------|------|
| G1 | 引用可解析 | DOI 可解析，期刊名正確 |
| G2 | 無誤植殘留 | 已知易錯引用已更正 |
| G3 | 無 AI 寫作痕跡 | 無破折號濫用、三段式、公式化語句 |
| G4 | 無佔位文字 | 無 TODO、[待驗證] 未標示、空連結 |
| G5 | 標題階層合理 | H2 ≤ 6 個，無跳階 |
| G6 | FAQ schema 有效 | JSON-LD FAQPage 語法正確 |
| G7 | frontmatter 完整 | title、description、keywords 齊備 |
| G8 | 術語一致 | 全文關鍵詞用詞統一 |
| G9 | 無意外改動 | Diff 核查無段落遺漏或事實誤改 |

任何閘門失敗 → 自動回到對應階段修正 → 重跑閘門，不要要求使用者重新下指令。

---

## 第五部分：Assemble（組裝總覽）

### 步驟 1：驗證輸出

對每篇 `-v2.md` 確認：
- [ ] 檔案存在
- [ ] 以 `---` 開頭（YAML frontmatter）
- [ ] 含 H1 標題
- [ ] 含 `application/ld+json`
- [ ] 含 `FAQ`
- [ ] 含 `參考資料`
- [ ] 品質閘門 G1–G9 全綠

### 步驟 2：建立 index.md

```markdown
---
title: "{book_title} 衛教文章總覽"
description: "依據 {book_title} 各章重點整理的繁體中文衛教文章目錄。"
keywords: [...]
date: {date}
tags: [...]
schema_type: "CollectionPage"
source_book: "{book_citation}"
---

# {book_title} 衛教文章總覽

[安全提醒]

## 章節文章

1. [Chapter 1 title](01-slug-v2.md)
2. [Chapter 2 title](02-slug-v2.md)
...

## 建議閱讀順序

建議依章節順序閱讀。

## 參考資料

- {book_citation}
```

### 步驟 3：最終報告

輸出完整摘要表：

```
| # | 原始檔 | 優化版 | 行數 | SEO 改善 | 引用修正 | 狀態 |
|---|--------|--------|------|---------|---------|------|
| 1 | 01-xxx.md | 01-xxx-v2.md | 203 | +FAQ, +schema | 1 條更正 | G1-G9 ✅ |
...
```

列出所有殘留的 `[NEEDS VERIFICATION]` 標記供人工複核。

---

## 快速指令參考

| 目的 | 做法 |
|------|------|
| 啟動完整流水線 | 提供書籍路徑，說明「一條龍轉製優化文章」 |
| 只跑萃取 | 說明「只要 extract，不要 optimize」 |
| 只跑優化（已有文章） | 改用 `optimize-article` skill |
| 跳過優化 | 說明 `auto_optimize=false` |
| 並行 vs 序列優化 | 說明 `optimize_parallel=true/false` |

## 常見錯誤排除

| 錯誤 | 解法 |
|------|------|
| chapters.json 為空 | 手動讀 full_text.txt 找目錄 |
| MOBI/AZW3 萃取失敗 | 確認 Calibre 已安裝（ebook-convert） |
| 優化後引用仍未通過 G1 | 回到 optimize 子代理，指定強制重查該條引用 |
| 多代理寫入同一檔案 | 確認每個代理的輸出檔名唯一 |
| Edit 誤植 | 子代理需執行 Verify-then-Edit（Read → Edit → 確認） |
