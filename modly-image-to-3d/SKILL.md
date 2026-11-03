---
name: modly-image-to-3d
description: Use when converting images to 3D GLB models via the Modly MCP server, running batch image-to-3D pipelines, debugging Modly/Hunyuan3D errors (IndexError next_points, Unknown canonical modelId, empty model list, DINOv2/transformers key mismatch, mesh export None), installing Modly extensions, or sourcing CC0 images from Openverse for 3D generation.
---

# Modly 圖生 3D 批次管線

## Overview

管線：CC0 圖源（Openverse）→ Modly MCP（Hunyuan3D 2 Mini Turbo）→ GLB。
核心原則：**失敗先查「錯誤簽章表」，不要猜**——大多數故障有固定簽章與已知解法；改擴充程式碼或套件後**必須** POST `/extensions/reload`，否則子進程仍跑舊碼。

## 前置檢查（每次批次前）

1. Modly app 在跑：`GET http://127.0.0.1:8765/health` 回 ok
2. **VRAM 空出來**（`nvidia-smi`，使用量 < 6GB）——本機 LLM 服務常佔滿 12GB，會 OOM
3. 模型已註冊：`GET /model/all` 非空、`downloaded: true`
4. rembg 模型已快取（`~/.rembg/models/`，首次下載 1GB，GitHub 慢速屬正常，一次性）

## 錯誤簽章表（先查這裡）

| 症狀 | 根因 | 解法 |
| --- | --- | --- |
| `Unknown canonical modelId` / model list 空 / `GET /automation/capabilities failed` / `/model/status` 500 KeyError | `EXTENSIONS_DIR`（後端設定的擴充目錄）沒有擴充。看 `%APPDATA%\Modly\logs\runtime.log` 的 `[Registry] EXTENSIONS_DIR = ...` | 到該目錄安裝擴充：資料夾名必須等於 manifest `id`；有 setup.py 就 POST `/extensions/setup/{id}`，再 POST `/extensions/reload` |
| 載入模型時 DINOv2 `Missing key(s): ...q_proj... Unexpected: ...attention.attention...weights_in...` | transformers 5.x 改了模組命名，與權重不相容 | 擴充 venv 釘 `transformers==4.46.3`、`huggingface_hub<1.0`、`diffusers==0.31.0`，**然後 `/extensions/reload`**（子進程快取舊套件，不 reload 等於沒改） |
| `IndexError: min(): Expected reduction dim 0 to have non-zero size`（progress 19，Generating 3D shape） | FlashVDM adaptive-KV 解碼器對某些圖算出空 chunk；換 seed 只能救一部分 | 改擴充 `generator.py` 的 `_enable_flashvdm`：`enable_flashvdm_decoder(enabled=False)`（VanillaVolumeDecoder，慢數十秒但穩）→ `/extensions/reload` → 重跑 |
| `AttributeError: 'NoneType' object has no attribute 'export'`（progress 96，Exporting GLB） | 解碼退化回 None mesh，同上游問題 | 同上，vanilla decoder 一併解決 |
| 換過 generator.py/套件後重試「沒生效」 | ExtensionProcess 子進程快取 | `/extensions/reload`（stop 舊子進程、重掃描）；確認 reload 回應 `"reloaded": true` |

## 批次工作流

工具已存在於 `C:\心理學\3Dsymbol\tools\`（新機器需一併搬）：

| 腳本 | 用途 |
| --- | --- |
| `generate-professions.mjs` | 批次：讀 `professions-src/manifest.json` → 逐張 `workflowRun.createFromImage`（modelId `hunyuan3d-mini-turbo/generate`）→ 輪詢 status → GLB 落 `professions-glb/`。**可斷點續跑**（跳過已存在 GLB），失敗自動記 `generation-report.json` |
| `download-professions.mjs` / `fix3-professions.mjs` | Openverse CC0 搜尋下載（缺漏清單 `missing.json`） |
| `cleanup-round3.mjs` 等 | 誤抓圖清除（刪檔 + 同步 manifest） |

參數（速度優先）：`num_inference_steps: 5`、`octree_resolution: 256`、`seed: -1`。品質不夠改 10 步/380。

## 圖源 QA 規則（Openverse CC0）

- rate limit：匿名 20/min、200/day；搜尋間隔 ≥3.5s；圖檔下載走 CDN 不佔額度
- rawpixel `image_png_*` URL = 1300px 透明 PNG（最佳）；svgsilh 直連會 403 → 改用 Openverse thumb proxy `?height=1024`
- **逐張人工複核不可省**：搜尋評分擋不住「職業相關物品」（菜刀、麥克風、鯉魚）、動物、實拍照、多人場景
- 合格輸入：單人、全身、乾淨背景、插畫/卡通風最佳；半身/多人/照片可用但品質打折

## Red Flags

- 改了 generator.py 或 venv 套件卻直接重跑批次（沒 reload）→ 白跑
- 用「降低 octree / 換 seed / 換 sampler」處理 next_points IndexError → 沒治本，該換 vanilla decoder
- 看 `/model/all` 空就重裝 app → 先查 runtime.log 的 EXTENSIONS_DIR
- 批次全量重跑而不是增量 → 腳本已支援跳過已完成項
- VRAM 滿載還送生成 → 先釋放，不要硬跑等 OOM
