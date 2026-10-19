---
id: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
title: Resource Manifest 同源与空目的地语义
kind: governance/checker
governance_version: 2
status: ready
approval: codex_release_20261019_after_P19-UI-MANIFEST-VIEW-1_closeout
suggested_owner: Antigravity
owner: antigravity
reviewer: dsh
depends_on: [GOV-RESOURCE-MANIFEST-JSON-1]
base_commit: 0393ce44b08dd1562d7c404ce911d84934a8f54f
branch: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
worktree: G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
allowed_paths:
  - tools/governance/check.ps1
  - tools/governance/tests/
  - verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/
  - doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md
  - doc/handoffs/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-*.md
  - doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-*.md
---

# GOV-RESOURCE-MANIFEST-SAME-LOCATION-1：Resource Manifest 同源与空目的地语义

## 来源与目标

`P19-UI-MANIFEST-VIEW-1` 在修复外部清单引用格式后，使 checker 首次可达 6 个 destination 校验结果。其中 5 个 `destination_path` 是同源位置说明，不是可以直接交给路径解析器的文件系统路径：

- `Same ignored target/dist locations in this worktree`
- `Same source location`
- `Same shared build environment`
- `Same local cache location`
- `Same main-repository paths`

已集成的 `GOV-RESOURCE-MANIFEST-JSON-1` 提供外部 JSON Manifest 读取、schema 校验及路径检查；它没有定义上述同源标记、空字符串或 `-` 的解释。本 Task 为 checker 增加限缩、可审计的同源语义，且不修改源 JSON、schema 或 P19 历史文件。

## Acceptance Criteria

- [ ] **AC1 同源与空值解析**：外部 JSON Resource Manifest 中，仅将上述五个已核实的 `Same ...` sentinel、空白/空字符串及字面 `-` 作为同源标记。将其解释为该行 `source_path` 并对 source 运行现有路径解析/存在性校验，或明确跳过 destination 存在性校验并输出可审计 note；优先采用 source-path 回退并验证 source。不得把 sentinel 文本本身传给 `Test-Path`。
- [ ] **AC2 note 可追溯**：对每个被解释为同源的资源输出 note，至少指出资源标识、原 `destination_path` 形态及使用的 `source_path`；不得宣称存在一个不同于 source 的 destination。
- [ ] **AC3 限制匹配范围**：非同类普通散文（例如 `some other place`）不能获得同源豁免，仍按普通 destination 路径处理并失败；未知 `Same ...` 文本也不能自动扩展为通用自然语言解析，除非它精确匹配本 Task 列明的 sentinel 之一。
- [ ] **AC4 真实缺失路径继续失败**：`apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 继续按真实 destination 路径进行存在性校验；不存在时必须报错。不得把它归类成同源标记、静默豁免或记为通过。
- [ ] **AC5 离线回归用例**：扩展 `tools/governance/tests/run-resource-manifest-cases.py` 及其现有 fixtures，至少覆盖：五个同源 sentinel 通过且给出 note；空字符串/空白与 `-` 回退 `source_path` 并给出 note；存在的普通 destination 通过；非同类散文失败；真实缺失 destination 失败。用例不得访问网络或依赖用户漫画/模型数据。
- [ ] **AC6 集成前验证证据**：运行既有 Resource Manifest 离线套件及指定 Task checker，记录命令、环境、每例 PASS/FAIL、完整 stdout/stderr 与退出码。新行为不改变既有 19 个用例预期；目标 P19 源 Task 中的两项日志 SHA 差异、worktree 行尾差异、8 个未登记文件及真实缺失路径不得被宣称已清理。
- [ ] **AC7 范围与资源保护**：差异只在 `allowed_paths`；不改源 JSON、P19 Task/evidence/pins、其他 Task、schema、依赖或任何资源；Handoff 与独立 Review 固定实际 delivery/reviewed head。

## 允许修改范围

- `tools/governance/check.ps1`：仅外部 JSON Resource Manifest 的 destination 同源语义与 note。
- `tools/governance/tests/`：离线 Resource Manifest 用例与 fixtures。
- `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/`：本 Task 判别力证据。
- 本 Task 自己的 Handoff 与独立 Review 文件。

超出以上范围须先由 Codex 另行裁定，不得由 Owner 自行扩围。

## 禁止范围

- 不改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 不改 `doc/tasks/P19-UI-FIX-1.md` 正文或其 frontmatter。
- 不改 P19 的 evidence、pins、Review、Handoff 或历史日志。
- 不重钉 pin，不删除、移动、归档、重建或清理任何资源。
- 不改 schema、依赖或其它 Task；不扩大为通用自然语言解析器。
- 不把仍缺失的 isolation destination 记为通过。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 同源、空值与 note | `python tools/governance/tests/run-resource-manifest-cases.py`；逐例断言 source 回退与 note | 离线、隔离临时 fixture | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/resource-manifest-cases.txt` |
| AC3 普通散文与未知 sentinel | 同一离线套件；断言不被豁免并失败 | 离线 | NOT_RUN | 同上 |
| AC4 真实缺失 destination | 同一离线套件；用隔离根下不存在的真实路径断言失败；另保留该已知 P19 路径的预期失败事实 | 离线，不创建该路径 | NOT_RUN | 同上 |
| AC5 既有回归 | `python tools/governance/tests/run-resource-manifest-cases.py` | Python 环境与既有 19-case fixtures | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/regression.txt` |
| AC6 指定治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md` | Windows PowerShell 7 | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/task-check.txt` |

实现路径/参数若与仓库实际脚本不符，先由 Codex核对并修订 Task；不得记录未运行命令为 PASS。

## 依赖、风险与阻塞

- 硬依赖：`GOV-RESOURCE-MANIFEST-JSON-1`，已集成；本 Task base 固定为主 checkout 的 `0393ce44b08dd1562d7c404ce911d84934a8f54f`。
- 5 个同源标记来自 `verification/P19-UI-FIX-1/resource-manifest.json` 的现有原文，仅作为测试输入；禁止修改该输入。
- 真正缺失的 isolation 路径是独立资源核实事项，不能由本 Task 的 checker 语义实现推断其历史去向。
- 任何 schema 不兼容、需要改 schema/依赖或无法保留非同类散文失败行为时，停止并交 Codex 裁定。

## 交付与运行记录

- Owner：Antigravity；Reviewer：DeepSeek Harness；Codex 负责 Task 注册、集成和 closeout。
- Handoff：`doc/handoffs/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-<short-head>.md`。
- Review：`doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-<short-head>-dsh-r1.md`。
- Handoff 记录 base、delivery head、提交、实际用例/检查命令与结果、未跑项及资源保留状态。Review 固定精确 `reviewed_head`，重点复核 sentinel 白名单、普通散文和不存在路径仍失败、note 语义及禁止范围。

## Canonical Evidence

进入 `in_review` 前为 AC1–AC7 各登记当前判别力证据及含文件的 commit/SHA-256。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

Task worktree 与派生产物在 closeout 逐项核实；未知或 dirty 项保留，不按目录名推断可删除。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | `G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` | `PRESERVE_UNKNOWN` | 原路径 | closeout 时记录 HEAD/status | 未完成盘点前保留 |
| task env / agent output / exchange | `G:/CODEX/New Manga.workspace/` 对应 Task 子目录 | `NOT_APPLICABLE` 或按实核实 | — | closeout 时复核 | 不假定存在；记录检查结果 |
| test fixtures / evidence | 本 Task `tools/governance/tests/` 与 `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/` | `PRESERVE_REFERENCED` | 原路径 | closeout 时计算 | 被回归套件/证据索引引用，保留 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`: `pending`。
- `resource_closeout_status`: `pending`。
- 删除、迁移、归档数量/字节数：待核实；未获授权不操作。
- 未关闭项及保留原因：待实测后填写。
- 当前指针清理：Codex 更新 STATUS / Plan 并运行 Task checker。
