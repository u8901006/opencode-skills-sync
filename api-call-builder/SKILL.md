---
name: api-call-builder
description: >
  為指定的公開 API 生成呼叫範本程式碼（curl / Python / JavaScript）。
  自動抓取 API 文件頁面，分析端點、參數、認證方式，生成可直接使用的範本。
  觸發詞：「呼叫 API」「生成 API 範本」「API 怎麼用」「寫 API 請求」
  「call api」「api template」「api 範例」。
version: 1.0.0
tags:
  - api
  - code-generation
  - http
  - curl
  - python
  - javascript
---

# API Call Builder

為公開 API 生成可直接使用的呼叫範本程式碼。支援 curl、Python (requests)、JavaScript (fetch) 三種格式。

## 觸發條件

當使用者提到以下情境時觸發：
- 想要呼叫某個特定的 API
- 需要 API 的使用範例或範本
- 問「這個 API 怎麼用」
- 從 `public-api-finder` 搜尋結果中選擇了某個 API

## 前置依賴

- 使用者必須已指定目標 API（名稱或 URL）
- 如果未指定，先建議使用 `public-api-finder` skill 搜尋

## 工作流程

### Step 1: 確認目標 API

從使用者的訊息中提取：
- API 名稱（如 "OpenWeatherMap"）
- API 文件 URL（如果有）

如果只有名稱，先使用 `public-api-finder` 在 public-apis 列表中查找對應的 URL 和基本資訊。

### Step 2: 抓取 API 文件

使用 `web-reader` 工具訪問 API 的文件頁面：

```
web-reader_webReader:
  url: "<API documentation URL>"
  return_format: "markdown"
```

從文件中提取：
- Base URL / Endpoint URLs
- HTTP Methods (GET, POST, PUT, DELETE)
- Required / Optional Parameters
- Request Headers
- Response Format (JSON, XML, etc.)
- Authentication Method & Placement (header, query, body)

如果文件頁面無法存取，使用從 public-apis 列表取得的資訊生成基本範本，並標註需確認。

### Step 3: 判斷認證類型並生成說明

根據從 public-apis 列表取得的 Auth 值：

| Auth 類型 | 範本處理方式 |
|-----------|------------|
| `No` | 無需額外認證，直接呼叫 |
| `apiKey` | 在範本中加入 `YOUR_API_KEY` 佔位符，並提供取得 key 的連結和步驟 |
| `OAuth` | 生成 OAuth 授權流程說明 + token 取得範本 |
| `X-Mashape-Key` | 在 Header 中加入 `X-Mashape-Key: YOUR_KEY` |
| `User-Agent` | 在 Header 中加入 `User-Agent` 欄位 |

### Step 4: 生成範本程式碼

為每個 API 生成三種格式的範本：

#### curl 範本

```bash
# {API Name} - {Brief Description}
# Docs: {Documentation URL}

curl -s -X GET \
  "https://api.example.com/v1/endpoint?param1=value1" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" | jq
```

#### Python 範本

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.example.com/v1"

response = requests.get(
    f"{BASE_URL}/endpoint",
    headers={"Authorization": f"Bearer {API_KEY}"},
    params={"param1": "value1"}
)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error {response.status_code}: {response.text}")
```

#### JavaScript 範本

```javascript
const API_KEY = "YOUR_API_KEY";
const BASE_URL = "https://api.example.com/v1";

const response = await fetch(
  `${BASE_URL}/endpoint?param1=value1`,
  {
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    }
  }
);

if (response.ok) {
  const data = await response.json();
  console.log(data);
} else {
  console.error(`Error ${response.status}: ${response.statusText}`);
}
```

### Step 5: 輸出格式

```markdown
## {API Name}

**文件：** {Documentation URL}
**認證：** {Auth Type}
{如果需要 API Key：**取得 Key：** {Registration URL}}

### curl
`​`bash
{curl template}
`​`

### Python
`​`python
{python template}
`​`

### JavaScript
`​`javascript
{js template}
`​`

### 常用端點

| 端點 | 方法 | 說明 | 認證 |
|------|------|------|------|
| `/v1/endpoint1` | GET | ... | 需要 |
| `/v1/endpoint2` | POST | ... | 需要 |

### 注意事項
- {Rate limiting info if available}
- {Pricing info if available}
- {Special requirements}
```

## 文件解析策略

### 有 OpenAPI/Swagger 規範的 API
1. 尋找 Swagger UI 或 OpenAPI JSON/YAML 連結
2. 直接解析規範檔案取得完整端點資訊
3. 這是最精確的方式

### 有獨立文件頁面的 API
1. 用 web-reader 抓取文件頁面
2. 尋找 "Endpoints"、"API Reference"、"Documentation" 等區塊
3. 提取 HTTP methods、URL patterns、parameters

### 文件較少或簡陋的 API
1. 從 public-apis 列表的描述中推斷
2. 使用 base URL + 常見 RESTful 路徑模式生成基本範本
3. 標註「此為推測範本，請參考官方文件確認」

## 與其他 Skill 的協作

- **public-api-finder** → 找到 API 後，自動銜接此 skill 生成範本
- **python-patterns** → 生成 Python 範本時遵循最佳實踐
- **frontend-patterns** → 生成 JavaScript 範本時遵循前端最佳實踐

## 常見問題

| 問題 | 處理方式 |
|------|---------|
| API 文件頁面無法存取 | 提供基本範本（基於 public-apis 列表資訊），標註需確認 |
| 找不到 API 註冊頁面 | 提供文件 URL，請使用者自行查找註冊入口 |
| API 已停用或失效 | 建議使用 `public-api-finder` 尋找替代方案 |
| 文件為非英文 | 仍然生成範本，但在注意事項中標註語言 |
