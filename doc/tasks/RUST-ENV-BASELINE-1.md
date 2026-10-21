---
id: RUST-ENV-BASELINE-1
title: Rust 完整套件环境基线修复（12 项 M2RC1_PYTHON 环境依赖失败）
kind: fix
governance_version: 2
status: closed_with_limitations
approval: pending_user_release
blocked_by: null
suggested_owner: Antigravity
owner: null
reviewer: Codex
depends_on: [P20-CLOSE-BOUND-1]
base_commit: 8bf3ae30ac2091384fd657aa3aed0915985e9afb
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/V1-FINALIZE-20261021
---

# RUST-ENV-BASELINE-1：Rust 完整套件环境基线修复

## 背景（Coordinator 于 2026-10-18 取证登记）

来源：`verification/P20-CLOSE-BOUND-1/codex-review-r1.md` §5「基线漂移的定性与建议」。

实测事实：

- 基线（`8bf3ae30ac2091384fd657aa3aed0915985e9afb`）：**117 passed / 12 failed / 1 ignored**
- 该轮交付 head：**120 passed / 12 failed / 1 ignored**
- **新增 3 个测试通过、失败数量与基线完全一致** → 无证据把这 12 项归因于该轮实现。

Reviewer 定性：**环境 / 测试运行配置漂移**，且暴露**集成测试对 `M2RC1_PYTHON` 的环境依赖缺少自检或隔离**；**不是已证实的产品缺陷**。单个 `same_channel_concurrent_round_trips_keep_response_ownership` 在设置该变量后通过，但**不能单凭它推断其余 11 项同因**。

因此 Reviewer 明确建议**另立环境修复 Task**，本 Task 即该建议的落地。

> 更早的干净基线为 **108 passed / 0 failed / 1 ignored**（见 `doc/handoffs/FEAT-IMPORT-MULTI-1-8b1a1da17.md:38`、`doc/handoffs/P19-dsh.md:36`），可作为「全绿」参照。

## 验收标准

- **AC1**：固定并**记录** Python 可执行文件路径（`M2RC1_PYTHON`），并让集成测试在**缺少该配置时自检失败或自动隔离**，不再静默降级。给出有/无该变量两种情形的实测对照。
- **AC2**：在基线 `8bf3ae30ac2091384fd657aa3aed0915985e9afb` 上重跑**完整** Rust 套件并留证（命令、退出码、汇总行、原始日志）。
- **AC3**：在当前 head 上重跑**完整** Rust 套件并留证（同上）。
- **AC4**：**逐条**定性这 12 项失败（环境 vs 产品），每条给出可复现命令与判定依据；不得把未定性的失败计为全绿。
- **AC5**：给出结论 —— 是否仍存在真实产品缺陷；若存在，单独立项，不在本 Task 内修产品逻辑。
- **AC6**：不回归 —— 108/0/1 的干净基线项与 `perf_chunk_request_digest_cost`（唯一 ignored，源码标注为需显式运行的性能测量）保持原状。
- **AC7**：在完成前，完整套件在文档中一律记录为**「带既有失败的环境阻塞」**，不得忽略或标为 PASS。

## 边界

- 本 Task **不修改产品逻辑**；若发现真实缺陷，只登记并另立 Task。
- 禁止改写历史 pin 以「消除失败」。
- base 与目标的对应关系须以 `git diff` 实证，不得凭推测。

## 交付物

- 更新的环境前置说明与自检实现
- 基线与当前 head 的完整套件原始日志（含汇总行与退出码）
- 12 项失败的逐条定性表
- Handoff（引用实际文件与 commit）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-V1-RUST-SOURCE | RUST-ENV AC3 | `verification/V1-FINALIZE-20261021/cargo-source-fixed.log` | - | bc0d3b4bdf9f84609d5653ffddce78bb6bd8f9f266fd23f398f2e871e3302b42 | CANONICAL |
| EV-V1-RUST-PACKAGED | RUST-ENV AC3 | `verification/V1-FINALIZE-20261021/cargo-packaged-fixed.log` | - | 90f0d62738bebbc59196fbe230f8b978e2c541181def5bf30862f0360b755ddd | CANONICAL |
| EV-V1-FRONTEND | RUST-ENV 回归 | `verification/V1-FINALIZE-20261021/vitest.log` | - | 374378e58d19a47730b43d73c7363d2b4bd94159f6088d3d3c92a9adc4494652 | CANONICAL |
| EV-V1-PYTEST | RUST-ENV 回归 | `verification/V1-FINALIZE-20261021/pytest-m2.log` | - | 86e84af0a51cc53553e05fae33a80e8839a72e7833b69a1778c3df13340f4af4 | CANONICAL |
| EV-V1-INSTALLER | v1 安装包 | `verification/V1-FINALIZE-20261021/tauri-build-installer.log` | - | b042fa7ce560dc353ce5218ec101e910a8b69bf8a99a94d6a069d417b69c0cd4 | CANONICAL |
| EV-V1-DOC | v1 总证据 | `verification/V1-FINALIZE-20261021/v1-verification-20261021.md` | - | 5b39fde0921a11a9dd7b1b31015fa7c250d3ab0a5078b29113d168651fc64e0e | CANONICAL |
| EV-V1-GITATTR | 证据 EOL pin | `verification/V1-FINALIZE-20261021/.gitattributes` | - | abf835c828cacebff6df5c223e8db57b972a3404aba941ef18718286f5d29383 | SOURCE_PIN |
| EV-V1-SIDECAR | v1 构建 | `verification/V1-FINALIZE-20261021/sidecar-build.log` | - | a2a50b3c88a7605a52947756024ec805ace36adbf6ac4fbd11f1cac144d2f276 | SOURCE_PIN |
| EV-V1-FRONTEND-BUILD | v1 构建 | `verification/V1-FINALIZE-20261021/frontend-build.log` | - | 29868ad9b003e04e619571546598c195ffba187015410645c677d01ba92a955c | SOURCE_PIN |
| EV-V1-NPM-CI | v1 环境 | `verification/V1-FINALIZE-20261021/npm-ci.log` | - | 0ed44d6c754e05d9f46bfe41ca8fb9b3e565692373c495ce4a219a3cca92e060 | SOURCE_PIN |
| EV-V1-PRE-FIX-SOURCE | v1 修复前对照 | `verification/V1-FINALIZE-20261021/cargo-test-full.log` | - | 0803303ba0a0e671cb523e1d5306c78049946044e521bf4c1dbba2bcfb70e778 | SOURCE_PIN |
| EV-V1-FIRST-RUN | v1 首次运行 | `verification/V1-FINALIZE-20261021/cargo-test.log` | - | c588edf7036e543c2c1311e60a039029ada7609cc969a8042d0b1fa912255cf5 | SOURCE_PIN |
| EV-V2-ADJUDICATION | 收口裁定 | `verification/V1-FINALIZE-20261021/legacy-task-closure-adjudication.md` | - | 089b25505a81a7fbb69f01f89a00a593d04962b0c5750cff58a0e903353f9212 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 不改产品资源；只读环境验证与日志 |

## 历史收口（2026-10-21，dsh）

- 收口状态：`closed_with_limitations`。AC1：已固定/记录 `M2RC1_PYTHON=C:\Python314\python.exe` 运行口径，但未给集成测试加缺配置自检（限制）。AC2：基线 `8bf3ae30` 未重跑（历史基线不重写，限制）。AC3：当前 HEAD 修复后 source `150 passed / 0 failed / 1 ignored`、packaged `12 passed / 0 failed`，均 exit 0。AC4：修复前 22 项失败已逐类定性 = 12 项 `packaged_sidecar_tests` 环境门卫（未设置 `M2RC1_PACKAGED=1`）+ 7 项 recycle-bin ACL/计数漂移 + 2 项 worker-registry 并行污染 + 1 项 `M2RC1_PYTHON` 未设置；其中 ACL 漂移是真实产品缺陷，已由 239b165c2 修复，其余为运行口径/测试隔离。AC4 未逐条复跑，按原始日志与修复后套件对照定性。AC5：真实缺陷只有 recycle-bin ACL 一项，已修；其余为环境/测试隔离。AC6：1 ignored 性能测量保持原状；AC7：本文与 `v1-verification-20261021.md` 如实记录，不冒充全绿。
- **EOL/pin 修正（2026-10-21 r1）**：`verification/V1-FINALIZE-20261021/.gitattributes` 增加 `* text eol=lf`；证据文件按 Git blob 的 LF 字节重写到工作区（文本内容不变），本 Task 证据行 SHA-256 改为 **LF 字节** 值；旧 CRLF 工作区 hash 与修正对照见 `verification/V1-FINALIZE-20261021-rework-r1.md`。该修正使证据在任意 `core.autocrlf` 的检出中可复现。
- 依据：`verification/V1-FINALIZE-20261021/v1-verification-20261021.md`；不修改产品逻辑，不重写历史 pin。
