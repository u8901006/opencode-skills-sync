# 語音與音訊：坑、診斷、修復配方

## 1. 先問：prompt 裡真的有台詞嗎？（最常見根因）

症狀：整句亂碼（Whisper 聽出「此外相酒, 吟乳香拌菜」這種無意義句）、或整段沒有人聲（Whisper 只輸出「作詞・作曲・編曲 李宗盛」這類**全零長度 token 的音樂幻聽**）。

診斷順序：
1. 印出該段渲染用的 prompt，確認含有 `「台詞」`。台詞沒插進去時，模型在 QUIET 場景會自己瞎掰說話或不出聲——不是 take 運氣問題，重抽一百次都一樣。
2. 有台詞再談 take 品質（見下）。

SKILL.md 的「台詞自我檢查」snippet 就是為此存在，送單前必跑。

## 2. 亂碼開頭（garbled lead-in）

VO 段開頭常有 1–2 秒亂碼語音，之後台詞正確。**這是常态，不是失敗**：

- VO 段（畫面無人對嘴）：`concat.py` 用 `a=` 跳過。例：台詞在 source 2.3–6.2 s → `@a=2.25,d=0.3`。
- 對嘴段（`says()`）：`a=` 會破壞對嘴。處理順序：先換 take 重抽（同一 prompt 常有一次乾淨的）；仍不行用 `dub.py` 把開頭靜音、台詞原位保留：
  ```
  dub.py out.mp4 picture.mp4 take.mp4@2.3-6.55@0.5
  ```
  （圖片不變，音訊取 source 2.3 s 起放到 0.5 s 處，前面靜音。）08 段實例：站立鏡頭的「EM-D-M-DR」練習被靜音，正好做出分鏡要的「音樂降低」注意力轉折。

## 3. 跨 take 拼音（畫面與聲音來自不同 take）

VO 段沒有對嘴約束，`concat.py` 的 `src=` 直接借別的 take 的音訊：
```
seg03_t6_00001_.mp4@src=output/gpu0/.../seg03_t5_00001_.mp4,a=1.35,d=0.4
```
同一句話**任何一個 take** 的正確音訊都是備援——某段的台詞在多個 take 都有瑕疵時，可以從兩個 take 各剪正確的半句用 `dub.py` 接起來。15 段實例：
```
dub.py seg15_dub.mp4 seg15_t5.mp4 seg15_t5.mp4@0-1.5@0.3 seg15_t5.mp4@3.4-6.15@1.85
```
（開頭「如果不適合眼動」正確、中間亂碼、結尾「也可以評估其他雙側刺激方式」正確 → 剪掉中間直接接，聽感自然。）

## 4. Whisper 驗證的坑

- `transcripts.txt` 是所有影片共用的附加檔。查最新結果用 `grep -n "" transcripts.txt | tail -N`；grep 片段名會撈到舊片同名段落。
- 同音字≠發音錯誤：`喪慟`聽成`喪痛`、`仍可能`聽成`人可能`、`不適`聽成`不是`——語音其實正確，比照 rumination 片`反芻`案例，不要因此重抽。
- 真的唸不出/唸錯的詞：改台詞（EMDRIA→「EMDR 國際協會認證」、緊繃→「緊張」）。`反芻`這類詞在 `initial_prompt` 加詞即可正確轉寫，語音本身沒問題。
- **發音提示規則**：`EMDR is spoken as the four English letters E-M-D-R` 這類提示只在台詞真的含該詞時加；色鉛筆段**完全不加**（會被畫在紙上）。VO 段加提示常導致開頭出現「EMDR 練習」亂碼——反正會被 `a=` 跳過，可接受。
- 音樂幻聽：純音樂段 Whisper 可能輸出「作詞・作曲・編曲 李宗盛」（word token 全零長度）甚至德文——這代表**沒有語音**，不是字幕。
- **片尾低音量／靜音尾巴的長篇幻聽**：全片 ASR 可能在最後一句正確口白後，對低音量 room tone 或純靜音編出一串無關字詞，時間戳集中在切點、甚至多個零長度 token。先單獨聽 final comp 的尾段，並看該段與成片末秒的 waveform/RMS；若口白已完整、尾段無可辨識人聲（例如末秒約 -31 dBFS 後接數位靜音），不要把幻聽寫進 SRT，也不要只因轉寫重拍／重配音。只有實際聽到多餘人聲時，才依可聽邊界用 `dub.py` 修剪並重驗整句。
- 環境：`WHISPER_DEVICE=cpu`（GPU 渲染時絕不上 GPU）；CPU 用 int8，每次呼叫載模型約 1 分鐘，盡量整批餵檔案。

## 5. concat.py 音訊參數

- `a=` 音訊起點（預設=v，保持對嘴）；`d=` 槽內靜音延遲；`x=` 溢出到下一槽（交叉淡化，下一槽配 `d=` 吸收）。
- **對嘴段的 `a` 一定等於 `v`**（兩者一起位移才不破對嘴）；VO 段才能單獨動 `a=`。
- 排 `d=` 時先畫出 20 個槽的時間軸（每句起訖），確保 `x=` 的溢出被下一槽的 `d=` 吃掉、句尾不超過 6 s。
- 06/10 實例：畫面用 A take、音訊用 B take（`src=`），VO 段沒有對嘴負擔。

## 6. PyAV 後處理三坑（淡出/淡入）

1. **同一 container 先 decode 完視訊，再 decode 音訊會 EOF**——音訊默默變零筆，輸出沒有聲音。必須開**兩個 container handle**（一個讀視訊、一個讀音訊）。
2. `src.demux()` 的 packet 直接 `out.mux(pkt)` 會因 stream_index 對不上新容器被丟棄——要 `decode()` 後經過 `aus.encode(fr)` 重編碼，最後 `aus.encode(None)` flush。
3. 收尾必驗證：`av.open(輸出)` 後確認 `streams.video` 與 `streams.audio` 都存在、時長 = 預期。**音訊消失不會報錯**，只有驗證會抓到。

其他：cp950 console 不能 print 中文（UnicodeEncodeError）→ 寫檔再 `cat`；`aus.encode(None)` 只能在所有音訊幀送完後呼叫，提前呼叫會 EOF 該 stream。

## 7. 佇列管理

- 刪除 pending job：`POST /queue`，body `{"delete": ["<prompt_id>", ...]}`——用 `filename_prefix`（如 `emdrwho916/seg06_t3`）在 queue 的 graph inputs 裡比對。**running 中的刪不掉**，會跑完寫檔，改用下一個 take 號即可。
- 刪完佇列後，當初送單的背景腳本會永远等不到 history 裡的 prompt_id 而**掛死**——用 `wmic process where "name='python.exe'" get processid,commandline` 找出對應指令的 PID，`taskkill //F //PID ...` 清掉，否則它可能稍後又把壞 prompt 送回佇列。
- `story.submit()` 對同 prefix 去重：中斷後重跑同一指令安全；但**改過 prompt 的段落要換 take 號**，否則會沿用舊 job。
