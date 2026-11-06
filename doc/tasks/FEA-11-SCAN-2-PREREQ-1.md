---
id: FEA-11-SCAN-2-PREREQ-1
title: FEA-11-SCAN-2 前置契约：C-17 v1.1 UNFREEZE（冷启动扫描目标枚举命令层）
kind: contract
governance_version: 3
status: done
approval: 用户 2026-11-06「让 Codex 判断下一部任务，由 DSH 执行」→ Codex 裁决 NEXT-TASK=FEA-11-SCAN-2（先独立 scope review，优先 B1）；scope review `doc/reviews/FEA-11-SCAN-2-scope-r1.md` 结论 **READY-WITH-UNFREEZE**、推荐 B1；DSH 2026-11-06 裁决：B1 采纳、S-1 取选项②（AC 降级 typed SOURCE_REGISTRY_UNAVAILABLE + L-G 保留）、S-2 采纳（Core 枚举 source_id 为唯一权威）、S-4 登记 limitation；本卡为 C-17 v1.1 UNFREEZE 前置，不直接实施 SCAN-2 运行时
suggested_owner: dsh（Lead/Architect：契约 UNFREEZE 由 DSH 提案并执行；独立 Reviewer 必选）
owner: dsh（Lead）
reviewer: 独立上下文 fresh subagent（byte-level 契约字节复核；session `1326c586-5b5b-4e7a-bc80-653ed57f3e3a`；报告 `doc/reviews/FEA-11-SCAN-2-PREREQ-1-c17-review.md`；APPROVE P0/P1/P2=0，P3×6 已处置；未参与提案/实现）
depends_on:
  - FEA-11-SCAN-1
  - FEA-11-SCAN-2
base_commit: c5d30e4ca   # 本卡登记时 main head（实现释放点由 DSH 在重冻后重新固定）
branch: null
worktree: null
integration_commit: 7451bfaaa
delivery_head: 7451bfaaa
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-SCAN-2-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-SCAN-2-PREREQ-1.md
  - doc/tasks/FEA-11-SCAN-2.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - doc/reviews/FEA-11-SCAN-2-*.md
  - doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C17.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-SCAN-2-PREREQ-1/**
out_of_scope:
  - Core/Host 生产代码（命令 handler、scheduler、App 接线归 FEA-11-SCAN-2 实现卡）
  - SQLite schema/migration/索引；任何业务表新增
  - M2-C1/C-16/C-15/C-06 字节修改（本卡只动 C-17 v1.1 与冻结记录/矩阵）
  - 新增依赖、真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-SCAN-2-PREREQ-1：C-17 v1.1 UNFREEZE（冷启动扫描目标枚举命令层）

> 定位：**契约前置卡**。只做 C-17 v1.1 的 UNFREEZE 提案、独立 byte-level 复核、重冻与 pins；不做 SCAN-2 运行时实现（另卡 `FEA-11-SCAN-2`）。

## 来源与依据

1. Codex 2026-11-06 裁决：`G:\CODEX\New Manga.workspace\FEA-12\codex-next-task.md`（NEXT-TASK=FEA-11-SCAN-2；先 scope review，优先 B1）。
2. Scope review：`doc/reviews/FEA-11-SCAN-2-scope-r1.md`（fresh subagent；结论 READY-WITH-UNFREEZE；B1 可行；B2 不推荐；S-1/S-2/S-4 待 DSH 裁决已由本卡链落实）。
3. DSH 裁决（2026-11-06）：
   - **B1 采纳**：Core 提供业务目标事实（`source_id`/`source_kind`/`registry_id`/`generation`/`identity_digest`/`project_ids`），Host 用持久 registry 核验授权、取得 locator、铸造新会话 grant；Core 业务真值与 Host 授权真值分离，不建第二套 Book/Page 库。
   - **S-1 选项②**：生产 file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` 属 fail-closed；本卡与实现卡 **不得**声称"启动前缺失 → missing"；SCAN-2 AC 中该场景降级为 typed `SOURCE_REGISTRY_UNAVAILABLE`，L-G 保留；registry resilience 另立后续缺陷卡（不在本轮）。
   - **S-2 采纳**：以 Core 枚举 `source_id`（`src-<uuid>`）为唯一权威；App 不得用 `StableSourceId`/folder `registry_id` 冒充；AC 必须含"真实导入 → 枚举 → target.id == Core `sources.source_id`"判别测试。
   - **S-4 登记 limitation**：`refresh_source_location_auth` 为死代码，撤销/重注册后 Core location auth 不更新；只读切片无法恢复，登记为 L-S4。
   - B2 不推荐（无法覆盖升级前旧库、会复制 Core 业务事实）。

## Scope（冻结）

### C-17 v1.1 必须修订的节（依据 scope review §5）
1. **§0 版本与修订记录**：v1.0 → v1.1；载明触发（SCAN-2 冷启动枚举）、授权链（用户 2026-11-06 + Codex 裁决）、UNFREEZE 载体路径。
2. **§4 capability**：新增 `source.sync.enumerate/1`，**只进 `core.ping` 的 capabilities 列表**；C-17 的 Capabilities DTO 字段集合保持恰好 7 项，不得扩成 8；旧 Core 不公告 → Host fail-closed（typed `CORE_CAPABILITY_MISSING`），不得以 UNKNOWN_COMMAND 探测。
3. **§5.1 命令目录**：新增只读命令 `source_list_scan_targets`（Core app channel，Host 内部直连；**不**登记 HostCommandRegistry/C-07，不新增 UI 命令面）；入参 `{}`（closed shape，拒未知键）；出参 `ScanTargets`。
4. **§5.2 DTO**：`ScanTarget` = `{source_id, registry_id, generation, source_kind, identity_digest, project_ids[]}`（**去掉**草案里的 `identity_facts`；补 `source_kind`；`version` 不是 Core 事实，排除）；`ScanTargets` = `{targets: ScanTarget[]}`（去重、稳定排序键 = source_id；>上限时 typed skip 规则按 §5.3 冻结）。
5. **§5.3 守卫**：只读、零 DB 写、不建 plan/apply；`source_id` 权威来自 Core `sources`；`identity_digest` = `identity_digest_of(location facts)`（model.py:255-268）；缺失/损坏 location → 该 target typed skip（不伪造 identity）；registry 缺失/撤销 → Host 侧 fail-closed；错误码**零新增**（复用 C-17 §8 闭集）。
6. **§9 P3/P7/P8**：同步该命令的权限/审计/无副作用声明与 P 条款。
7. **冻结记录与矩阵**：`doc/plan/FEA-CONTRACT-FROZEN-C17.md` 更新 sha256 与修订记录；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 的 C-17 行由 `DRAFT` 更正为 `FROZEN v1.1`；`verify_pins.ps1` **仍 18 pins**（pin #18 重算）；其余 17 份契约字节不变。

### Out
- Core/Host 运行时实现、SQLite schema/迁移、依赖、M2-C1/C-16/C-15/C-06 字节、UI/通知、watcher、真实数据；push。

## Acceptance Criteria

- [x] **AC1 UNFREEZE 提案**：`doc/reviews/CONTRACT-UNFREEZE-<DATE>-C17.md` 写明触发、授权链、逐节 diff、pins/冻结记录/矩阵更新清单、风险与回退条件；由独立 fresh subagent 做 byte-level 复核并 APPROVE（记录 session）。 <<MET>>
- [x] **AC2 契约字节**：C-17 v1.1 仅改 §0/§4/§5.1/§5.2/§5.3/§9 与修订记录；`ScanTarget` 字段与 scope 冻结一致（无 `identity_facts`，含 `source_kind`）；无新错误码；Capabilities DTO 7 项不变；旧 Core fail-closed 语义保留。 <<MET>>
- [x] **AC3 重冻与 pins**：冻结记录 sha256 更新并与其实际字节一致；矩阵 C-17 行 = FROZEN v1.1；`verify_pins.ps1` **18/18 PASS**；其余 17 契约与 ADJ-001 字节零 diff。 <<MET>>
- [x] **AC4 治理**：`check.ps1`（默认与本卡）PASS；STATUS/PLAN/LEDGER 指针更新；UNFREEZE 提交只含本卡范围文件；未 push；证据 `verification/FEA-11-SCAN-2-PREREQ-1/**`。 <<MET>>
- [x] **AC5 后续交接**：在 `FEA-11-SCAN-2` 卡登记"契约已冻结（commit/sha）"，实现释放点由 DSH 在重冻后固定；WATCH-1 不同时释放。 <<MET>>

## 允许修改范围

frontmatter `allowed_paths` 为准；只做契约/冻结记录/矩阵/UNFREEZE 载体/证据/卡。

## 禁止范围

不改其他 17 份冻结契约与 ADJ-001 字节；不改 schema/migration/依赖；不碰 Core/Host 生产代码；不 push；不得以实现会话自审契约复核。

## 测试要求

| 计划测试 | 命令/方法 | 环境 | 期望 | 证据路径 |
|---|---|---|---|---|
| 契约 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 仓库根 | **18/18 PASS** | `verification/FEA-11-SCAN-2-PREREQ-1/logs/pins.log` |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1`（含 `-TaskPath`） | 仓库根 | PASS | `verification/FEA-11-SCAN-2-PREREQ-1/logs/gates.log` |
| 字节范围 | `git diff --name-only <base>..<head> -- doc/plan doc/contracts` | 仓库根 | 仅 C-17/冻结记录/矩阵/载体 | `logs/scope-diff.log` |
| 独立复核 | fresh subagent byte-level（工作树最终字节） | 只读 | APPROVE | `doc/reviews/CONTRACT-UNFREEZE-*-C17-review.md` |

## 依赖、风险与阻塞

- 依赖：FEA-11-SCAN-1 done（`7080167e1`）；SCAN-2 scope review（READY-WITH-UNFREEZE）；DSH 裁决 B1/S-1②/S-2/S-4 已落地。
- 风险：①C-17 是 18 pins 之一，重冻需独立 byte-level 复核与 pins 重算；②Capabilities DTO 7 项约束不得被违反（新 capability 只进 `core.ping` 列表）；③S-1 的 registry 语义未被本卡解决（limitation 保留）；④若独立复核 CHANGES，按最小修订重出载体并 r2 复核。
- 阻塞：无；本卡 ready。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md | 7451bfaaa | d501434c903d62e3c14871a62b233fa130a388a4c5dab072b8f42afe2f3f6f43 | CANONICAL |
| EV-02 | AC2 | doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md | 7451bfaaa | aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59 | CANONICAL |
| EV-03 | AC3 | doc/plan/FEA-CONTRACT-FROZEN-C17.md | 7451bfaaa | e0c6e7b87a51b830251a852bf2e96775d03ac76eebe085246f48d9dcc41c146c | CANONICAL |
| EV-04 | AC3 | doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md | 7451bfaaa | 4f93ddbc55012ce581f46822808d92e1b32dac1119daa60743ba4abd7d8a0a2a | CANONICAL |
| EV-05 | AC3 | verification/FEA-11-SCAN-2-PREREQ-1/logs/pins.log | - | 022ae2cf2cc2f9c392f7dc2b8d0f9edd6cce2342fd1ebdeeaf4f8724f660728b | CANONICAL |
| EV-06 | AC4 | verification/FEA-11-SCAN-2-PREREQ-1/logs/gates.log | - | 4b38d3631acf9be16af4d5423747e9975560875519001b35dc049341c2480dc7 | CANONICAL |
| EV-07 | AC4 | verification/FEA-11-SCAN-2-PREREQ-1/logs/gates-taskpath.log | - | 4b38d3631acf9be16af4d5423747e9975560875519001b35dc049341c2480dc7 | CANONICAL |
| EV-08 | AC4 | verification/FEA-11-SCAN-2-PREREQ-1/logs/scope-diff.log | - | c3d9152c1ed234d48c1f0af6c997fd2f02a898e0a95eca5a2c9084efcabdedb1 | CANONICAL |
| EV-09 | AC1 | doc/reviews/FEA-11-SCAN-2-PREREQ-1-c17-review.md | - | 28241e3bae8c1605a2e46573168e33b62bd5397c97f713a61a0f21d79668da74 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树） | NOT_APPLICABLE | — | — | 未创建独立 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无仓外临时资源 |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-12\`（Codex 裁决/scope review 输入） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-12` | G:\CODEX\New Manga.workspace\FEA-12\codex-next-task.md | 上游决策输入，只读；不清理 |

## Closeout Record

- Closeout date / DSH：2026-11-06 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；delivery_head / integration_commit = **`7451bfaaa`**（UNFREEZE 提交：载体 + C-17 v1.1 + 冻结记录 + 矩阵；main 线性集成）。
- Review：独立 fresh subagent byte-level **APPROVE**（P0/P1/P2=0；P3×6 已按 §1B/矩阵元数据修正或登记 residual；session `1326c586…`；报告 `doc/reviews/FEA-11-SCAN-2-PREREQ-1-c17-review.md`）。
- 契约定稿：C-17 **v1.1** sha256 `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59`；三指纹见冻结记录 §1/§1B；`verify_pins.ps1` **18/18 PASS**；其余 17 契约与 ADJ-001 零 diff；无 schema/migration/依赖；M2-C1 无增量。
- AC 定稿：AC1–AC5 全 MET。
- 保留项（如实）：P3-3 `source_kind` 用 ID 而非五值枚举（实现卡须对未知值 fail-closed，必要时另走 additive）；P3-4 `project_ids` 沿用 1..20（实现卡 AC 写明共享源 >20 books 不进 targets、不静默截断）；P3-6 SCAN-2 卡旧 DTO 示例已在冻结实现卡时替换。
- 后续：`FEA-11-SCAN-2` 实现卡由 DSH 冻结并释放（Core 枚举命令 + Host registry 核验/铸造 live grant + App 触发刷新；AC-S2-1…9；S-1②/S-2/S-4 limitation 登记）；WATCH-1 不同时释放。
- 删除、迁移、归档数量/字节数：0。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态。
