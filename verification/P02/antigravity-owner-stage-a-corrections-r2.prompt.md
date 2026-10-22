# P02 Stage A 定向修订（DSH changes_requested）

请在现有 Owner worktree `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`、branch `agent/antigravity/P02-real-webview-harness` 上，从固定交付 `972049f991b5c119555647eeea816e89dd4769f3` 继续，完成下面的 Stage A 证据与脚手架修订，并提交新的固定交付 commit + Handoff。

P02 行为范围 r1–r4 与 Owner allowlist 已冻结；不要重冻结、扩大范围或修改产品行为。当前正式 DSH Review 对 `base=5de8d44c784cbd20b23bcd41a8f1a7258c7addff`、`reviewed_head=972049f991b5c119555647eeea816e89dd4769f3` 的 decision 为 `changes_requested`。完整报告在 Codex root 的 `doc/reviews/P02-972049f9-dsh-review.md`（报告指出 DSH 无 shell、tree/scope SHA 未能独立复核；Codex 会在 Gate 复算）。逐项计数已由同一 DSH session 核实：`P0/P1/P2/P3=0/1/6/5`，F-01 为 P1，F-02–F-07 六项 P2，F-08–F-12 五项 P3，全部 open。下面完整列出修订点，不要依赖 root review 文件存在于 Owner worktree。

## 必须修订的 DSH findings

1. **F-01 P1：准确描述当前 Stage A。** 当前代码没有 CDP 客户端，`target_exe`/`cdp_port` 未使用，AC 分支被硬编码 build barrier 截断，TS 文件也未被 import 且 `tsconfig` 不包含 `e2e/`。把 handoff/Task execution note/docstring 的“管理 CDP 通信、实现 AC1–AC7 驱动”等表述改为“Stage A preflight/verdict report generator；CDP/行为驱动尚未实现”。删除真正无用的参数/死导入。不要在本修订里冒称完成 Stage B 或真实 UI 验证；AC1–AC6 运行时继续 `BLOCKED`。后续 WebView 驱动仍是 P02 目标，但构建须等 Codex 隔离 scratch-build Gate。
2. **F-02 P2：颜色来源真实。** 当前夹具的七个 `visual_direction_f_tokens` 值并非 F token，其中 `#58a6ff`、`#2a3038` 在 `src/**` 无来源。将真实方向 F token（`bg-page #1a1a1d`、`ink #ececee`、`ink-2 #a9a9b3`、`ink-3 #91919c`、`ink-dis #70707b`、`accent #4d63e8`）与当前 Workbench `live_inline_palette` 分开记录；内联色逐值记来源文件/行，删除无来源色。未实际匹配到 F token 时 `token_mapping=UNMAPPED`，不要称为 MAPPED。
3. **F-03 P2：消除对比度数字矛盾。** handoff 的 `14.28:1/5.76:1` 与 JSON 报告的 `13.87/6.01` 不一致，且无 artifact 支持前者。以一个机器可读结果为单一来源，handoff 链接该结果，不重复手写数字；本次仅报告确切实际算出的前置模型数值，不声称 runtime 采集。
4. **F-04 P2：区分前置控制与 AC6。** 把 `TOKEN_MODEL` 场景的 `ac_id: AC6` 改成 `PRE-03`/`AC6-PRECHECK` 等非 AC6 标识。真实 runtime AC6 必须继续单独 `BLOCKED`，没有 computed colors 时不可出现 AC6 `PASS`，也不得遗漏 `token_mapping` 与 `contrast_result` 的状态字段。
5. **F-05 P2：修正 provenance。** 当前 reports 将 `source_head/tree` 错填为 diff base `5de8d44c/f27d12a7`，且 `is_clean:false`，handoff 缺实际交付 head/tree。重新生成报告并绑定被测 source commit/tree、测试命令和相关 artifact hashes；明确区分行为基线 `241ff3b7…`、source commit、delivery/evidence commit。避免让一个文件自引用其最终 commit；如测试源与只含证据的后续提交不同，分别命名并记录。不要伪造 shell/Node 输出。
6. **F-06 P2：退出状态必须是观察值。** 不能把未执行场景的 `exit_code` 写成常量 `126`；未尝试场景设 `null`/省略，runner/powershell 实际进程 exit 单独记录。为真实执行的 probe 留存含准确命令、PowerShell/Python/Node 版本头、stdout、stderr、EXIT 的原始日志。让 runner 聚合各 probe/harness 返回状态；子检查失败必须导致非零退出，不要无条件 `exit 0`。本轮只运行无构建的 `run-webview.ps1 -ProbeOnly` 与允许的 synthetic/static controls。
7. **F-07 P2：更新 `verification/P02/RESUME.md`。** 当前恢复点仍说 formal implementation prompt 未发送、所有证据 `NOT_RUN`，会引起重复派发。保留历史段，更新当前 checkpoint 为本轮 Stage A fixed head、DSH decision/findings、实际验证状态、root/Owner heads、硬构建屏障及下一条指令。
8. **F-08 P3：令数学检查真实使用数据。** 当前 harness 读取 `tokens` 却以硬编码 RGB 计算。解析夹具中实际 hex 值并记录来源；改动夹具应能改变结果；或移除死加载与不实检查名。对 `rgba()` 前景/背景先做 alpha 合成再计算 WCAG ratio，不能简单截断 alpha；新逻辑保留一个小自检/断言。
9. **F-09 P3：修环境探针。** 探针代码 GUID 与其本次采集到的 WebView2 Registry GUID 不一致，导致 WebView2 分支死代码并可能退回任意 EdgeUpdate 产品版本；修正为真实 WebView2 key，找不到时返回 `UNKNOWN` 而非猜测。Windows 的 `npm` `.cmd` 调用异常不得静默成为空字符串，应在报告中显式记录 unavailable/error。PowerShell runner 与 Python harness 使用同一 Python 解释器；同一运行不重复执行静态 probe。
10. **F-10 P3：修 synthetic fixture 契约。** `synth-page-102 has_regions=true` 却没有对应 regions；region payload 与真实 `region/types.ts` / client contract 不匹配（字段应按实际数据形状如 `region_id`、`revision_no`、真实 region enum 复核，不要使用 `id/current_revision/dialogue/thought` 占位）。区分 UI `undo` 动作和真实 IPC 命令；在每个 AC4 场景中列出实际 write command、write 返回、随后 `list_regions` readback 与顺序/单调时钟期望。删除不适用于普通 fixture 数据的顶层 `$schema`。
11. **F-11 P3：修协议层类型的可信度。** 当前 TS layer union 与 JSON 实际输出的 `FILESYSTEM`/`STATIC_AST`/`TOKEN_MODEL` 不匹配，且此 TS 文件未被 TypeScript 编译或 import。要么把它修成与实际 evidence protocol 一致并提供无新增依赖的静态检查，要么删除/延期到 Stage B；不得继续称它已提供可执行 AC 驱动。
12. **F-12 P3：更新 Task 测试表。** 将已实际执行的 preflight/static controls 与运行时 `BLOCKED` 分行记录并链接到准确报告和原始日志；不能让表格仍写 `NOT_RUN/无` 而报告已有 BLOCKED 证据，也不能把 BLOCKED 混写成 PASS。

## Codex 独立 Review 的补充问题

- 修正 fixture 与实际 Workbench region payload/enum/ID 字段不匹配（见上 F-10）。
- contrast alpha 必须正确合成（见上 F-08）。
- `main()` 必须检查并传播 static/control probe 失败（见上 F-06）。
- Codex 固定范围 `git diff --check 5de8d44c784cbd20b23bcd41a8f1a7258c7addff 972049f991b5c119555647eeea816e89dd4769f3` 返回 `EXIT=2`，发现 6 个 JSON/TXT report 的 293 条 trailing-whitespace 诊断；证据在 root `verification/P02/implementation-stage-a-972049f9-diff-check.log`。修正新增/变更 P02 产物的行尾/空白并在新 head 复跑确切 Git-object diff-check，保存完整输出与 EXIT。不要把 P02 以外既有文件重新格式化。
- 独立 Review 还发现 AC6 值及最终结果无条件 PASS、fixture 色值错误、static probe 返回被忽略、WebView2 fallback 会误认其他 EdgeUpdate 产品。以上均在 F-02/F-04/F-06/F-08/F-09 处理。

## 范围和交付要求

- 只修改 Owner allowlist：`verification/P02/**`、`apps/desktop/frontend/e2e/**`、`doc/handoffs/P02-*.md`，以及 `doc/tasks/P02.md` 的真实执行/交付记录。不得改 `STATUS`、Plan、ROADMAP、共享契约/Schema、依赖、`frontend/src/**`、`src-tauri/**`、Python Core、P03 runner 或设计 token。
- 保留原始 r1 报告、DSH Review 与历史证据，不覆盖 root 的 Codex/DSH review carriers；新日志使用新的 r2 名称或依靠 Git 历史保留前态。
- 不运行 Cargo/Tauri/sidecar build，不启动产品 WebView，不访问真实用户数据，不添加依赖，不修产品行为。
- 允许重新运行 `run-webview.ps1 -ProbeOnly`、fixture/static/math 自检。逐项记录实际命令、状态、观测到的 runner exit、stdout/stderr 和环境头；未执行的场景保留 `BLOCKED`/`NOT_RUN` 与原因。
- 更新 Handoff、Task evidence table、当前 RESUME；检查 `git diff --check`、allowlist、working tree。提交后给出 commit/tree、每条 finding disposition、测试/探针实际 EXIT、文件清单、剩余风险和下一步。不要声称 P02 done 或 runtime AC PASS。

请先只读核对 branch/head/dirty 是否仍匹配上述基线，再实施。若受保护数据出现新的 drift，停止于该边界、保留现场并在 Handoff 如实记录。
