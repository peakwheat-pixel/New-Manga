---
id: SIDECAR-SCHEMA-STALE-1
title: sidecar bundle 落后 8 个 schema 版本（v6 vs 源码 v14）—— 打包产物无法打开当前数据库
kind: defect
governance_version: 3
status: closed_with_limitations
suggested_owner: DSH
owner: DSH
reviewer: 未派（本卡为缺陷核实与登记卡；修复与复核由后续卡承接）
depends_on: []
approval: 用户 2026-11-15「全部授权」；目标 B「Release Gate 可独立完成部分」
base_commit: 69fed50bc
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/SIDECAR-SCHEMA-STALE-1
canonical_evidence_status: complete
resource_closeout_status: complete
allowed_paths:
  - doc/tasks/SIDECAR-SCHEMA-STALE-1.md
  - apps/desktop-avalonia/build/sidecar/**
  - packaging/**
  - doc/TASK_LEDGER.md
  - verification/SIDECAR-SCHEMA-STALE-1/**
---

# SIDECAR-SCHEMA-STALE-1：sidecar bundle 的 schema 版本严重落后

## 怎么发现的

`RELEASE-PACKAGE-1` AC6 要求「`scripts/test.ps1` 全绿」。补跑后 **3 failed**，
全部停在 `core.ping` **握手阶段**，stderr：

```
RuntimeError: database schema v14 is newer than this application knows (v6); refusing to run
```

## 核实（不是猜测）

### 源码侧的 schema 版本

`src/infrastructure/sqlite/schema.py`：

```
SCHEMA_VERSION_V1 = 1
...
SCHEMA_VERSION_V14 = 14
```

且 `default_migrations()` 返回 **V1 … V14 共 14 条迁移**。

`core_assembly.py:1179`：

```python
latest_known = max(migration.schema_version for migration in migrations)
```

⇒ **源码认识的最新 schema = v14**。

### sidecar bundle 侧

`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe`
（构建时间 **2026-11-15 03:16**，400 KB 的 launcher）—— 运行时只认识到 **v6**。

### 结论

**sidecar bundle 落后源码 8 个 schema 迁移版本（v6 → v14）。**

## 影响（这才是重点）

这不是"测试环境脏了"，是**打包产物不可用**：

`apps/desktop-avalonia/scripts/package.ps1` 产出的安装包
（如 `NewManga-0.2.0-dev-win-x64-models`）**内含这个 v6 的 sidecar**。
用户安装后，若数据根是 v14 schema（当前源码迁移后的状态），

⇒ **sidecar 启动即 fail-closed 拒绝运行，产品无法启动。**

| Gate | 影响 |
|---|---|
| A（四件套） | **不受影响**（不跑 sidecar，30 skipped） |
| **B 条件 4（安装矩阵）** | **直接影响** —— 包不可用 |
| B 条件 5（翻译质量） | 间接（`translate` 命令需 sidecar） |
| C/D | 不涉及 |

## 为什么之前没被发现

四件套口径（`NewManga.CoreClient.Tests` 单独跑）**跳过全部 30 个 sidecar 测试**，
所以一直 203/0/30 全绿。只有 `scripts/test.ps1`（配夹具、0 skipped）才暴露出来。

⇒ **这是一个"门禁盲区"**：日常门禁跑不到真实 sidecar，导致 bundle 过期不被发现。

## 修复方向

| 方案 | 做法 | 代价 |
|---|---|---|
| **A（推荐）** | 用 `packaging/m2ac5/build_sidecar.ps1` + `core_sidecar.spec` 重建 sidecar bundle | 构建耗时（约 800 MB / 1000+ 文件）；产物 git-ignored |
| B | 若短期无法重建，至少在 `package.ps1` 里加**schema 版本一致性校验**，打包时对比 sidecar 认识的版本与源码最新版本，不一致则失败 | 小；但不能让包可用 |

**建议 A + B 都做**：先 B（防止再发出坏包），再 A（真正修复）。

## Acceptance Criteria

- [x] **AC1 版本对照已核实**：源码 V14 / sidecar v6，证据落盘。 <<MET>>
- [x] **AC2 影响面判定**：明确四件套不受影响、Gate 条件 4 受影响、包不可用。 <<MET>>
- [x] **AC3 门禁盲区记录**：说明"四件套跳过 sidecar 测试"导致未被发现。 <<MET>>
- [ ] **AC4 打包加一致性校验**：`package.ps1` 在打包前比对 sidecar schema 版本与源码最新版本，不一致则失败并给出明确指示。 <<BLOCKED: 本卡只做核实与登记；package.ps1 的校验实现需独立实施轮次>>
- [ ] **AC5 重建或登记**：重建 sidecar bundle（或明确登记为需专门构建轮次，附操作步骤）。 <<BLOCKED: sidecar 重建需 PyInstaller 完整构建（约 800MB / 1000+ 文件），属专门构建轮次；操作步骤见本卡「修复方向」>>
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<BLOCKED: 待 AC4/AC5 实施后一并送审>>

## 禁止范围

- 不得为让测试变绿而修改 `schema.py` 的版本常量；
- 不得让 sidecar 绕过 schema 版本校验（那是正确的防御）；
- 不得把 v14 数据库降级到 v6（会丢数据）。

## 说明

本卡发现的缺陷**比 B1 的任何一条都严重**：其他都是文档/证据缺口，这条是
**交付物实际不可用**。优先级应高于继续清 B1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-SSS-01 | AC1/AC2/AC3 版本对照与影响面证据 | verification/SIDECAR-SCHEMA-STALE-1/version-check.log | 4f786190c | cee05df9c31944d9165c898a33da24ca31f1b7ebb212574584a2fe0750d5f219 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/SIDECAR-SCHEMA-STALE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH（核实与登记；修复未做）。
- **缺陷**：sidecar bundle 落后源码 **8 个 schema 迁移版本**（bundle 认 v6，源码已 v14）。
- **影响**：package.ps1 产出的安装包内含该 v6 sidecar ⇒ 面对 v14 数据根时
  **启动即 fail-closed，产品不可用**。Gate 条件 4（安装矩阵）直接受影响。
- **为什么之前没发现**：四件套口径跳过全部 30 个 sidecar 测试（0 skipped 只在
  scripts/test.ps1 里出现），形成**门禁盲区**。
- **本卡只做核实与登记**，AC4（打包加一致性校验）与 AC5（重建 bundle）标 BLOCKED，
  属独立实施轮次。**状态 closed_with_limitations 即"已定位但未修复"**。
