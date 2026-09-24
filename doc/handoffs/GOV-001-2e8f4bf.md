---
task_id: GOV-001
author: Codex
recipient: DeepSeek Harness
base_commit: 1e8cb1157c987945316351728f725073b8b109f9
delivery_head: 2e8f4bf951ad8a16af50300463f990d325b768e6
status: in_review
---

# Handoff — GOV-001 Architecture Decision Registration Gate

## 交付结果

用户已确定的 React + TypeScript + Tauri + Python Core 未来目标记录于 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。`REBASELINE_PLAN` 登记 M2 `PLANNED / NOT_RELEASED` 和唯一审计型 successor；`STATUS` 保留 T3.2.1 唯一 Active 产品 Task；Index/Roadmap/AGENTS 提供当前与目标边界导航。交付 commit `2e8f4bf951ad8a16af50300463f990d325b768e6` 基于 `1e8cb1157c987945316351728f725073b8b109f9`。改动路径为 `AGENTS.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、新 `doc/tasks/GOV-001.md`。本 Handoff 和 Task 状态回填是后续文档提交。

AC1～AC4 的登记、范围与文件保护自查完成；AC5 的非作者 Review 和集成尚未运行。目标技术路线不再重新选型。当前 T3.2.1 Gate、REPAIR-13、历史 Task/Handoff/Review/Verification 均未改写。没有产品代码、测试、打包、依赖、Schema、React/Tauri 初始化改动。

## 验证证据

| 场景 | 实际命令/步骤 | 环境与 commit | 结果 | 证据 |
|---|---|---|---|---|
| 基线 | `git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD; git status --short; git worktree list; git remote -v` | 主工作树，2026-09-25，`1e8cb11` | PASS；主工作树既存 1 tracked dirty path、35 untracked entries 均标 `PRE_EXISTING_WORKTREE_CHANGE`；origin 为 GitHub 仓库 | [GOV-001 Task](../tasks/GOV-001.md) 运行记录；固定 base Git 对象 |
| 差异空白 | `git diff --cached --check` before delivery commit | 隔离 worktree，`1e8cb11..2e8f4bf` | PASS，exit 0 | Git commit `2e8f4bf` |
| 变更范围 | `git diff --cached --name-only` before delivery commit；逐路径与 Task allowed paths 比较 | 隔离 worktree，`1e8cb11..2e8f4bf` | PASS；7 个路径均在范围内，无受保护路径 | Git commit `2e8f4bf` |
| 文档导航 | 逐一解析六个被改 Markdown 文件的本地相对链接并检查目标存在 | 隔离 worktree，delivery 工作树 | PASS；无断链 | 本 Handoff 与 delivery 文件 |
| 非作者 Review | DeepSeek Harness 固定 base/head 审查 | 尚未安排独立执行 | NOT_RUN | 后续新 Review 报告 |
| 集成 | Review approved 后 Codex 复核、集成并回填 STATUS/Task | 尚未执行 | NOT_RUN | 后续集成 commit |

## 接收方式

Review branch=`codex/architecture-decision-registration`；worktree=`G:/CODEX/New Manga.worktrees/architecture-decision-registration`。审查固定交付 `2e8f4bf951ad8a16af50300463f990d325b768e6`，并核对其后仅追加本 Handoff 和 Task 状态的文档 commit。Reviewer 以单独 Review 文件记录结论，不改作者文档。核查用户决策忠实度、CURRENT_REALITY / TARGET_INTENT、历史事实、T3.2.1 Gate、授权、Headless、SQLite、IPC、大型二进制与 parity。若需要修订，返回 `changes_requested`；批准后由 Codex 集成，届时才将 GOV-001 标 `done`。

## 下一任务建议

- Task / 标题：M2 Discovery-1 — Headless & Qt Coupling Audit，`research / audit`；仅在 AD-001 非作者 Review approved、Codex 集成且新 Task 冻结后可释放。不是当前 implementation authorization。
- Agent / Reviewer：推荐 DeepSeek Harness 为研究 Owner，Codex 为非作者 Reviewer/Integrator；二者职责不同。若 DeepSeek Harness 正在审查 GOV-001，先完成当前 Review，再决定是否承担新 Task。
- Recovery point：仓库=`G:/CODEX/New Manga`；本 Handoff 固定 delivery=`2e8f4bf951ad8a16af50300463f990d325b768e6`，审计的实际 base 应在 AD-001 集成后由 Codex 固定；审计 branch/worktree **待 Codex 创建**，不得用此作者 worktree 开工。
- Scope：只读审计 `src/domain`、`src/application`、`src/ports`、`src/infrastructure`、`src/bootstrap`、`src/ui`；可在后续 Task 明确授权新研究报告、Handoff 和验证清单路径。无共享接口、Schema 或依赖变更授权。
- 禁止范围：不修改 `src/**`、`tests/**`、`packaging/**`、依赖、Schema、产品 QML；不建 React/Tauri/IPC 实现；不改 T3.2.1 Gate 或历史证据。若发现修复需求，仅登记后续候选。
- Deliverables：带文件行号和运行证据的 Qt coupling / headless / SQLite writer 矩阵，逐项分类 `KEEP`、`DECOUPLE`、`REPLACE`、`LEGACY`、`UNVERIFIED`，列出可复用 Core、风险与候选后续切片。
- Verification：在新 Task 的固定 base 上执行 `rg -n 'PySide6|QObject|QImage|QPdfWriter|sqlite3|connect' src/domain src/application src/ports src/infrastructure src/bootstrap src/ui`，逐处复核调用链；按 Task 约定记录命令、环境、head、证据、未验证项与非作者 Review。Gate 为矩阵覆盖上述六棵目录及指定 Qt/SQLite/headless 问题，Review approved 后由 Codex 集成研究结论。不得将 grep 命中直接判为需替换。
- 可直接转发给 Owner 的指令：待 AD-001 Review approved 且 Codex 集成后，请在 Codex 新建并登记的 M2 Discovery-1 worktree、branch 和固定 base/head 上执行只读 Headless & Qt Coupling Audit。审计 `src/domain`、`src/application`、`src/ports`、`src/infrastructure`、`src/bootstrap`、`src/ui` 的 PySide6 imports、QObject、QImage/QPdfWriter、Qt compositor/layout/font、Webtoon tile decoding、importing、bootstrap engine coupling、SQLite writer paths 和 headless entry feasibility。交付带证据的 `KEEP/DECOUPLE/REPLACE/LEGACY/UNVERIFIED` 矩阵、新研究报告和 Handoff；记录实际命令、环境、未验证项。不要修改产品代码、测试、依赖、Schema、T3.2.1 或历史证据，也不要初始化 React/Tauri/IPC。请由 Codex 非作者 Review；Review 前不要把研究结论视为实现授权。

## 风险与遗留

- T3.2.1 Legacy Closure 投资范围为 `USER_DECISION_REQUIRED`；用户裁决前 Gate 保持原范围。
- React UI 主责为 `USER_DECISION_REQUIRED`；本 Task 不调整 Qoder/Zcode/Codex/DeepSeek Harness 角色。
- `09_COLLABORATION.md` 的“无 remote”与当前 `git remote -v` 不符，标为 `DOCUMENT_DRIFT`；该文件不在本 Task 修改范围。
- 现有 D02/D05/D07/D08 的 PySide6/QML 目标措辞由未来独立 Architecture Documentation Rebaseline 处理；本次决策登记不改写其历史内容。
