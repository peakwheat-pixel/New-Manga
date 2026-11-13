---
id: REL-GATE-1
title: Release Gate 可执行证据补齐（GUI 冒烟 / 构建 / NOT_RUN 边界）
kind: verification
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT14-V1-MANIFEST-1]
base_commit: 903014273
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 53470bee3bcc4a29204f22070befebed813c2fcf
delivery_head: 53470bee3bcc4a29204f22070befebed813c2fcf
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REL-GATE-1
allowed_paths:
  - verification/REL-GATE-1/**
  - doc/tasks/REL-GATE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# REL-GATE-1：Release Gate 可执行证据补齐（GUI 冒烟 / 构建 / NOT_RUN 边界）

## 来源与目标

`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 维持 **BLOCKED**，缺 clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据。本 Task 在**不安装、不发布、不调用付费模型 API**的边界内，补齐可执行证据：固定 HEAD/构建、GUI 冒烟（V2 shell 隔离数据根）、发布产物生成（workspace 内，不安装）、明确 NOT_RUN 项；不改变 Release Gate 结论，不声称产品已发布。

## Acceptance Criteria

- [x] **AC1**：固定 HEAD 与构建证据（.NET 构建/app 构建、EXIT、原始输出），记录 build 环境。 <<MET>>
- [ ] **AC2**：GUI 冒烟：在隔离数据根启动 V2 shell，记录进程存活、截图/日志、EXIT 与限制；若环境无法启动，记录 BLOCKED 并保留原始 stderr。 <<PARTIAL: GUI 冒烟未执行；App 无隔离数据根入口，启动会写真实 %APPDATA% 根（本 Task 禁止）；无安装包/UIA 工具。记录 BLOCKED，不写成 PASS>>
- [ ] **AC3**：发布产物生成到 workspace（`publish.ps1` 路径策略已改）或明确 NOT_RUN；安装/卸载、真实模型 API、clean install 明确 NOT_RUN，不写成 PASS。 <<PARTIAL: S0 配方（PublishTrimmed=true）实测 EXIT 1（IL2026 ×2）；非 trimming 单文件发布 EXIT 0（62.6MB）；安装/卸载/真实模型 API/clean install 均 NOT_RUN>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决；Release Gate 维持 BLOCKED 并记录本 Task 能/不能证明的内容。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| RELGATE-BUILD-LOG-1 | AC1 | `verification/REL-GATE-1/logs/dotnet-build-sln.log` | `53470bee3bcc4a29204f22070befebed813c2fcf` | `22563DC963B7DEDEC0C1E220CEF9E00EB79178B181D476C80115A1EB5C564C35` | CANONICAL | BLOB |
| RELGATE-PUBLISH-S0-LOG-1 | AC3 | `verification/REL-GATE-1/logs/dotnet-publish-app.log` | `53470bee3bcc4a29204f22070befebed813c2fcf` | `EC36434BDFC9A46B24E40262688E8C329F0497429C8206F1BC65B8A8B65E8B36` | CANONICAL | BLOB |
| RELGATE-PUBLISH-NOTRIM-LOG-1 | AC3 | `verification/REL-GATE-1/logs/dotnet-publish-app-notrim.log` | `53470bee3bcc4a29204f22070befebed813c2fcf` | `739EEAFC1FA9CFE7CFCED12706600D2B90EAD7AEDB9C6E83EF9FF71D7D81CA49` | CANONICAL | BLOB |
| RELGATE-GUI-SMOKE-LOG-1 | AC2 | `verification/REL-GATE-1/logs/gui-smoke.log` | `53470bee3bcc4a29204f22070befebed813c2fcf` | `A2CA4F7A4B1A8F968E69765D48ED36D9EA826601A8D66CCF28DAD8EE6E77DB9A` | CANONICAL | BLOB |
| RELGATE-EVIDENCE-1 | AC4 | `verification/REL-GATE-1/evidence/rel-gate.json` | `53470bee3bcc4a29204f22070befebed813c2fcf` | `39F03FC1482215DEF055771633CBDF787A2CCB6EB50488261F74A6B488A0A83E` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/REL-GATE-1/evidence/rel-gate.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/REL-GATE-1/evidence/rel-gate.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/REL-GATE-1/evidence/rel-gate.json | 无 agent-output |
| artifact | verification/REL-GATE-1 | PRESERVE_REFERENCED | doc | verification/REL-GATE-1/evidence/rel-gate.json | 构建/发布证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/REL-GATE-1/evidence/rel-gate.json | 无 |
| exchange | - | NOT_APPLICABLE | doc | verification/REL-GATE-1/evidence/rel-gate.json | 无外部传输 |

## 结论与边界

- 构建证据成立：`dotnet build NewManga.sln -c Debug` **0 warnings / 0 errors / EXIT 0**。
- **S0 单文件发布配方当前失败**：`PublishTrimmed=true` 时 IL2026 ×2（AvaloniaXamlLoader、JsonSerializer.SerializeToElement），EXIT 1；已释放 `PUBLISH-FIX-1` 修复。
- 非 trimming 单文件发布成功（`NewManga.App.exe` 62,627,468 bytes），仅证明可生成单文件，不证明 trimming 配方可用。
- GUI 冒烟：**BLOCKED**（无隔离数据根入口；避免真实用户数据根；无安装/UIA 环境）。
- 安装/卸载、clean install、真实模型 API、完整 GUI 验收：**NOT_RUN**。
- **产品 Release Gate 维持 BLOCKED**；本 Task 不构成产品发布通过。

## 允许修改范围

- `verification/REL-GATE-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

安装/卸载/发布/上传、真实模型 API 付费调用、产品源码、契约、依赖、真实用户数据、远端写操作、历史改写。

## 测试要求

构建与 GUI 冒烟保存原始 stdout/stderr/EXIT/时间；不可运行项写 NOT_RUN/BLOCKED；不得把截图存在写成完整产品验收。
