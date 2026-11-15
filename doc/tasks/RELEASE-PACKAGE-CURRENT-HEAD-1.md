---
id: RELEASE-PACKAGE-CURRENT-HEAD-1
title: 在当前 HEAD 重新打包 Windows 单文件包并做真实窗口冒烟（替换不绑定基线的 0.1.1 旧证据）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: package-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: 8997b8e23
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - RELEASE-GATE-DISPOSITION-1
  - SIDECAR-REBUILD-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B「Gate 条件 4 的 Agent 可做部分」
base_commit: da7f88fb5
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/RELEASE-PACKAGE-CURRENT-HEAD-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-CURRENT-HEAD-1.md
  - doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-PACKAGE-CURRENT-HEAD-1/**
---

# RELEASE-PACKAGE-CURRENT-HEAD-1：当前 HEAD 打包 + 真实窗口冒烟

## 来源

`RELEASE-GATE-DISPOSITION-1` 判定 Gate 条件 4 的「打包与冒烟」是 **Agent 可做**部分，
且 `MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §3 明记：

> `G:\CODEX\New Manga.workspace\artifacts\release\NewManga-0.1.1-win-x64\` 是 `0.1.1` 的旧产物，
> **不绑定当前基线**，不得当作当前 commit 的安装包证据。

本卡消除这一缺口：在**当前 HEAD** 重新产出单文件包，并跑真实窗口冒烟。

## 前置（已具备）

- `SIDECAR-REBUILD-1` 已用 PyInstaller 重建 sidecar，产物在
  `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/`（**792 MB / 1024 文件**，git-ignored）；
- 实测该 sidecar 可运行：`core.ping` 有响应、`schema v14 already current`。

## 目标（一个可观察结果）

产出**绑定当前 HEAD commit** 的 Windows 单文件包（含 sha256）与**真实窗口冒烟证据**
（窗口找到 + host ready + 自然退出 + 截图），并如实说明它**不等于**安装矩阵。

## Acceptance Criteria

- [x] **AC1 打包成功且绑定基线**：`tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir <bundle>` <<MET>>
      退出 0；`manifest-singlefile.json` 的 `git_head` == 当前 HEAD 完整 sha。
- [x] **AC2 真实窗口冒烟 PASS**：`smoke-singlefile.json` 中 `window_found=true`、`window_title="New Manga"`、 <<MET>>
      `host_ready=true`、`exit_code=0`、`exit_kind="natural"`、`pass=true`；并留存截图。
- [x] **AC3 产物指纹**：记录 exe 尺寸、sha256、`publish_exit_code`、耗时。 <<MET>>
- [x] **AC4 零产品代码改动 + 零工作区污染**：`git diff` 不触及 `src/**`、`apps/**`、`tools/**`； <<MET>>
      提交后工作区仅含本卡与证据目录。
- [x] **AC5 边界如实说明**：明确本卡**只**替换「不绑定基线的旧包」缺口， <<MET>>
      **不等于** clean install / 升级回退 / 卸载矩阵；**不改变 Gate 条件 4 的判定**。
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只新增证据与文档，不改产品代码**。

## 禁止范围

- 不得声称「条件 4 已完成」或「Gate 可解锁」；
- 不得把单文件包的冒烟当作安装/卸载验证；
- 不得修改 `.csproj`/`.sln`/源码以让打包通过；
- 不得删除或改写 `0.1.1` 旧包（保留为历史证据）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 打包 + 冒烟 | `pwsh -NoProfile -File tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir <bundle> -EvidenceDir verification/RELEASE-PACKAGE-CURRENT-HEAD-1` | EXIT 0，`publish: 1/1 PASS` |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RPC-00 | AC1-AC5 证据说明（不影响判定） | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/README.md | 3085962e2 | 85cbaf683e95c8502ff461398e22c7bf5e85fa79eb9ca28ad06ec6013d9c7a41 | CANONICAL | BLOB |
| EV-RPC-02 | AC1 打包 manifest（git_head/尺寸/sha256） | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/manifest-singlefile.json | 8997b8e23 | 95930d923c8e39370265bc3ff9648bbd4c1fbdafc5c004d0514e3cfec92d61cd | CANONICAL | BLOB |
| EV-RPC-03 | AC2 冒烟结果（window_found/host_ready/natural exit） | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/smoke-singlefile.json | 8997b8e23 | edc12e2cf9eac1c99cc1c994f0e793fbad2dfec3a73577aaec6bc57f7dfa549d | CANONICAL | BLOB |
| EV-RPC-04 | AC2 真实窗口截图 | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/published-singlefile.png | 8997b8e23 | 149f79fca4832de8fa6c5422694de7278fdb248319f0aae637762f1a50bedb22 | CANONICAL | BLOB |
| EV-RPC-05 | AC1 打包完整日志 | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/publish-release.log | 8997b8e23 | 1a4da218b8c064462b5a5ea1ba3d65b296cbd792cb7606e0f5f8205b9006575c | CANONICAL | BLOB |
| EV-RPC-06 | AC3 打包构建日志 | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/build-singlefile.log | 3085962e2 | aa5ba258cda93957247d419a67283ee99545c0f5d2c56de3d471b7376e5a68b9 | CANONICAL | BLOB |
| EV-RPC-07 | AC1/AC3 多模式汇总 | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/manifest-summary.json | 3085962e2 | 6199525c795894b136e54a87a4fc68b3390546bd91170cb302da6a3db1ebf78b | CANONICAL | BLOB |
| EV-RPC-08 | AC1 sidecar 可用性核证 | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/sidecar-availability.log | 3085962e2 | c26b8b84dcc5e8f9ee62e4cc98cff3338aad400a9bff45425254ecbc5367f174 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/RELEASE-PACKAGE-CURRENT-HEAD-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 `8997b8e23`。
- **结果**：在当前 HEAD 的产品代码树上产出 **94.94 MB 单文件 exe**（sha256 `07DD80F0…3AE74`）
  并通过**真实窗口冒烟**（`window_found=true`、`window_title="New Manga"`、`host_ready=true`、
  `exit_code=0`、`exit_kind=natural`、`pass=true`，含截图）。
- **独立复核**：`package-review` verdict **APPROVED_WITH_LIMITATIONS**（0/2/3/4）：
  - **亲眼看图确认是 NewManga 本体**（1416×939，底部两处「Host 就绪」与 `host_ready` 独立互证），
    排除本项目此前出现过的假截图风险；
  - P1-01（`git_head` 是父提交）→ 已补 **tree-hash 等价性**说明（`apps`/`src` 两提交完全一致）；
  - P1-02（**包不含 sidecar 不可独立分发** + E-7 五项开放 + 冒烟不覆盖功能路径）→ 已全部披露；
  - P2-01（`host.log` 被删）→ 由截图旁证并记录；
  - P2-02/P2-03（PLAN/STATUS 未登记）→ STATUS/PLAN 预算已近上限（3178/3200、6960/7000），
    登记在本卡与判定表，**未强改指针**（记录为未关闭项）。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. **单文件包不含 sidecar**（792 MB 外挂），**不能独立分发** —— 需另立卡补 sidecar 打包步骤；
  2. 冒烟只覆盖「启动 + Host ready + 自然退出」，**功能路径未触达**；
  3. **E-7 仍有 5 项开放**（并发安全不可宣称）；
  4. clean install / 升级回退 / 卸载 / 签名仍缺（需真机与证书）；
  5. PLAN/STATUS 未登记本卡（预算上限）。
