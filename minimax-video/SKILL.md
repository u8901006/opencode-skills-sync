---
name: minimax-video
description: MiniMax H3 + ComfyUI R2V 心理衛教短片製作工作流（D:\minimaxH3 工作區）。只要使用者要做新影片、寫分鏡 story 腳本、渲染或重拍 take、檢查畫面/語音、合成定剪，或回報 R2V 瑕疵（鬼臉、燒入字幕、亂碼語音、色鉛筆塗鴉、語音缺字），就使用本 skill——即使只說「做一部新片」「某段怪怪的」也一樣觸發。
---

# MiniMax H3 短片製作

工作區 `D:\minimaxH3`。硬體/啟動/模型細節見該 repo 的 `AGENTS.md` 與 `README.md`——本 skill 不重複它們，只補**流程紀律**與**實際翻車過的坑**。動手前先讀 README 找最接近的舊片當模板。

## 鐵律

- Python 一律 `venv\Scripts\python -I ...`。`-I` 會丟掉 `PYTHON*` 環境變數：非 ASCII 輸出要寫檔再 `cat`，不要 print。
- 不安裝套件/模型、不更新 custom nodes、不動別人已排入佇列的工作。
- 開工前 `curl http://127.0.0.1:8188/system_stats`（和 `:8189`）：已在跑就直接用，不要重開。
- 渲染固定 158 幀（6.58 s），裁 6.0 s 交給 `concat.py`，不要改幀數。
- 沒有 ffmpeg；影片後處理用 PyAV（`venv\Scripts\python -I`）。
- GPU 正在渲染時，Whisper 必須 `WHISPER_DEVICE=cpu`。

## 標準流程

1. **模板**：複製最接近的 `tools\story_<name>.py`。它們用 importlib 載入 `story.py` 並覆寫 `OUT_DIR` / `SEED` / `SEGMENTS`（SEED 每片換一個，格式 2026MMDD）。新角色先渲染無參考的 `c0` 段再抽幀做 `ref_<x>_face/body.png`。
2. **寫分鏡**後、送單前，跑「台詞自我檢查」（見下一節）——這步省略過一次，代價是 9 個 take 白渲染。
3. **送單**：preflight 檢查節點要用 `story.get()`（裸 `urllib` 會被 Windows socket reset 殺死整支腳本）。雙 GPU 分工：奇數段→8188、偶數段→8189，各自背景執行＋log：
   ```
   venv/Scripts/python -I tools/story_<name>.py 8188 01 03 05:2 ... > <name>_gpu0_a.log 2>&1
   ```
   `05:2` = take 2（seed+take−1，輸出 `seg05_t2_00001_.mp4`）。同 prefix 已在佇列/history 時 `story.submit()` 會沿用不重送，中斷後可安全重跑同一指令。
4. **逐段檢查（不可省略，邊渲染邊做）**：
   - 畫面：`venv/Scripts/python -I tools/contact.py <seg.mp4> checks/<name>/segXX.png 9`，親自看圖，**特別看結尾幀**（參考圖複製最常出現在結尾）。
   - 語音：`WHISPER_DEVICE=cpu venv/Scripts/python -I tools/transcribe.py <seg.mp4> ...`，用時間戳決定 concat 的 `a=`。台詞要逐字核對（多字/漏字/重複字都算失敗）。
5. **淘汰與重拍**：換 take 號重送即可（新 seed）。畫面可用但音訊壞 → 不要整段重抽，用 `dub.py`/`splice.py` 修（見 references/audio.md）。
6. **定剪**：`tools/concat.py`（參數見下）→ PyAV 淡出 → **驗證輸出** → `README.md` 補該片段落（參考圖、Final cut 參數、Rejected 清單、新坑）。

## 送單前台詞自我檢查（血淚根因）

曾發生 9 個段落的 prompt 有場景描述、有 QUIET，**但引號台詞本身忘了插進去**——模型在靜音場景裡自行瞎掰語音（整句亂碼）或根本不出聲（Whisper 只幻聽到背景音樂）。渲染回來才發現，浪費整整一輪。送單前必跑：

```bash
venv/Scripts/python -I - <<'EOF'
import importlib.util, os
os.environ['STORY_ASPECT'] = '9x16'
spec = importlib.util.spec_from_file_location('s', 'tools/story_<name>.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for seg, (refs, text) in m.SEGMENTS.items():
    if 'c0' not in seg and '「' not in text:   # c0 = 無聲人像段
        print('MISSING LINE:', seg)
EOF
```

規則：每個有旁白/對白的段落，prompt 內必須真的含有 `「台詞」` 字串（`vo()`/`says()`/`mixed()` helper 會帶，但改版段落時容易在重寫中弄丟——改完必跑此檢查）。

## 檢查與驗證的紀律

- `transcripts.txt` 是所有影片共用的**附加**檔：看結果要用 `grep -n "" transcripts.txt | tail -N` 抓最後幾行；用片段名 grep 會撈到舊片的同名段落。
- 縮圖表小圖會騙人：亮窗前的人像在小圖上像半透明鬼影。**判死前先抽原始幀放大確認**，誤判一次就是多等一輪渲染。
- concat 前先 `ls` 確認每個 take 的實際路徑：奇偶段、不同輪重拍可能落在 `output\gpu0` 或 `output\gpu1`，寫錯目錄 concat 會直接 FileNotFoundError。
- 定剪完成必驗四項：時長 = 段數 × 6 s、480×864、**有音訊 stream**（音訊常在後處理時默默消失，見 references/audio.md）、全片轉寫逐句核對。

## 定剪與淡出

`concat.py <out.mp4> <seg.mp4>[@v=,a=,d=,x=,src=...]`：`v` 畫面起點、`a` 音訊起點（預設=v 保持對嘴）、`d` 槽內延後、`x` 溢出到下一槽（下一槽要配 `d=`）、`src=` 從別的檔借音訊。對嘴段的 `a` 一定等於 `v`；VO 段才能用 `a=` 跳過亂碼開頭。

淡出用 PyAV，**必須開兩個 container handle**（同一 handle 先 decode 完視訊再讀音訊會 EOF，音訊會默默消失）：

```python
srcv = av.open("raw.mp4"); srca = av.open("raw.mp4")   # 兩個 handle
# 視訊：逐幀處理（淡出＝尾段乘 ramp 或 blend 向目標色）→ vs.encode
# 音訊：for fr in srca.decode(audio=0): aus.encode(fr) → 最後 aus.encode(None)
# 收尾驗證：av.open(輸出) 檢查 streams.video 與 streams.audio 都存在、時長正確
```

## 瑕疵對策（速查）

R2V 的失敗模式是**可分類且會重複出現**的，逐段檢查時對照 `references/artifacts.md` 的圖鑑決定「換 take」「改 prompt 再抽」「換構圖」還是「換表現方式（色鉛筆↔真人）」。語音問題對照 `references/audio.md`。

快速心法：
- 同一 prompt 連兩 take 同樣死法 → 是 prompt 誘發，改詞再抽；只壞一次 → 換 take 重抽。
- 「插入鏡頭／穿過門／溶解轉場」類運動極易鬼影 → 改成「開鏡已在定位」的單一連續鏡頭＋明寫 plain hard cut。
- 畫面上任何空曠均質區域（大牆、路面、天空、桌面）都會被拿來畫東西 → 構圖塞滿或避開。
- 色鉛筆段的動態詞（sway、wind lines、ripples、shadow、whip pan）＝捲曲塗鴉；要動態就讓「場景本體」動（水波、窗簾、樹葉），不要叫模型畫「力的線條」。

詳細圖鑑（誘發詞、長相、對策、實例 take）見 `references/artifacts.md`；語音/音訊坑與 dub/splice 配方見 `references/audio.md`。
