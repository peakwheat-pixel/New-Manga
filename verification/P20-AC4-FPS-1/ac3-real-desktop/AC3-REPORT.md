# P20-AC4-FPS-1 · AC3 真实桌面帧率测量报告

日期：2026-10-18 · 执行者：Coordinator（dsh，epoch 8）· 判定口径：用户 2026-10-18 裁决 **`avg ≤ 50 ms` 为 PASS**

---

## 1. 结论

**AC3 PASS** —— 两个模式均满足阈值。

| 轮次 | 阅读模式 | 样本（kept/excluded） | **avg** | min | p95 | max | allMax | 判定 |
|---|---|---|---|---|---|---|---|---|
| 单页 | 翻页 (paged) | 1266 / 0 | **16.681 ms** | 16.3 | 16.8 | 17.0 | 17.0 | **PASS** ✅ |
| Webtoon | 长条 (long-strip) | 1202 / 0 | **17.527 ms** | 16.5 | 33.3 | 33.5 | 33.5 | **PASS** ✅ |

**附带结论（如实记录，不消解）**：Webtoon 长条滚动的 `p95=33.3 ms` / `max=33.5 ms` 约为单页（16.8 / 17.0）的 **2 倍** —— 长图滚动存在更高的帧时间尖峰。`avg` 仍远低于阈值，故达标；冷路径优化按裁决另立 Task，不在本 Task 内处理。

**60 Hz VSync 说明**：`avg≈16.7 ms` 对应约 60 fps，是显示器刷新率的固有下限；两轮独立观测一致（16.681 / 17.527），与 60 Hz 面板相符。

## 2. 采集参数（冻结）

```
runner : verification/P20-AC4-FPS-1/run-ac4-fps.ps1
单页轮 : -Mode both ...（run1 执行 single 阶段）
Webtoon : -Mode webtoon -ScrollSeconds 20 -ScrollMode wheel
滚动   : 真实桌面滚轮注入，20 秒；每个 tick 均受前台 PID 守卫
排除规则: raf_gap_ge_1000ms_while_hidden（页面隐藏区间相交）、non_positive_delta
p95方法 : nearest-rank（与前端同法）
```

**样例**：`P20-AC4-FPS-1-samples\single\page-01.png`（420×620）、`...\webtoon\long-strip-01.png`（**600×18401**，6.1 MB 真实韩漫长条图）

## 3. 数据归属校验（runner r2 口径，两轮全通过）

| 校验项 | 单页 | Webtoon |
|---|---|---|
| `meta.task == P20-AC4-FPS-1` | ✅ | ✅ |
| CSV 行数 == JSON `samples[]` 长度 | 1266 == 1266 | 1202 == 1202 |
| 首样本 `frameTsMs` 一致 | 319358.1 | 143577.1 |
| 末样本 `frameTsMs` 一致 | 340459.4 | 164628.3 |
| Coordinator 独立复算 vs 前端自报 | 逐项一致 | 逐项一致 |

**独立复算（Coordinator，nearest-rank）**

```
单页   : rows=1266 kept=1266 excluded=0  avg=16.681 min=16.3 p95=16.8 max=17.0 all_max=17.0
Webtoon: rows=1202 kept=1202 excluded=0  avg=17.527 min=16.5 p95=33.3 max=33.5 all_max=33.5
```

**窗口标题摘要原文**

```
单页   : M2FPS state=STOPPED samples=1266 avg=16.681 p95=16.8 max=17 allmax=17 excluded=0 avg<=50ms:PASS
Webtoon: （抓取时 state=RUNNING samples=0，本轮摘要行未及时刷新；统计取自前端导出的 summary.json）
```

## 4. 隔离与用户数据安全（两次独立证实）

```
run1: APPDATA[final] UNCHANGED (files=24, per-path sha256 compared)
run4: APPDATA[final] UNCHANGED (files=24, per-path sha256 compared)
```

独立复核 `appdata-baseline.txt` vs `appdata-after.txt`（各 24 行）→ **逐行完全一致**。

- 四个数据根全部 fail-closed 钉死到 `%TEMP%\p20fps-*` 隔离根，任一缺失即拒绝启动
- 收纳为 Managed Copy：`managed\books\<book>\chapters\<ch>\original\<page>.png`
- 收尾 `TEARDOWN all our processes exited`，仅清理本轮 PID 家族；对 `msedgewebview2` 等白名单外同名进程记录 `SKIP ... NOT touched`

## 5. 缺陷与偏差（如实登记，未抹除）

### 5.1 runner 抓取通道在 WebView2 下不可用（**每轮必然产生 FAIL**）

`run-ac4-fps.ps1:260` 用 UIA `ValuePattern` 读取面板 textarea，WebView2 返回 `null`：

```
FAIL CAPTURE_CSV_MISSING  (UIA pickup failed; rerun or export manually via the in-app Save As)
FAIL CAPTURE_JSON_MISSING (UIA pickup failed)
FAIL SUMMARY missing csv / FAIL REQUIRED_ARTIFACT_MISSING fps-*-summary.json
```

`Show CSV` / `Show JSON` 按钮本身 **invoke 成功**（未报 `CAPTURE_*_BUTTON_FAILED`）——**纯粹是读取 pattern 不兼容**。

**处置**：改用同一 `Edit` 元素同样支持的 **`TextPattern`** 读取**同一 textarea**，取前端**原样导出**文本落盘，未做任何编辑。**runner 的 4 个 FAIL 记录保留在各自 trace 中，未删除、未改写。**

### 5.2 runner 收到 6 秒内即 TEARDOWN，人工抢抓窗口过窄

run3 中采样**完全成功**（`ticks=316`），但从 `FAIL CAPTURE_*` 到 `TEARDOWN` 仅 **6 秒**，导致该轮数据随 App 关闭丢失。

**处置**：新增 `ac3-grabber.ps1` —— 0.4 s 轮询 trace，一见 `SCROLL end label=<mode>` 立即用 `TextPattern` 抓走 CSV/JSON（run4 成功：`CSV 32791 chars`、`JSON 201901 chars`，`app_alive=True`）。

### 5.3 前台被 `GameInputSvc` 霸占导致整轮作废（run2）

run2 记录：

```
FOCUS_ACTIVATE scroll[single]tick=0 attempt=SetForegroundWindow
FAIL FOCUS_ACTIVATE_FAILED (foreground pid=22364 is still not this run's app pid=33172; NO input injected)
SCROLL end label=single ticks=0
```

`pid 22364 = GameInputSvc`（Windows 系统服务，非用户窗口）。**焦点守卫的行为完全正确**：它**拒绝**把滚轮注入到非本轮 App 的窗口，宁可整轮失败也没有误伤其它程序。

**处置**：由人工点击 App 窗口夺回前台（自动化 `SetForegroundWindow` / `bring_to_front` 均被 Windows 前台锁拒绝）。run1 与 run4 均为人工点击后通过。

## 6. 复现步骤

```powershell
# 前置：带钩子的前端 + 重编译 exe（Tauri 编译期嵌入 dist）
cd apps\desktop\frontend; $env:VITE_M2_FPS_SAMPLING='1'; npm run build
cd ..\src-tauri; cargo build --bin m2rc1-desktop

# 抢抓器（先起，避免 6 秒窗口丢数据）
pwsh -NoProfile -File <evidence>\ac3-grabber.ps1 -OutDir "$env:TEMP\p20-ac4-fps-ac3-runN" -Label webtoon

# 测量
pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 `
  -Mode webtoon -ScrollSeconds 20 -ScrollMode wheel `
  -OutDir "$env:TEMP\p20-ac4-fps-ac3-runN"
# 人工：导入样例 -> 打开阅读器到目标模式 -> 点击 App 窗口夺回前台 -> 回车放行
# 收尾：恢复默认 dist
cd apps\desktop\frontend; npm run build   # 不带 VITE_M2_FPS_SAMPLING
```

## 7. 证据清单

| 文件 | 说明 |
|---|---|
| `fps-single-samples.csv` / `fps-webtoon-samples.csv` | 前端原样导出（34664 / 32791 B） |
| `fps-single-summary.json` / `fps-webtoon-summary.json` | 前端原样导出（212730 / 201901 B） |
| `*-title-summary.txt` | 面板 `Document.Name` 摘要原文 |
| `run1-single-trace.log` / `run4-webtoon-trace.log` | runner 完整 trace（含全部 FAIL 记录） |
| `run{1,4}-appdata-{baseline,after}.txt` | 真实 AppData 前后逐文件 sha256 清单 |
| `capture-channel-note.md` | 抓取通道说明（含 run1 详细经过） |
| `ac3-grabber.ps1` | 抢抓器源码 |

**Task 状态影响**：AC3 完成后 `P20-AC4-FPS-1` 具备转入 `done` 的条件；**AC5（撕裂）按用户裁决继续记 `NOT_VERIFIED_BY_RULING`**，仅为 limitation，不得写 PASS。
