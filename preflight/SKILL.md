---
name: preflight
description: |
  書籍／EPUB／PDF pipeline 派發前的前置檢查。Use BEFORE dispatching book-worm,
  book-worm-auto-optimize, or any book-to-articles pipeline — verify book metadata
  (title/subtitle/author) via web search, confirm extracted text is valid UTF-8,
  validate chapter reading order (EPUB spine), and initialize a checkpoint file for
  resume. Triggers - preflight, 前置檢查, 派發前檢查, 檢查書檔, verify book metadata,
  validate epub, 開跑前檢查, 書籍 pipeline 前置檢查.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
metadata:
  trigger: "preflight, 前置檢查, 派發前檢查, 開跑前檢查, verify book metadata, validate epub"
  chains: "強制在 book-worm / book-worm-auto-optimize 派發前執行"
  source: "移植自 .claude/skills/preflight，補上 opencode frontmatter"
---

# Preflight — 書籍 pipeline 前置檢查

在派發任何書籍轉文章 pipeline 之前，依序完成以下五項檢查。**任何一項失敗就先修正並重新驗證，不得帶著問題開跑。**

> 這支 skill 直接對應 Claude Code Insights 報告的兩大摩擦：① EPUB 章節錯亂 + 編碼崩潰（全跑重來）② 配額中斷後無法 resume。完成 preflight 後才呼叫下游 pipeline。

## 輸入

- 書籍檔案路徑（PDF / EPUB / MOBI / AZW3）
- （可選）之後要執行的 pipeline 名稱與輸出目錄

## 步驟

### 1. Metadata 驗證

1. 從檔案 metadata（EPUB 的 OPF、PDF 的 document info）與封面頁抽出書名、副標題、作者、出版年。
2. 用 WebSearch（或 web-search-prime MCP）核對完整正確的書名與副標題。
3. 若與檔案內的資訊不一致，以查證後的版本為準，並在 dispatch 指令中使用正確版本。

> 備用查證管道（WebSearch 不可用時）：Gemini CLI flash
> `export PATH="/c/Users/u8901/AppData/Roaming/npm:$PATH" && gemini -m gemini-2.5-flash -p "<書名> 的正確完整書名與副標題"`

### 2. 編碼檢查

1. 抽取一段樣本文字（每章開頭各取一段），確認為有效 UTF-8。
2. 出現亂碼、replacement character（U+FFFD）或 decode error 時，偵測實際編碼（如 GB18030、Big5、latin-1），用正確編碼重新抽取，再驗證一次。
3. Python 抽取腳本一律明確指定 `encoding="utf-8"` 寫出，並設 `errors="strict"` 讓問題提早爆出來，而不是靜默寫入亂碼。

### 3. 章節閱讀順序驗證

1. **EPUB：** 以 OPF `<spine>` 順序為準解析章節，絕不可依檔名字母排序（`chapter10.xhtml` 會排在 `chapter2.xhtml` 前面）。
2. **PDF：** 以書籤（outline）或目錄頁為準切分章節。
3. 列出解析出的前 10 個章節標題，確認順序合理（封面 → 序 → 第一章 → 第二章 …）。順序可疑時停下來回報，附上完整章節清單。

### 4. 檢查點初始化

在輸出目錄建立 `_pipeline_progress.json`：

```json
{
  "source": "<書檔路徑>",
  "verified_title": "<查證後書名：副標題>",
  "verified_author": "<查證後作者>",
  "encoding": "utf-8 (verified)",
  "chapter_order_verified": true,
  "pipeline": "book-worm-auto-optimize",
  "started_at": "<ISO timestamp>",
  "chapters": [
    { "index": 1, "title": "...", "status": "pending", "output_file": null },
    { "index": 2, "title": "...", "status": "pending", "output_file": null }
  ]
}
```

之後的 pipeline（book-worm / book-worm-auto-optimize）每完成一篇文章就把對應章節改為 `"done"` 並填入 `output_file`。中斷重跑時先讀此檔，只處理 `pending` 項目。

### 5. 放行

以上全部通過後，輸出一份 preflight 報告：

```
## Preflight 報告
- 書名：<查證後書名>（原檔 metadata：<原始> → 修正／一致）
- 作者：<查證後作者>
- 編碼：UTF-8 (verified)
- 章節數：N，順序已確認（spine 順序）
- 檢查點：_pipeline_progress.json 已初始化（N 章 pending）
```

然後才呼叫對應的 pipeline skill（如 `book-worm` 或 `book-worm-auto-optimize`），並把查證後的 metadata 一併帶入 dispatch 指令。

## 失敗處理

| 狀況 | 處理方式 |
|------|---------|
| 書名／副標題查證不到或矛盾 | 停止，列出候選版本請使用者確認 |
| 編碼修復後仍有亂碼 | 停止並回報，列出問題章節與樣本 |
| 章節順序無法確定 | 停止，附完整章節清單請使用者確認順序 |
| 檔案不存在或格式不支援 | 停止，回報並建議先轉檔 |

## 與下游 pipeline 的銜接

```
preflight（本 skill）
  ├─ 驗證 metadata / 編碼 / 章節順序
  ├─ 初始化 _pipeline_progress.json
  └─ 呼叫 → book-worm 或 book-worm-auto-optimize
              └─ 開頭讀 _pipeline_progress.json，只跑 pending 章節
```
