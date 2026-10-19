---
task_id: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
author: Antigravity
recipient: Codex
base_commit: 57ac3c6ae
delivery_head: d15aae88a
status: completed
---

# Handoff：GOV-RESOURCE-MANIFEST-SAME-LOCATION-1

## 交付结果

本任务已按 `doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md` 的全部 7 条 AC 及禁止范围完成实现：

1. **AC1 同源与空值解析（达成）**：
   在 `tools/governance/check.ps1` 中，为外部 JSON Resource Manifest 增加了精确同源语义支持：
   - 仅对 5 个已核实精确 sentinel（`Same ignored target/dist locations in this worktree`、`Same source location`、`Same shared build environment`、`Same local cache location`、`Same main-repository paths`）、空白/空字符串以及字面 `-` 进行同源解释；
   - 解释为该行的 `source_path` 并输出可审计 note；
   - 优先对 source 进行路径解析与存在性校验。对 5 个已核实 sentinel，若本地 source 未实际存在（如已清理的构建缓存）则明确跳过 destination 校验；
   - 绝对不将 sentinel 文本本身传递给 `Test-Path`。
2. **AC2 note 可追溯（达成）**：
   对每个被解释为同源的资源，在 Warning/Notes 中明确输出：资源标识（如 `resource_type` 或 `source_path`）、原 `destination_path` 形态（如 sentinel 文本、`(blank)`、`-`）以及使用的 `source_path`。绝不宣称存在不同于 source 的 destination。
3. **AC3 限制匹配范围（达成）**：
   非同类普通散文（如 `some other place`）以及未知 `Same ...` 文本（如 `Same custom unknown location`）均不获得同源豁免，仍按普通 destination 处理并校验失败。
4. **AC4 真实缺失路径继续失败（达成）**：
   `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 继续作为真实 destination 进行存在性校验并明确报错失败，未被归类为同源，未被静默豁免。
5. **AC5 离线回归用例（达成）**：
   扩展 `tools/governance/tests/run-resource-manifest-cases.py` 与 `tools/governance/tests/fixtures/resource-manifest/cases.json`，在既有 19 个用例基础上新增用例 20–32（共 32 个用例），逐例断言 source 回退、note 输出与失败分支。
6. **AC6 集成前验证证据（达成）**：
   完成离线套件与指定任务治理检查，完整记录 stdout/stderr 与退出码，全部保存至 `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/`。
7. **AC7 范围与资源保护（达成）**：
   修改严格限定在 `allowed_paths`。源文件 `verification/P19-UI-FIX-1/resource-manifest.json`、P19 任务正文、pins 及其他任务未作任何修改。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC4 同源/note/限制匹配/真实缺失路径 | `python tools/governance/tests/run-resource-manifest-cases.py`<br>`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md` | Windows PowerShell 7, commit `d15aae88a` | PASS | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/resource-manifest-cases.txt` |
| AC5 离线测试用例与既有回归 | `python tools/governance/tests/run-resource-manifest-cases.py` | Python 3, commit `d15aae88a` | PASS (32/32 behaved as expected) | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/regression.txt` |
| AC6 当前任务治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md` | Windows PowerShell 7, commit `d15aae88a` | PASS (0 errors, 1 warnings) | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/task-check.txt` |
| 治理全局检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | Windows PowerShell 7, commit `d15aae88a` | PASS (0 errors, 1 warnings) | 控制台验证 |

### 目标 P19 检查变化观察

在运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md` 时：
- **改动前**：P19 在主检出上共报 9 个错误，其中 6 个为 `Resource 最终路径未验证`（5 个 sentinel + 1 个 isolation 真实缺失路径）。在当前新建 worktree 上共报 10 个错误（多 1 项行尾差异）。
- **改动后**：5 个 sentinel 相关的错误全部消除，并对应输出了 5 条清晰的同源解释 Warning/Note；真实缺失路径 `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 继续报错；整体错误数**严格减少 5 个**（主检出由 9 个降至 4 个，当前 worktree 由 10 个降至 5 个）。

### 工作树未追踪历史资料说明

按照用户指令与项目环境提示，主 checkout 中存在约 1233 个未追踪历史文件（含 `doc/WORKSPACE_GOVERNANCE.md` 及 `archive/`）。新建 worktree 由于缺乏这部分未入库文件，会引起 6 个与本任务无关的治理入口缺失错误。为确保治理检查器正常运行，将主 checkout 中的 `doc/WORKSPACE_GOVERNANCE.md` 与 `archive/` 复制到了本 worktree 运行环境，**未进行 git add、未入库、不提交**。

## 接收方式

- 分支：`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`
- 工作树：`G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`
- delivery_head：`d15aae88a`
- 验证复现命令：
  ```powershell
  python tools/governance/tests/run-resource-manifest-cases.py
  pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md
  pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md
  ```

## 下一任务建议（必填）

- **Task ID / 标题**：`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` 独立代码审查
- **推荐 Agent / Reviewer**：DeepSeek Harness (dsh)
- **推荐原因与前置依赖**：Antigravity 已在分支 `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`（HEAD `d15aae88a`）完成全部实现与 32/32 离线用例验证，按照角色分工与协作协议 §4，需要由指定 Reviewer `dsh` 进行独立代码与治理审查。
- **Recovery point**：仓库 `G:/CODEX/New Manga`，分支 `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`，reviewed_head 固定为 `d15aae88a`。
- **允许修改路径**：`doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-d15aae88a-dsh-r1.md`
- **禁止范围与新增授权条件**：不得修改源 JSON、不得修改 P19 历史任务/证据/pins、不得放宽散文或未知 sentinel 白名单。
- **交付物**：审查报告 `doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-d15aae88a-dsh-r1.md`。
- **验证命令、环境与完成 Gate**：
  ```powershell
  python tools/governance/tests/run-resource-manifest-cases.py
  pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md
  ```
  要求 32/32 用例 PASS，且 Task 检查 PASS。
- **可直接转发给 Agent 的指令**：
  ```markdown
  请审查任务 GOV-RESOURCE-MANIFEST-SAME-LOCATION-1。工作树 G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1，分支 GOV-RESOURCE-MANIFEST-SAME-LOCATION-1，reviewed_head d15aae88a。审查文件输出至 doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-d15aae88a-dsh-r1.md。重点核验：AC1-AC4 同源 sentinel 白名单及回退 note、普通散文与真实缺失路径（isolation）仍失败、不修改源 JSON/P19 历史资源、既有 19 用例预期不破坏。
  ```

## 风险与遗留

1. **真实缺失路径未予豁免**：`apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 继续作为真实 destination 路径在 check.ps1 中报错，符合 AC4 硬约束，留待后续独立资源处置。
2. **P19 历史文件与 schema 保持原样**：源 JSON `verification/P19-UI-FIX-1/resource-manifest.json` 与 P19 历史任务正文未做任何改动。
3. **Task frontmatter status 说明**：本 Task 已在 `d15aae88a` 完成实现与交付，Canonical Evidence 和 Resource Manifest 表格已全部填齐。由于 `doc/REBASELINE_PLAN.md` 当前 DAG 第 38 行将本任务登记在 `READY 节点：` 中（该文件属 Codex 权限，非 Owner 允许修改路径），若在分支中提前修改为 `status: in_review` 会触发检查器第 241 行的 READY DAG 约束并使离线用例全部报无关失败。因此本分支保持 `status: ready`，以保证离线套件 32/32 全绿（退出码 0）及治理检查 PASS（退出码 0），交由 Codex 在接收 Handoff 并更新 Plan（将本任务移至 in_review 节点）时统一推进为 `status: in_review`。
