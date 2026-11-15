---
id: RELEASE-PACKAGE-BUNDLE-1
title: 组装含 sidecar 的可分发 Windows portable 包（当前 HEAD）并做包内启动验证
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: bundle-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: 53d803e04
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - RELEASE-PACKAGE-CURRENT-HEAD-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B「Gate 条件 4 的可做部分」
base_commit: e2c9fd058
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/RELEASE-PACKAGE-BUNDLE-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-BUNDLE-1.md
  - doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-PACKAGE-BUNDLE-1/**
---

# RELEASE-PACKAGE-BUNDLE-1：含 sidecar 的可分发包

## 来源

`RELEASE-PACKAGE-CURRENT-HEAD-1` 的 r1 复核 **P1-02a** 指出：

> **单文件包不含 sidecar** —— 94.94 MB 的 exe 无法独立运行，需 792 MB sidecar 外挂
> （`publish-release.ps1:61` 自述 `needs the sidecar bundle at runtime`）⇒ **不是可分发包**。

本卡补上这一块：把 exe + sidecar + 许可证 + 启动脚本组装成**可分发的 portable 包**，
并用**包内路径**实际启动验证（不是拿外挂 sidecar 跑）。

## 目标（一个可观察结果）

产出 `NewManga-<head>-win-x64/`（含 `core-sidecar/`）与对应 zip；
**用包内 exe + 包内 sidecar 启动一次**，窗口出现、Host ready、数据库创建成功；记录 zip sha256。

## Acceptance Criteria

- [x] **AC1 包结构完整**：包内至少含 `NewManga.App.exe`、`core-sidecar/`（5 个 exe + `_internal` + `models`）、 <<MET>>
      `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`Run-NewManga.cmd`、`README.md`、`RELEASE-<head>.md`。
- [x] **AC2 包内启动验证**：用**包内**路径启动（`--sidecar-dir=<包>/core-sidecar`，隔离 data/log/theme）， <<MET>>
      进程存活、窗口标题为 `New Manga`、`host.log` 出现 `core_service ready` + `host_bridge ready` +
      `self-check status=Passed`、`library.db` 被创建。
- [x] **AC3 zip 与指纹**：产出 zip，记录条目数、大小、sha256；抽样校验 zip 内含 `NewManga.App.exe`、 <<MET>>
      `core-sidecar/core_service.exe`、`Run-NewManga.cmd`、`core-sidecar/models/`。
- [x] **AC4 边界如实**：明确本包是 **portable 文件夹**，**不是安装器**；clean install / 升级回退 / 卸载 / <<MET>>
      签名仍未做；E-7 并发项仍开放 ⇒ **不改变 Gate 条件 4 的最终判定**。
- [x] **AC5 不回归**：`check.ps1` PASS；`verify_pins.ps1` 18/18；`api_inventory` 1/80/6=87。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只新增证据与文档**；包体在 `G:\CODEX\New Manga.workspace\artifacts\release\`（仓外，不入 Git）。

## 禁止范围

- 不得把 portable 包说成「安装器」或「可发布版本」；
- 不得声称已完成 clean install / 升级 / 卸载矩阵；
- 不得修改产品代码；
- 不得把 zip 提交进仓库（887 MB / 694 MB）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 包内启动 | 启动 `<包>/NewManga.App.exe --sidecar-dir=<包>/core-sidecar --data-root …` | 窗口 "New Manga"、host.log 有 ready、library.db 创建 |
| zip 校验 | 抽样读 zip 条目 | 含 exe / core_service.exe / Run 脚本 / models |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RPB-01 | AC1/AC2/AC3/AC4 证据总述 | verification/RELEASE-PACKAGE-BUNDLE-1/README.md | 53d803e04 | PLACEHOLDER_SHA | CANONICAL | BLOB |
| EV-RPB-02 | AC1 正规包清单 | verification/RELEASE-PACKAGE-BUNDLE-1/bundle-manifest.txt | 53d803e04 | 8c304152eafce970dc39e39efffe16bded3ff3788d7a01b440f8ace1abbb3792 | CANONICAL | BLOB |
| EV-RPB-03 | AC2 包内启动日志（host.log） | verification/RELEASE-PACKAGE-BUNDLE-1/launch-verification.log | 53d803e04 | 84a1c4b3a3bd3d0a9b7dcf252fb167b502b7b6968233f6b5d52535f1d0d5122b | CANONICAL | BLOB |
| EV-RPB-04 | AC3 zip 指纹 | verification/RELEASE-PACKAGE-BUNDLE-1/zip-fingerprint.txt | 53d803e04 | d8d7f7ad4d3bc943f80521d5a5e8fd504af6cb52aab1ede9eb3f4b800a1f2a0f | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/RELEASE-PACKAGE-BUNDLE-1/ | NOT_APPLICABLE | — | — | 新增证据；包体与 zip 在仓外 task-envs/FINAL-VALIDATION-1/out/，不入 Git |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 `53d803e04` + r1 返修（本提交）。
- **结果**：用**正规打包脚本** `package.ps1 -WithModels` 产出 `models` 变体可分发包：
  **1,038 文件 / 827.6 MB**，zip **683.3 MB**（sha256 `6a97d2e4…`）；
  包内启动验证 PASS（窗口 `New Manga`、`core_service ready` → `host_bridge ready`、
  `self-check status=Passed` 17 capabilities、`library.db` 创建）；
  **独立复核者另行从零启动两次**（含「不传 `--sidecar-dir`」的回退路径），
  确认子进程路径指向包内 ⇒ **portable 可独立分发成立**。
- **独立复核**：`bundle-review` verdict **APPROVED_WITH_LIMITATIONS**（0/0/4/4）：
  - **R-01**（AC2 证据不自足）→ 已补 PID/窗口标题/子进程路径/DB 尺寸字段；
  - **R-02**（`TASK_LEDGER` 派生指标过期）→ 收口时重跑；
  - **R-03**（许可/变体不符：含 AGPL 模型却用 base 命名、缺 `THIRD_PARTY_LICENSES.md`、无 `VERSION.json`）
    → **改用正规脚本重打 models 变体**，4 件套许可逐字节一致、`VERSION.json` 声明 `license=AGPL-3.0`；
    初版手工包**已废弃**并在证据 §5 声明不得用于对外分发；
  - **R-04**（非终态未登记 DAG）→ 由本卡标 `done` 消解（既有表外边界）；
  - **R-05**（数字不准）→ 更正为 **1,038 文件**、**17 capabilities**；
  - R-06/R-07/R-08 → 证据 §7 记录；包内 README 边界由正规脚本产物覆盖。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. 未执行 clean install / 升级回退 / 卸载矩阵（包内带脚本但未真机跑）；
  2. **未代码签名**；
  3. **E-7 并发项仍 5 项开放** —— 并发安全不可宣称；
  4. 冒烟只覆盖「启动 + Host ready + 自然退出」，**功能路径未触达**；
  5. 初版手工包（`NewManga-e2c9fd058-win-x64`）已废弃，保留在仓外仅作历史。
