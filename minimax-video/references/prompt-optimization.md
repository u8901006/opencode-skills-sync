# 依官方 H3 指南修正影音 prompt

## 入口與適用範圍

先載入 `h3-prompt-writing`，從其回傳的 base directory 讀 `references/base-en.txt`（鏡頭、說話者、台詞、聲景共通規則），R2V／Ref2VA 另讀 `references/ref-en.txt`（參考標籤與六節格式）。這些路徑屬於 **h3-prompt-writing**，不是本文件所在的 minimax-video/references。

若 skill 無法載入，先確認已安裝並回報缺少官方指南；可依本地 artifacts/audio 指引處理，但不得宣稱已核對官方格式。

## 診斷 → 最小修改 → 單段驗證

1. **保留證據**：記錄 segment、take、實際送出的完整 prompt、參考圖順序、瑕疵時間點；看結尾原始幀，實際聽音訊並對照 Whisper 時間戳。先查 `artifacts.md`／`audio.md`。
2. **排除非 prompt 問題**：成片缺聲先查音訊 stream；源片完整而定剪漏字先修 concat；Whisper 幻聽先聆聽確認；socket reset、OOM、節點錯誤先依 AGENTS.md 排障，不改模型、不重啟他人工作。
3. **核對模式與參考角色**：本地 face/body 圖是同一角色的外貌來源，不是兩個人，也不表示首幀或尾幀。依 ref 指南可用 `<Subject 1>` 統一該角色並引用 `<Picture 1>`／`<Picture 2>`；索引必須與 refs 清單一致。只有真正的首尾幀任務才用 I2VA／FL2VA／L2VA 對齊指令。
4. **最小修改**：針對下表問題修訂，不同時改風格、角色、場景與台詞。正文以英文描述，保留原繁中台詞；若必須改難發音詞，明列改前／改後，保留原意。
5. **新 take 小測**：改 prompt 後使用未用過的新 take 號；同 prefix 會被 `story.submit()` 去重沿用舊 job。仍用既有 story.get()/submit()，不刪他人佇列、不重送整部片。
6. **驗證與留紀錄**：contact sheet 加結尾原始幀、實際聆聽、CPU Whisper 逐字核對。未通過不可宣稱修好。README 記錄舊／新 take、症狀、改詞、結果與 Rejected；通過後才套用同類段落。

## 症狀與官方規則對照

| 症狀 | 優先核對與修正 |
|---|---|
| 結尾灰棚／靜態參考圖 | 確認圖片僅參考外貌，不是畫面落點；描述角色在同一實景持續動作直到 6.58 s，最後仍維持實景與原構圖，不落在棚拍站姿；避免額外切鏡。 |
| 換臉／人物重複 | 統一 subject 定義與圖序，明列人數、每人位置、衣著；face/body 同屬一人，不把多張圖各自變成角色。 |
| 旁白人物跟念／雙人搶話 | 使用穩定 speaker ID，區分實際說話者與畫面人物；旁白用 `says in an off-screen voiceover`，每句後明寫對應畫面人物嘴唇全程閉合，保留 QUIET；本專案每段僅一位說話者。 |
| 台詞錯漏／亂碼 | 先確認最終 prompt 真的含完整台詞；說話者、語言、開始及結束時間放在台詞之外；不把發音提示當台詞。保留 standard Taiwanese Mandarin；必要時縮短或拆句，不靠加快語速硬塞。 |
| 句尾被截／時間矛盾 | 原片 158 幀約 6.58 s，定剪槽 6.0 s；動作時間可涵蓋源片，台詞依既有 helper 約 0.3 s 起、5.7–5.8 s 前結束。先分清源片沒念完或 concat 截掉，再選改台詞或修剪接。 |
| 字幕／發音字母燒入畫面 | 官方 visible-text 規則只適用真的需要畫中文字的任務；本專案仍禁任何畫面文字。台詞不可另寫成招牌、字幕或紙上內容；色鉛筆段不加字母發音提示。 |
| 鬼影／鏡頭混亂 | 按 composition → action → camera → sound 寫可見／可聽內容，簡化單一連續鏡頭；需要切鏡才寫嚴格遞增且在片長內的 cut time，避免同時要求連續鏡頭與多次切換。 |
| 音樂壓過口白／多餘人聲 | 區分台詞、環境聲與觀眾才聽到的配樂；overall_soundscape 不重複台詞，non_diegetic_music 不加入歌聲。無配樂用 N/A；有口白時不能把整段聲景寫成完全靜音。 |

## 兼容現有 helper，不盲目遷移格式

預設沿用 story 腳本的 BASE／QUIET／vo()／says()／voice() 及 `「台詞」`，只借用官方的角色、時間線、鏡頭、說話者與聲景規則。這是**依官方原則調整的本地 prompt**，不是完整官方格式。

若刻意採用完整 Ref2VA 格式，嚴格依序寫 `subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music`，並依兩份指南使用 `<d>[Language] 台詞</d>`；不要把 T2VA 的 integrated_multimodal_description 混入六節結構。同步調整送單前檢查：以每段預期完整台詞為準核對實際 prompt，明確區分有聲／無聲段，支援採用的台詞包裝；只檢查 `「` 是否存在不夠。先單段驗證再遷移，不能為通過舊檢查而把同一句台詞重複放兩次。

### 最小修詞示例（沿用現有 VO helper）

原描述：`The woman from <Picture 1> and <Picture 2> sits in a room. Voiceover.`

改為：`Exactly one woman, whose face and clothing follow <Picture 1> and <Picture 2>, is already seated beside a bookcase. Both pictures define the same woman's appearance only, not opening or ending frames. The camera holds a seated chest-up static shot in this room throughout 0.00–6.58 s. She gently lowers her hands and stays in the room through the final frame. The narrator says in an off-screen voiceover; the woman's lips remain completely closed throughout.`

再接原本 VO helper 產生的完整 `「台詞」`、台灣國語與起訖時間，保留 BASE 禁字／禁灰棚規則；不額外加入第二份台詞。不承諾改詞一定消除瑕疵，仍須新 take 驗證。
