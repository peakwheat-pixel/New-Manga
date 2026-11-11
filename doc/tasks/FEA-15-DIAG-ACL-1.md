---
id: FEA-15-DIAG-ACL-1
title: FEA-15 测试失败与资源影响只读诊断
kind: diagnosis
governance_version: 3
status: in_review
approval: ZCode 2026-11-11 冻结并释放；依赖 FEA-15-ACCEPT-1 带限制终态
suggested_owner: codex
owner: codex
reviewer: Codex Reviewer subagent `/root/fea15_diag_acl_review`（独立上下文）
depends_on:
  - FEA-15-ACCEPT-1
base_commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: daeb6dcccbf970facd2272c00645255ae6bdfb87
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-15-DIAG-ACL-1
allowed_paths:
  - doc/tasks/FEA-15-DIAG-ACL-1.md
  - doc/reviews/FEA-15-DIAG-ACL-1-*.md
  - doc/handoffs/FEA-15-DIAG-ACL-1-*.md
  - verification/FEA-15-DIAG-ACL-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 不修改生产代码、测试、依赖、Schema 或冻结契约；不进行修复
  - 不撤销或修改系统解释器 ACL、不清理任何文件或 AppContainer profile、不 push
  - 不访问或修改真实用户库；未知资源只评估，不推断归属
---

# FEA-15-DIAG-ACL-1：测试失败与资源影响只读诊断

## 目标和范围

依据 [FEA-15-ACCEPT-1](FEA-15-ACCEPT-1.md) 及其 `verification/FEA-15-ACCEPT-1/README.md`，诊断插件 sandbox 与 export hook 失败、Host `SetSecurityInfo` ACL 失败；评估 `C:/Python314` ACE、AppContainer profile 和 62 个共享 fixture 候选的归属可行性；输出带证据边界的修复建议（含 v7 测试构造问题）。允许结论为不可判定，不得猜测。

## Acceptance Criteria

- [ ] **AC1 sandbox/export**：形成真实失败链与可复现环境矩阵，区分已证实、假设和不可判定；仅使用任务控制的解释器与隔离目录。 <<PARTIAL: 跨环境复现与调用链已记录；底层失败操作和原始错误未能定位>>
- [ ] **AC2 Host ACL**：诊断 `SourceSecurity.PrivateDirectory` / `SetSecurityInfo` 的失败条件与适用范围，保留失败与未执行项。 <<PARTIAL: 失败堆栈和卷能力已记录；精确原方法探针因自动审批额度限制NOT_RUN，拒绝条件仍未知>>
- [ ] **AC3 资源影响**：评估 Python ACL 和用户级 AppContainer profile 的归属可行性；禁止写系统解释器 ACL 或清理。 <<PARTIAL: 缺少运行前快照，ACE/profile归属不可判定；均按PRESERVE_UNKNOWN保留>>
- [x] **AC4 fixture**：对 62 个时间窗口候选给出证据支持的保留或后续处置建议，不执行处置。 <<MET>>
- [ ] **AC5 建议与交付**：形成归因矩阵、修复建议与 v7 测试债说明；命令、环境、时点、HEAD、EXIT 及 NOT_RUN 留证，并提交独立 Review。 <<PARTIAL: 诊断证据已固定提交；ZCode独立Review及最终裁决待完成>>

## 资源与证据

- 工作根：`G:/CODEX/New Manga.workspace/FEA-15-DIAG-ACL-1/`，具体新资源创建前确认不存在；不覆盖、不清理既有资源。
- 证据目录：`verification/FEA-15-DIAG-ACL-1/`。保留原始日志、失败与不可判定说明。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task workspace | `G:/CODEX/New Manga.workspace/FEA-15-DIAG-ACL-1` | PRESERVE_REFERENCED | 原位保留 | `verification/FEA-15-DIAG-ACL-1/resource-manifest.json` | 只读核实目录与 `acl-probe-001`；零删除、零移动 |
| ACL probe | `.../acl-probe-001` | PRESERVE_REFERENCED | 原位保留 | `verification/FEA-15-DIAG-ACL-1/acl-probe.log` | 等价 PowerShell 探针创建；原始 Host 方法未运行 |
| Python ACL / AppContainer profile | `C:/Python314` 与用户级 profile 集合 | PRESERVE_UNKNOWN | 原位保留 | `verification/FEA-15-ACCEPT-1/python-acl-observation.log` | 无运行前快照，无法归属；本 Task 不改 ACL/profile |
| FEA-11 fixtures | `G:/CODEX/New Manga.workspace/FEA-11/fixtures`（62 candidates） | PRESERVE_UNKNOWN | 原位保留 | `verification/FEA-15-ACCEPT-1/fixture-observation.log` | 时间窗不证明归属；不清理 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1–AC5 | `verification/FEA-15-DIAG-ACL-1/README.md` | `daeb6dcccbf970facd2272c00645255ae6bdfb87` | `6a43c65a5cfe179ace566c3e49b63ae4edbe9450d1febc4020ad7ef48920af80` | CANONICAL |
| EV-02 | AC1 | `verification/FEA-15-ACCEPT-1/plugin-control.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `86422c6a9f385699d2614067b0600dcf9740244fe98750a48bfcf8d80e55232e` | CANONICAL |
| EV-03 | AC2 | `verification/FEA-15-ACCEPT-1/dotnet-host-control.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `0ce018b15aa1413d02eeaf27b04afe3758ccb2d94bd8bdd882d3fcf29b5530ec` | CANONICAL |
| EV-04 | AC3 | `verification/FEA-15-ACCEPT-1/python-acl-observation.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `4ef940a1bb3dfd567f7cf2be23679d344c578db6989c620b3a288fbfbbe8a385` | CANONICAL |
| EV-05 | AC4 | `verification/FEA-15-ACCEPT-1/fixture-observation.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `f54409a15d7b09d01eff581862fb65a78365ec7b4b469e0013f6419a377e48ab` | CANONICAL |
| SRC-01 | supporting | `verification/FEA-15-DIAG-ACL-1/resource-manifest.json` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `48e7bc49898d390a94f2424d8240ba0efb6c8cc6f8c640e0f09c600f418c7eac` | SOURCE_PIN |
| SRC-02 | supporting | `verification/FEA-15-DIAG-ACL-1/workspace-observation.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `2bc13c8a06f73595421b9870ae5ac5aed74d4364cab3df55afaf9c918662f2f3` | SOURCE_PIN |
| SRC-03 | supporting | `verification/FEA-15-DIAG-ACL-1/volume-observation.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `7e2d56b13357d360cac90fbe97364490709dbf353ec03e4d08c8d9c317fca5cb` | SOURCE_PIN |
| SRC-04 | supporting | `verification/FEA-15-DIAG-ACL-1/volume-winapi.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `05b8e504c104e5bf192b5f9d3260e8d6a9d227ae6d64dd967e7f4422a086b714` | SOURCE_PIN |
| SRC-05 | supporting | `verification/FEA-15-DIAG-ACL-1/acl-probe.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `fc661835ee481a8421f389e5a7024393998c8a864f7af03f1544daf5892b2ef2` | SOURCE_PIN |
| SRC-06 | supporting | `verification/FEA-15-DIAG-ACL-1/checkpoint.md` | `daeb6dcccbf970facd2272c00645255ae6bdfb87` | `f8c9e340c3baf74fcaa44948ff8e606df1c87d6acf7d0955375a4322d33d0897` | SOURCE_PIN |
| SRC-07 | supporting | `verification/FEA-15-ACCEPT-1/v7-repro-2.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `8e0abc01bec34b3e38cc3a9e6117d34f443529552d60405ca2860c271779a6e6` | SOURCE_PIN |
| SRC-08 | supporting | `verification/FEA-15-ACCEPT-1/v7-v14-probe.log` | `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488` | `bf1413267cffabc37b9f58e19526ae1e2ff4c0b98df9278f8c619d3e2cfe9dd7` | SOURCE_PIN |
| SRC-09 | supporting | `verification/FEA-15-DIAG-ACL-1/appointment.md` | `daeb6dcccbf970facd2272c00645255ae6bdfb87` | `ce7b5fcd2e1a98fdaa7c379793df81924712dae23a9d7da09af20d58af38e938` | SOURCE_PIN |
| SRC-10 | supporting | `verification/FEA-15-DIAG-ACL-1/gates-review.log` | `97145556a7be4865dae3b5bfe2868cf7fbf90e1d` | `a0d56069846c0fe9c1017dc57dfb3fd46575ca42636d74194eb00785c2c3a1c9` | SOURCE_PIN |

## Closeout Record

- 2026-11-11：ZCode 冻结诊断范围并释放 `ready`；与 FEA-15-ACCEPT-1 终态及唯一当前指针原子切换；未执行。
- 2026-11-11：Codex 认领 `in_progress`；实测 main 基线 `1e4542a047e991a5f10b0b213ca5a96eafe919a4`，工作树干净；范围不变。
- 2026-11-11：完成只读诊断并将证据固定于 `c06d06377dc7e7a9cb5e7ee83a067a28ec0d0488`；AC1–AC3/AC5 保留 partial，AC4 met；所有未知资源保留。
- 2026-11-11：登记 ZCode 独立 CLI Review；进入 `in_review`，报告与状态结论待 ZCode 审查/裁决。
