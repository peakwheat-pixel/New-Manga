---
task_id: HOST-TTL-BOUNDARY-1
author: Codex
recipient: DSH / Coordinator
base_commit: 45b3c3a4ba497955daa41b90dc4fe5bb38eb9308
delivery_head: 7fbce30180da18450b07e9951e6cef32cab68b5a
status: in_review
---

# Handoff：HOST-TTL-BOUNDARY-1 export TTL bounded repair

## 交付结果

DSH R1 的唯一 finding I1 是 `build_export_grant` 仍签发 `unix_seconds() + 300.0`，而 Core `target_refs.py:127` 允许上限为 `now + 300`，形成与 import 相同的零裕量。修复遵循 AC1 同一契约裁决：export host TTL 改为 `+299.0`；Core 守卫、导出授权 scope、session 绑定、替换权限、单次消费和过期/撤销/签名校验都保持不变。

DSH R1 原文只读来源：`G:/CODEX/New Manga/verification/HOST-TTL-BOUNDARY-1/dsh-review-r1.md`。该文件位于共享主仓，不复制进本 worktree。

M2-C1 §10.3 L814 规定 export ref 默认 300 秒、不滑动续期且单次有效调用后消费；§5.7 L456/L476 将上限和拒绝规则交回 §10.3/§10.4，没有要求 host 必须签发恰好 300 秒。导入侧裁决及对称说明见 [AC1 契约裁决](../../verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md)。

改动路径：

- `apps/desktop/src-tauri/src/host_issuer.rs`
- `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs`
- `tests/core/test_p16_reader_export.py`
- 本 Task、Canonical Evidence、AC1 ruling 与本 Handoff

实现与测试固定于 `7fbce3018`；其中 `4662239b4` 改 export TTL 并加入边界测试，`7fbce3018` 修正 packaged probe 使用的既有 StartExport DTO 字段。没有修改 `src/infrastructure/export/target_refs.py` 或任何契约、Schema、依赖、STATUS、Plan。

## Acceptance Criteria 状态

| AC | 状态 | 结果 |
|---|---|---|
| AC1 | PASS | §10.3 / §10.4 的 300 秒默认值均未规定必须恰好签发 300 秒；两侧 host 均留 1 秒裕量。 |
| AC2 | PASS | Import 与 Export host 均为 +299 秒；所有 Core guard 和安全语义保持。 |
| AC3 | PASS | import/export 各 5 个 Python 注入时钟边界均通过；Rust export issuer 断言 TTL 为 299 秒。 |
| AC4 | PASS | frozen 2.3 Core 接受 `RegisterExportTarget`；下游 `StartExport` 返回预期 `TARGET_NOT_FOUND`，目标未写。Import 既有链路也通过。 |
| AC5 | PASS | 无契约、Schema、依赖、wire、STATUS / Plan 或无关产品行为变更。 |
| AC6 | PASS | Python Core 405 passed；Rust non-packaged 76 passed / 1 ignored；frozen packaged 8 passed。 |
| AC7 | 交付固定，Review 待复审 | implementation/test commit 固定；DSH exact-head re-review 尚未完成，Task 仍 `in_review`。 |

## 验证证据

| 场景 | 实际命令/步骤 | 被测代码 | 结果与证据 |
|---|---|---|---|
| Export AC3 Python | `python -m pytest tests/core/test_p16_reader_export.py -k ttl_boundary -vv` | `4662239b4`；Python 3.14.6 / pytest 9.1.1 | PASS 5/5；见 [focused log](../../verification/HOST-TTL-BOUNDARY-1/ac3-export-python-ttl-boundary-4662239.log)，EXIT 0。 |
| Export AC3 Rust | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop export_ref_is_one_target_token_with_frozen_prefix` | `4662239b4`；Rust 1.98.1 | PASS 1/1；见 [focused log](../../verification/HOST-TTL-BOUNDARY-1/ac3-rust-export-ttl-boundary-4662239.log)，EXIT 0。 |
| Export AC4 packaged | frozen 2.3 Core 上 Rust host `start_export_to_path` → `RegisterExportTarget` → `StartExport` | `7fbce3018`；`M2RC1_PACKAGED=1`；`M2RC1_SRC_ROOT` / `M2RC1_PYTHON` unset；startup timeout 120 s | PASS；`register=accepted`、`export_error=TARGET_NOT_FOUND`、`target_written=false`；`core_service.exe` 68,717,156 bytes，SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`。见 [packaged suite log](../../verification/HOST-TTL-BOUNDARY-1/ac6-export-rust-packaged-7fbce30.log)，8/8，EXIT 0。 |
| Python Core | `python -m pytest tests/core -q` | `7fbce3018`；Python 3.14.6 / pytest 9.1.1 | PASS 405；1 条既有 Pillow deprecation warning；见 [log](../../verification/HOST-TTL-BOUNDARY-1/ac6-export-tests-core-7fbce30.log)，EXIT 0。 |
| Rust non-packaged | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop -- --skip packaged_sidecar_tests --test-threads=1` | `7fbce3018`；`M2RC1_PYTHON=C:\Python314\python.exe`；packaged env unset | PASS 76 / 1 ignored；见 [log](../../verification/HOST-TTL-BOUNDARY-1/ac6-export-rust-nonpackaged-7fbce30.log)，EXIT 0。 |

首次 packaged 尝试把请求写成 `chapter_id` / `page_ids`，被 host DTO 校验正确拒绝为 `INVALID_REQUEST`，未作为通过证据。按生产接口已冻结的 `book_id` / `chapter_ids` / `ordered_page_ids` 修正后成功；原始失败日志保留于 `ac4-export-frozen-rust-attempt1-4662239.log`。

签名精度未变：Rust `format!("{expires_at:.6}")` 与 Core `f"{expires_at:.6f}"` 保持配对。Frozen Core 注册成功并继续到 `StartExport`，证明 export grant 的新 expiry 签名可通过验证。

Cargo 将 27 个生成 Schema/permission 文件显示为状态变化；`git diff --ignore-space-at-eol` 确认为纯行尾噪音后逐文件恢复。并发测试生成的 P04 diagnostic 已逐字节复制到 Task evidence 并清除原临时文件；用于 Cargo 的空 `frontend/dist/index.html` 已删除。

## 接收方式

- Branch：`codex/HOST-TTL-BOUNDARY-1-grant-ttl`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`
- Base：`45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`
- Implementation/test head：`7fbce3018`
- 当前 Task 状态：`in_review`；没有声称 Reviewer 接受或集成完成。

## 下一任务建议

- Task ID / 标题：`HOST-TTL-BOUNDARY-1` DSH exact-head re-review（针对 export I1 的 bounded repair）
- 推荐 Agent / Reviewer：DeepSeek Harness（dsh），非作者
- 推荐原因与前置依赖：实现、边界测试、frozen 2.3 链路与 Canonical Evidence 已固定；等待独立复审。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/HOST-TTL-BOUNDARY-1-grant-ttl`；worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`；base `45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`；implementation/test head `7fbce3018`。
- 允许修改路径：仅 `verification/HOST-TTL-BOUNDARY-1/**` 中新增 Review 报告。
- 禁止范围与新增授权条件：不改实现、Task、契约、Core guard、Schema、依赖、STATUS 或 Plan；发现新 finding 时交 Codex 处理，不自行扩大范围。
- 交付物：按 `doc/templates/REVIEW.md` 复核 base 至固定实现 head 的完整变更、调用链、Core 上下界拒绝、两端 `.6` / `.6f` 签名格式、两侧边界测试、Python/Rust 全套日志与 frozen 2.3 export registration 证据；如需复核最终 Task/Handoff/evidence 文档，使用当前分支 tip。
- 验证命令、环境与完成 Gate：复核本 Handoff 的 Python Core、分环境 Rust non-packaged 与 packaged 命令；报告真实退出码、未运行项及 findings。Review 未完成前保持 `in_review`。
- 可直接转发给 Agent 的指令：

> 请对 `HOST-TTL-BOUNDARY-1` 做非作者 exact-head re-review。仓库为 `G:/CODEX/New Manga`，worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`，branch `codex/HOST-TTL-BOUNDARY-1-grant-ttl`，base=`45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`，实现/测试 head=`7fbce3018`。只允许在 `verification/HOST-TTL-BOUNDARY-1/**` 新增 Review 报告。核对 DSH R1 I1：导出 host +299 秒、Core 守卫未改；按 M2-C1 §10.3 L814 对 default 300 s 的语义说明；签名 `{:.6}` / `{:.6f}` 未变；五项 export 时钟边界、Core 全量 405、Rust non-packaged 76 passed/1 ignored、frozen 2.3 packaged 8/8 及 `RegisterExportTarget` accepted / `StartExport` `TARGET_NOT_FOUND` 原始日志。不要修改实现或声称集成；按 Review 模板给出 exact-head findings 与结论。

## 风险与遗留

- Export probe 用不存在的 Book，故真实链路验证注册和下游拒绝，不声称执行实际文件导出。
- 有一项既有 Rust perf 测试保持 ignored；Python Core 有一条既有 Pillow deprecation warning。
- Task 等待 DSH 对此次 bounded repair 的独立 re-review；尚未 adjudicate / integrate / closeout。
