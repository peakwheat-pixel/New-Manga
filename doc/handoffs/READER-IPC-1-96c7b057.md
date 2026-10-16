---
task_id: READER-IPC-1
author: Codex
recipient: dsh
base_commit: f7d9da6b3102dc4fcde2a1d6823b14d54feaa0a8
delivery_head: 96c7b057672589892458a3d1e78c91031f8f03e6
status: in_review
---

# Handoff：READER-IPC-1

## 交付结果

实现提交：`96c7b057672589892458a3d1e78c91031f8f03e6`（`feat(reader): expose reader IPC commands`）。任务文档和本 Handoff 在后续文档提交中更新；`delivery_head` 仍指实现提交，避免 BL-15 自引用。

新增 production-only Tauri 命令：

- `library_get_reader_projection` → Core wire `GetReaderProjection`
- `library_save_reading_progress` → Core wire `SaveReadingProgress`

同步了生产 allowlist、生产 handler、`build.rs` manifest、capability、自动生成权限及生成 ACL schema。生产命令数为 27；probe=7、AC1=6 保持不变。Core/契约未修改，`resolve_page_resource` 未改动。

### Acceptance Criteria

| AC | 状态 | 证据与限制 |
|---|---|---|
| AC1 命令名与 §5 形状冻结 | PASS | Task 的 AC1 表冻结两命令、参数及 PascalCase Core wire；没有增加 wire 或字段。 |
| AC2 production host 接线与权限同步 | PASS | 实现提交中同步 handler、allowlist、manifest、capability 与生成权限；两命令只进入生产面。 |
| AC3 §6.3 语义 | PASS（Core/host 传输约束） | Core 隔离测试覆盖资源引用不透明且无路径、缺失译图为 null、`beginning` 保留 `saved_progress`、original/translated 进度独立、Webtoon `scroll_offset_y` 使用逻辑页原图像素坐标。Rust payload 单测确认缺失 `elapsed_seconds_delta` 不会重发。Host 原样透传投影，不处理资源引用。 |
| AC4-① allowlist | PASS | Rust 测试钉住两命令只在生产面，probe/AC1 无，数量 27/7/6。 |
| AC4-② typed 拒绝 | PASS | frozen/Core 隔离测试覆盖未知 chapter → `TARGET_NOT_FOUND`、非法 mode → `INVALID_REQUEST`；存在 chapter + 未知 page → `TARGET_NOT_FOUND`，且 DB `total_changes`、进度快照不变、无事件。 |
| AC4-③ frozen protocol 2.3 往返 | PASS（域级可达） | packaged 测试中两条 wire 均返回域级错误而非 `PROTOCOL_MALFORMED`。投影用不存在 chapter；保存请求同时传不存在 chapter 和 page，Core 先拒绝 chapter，因此该 frozen 用例不验证 page 专项拒绝。 |
| AC4-④/AC5 日志与回归 | PASS | Core 407 passed；Rust source 89 passed / 1 ignored；frozen packaged sidecar 11 passed；均退出码 0。 |
| AC6 固定交接 | PASS，等待 DSH Review | 本文、Task 状态及 Canonical Evidence 已登记；尚未由 DSH 接受。 |

## 验证证据

所有日志都记录原始输出和 `EXIT=0`。SHA-256 按工作树中的磁盘字节计算。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4-①/AC5 Rust source | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests` | PowerShell 7.6.6；Rust 1.98.1；实现树父提交 `f7d9da6b...` | 89 passed / 0 failed / 1 ignored；EXIT=0 | `verification/READER-IPC-1/rust-source-tests.log` |
| AC4-③/AC5 targeted packaged Reader | `M2RC1_PACKAGED=1 cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::reader_commands_reach_frozen_core_with_typed_rejections -- --nocapture` | 使用既有 packaged bundle/junction；isolated `PackagedLab` 数据目录；协议 2.3 | 1 passed；EXIT=0 | `verification/READER-IPC-1/rust-packaged-reader-test.log` |
| AC4-③/AC5 full frozen suite | `$env:M2RC1_PACKAGED='1'`；unset `M2RC1_SRC_ROOT`、`M2RC1_PYTHON`；`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | Windows；既有 junction；冻结 sidecar SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`；isolated data dirs | 11 passed / 0 failed / 0 ignored；EXIT=0 | `verification/READER-IPC-1/rust-packaged-sidecar-tests.log` |
| AC3/AC4-②/AC5 Core | `C:\Python314\python.exe -m pytest tests/core -q -p no:cacheprovider` | Python 3.14.6；所有 Reader Core fixtures 使用 pytest `tmp_path` | 407 passed；1 个 Pillow deprecation warning；EXIT=0 | `verification/READER-IPC-1/core-pytest.log` |

### Canonical Evidence（磁盘字节 SHA-256）

| path | commit | sha256 | class |
|---|---|---|---|
| `verification/READER-IPC-1/rust-source-tests.log` | `96c7b057672589892458a3d1e78c91031f8f03e6` | `b5242e800eb7b0f9a7a0ba2a5bdbe7c36a2f2aa9de784706f3291a5a0657274d` | CANONICAL |
| `verification/READER-IPC-1/rust-packaged-reader-test.log` | `96c7b057672589892458a3d1e78c91031f8f03e6` | `bb1eb8b4f59d64ac51b1bdd327f9ecd10220f0753328641682f97a165e35743a` | CANONICAL |
| `verification/READER-IPC-1/rust-packaged-sidecar-tests.log` | `96c7b057672589892458a3d1e78c91031f8f03e6` | `a5170cf83e8dbbb2b1a03d275e1d6f0e3967145a3aab66978ff246552b10d108` | CANONICAL |
| `verification/READER-IPC-1/core-pytest.log` | `96c7b057672589892458a3d1e78c91031f8f03e6` | `1cb15e787efc9bf37df4ef7ac267a8f6855be058a52edfe30be5d25902fa27fa` | CANONICAL |

## 接收方式

- 分支：`codex/READER-IPC-1`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1`
- Base：`f7d9da6b3102dc4fcde2a1d6823b14d54feaa0a8`
- 实现提交：`96c7b057672589892458a3d1e78c91031f8f03e6`
- packaged 复核命令需设置 `M2RC1_PACKAGED=1` 并 unset `M2RC1_SRC_ROOT`、`M2RC1_PYTHON`；测试使用隔离数据目录。未运行 `build_sidecar.ps1`，复用现有 junction。
- `SaveReadingProgress` 是写操作。本 Task 新增的 packaged/Core 拒绝用例只验证拒绝路径；已有 Core 进度语义测试中的成功保存仅写入 pytest `tmp_path` 隔离目录。

## 下一任务建议（必填）

- Task ID / 标题：`READER-IPC-1` / DSH 独立 Review
- 推荐 Agent / Reviewer：DSH
- 推荐原因与前置依赖：实现与证据已固定，项目指定 DSH 做独立 Review；不得把内部 pre-commit 复核当成 DSH 接受。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/READER-IPC-1`；worktree `G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1`；base `f7d9da6b3102dc4fcde2a1d6823b14d54feaa0a8`；implementation head `96c7b057672589892458a3d1e78c91031f8f03e6`；Review 时 branch HEAD 包含后续 Task/Handoff 文档提交。
- 允许修改路径：只读审查；若要写 Review 记录，仅使用项目规定的 Review 证据路径并保留现有 dirty 文件。
- 禁止范围与新增授权条件：不得修改实现、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、用户 19 项 dirty 内容、`verification/P04/diagnostic_*.jsonl`；不 push、不 merge。需要代码修订时先回交 Codex 分配新范围。
- 交付物：独立 Review 结论、发现及测试/证据核对结果；明确是否通过 Review gate。
- 验证命令、环境与完成 Gate：核对本 Handoff 的四份 Canonical Evidence 及磁盘 SHA-256；必要时按上表原命令复跑。只有 DSH Review 与 Codex 集成验证完成后才可关闭 Task。
- 可直接转发给 Agent 的指令：请基于 base `f7d9da6b3102dc4fcde2a1d6823b14d54feaa0a8`、实现提交 `96c7b057672589892458a3d1e78c91031f8f03e6` 及当前 branch HEAD，对 READER-IPC-1 做独立只读 Review。核查两条命令、生产/冻结 allowlist、typed 错误、数据隔离及 §6.3 语义；确认 packaged Save 用例由缺失 chapter 先拒绝、成功 host/frozen 投影和进度保存未验证。引用真实文件/测试/证据，报告 findings 与结论；不修改代码、不 push、不 merge，不要将本次交付标为已接受。

## 风险与遗留

- **Tauri host/frozen packaged 上的成功投影和成功进度保存未验证**。Core 层已有的成功语义测试在 pytest 临时数据目录内运行；它们不能证明 frozen host 的成功响应形状。
- packaged Save 的拒绝请求包含未知 chapter 与未知 page，Core 先因 chapter 返回 `TARGET_NOT_FOUND`；已存在 chapter + unknown page 的 page 专项拒绝及无副作用由 Core 隔离测试证明，尚无 frozen page 专项覆盖。
- 治理检查器未在该工作树中提供，未运行；没有伪造其结果。未运行 GUI。
- 独立 Review 尚待 DSH；本 Handoff 不表示已接受。未 push、未 merge。
- 回退方法：由 Codex 在分支上按该实现提交审查后再决定 revert；不要覆盖或清理本工作树中的其他 dirty/untracked 内容。
