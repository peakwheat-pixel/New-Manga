---
task_id: P20-AC4-FPS-1
author: ZCode
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: de5c06a4d
status: delivered_for_review
review_round: r2-rework
---

# Handoff：P20-AC4-FPS-1（AC4 帧率与帧时间测量钩子）r2 返修

## 交付结果

本轮为 codex-review-r2（`changes_requested`）的返修交付。实现 commit `de5c06a4d572c849de7d7fed8e5027f92e0de156`（main，22 个明确路径）；本文档随其后的文档 commit 一并入库。r1 返修 `4c54f3dd1`、r0 原始交付 `011293151` 保持为历史证据（前端与 npm-test pin 未变，Task 表仍指向各自 commit）。**r2 四项 finding 全部落在 runner 脚本，前端零改动**（`src/perf/**` 与 r1 交付逐字节一致，`npm test` 基线 324/324 仍有效）。

## r2 逐项处置

| Finding | 级别 | 处置 | 验证 |
|---|---|---|---|
| FPS-R1-02 窗口未绑定本轮进程（UIA 可能操作他人同标题实例） | **P1 阻断** | 窗口查找重写为 `Find-WindowByTitleForPid`：枚举**全部**同标题顶层窗口，只返回 `ProcessId` == 本轮 app PID 的那个；**无「取首个同标题窗口」回退**；异进程同标题窗口登记 `NOT_OURS_WINDOW`（每 pid 一次）且永不点击/滚动/杀灭。测量路径窗口就绪后经 `Assert-OurWindow` 二次校验（不匹配 exit 2）；`WINDOW_BOUND pid=...` 日志固定绑定证据；滚动注入期间 app 退出即 `SCROLL_ABORT` FAIL | **两层实测**：① `-SafetySelfCheck` 干扰窗口注入三连 PASS（decoy 自身 PID 可查得=阳性对照／异 PID 返回 null=无首匹回退／`NOT_OURS_WINDOW` 审计轨迹），`selfcheck-20261018-180541/`；② 实机组合：持久 decoy 窗口（pid=48468）在场跑 `-SmokeTest` → 登记 NOT_OURS_WINDOW 48468 → 绑定本轮窗口（`window_pid=29896 app_pid=29896` 一致）→ 11 后代全退 → AppData UNCHANGED → exit 0 → **decoy 全程存活未被触碰**（验证后自行清理），`smoke-20261018-180626/` |
| FPS-R1-01 AppData 快照不完整可能漏报（同路径前后均读失败 → 误判未变化）；缺故障注入 | PARTIAL | `Get-TreeManifest` 把枚举错误（`ENUM_FAIL`）与哈希错误（`HASH_FAIL`）记入错误表：**基线不完整拒绝启动（exit 7，不启动 exe）**、终末快照不完整 FAIL（exit 6）；`Compare-Manifests` 加 UNREADABLE 守卫（双侧不可读 → NOT-unchanged）。故障注入进 `-SafetySelfCheck`：独占锁定文件→HASH_FAIL 入表 PASS；同路径双侧 UNREADABLE→拒绝 PASS；枚举注入在本 Owner 令牌下因持 **ENABLED `SeBackupPrivilege`**（Windows 设计 bypass 读类 DACL）诚实降级为 PASS-by-channel（missing-directory 探针证明喂 ENUM_FAIL 的 `-ErrorVariable` 通道存活），无特权令牌走完整 deny-ACL 注入路径 | 12 项断言 PASS exit 0；**注入开发自身抓出两个真实缺陷并修复**（`Get-FileHash` 非终止错误须 `-ErrorAction Stop` 才进 catch，否则 `$hash` 静默变 `$null`；icacls `(OI)(CI)` 为 inherit-only 不作用于目录本对象）——两次中间 FAIL（`selfcheck-20261018-180101/`、`...180200/`）留档为注入有效性实证 |
| FPS-R1-03 两处 false-pass（JSON artifact 可为残留内容；SmokeTest 窗口缺失/早退/隔离空仍 exit 0） | PARTIAL | ① `Show CSV`/`Show JSON` 按钮失败即 FAIL 且**不把 textarea 残留写成 artifact**；CSV 校验表头+行结构；JSON **解析并校验确为本轮数据**（`meta.task`、`totalSamples`/`excludedCount`、`samples[]` 长度 vs CSV 行数、首/末样本 `frameTsMs` vs CSV 首末行 `frame_ts_ms`）——上一轮残留 payload 无法通过。② SmokeTest 三处 false-pass 闭合：`SMOKE_NO_WINDOW`／`SMOKE_APP_EXITED_EARLY`／`..._DURING_SETTLE`／`ISO_EMPTY` 全部进 failure list（exit 6） | 按钮失败/结构不符/内容不匹配路径均产生非零退出（代码路径直连 failure list）；SmokeTest 窗口/退出/隔离判据在 decoy 组合冒烟中以正向形态验证（window_pid==app_pid、iso 4 文件、exit 0）；JSON 交叉核对的端到端执行归 AC3 实测（Coordinator） |
| smell：`T`/`F` 命名不明 | 非阻断 | `T` → `Write-Trace`（日志职责）、`F` → `Find-UiaByName`（UIA 查找职责），全部调用点同步（含 `$refuse` 两处漏网形态） | `grep -P '(?<![A-Za-z0-9_$.])T [("\'']'` 零残留；PSParser 0 errors |

## 交付物与验证证据

| 交付物 | 路径 | 验证 |
|---|---|---|
| 测量脚本（r2） | `verification/P20-AC4-FPS-1/run-ac4-fps.ps1` | PSParser 0 errors；`-SafetySelfCheck` **12 项断言** PASS exit 0；decoy 组合 `-SmokeTest` PASS exit 0 |
| 步骤说明（r2） | `verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md` | 窗口绑定/快照 fail-closed/JSON 校验/SmokeTest 失败条件/12 项自检表/decoy 冒烟记录已同步 |
| r2 Review 入库 | `verification/P20-AC4-FPS-1/codex-review-r2.md` | commit `de5c06a4d`（Canonical Evidence 表 EVID-FPS-REVIEW-R2） |
| 自检证据（r2） | `selfcheck-20261018-180541/`（PASS）＋ `...180101/`、`...180200/`（中间 FAIL，注入有效性实证） | 全部入库 |
| 冒烟证据（r2, decoy 在场） | `smoke-20261018-180626/` | 入库 |
| 前端（r1 交付不变） | `apps/desktop/frontend/src/perf/**` | `npm test` 32 files / 324 tests passed（`npm-test-20261018-r2.log`）；`tsc --noEmit` 0；r2 未重跑（零改动） |

## AC 对照（r2 返修后）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认关闭零开销 | **PASS**（单元级，r1） | 默认态 rAF spy 0 注册、无实例无数组、默认 DOM 无面板 |
| AC2 结构化产物 | **PASS**（单元级，r1+r2） | CSV/JSON 结构与导出行为不变；r2 加按钮失败不落盘、JSON 内容校验（runner 侧） |
| AC3 真实桌面测量 | **NOT_RUN（Owner 范围外）** | runner 按 r2 再加固（窗口绑定/快照 fail-closed/artifact 校验）并经 12 项自检 + decoy 组合冒烟实证；单页+Webtoon 测量归 Coordinator（dsh, epoch 8） |
| AC4 p95 如实记录 | **PASS**（机制层，r1） | 排除仅两类且逐样本留痕；kept/all-sample/excluded 三口径并列；阈值 50ms 常量不可配置 |
| AC5 撕裂只记 limitation | **NOT_VERIFIED_BY_RULING** | runner metadata 与 GUIDE 显式声明 |
| AC6 不回归 | **PASS** | r2 零前端改动（基线 324/324 有效）；AC4 既有延迟结论未触碰 |
| AC7 不回归 P20 其他 AC | **PASS** | r2 变更面仅 `verification/P20-AC4-FPS-1/**` + 本 Task/Handoff；未碰 IPC/契约/Schema/ACL/依赖/`src-tauri/**`/`.qoder-credits/report.json`/`doc/REBASELINE_PLAN.md`/`doc/STATUS.md` |

## 接收方式

- 分支/仓库：`main` @ `G:\CODEX\New Manga`（未新建 worktree）。delivery_head = `de5c06a4d`（实现）；文档 commit 在其后。
- 复现：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SafetySelfCheck`（应 12 项 PASS exit 0；含 decoy 窗口注入，会短暂弹一个 320x200 窗口）；
  `pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SmokeTest`（应 AppData UNCHANGED、进程全退、exit 0；会短暂启动 GUI）；
  `cd apps/desktop/frontend && npm test`（应 324 passed，r2 零改动）。
- Coordinator 测量入口：`pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -BuildFrontend -Mode both`（exe 重编译 `-BuildExe` 需先与 P20-CLOSE-BOUND-HARDEN-1 协调）。
- 无依赖变化；无共享契约变化。

## 下一任务建议（必填）

- Task ID / 标题：本 Task r3 复审（Reviewer = Codex）；通过后由 Coordinator（dsh, epoch 8）执行 AC3 真实桌面测量。
- 推荐 Agent / Reviewer：Reviewer = Codex；测量执行 = dsh（Coordinator）。
- 推荐原因与前置依赖：r2 四项 finding 已全处置并附实测证据（P1 两层验证）；测量依赖 `-BuildExe`（避开 HARDEN-1 对 `src-tauri/target` 的并行使用）。
- Recovery point：仓库 `G:\CODEX\New Manga`，branch `main`，base `a04e4ea78`，r2 rework delivery `de5c06a4d`（r1=`4c54f3dd1`、r0=`011293151` 留史）。
- 允许修改路径：复审返修限 `verification/P20-AC4-FPS-1/**`、`apps/desktop/frontend/src/perf/**`、本 Task 与本 Handoff。
- 禁止范围与新增授权条件：维持 Task 冻结范围（不碰 IPC/契约/`src-tauri/**`/`.qoder-credits/report.json`/`doc/REBASELINE_PLAN.md`/`doc/STATUS.md`/用户具名 dirty 文件；不得默认开启钩子；不得改 `avg ≤ 50 ms` 口径；不得以排除规则掩盖尖峰）。
- 验证命令、环境与完成 Gate：`npm test` 全绿 + `-SafetySelfCheck` 12 项 exit 0 + `-SmokeTest` exit 0 + Codex r3 Review approved + Coordinator 产出 `run-*/fps-*-samples.csv` 与汇总（avg 判定、p95/all_max 如实）。

## 风险与遗留

- AC3 未执行（归 Coordinator）；`-SmokeTest` 已实证隔离/进程所有权/窗口 PID 绑定/退出码，但不产生测量数据；JSON 交叉核对的端到端执行也随 AC3 实测。
- 枚举故障注入在**持 ENABLED `SeBackupPrivilege` 的令牌**下无法以 DACL deny 呈现（Windows 语义 bypass，实测 cmd dir 亦照常）；该环境以通道探针验证（PASS-by-channel，trace 内明示原因）。Coordinator/Reviewer 正常终端令牌无此特权时走完整 deny-ACL 注入路径，两者已在代码中自动分流。
- 治理检查 `tools/governance/check.ps1`：STATUS 指针（`doc/STATUS.md:9` 仍写 r0 head）与 PLAN 同步归 Codex/Coordinator（用户 dirty 文件，Owner 无权改）。
- r2 证据行尾为 LF（本轮写入）；sha256 均按磁盘真实字节实算并已在 Task 注明。
- p95 预期仍超 50ms（既有 77.5ms）：按用户裁决不阻断达标，如实登记；冷路径优化是否立项由 Coordinator 决定。
- 回退方法：revert `de5c06a4d` 即回到 r1 交付（无共享面变更）。
