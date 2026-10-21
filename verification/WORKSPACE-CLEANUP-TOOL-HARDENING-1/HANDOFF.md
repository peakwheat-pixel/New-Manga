---
handoff_id: HANDOFF-WORKSPACE-CLEANUP-TOOL-HARDENING-1
task_id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
author: workspace-hardening (DSH)
reviewer: Codex
status: in_review
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
delivery_head: cf7d2d46dad593eac9ec0789943aab38d4931fa2
date: 2026-10-21
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1
branch: dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1
---

# WORKSPACE-CLEANUP-TOOL-HARDENING-1 Handoff（r208/r209 事故根因修复）

> 本文件是 Handoff，不是 Review，不是批准，不是关闭。任务状态仍为 `in_review`。
> 本 Task 不执行任何真实 apply / 删除 / 移动 / 分支清理 / GC / prune / push；不把本文件或任何 Review 当作对历史越界删除的追认。

## 1. 交付内容

| 文件 | 变更摘要 |
|---|---|
| `tools/governance/clean_workspace.py` | 重写为 fail-closed；同时承载五个工具共享的 guard core（allowed_paths 只冻结这 5 个 .py，无法新增 `safety.py`） |
| `tools/governance/remove_worktrees.py` | 路径身份保护 + 非标准位置拒绝 + status/stash 非零拒绝 + ignored 清册门禁 + incident replay |
| `tools/governance/archive_branches.py` | 默认 dry-run；无 `git tag -f`；bundle 不覆盖；verify 通过后才落盘；release-window 门禁 |
| `tools/governance/delete_branches.py` | merged 状态复算、归档 proof/tag/bundle verify 三重校验、release-window 门禁、无 `--force` |
| `tools/governance/consolidate.py` | 严格 Git/porcelain 解析（失败=拒绝，不再静默 `""`/`None`）；复用保护索引；inspection 失败显式记录并 exit 2 |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/` | 66 项 unittest（AC1–AC6 + AC4 11 类夹具 + AC5 apply 隔离夹具 + AC6 正负向回放） |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 可复算证据生成器（测试、既有测试、回放、真实仓库声明审计、工作区前后快照） |
| `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/` | 判别力证据（见 §5） |
| `doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md` | AC 勾选、测试表、Canonical Evidence、Closeout Record |

**未修改**（遵守范围冻结）：`doc/WORKSPACE_GOVERNANCE.md`、`doc/09_COLLABORATION.md`、Plan/STATUS、任何其他 Task、历史 Review/清册、`tools/governance/check.ps1`、`task_ledger.py`。

## 2. AC1–AC7 逐项结果

| AC | 结果 | 判别力证据 |
|---|---|---|
| AC1 路径身份 + 父子覆盖 | **MET** | 规范化绝对路径（normcase/normpath，Windows 大小写不敏感、统一 `/`）；`same` / `descendant`（任意深度）/ `ancestor` 三向判定，组件边界比较（`temp/P02-NEW-TIME-X` 不保护 `…-X6`）；同一路径多来源声明合并（不去重削弱保护）；共享根/泛化声明（工作区根、各 managed area 根、其祖先）→ `DECL_GENERALIZED` 完整性错误并拒绝全部删除。测试见 `TestPathIdentity` / `TestProtectionIndex` / `test_ac4_01/02/05/06/10`。 |
| AC2 失败关闭 | **MET** | 路径解析失败/裸路径/相对路径/`..`/glob/环境变量/歧义相对 → 拒绝；非标准表格列数/坏分隔行 → `TABLE_*` 完整性错误 → 整态拒绝；未知/空 disposition → 完整性错误；`git status`/`git stash list`/`git ls-files`/`git worktree list` 非零退出 → 该候选拒绝或整态拒绝；权限拒绝/不可读 → 拒绝；symlink/junction alias/越界 → 拒绝。旧版“失败当空结果、静默计 0”全部移除。测试见 `test_ac4_03/04/07/08/09/11`、`test_ac2_*`、`test_audit_declarations_refuses_unknown_disposition`。 |
| AC3 删除前清册 | **MET** | `build_inventory`：ignored / untracked / 非 git 源的逐文件 `relative path + size + SHA-256`，链接记录 target；超限→拒绝（无法完整盘点即不得删）；`purpose_hint` 仅为提示，**绝不**自动认定为缓存；apply 前必须生成清册，任何非空清册需 release-window 内 `inventory_acceptance.inventory_sha256` 与清册摘要一致，否则拒绝 apply。夹具验证：`git worktree remove` 对 ignored 内容静默 exit 0（本次实测），因此 ignored 清册门禁是关键。测试见 `test_inventory_records_size_and_sha256_per_file`、`test_ac3_ignored_content_blocks_apply_until_accepted`。 |
| AC4 夹具/失败注入 | **MET** | 11 类：nested root、bare 声明路径、相对路径、非标准表格列数、PRESERVE_UNKNOWN、父目录保护（ancestor）、非 `/worktrees/` 命名位置、stash 非零退出、权限拒绝、重复/别名路径（junction）、symlink/escape（junction 指向工作区外）。每项断言“拒绝删除/不删除”。`test_ac4_matrix_is_complete` 校验矩阵完整。 |
| AC5 dry-run/apply 解耦 | **MET** | 所有会变更的工具默认 dry-run；apply 必须 `--apply` + release-window 记录（task/authorizer/时间窗/roots/候选集 SHA-256/计数），apply 时重算候选集 digest，漂移即 `WINDOW_CANDIDATE_DRIFT` 拒绝；dry-run 报告 `report_sha256` 可复算（同夹具两次运行一致）；apply 报告记录与 dry-run 相同 `candidates_sha256`；apply 只在 `%TEMP%` 夹具上验证。测试见 `TestReleaseWindowAndInventory`、`test_ac5_*`、`test_archive_*`、`test_delete_*`。 |
| AC6 事故回放 | **MET** | 以 `verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json` 为输入：18 protected source / 15 removed root；`clean_workspace.py --replay-incident` 与 `remove_worktrees.py --replay-incident` 均 **15/15 REJECT、0 删除、0 violation、18/18 source 覆盖**，逐项给出 exact/descendant/ancestor 原因；负向对照（去掉 SRC-02、相对 root、坏 schema）→ violation 且非零退出；replay 模式拒绝 `--apply`，并有测试证明删除函数不可达。 |
| AC7 回归与文档 | **MET（有限）** | 新测试 66/66 OK（exit 0）；既有 `test_ac_gate.py` 12/12 PASS（exit 0）；既有 `run-resource-manifest-cases.py` **0/32（exit 1，既存失败）**——原因见 §4.3，属 `check.ps1`/`task_ledger.py` 的仓库状态问题，不在本 Task 冻结范围，且该测试不 import/不执行这五个脚本；未修改 `WORKSPACE_GOVERNANCE.md` 或协作协议。 |

## 3. 关键实现规则（供 Review 快速核对）

1. **路径身份**：`norm_abs()` 只接受 drive-letter/UNC 绝对路径；`normcase+normpath+"/"`；裸/相对/根相对/NUL 一律 `GuardError`，绝不按 cwd 猜测。
2. **保护判定**：候选与每个 protected root 做组件边界关系判定；`descendant`（保护根的后代）与 `ancestor`（候选是保护根的父目录）同样拒绝。
3. **共享/泛化声明**：同一路径多来源声明取并集；工作区根/`worktrees` 等 managed area 根及其祖先声明 → `DECL_GENERALIZED`（过宽声明需人工裁定，不静默阻断也不忽略）。
4. **声明来源**：tracked `doc/tasks/**.md` 的 `## Resource Manifest`（含裸路径单元格）、`## Canonical Evidence` 的 `path` 列；tracked `verification/**.json` 中同时含 `source_path`+`disposition(-original)` 的任意层级对象，以及 `resource_type`+`path`+`disposition` 形态；destination 可解析时也作为保护。
5. **完整性错误 = 整态拒绝**：任何无法解析/未知 disposition/表格非标准/JSON 含 PRESERVE 但不可解析 → 工具输出 `REFUSE`（exit 2），不产出可删除候选。
6. **预删除清册**：git 候选用 `git ls-files --others [--ignored]` + 逐文件哈希；非 git 候选遍历所有文件；`shutil.rmtree` 前置；超限或读取失败即拒绝。
7. **apply 门禁**：release-window 记录字段齐全、时间窗包含 now、roots 精确匹配、`candidates_sha256` 与现场重算一致、`candidate_count` 一致、可选 dry-run 报告引用一致；非空清册另需 `inventory_acceptance` hash。`--apply` 无 `--out` 拒绝（清册必须保留）。
8. **删除执行**：`delete_path` / `git worktree remove`（无 `--force`）；失败记 refused 且非零退出；不做部分成功汇报。
9. **回放**：ledger 严格 schema 校验；每 root 必须有 protected source 覆盖，否则记 violation 并 exit 2；replay 模式无任何删除代码路径。

## 4. 运行记录（命令 / 环境 / 退出码）

环境：Windows 11（10.0.26300）、Python `C:\Python314\python.exe` 3.14.6、Git 2.52.0.windows.1；所有命令在 worktree 内执行，`PYTHONDONTWRITEBYTECODE=1`、`-B`，不装依赖。原始输出与命令记录：`evidence/tests.log`、`evidence/environment.json`（含每条命令的 exit code 与 stdout/stderr SHA-256）。

### 4.1 新增测试（AC1–AC6）

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py
```
exit `0`；`Ran 66 tests` / `OK`；`JSON_RESULTS` 66 项全部 `ok`（无 skip）。日志：`evidence/tests.log`。

### 4.2 事故回放（AC6）

```
C:/Python314/python.exe -B tools/governance/clean_workspace.py --replay-incident <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
C:/Python314/python.exe -B tools/governance/remove_worktrees.py --replay-incident <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
```
均 exit `0`；两报告均 `candidates=15, rejected=15, deleted=0, violations=0, ok=true`，18/18 source 覆盖。报告：`evidence/incident-replay-clean-workspace.json`、`evidence/incident-replay-remove-worktrees.json`。

### 4.3 既有治理工具测试（AC7）

```
C:/Python314/python.exe -B tools/governance/tests/test_ac_gate.py
```
exit `0`，`12/12 cases behaved as specified`。日志：`evidence/existing-test_ac_gate.py.log`。

```
C:/Python314/python.exe -B tools/governance/tests/run-resource-manifest-cases.py
```
exit `1`，`0/32 cases behaved as expected`。**这是既存失败**：用例 expectation 被 `check.ps1` 的 `TASK_LEDGER 已过期`（322/13 计数不一致）等无关规则打断，属当前仓库状态 + 冻结范围外的 `check.ps1`/`task_ledger.py`；该测试不 import 五个加固脚本，与本次改动无关。日志：`evidence/existing-run-resource-manifest-cases.py.log`。

### 4.4 真实仓库声明审计（只读，AC1/AC6 补充证据）

```
C:/Python314/python.exe -B tools/governance/clean_workspace.py --audit-declarations --incident-ledger <ledger> --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence
```
exit `2`（**预期 fail-closed**，未删除任何文件）：扫描 1501 条声明 / 1023 个保护根；**18/18 incident source 被真实仓库声明覆盖**；46 条历史声明完整性错误（1 arity、17 bare/prose、5 unresolved relative、1 ambiguous relative、4 env、6 generalized、9 unknown disposition、3 unreadable），90 条 warning（不可解析 JSON 无 PRESERVE 标记等）。结论：真实仓库现状下工具会**拒绝任何清理**，直到这些历史声明被修复或由 Codex/用户裁定；这不是清理授权。报告：`evidence/declaration-audit.json`、`evidence/declaration-audit.log`。

### 4.5 真实工作区未被触碰（Gate）

`evidence/real-workspace-snapshot.json`：运行前后 HEAD 一致、worktree `git status`（排除本 Task 自身路径）一致、ledger 的 18 source + 15 root 路径存在性一致。所有 apply 仅在 `%TEMP%` 隔离夹具执行。

### 4.6 复算方式

```
C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py
```
exit `0`（`evidence-ok`）时重新生成上述全部证据并校验：新测试 exit 0、两 replay ok、真实工作区快照一致；`evidence/manifest.sha256` 为各证据文件 SHA-256 清单。

## 5. 证据索引

| 文件 | 内容 |
|---|---|
| `evidence/tests.log` | 66 测试完整 verbose 输出 + `JSON_RESULTS` |
| `evidence/ac-coverage.json` | AC1–AC6 → 测试方法映射与实际 ok 状态；AC7 既有测试 exit codes |
| `evidence/incident-replay-clean-workspace.json` | AC6 回放报告（15 roots 逐项 REJECT + 原因） |
| `evidence/incident-replay-remove-worktrees.json` | 同上（worktree 工具，含非标准位置附加原因） |
| `evidence/declaration-audit.json` / `.log` | 真实仓库声明审计（18/18 覆盖、46 errors、90 warnings、exit 2） |
| `evidence/existing-test_ac_gate.py.log` | 既有 AC gate 测试原始输出（12/12） |
| `evidence/existing-run-resource-manifest-cases.py.log` | 既有 manifest 用例原始输出（0/32，既存失败） |
| `evidence/environment.json` | 平台/解释器/Git、每条命令与 exit code、stdout/stderr SHA-256、AC 覆盖、快照、失败清单 |
| `evidence/real-workspace-snapshot.json` | 真实工作区运行前后快照与一致性断言 |
| `evidence/manifest.sha256` | 上述文件 SHA-256 |
| `tests/`、`run_evidence.py` | 测试源码与证据生成器（可复算） |

## 6. 治理检查

命令（worktree 内）：

```
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md
```

exit `1`，`Governance check: FAIL (5 errors, 4 warnings)`。原始输出与 exit code：`evidence/governance-check.log`。错误逐项：

| # | 结论 | 归因 |
|---|---|---|
| 1–2 | `TASK_LEDGER 已过期：声明 322 个 Task，实际 296 个`；`声明 13 个非终态 Task，实际 2 个` | worktree base `b8a1e5197` 早于主仓 Task 释放提交 `b63f22aba`；账本由 `tools/governance/task_ledger.py --write` 维护，不在本 Task allowed_paths |
| 3–5 | `doc/00_INDEX.md` / `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 的 3 条 `archive/history/...` 本地引用失效 | 同样是 base 快照的既有文档状态；不在本 Task allowed_paths，未修改 |

warnings：非终态 Task 计数提示、STATUS/Plan 预算提示，以及 `evidence_dir` 中未逐行登记的 `HANDOFF.md`、`evidence/declaration-audit.log`、`evidence/manifest.sha256`（另有本次运行后才生成的 `governance-check.log`；均由本节与 Task 交付记录引用）。

**未修改 Plan/STATUS/check.ps1/task_ledger.py**；最终治理检查由 Codex 在主仓集成后执行。上述 5 个 error 均与本次五个脚本改动无关（check.ps1 不执行这些脚本）。

## 7. 未执行 / 残余风险

**未执行**：真实 `--apply`、任何真实删除/移动/分支清理/GC/prune/push、`--force`、修改 Plan/STATUS/其他 Task/历史 Review/清册/治理文档；未对真实仓库运行 normal dry-run（声明审计已 fail-closed），未重跑一次性 X6 夹具。

**残余风险 / 限制**：

1. **真实仓库仍有 46 条历史声明完整性错误**：工具会整态拒绝清理（fail-closed 符合 AC2，但意味着“可用性降低”）；需另立 Task 或由 Codex/用户裁定历史声明后才可能再次清理。
2. **共享 guard core 寄居在 `clean_workspace.py`**：allowed_paths 冻结只允许改这 5 个文件，无法新增 `tools/governance/safety.py`；长期使用建议由 Codex 冻结范围后拆出独立模块（本 Task 不扩大范围）。
3. **apply 仅在 `%TEMP%` 夹具验证**：真实清理仍应由 Codex 在 manifest/清册逐项复核后执行；release-window 记录需人工生成（无自动审批链）。
4. **declaration 扫描为全仓库 tracked 文件**：真实仓库 897 JSON 中 60 个非单一 JSON 文档，按“含 PRESERVE 则报错，否则 warning”处理；这是有意的保守规则，仍需 Review 确认口径。
5. **`purpose_hint` 仅提示**：ignored/untracked 内容一律需要 release-window 显式接受对应清册 hash，不做“缓存”自动判断。
6. **既有 `run-resource-manifest-cases.py` 失败未修复**：属 check.ps1/task_ledger 的仓库预算问题，范围外；未改其 expectation 以免掩盖问题。
7. **进程占用检查未实现**（无跨平台可靠 API）；通过“预删除清册 + 人工接受 + 无 `--force`”降低风险，Review 可要求后续补强。
8. 回放与审计均只读；AC6 的 15 个 root 当前状态（部分重建/缺失）未在本 Task 改变或恢复。
