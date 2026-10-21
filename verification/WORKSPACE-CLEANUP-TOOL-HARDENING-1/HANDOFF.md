---
handoff_id: HANDOFF-WORKSPACE-CLEANUP-TOOL-HARDENING-1
task_id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
author: workspace-hardening (DSH)
reviewer: Codex
status: in_review
resubmission: 3
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
evidence_commit: 30946decf1f3f6f9f66ce53043f543b490f8b377
previous_deliveries: 21715c5c0（r1 changes_requested）、beeac02af（r2 changes_requested）
date: 2026-10-21
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1
branch: dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1
---

# WORKSPACE-CLEANUP-TOOL-HARDENING-1 Handoff（Resubmission 3：F-02 malformed JSON + F-05 证据字节冻结）

> 本文件是 Handoff，不是 Review，不是批准，不是关闭。任务状态仍为 `in_review`。
> 本 Task 不执行任何真实 apply / 删除 / 移动 / 分支清理 / GC / prune / push；不把本文件或任何 Review
> 当作对历史越界删除的追认。**提交顺序：evidence commit `30946decf`（冻结代码/测试/证据/最终日志/manifest）
> → Task-only 记录 commit（引用该 evidence commit）。**

## 0. Review 返修对照

### r1（`21715c5c0`，changes_requested）

| 编号 | 结论 | 修复 |
|---|---|---|
| F-01 | 声明经 junction 时真实目标可能进候选 | 声明同时按词法与真实目标登记保护；真实入口夹具 + 单测 |
| F-02 | 声明扫描只读 tracked 文件 | 扫描非忽略 untracked `.md/.json`；解析失败整态拒绝 |
| F-03 | destination 解析失败降为 warning | path-like 不可解析 → 完整性错误；说明文字有明确规则 |
| F-04 | `--out` 可位于候选内 | apply 前按词法 + realpath 拒绝 `OUT_INSIDE_CANDIDATE` |
| F-05 | 证据 commit/sha 失配 | 改为 evidence commit + Task-only 记录的顺序（r2 再次加严） |
| F-06 | 失败注入未走真实入口 | stash/权限走 `main(argv)`；重复 identity 拒绝 |
| F-07 | 治理归因不准确 | 改为“worktree 缺少主仓未跟踪 drafts/archive 内容 + 既有 stale 引用” |

### r2（`beeac02af`，changes_requested，本轮修复）

| 编号 | 结论 | 修复 |
|---|---|---|
| F-02 | malformed JSON 仅检查字面 `PRESERVE`，MIGRATE/ARCHIVE 可能漏保护 | **删除启发式**：扫描范围内任何 JSON 解析失败一律 `JSON_PARSE` 完整性错误（整态拒绝）。新增 MIGRATE / ARCHIVE / 无 marker 三个 malformed JSON 夹具（均 exit 2、候选保留） |
| F-05 | evidence 冻结与 commit 字节不一致（`governance-check.log` 因 CRLF 与 blob 不一致；manifest 10/11） | `governance-check.log` 显式 **LF 归一**后写入；manifest 覆盖最终日志与全部证据（11 项）；evidence commit `30946decf` **同时包含**最终日志与最终 manifest；27 条证据行全部 pin `30946decf`，SHA-256 等于该 commit 的 **Git blob 字节**（逐项校验，无 SHA-only 行、无自引用） |

## 1. 交付内容

| 文件 | 变更摘要 |
|---|---|
| `tools/governance/clean_workspace.py` | fail-closed guard core（真实路径保护、untracked 声明扫描、JSON 解析失败一律拒绝、destination 完整性、`--out` 防自删、清册/release-window/replay） |
| `tools/governance/remove_worktrees.py` | 路径身份保护、非标准位置拒绝、status/stash 非零拒绝、ignored 清册门禁、重复 identity 拒绝、`--out` 防自删、incident replay |
| `tools/governance/archive_branches.py` | 默认 plan-only；无 `git tag -f`；bundle 不覆盖；verify 后落盘；release-window 门禁 |
| `tools/governance/delete_branches.py` | merged 复算、归档 proof/tag/bundle verify 三重校验、release-window 门禁、无 `--force` |
| `tools/governance/consolidate.py` | 严格 Git/porcelain 解析；inspection 失败显式记录并 exit 2；复用保护索引 |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/` | 80 项 unittest（r1/r2 新增真实入口、junction、untracked、destination、malformed JSON、`--out` 夹具） |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 可复算证据生成器 |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/` | 判别力证据（§5） |
| `doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md` | AC 勾选、测试表、Canonical Evidence（27 行 pin `30946decf`）、Closeout |

**未修改**：`doc/WORKSPACE_GOVERNANCE.md`、`doc/09_COLLABORATION.md`、Plan/STATUS、其他 Task、历史 Review/清册、
`tools/governance/check.ps1`、`task_ledger.py`、主仓库。

## 2. AC1–AC7 逐项结果

| AC | 结果 | 判别力证据 |
|---|---|---|
| AC1 路径身份 + 父子覆盖 | **MET** | 规范化绝对路径；same/descendant(任意深度)/ancestor 组件边界；多来源并集；泛化声明拒绝；junction 声明的真实目标与 alias 候选均 REJECT |
| AC2 失败关闭 | **MET** | 裸/相对/`..`/glob/env/歧义、非标准表格、未知 disposition、status/stash/ls-files 非零、权限拒绝、alias/越界 → 拒绝或整态 REFUSE；untracked 声明纳入扫描；**JSON 解析失败一律完整性错误**（MIGRATE/ARCHIVE 不再漏保护）；path-like destination 失败即错误；重复 inventory identity 拒绝 |
| AC3 删除前清册 | **MET** | ignored/untracked/非 git 逐文件 size+SHA-256；超限/不可读→拒绝；无清册/未接受 → 不得 apply；`purpose_hint` 仅为提示 |
| AC4 夹具/失败注入 | **MET** | 11 类矩阵 + stash/权限真实 CLI 入口 + 重复 identity + MIGRATE/ARCHIVE malformed JSON 反例（均断言拒绝/0 删除） |
| AC5 dry-run/apply 解耦 | **MET** | 默认 dry-run；apply 需 release-window + 候选集 digest 现场复算；dry-run 报告可复算；`--out` 位于/等于/alias 指向候选 → 拒绝 |
| AC6 事故回放 | **MET** | 18 source / 15 root：两工具均 15/15 REJECT、0 删除、0 violation、18/18 覆盖；负向对照缺 SRC-02/相对 root/坏 schema → violation；replay 拒绝 `--apply` |
| AC7 回归与文档 | **MET（有限）** | 新测试 80/80 OK；既有 `test_ac_gate.py` 12/12 PASS；`run-resource-manifest-cases.py` 0/32 既存失败（范围外，如实记录）；未改治理文档 |

## 3. 关键实现规则（Review 可核对）

1. **路径身份**：`norm_abs()` 只接受绝对路径；`normcase+normpath+"/"`；裸/相对/根相对/NUL → `GuardError`。
2. **真实目标（F-01）**：声明解析后 `resolve_real_target()`；词法路径与真实目标同时登记保护；alias 声明记
   `DECL_ALIAS_REAL_TARGET` warning；解析失败 → `REALPATH_FAILED` 拒绝。
3. **保护判定**：候选与每个保护根做 same/descendant/ancestor；descendant/ancestor 一并拒绝。
4. **泛化声明**：工作区根/managed area 根及其祖先（词法或真实）→ `DECL_GENERALIZED` 整态拒绝。
5. **声明完整性 = 整态拒绝**：无法解析/未知 disposition/表格非标准/path-like destination 不可解析/
   **JSON 解析失败** → exit 2，不产出可删除候选。JSON 解析失败不再区分是否含 `PRESERVE`（MIGRATE/ARCHIVE
   同样受保护）。说明文字 destination 只记 warning，绝不作为保护或删除依据。
6. **untracked 声明（F-02）**：`doc/tasks`/`verification` 内 `--others --exclude-standard` 的 `.md/.json` 亦扫描；
   解析失败 → 完整性错误。
7. **预删除清册**：git 候选 `ls-files --others [--ignored]` + 逐文件哈希；非 git 候选遍历；超限/读取失败拒绝。
8. **apply 门禁**：release-window 字段/时间窗/roots/候选集 digest/count/清册 acceptance hash；`--out`
   位于/等于/alias 指向候选 → `OUT_INSIDE_CANDIDATE`（在写清册和删除之前拒绝）。
9. **重复候选（F-06）**：inventory 规范化后重复 → `INVENTORY_DUPLICATE_IDENTITY` exit 2。
10. **回放**：ledger 严格 schema；每 root 必须有 protected source 覆盖；replay 无删除代码路径。

## 4. 运行记录（命令 / 环境 / 退出码）

环境：Windows 11（10.0.26300）、Python `C:\Python314\python.exe` 3.14.6、Git 2.52.0.windows.1；
所有命令在 worktree 内执行，`-B`/`PYTHONDONTWRITEBYTECODE=1`，无第三方依赖。原始输出与命令：
`evidence/tests.log`、`evidence/environment.json`（含每条命令 exit code 与 stdout/stderr SHA-256）。

### 4.1 新增测试（AC1–AC6）

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py
```
exit `0`；`Ran 80 tests` / `OK`；`JSON_RESULTS` 80 项全部 `ok`（0 skip）。日志：`evidence/tests.log`。

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
exit `2`（**预期 fail-closed**，未删除任何文件）。口径说明（F-02 r2 修正）：

- **枚举路径数**：7392 tracked + 1504 untracked（`git ls-files` 列出的 `doc/tasks`/`verification` 路径）；
- **实际解析文件数**：2271 `.md` + 1147 `.json`（其余路径不是声明文件类型，或在此次扫描中未被解析）；
- **声明/保护根**：1858 declarations / 1264 保护根；**18/18 incident source 被真实仓库声明覆盖**；
- **错误 163 条**：`JSON_PARSE` 69、`DECL_BARE_NAME` 57、`DECL_UNKNOWN_DISPOSITION` 9、
  `DECL_DESTINATION_UNRESOLVED` 7、`DECL_GENERALIZED` 6、`DECL_RELATIVE_UNRESOLVED` 6、`DECL_ENV` 4、
  `FILE_UNREADABLE` 3、`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1；
- **warning 54 条**：`DECL_DESTINATION_PROSE` 35、`DECL_ALIAS_REAL_TARGET` 19。

真实仓库现状下工具会**拒绝任何清理**，直到历史声明被修复或裁定。

### 4.5 真实工作区未被触碰（Gate）

`evidence/real-workspace-snapshot.json`：运行前后 HEAD 一致、worktree `git status`（排除本 Task 自身路径）一致、
ledger 的 18 source + 15 root 路径存在性一致；apply 仅在 `%TEMP%` 隔离夹具执行。

### 4.6 复算方式

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py
```
exit `0`（`evidence-ok`）重新生成并校验：新测试 exit 0、两 replay ok、真实工作区快照一致；
`evidence/manifest.sha256` 为各证据文件 SHA-256 清单（含 `governance-check.log`，11 项）。

## 5. 证据索引

| 文件 | 内容 |
|---|---|
| `evidence/tests.log` | 80 测试完整 verbose 输出 + `JSON_RESULTS` |
| `evidence/ac-coverage.json` | AC1–AC6 → 测试方法映射与实际 ok 状态；AC7 既有测试 exit codes |
| `evidence/incident-replay-clean-workspace.json` | AC6 回放报告（15 roots 逐项 REJECT + 原因） |
| `evidence/incident-replay-remove-worktrees.json` | 同上（worktree 工具） |
| `evidence/declaration-audit.json` / `.log` | 真实仓库声明审计（1858/1264、18/18、163 errors、54 warnings、exit 2） |
| `evidence/existing-test_ac_gate.py.log` | 既有 AC gate 测试（12/12） |
| `evidence/existing-run-resource-manifest-cases.py.log` | 既有 manifest 用例（0/32，既存失败） |
| `evidence/environment.json` | 平台/解释器/Git、每条命令与 exit code、stdout/stderr SHA-256、AC 覆盖、快照、失败清单 |
| `evidence/real-workspace-snapshot.json` | 真实工作区前后快照与一致性断言 |
| `evidence/governance-check.log` | check.ps1 原始输出 + exit code（LF 归一） |
| `evidence/manifest.sha256` | 上述证据文件 SHA-256（11 项，含 governance-check.log；Git blob 字节口径） |
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
  （check 运行时 `EV-CHECK`/`EV-MANIFEST` 尚未登记；两者随后作为同一 evidence commit `30946decf` 的
  内容被 pin，最终治理检查由 Codex 在主仓执行）。

**时序说明（避免自引用）**：`governance-check.log` 生成时 Task 行仍 pin 上一 evidence commit `dbd6cbf5f`
（祖先、字节可由工作区命中），随后 evidence commit `30946decf` 同时冻结该日志与最终 manifest，Task-only
记录 commit 将全部行 pin 更新为 `30946decf`。检查结果（5 errors / 4 warnings）不受 pin 数值影响。
未修改 Plan/STATUS/check.ps1/task_ledger.py。

## 7. 未执行 / 残余风险

**未执行**：真实 `--apply`、任何真实删除/移动/分支清理/GC/prune/push、`--force`；未修改 Plan/STATUS/其他 Task/
历史 Review/清册/治理文档；未对真实仓库运行 normal dry-run（声明审计已 fail-closed）。

**残余风险 / 限制**：

1. **真实仓库 163 条声明完整性错误**（69 条 `JSON_PARSE`、57 条 bare name、7 条 path-like destination 等）
   → 工具整态拒绝清理；需另立 Task 修复声明或由 Codex/用户裁定。69 条不可解析 JSON 中大量是历史
   “非单一 JSON 文档”（如数组/拼接输出），在 fail-closed 口径下会阻止清理；这是有意的保守结果。
2. **声明扫描刻意覆盖 1504 个非忽略 untracked 声明路径**（实际解析 2271 `.md` + 1147 `.json`）：更保守，
   审计耗时约数秒、错误数上升（57 条 bare name 等来自 untracked drafts）；如 Codex 认为 untracked drafts
   不应作为保护来源，可另立口径。
3. **共享 guard core 寄居 `clean_workspace.py`**（allowed_paths 冻结 5 个文件，无法新增 `safety.py`）。
4. **apply 仅在 `%TEMP%` 夹具验证**；release-window 记录需人工生成（无自动审批链）。
5. **进程占用检查未实现**；以清册 + 人工接受 + 无 `--force` 缓解。
6. **既有 `run-resource-manifest-cases.py` 0/32 未修复**：check.ps1/task_ledger 仓库状态问题，范围外。
7. junction 夹具在非 Windows 会 skip（本机 Windows 未 skip）。
8. 回放与审计均只读；AC6 的 15 个 root 当前状态未在本 Task 改变或恢复。
