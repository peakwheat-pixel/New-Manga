---
task_id: P20-AC4-FPS-1
author: ZCode
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 4c54f3dd1
status: delivered_for_review
review_round: r1-rework
---

# Handoff：P20-AC4-FPS-1（AC4 帧率与帧时间测量钩子）r1 返修

## 交付结果

本轮为 codex-review-r1（`changes_requested`）的返修交付。实现 commit `4c54f3dd10e5e7168500e96687b67097ccae2c00`（main，29 个明确路径）；本文档随其后的文档 commit 一并入库。r0 原始交付 `011293151` 保持为历史证据（其 npm-test log 与 main.tsx pin 未变，Task 表仍指向该 commit）。

## FPS-R1 逐项处置

| Finding | 级别 | 处置 | 验证 |
|---|---|---|---|
| FPS-R1-01 隔离根不完整，可能写用户 AppData | P1 FAIL | runner 启动前把 `NEWMANGA_DATA_ROOT`/`M2RC1_DERIVED_ROOT`/`M2RC1_MANAGED_ROOT`/`M2RC2_CATALOG_DB` 全部钉到新建 `%TEMP%` 隔离根并读回校验，任一缺失/越界拒绝启动（exit 7）；`-DevSrcRoot` 显式设置并核对 `M2RC1_SRC_ROOT`（dev 模式），不传时要求 exe 旁 packaged sidecar 存在（否则 app 必 panic，同样拒绝）；真实 AppData 启动前/收尾后逐文件 sha256 快照比对，任何变化 FAIL | **实测 PASS**：`-SmokeTest` 启动 exe 12 s（窗口正常）→ 收尾只清本轮进程全退 → 真实 AppData **24 文件 sha256 前后 UNCHANGED** → 写入（`catalog/catalog.sqlite`、`library.db`、`derived/.preview-lifecycle.lock`、`managed/temp`）全部落在隔离根，exit 0 |
| FPS-R1-02 按进程名杀全局同名进程 | P1 FAIL | 只记录并清理本轮 app PID 及其后代（Win32_Process PPID 链；启动后与每轮 capture 前刷新；收尾补扫孤儿）；Stop-Process 前按家族白名单（m2rc1-desktop/core_service/host_bridge/acceptance_bridge/catalog_loader）复核防 PID 复用；既有同名进程登记 `NOT_OURS` 绝不触碰；清理统一 `try/finally`（正常/失败/人工中止三路覆盖），收尾复查全退、残留即 FAIL | 冒烟中 11 个后代 PID 全部清理退出（`TEARDOWN all our processes exited`）；启动前探测 `NOT_OURS no pre-existing same-name processes` |
| FPS-R1-03 失败仍返回 exit 0 | P1 FAIL | 失败累积制：CSV/JSON 缺失、capture 失败、kept=0、`avg>50ms`、AppData 变化、本轮进程残留任一 → exit 6；SmokeTest 不再提前 exit 0（落到统一失败计算）；退出码表 0/2/3/4/5/6/7 固化于 GUIDE | `-SafetySelfCheck` 6 项 PASS exit 0；`-SmokeTest` exit 0；首跑自检曾 FAIL（exit 6）抓出 iso 前缀判定缺陷——失败路径真实非零 |
| FPS-R1-04 导出走 WebView2 默认下载目录 | P2 PARTIAL | 面板导出改 `window.showSaveFilePicker()` 显式 Save As：目标由调用方选、**取消即不写任何位置**、无默认目录回退（Blob+anchor.download 路径已删除）；无 picker 环境明示用 Show/Copy；前端仍不接触绝对路径（handle 不暴露 path） | 单测三态：saved（内容=suggestedName 文件、createObjectURL/anchor.click 零调用）、cancelled（AbortError→"nothing written"）、unsupported（"unavailable"+零写入） |
| FPS-R1-05 ≥1s 无条件排除可能掩盖前台停顿 | P2 PARTIAL | 排除仅当 `delta≥1000ms` **且与采样的 hidden 区间相交**（visibilitychange 跟踪，源可注入；无跟踪能力时保守保留）；reason 更名 `raf_gap_ge_1000ms_while_hidden`；summary/标题/JSON 新增 `allMaxMs`（全样本 max）与 `excludedMaxMs`，runner 复算同步输出 `all_max_ms`/`excluded_max_ms` | 单测：visible 下 5100ms 停顿保留参与 kept（avg FAIL 如实）、hidden 区间内排除且留 CSV、有跟踪但无 hidden 仍保留、allMax/excludedMax 双口径、titleSummary 含 `allmax=` |

## 交付物与验证证据

| 交付物 | 路径 | 验证 |
|---|---|---|
| 采样钩子本体 | `apps/desktop/frontend/src/perf/fpsRecorder.ts` | `npm test` 32 files / **324** tests passed，exit 0（`verification/P20-AC4-FPS-1/npm-test-20261018-r2.log`）；`npx tsc --noEmit` exit 0 |
| 导出面板 | `apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx` | 同上（saved/cancelled/unsupported 三态用例） |
| 单元测试 | `src/perf/fpsRecorder.test.ts`、`src/perf/FpsRecorderPanel.test.tsx` | 同上 |
| 测量脚本 | `verification/P20-AC4-FPS-1/run-ac4-fps.ps1` | parser 0 errors；`-SafetySelfCheck` exit 0（`selfcheck-20261018-173828/`）；`-SmokeTest` exit 0（`smoke-20261018-173917/`） |
| 步骤说明 | `verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md` | 排除口径/导出行为/退出码表/隔离与进程安全/Owner 实测记录已同步 |
| r1 Review 入库 | `verification/P20-AC4-FPS-1/codex-review-r1.md` | commit `4c54f3dd1`（Canonical Evidence 表 EVID-FPS-REVIEW-R1） |

**Owner 侧实测如何证明未写用户 AppData**：`-SmokeTest` 在启动 exe 前对 `%APPDATA%\com.newmanga.m2rc1.desktop` 做逐文件 sha256 清单（`appdata-baseline.txt`，24 文件），12 秒运行并完整收尾后重拍 `appdata-after.txt` 逐路径比对 → `UNCHANGED`；同期隔离根内实际产生 `catalog/catalog.sqlite`、`library.db`、`derived/.preview-lifecycle.lock`、`managed/temp`——即"有写入行为但全部落在隔离根"的正反双证。快照比对机制本身经 `-SafetySelfCheck` 阴性（相同树→UNCHANGED）与阳性（改+增→MUTATED）对照验证。

## AC 对照（r1 返修后）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认关闭零开销 | **PASS**（单元级） | 默认态 rAF spy 0 注册、无实例无数组、默认 DOM 无面板；可见性监听仅 start() 时注册、stop/reset 注销 |
| AC2 结构化产物 | **PASS**（单元级） | CSV/JSON（meta+summary+samples，含 allMaxMs/excludedMaxMs）；导出仅经显式 Save As 或 UIA 抓取写 OutDir；代码无路径写入、不触碰 AppData、无默认落盘 |
| AC3 真实桌面测量 | **NOT_RUN（Owner 范围外）** | runner 已按 r1 Review 加固并经 SafetySelfCheck/SmokeTest 实证；单页+Webtoon 测量归 Coordinator（dsh, epoch 8） |
| AC4 p95 如实记录 | **PASS**（机制层） | 排除仅两类且逐样本留痕（hidden 相关 gap / non_positive）；kept/all-sample/excluded 三口径并列；阈值 50ms 常量不可配置 |
| AC5 撕裂只记 limitation | **NOT_VERIFIED_BY_RULING** | runner metadata 与 GUIDE 显式声明 |
| AC6 不回归 | **PASS** | `npm test` 324/324（基线全保留）；`tsc` 0；AC4 既有延迟结论 `verification/P20/ac4-20261018-0720/**` 未触碰 |
| AC7 不回归 P20 其他 AC | **PASS** | 变更面仅 `frontend/src/perf/**` + `verification/P20-AC4-FPS-1/**`；未碰 IPC/契约/Schema/ACL/依赖/`src-tauri/**`/用户 20 个 dirty 文件 |

## 接收方式

- 分支/仓库：`main` @ `G:\CODEX\New Manga`（未新建 worktree）。delivery_head = `4c54f3dd1`（实现）；文档 commit 在其后。
- 复现：`cd apps/desktop/frontend && npm test`（应 324 passed）；`npx tsc --noEmit`（应 exit 0）；
  `pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SafetySelfCheck`（应 6 项 PASS exit 0）；
  `pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SmokeTest`（应 AppData UNCHANGED、进程全退、exit 0；会短暂启动 GUI）。
- Coordinator 测量入口：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -BuildFrontend -Mode both`（exe 重编译 `-BuildExe` 需先与 P20-CLOSE-BOUND-HARDEN-1 协调）。
- 无依赖变化；无共享契约变化。

## 下一任务建议（必填）

- Task ID / 标题：本 Task r2 复审（Reviewer = Codex）；通过后由 Coordinator（dsh, epoch 8）执行 AC3 真实桌面测量。
- 推荐 Agent / Reviewer：Reviewer = Codex；测量执行 = dsh（Coordinator）。
- 推荐原因与前置依赖：五项 finding 已全处置并附实测证据；测量依赖 `-BuildExe`（避开 HARDEN-1 对 `src-tauri/target` 的并行使用）。
- Recovery point：仓库 `G:\CODEX\New Manga`，branch `main`，base `a04e4ea78`，r1 rework delivery `4c54f3dd1`。
- 允许修改路径：复审返修限 `apps/desktop/frontend/src/perf/**`、`verification/P20-AC4-FPS-1/**`、本 Task 与本 Handoff。
- 禁止范围与新增授权条件：维持 Task 冻结范围（不碰 IPC/契约/`src-tauri/**`/用户 20 个 dirty 文件；不得默认开启钩子；不得改 `avg ≤ 50 ms` 口径；不得以排除规则掩盖尖峰）。
- 验证命令、环境与完成 Gate：`npm test` 全绿 + `-SafetySelfCheck`/`-SmokeTest` exit 0 + Codex r2 Review approved + Coordinator 产出 `run-*/fps-*-samples.csv` 与汇总（avg 判定、p95/all_max 如实）。

## 风险与遗留

- 治理检查 `tools/governance/check.ps1`：READY DAG 指针项（`P20-AC4-FPS-1 当前为 in_review`）仍需 Codex 同步 `doc/REBASELINE_PLAN.md`（用户 dirty 文件，Owner 无权改）；其余见运行输出。
- AC3 未执行（归 Coordinator）；`-SmokeTest` 已实证隔离/进程所有权/退出码，但不产生测量数据。
- r1 证据行尾为 LF（本轮写入），与 r0 的 CRLF 检出字节不同；sha256 均按各自当时磁盘真实字节实算并已在 Task 注明。
- p95 预期仍超 50ms（既有 77.5ms）：按用户裁决不阻断达标，如实登记；冷路径优化是否立项由 Coordinator 决定。
- 回退方法：revert `4c54f3dd1` 即回到 r0 交付（无共享面变更）。
