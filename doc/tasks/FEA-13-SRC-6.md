---
id: FEA-13-SRC-6
title: SC-B01 ④ 源引用/授权元数据入包（包内加密段；Host staging 交接面）
kind: implementation
governance_version: 3
status: ready
approval: **ZCode 独立裁决 2026-11-09（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）**：单列立项（「必须包含」项，非不做）；**不阻塞 FEA-15 正式验收**（验收登记为已知 limitation）；排在 `FEA-11-HOST-AUTH-3` 之后（同域 SourceAccessRegistry/Host 授权）
suggested_owner: zcode（Host/C# 主责域）
owner: null
reviewer: null
depends_on:
  - FEA-13-COV-2
  - FEA-11-HOST-AUTH-3
base_commit: 07545adf1
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-13-SRC-6
allowed_paths:
  - doc/tasks/FEA-13-SRC-6.md
  - doc/reviews/FEA-13-SRC-6-*.md
  - doc/handoffs/FEA-13-SRC-6-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-13-SRC-6/**
  - src/infrastructure/sqlite/nmbak.py
  - src/application/maintenance/restore_plan.py
  - src/bootstrap/core_assembly.py
  - tests/storage/test_nmbak_source_access.py
  - tests/application/test_restore_plan_source_access.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - **实现范围以本卡冻结为准**（scope 冻结 2026-11-10，DSH）
  - 不实现跨机恢复（DPAPI CurrentUser：同机恢复有效，跨机须重授权；跨机负例只做 typed 拒绝断言）
  - **不改 C-06/C-09/C-17 契约字节与 18 pins**（C-09 SC-B01 已含「源引用与授权元数据…包内加密」，无需 UNFREEZE；如需扩条款另走 errata）
  - 不改 `SourceSecurity`/`DpapiSecretProtector` 的既有加解密语义、不改 registry.dat 内部格式版本
  - 不实现数据根迁移（`FEA-13-MIGRATE-6` 单列 blocked）
---

# FEA-13-SRC-6：SC-B01 ④ 源引用/授权元数据入包（占位）

## 裁决依据（ZCode 2026-11-09）

- C-09 SC-B01 的「必须包含」项，SC-B07 强制增量 ④ 已预留；明确不做需走契约 errata（成本高于实现）。
- 产品价值：AD-003 引用模型下，若 SourceAccessRegistry 不随包恢复，重装/恢复后用户须对全部源重新授权，备份恢复承诺落空。
- 时序：排在 `FEA-11-HOST-AUTH-3`（UNFREEZE）之后——两者同域（SourceAccessRegistry/Host 授权），先落恢复语义再叠备份打包。
- **同机恢复有效；跨机恢复须重授权**（DPAPI CurrentUser 绑定，不得写成通用跨机恢复）。

## 预估范围（待 scope review 冻结）

| 项 | 预估 |
|---|---|
| Host staging 交接面 | `SourceAccessRegistry` 导出 → 交给 Core 打包加密段 |
| Core 侧 | `nmbak` 包内新增加密段（`extras/source-access/…`）+ manifest 记录 |
| 恢复反向 | 解包 → Host 导入（冲突/过期处置） |
| 契约 | 若需 C-06/C-09 载体 → 另走 UNFREEZE/errata（不得直接改冻结字节） |
| 证据 | L2 正/负 fixture + 加密段不可读断言 + 恢复后授权可用 |

## Acceptance Criteria

- 待 scope review 冻结（当前仅占位；不得实施）。

## Scope 冻结（2026-11-10，DSH）

**契约依据**：C-09 `SC-B01` 备份覆盖清单的「必须包含」已列「源引用与授权元数据（AD-003 §3.3；Host 私有 registry 随备份纳入，备份包内加密）」→ **契约预留成立，无需 UNFREEZE**；C-06/C-17 零字节改动。

**实现骨架**（3 段）：

| 段 | 内容 |
|---|---|
| Host staging | `SourceAccessRegistry` 新增只读导出：把 `<dataRoot>/host/source-access/registry.v1.dat`（DPAPI 密文）**原字节**复制到 Core 可读 staging（不解密、不改清单）；打包后 staging 清理 |
| Core 打包 | `nmbak` 新增 extras 分类 `source-access`（`extras/source-access/registry.v1.dat`）+ manifest `included_categories` 记录；`EXCLUDED_CATEGORIES` 不新增排除；extras 覆盖面校验沿用 COV-2 |
| 恢复反向 | 解包 → `restore_plan` 把该段写回 `<dataRoot>/host/source-access/registry.v1.dat`；目标已存在时**先 quarantine 旧文件再写**（`SourceAccessRegistry` 既有 quarantine 目录），跨机/跨用户解密失败 → Host typed `SOURCE_REGISTRY_UNAVAILABLE`（不清空原文件） |

**语义边界**：同机同用户恢复有效；跨机/跨用户须重授权（DPAPI CurrentUser 绑定，不得写成通用跨机恢复）。

## Acceptance Criteria（scope 冻结）

- [ ] **AC-S6-1 打包零改源**：包内含 `extras/source-access/registry.v1.dat`，其字节 SHA-256 == 源文件（DPAPI 密文原样，无明文 identity/roots 泄漏）；manifest 记录 category；打包前后源 registry 文件 SHA-256 不变。 <<MET>>
- [ ] **AC-S6-2 同机恢复可用**：解包写回后 `SourceAccessRegistry.List()` 返回与备份前一致的 `registry_id/generation/roots/identity`；恢复前后 `library.db` 业务行数不变。 <<MET>>
- [ ] **AC-S6-3 跨机/跨用户负例**：以不同 protector（模拟 DPAPI 失败）导入 → typed `SOURCE_REGISTRY_UNAVAILABLE`；原 registry 不被清空（quarantine 保留），零未处理异常。 <<MET>>
- [ ] **AC-S6-4 冲突处置**：目标已有 registry 时，旧文件先 quarantine 再写回（不静默覆盖）；恢复计划记录该动作。 <<MET>>
- [ ] **AC-S6-5 门禁/契约/不夸大**：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 18/18（C-09/C-06/C-17 字节零变化）；`diff ⊆ allowed_paths`；全量 pytest/.NET 不低于当轮基线；gated/跨机用例默认 skip 且逐条原因。 <<MET>>

## 证据计划

L2 正/负 fixture（构造最小 registry.v1.dat + 假 DPAPI protector）：E1 包内段字节/SHA 与 manifest；E2 恢复后 List/行数；E3 跨机 typed 拒绝 + 原文件保留；E4 冲突 quarantine；E5 零写（打包前后源 SHA）；E6 全量门禁日志。

## 风险与回退

| 风险 | 处置 |
|---|---|
| DPAPI 跨机/跨用户 | 只声明同机同用户；跨机 typed 拒绝 + 文档 limitation |
| registry.dat 版本演进 | 只做原字节搬运，不解析内部格式（版本由 Host 自己校验） |
| 与 FEA-15 验收交互 | FEA-15 登记「跨机恢复不支持」已知 limitation（本卡不阻塞验收） |
| 回退 | evalue revert 实现提交；无 schema/契约字节变更 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（proposed 占位） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实数据 |

## Closeout Record

- 未开始（proposed）。
