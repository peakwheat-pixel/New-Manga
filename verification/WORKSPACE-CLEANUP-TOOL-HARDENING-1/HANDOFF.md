---
handoff_id: HANDOFF-WORKSPACE-CLEANUP-TOOL-HARDENING-1
task_id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
author: workspace-hardening (DSH)
reviewer: Codex
status: in_review
resubmission: 2
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
delivery_head: dbd6cbf5f3afa0d38bb3aa7b869198c4209f4499
previous_delivery: 21715c5c0（内容 head cf7d2d46d，Review changes_requested）
date: 2026-10-21
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1
branch: dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1
---

# WORKSPACE-CLEANUP-TOOL-HARDENING-1 Handoff（Resubmission 2：Review F-01…F-07 返修）

> 本文件是 Handoff，不是 Review，不是批准，不是关闭。任务状态仍为 `in_review`。
> 本 Task 不执行任何真实 apply / 删除 / 移动 / 分支清理 / GC / prune / push；不把本文件或任何 Review
> 当作对历史越界删除的追认。提交顺序为 **先冻结 evidence commit `dbd6cbf5f`，再由 Task 记录 commit 引用它**。

## 0. Review 返修对照（changes_requested @ `21715c5c0`）

| 编号 | Review 结论 | 本次修复 |
|---|---|---|
| F-01（P1） | 声明经 junction 时真实目标可能进删除候选 | 声明入索引时解析真实路径：`Declaration.real_normalized`；保护索引同时登记词法路径与真实目标，alias 声明记 `DECL_ALIAS_REAL_TARGET` warning；新增真实入口夹具（junction 声明 → 真实目标候选 REJECT + alias 候选 REJECT）与 guard-core 单测 |
| F-02（P1） | 声明扫描只读 tracked 文件 | `scan_repo_declarations` 增加 `git ls-files --others --exclude-standard`：`doc/tasks`/`verification` 内非忽略 untracked `.md/.json` 一并扫描；untracked 声明解析失败 → 完整性错误整态拒绝；真实仓库扫描 7351 tracked + 1504 untracked 声明文件（1855 declarations） |
| F-03（P1） | destination 解析失败被降为 warning | 新增 `is_path_like()` 明确规则：占位符跳过；无路径语法的说明文字 → `DECL_DESTINATION_PROSE` warning（允许）；path-like 但不可解析 → `DECL_DESTINATION_UNRESOLVED` 完整性错误并拒绝清理。真实仓库新增 7 条此类错误（fail-closed），34 条说明文字 warning |
| F-04（P2） | `--out` 可位于候选目录内 | 新增 `ensure_out_outside_candidates()`：apply 前按词法 + realpath 比较，`--out` 等于/位于任一候选（含经 alias 指向）→ `OUT_INSIDE_CANDIDATE` exit 2，且在写清册/删除之前拒绝；两个路径删除工具均接入；新增隔离夹具（普通 inside + junction inside） |
| F-05（P2） | Canonical Evidence commit 标注错误 + manifest 失配 | 重新按“先冻结 evidence，再提交引用它的 Task 记录”执行：evidence commit `dbd6cbf5f` 包含全部证据字节；Task 记录的 commit pin 全部指向 `dbd6cbf5f` 且 SHA-256 与该 commit 字节一致；`governance-check.log`/`manifest.sha256` 为日志/清单类过程证据，以 SHA-256 pin 登记；manifest 在最终 governance 日志确定后重算并提交 |
| F-06（P2） | AC4 部分失败注入未走真实入口 | 新增 `run_main()`：stash 失败与权限拒绝均通过工具真实 CLI 入口（`main(argv)`，含 argparse/报告/退出码/apply 门禁）验证；重复 inventory identity 由“去重”改为显式拒绝 `INVENTORY_DUPLICATE_IDENTITY` exit 2 |
| F-07（P3） | 治理归因不准确 | 见 §6：5 个 error 的准确归因是“worktree 缺少主仓未跟踪的 drafts/archive 内容，且存在既有 stale `archive/history` 引用”，不是“base 早于 b63”；4 个 warning 已区分 3 个仓库级 + 1 个本 Task evidence-dir warning |

## 1. 交付内容

| 文件 | 变更摘要 |
|---|---|
| `tools/governance/clean_workspace.py` | fail-closed guard core（声明真实路径保护、untracked 声明扫描、destination 完整性、`--out` 防自删、清册/release-window/replay） |
| `tools/governance/remove_worktrees.py` | 路径身份保护、非标准位置拒绝、status/stash 非零拒绝、ignored 清册门禁、重复 inventory identity 拒绝、`--out` 防自删、incident replay |
| `tools/governance/archive_branches.py` | 默认 plan-only；无 `git tag -f`；bundle 不覆盖；verify 后才落盘；release-window 门禁 |
| `tools/governance/delete_branches.py` | merged 复算、归档 proof/tag/bundle verify 三重校验、release-window 门禁、无 `--force` |
| `tools/governance/consolidate.py` | 严格 Git/porcelain 解析；inspection 失败显式记录并 exit 2；复用保护索引 |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/` | 77 项 unittest（含 F-01/F-02/F-03/F-04/F-06 新增真实入口与负向夹具） |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 可复算证据生成器 |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/` | 判别力证据（§5） |
| `doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md` | AC 勾选、测试表、Canonical Evidence（commit pin = `dbd6cbf5f`）、Closeout |

**未修改**：`doc/WORKSPACE_GOVERNANCE.md`、`doc/09_COLLABORATION.md`、Plan/STATUS、其他 Task、历史 Review/清册、
`tools/governance/check.ps1`、`task_ledger.py`、主仓库。

## 2. AC1–AC7 逐项结果

| AC | 结果 | 判别力证据 |
|---|---|---|
| AC1 路径身份 + 父子覆盖 | **MET** | 规范化绝对路径；same/descendant(任意深度)/ancestor 组件边界；多来源声明并集；泛化声明 → `DECL_GENERALIZED` 拒绝；**F-01**：声明按 junction/symlink 真实目标双重保护，真实目标候选与 alias 候选均 REJECT |
| AC2 失败关闭 | **MET** | 裸/相对/`..`/glob/env/歧义、非标准表格、未知 disposition、status/stash/ls-files 非零、权限拒绝、alias/越界 → 拒绝或整态 REFUSE（exit 2）；**F-02** untracked 声明纳入扫描且解析失败即拒绝；**F-03** path-like destination 失败即完整性错误；**F-06** 重复 inventory identity 显式拒绝 |
| AC3 删除前清册 | **MET** | ignored/untracked/非 git 逐文件 size+SHA-256；超限/不可读→拒绝；无清册/未接受 → 不得 apply；`purpose_hint` 仅为提示 |
| AC4 夹具/失败注入 | **MET** | 11 类矩阵全测；**F-06** stash/权限拒绝新增真实 CLI 入口验证；重复 identity 断言 exit 2 |
| AC5 dry-run/apply 解耦 | **MET** | 默认 dry-run；apply 需 release-window + 候选集 digest 现场复算；dry-run 报告可复算；**F-04** `--out` 位于/等于/alias 指向候选 → 拒绝 |
| AC6 事故回放 | **MET** | 18 source / 15 root：两工具均 15/15 REJECT、0 删除、0 violation、18/18 覆盖；负向对照缺 SRC-02/相对 root/坏 schema → violation；replay 拒绝 `--apply` |
| AC7 回归与文档 | **MET（有限）** | 新测试 77/77 OK；既有 `test_ac_gate.py` 12/12 PASS；`run-resource-manifest-cases.py` 0/32 既存失败（范围外，如实记录）；未改治理文档 |

## 3. 关键实现规则（Review 可核对）

1. **路径身份**：`norm_abs()` 只接受绝对路径；`normcase+normpath+"/"`；裸/相对/根相对/NUL → `GuardError`。
2. **真实目标（F-01）**：声明解析后立即 `resolve_real_target()`；保护索引同时登记词法路径与真实目标；alias 声明
   记 `DECL_ALIAS_REAL_TARGET` warning；真实目标解析失败 → `REALPATH_FAILED` 拒绝。
3. **保护判定**：候选与每个保护根做 same/descendant/ancestor；descendant/ancestor 一并拒绝。
4. **泛化声明**：工作区根/managed area 根及其祖先（词法或真实）→ `DECL_GENERALIZED` 整态拒绝。
5. **声明完整性 = 整态拒绝**：任何无法解析/未知 disposition/表格非标准/path-like destination 不可解析 → exit 2，
   不产出可删除候选；说明文字 destination 只记 warning，绝不作为保护或删除依据。
6. **untracked 声明（F-02）**：`doc/tasks`/`verification` 内 `--others --exclude-standard` 的 `.md/.json` 亦扫描；
   解析失败 → 完整性错误（apply 被拒绝）。
7. **预删除清册**：git 候选 `ls-files --others [--ignored]` + 逐文件哈希；非 git 候选遍历；超限/读取失败拒绝。
8. **apply 门禁**：release-window 字段/时间窗/roots/候选集 digest/count/清册 acceptance hash；**F-04** `--out`
   位于/等于/alias 指向候选 → `OUT_INSIDE_CANDIDATE`（在写清册和删除之前拒绝）。
9. **重复候选（F-06）**：inventory 规范化后重复 → `INVENTORY_DUPLICATE_IDENTITY` exit 2，不再静默去重。
10. **回放**：ledger 严格 schema；每 root 必须有 protected source 覆盖；replay 无删除代码路径。

## 4. 运行记录（命令 / 环境 / 退出码）

环境：Windows 11（10.0.26300）、Python `C:\Python314\python.exe` 3.14.6、Git 2.52.0.windows.1；
所有命令在 worktree 内执行，`-B`/`PYTHONDONTWRITEBYTECODE=1`，无第三方依赖。原始输出与命令：
`evidence/tests.log`、`evidence/environment.json`（含每条命令 exit code 与 stdout/stderr SHA-256）。

### 4.1 新增测试（AC1–AC6）

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py
```
exit `0`；`Ran 77 tests` / `OK`；`JSON_RESULTS` 77 项全部 `ok`（0 skip）。日志：`evidence/tests.log`。

### 4.2 事故回放（AC6）

```
C:/Python314/python.exe -B tools/governance/clean_workspace.py --replay-incident <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
C:/Python314/python.exe -B tools/governance/remove_worktrees.py --replay-incident <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
```
均 exit `0`；两报告均 `candidates=15, rejected=15, deleted=0, violations=0, ok=true`，18/18 source 覆盖。

### 4.3 既有治理工具测试（AC7）

```
C:/Python314/python.exe -B tools/governance/tests/test_ac_gate.py
```
exit `0`，`12/12 cases behaved as specified`。日志：`evidence/existing-test_ac_gate.py.log`。

```
C:/Python314/python.exe -B tools/governance/tests/run-resource-manifest-cases.py
```
exit `1`，`0/32 cases behaved as expected`。**既存失败**：用例被 `check.ps1` 的 `TASK_LEDGER 已过期`
（322/13 计数不一致）等无关规则打断，属仓库状态 + 冻结范围外的 `check.ps1`/`task_ledger.py`；该测试不 import
五个加固脚本。日志：`evidence/existing-run-resource-manifest-cases.py.log`。

### 4.4 真实仓库声明审计（只读；AC1/AC2/AC6 补充）

```
C:/Python314/python.exe -B tools/governance/clean_workspace.py --audit-declarations --incident-ledger <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
```
exit `2`（**预期 fail-closed**，未删除任何文件）：扫描 7351 tracked + 1504 untracked 声明文件；
1855 declarations / 1263 保护根；**18/18 incident source 被真实仓库声明覆盖**；93 条历史声明错误
（`DECL_BARE_NAME` 57、`DECL_UNKNOWN_DISPOSITION` 9、`DECL_DESTINATION_UNRESOLVED` 7、`DECL_GENERALIZED` 6、
`DECL_RELATIVE_UNRESOLVED` 5、`DECL_ENV` 4、`FILE_UNREADABLE` 3、`DECL_RELATIVE_AMBIGUOUS` 1、
`TABLE_ROW_ARITY` 1）；122 条 warning（`JSON_NONSTANDARD` 69、`DECL_DESTINATION_PROSE` 34、
`DECL_ALIAS_REAL_TARGET` 19）。真实仓库现状下工具会**拒绝任何清理**，直到历史声明被修复或裁定。

### 4.5 真实工作区未被触碰（Gate）

`evidence/real-workspace-snapshot.json`：运行前后 HEAD 一致、worktree `git status`（排除本 Task 自身路径）一致、
ledger 的 18 source + 15 root 路径存在性一致；apply 仅在 `%TEMP%` 隔离夹具执行。

### 4.6 复算方式

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py
```
exit `0`（`evidence-ok`）重新生成并校验：新测试 exit 0、两 replay ok、真实工作区快照一致；
`evidence/manifest.sha256` 为各证据文件 SHA-256 清单（含 `governance-check.log`）。

## 5. 证据索引

| 文件 | 内容 |
|---|---|
| `evidence/tests.log` | 77 测试完整 verbose 输出 + `JSON_RESULTS` |
| `evidence/ac-coverage.json` | AC1–AC6 → 测试方法映射与实际 ok 状态；AC7 既有测试 exit codes |
| `evidence/incident-replay-clean-workspace.json` | AC6 回放报告（15 roots 逐项 REJECT + 原因） |
| `evidence/incident-replay-remove-worktrees.json` | 同上（worktree 工具） |
| `evidence/declaration-audit.json` / `.log` | 真实仓库声明审计（1855/1263、18/18、93 errors、122 warnings、exit 2） |
| `evidence/existing-test_ac_gate.py.log` | 既有 AC gate 测试（12/12） |
| `evidence/existing-run-resource-manifest-cases.py.log` | 既有 manifest 用例（0/32，既存失败） |
| `evidence/environment.json` | 平台/解释器/Git、每条命令与 exit code、stdout/stderr SHA-256、AC 覆盖、快照、失败清单 |
| `evidence/real-workspace-snapshot.json` | 真实工作区前后快照与一致性断言 |
| `evidence/governance-check.log` | check.ps1 原始输出 + exit code |
| `evidence/manifest.sha256` | 上述证据文件 SHA-256（最终日志确定后重算） |
| `tests/`、`run_evidence.py` | 测试源码与证据生成器（可复算） |

## 6. 治理检查（F-07 修正归因）

命令（worktree 内）：

```
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md
```

exit `1`，`Governance check: FAIL (5 errors, 4 warnings)`。原始输出：`evidence/governance-check.log`。

**5 个 error（均与本 Task 改动无关）**：

| # | 结论 | 准确归因 |
|---|---|---|
| 1–2 | `TASK_LEDGER 已过期：声明 322 个 Task，实际 296 个`；`声明 13 个非终态 Task，实际 2 个` | **worktree 缺少主仓库中未跟踪（untracked）的起草 Task 文件**：这些 drafts 从未进入 Git 历史，因此不随 worktree checkout 出现；`TASK_LEDGER` 声明的计数是在主仓（含未跟踪 drafts）侧生成的，与 worktree 实际 296 个不一致。**不是** `b63f22aba` 改动所致（该提交未改 TASK_LEDGER/00_INDEX/AD-001，也未加入 archive 文件）。 |
| 3–5 | `doc/00_INDEX.md` / `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 的 3 条 `../archive/history/...` 本地引用失效 | 这些 `archive/history` 内容在主仓是**未跟踪/未入库**的归档资料，worktree 中本来就不存在；引用本身是既有 stale reference。既不在本 Task allowed_paths，也未修改。 |

**4 个 warning，区分两类**：

- 仓库级 3 个：非终态 Task 计数提示、`doc/STATUS.md` 预算 80%、`doc/REBASELINE_PLAN.md` 预算 80%；
- 本 Task 1 个：`evidence_dir` 含未逐行登记的过程文件 `HANDOFF.md`、`evidence/manifest.sha256`
  （check 运行时 `governance-check.log` 尚未生成；这些文件由 §5/§6 与 Task 交付记录引用，未强行入表以避免自引用）。

**未修改 Plan/STATUS/check.ps1/task_ledger.py**；`governance-check.log` 为对该 Task 记录运行所得的最终原始输出
（此时 `EV-CHECK`/`EV-MANIFEST` 行已登记，日志中唯一未登记过程文件是 `HANDOFF.md`），随后仅按该日志与清单的
最终字节更新两行的 SHA-256 pin 并重算 manifest（无自引用），不改变任何删除授权语义；
最终治理检查由 Codex 在主仓集成后执行。

## 7. 未执行 / 残余风险

**未执行**：真实 `--apply`、任何真实删除/移动/分支清理/GC/prune/push、`--force`；未修改 Plan/STATUS/其他 Task/
历史 Review/清册/治理文档；未对真实仓库运行 normal dry-run（声明审计已 fail-closed）。

**残余风险 / 限制**：

1. **真实仓库 93 条历史声明完整性错误**（含 7 条 path-like destination）→ 工具整态拒绝清理；需另立 Task 修复声明
   或由 Codex/用户裁定，本 Task 不修改历史 Task。
2. **声明扫描刻意覆盖 1504 个非忽略 untracked 声明文件**：更保守，但真实仓库审计耗时约 9 秒、错误数上升
   （57 条 bare name 等来自 untracked drafts）；如 Codex 认为 untracked drafts 不应作为保护来源，可另立口径。
3. **共享 guard core 寄居 `clean_workspace.py`**（allowed_paths 冻结 5 个文件，无法新增 `safety.py`）。
4. **apply 仅在 `%TEMP%` 夹具验证**；release-window 记录需人工生成（无自动审批链）。
5. **进程占用检查未实现**；以清册 + 人工接受 + 无 `--force` 缓解。
6. **既有 `run-resource-manifest-cases.py` 0/32 未修复**：check.ps1/task_ledger 仓库状态问题，范围外。
7. junction 夹具在非 Windows 会 skip（本机 Windows 未 skip）。
8. 回放与审计均只读；AC6 的 15 个 root 当前状态未在本 Task 改变或恢复。
