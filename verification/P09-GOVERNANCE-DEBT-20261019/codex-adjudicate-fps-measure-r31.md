# P20-AC4-FPS-MEASURE-1 释放裁定（r31）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：拟议的 P20 AC4 FPS 测量入口 Task  
写入范围：仅本文件。未修改 Task、STATUS、Plan、代码或既有证据；未调用 `coordinator-lease.py`，未执行 Git 写命令。

## 裁定摘要

**不按草案释放 `P20-AC4-FPS-MEASURE-1`。** 草案所称“记录器没有产品入口、没有页面挂载，因此只缺入口”的事实与当前代码和既存实测证据不符：

- `apps/desktop/frontend/src/main.tsx` 已调用 `readFpsRecorderRequest()`；显式开关打开时调用 `startFpsRecorder()` 并挂载 `FpsRecorderPanel`。默认关闭时不启动 rAF、不创建样本数组、不挂载面板。
- 启用通道已有三种：测量构建 flag `VITE_M2_FPS_SAMPLING=1`、`?m2_fps=1`、localStorage `m2rc1_fps_sampling=1`。真实桌面测量指南已指定 build flag 与 runner 流程。
- 已存在单页与 Webtoon 长图真实桌面帧率结果：单页 avg **16.681 ms**、p95 **16.8 ms**、max **17.0 ms**；Webtoon avg **17.527 ms**、p95 **33.3 ms**、max **33.5 ms**。两项均满足用户裁定的 avg ≤ 50 ms；p95/max 已照实报告。原始报告也记录 runner 抓取通道故障、前台焦点失败尝试和修复/复跑证据，没有删掉失败记录。

所以 AC4 帧率子项已有测量结果，不需要新增 Settings 开关、隐藏手势或再次建立 FPS 入口 Task。AC4 仍剩缩放平移的人工撕裂观察；不能把 FPS 帧时间数据代替画面观察。

## 一、事实核对与来源差异

### 1.1 当前实现与 Task 草案不一致

当前 `main.tsx` 明确导入 `FpsRecorderPanel`、`readFpsRecorderRequest` 和 `startFpsRecorder`。采样请求只在启动时读取一次；请求为真时启动记录器并渲染面板，为假则传入 null、不渲染面板。故：

- “Settings 页没有 FPS 控件”是对的；
- “全仓只有测试导入面板”“没有产品页面挂载”“只能新增设置入口才可测”与当前代码不符；
- 开关可由 measurement build 或启动 URL 等现有启动条件触发；是否在当前打包 build 的特定启动环境可达，应以已留存的 runner 记录为准，不能据旧只读调查推断不可用。

草案建议把 AC3 定义为已有导出通道的产品可达性，但现有面板已包含 Save-As、Show/Copy 通道；当前真实桌面报告已通过该通道取得 CSV/JSON。未发现需要为此再改面板或记录器的理由。

### 1.2 FPS 已测，且数值支持现行用户判据

依据 `verification/P20-AC4-FPS-1/ac3-real-desktop/AC3-REPORT.md`：

| 模式 | 样本（kept / excluded） | avg | p95 | max | allMax | 判定 |
|---|---:|---:|---:|---:|---:|---|
| 单页翻页 | 1266 / 0 | 16.681 ms | 16.8 ms | 17.0 ms | 17.0 ms | PASS |
| Webtoon 长条 | 1202 / 0 | 17.527 ms | 33.3 ms | 33.5 ms | 33.5 ms | PASS |

CSV/JSON 行数、首末样本时间戳、前端汇总与独立复算在报告中有逐项核对；报告还记录两轮真实 AppData 快照未变化及进程清理结果。Webtoon 的 p95/max 明显高于单页，必须保留该差异，不得把 avg 达标写成“帧时间稳定”或抹去尖峰。

### 1.3 当前文档存在需要 Codex 后续同步的差异

本次核对到的资料并不一致：

- `verification/P20/ac4-measurability-analysis.md` 与 r30 对 FPS 入口/实测的表述，早于当前接线/AC3 实测证据，仍说“未挂载、未测”。
- `doc/STATUS.md` 仍把 FPS-1 描述为 AC3 `NOT_RUN`。
- `doc/REBASELINE_PLAN.md` 将 FPS-1 列为 `closed_with_limitations（AC3 PASS；AC5 依裁决）`。
- `doc/tasks/P20-AC4-FPS-1.md` 的 Canonical Evidence / AC3 报告记录了上述实测结果。

按 r27 §5，事实核验应先于状态语义改变。本文件不替代权威状态同步；上述差异应由 Codex 在适用的 Task 生命周期中核实并协调，不能据本裁定改写旧报告或当前状态。

只读观察时 checkout 的 HEAD 为 `b9811d07b332a8af35c072b36b78189c827005ce`，分支为 `antigravity/P09-AC3-DELETE-HARDEN-1`；工作区另有既存 dirty/untracked 内容。本次均未改动。该 checkout 不被本裁定冒充为新 Task 的冻结 base 或主线集成点。

## 二、五项问题裁定

### 2.1 是否立 Task；localStorage 预置是否绕过 UI

**不立“新增产品入口”Task。** 记录器、面板、主入口接线、三种显式启用通道、Save-As 导出通道和真实桌面测量结果都已存在。把相同范围另立 Task 会重复实现并制造不必要的产品 UI。

直接修改 WebView2 profile 内部存储文件来预置 localStorage，理论上要先识别当前 WebView2 origin 与其 Chromium profile 存储格式；该办法未在本轮验证，也不是必要路径。它还会依赖具体 profile/应用状态。已有测量指南以构建 flag 生成显式 measurement build，并通过受隔离的 runner 采集；现有报告证明此通道已经工作。因此不建议尝试手工改 profile，也不需要为 localStorage 写操作步骤文档。

### 2.2 Owner 与 Reviewer

本裁定不释放实现 Task，故不指派 React UI Owner。若后续只需复核或补录 FPS-1 的状态差异，应由 Codex 按正式生命周期处理。

对于剩余撕裂观察，可在单独冻结的 P20 AC4 收口/观察范围中由 Coordinator 组织真实桌面操作并留存观察条件及结论；Reviewer 需为非执行者（例如可用的 Antigravity）。若范围后来确实变成 React UI/UX 改动，ZCode 仍是主责；ZCode 无 headless CLI 时只能由 Codex 在 Task 中明确释放给 Antigravity 承担必要的最小 UI 接线，这属于显式例外授权，不能由本裁定自动授予。

### 2.3 AC 数量与真实桌面操作

草案 6 条 AC 面向“增加入口、显示面板、导出、实测、零回归、Review”；入口/面板/导出/实测已有实现或证据，不应再转写成一个重复实现 Task 的 AC。

如以后需为剩余缺口单独冻结观察 Task，AC 可压缩为 3–4 条：①按冻结条件执行并记录缩放/平移的人工观察；②报告观察环境、操作、观察者、结果及可用影像证据和限制；③保留 `NOT_MEASURED`、失败或超出覆盖范围的结论，不从 FPS 统计推断撕裂；④固定证据 head 后独立 Review。FPS 实测不是前置重跑项。

FPS 滚动与缩放平移可在同一桌面会话分阶段操作，但必须分别形成结果：滚动 FPS 以既有 CSV/summary 为准；撕裂需独立的人工观察记录。不能因为同次操作或同一报告，就把帧间隔统计当成撕裂证据。

### 2.4 撕裂与同 Task 处理

FPS 记录本身不检测撕裂，原 FPS 报告也明确把撕裂保留为限制；不能追溯补记为 PASS。按 r30 已认可的路径，可由有记录、范围明确的人工观察验收，记录观察者、时间、硬件/刷新率/窗口条件、缩放和平移操作及结论；可取得时附影像。观察 PASS 仅适用于记录的环境与操作覆盖。

若下一步只为完成 P20 AC4 的剩余观察，可把撕裂检查作为该次 AC4 收口/观察 Task 的独立 AC，与复核既有 FPS 证据放在同一交付包，不需要再新立 FPS 实现 Task。没有可执行的观察者/环境时保留 `NOT_MEASURED`，由用户决定是否接受限制关闭。

### 2.5 P20 终态与 Closeout

FPS avg 达标且未来撕裂观察通过，**仍不足以单独让 P20 转 `done`**。r30 已指出 P20 自身另有缺口：AC1 干净环境安装/卸载、AC3 单图批处理峰值、AC5 本地模型 CPU 推理，以及全 Task 的证据和资源 closeout。最终状态应按这些 AC 的实际证据决定：

- 全部已释放 AC 满足且 evidence/resource closeout 完成，才可按协议转 `done`；
- 用户明确接受剩余限制并批准停止验收时，才可按协议转 `closed_with_limitations`，逐项保留原始未完成状态，不得写成 PASS。

P20 当前 `ready`，且确有自己的 Closeout Record 字段（关闭日期、`canonical_evidence_status`、`resource_closeout_status`、资源操作计数、未关闭项及保留原因等）。在正式进入终态时必须按协议补齐；本裁定不修改这些字段或 Plan/STATUS。

## 三、决定与推荐下一步

决定：**拒绝按现有草案释放 `P20-AC4-FPS-MEASURE-1`；不新增产品入口；接受 FPS 实测报告所载的 avg 判定与 p95/max 限制性描述，撕裂继续待人工观察。** 不填该草案的 base/branch/worktree/owner/reviewer 字段，不将未释放 Task 写入 DAG。

推荐下一步：Codex 以当前 P20 权威 Task 生命周期核对并同步 FPS-1 实测状态差异；随后为撕裂人工观察及 P20 剩余发布缺口冻结一个有明确范围和 Owner/Reviewer 的下一步。P20 保持 `ready`，直到其余验收与 closeout 条件有正式结论。

