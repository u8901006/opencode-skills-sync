# R2V 瑕疵圖鑑與對策

每一類都來自實際被淘汰的 take（主要取自 emdrwho_120s 與 stab/safe 片）。判斷順序：先分類 → 依「對策」欄決定換 take、改 prompt、換構圖或換表現方式。

## A. 人物與臉

| 瑕疵 | 誘發 | 對策 | 實例 |
|---|---|---|---|
| 灰棚/參考圖靜態複製（全身正面站姿開鏡） | 有 face/body 參考圖 + 「medium shot」類描述 | BASE 寫「never open on a full-body standing pose / never a still copy of a reference image」；開鏡直接寫「opens directly on a seated chest-up shot」 | emdrwho 02 t1 |
| 牆上巨大鬼臉、頭形陰影、暗色弧形 | 空白牆面、抽象光影、門縫透光 | 牆放滿書架/植物/花瓶；寫明「never a plain grey wall」「no ghostly double exposures, no faint floating faces」；門類轉場直接刪掉 | 01 t1（鬼臉）、01 t2（天花板弧形） |
| 雙重曝光/溶解鬼影 | 「快速推入穿過門」「insert shot」「溶解轉場」，或一段內兩個場景切換 | 全片單一連續鏡頭；場景切換明寫「plain hard cut (no dissolve, no overlay)」並接受偶爾仍失敗 → 換構圖 | 07 t1（天平畫在真臉上）、15 t1、16 t1/t2、10 t2 |
| 鏡中倒影是另一個人（變老/換臉） | 鏡子場景要模型畫兩張一致的臉 | 改構圖讓畫面只有一張臉：三側面+鏡中倒影為唯一正面；明寫「the mirror shows only her single reflection, her face exactly as in the reference」 | 12 t1；t2 成功 |
| 人物重複/多出的人 | 多人場景 | 「exactly N people, each appears only once, no duplicates」；一段只放一個已知角色+匿名配角 | stab 08 經驗 |
| 跟念旁白（畫面人物嘴動念出旁白） | VO 段沒設 QUIET，或同框兩人 | VO 段一律加 QUIET 常數；仍發生可接受（小面向）或換 take | 14 t6（輕微，已接受並記錄） |

## B. 文字與符號（全片嚴禁字元）

| 瑕疵 | 誘發 | 對策 | 實例 |
|---|---|---|---|
| 台詞被燒成字幕 | 台詞含內層「」、場景有紙張/證件/名牌 | BASE 全面禁字；台詞內不放內層引號；名牌一律 blank | rumination 12 t2 教訓 |
| **發音提示被畫出來** | prompt 內「EMDR is spoken as the four English letters E-M-D-R」出現在**色鉛筆段** | 發音提示只在台詞真的含該詞時加（`says()`/`hints()` 做法）；**色鉛筆段完全不加**（`vo(line, hint=False)`），字母會被畫在紙上 | 06 t1/t2（巨大 E-M-D-R 燒進畫面） |
| 招牌/書頁偽文字 | 街景店面、書本、獎狀 | 「plain blank fascia boards, no signs」；或構圖避開招牌 | 03 t3（第A>X\OIK 偽字） |
| 桌面長出印刷卡/標籤/墨點 | 「藥瓶/label/blank label」等詞 + 大面積桌面 | 別讓「label」這個字出現（寫 plain smooth sides, nothing printed）；把道具放到**已有人物環境**的桌上（醫師書桌全景），不要空桌面特寫 | 14 t2（藍標籤）、t4（印刷卡）、t5（墨點）；t6（書桌全景）成功 |
| 地面/牆面塗鴉（螺旋、@符號、 Scribbles） | 大片均質路面/牆面 + 「drifts/pan」運動 | 構圖塞滿（只留窄帶地面）；明列「no skid marks, no spirals, no circles」 | 03 t4/t5；17 t2（天花板藍色塗鴉） |

## C. 色鉛筆動畫專用

核心原則：**場景要「接地」**——畫在房間/窗邊/桌面等環境裡的物體（04 毛線房、05 田野、07b 窗前天平、09 橋、13 窗台盆栽）都乾淨；「紙上孤懸的物件」必然長出裝飾塗鴉。

| 誘發詞/題材 | 長相 | 對策 |
|---|---|---|
| sway、wind lines、ripples、shadow、whip pan、「waves rise」 | 黑金色捲曲螺旋鋪滿紙面 | 刪掉力的線條；改讓場景本體動（水波慢移、窗簾鼓起、葉子輕顫）；天平要「晃後歸平」就直接寫靜止，動態放棄 |
| 海邊/沙灘 | 成群黑色鳥群 + 沙上腳印塗鴉 | 放棄海邊（stab 16c 例外是純空景＋水平筆觸天空配方：「smooth sky with only soft horizontal pencil shading, no birds」）；人物+海更容易失敗，改真人版（窗簾=浪的隱喻，17 t6 成功） |
| 「drawn as if by an invisible pencil」「vignettes appear one by one」 | 出現動畫過程變成塗鴉 | 物件直接「已在紙上」，不描述繪製過程；三圓框並列像裝飾頁 → 改成真人手部三景硬切（06 t4 成功） |
| 兩個場景 in one clip | 場景間鬼影溶解 | 各場景各自成段，或真人硬切（ stab 13 模式）；即使寫 plain hard cut 也有約三成仍溶解，失败就換 take 或重構 |
| 白色光暈描邊 | 物體周圍一圈 sticker 白光 | 輕微可接受（記錄即可），嚴重換 take |

## D. 幾何物件與道具

| 瑕疵 | 對策 |
|---|---|
| 物件數量浮動（3 瓶變 5 瓶） | 明寫「exactly three…; no other bottles appear at any time」；開頭 1-2 秒仍可能不穩 → 若中後段穩定可用 `splice.py` 拼接 |
| 指定的道具被忽略（聽診器消失） | 逐項明列；仍缺就接受（VO 有唸到即可）或換 take |

## 判斷流程

1. 縮圖表逐格看（含結尾）→ 發現疑似瑕疵。
2. **抽原始幀放大確認**（小圖會把亮窗人像看成半透明鬼影，誤判成本是一輪渲染）。
3. 分類 → A/B/C/D → 查上表決策：
   - 隨機性瑕疵（臉融化、藍橘條紋、單次鬼影）→ 換 take（`XX:N`）。
   - prompt 誘發（動態詞、特定題材、插入鏡頭）→ 改 prompt 再抽；同一 prompt 連兩次同樣死法就一定要改詞或換構圖。
   - 題材本身詛咒（鏡子雙臉、海邊鳥群、空桌面文字）→ 換構圖或換表現方式（色鉛筆↔真人、道具入人物環境）。
4. 淘汰者記入 README 的 Rejected 清單（take 號 + 一句原因）。
