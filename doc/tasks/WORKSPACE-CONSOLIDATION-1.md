---
id: WORKSPACE-CONSOLIDATION-1
title: 工作区整理：归档未合并支线、清理可再生体积、收敛为单一主线
kind: ops
governance_version: 2
status: ready
approval: approved_by_owner_2026-10-20
blocked_by: null
suggested_owner: dsh
owner: dsh
reviewer: Codex
depends_on: []
base_commit: b4560ae8ab2ff9c6c4db50f9d57b50fe1e8393df
branch: antigravity/P09-AC3-DELETE-HARDEN-1
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/WORKSPACE-CONSOLIDATION-1
allowed_paths:
  - verification/WORKSPACE-CONSOLIDATION-1
  - doc/WORKTREE_SAFETY_INVENTORY.md
  - doc/tasks/WORKSPACE-CONSOLIDATION-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - G:/CODEX/New Manga.workspace/archive/bundles
---

# WORKSPACE-CONSOLIDATION-1：工作区整理

## 来源与目标

**用户 2026-10-20 授权**：「由你来执行」——整理项目文件、合并支线、只剩一条主线、清理不需要的文件和支线。

**Codex 于 2026-10-20T19:55:38 完成只读前置核查后**按治理规则停止（未执行任何清理），理由三条：

1. STATUS 登记 dsh 为唯一 Active Coordinator，未完成串行交接
2. 本 Task 尚未在 Plan/STATUS 激活并冻结范围
3. `WORKTREE_SAFETY_INVENTORY` 未刷新到当前状态

**本 Task 的存在即为解除这三条**：

1. **不需要交接**——dsh 已在位（`coordinator-lease.py status` → `active_agent: dsh, epoch 8, state: ACTIVE`）。由 dsh 自己执行
2. **本文件 + Plan/STATUS 登记**即激活与冻结
3. **AC2 即刷新该 Inventory**

**可观察交付**：一条主线、可解释的分支集合、已归档的未合并工作、已释放的可再生磁盘体积，且治理检查仍为 PASS。

## 实测基线（2026-10-20，Codex 前置核查 `preflight.json`）

| 项 | 值 |
|---|---:|
| HEAD | `b4560ae8a` |
| 治理主线 | `antigravity/P09-AC3-DELETE-HARDEN-1` |
| 本地分支 | **418** |
| 已并入 / 未并入主线 | 342 / **76** |
| 已注册 worktree | **213** |
| 主 checkout 未跟踪文件（逐文件口径） | **1592**（含 26 个 Task 草稿） |
| `.git` | 1348 MB |
| `New Manga.workspace` | **167 GB** |
| `main` 相对主线 | 0 / 476（落后 476） |
| `master` 相对主线 | **3** / 2380（**master 有 3 个独有提交**） |

## Acceptance Criteria

- [ ] **AC1 四表盘点**：分支表（逐条算 `git rev-list --count <主线>..<branch>`，不许抽样）、worktree 表、未跟踪文件表、大体积目录表；产出 `inventory.md` + `inventory.json`
- [ ] **AC2 刷新权威清单**：`doc/WORKTREE_SAFETY_INVENTORY.md` 更新到当前 213 个 worktree 的实测状态，逐项标注 dirty/untracked/独有提交/资源 disposition
- [ ] **AC3 保护项全量枚举**：列出所有 `PRESERVE_REFERENCED` worktree（实测 57 个：38 来自 `verification/**/*.json`，Task 表另有）与被证据 pin 引用的文件；证明清理前后**逐一在位**
- [ ] **AC4 未合并分支归档**：76 个未合并分支每个给出 `git tag archive/<branch>` + `git bundle create`；bundle 落在 `G:\CODEX\New Manga.workspace\archive\bundles\`；**无 bundle 不得删分支**
- [ ] **AC5 已合并分支清理**：仅 `-d`（不用 `-D`），仅对非 worktree 检出、非保护、非主线者；git 拒绝的如实记录
- [ ] **AC6 worktree 清理**：仅清理「不在保护名单 且 `status --porcelain` 空 且 `stash list` 空」者；**先 `worktree remove` 再删分支**；遇 dirty **不 `--force`**
- [ ] **AC7 workspace 体积释放**：只清可再生的缓存/依赖/构建物/venv；**禁止触碰 `verification/` 与任何保护项路径**；逐项记录路径、体积、判定依据
- [ ] **AC8 主线裁定**：明确唯一长期主线；处置 `master` 的 3 个独有提交（不得直接丢弃）；裁定写进 `doc/`
- [ ] **AC9 验收**：治理检查仍 **PASS**（warning 数不增加）；未跟踪草稿数不因清理而减少；`doc/tasks` 已跟踪数仍为 295

## 允许修改范围

- 本 Task 文件、`verification/WORKSPACE-CONSOLIDATION-1/`
- `doc/WORKTREE_SAFETY_INVENTORY.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`
- `G:\CODEX\New Manga.workspace\archive\bundles\`（仓外归档）
- Git refs：`archive/*` tag 的创建、非保护分支的删除、非保护 worktree 的移除

## 禁止范围

- **禁止 `git add -A` / `git add doc/tasks` / `git add .`**——会卷走 26 个未提交草稿（本仓库已栽两次）
- **禁止 `git clean -fdx` / `git checkout -- .` / `git reset --hard`** 于含未跟踪内容的目录
- **禁止删除任何 `PRESERVE_REFERENCED` 的 worktree**
- **禁止删除有独有提交且无 bundle 的分支**
- **禁止 `git worktree remove --force`**
- **禁止 push**
- **禁止改名或合并治理主线本身**（AC8 只裁定并记录，不改写历史）
- 不修改任何他人未提交内容

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `git rev-list --count <主线>..<branch>` 逐条 | 418 分支 | NOT_RUN | inventory.json |
| AC2 | `git worktree list` + 逐项 status | 213 worktree | NOT_RUN | inventory.md |
| AC3 | 收集 `PRESERVE_REFERENCED` + 证据 pin 路径 | — | NOT_RUN | protected.json |
| AC4 | `git bundle create` + `git tag` | 76 分支 | NOT_RUN | bundles/ |
| AC5–AC6 | `git branch -d` / `git worktree remove` | — | NOT_RUN | 前后对比 |
| AC7 | 体积测量 + 删除 | 167 GB | NOT_RUN | 释放统计 |
| AC9 | `pwsh -NoProfile -File tools/governance/check.ps1` | — | NOT_RUN | 前后输出 |

## 依赖、风险与阻塞

- **无硬依赖**
- **风险 R1**：`master` 有 3 个独有提交——直接删会丢工作。必须逐条审查后归档或合并
- **风险 R2**：`git branch -m` 改名主线会牵动以它为基的 worktree；本 Task 不改名
- **风险 R3**：`.git` 仅 1.3 GB，167 GB 在 workspace；真正收益在 AC7，而 AC7 的风险最高（可能与运行中的进程共用）
- **风险 R4**：26 个草稿归原作者；任何批量 add 都会误伤

## 交付与运行记录

- Handoff：尚无。
- Review：`reviewer: Codex`（本 Task 为自己执行，按协作协议不得自审）。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | — | 主 checkout，本 Task 执行位置 |
| archive | G:/CODEX/New Manga.workspace/archive/bundles | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/archive/bundles | — | AC4 的 bundle 归档目标；待创建 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待填写。
- 当前指针清理：待填写。
