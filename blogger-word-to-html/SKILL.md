---
name: blogger-word-to-html
description: |
  Use when converting a Word .docx article into Blogger-ready HTML for 李政洋身心診所部落格。
  Triggers: 'Word 轉 HTML'、'docx 轉 Blogger'、'Blogger 排版'、'產出 Blogger HTML'、
  'word to blogger html'，或收到一份 .docx 並指定要貼入 Blogger「HTML 檢視」時。
  涵蓋標題階層、文章目錄、表格、重點提示框、固定預約 CTA、FAQ、JSON-LD 與診所標準 CSS。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  trigger: 將 Word .docx 文章一次轉成可直接貼入 Blogger HTML 檢視的單一 HTML 字串
  output: 單一 HTML 檔（<!--more-->、根容器、預約 CTA、FAQ、JSON-LD、完整 CSS；不含網頁字型）
  fixed_cta: https://lin.ee/mUIBMWa
  root_id: app-2025-trd-paradigm-failure
---

# blogger-word-to-html：Word 文件 → Blogger HTML 一次性轉換器

## Overview

你是一位同時具備**前端工程、SEO 編輯、Blogger 排版、Word .docx 解析、Schema.org JSON-LD、台灣繁中內容**能力的專家。任務只有一個：**接收一份 Word `.docx`，輸出一份可直接貼入 Blogger「HTML 檢視」的單一 HTML**。

**核心鐵律：最終回應只能包含 HTML 本身。** 不解釋、不前言、不修改摘要、不 SEO 分析、不檢核表、不用 Markdown 程式碼圍欄、不印 Word 檔名、不印無效圖片網址、不印虛構的延伸閱讀。

## When to Use

**Use when：**
- 使用者說「Word 轉 HTML」「docx 轉 Blogger」「Blogger 排版」「產出 Blogger HTML」「word to blogger html」。
- 使用者直接丟一份 `.docx` 並說要貼上 Blogger。
- 內容是李政洋身心診所衛教文章、心理學科普、健康知識型長文。

**Do NOT use when：**
- 使用者要的是 PDF/EPUB 書籍轉文章（改用 `book-worm` 或 `book-worm-auto-optimize`）。
- 使用者要做 SEO 文章優化 / 去 AI 味 / 文案潤飾（改用 `optimize-article` / `speak-human-tw` / `copywriting-optimizer`）。
- 使用者只是要純 Markdown 而非 Blogger HTML（改用 `markitdown`）。

---

## 一、執行流程

收到 Word 文件後，依序執行：

1. 分析文章主題、主要關鍵字與搜尋意圖。
2. 辨識標題、段落、清單、表格、圖片、引言、提示框、參考文獻及 FAQ。
3. 建立語意清楚的 HTML 標題階層。
4. 製作文章目錄。
5. 將圖片轉換成 Blogger 圖片格式。
6. 在 FAQ 前插入固定的預約與延伸閱讀區塊。
7. 保留或建立 JSON-LD 結構化資料。
8. 加入完整 CSS。
9. 進行 SEO、內容完整性、錯字、連結與 HTML 結構檢查（內部進行，不輸出）。
10. **僅輸出可直接貼入 Blogger 的 HTML。**

## 二、SEO 與內容排版規則

### 1. 搜尋意圖
- 開頭直接回應讀者主要疑問。
- 主章節與讀者可能搜尋的問題一致。
- **禁止**為了 SEO 加入原文沒有的內容。
- **禁止**虛構研究結果、統計、疾病資訊或治療效果。

### 2. 主要關鍵字
若文件提供關鍵字：
- 保留完整比對的主要關鍵字。
- 自然放入文章開頭。
- 至少出現在一個 `<h2>` 中。
- 視需要自然出現在 FAQ。
- 不堆疊、不強改專有名詞。

若未提供，自行辨識一個最適關鍵字，但**不可**把關鍵字分析文字寫進文章。

### 3. 文章標題
- 正文**原則上不要**重複建立 `<h1>`（Blogger 文章標題欄位已是 `<h1>`）。
- Word 最上方的文章標題可不放入正文。
- 第一個正文標題從 `<h2>` 開始。
- **禁止跳級**（例如 `<h2>` 後直接 `<h4>`）。

### 4. 開頭導言
開頭 2~4 個簡潔段落，包含：讀者問題、本文核心問題、讀完能得到什麼。

具摘要／核心理念／導讀性質的段落用：
```html
<p class="strong-lead">文字內容</p>
```

**禁止誇大承諾**：保證治癒、完全根治、一定有效、最有效、零風險。

---

## 三、頂層 HTML 結構

### 1. 字型：一律不得加入 Google Fonts
**禁止**輸出任何指向 `fonts.googleapis.com` / `fonts.gstatic.com` 的 `<link>`，
也不得使用 `@font-face` 或 `@import` 載入網頁字型。字型完全由下方 CSS 的
`--font-body` / `--font-heading` 系統字型堆疊決定。

規則來由（2026-08-26 實測）：本 skill 舊版固定輸出三行 Google Fonts 連結。
由於那段 markup 會落在**文章內文**裡，等於每產出一篇文章就夾帶一次 ——
245 篇抽樣中 34% 中鏢，推估全站約 503 / 1,466 篇。線上實測單篇文章因此拉下
**38 個字型檔、1,982 KB，佔 3,593 KB 頁面的 55%**，其中幾乎全是 Noto Sans TC
的 CJK 子集。Blogger 主題本身完全沒有網頁字型、早就用系統字型堆疊，
這段連結是在跟主題打架。

系統堆疊在各平台的中文渲染都沒問題：Windows 微軟正黑、macOS/iOS 蘋方、
Android Noto Sans CJK。
### 2. 首圖（Optional）
```html
<div class="separator" style="clear: both; text-align: center;">
  <a href="完整圖片網址" style="margin-left: 1em; margin-right: 1em;">
    <img alt="描述圖片內容的替代文字" border="0"
         data-original-height="高度" data-original-width="寬度"
         src="完整圖片網址" />
  </a>
</div>
```
- 保留原始圖片順序，放在相關段落附近。
- `alt` 必須**描述內容**，禁用「圖片」「照片」。
- **禁止虛構網址**。無網址時改放註解：
  ```html
  <!-- 圖片位置：請手動上傳並補入 Blogger 圖片網址 -->
  ```

### 3. Blogger 閱讀更多標記
在首圖之後（若無首圖則置於 HTML 最前）插入：
```html
<!--more-->
```

### 4. 根容器
```html
<div id="app-2025-trd-paradigm-failure">
  <div class="article-content">
    <!-- 文章內容 -->
  </div>
</div>
```
**CSS `<style>` 不可放進 `.article-content` 裡面。**

---

## 四、文章目錄

在導言後、第一個主要章節前建立。只收 `<h2>` 與重要的 `<h3>`。

```html
<nav class="table-of-contents" aria-label="文章目錄">
  <p class="toc-title">文章目錄</p>
  <ol>
    <li><a href="#section-id">章節名稱</a></li>
    <li>
      <a href="#section-id-2">章節名稱</a>
      <ol>
        <li><a href="#subsection-id">次章節名稱</a></li>
      </ol>
    </li>
  </ol>
</nav>
```

規則：
- 每個連結必須對應**真實存在**的標題 `id`。
- `id` 用簡短可讀的英文小寫字串，單字間用連字號。
- **禁止**重複 `id`、中文標點、空格。
- FAQ 標題固定 `id="faqs"`。

---

## 五、Word 內容映射規則

### 1. 主要章節 → `<h2>`
例如「一、挑戰傳統認知」「第一部分：創傷如何影響大腦」→
```html
<h2 id="semantic-id">挑戰傳統認知</h2>
```
- 去除「一、」「第一章」「第一部分」等純編號。
- 若編號具理解價值可保留於文字中。
- 去除不必要的引號，不改變原意。

### 2. 次標題 → `<h3>`
例如「1. 治療抵抗性憂鬱症」「【成為講師步驟一】累積專業知識和經驗」→
```html
<h3 id="semantic-id">累積專業知識和經驗</h3>
```
- 去除開頭數字與純裝飾括號。
- 保留真正具意義的「步驟一」「方法一」。
- **禁止**用 `<strong>` 代替標題。

### 3. 三級標題 → `<h4>`
例如「（1）二元模型的分類對比」「臨床表現」→
```html
<h4>二元模型的分類對比</h4>
```
去純編號，但不得刪除具語意的文字。

### 4. 一般段落
```html
<p>段落內容</p>
```
**禁止**：大量 `<br>` 代替段落、空白 `<p></p>`、`MsoNormal`、行內字型／字級／顏色、無意義 `<span>`。

### 5. 重點引言 `.strong-lead`
具核心理念、摘要、導讀、重要結論、需優先理解性質的段落：
```html
<p class="strong-lead">
  <strong>核心理念：</strong>段落內容
</p>
```

### 6. 清單
```html
<ul>
  <li>項目一</li>
  <li>項目二</li>
</ul>
```
```html
<ol>
  <li>步驟一</li>
  <li>步驟二</li>
</ol>
```
- 必須保留巢狀清單。
- 每個 `<li>` 是完整語意單位，不可拆成獨立段落。
- 步驟／原則／排序用 `<ol>`；並列資訊用 `<ul>`。

### 7. 重點提示框 `.highlight-box`
Word 中標示為：重點提示／核心重點／臨床情境舉例／注意事項／實務建議／研究提醒：
```html
<div class="highlight-box">
  <p class="highlight-title">臨床情境舉例</p>
  <p>說明文字。</p>
  <ul>
    <li>項目一</li>
    <li>項目二</li>
  </ul>
</div>
```
- 標題**不得**保留 emoji。
- 不可為美化把普通段落全轉成提示框。
- 提示框內可用 `<p>`、`<ul>`、`<ol>`。
- **禁止**在提示框內放新的 `<h2>`。

### 8. 表格
```html
<div class="table-container">
  <table>
    <thead>
      <tr>
        <th scope="col">欄位一</th>
        <th scope="col">欄位二</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>內容一</td>
        <td>內容二</td>
      </tr>
    </tbody>
  </table>
</div>
```
- 第一列若為欄名放 `<thead>`，其餘放 `<tbody>`。
- **禁止遺漏**任何儲存格內容。
- 合併儲存格可用 `rowspan`／`colspan`。
- **禁止**固定像素寬度、Word 原始表格樣式。

### 9. 分隔線
```html
<hr />
```
禁止用連續破折號或底線模擬。

### 10. 粗體、斜體、超連結
```html
<strong>重點文字</strong>
<em>文字內容</em>
<a href="完整網址">連結文字</a>
<!-- 外部連結建議 -->
<a href="完整網址" rel="noopener noreferrer" target="_blank">連結文字</a>
```
- 保留 Word 中有效的內外部連結。
- **禁止虛構網址**。
- **禁止**把整個長網址當連結文字（DOI 除外）。
- 連結文字需清楚表達目的。
- 可信研究／政府／專業機構來源可保留為外部連結。

---

## 六、固定插入：FAQ 前預約與延伸閱讀區塊

**位置順序（不可調換）：**
1. 文章主要內容
2. 預約與延伸閱讀區塊
3. FAQ
4. 參考文獻
5. JSON-LD
6. CSS

**固定 HTML（每篇只插入一次）：**
```html
<section class="pre-faq-actions" aria-label="預約與延伸閱讀">
  <div class="appointment-card">
    <p class="action-title">需要進一步的專業協助嗎？</p>
    <p>
      歡迎預約李政洋身心診所治療師，讓專業人員陪你進一步了解目前的困擾與適合的協助方向。
    </p>
    <p class="action-link">
      <a href="https://lin.ee/mUIBMWa" rel="noopener noreferrer" target="_blank"
      >歡迎預約李政洋身心診所治療師</a>
    </p>
  </div>

  <div class="related-reading">
    <p><strong>延伸閱讀：</strong></p>
  </div>
</section>
```

**硬規則：**
- 預約網址**固定為 `https://lin.ee/mUIBMWa`**，不得修改、縮短或替換。
- 「延伸閱讀」後方**必須保持空白**，讓使用者手動補入。
- **禁止**杜撰延伸閱讀標題或網址。
- **禁止**放到 FAQ 後方。
- 每篇文章只插入一次。
- Word 原本已有同區塊需合併避免重複。

---

## 七、FAQ 規則

### 1. FAQ 標題（統一格式）
```html
<h2 id="faqs">常見問題 FAQ</h2>
```
即使原文寫「常見問題」「FAQ」「問與答」「文章主題 FAQ」，仍統一為上述。

### 2. FAQ 問答格式
```html
<section class="faq-section">
  <h2 id="faqs">常見問題 FAQ</h2>

  <div class="faq-item">
    <h3 id="faq-question-1">問題一？</h3>
    <p>回答內容。</p>
  </div>

  <div class="faq-item">
    <h3 id="faq-question-2">問題二？</h3>
    <p>回答內容。</p>
  </div>
</section>
```
- 問題必須是問句。
- 回答直接回應問題。
- 保留原文 FAQ，**禁止虛構**醫療建議或研究結論。
- 原文沒有 FAQ 時不必憑空新增大量問答；可整理 3~6 題。
- FAQ 可自然含主要關鍵字，**禁止堆疊**。
- **禁止**把預約資訊當成 FAQ 問題。

---

## 八、參考文獻

```html
<div class="references">
  <h3>主要參考文獻</h3>
  <ol>
    <li>參考文獻內容</li>
  </ol>
</div>
```
- 保留作者、年份、文章名、期刊、卷期、頁碼、DOI、網址。
- **禁止自行補造缺漏的 DOI**。
- DOI/識別碼用 `<code>`：
  ```html
  <code>10.xxxx/xxxxx</code>
  ```
- DOI 可連結時：
  ```html
  <a href="https://doi.org/10.xxxx/xxxxx" rel="noopener noreferrer" target="_blank">
    <code>10.xxxx/xxxxx</code>
  </a>
  ```
- 「主要參考文獻」「其他參考資料」用 `<h3>`，清單用 `<ol>`。
- **禁止**將參考文獻混入 FAQ。
- 原文沒有參考文獻時**禁止虛構**。

---

## 九、JSON-LD 結構化資料

### 1. 保留既有 JSON-LD
若輸入已附 JSON-LD：**必須完整保留**、**禁止**顯示為一般文字、**禁止**刪除既有欄位、檢查 JSON 語法有效、**禁止**用 HTML 註解包住。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article"
}
</script>
```

### 2. FAQPage
文章實際存在 FAQ 時可建立／保留 `FAQPage`。**問題與答案必須與頁面可見 FAQ 完全一致**，禁止加入頁面不存在的問答。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "問題文字",
      "acceptedAnswer": { "@type": "Answer", "text": "回答文字" }
    }
  ]
}
</script>
```

### 3. 禁止虛構
作者姓名、發布日期、修改日期、圖片網址、網頁永久網址、醫療審閱者、評分、評論數量、組織資料 — **沒有資料就省略欄位**，不可猜測。

---

## 十、CSS 樣式

HTML 末尾**必須保留完整 CSS**，不得刪除、縮寫或改寫原有規則。在原 CSS 的 `@media` 規則**之前**加入新增樣式（目錄、CTA、FAQ）。

完整 CSS 必須用以下包裝：
```html
<style>/* <![CDATA[ */
/* 使用者提供的完整 CSS */
/* 加上本規格新增的目錄、CTA 與 FAQ CSS */
/* ]]> */</style>
```

### 必須包含的完整 CSS（不可省略）

```css
#app-2025-trd-paradigm-failure {
  /* --- Design Tokens --- */
  --font-body: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif;
  --font-heading: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif;
  --color-surface: #ffffff;
  --color-title: #2c3e50;
  --color-text: #34495e;
  --color-text-light: #526c84;
  --color-accent: #3498db;
  --color-accent-hover: #2980b9;
  --color-accent-bg: #eaf2f8;
  --color-border: #e0e5ea;
  --color-table-header: #f8f9fa;
  --shadow-level-1: 0 4px 12px rgba(0,0,0,.08);

  font-family: var(--font-body);
  color: var(--color-text);
  line-height: 1.8;
  background-color: transparent;
  padding: 1rem 0;
  box-sizing: border-box;
}
#app-2025-trd-paradigm-failure *,
#app-2025-trd-paradigm-failure *::before,
#app-2025-trd-paradigm-failure *::after { box-sizing: border-box; }
#app-2025-trd-paradigm-failure .article-content {
  background-color: var(--color-surface);
  padding: 20px 30px;
  border-radius: 8px;
  box-shadow: var(--shadow-level-1);
}
#app-2025-trd-paradigm-failure h1,
#app-2025-trd-paradigm-failure h2,
#app-2025-trd-paradigm-failure h3,
#app-2025-trd-paradigm-failure h4 {
  font-family: var(--font-heading);
  color: var(--color-title);
  margin: 1.5em 0 0.8em;
  line-height: 1.4;
  font-weight: 700;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--color-border);
}
#app-2025-trd-paradigm-failure h2 { font-size: 1.8em; }
#app-2025-trd-paradigm-failure h3 { font-size: 1.4em; border-bottom-style: dashed; }
#app-2025-trd-paradigm-failure h4 { font-size: 1.1em; font-weight: 600; border-bottom: none; }
#app-2025-trd-paradigm-failure p { margin: 0 0 1.2em; }
#app-2025-trd-paradigm-failure a {
  color: var(--color-accent);
  text-decoration: none;
  transition: color 0.2s ease;
}
#app-2025-trd-paradigm-failure a:hover {
  color: var(--color-accent-hover);
  text-decoration: underline;
}
#app-2025-trd-paradigm-failure strong,
#app-2025-trd-paradigm-failure b { font-weight: 700; color: var(--color-title); }
#app-2025-trd-paradigm-failure .strong-lead {
  font-size: 1.1em;
  font-weight: 500;
  color: var(--color-title);
  border-left: 4px solid var(--color-accent);
  padding-left: 1em;
  margin: 1.5em 0;
}
#app-2025-trd-paradigm-failure ul,
#app-2025-trd-paradigm-failure ol { margin: 0 0 1.5em; padding-left: 2em; }
#app-2025-trd-paradigm-failure li { margin-bottom: 0.8em; padding-left: 0.5em; }
#app-2025-trd-paradigm-failure ul ul,
#app-2025-trd-paradigm-failure ul ol,
#app-2025-trd-paradigm-failure ol ul,
#app-2025-trd-paradigm-failure ol ol { margin-top: 0.5em; margin-bottom: 0.8em; }
#app-2025-trd-paradigm-failure li::marker { color: var(--color-accent); font-weight: bold; }
#app-2025-trd-paradigm-failure .highlight-box {
  background-color: var(--color-accent-bg);
  border: 1px solid var(--color-border);
  border-left: 5px solid var(--color-accent);
  padding: 1.5em;
  margin: 2em 0;
  border-radius: 4px;
}
#app-2025-trd-paradigm-failure .highlight-box .highlight-title {
  font-size: 1.2em;
  font-weight: bold;
  color: var(--color-title);
  margin-top: 0;
}
#app-2025-trd-paradigm-failure .highlight-box ul { margin-bottom: 0; }
#app-2025-trd-paradigm-failure .table-container { overflow-x: auto; margin: 2em 0; }
#app-2025-trd-paradigm-failure table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid var(--color-border);
}
#app-2025-trd-paradigm-failure th,
#app-2025-trd-paradigm-failure td {
  padding: 12px 15px;
  text-align: left;
  border: 1px solid var(--color-border);
  vertical-align: top;
}
#app-2025-trd-paradigm-failure thead th {
  background-color: var(--color-table-header);
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--color-title);
}
#app-2025-trd-paradigm-failure tbody tr:nth-child(even) { background-color: #fdfdfd; }
#app-2025-trd-paradigm-failure hr {
  border: none;
  height: 1px;
  background-color: var(--color-border);
  margin: 3em 0;
}
#app-2025-trd-paradigm-failure .references { font-size: 0.9em; color: var(--color-text-light); }
#app-2025-trd-paradigm-failure .references ol { padding-left: 1.5em; line-height: 1.7; }
#app-2025-trd-paradigm-failure .references li { margin-bottom: 1em; }
#app-2025-trd-paradigm-failure .references code {
  font-family: monospace;
  background-color: #ecf0f1;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 0.95em;
}

/* === 本規格新增（目錄、CTA、FAQ）— 必須在 @media 之前 === */
#app-2025-trd-paradigm-failure .table-of-contents {
  background-color: #f8fafc;
  border: 1px solid var(--color-border);
  border-left: 5px solid var(--color-accent);
  border-radius: 6px;
  margin: 2em 0;
  padding: 1.25em 1.5em;
}
#app-2025-trd-paradigm-failure .table-of-contents .toc-title {
  color: var(--color-title);
  font-family: var(--font-heading);
  font-size: 1.2em;
  font-weight: 700;
  margin: 0 0 0.8em;
}
#app-2025-trd-paradigm-failure .table-of-contents ol { margin-bottom: 0; }
#app-2025-trd-paradigm-failure .table-of-contents li { margin-bottom: 0.5em; }
#app-2025-trd-paradigm-failure .pre-faq-actions {
  border-top: 1px solid var(--color-border);
  margin: 3em 0 2em;
  padding-top: 2em;
}
#app-2025-trd-paradigm-failure .appointment-card {
  background-color: var(--color-accent-bg);
  border: 1px solid var(--color-border);
  border-left: 5px solid var(--color-accent);
  border-radius: 6px;
  margin-bottom: 1.5em;
  padding: 1.5em;
}
#app-2025-trd-paradigm-failure .appointment-card .action-title {
  color: var(--color-title);
  font-family: var(--font-heading);
  font-size: 1.2em;
  font-weight: 700;
  margin-bottom: 0.6em;
}
#app-2025-trd-paradigm-failure .appointment-card .action-link { margin-bottom: 0; }
#app-2025-trd-paradigm-failure .appointment-card .action-link a {
  display: inline-block;
  background-color: var(--color-accent);
  border-radius: 5px;
  color: #ffffff;
  font-weight: 700;
  padding: 0.7em 1.1em;
  text-decoration: none;
}
#app-2025-trd-paradigm-failure .appointment-card .action-link a:hover {
  background-color: var(--color-accent-hover);
  color: #ffffff;
  text-decoration: none;
}
#app-2025-trd-paradigm-failure .related-reading {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 1.2em 1.5em;
}
#app-2025-trd-paradigm-failure .related-reading p { margin-bottom: 0; }
#app-2025-trd-paradigm-failure .faq-item {
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5em;
}
#app-2025-trd-paradigm-failure .faq-item:last-child { border-bottom: none; }

@media (max-width: 768px) {
  #app-2025-trd-paradigm-failure .article-content { padding: 15px 20px; }
  #app-2025-trd-paradigm-failure h2 { font-size: 1.6em; }
  #app-2025-trd-paradigm-failure h3 { font-size: 1.3em; }
}
```

**禁止輸出**：`<html>`、`<head>`、`<body>`、Word XML、`class="MsoNormal"`、`font-family: Calibri`、`mso-` 開頭 CSS、Base64 圖片、JavaScript 互動元件、Bootstrap、Tailwind、外部 CSS 框架。

---

## 十一、文章排版與 SEO 檢核（內部進行，不輸出）

### 內容檢查
- 保留原文所有重要資訊，無遺漏段落。
- 與原文無矛盾。
- 修正明顯錯字與不自然斷行。
- 維持台灣繁體中文。
- 保留專有名詞、數字、年份、研究資料。
- 避免誇大／不實醫療宣稱。
- 資訊與數字一致性檢查。

### SEO 檢查
- 符合主要搜尋意圖。
- 主要關鍵字自然出現在開頭、至少一個 `<h2>`。
- 標題清楚描述章節內容。
- 保留相關內部連結與可信外部連結。
- 圖片具描述性 `alt`。
- FAQ 包含讀者常見長尾問題。
- 清楚但不誇大的品牌與預約資訊。

### HTML 檢查
- 只有一個根容器。
- 所有標籤正確關閉。
- 無重複 `id`。
- 目錄連結都能對應標題。
- 表格位於 `.table-container`。
- FAQ 前已插入預約及延伸閱讀區塊。
- 延伸閱讀保持空白。
- 預約網址完全正確（`https://lin.ee/mUIBMWa`）。
- JSON-LD 為有效 JSON。
- CSS 完整保留。
- 無 Word 垃圾標籤與行內樣式。

---

## 十二、固定輸出順序

最終 HTML 必須依序排列：

1. 首圖（若無則略過）
2. `<!--more-->`
3. 根容器開始
5. 文章導言
6. 文章目錄
7. 文章主要內容
8. 預約與延伸閱讀區塊
9. FAQ
10. 參考文獻
11. 根容器結束
12. JSON-LD
13. 完整 CSS

---

## 十三、輸出限制（硬規則）

**最終回答只能包含 HTML。**

**禁止輸出：**
- 「以下是轉換結果」之類的前言
- 任何說明文字或修改摘要
- SEO 分析或檢核表
- Markdown 程式碼圍欄（```` ``` ````）
- Word 文件名稱
- 無法使用的圖片網址
- 未經原文支持的延伸閱讀
- 未經原文支持的研究或醫療資訊

**直接輸出可貼入 Blogger HTML 檢視的完整程式碼。**

---

## Common Mistakes（常見錯誤）

| 錯誤 | 修正 |
|------|------|
| 在回應開頭加「以下是轉換後的 HTML」 | 刪除前言，直接從第一個 HTML 標籤開始輸出 |
| 把 CSS `<style>` 放進 `.article-content` 內 | 移到根容器外、整份 HTML 最尾端 |
| 忘記插 `<!--more-->` | 在首圖後（若無首圖則置於最前）補上 |
| 加入 Google Fonts `<link>` | 一律刪除，改用系統字型堆疊 |
| JSON-LD 內把中文標點寫成 `&#65292;` 這類實體 | 改回真實字元 `，、。？`；script 內的實體不會被解碼 |
| 預約網址改成其他診所或縮短 | 固定使用 `https://lin.ee/mUIBMWa` |
| 「延伸閱讀」自行填入文章標題 | 保持空白，僅留 `<p><strong>延伸閱讀：</strong></p>` |
| FAQ 標題用「常見問題」 | 統一為 `<h2 id="faqs">常見問題 FAQ</h2>` |
| 標題跳級（h2 → h4） | 補上中間層級 h3 |
| 表格沒包 `.table-container` | 補上外層 `<div class="table-container">` |
| 虛構圖片網址或 DOI | 改用 HTML 註解標示需手動補 |
| Word 編號沒去除（「一、」「1.」「（1）」） | 從標題文字移除，僅保留具語意的編號 |
| 用 Markdown 包住最終 HTML | 直接輸出純 HTML，不要 ```` ```html ```` 圍欄 |
