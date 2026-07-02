---
name: public-api-finder
description: >
  搜尋和發現 public-apis/public-apis 倉庫中的 1400+ 個免費公開 API。
  支援按分類、關鍵字、認證方式、HTTPS、CORS 等條件過濾搜尋。
  即時從 GitHub 抓取最新資料。
  觸發詞：「找 API」「搜尋 API」「有哪些 API」「API 列表」「免費 API」
  「查 API」「public api」「find api」「search api」「API 搜尋」。
version: 1.0.0
tags:
  - api
  - search
  - public-apis
  - discovery
---

# Public API Finder

搜尋 [public-apis/public-apis](https://github.com/public-apis/public-apis) 倉庫中的 1400+ 個公開 API。

## 觸發條件

當使用者提到以下任何情境時觸發此 skill：
- 尋找特定類型的 API（天氣、金融、音樂等）
- 搜尋免費或無需認證的 API
- 瀏覽某個分類下的 API 列表
- 比較同類型的 API 選項
- 「有沒有 XXX 的 API」

## 工作流程

### Step 1: 抓取最新資料

從 GitHub 即時抓取 README.md：

```
使用 zread_read_file 工具：
  repo_name: "public-apis/public-apis"
  file_path: "README.md"
```

如果 zread 工具不可用，使用 web-reader 工具：
```
url: "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
```

### Step 2: 解析資料結構

README.md 的結構為：
- `### CategoryName` — 分類標題（共 51 個分類）
- 每個分類下是一個 markdown 表格，欄位為：

| 欄位 | 格式 | 範例 |
|------|------|------|
| API | `[Name](URL)` | `[Cat Facts](https://alexwohlbruck.github.io/cat-facts/)` |
| Description | 純文字 | `Daily cat facts` |
| Auth | `` `apiKey` `` 或 `No` | `` `OAuth` `` |
| HTTPS | `Yes` 或 `No` | `Yes` |
| CORS | `Yes`、`No` 或 `Unknown` | `Unknown` |

### Step 3: 根據使用者需求過濾

從使用者的自然語言中提取過濾條件：

**分類過濾（category）：**

| 中文關鍵字 | 對應分類 |
|-----------|---------|
| 動物 | Animals |
| 動漫 | Anime |
| 惡意軟體/防毒 | Anti-Malware |
| 藝術/設計 | Art & Design |
| 認證/授權 | Authentication & Authorization |
| 區塊鏈 | Blockchain |
| 書籍 | Books |
| 商業 | Business |
| 日曆 | Calendar |
| 雲端/檔案 | Cloud Storage & File Sharing |
| CI/持續整合 | Continuous Integration |
| 加密貨幣 | Cryptocurrency |
| 匯率/貨幣 | Currency Exchange |
| 資料驗證 | Data Validation |
| 開發 | Development |
| 字典 | Dictionaries |
| 文件/生產力 | Documents & Productivity |
| 電子郵件/Email | Email |
| 娛樂 | Entertainment |
| 環境 | Environment |
| 活動/事件 | Events |
| 金融/財經 | Finance |
| 食物/餐飲 | Food & Drink |
| 遊戲/漫畫 | Games & Comics |
| 地理/定位/地圖 | Geocoding |
| 政府 | Government |
| 健康/醫療 | Health |
| 工作/職缺 | Jobs |
| 機器學習/AI/ML | Machine Learning |
| 音樂 | Music |
| 新聞 | News |
| 開放資料 | Open Data |
| 開源 | Open Source Projects |
| 專利 | Patent |
| 人格/心理測驗 | Personality |
| 電話 | Phone |
| 攝影/照片 | Photography |
| 程式設計 | Programming |
| 科學/數學 | Science & Math |
| 安全/資安 | Security |
| 購物 | Shopping |
| 社交/社群 | Social |
| 運動/健身 | Sports & Fitness |
| 測試資料 | Test Data |
| 文字分析/NLP | Text Analysis |
| 追蹤/物流 | Tracking |
| 交通 | Transportation |
| 短網址 | URL Shorteners |
| 車輛 | Vehicle |
| 影片/視頻 | Video |
| 天氣/氣象 | Weather |

**認證過濾（auth）：**
- 「免費」「不用申請」「無需認證」「no auth」→ `auth = "No"`
- 「需要 key」「要 API key」→ `auth = "apiKey"`
- 「OAuth」→ `auth = "OAuth"`

**HTTPS 過濾：**
- 「安全」「HTTPS」→ `https = "Yes"`

**CORS 過濾：**
- 「跨域」「前端呼叫」「瀏覽器」「CORS」→ `cors = "Yes"`

**關鍵字搜尋：**
- 在 API 名稱和描述中搜尋（case-insensitive）

### Step 4: 格式化輸出

輸出格式化表格，每次最多顯示 20 筆結果：

```markdown
## 搜尋結果：{Category} APIs

找到 **{count}** 個符合條件的 API

| # | API | 描述 | 認證 | HTTPS | CORS |
|---|-----|------|------|-------|------|
| 1 | [Name](url) | Description... | `apiKey` | Yes | Unknown |
| 2 | [Name](url) | Description... | No | Yes | Yes |

### 篩選條件
- 分類：{Category}
- 認證：{auth filter or 不限}
- HTTPS：{filter or 不限}
- CORS：{filter or 不限}
```

如果結果超過 20 筆，分頁顯示並告知使用者可以縮小範圍。

### Step 5: 後續動作

搜尋完成後，詢問使用者：
1. 是否要查看某個 API 的詳細資訊並生成呼叫範本（→ 觸發 `api-call-builder` skill）
2. 是否要調整過濾條件重新搜尋
3. 是否要匯出結果到 Obsidian 知識庫（`D:\obdidian\03-資源庫\Public APIs\`）

## 51 個分類完整列表

Animals, Anime, Anti-Malware, Art & Design, Authentication & Authorization,
Blockchain, Books, Business, Calendar, Cloud Storage & File Sharing,
Continuous Integration, Cryptocurrency, Currency Exchange, Data Validation,
Development, Dictionaries, Documents & Productivity, Email, Entertainment,
Environment, Events, Finance, Food & Drink, Games & Comics, Geocoding,
Government, Health, Jobs, Machine Learning, Music, News, Open Data,
Open Source Projects, Patent, Personality, Phone, Photography, Programming,
Science & Math, Security, Shopping, Social, Sports & Fitness, Test Data,
Text Analysis, Tracking, Transportation, URL Shorteners, Vehicle, Video, Weather

## 與其他 Skill 的協作

- 搜尋到 API 後 → 建議使用 `api-call-builder` 生成呼叫範本
- 使用者要建知識庫 → 生成 Obsidian 分類筆記到 `D:\obdidian\03-資源庫\Public APIs\`
