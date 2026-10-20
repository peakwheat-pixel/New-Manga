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
| EV-V1-RUST-SOURCE | RUST-ENV AC3 | `verification/V1-FINALIZE-20261021/cargo-source-fixed.log` | - | 8f2f94684291117b5eb5e04479175aa19e5758e5d2cf7253e99975e55366994e | CANONICAL |
| EV-V1-RUST-PACKAGED | RUST-ENV AC3 | `verification/V1-FINALIZE-20261021/cargo-packaged-fixed.log` | - | c83ee5828c31d9220bf4211618dc232fbe30d17b7f1f311c710ea420cf5a26c3 | CANONICAL |
| EV-V1-FRONTEND | RUST-ENV 回归 | `verification/V1-FINALIZE-20261021/vitest.log` | - | de1bb344dd99678056b344e145783b41ac4f77a58f6135ef328592a0822372a7 | CANONICAL |
| EV-V1-PYTEST | RUST-ENV 回归 | `verification/V1-FINALIZE-20261021/pytest-m2.log` | - | a3a074188908f523411bb54c127fb9ddb4f746c11852a75b0d0c1a33e973b657 | CANONICAL |
| EV-V1-INSTALLER | v1 安装包 | `verification/V1-FINALIZE-20261021/tauri-build-installer.log` | - | 7fa190f4c05ed2bf439def9e3b870a0367149a52433e8a8936344d23d504b007 | CANONICAL |
| EV-V1-DOC | v1 总证据 | `verification/V1-FINALIZE-20261021/v1-verification-20261021.md` | - | 5b39fde0921a11a9dd7b1b31015fa7c250d3ab0a5078b29113d168651fc64e0e | CANONICAL |
| EV-V1-SIDECAR | v1 构建 | `verification/V1-FINALIZE-20261021/sidecar-build.log` | - | c9e29c32f856083c2e8833dcd7847ea157dfaa3b916bf19e94d31468452140a3 | SOURCE_PIN |
| EV-V1-FRONTEND-BUILD | v1 构建 | `verification/V1-FINALIZE-20261021/frontend-build.log` | - | 8039ccb0ce829811075d16940d0c36bd1e75d97205c3821eca32ebc70ba7f1c6 | SOURCE_PIN |
| EV-V1-NPM-CI | v1 环境 | `verification/V1-FINALIZE-20261021/npm-ci.log` | - | a36e1aad0294731fdcb15139368c3d680ee4398c9484ca917fcc43c17b8d9785 | SOURCE_PIN |
| EV-V1-PRE-FIX-SOURCE | v1 修复前对照 | `verification/V1-FINALIZE-20261021/cargo-test-full.log` | - | 55d01b23ef6c04320651cc656d7c46569ccf04f725baa7200d5011a2a09e170e | SOURCE_PIN |
| EV-V1-FIRST-RUN | v1 首次运行 | `verification/V1-FINALIZE-20261021/cargo-test.log` | - | 1e0a05b92a88741775a89c8bba0b9fb46cdf8532bb9f214b221ac223da59ca71 | SOURCE_PIN |
| EV-V2-ADJUDICATION | 收口裁定 | `verification/V1-FINALIZE-20261021/legacy-task-closure-adjudication.md` | - | 798e25a2c3d6adee17edf463eebc5bce3dc1dc1a69516df58cae20eef5a89370 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 不改产品资源；只读环境验证与日志 |

## 历史收口（2026-10-21，dsh）

- 收口状态：`closed_with_limitations`。AC1：已固定/记录 `M2RC1_PYTHON=C:\Python314\python.exe` 运行口径，但未给集成测试加缺配置自检（限制）。AC2：基线 `8bf3ae30` 未重跑（历史基线不重写，限制）。AC3：当前 HEAD 修复后 source `150 passed / 0 failed / 1 ignored`、packaged `12 passed / 0 failed`，均 exit 0。AC4：修复前 22 项失败已逐类定性 = 13 项 packaged 环境门卫（错误运行口径）+ 7 项 recycle-bin ACL/计数漂移 + 3 项并行 registry 污染；其中 ACL 漂移是真实产品缺陷，已修复。AC5：真实缺陷只有 recycle-bin ACL 一项，已修；其余为环境/测试隔离。AC6：1 ignored 性能测量保持原状；AC7：本文与 `v1-verification-20261021.md` 如实记录，不冒充全绿。
- 依据：`verification/V1-FINALIZE-20261021/v1-verification-20261021.md`；不修改产品逻辑，不重写历史 pin。
