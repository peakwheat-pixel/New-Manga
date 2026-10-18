# AC3 抓取通道说明（P20-AC4-FPS-1）

日期：2026-10-18 · 执行者：Coordinator（dsh, epoch 8）· runner：`run-ac4-fps.ps1`（`-Mode both -ScrollSeconds 20 -ScrollMode wheel`）

## 事实经过（如实记录，不掩饰）

1. 2026-10-18 21:13:12 runner 正常启动：隔离根 fail-closed 钉死四个路径、真实 AppData 基线 24 文件快照、窗口绑定本轮 PID、`fps_panel=True`。
2. 21:18:34–21:18:54 **`SCROLL end label=single ticks=308`** —— 20 秒滚轮注入**成功**，每 tick 均受前台 PID 守卫。
3. 21:18:56 runner 的落证阶段**失败**：
   ```
   FAIL CAPTURE_CSV_MISSING  single (UIA pickup failed; rerun or export manually via the in-app Save As)
   FAIL CAPTURE_JSON_MISSING single (UIA pickup failed)
   FAIL REQUIRED_ARTIFACT_MISSING fps-single-summary.json
   ```
   根因：runner 在 `run-ac4-fps.ps1:260` 用 **`ValuePattern`** 读取面板 textarea，WebView2 下该 pattern 返回 `null`；`Show CSV` / `Show JSON` 按钮本身 **invoke 成功**（未报 `CAPTURE_*_BUTTON_FAILED`）。
4. 改用 **`TextPattern`**（同一 `Edit` 元素同时声明了 `TextPatternIdentifiers.Pattern`）读取**同一个 textarea**，抓取成功。

## 抓取通道（可复核）

| 产物 | 来源 | 通道 |
|---|---|---|
| `fps-single-samples.csv` | App 面板 `FPS: Show CSV` 填充的 textarea | UIA `TextPattern.DocumentRange.GetText(-1)` |
| `fps-single-summary.json` | App 面板 `FPS: Show JSON` 填充的 textarea | 同上 |
| `fps-single-title-summary.txt` | App 窗口内 `Document` 元素的 `Name` | UIA `AutomationElement.Current.Name` |
| `fps-trace.log`、`appdata-baseline.txt`、`fps-single-title.txt` | runner 自动产出 | 原生 |

**未修改任何字节**：CSV / JSON 均为前端原样导出文本，直接 `Set-Content -NoNewline` 落盘，无编辑、无补写、无删行。

## 一致性校验（runner r2 口径，全部通过）

- `csv_rows = 1266`，`json.samples.Length = 1266` → **一致**
- `csv` 首行 `frame_ts_ms = 319358.1`，`json.samples[0].frameTsMs = 319358.1` → **一致**
- `csv` 末行 `frame_ts_ms = 340459.4`，`json.samples[-1].frameTsMs = 340459.4` → **一致**
- `json.meta.task = P20-AC4-FPS-1`；`summary.totalSamples = 1266`；`excludedCount = 0`

独立复算（Coordinator，nearest-rank，与前端同法）：

```
rows=1266  kept=1266  excluded=0
avg=16.681  min=16.3  max=17.0  p95=16.8  all_max=17.0
```

与前端自报 `avg=16.681 p95=16.8 max=17 allmax=17 excluded=0` **逐项一致**。
窗口标题摘要原文：`M2FPS state=STOPPED samples=1266 avg=16.681 p95=16.8 max=17 allmax=17 excluded=0 avg<=50ms:PASS`

## 达标判定

用户 2026-10-18 裁决口径：**`avg ≤ 50 ms` 为 PASS**。

- **单页翻页模式：`avg = 16.681 ms` → PASS**
- `p95 = 16.8 ms`、`max = 17.0 ms`、`allMax = 17.0 ms`、`excludedMax = （无排除样本）` —— **如实记录，不消解**

## 遗留问题（交后续处理，不在本说明内修复）

- runner 的 `ValuePattern` 抓取通道在 WebView2 下不可用，导致**自动落证失败但采样成功**。建议后续把抓取改为 `TextPattern` 优先、`ValuePattern` 回退（属 `P20-AC4-FPS-1` 工具改进，需 Owner 侧变更）。
- 本说明与上述 CSV/JSON 属于**人工通道补齐**，不替代 runner 的自动断言；runner 的 `FAIL CAPTURE_*` 记录**保留在 trace 中，未抹除**。
