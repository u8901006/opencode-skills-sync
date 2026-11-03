# 最小資料契約

四份 UTF-8 輸入放在使用者指定的研究資料夾。`scripts/publish.py` 是離線生成工具：不檢索、不下載、不用模型代寫摘要。先做研究，再建立資料。

## project.json

```json
{
  "title": "研究主題",
  "subtitle": "證據支持到哪裡？",
  "start_date": "2021-01-01",
  "end_date": "2026-10-21",
  "as_of": "2026-10-21",
  "categories": [
    {"id": "direct", "label": "直接對象研究", "color": "green"},
    {"id": "indirect", "label": "一般族群證據", "color": "purple"},
    {"id": "clinical", "label": "健康與風險", "color": "slate"},
    {"id": "care", "label": "照護與介入", "color": "pink"}
  ],
  "method_note": "主題導向敘述性整理；資料庫、檢索日期與限制請見檢索紀錄。"
}
```

日期範圍可跨任意年數，不綁 2021–2026。`as_of` 為實際整理日，`end_date` 不可晚於它；使用者要到未來年度時，只檢索截至實際日並說明。分類 `id` 用英數與連字號，顏色支援 green/purple/slate/pink。

## papers.json

JSON 陣列，每篇至少包含：

```json
[
  {
    "id": "R01",
    "title": "Verified English article title",
    "authors": "Surname, Given; Surname, Given",
    "journal": "Verified Full Journal Title",
    "doi": "10.xxxx/verified-doi",
    "first_published": "2025-02-10",
    "issue_year": "2025",
    "category": "direct",
    "read_level": "abstract",
    "design": "研究設計",
    "population": "研究對象、樣本數、測量工具",
    "findings": "核實過的中文結果摘要",
    "limitations": "方法限制與不能推論之處",
    "implications": "與本主題的關係",
    "fulltext": [],
    "access_note": "未取得全文；只依摘要整理。",
    "source_url": "https://doi.org/10.xxxx/verified-doi",
    "license": "尚未核實全文授權",
    "retrieved_on": "2026-10-21",
    "fulltext_version": "僅摘要；無全文版本",
    "metadata_note": "日期或書目來源差異（若有）",
    "abstract_en": "可選：已取得的英文來源摘要，只保存本地"
  }
]
```

- `id` 是唯一 `R`＋兩位以上數字，如 R01、R100；可不連續。
- `doi` 不含 `https://doi.org/`。沒有 DOI 但確有正式來源時設為空字串，另提供可核實的 `source_url`；不為通過驗證捏造 DOI。
- `first_published` 允許 `YYYY`、`YYYY-MM`、`YYYY-MM-DD`。只有月份／年份時保留精度；與日期邊界部分重疊但無法確定是否合格，應先人工核對，工具會拒絕這種模糊邊界。
- `read_level`：`abstract`（僅摘要），或 `fulltext`（已取得且實際讀過正文）。
- `fulltext`：研究資料夾內的相對路徑陣列，同篇 XML＋HTML 只算一篇。例：`["fulltext/R01.xml", "fulltext/R01.html"]`。
- 有全文須提供授權與 `source_url`。不以假作者、示範 DOI 或占位結果交付。
- 有全文另須填 `retrieved_on`（實際下載日期）及 `fulltext_version`（出版 XML／出版 PDF／作者手稿等）；寫入全文 manifest。不同檔案若屬不同版本，分開保存取得紀錄，不把作者手稿叫出版版。
- `fulltext` 不含錯誤回應、摘要頁、登入頁。只有 abstract 級別時必須為空；如果已下載卻未讀，先讀完或另記原始候選，不可宣稱全文評讀。

## cards.json

```json
[
  {
    "title": "相關不是因果",
    "category": "direct",
    "study": "年份｜設計與樣本數",
    "takeaway": "讀者要記得的一句話",
    "description": "一項必要的限制或補充",
    "refs": ["R01"]
  }
]
```

卡片數與文獻數互不相依。每卡至少一個已存在來源 ID；若是純編輯提醒可引用支撐其脈絡的研究，不編造研究驗證過該提醒。

## article.html

```html
<h2 id="at-answer">先說結論</h2>
<p>清楚區分結果與推論。<a href="#at-ref-R01">[R01]</a></p>
<h2 id="at-limitations">不能過度解讀的地方</h2>
<p>將直接與間接證據、相關與因果分開。</p>
```

使用安全、靜態的 HTML 文章片段；`at-` 前綴 ID 避免主題衝突。不可包含 script、iframe、style、事件屬性、外部圖片、表單或本機路徑。引文採 `#at-ref-ID`。所有納入文獻至少被文章或卡片引用一次；若不支撐文章就不要為衝篇數納入。

## 生成產物

- `Blogger_貼上版.html`：Blogger 編輯器使用的片段。
- `Blogger_完整預覽.html`：含 head/body 的獨立頁面。
- `index.html`：本地入口及本地全文／摘要連結；不可直接公開此頁以免暴露全文。
- `summaries/Rxx_中文摘要.md`、`00_研究摘要總覽.md`。
- `01_文獻清單.csv`、`references.bib`。
- `02_研究文章.md`（由 HTML 擷取，手動檢查）、`README.md`。
- `fulltext/manifest.json`、`verification.json`。
- `screenshots/`、`browser-verification.json`：另外執行瀏覽器測試後產生。

自行保存 `search/`、候選清單及 `03_檢索與全文取得紀錄.md`：工具無法代替實際檢索紀錄。輸入未提供的科學內容不會自動補完。

範圍外的背景材料另存 `background/` 與候選清單，不放入受年份驗證的 `papers.json`，也不計入選定文獻篇數。若需要在網頁提及，直接以可核實的 HTTPS 來源連結且明示年份外背景，不能假填日期讓它通過。
