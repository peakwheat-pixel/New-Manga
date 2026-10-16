---
task_id: EXPORT-REVEAL-1
author: Codex
recipient: Coordinator
base_commit: 958fa8a5b137f2b99ec74ba5902760e1d8aaebdc
delivery_head: 13a748b03b1fcf97518ece18abc2b704fc53599f
status: in_review
---

# Handoff：EXPORT-REVEAL-1（post-merge）

## 交付结果

已在 codex/EXPORT-REVEAL-1 把 main (07bb1b0608af6052725d98a51790ab9fcc47ab43) 并入任务分支，冲突解决提交为 b1e4d87d49295b1a76453b6960060be2a648f8f8。随后归档重跑与冲突说明于 4e4d73a0be67407d92487cf240d695c4041c158d，Task 更新提交为 13a748b03b1fcf97518ece18abc2b704fc53599f。

两侧功能都保留：

- apps/desktop/src-tauri/src/library_bridge.rs 保留 EVENTS-FWD-1 的 stdout 后台读线程、pending_responses 按 request_id 解复用和六类安全事件投影；保留 EXPORT-REVEAL-1 的 session_export_ids、当前会话拒绝面及 GetExportHistory 查询。Reveal 通过 round_trip("GetExportHistory", …) 使用新 exchange 路径。未恢复内联请求读线程。
- apps/desktop/src-tauri/src/main.rs 同时保留 .manage(state) 前移、setup 内事件 sink 注册和 library_reveal_export_folder 注册。
- capabilities/m2rc1-commands.json 与生成的 gen/schemas/capabilities.json 同时保留 reveal permission 和 core:event:allow-listen / allow-unlisten。
- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md 合并为联合 rev 2.4 总览；§5.8 正文与合并前文本在换行归一后逐字相同。拒绝码、production-only 边界、路径保密和 ExportTargetRef 单次消费语义没有改变。

冲突逐处说明与验证证据见 verification/EXPORT-REVEAL-1/merge-resolution.md。没有修改 doc/tasks/EVENTS-FWD-1.md；没有 push 或合并到 main。用户 19 项 dirty 位于主 worktree，本次没有在主 worktree 写入或整理它们。

delivery_head 为填写本 Handoff 时的 git rev-parse HEAD：13a748b03b1fcf97518ece18abc2b704fc53599f。由于 Handoff 提交及随后用于 pin 本 Handoff 的 Task 元数据提交会推进分支，delivery_head 为填表时刻的 HEAD，最终 HEAD 以 git rev-parse HEAD 为准；Coordinator closeout 时冻结实际 HEAD。

本次是重新交付，Task 保持 in_review。原 R1 的 approved 仅绑定合并前 head，不代表本 head 已获接受；等待 Coordinator 复核。

## 验证证据

所有指定运行从 G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1 使用 PowerShell 7.6.6（C:\Program Files\PowerShell\7\pwsh.exe）。三份日志均记录命令、环境、原始输出和退出码。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 / §5.8 | 对比合并前 §5.8 正文并审阅联合 rev 2.4 总览 | §5.8 对比 5e698742ad2a2283c0bd0c7605d270cff00ad224 与合并结果；当前重审待做 | §5.8 正文未变；新 head 尚待 Coordinator 复核 | verification/EXPORT-REVEAL-1/merge-resolution.md |
| AC4-①/②、Rust source | cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests | M2RC1_PYTHON=C:\Python314\python.exe；M2RC1_PACKAGED / M2RC1_SRC_ROOT unset；测试代码在 merge commit b1e4d87d4 | 86 passed，0 failed，1 ignored，9 filtered；exit 0。same_channel_concurrent_round_trips_keep_response_ownership、4 个 test_events_fwd_*、export_reveal_command_is_production_only、reveal resolver/rejection cases 和 opener 未调用断言均通过 | verification/EXPORT-REVEAL-1/post-merge-source.log |
| AC4-③ / packaged sidecar | cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 | M2RC1_PACKAGED=1；M2RC1_SRC_ROOT / M2RC1_PYTHON unset；测试代码在 merge commit b1e4d87d4 | 9 passed，0 failed，0 ignored；exit 0。包含 real_library_sidecar_event_sink_registration_and_lifecycle。此 suite 不证明真实 GUI Reveal | verification/EXPORT-REVEAL-1/post-merge-packaged.log |
| AC4-③ / GUI Reveal | 本次未重跑 GUI 往返 | 既有 frozen bundle 证据 | 继续 BLOCKED：fixture missing-book 返回 TARGET_NOT_FOUND，无成功输出；WebView2 0x80070578 阻止真实 GUI 往返。没有声称发生过打开动作 | frozen-export-attempt.log、reveal-roundtrip-status.md、verification/PROJECT-ORCHESTRATION-20261016/checkpoint-r9.md |
| AC6 / Core Python | C:\Python314\python.exe -m pytest tests/core -q -p no:cacheprovider | Python 3.14.6；测试代码在 merge commit b1e4d87d4 | 405 passed，1 Pillow deprecation warning；exit 0 | verification/EXPORT-REVEAL-1/post-merge-python.log |

一次错误的 PowerShell 捕获尝试把 -Append 传给 Rust harness，exit 101；它没有进入测试，未计入验证结果。记录在 post-merge-packaged-capture-error.log，正确的 packaged 结果见上表。Cargo 产生的 permission/schema 行尾噪音经 git diff 确认后已从 worktree 恢复。真实 GUI e2e 未运行，AC4-③ 保持 BLOCKED。

## 接收方式

- Branch/worktree：codex/EXPORT-REVEAL-1 / G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1
- 原始基线：958fa8a5b137f2b99ec74ba5902760e1d8aaebdc
- merge commit：b1e4d87d49295b1a76453b6960060be2a648f8f8
- 本 Handoff 填表时 head：13a748b03b1fcf97518ece18abc2b704fc53599f；开始复核前请在该 worktree 运行 git rev-parse HEAD 并以实际值冻结 review target。
- 不要清理或覆盖未跟踪数据。验证期间 worktree 出现 verification/P04/diagnostic_p22_40684_1792151017412.jsonl；来源未确认，保持未跟踪且未纳入本交付。

## 下一任务建议（必填）

- Task ID / 标题：EXPORT-REVEAL-1 / 合并后独立复核与 Coordinator 集成验收。
- 推荐 Agent / Reviewer：DeepSeek Harness 复核；Codex/Coordinator 在复核后执行集成验收。此前 R1 不能覆盖新 head。
- Recovery point：仓库 G:/CODEX/New Manga；branch codex/EXPORT-REVEAL-1；worktree G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1；base 958fa8a5b137f2b99ec74ba5902760e1d8aaebdc；复核前用 git rev-parse HEAD 固定实际 head。
- 允许修改路径：Reviewer 独立 worktree 内只新增 verification/EXPORT-REVEAL-1/review-r2.md；生产实现保持只读。Codex 后续只能按 review disposition 与现有 Task 允许范围处理。
- 禁止范围与新增授权条件：不改 doc/STATUS.md / doc/REBASELINE_PLAN.md、doc/tasks/EVENTS-FWD-1.md、§5.8 语义或拒绝面；不把路径交给 WebView；不 push、不合并到 main；不触碰用户 dirty/untracked 或 P04 diagnostic 文件；不得把 AC4-③ 的 BLOCKED 改为 PASS。
- 交付物：绑定实际 review head 的逐 AC Review、findings 与复核结论；Coordinator 再决定是否允许集成。
- 验证命令、环境与完成 Gate：核对三份 post-merge-*.log 的命令、shell/env 和 exit；确认事件四项与并发 round-trip 用例、reveal production-only/拒绝面仍通过；若重新运行，沿用本 Handoff 中三条命令和环境，并逐条归档结果。真实 GUI Reveal 仍单独记录为 BLOCKED，直到在可启动 GUI 环境实际验证。
- 可直接转发给 Reviewer 的指令：

  > 请独立复核 EXPORT-REVEAL-1 合并后交付。仓库 G:/CODEX/New Manga，branch codex/EXPORT-REVEAL-1，worktree G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1，原始 base 958fa8a5b137f2b99ec74ba5902760e1d8aaebdc；请先在 worktree 执行 git rev-parse HEAD 并将实际 HEAD 固定为 reviewed_head。只读核验 library_bridge.rs 的后台读线程与按 request ID 解复用、session export ID 校验和 GetExportHistory 经 exchange 的路径；核验 main.rs 的 .manage(state)、event sink 与 reveal command；核验两组 capabilities 权限及契约 §5.8 拒绝面/路径保密/单次消费语义。对照 verification/EXPORT-REVEAL-1/merge-resolution.md 和三条 post-merge-*.log。不得改 EVENTS-FWD-1 closeout、STATUS/Plan、用户 dirty/untracked 或把 GUI BLOCKED 记为通过。只在独立 review worktree 写 verification/EXPORT-REVEAL-1/review-r2.md；Coordinator 复核后再决定集成。

## 风险与遗留

- 真实成功导出后的 GUI Reveal 仍未验证；AC4-③ 继续 BLOCKED。
- 需要新 head 的独立 Review 和 Coordinator 集成确认；本 Handoff 不表示该交付已接受。
- rustfmt --check 检查未通过，报告了合并文件及其他 Rust 文件中的格式差异；未进行全文件格式化，以免扩展本次范围。合并引入的上游 EVENTS-FWD-1 原始日志还被 git diff --cached --check 报告有 EOF 空行，本次未修改已 closeout 的 EVENTS-FWD-1 证据。
- 验证期间出现的 P04 未跟踪 diagnostic 文件来源未确认，保留且未提交。
- 无数据迁移；如需回退合并提交，可在 Coordinator 裁决后回退 b1e4d87d4 及其后的任务分支文档提交；不得在当前待复核分支上自行 reset。
