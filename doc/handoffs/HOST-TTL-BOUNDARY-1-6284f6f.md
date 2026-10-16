---
task_id: HOST-TTL-BOUNDARY-1
author: Codex
recipient: Coordinator / independent Reviewer
base_commit: 45b3c3a4ba497955daa41b90dc4fe5bb38eb9308
delivery_head: 6284f6f322fa4e990037d56a7cd480d219c0febb
status: in_review
---

# Handoff：HOST-TTL-BOUNDARY-1

## 交付结果

**delivery head:** `6284f6f322fa4e990037d56a7cd480d219c0febb`（实现与测试提交）

- **AC1：PASS，裁决 (b)。** M2-C1 §5.7 L456/L476 将有效期上限和拒绝语义交给 §10.3/§10.4；§10.4 L826 对导入引用规定的是默认 300 秒和活动消费期间滑动续期，没有规定 host 必须签发恰好 300 秒或把它作为精确 host 签发上限。HOST-ISSUER-1-C1 rev 2.3（契约 L3/L17/L23；coverage matrix L14/L22–23）不改既有 P12 import wire、ref 与 `REF_*` 语义。故 host 由 +300 改为 +299 秒，Core 既有 `<= now` 过期与 `> now + 300` 超窗拒绝不变。改码前裁决记录：[ac1-contract-ruling.md](../../verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md)。
- **AC2：PASS。** 只改 import issuer 的有效期数值；未改 Core 守卫、来源 scope、只读限制、`ImportPages`、session 绑定或签名校验。
- **AC3：PASS。** Python 注入时钟的五个回归用例覆盖窗口内成功、Core 时钟等于 host 构建时刻成功、略早成功、真过期拒绝、真超 300 秒窗口拒绝。Rust 断言 host issuer 实际取值为 +299 秒并留有 1 秒裕量。
- **AC4：PASS（控制链路到达 `ImportPages`）。** 用 Rust `StdioLibraryChannel` 和协议 2.3 frozen Core 实跑 `OpenHostSession` → host 签发 → `RegisterImportSource` → `ImportPages`。注册成功，随后 Core 对测试中不存在的 Chapter 返回 `TARGET_NOT_FOUND`。它证明请求已越过原注册拒绝点并到达 `ImportPages`；该探测没有提交 Page。
- **AC5：PASS。** 没有改契约、Schema、依赖、AD-001、STATUS/Plan、wire 或其他产品行为。
- **AC6：PASS。** `tests/core/**` 为 400 passed（有 1 条既有 Pillow 弃用警告）；Rust 非-packaged 测试 76 passed、1 ignored，frozen packaged 测试 7 passed。Rust 两组因 `M2RC1_PYTHON` 环境要求互斥而分开运行，覆盖全部 84 项，其中 83 passed、1 ignored。
- **AC7：交付固定，Review 未完成。** Task、Canonical Evidence 和本 Handoff 已记录；Task 保持 `in_review`，未标为 accepted 或 done。

改动文件：

- `apps/desktop/src-tauri/src/host_issuer.rs`
- `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs`
- `tests/core/test_p09_fu2_import_pages.py`
- `doc/tasks/HOST-TTL-BOUNDARY-1.md`
- `verification/HOST-TTL-BOUNDARY-1/**`
- 本 Handoff

实现提交之后的测试和 Task/Handoff 记录提交只增加文档与原始证据，不改变已测试的源代码或测试代码。没有 push、merge、reset 或 stash。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | 对读契约 §5.7、§10.4 与 C1 rev 2.3 | 只读；改码前冻结裁决 | PASS；分类 (b)，host 留 1 秒裕量 | [契约裁决](../../verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md) |
| AC2 | 审查实现 diff 与已有 Core 校验 | `6284f6f` | PASS；只改 host import expiry 数值；Core `<= now` / `> now + 300` 均未改 | `git diff 45b3c3a4b..6284f6f` |
| AC3 Python | `python -m pytest tests/core/test_p09_fu2_import_pages.py -k ttl_boundary -vv` | Python 3.14.6、pytest 9.1.1；`6284f6f` | PASS；五个 case 5/5 | [Python 定向日志](../../verification/HOST-TTL-BOUNDARY-1/ac3-python-ttl-boundary-6284f6f.log)，EXIT 0 |
| AC3 Rust | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop import_grant_ref_has_only_frozen_fields_and_directory_is_direct_only` | Rust 1.98.1；`6284f6f` | PASS；1/1 | [Rust 定向日志](../../verification/HOST-TTL-BOUNDARY-1/ac3-rust-ttl-boundary-6284f6f.log)，EXIT 0 |
| AC4 / AC6 packaged | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop packaged_sidecar_tests -- --test-threads=1 --nocapture` | Windows；`M2RC1_PACKAGED=1`；`M2RC1_SRC_ROOT` / `M2RC1_PYTHON` unset；`6284f6f` | PASS；7/7。frozen `core_service.exe` SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`；host import test记录 `register=accepted`、`import_error=TARGET_NOT_FOUND` | [packaged 日志](../../verification/HOST-TTL-BOUNDARY-1/ac4-ac6-packaged-rust-6284f6f.log)，EXIT 0 |
| AC6 Core | `python -m pytest tests/core -q` | Python 3.14.6；`6284f6f` | PASS；400 passed，1 条既有 Pillow deprecation warning | [Core 全量日志](../../verification/HOST-TTL-BOUNDARY-1/ac6-tests-core-6284f6f.log)，EXIT 0 |
| AC6 Rust（非-packaged） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop -- --skip packaged_sidecar_tests --test-threads=1` | `M2RC1_PYTHON=C:\Python314\python.exe`；packaged env unset；`6284f6f` | PASS；76 passed、1 ignored | [Rust 非-packaged 日志](../../verification/HOST-TTL-BOUNDARY-1/ac6-rust-source-6284f6f.log)，EXIT 0；[并发 diagnostic](../../verification/HOST-TTL-BOUNDARY-1/ac6-rust-concurrency-diagnostic-6284f6f.jsonl) |
| AC5 | `git diff --name-only 45b3c3a4b..6284f6f` | 固定实现提交 | PASS；所有实现路径均在 Task 允许范围 | Task 本文及提交 diff |
| AC7 | 固定提交与 Handoff | `6284f6f`；本 Handoff commit 随后追加 | PASS；delivery head 固定；等待独立 Review | 本 Handoff 与 Canonical Evidence 表 |

**重试记录（不计入通过数）：**首次 Rust 编译尝试因 worktree 缺少 Tauri 的 `frontend/dist` 且测试代码用了要求 `ImportSummary: Debug` 的 `unwrap_err()` 而失败；修正测试并使用临时 ignored `dist/index.html` 后通过，临时文件已删除。首次 AC4 probe 漏了显式 `OpenHostSession`，在 host 侧返回 `HOST_SESSION_INVALID`，请求没有到 Core；补上握手后通过。首次合并运行全部 Rust 测试时没有设置 `M2RC1_PYTHON`，故并发测试 setup 失败；按两套必要环境拆分后，非-packaged 76/76 与 packaged 7/7 全部通过。原始尝试分别保存在 `ac3-rust-ttl-boundary-build-attempt-1.log`、`ac4-frozen-host-importpages.log`、`ac6-rust-tests.log`。

**签名精度：**没有改变签名规范化格式。Rust 仍使用 `format!("{expires_at:.6}")`，Core 仍使用 `f"{expires_at:.6f}"`。frozen Core 的实际 grant 注册成功且返回后续 `ImportPages` typed response，证明新 expiry 值的签名重算通过。

**对照 ENV-BUNDLE-1-FU1 AC3：**此前冻结 Core 在 `RegisterImportSource` 返回 `REF_EXPIRED`，因此 ImportPages 没有执行；本次同一 SHA-256 的 2.3 frozen executable 接受注册并返回 `TARGET_NOT_FOUND`，这是 `ImportPages` 的下游响应。差异与 host 留出的 1 秒裕量一致。原始对照：[ENV-BUNDLE-1-FU1 AC3](../../verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md)。

Cargo 生成的 27 个 schema/permission 状态变化经 `git diff` 确认无实际内容差异后逐项恢复。并发 Rust 测试在 `verification/P04/` 生成的诊断日志已逐字节复制至本 Task evidence 后移除原文件；未留下越界修改。

## 接收方式

- Branch：`codex/HOST-TTL-BOUNDARY-1-grant-ttl`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`
- Base：`45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`
- Reviewed candidate / delivery head：`6284f6f322fa4e990037d56a7cd480d219c0febb`
- 当前 HEAD：包含 delivery head 及后续 Task/Handoff 证据记录；未改动产品源码。
- 下一接收者应独立核对 Task diff、签名保持一致、AC3 四类（含 host 时钟相等/略早）拒绝和通过面，以及 AC4 真实 packaged 日志。没有引入依赖或数据迁移。

## 下一任务建议

- Task ID / 标题：`HOST-TTL-BOUNDARY-1` 独立 Review（固定 reviewed_head `6284f6f322fa4e990037d56a7cd480d219c0febb`）
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者）；由 Coordinator 确认分派。Codex 是本 Task Owner，不执行自己的批准。
- 推荐原因与前置依赖：实现和完整测试已固定；Owner 与 Reviewer 必须不同。P12 导入 UI 依赖这条路径，Review 应在 P12 验收前完成。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/HOST-TTL-BOUNDARY-1-grant-ttl`；worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`；base `45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`；reviewed head `6284f6f322fa4e990037d56a7cd480d219c0febb`。
- 允许修改路径：仅 `verification/HOST-TTL-BOUNDARY-1/**` 中新增 Review 报告。
- 禁止范围与新增授权条件：不改 Rust/Python 实现、Task、契约、Schema、依赖、`STATUS` / Plan；发现 finding 时报告给 Codex，由新授权修复 Task 处理。
- 交付物：按 `doc/templates/REVIEW.md` 写固定 base/head 的非作者 Review，覆盖完整 diff、相关调用链和测试日志，列出 Findings、风险与 `approved` / `changes_requested` 结论。
- 验证命令、环境与完成 Gate：复核本 Handoff 表中三组测试命令；Rust source 与 packaged 必须分别设置/清除 `M2RC1_PYTHON`，不能跳过 packaged 组。无未解决 P0/P1、关键路径证据可复核后，由 Codex adjudicate 并集成；在此之前 Task 不进入 `done`。
- 可直接转发给 Agent 的指令：

> 请对 `HOST-TTL-BOUNDARY-1` 做非作者 exact-head Review。仓库为 `G:/CODEX/New Manga`，worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1`，branch `codex/HOST-TTL-BOUNDARY-1-grant-ttl`，base `45b3c3a4ba497955daa41b90dc4fe5bb38eb9308`，reviewed_head 固定为 `6284f6f322fa4e990037d56a7cd480d219c0febb`。只允许在 `verification/HOST-TTL-BOUNDARY-1/**` 写 Review 报告；不要修改实现、Task、契约、Schema、依赖、STATUS 或 Plan。完整审查 diff 与调用链，核对 AC1 的 §5.7/§10.4 与 HOST-ISSUER-1-C1 rev 2.3 裁决，确认 Rust/Python `.6`/`.6f` 签名一致、Core 上下界拒绝仍在、AC3 四类边界均有断言，以及 AC4 frozen 2.3 bundle 日志。复核 Handoff 中 Python Core 与分环境 Rust 命令；记录真实退出码、未运行项和 findings。结论按 Review 模板写为 `approved` 或 `changes_requested`；Codex Owner 将在 Review 后做 adjudication 和 integration，之前不要标 Task `done`。

## 风险与遗留

- AC4 真实 HostControl/ImportPages 往返用不存在的 Chapter 验证注册边界，因此其成功结果是 `TARGET_NOT_FOUND`；它没有导入实际页面。真实页面写入另由 `tests/core/**` 的既有成功路径覆盖，非本次 packaged 探测覆盖。
- 300 秒合同语义是默认值；host 实际签发 299 秒，最大有效期比默认少 1 秒，以避开 Core 的精确 300 秒硬上界。Core 拒绝语义与安全检查未放宽。
- 一项既有 Rust perf 测试保持 ignored；Python 测试有一条既有 Pillow 弃用警告。
- Reviewer 尚未由 Coordinator 指定，Review、adjudication 和 integration 未完成。当前 Task 为 `in_review`，本交付**未被接受**。
- 按 Task 硬性禁止，本次没有修改 `doc/STATUS.md` 或 `doc/REBASELINE_PLAN.md`；下一步需由 Coordinator 按项目流程同步集成状态。
