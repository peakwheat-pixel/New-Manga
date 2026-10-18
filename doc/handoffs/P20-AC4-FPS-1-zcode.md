---
task_id: P20-AC4-FPS-1
author: ZCode
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 16b995247
status: delivered_for_review
review_round: r3-rework
---

# Handoff：P20-AC4-FPS-1（AC4 帧率与帧时间测量钩子）r3 返修

## 交付结果

本轮为 codex-review-r3（`changes_requested`）的返修交付，经用户 2026-10-18 **DIR-4 豁免授权**（本 Task 最后一次返修机会）。实现 commit `16b99524794a7ff2132a19753ce6a7fcd53fc244`（main，51 个文件：runner + guide + r3 review 入库 + 六组证据目录）；本文档随其后的文档 commit 一并入库。r2 返修 `de5c06a4d`、r1 返修 `4c54f3dd1`、r0 原始交付 `011293151` 保持为历史证据（前端与 npm-test pin 未变，Task 表仍指向各自 commit）。**r3 两项 finding 全部落在 runner 脚本，前端零改动**（`src/perf/**` 与 r1 交付逐字节一致，`npm test` 基线 324/324 仍有效）。

## r3 逐项处置

| Finding | 级别 | 处置 | 验证 |
|---|---|---|---|
| FPS-R1-02 滚轮/按键注入未绑定前台焦点（`WM_MOUSEWHEEL` 发给焦点窗口；操作者刚按 Enter 的终端或其他抢焦点窗口会收到输入） | **P1 阻断** | 新增 `Assert-ForegroundIsPid` 守卫：**每轮注入 tick 前**经 `GetForegroundWindow`+`GetWindowThreadProcessId` 校验前台窗口 PID == 本轮 app PID；不符先做一次激活（`TryActivate`＝SW_RESTORE+`SetForegroundWindow`+BringWindowToTop，前台锁被拒时合成 Alt 键解锁重试）后重验；仍不符即 fail-closed（`FOCUS_NOT_OURS`/`FOCUS_ACTIVATE_FAILED`/`FOCUS_NO_HWND` → failures → **exit 6 非零**），绝不在焦点不明时注入。keys 路径检查 `AppActivate` 返回值（false 即 `KEYS_ACTIVATE_FAILED`，不发按键）后仍做前台 PID 复验 | **三窗口实弹自检**（stub=本轮 app 替身同标题窗、decoy=异 PID 同标题干扰窗、outsider=异标题外部窗且**真实持有前台**）：① 外部占前台时 guard 拒绝且 **stub/decoy/outsider 三窗 WM_MOUSEWHEEL 逐窗 WndProc 计数零新增**（外部窗口未收到任何输入的实证），拒绝经 `Fail()` 进入 exit-6 机制（与测量共用同一函数）；② `TryActivate` 把 stub 带到前台、PID 校验通过后注入 1 个滚轮事件**只落在 stub**（decoy 与 outsider 零接收）；`-SafetySelfCheck` 16 项全 PASS exit 0（`selfcheck-20261018-194056/`） |
| FPS-R1-02-AUDIT 自有窗口先被枚举到即提前 return，其后异 PID 同标题窗口不登记 `NOT_OURS_WINDOW` | P2 | `Find-WindowByTitleForPid` 改为**全扫描后返回**：同一次调用既返回自有窗口也登记全部异 PID 同标题窗口 | 自检焦点组判别断言：stub 与 decoy 双同标题窗口在场时，**单次**查找同时返回 stub 并登记 decoy `NOT_OURS_WINDOW`（不论 UIA 枚举顺序），PASS；decoy 组合 SmokeTest 实机复验（decoy 登记、绑定本轮窗口、decoy 存活未触碰，`smoke-20261018-194147/`） |

## 交付物与验证证据

| 交付物 | 路径 | 验证 |
|---|---|---|
| 测量脚本（r3） | `verification/P20-AC4-FPS-1/run-ac4-fps.ps1` | PSParser 0 errors；`-SafetySelfCheck` **16 项断言** PASS exit 0；`-SmokeTest` 与 decoy 组合 `-SmokeTest` 均 PASS exit 0 |
| 步骤说明（r3） | `verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md` | 前台焦点绑定协议、`FOCUS_*` 退出码归类、r3 三条实测记录已同步 |
| r3 Review 入库 | `verification/P20-AC4-FPS-1/codex-review-r3.md` | commit `16b995247`（Canonical Evidence 表 EVID-FPS-REVIEW-R3） |
| 自检证据（r3） | `selfcheck-20261018-194056/`（16 项 PASS）＋ `…193652/…193804/…193857/…193957`（四轮中间 FAIL，先后抓出 `Start-Process -ArgumentList` 不自动加引号、Windows PowerShell 5.1 `Add-Type -TypeDefinition` 需显式 `-ReferencedAssemblies System.Windows.Forms`、C# 裸 `CenterScreen` 不存在、含空格标题参数被拆断——注入开发有效性实证） | 全部入库 |
| 冒烟证据（r3） | `smoke-20261018-194111/`（回归）、`smoke-20261018-194147/`（decoy 在场） | 入库 |
| 前端（r1 交付不变） | `apps/desktop/frontend/src/perf/**` | `npm test` 32 files / 324 tests passed（`npm-test-20261018-r2.log`）；r3 未重跑（零改动） |

## AC 对照（r3 返修后）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认关闭零开销 | **PASS**（单元级，r1） | 默认态 rAF spy 0 注册、无实例无数组、默认 DOM 无面板 |
| AC2 结构化产物 | **PASS**（单元级，r1+r2） | CSV/JSON 结构与导出行为不变；r2 加按钮失败不落盘、JSON 内容校验（runner 侧） |
| AC3 真实桌面测量 | **NOT_RUN（Owner 范围外）** | runner 按 r3 再加固（前台焦点绑定注入）并经 16 项自检 + 双 SmokeTest 实证；单页+Webtoon 测量归 Coordinator（dsh, epoch 8） |
| AC4 p95 如实记录 | **PASS**（机制层，r1） | 排除仅两类且逐样本留痕；kept/all-sample/excluded 三口径并列；阈值 50ms 常量不可配置 |
| AC5 撕裂只记 limitation | **NOT_VERIFIED_BY_RULING** | runner metadata 与 GUIDE 显式声明 |
| AC6 不回归 | **PASS** | r3 零前端改动（基线 324/324 有效）；AC4 既有延迟结论未触碰 |
| AC7 不回归 P20 其他 AC | **PASS** | r3 变更面仅 `verification/P20-AC4-FPS-1/**` + 本 Task/Handoff；未碰 IPC/契约/Schema/ACL/依赖/`apps/desktop/src-tauri/**`/`.qoder-credits/report.json`/`doc/REBASELINE_PLAN.md`/`doc/STATUS.md` |

## 接收方式

- 分支/仓库：`main` @ `G:\CODEX\New Manga`（未新建 worktree）。delivery_head = `16b995247`（实现）；文档 commit 在其后。
- 复现：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SafetySelfCheck`（应 16 项 PASS exit 0；会短暂弹出 decoy/stub/outsider 测试窗口并切换焦点——焦点注入组的设计使然）；
  `pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SmokeTest`（应 AppData UNCHANGED、进程全退、exit 0；会短暂启动 GUI）；
  `cd apps/desktop/frontend && npm test`（应 324 passed，r3 零改动）。
- Coordinator 测量入口：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -BuildFrontend -Mode both`（exe 重编译 `-BuildExe` 需先与 P20-CLOSE-BOUND-HARDEN-1 协调）。测量期间勿操作键鼠：Read-Host 后 runner 会自动激活 app 窗口；中途失焦会自动尝试带回前台，带不回即非零退出。
- 无依赖变化；无共享契约变化。

## 下一任务建议（必填）

- Task ID / 标题：本 Task r4 复审（Reviewer = Codex；这是最后一次返修机会——若仍有未闭合 finding，按用户 DIR-4 裁决以 `closed_with_limitations` 收口并拆加固 Task）；通过后由 Coordinator（dsh, epoch 8）执行 AC3 真实桌面测量。
- 推荐 Agent / Reviewer：Reviewer = Codex；测量执行 = dsh（Coordinator）。
- 推荐原因与前置依赖：r3 两项 finding 已全处置并附实测证据（P1 三窗口实弹：外部占前台零输入 + Fail→exit6 + 滚轮只落 stub）；测量依赖 `-BuildExe`（避开 HARDEN-1 对 `src-tauri/target` 的并行使用）。
- Recovery point：仓库 `G:\CODEX\New Manga`，branch `main`，base `a04e4ea78`，r3 rework delivery `16b995247`（r2=`de5c06a4d`、r1=`4c54f3dd1`、r0=`011293151` 留史）。
- 允许修改路径：复审返修（若有）限 `verification/P20-AC4-FPS-1/**`、`apps/desktop/frontend/src/perf/**`、本 Task 与本 Handoff。
- 禁止范围与新增授权条件：维持 Task 冻结范围（不碰 IPC/契约/`apps/desktop/src-tauri/**`/`.qoder-credits/report.json`/`doc/REBASELINE_PLAN.md`/`doc/STATUS.md`/用户具名 dirty 文件；不得默认开启钩子；不得改 `avg ≤ 50 ms` 口径；不得以排除规则掩盖尖峰）。
- 验证命令、环境与完成 Gate：`npm test` 全绿 + `-SafetySelfCheck` 16 项 exit 0 + `-SmokeTest` exit 0 + Codex r4 Review approved + Coordinator 产出 `run-*/fps-*-samples.csv` 与汇总（avg 判定、p95/all_max 如实）。

## 风险与遗留

- AC3 未执行（归 Coordinator）；焦点守卫在真实 app（WebView2 顶层 HWND 属 m2rc1-desktop 进程）下的端到端滚动随 AC3 实测；自检已用真实 WinForms 顶层窗口对同一守卫/激活/注入函数链做了实弹验证。
- 合成 Alt 键激活是前台锁的标准解锁手法：Alt 按下/释放会送达当时的前台窗口（测量场景下即终端，单独 Alt 按下再释放无副作用）；仅当直接 `SetForegroundWindow` 被前台锁拒绝时才使用。
- 枚举故障注入在**持 ENABLED `SeBackupPrivilege` 的令牌**下无法以 DACL deny 呈现（Windows 语义 bypass）；该环境以通道探针验证（PASS-by-channel，trace 内明示原因）。Coordinator/Reviewer 正常终端令牌无此特权时走完整 deny-ACL 注入路径，两者已在代码中自动分流。
- 治理检查 `tools/governance/check.ps1`：STATUS 指针（`doc/STATUS.md:9` 仍写 r2 head）与 PLAN 同步归 Codex/Coordinator（用户 dirty 文件，Owner 无权改）。
- r3 证据行尾为 LF（本轮写入）；sha256 均按磁盘真实字节实算并已在 Task 注明。
- p95 预期仍超 50ms（既有 77.5ms）：按用户裁决不阻断达标，如实登记；冷路径优化是否立项由 Coordinator 决定。
- 回退方法：revert `16b995247` 即回到 r2 交付（无共享面变更）。
