---
id: RUST-ENV-BASELINE-1
title: Rust 完整套件环境基线修复（12 项 M2RC1_PYTHON 环境依赖失败）
kind: fix
governance_version: 2
status: proposed
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
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RUST-ENV-BASELINE-1
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
