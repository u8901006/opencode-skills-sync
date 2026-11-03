# research-to-blogger

OpenCode skill：主題英文研究 → 合法全文 → 繁體中文摘要 → 卡片式 Blogger 文章。

## 呼叫

```text
@research-to-blogger
請整理「主題」2021–2026 年英文研究，全文與繁體中文摘要存到 .\指定資料夾，
依深藍標頭、彩色編號卡片版型製作 Blogger 網頁。
```

可替換主題、年份、儲存目錄與版型參考。沿用已確認設計，不需每次再交代整套流程。研究判讀由載入 skill 的代理執行；腳本只負責驗證與離線生成，**不是自動搜尋或自動下載論文的獨立程式**。

## 內容

- `SKILL.md`：觸發條件、流程、品質與安全界線。
- `references/workflow.md`：檢索、全文、證據解讀與交付細節。
- `references/data-contract.md`：可重用資料格式。
- `templates/styles.css`：深藍標頭、四色分類、響應式卡片樣式。
- `scripts/publish.py`：標準 Python、離線產出 Blogger 與摘要／書目。
- `scripts/browser_check.py`：使用既有 Playwright／Chrome 或 Edge 測試。
- `tests/`：迴歸測試、整合測試結果與測試紀錄。

不覆寫現有 skill、不改原 ArtTrauma 研究資料；未授權不發布網頁、不付費下載、不繞過存取限制、不自行安裝瀏覽器依賴。
