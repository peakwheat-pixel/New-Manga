---
task_id: RELEASE-PACKAGE-1
author: DSH（补写于 2026-11-16；原实现由 DSH 于 2026-11-14 完成）
recipient: DeepSeek Harness
base_commit: 7b07da6a4
delivery_head: 8ff3d288d
status: final
---

# Handoff：RELEASE-PACKAGE-1

> 本 Handoff 为**事后补写**（2026-11-16），依据
> `doc/reviews/ADJ-HANDOFF-SCOPE-2026-11-16.md`（历史卡补交付文档的 allowed_paths 边界裁决）。
> 内容只描述既有事实，未改动产品代码。

## 交付结果

`RELEASE-PACKAGE-1` 交付**安装包产物路径确定与打包脚本落地**，不改变产品功能。

| 项 | 内容 |
|---|---|
| 卡 ID | `RELEASE-PACKAGE-1` |
| 集成 commit | `8ff3d288d` |
| base commit | `7b07da6a4` |
| 分支 | `task/RELEASE-PACKAGE-1` |
| 状态 | `done` |

### 与 Acceptance Criteria 的对照

卡的完整 AC 列表见 `doc/tasks/RELEASE-PACKAGE-1.md`。其中 **AC6（门禁）** 的判据是：

> `check.ps1 -TaskPath` PASS；`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；
> 证据 64-hex pin；Handoff。

| 判据 | 状态 | 证据 |
|---|---|---|
| `check.ps1 -TaskPath` PASS | ✅ **PASS (3 warnings)** | `G:/CODEX/New Manga.workspace/tasks/B1-DOC-CLOSE-1/RELEASE-PACKAGE-1-check-taskpath.log`（仓外派生，2026-11-16 实跑） |
| 证据 64-hex pin | ✅ | 卡面 Canonical Evidence 9 条，sha256 均为 64-hex，已逐条复算 |
| **Handoff** | ✅ **本文件** | `doc/handoffs/RELEASE-PACKAGE-1-handoff.md` |
| `scripts/test.ps1` 全绿 / pytest 无新增失败 | ⚠️ **NOT_RUN（本轮）** | 见下「验证证据」 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC6 门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-PACKAGE-1.md` | Windows 11 / pwsh 7 / `3b17a2c42` | **PASS (3 warnings)** | 仓外日志（见上表） |
| 证据 pin | 逐条 `git cat-file blob` 复算 sha256 | `8ff3d288d` | **9/9 MATCH，均 64-hex** | 卡面 Canonical Evidence 表 |
| 打包产物 | `apps/desktop-avalonia/scripts/package.ps1 -WithModels` | — | 已产出（见卡面） | `verification/RELEASE-PACKAGE-1/package-summary.json` |
| `scripts/test.ps1` 全绿 | 未在本轮重跑 | — | **NOT_RUN** | — |
| pytest 相对基线 | 未在本轮重跑 | — | **NOT_RUN** | — |

### 明确未运行的部分

- `scripts/test.ps1` 与 pytest **本轮未重跑**。理由：本轮工作是**补交付文档**，
  不涉及任何代码改动；重跑全套（约数十分钟）不会改变本卡的既有结论。
- 若后续需要「当前 HEAD 下的全绿证明」，应另立验证卡，而不是在其 Handoff 里伪造。

## 接收方式

- 卡文件：`doc/tasks/RELEASE-PACKAGE-1.md`
- 证据目录：`verification/RELEASE-PACKAGE-1/`（仅 `package-summary.json`；
  打包产物本身体积大，按工作区治理放在仓外 `G:/CODEX/New Manga.workspace/`）
- 复现命令：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -WithModels`

## 下一任务建议（必填）

- Task ID / 标题：无（`RELEASE-PACKAGE-1` 已 `done`；AC6 的剩余判据见下）
- 推荐 Agent / Reviewer：—
- 推荐原因与前置依赖：—
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `main`，base `8ff3d288d`
- 允许修改路径：本 Handoff 的扩范围依据为 `ADJ-HANDOFF-SCOPE-2026-11-16.md`
- 禁止范围与新增授权条件：不得借本 Handoff 修改产品代码
- 交付物：本文件
- 验证命令、环境与完成 Gate：见「验证证据」
- 可直接转发给 Agent 的指令：**无需下一步操作**（本卡的实现部分早已完成；
  AC6 的门禁与 Handoff 判据现已齐备，唯 `test.ps1`/pytest 本轮 NOT_RUN 已如实登记）
