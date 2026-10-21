---
task: WORKSPACE-CLEANUP-TOOL-HARDENING-1-REVIEW
reviewer: Codex
author: dsh-workspace-hardening
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
reviewed_head: 21715c5c005e1a757b5f6f3befb9bf1e701e991b
implementation_head: cf7d2d46dad593eac9ec0789943aab38d4931fa2
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A/B/C/D/E）

- **A 范围与 diff：通过。** `b8a1e5197..cf7d2d46d` 只改五个工具、该 Task 和其 evidence 目录。`cf7d2d46d..21715c5c0` 也只涉及该 Task 与其 Handoff/evidence。没有越界修改其他 Task、STATUS、Plan、GOVERNANCE 或历史证据。
- **A 清理路径：有受门禁保护的真实变更代码。** `clean_workspace.py` 有 `rmtree/remove`，`remove_worktrees.py` 调用不带 `--force` 的 `git worktree remove`，分支工具有归档和删除路径；默认 dry-run，apply 需 release-window。本轮没有执行清理。未发现 push、`git gc` 或 prune 路径。没有 `--force` CLI 选项、`git worktree remove --force` 或 `git tag -f`；但 `delete_branches.py` 对未合并分支使用受归档证明和 release-window 门禁保护的 `git branch -D`。
- **B AC1–AC7：AC1–AC4 存在安全或验证缺口；AC5、AC6 的提交证据基本成立；AC7 需按失败结果记录，不能算全绿。** 详见判定表。
- **C 证据：内容大多可复算，但 commit pin 与 manifest 有错误。** Task 的 23 条 Canonical Evidence 哈希在 `21715c5c0` 上全部匹配；其中 10 条不匹配其记录的 `cf7d2d46d`。最终 `manifest.sha256` 有 1/11 条不匹配。
- **D 残余风险：Task 如实记录了 46 条声明错误导致真实清理 fail-closed、共享 core 所在文件、仅在 `%TEMP%` 验证 apply、人工生成 release-window、未实现进程占用检查及非 Windows junction 测试限制。** 另有下列未记录的保护索引缺口。
- **E 治理：** Task frontmatter 的状态、路径、base 和 `delivery_head` 结构本身没有发现格式错误。`check.ps1` 日志所记 5 个 error 与 Task 代码无关，但“Handoff 将其归因于早于 `b63f22aba`”不准确；4 个 warning 中有一项来自本 Task 未登记过程文件。

## 2. Findings

### F-01 — P1：保留声明经过 junction 时，真实目标可能进入删除候选

[clean_workspace.py:728](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:728>) 对声明只做词法 `norm_abs`，`ProtectionIndex.evaluate` 也只比较词法路径；只有候选路径自身在 [clean_workspace.py:1544](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1544>) 检查 alias。

具体情形：`PRESERVE_*` 声明指向一个 junction，而被保护目录通过真实路径成为候选。声明路径和候选路径词法不相交，真实目标可能被判为 `CANDIDATE`；最终删除检查也只检查目标自身是不是 alias。因此存在删除受保护目标的路径。现有 junction 测试只验证“junction 候选被拒绝”，没有验证“junction 声明保护其真实目标”。

**最小修正：** 声明入索引时也解析并检查 realpath；对 alias 声明整态拒绝，或将其真实目标纳入保护索引。增加真实入口夹具：保护声明经 junction 指向候选目标，要求目标被拒绝或整态 exit 2。

### F-02 — P1：声明扫描只读 tracked 文件，遗漏未提交保护声明

[clean_workspace.py:1094](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1094>) 使用 `git ls-files`，只扫描 tracked 的 `doc/tasks` 与 `verification`。主仓当前有未跟踪的 `doc/tasks/`、`verification/` 内容；其中若有保护路径声明，工具不会看到它们，仍可能将对应 workspace 路径判为可删。

这与项目规则“未提交内容归原作者所有”不相容，也使 1501 条声明的审计不代表完整工作树。

**最小修正：** 扫描上述目录内非忽略的 untracked `.md/.json` 声明文件；若不能安全解析，拒绝 apply。也可先对这些目录存在 untracked 声明文件时整态拒绝。

### F-03 — P1：无法解析的 destination 声明被降为 warning

[clean_workspace.py:830](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:830>) 在 destination path 解析失败时仅记录 warning 并继续。实际审计有 30 条 `DECL_DESTINATION_UNRESOLVED` warning。由于成功解析的 destination 会加入保护索引，失败时静默跳过可能让某个受保护目的地不再受保护。代码没有区分可接受的说明文字与 glob、环境变量、遍历或歧义路径。

**最小修正：** 对允许的说明文字/占位符设明确规则；任何 path-like 但无法解析的 destination 都记完整性错误并拒绝清理。

### F-04 — P2：`--out` 可放在候选目录内，apply 会删除刚写出的清册

apply 先生成 inventory，随后把清册写入 `--out`，再删除候选目录，见 [clean_workspace.py:1693](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1693>) 和 [clean_workspace.py:1703](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1703>)。`--out` 没有与候选路径做包含关系校验。若输出目录位于候选内，清册和 apply 报告会随候选一起被删除；新生成的输出也不在预先计算的 inventory 中。

**最小修正：** apply 前拒绝 `--out` 等于、位于或经 alias 指向任一候选的情形，并为该情况增加隔离夹具。

### F-05 — P2：Canonical Evidence 的 commit 标注错误，最终 manifest 有一项失配

[Task Canonical Evidence 表](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md>) 的 23 条记录都标注 `cf7d2d46d`：

- 对照 `cf7d2d46d` blob，只有 **13/23** 哈希匹配；另外 10 条哈希不匹配。
- 对照最终记录提交 `21715c5c0`，**23/23** 哈希匹配。
- `cf7d2d46d..21715c5c0` 修改了 `tests.log`、回放报告、环境/审计文件及 `run_evidence.py` 等；因此最终证据并非都来自 `delivery_head`。
- 最终 `manifest.sha256` 对 11 个条目仅 **10/11** 匹配；`governance-check.log` 的 manifest 哈希为 `e389…`，实际为 `2721…`。`cf7d2d46d` 版本的 manifest 则为 18/18 匹配。
- 内部 JSON 复算通过：coverage 与 environment 一致，三份报告的 `report_sha256` 有效；两份事故回放均为 15/15 REJECT、0 删除、0 violation、18/18 source 覆盖。
- `environment.json` 的 `required_failures` 为空，但未记录 `run_evidence.py` 自身的 exit code。日志与运行器条件支持其声称结果，但本轮没有独立重跑。

**最小修正：** 重新冻结最终 evidence 字节，修正每条证据的 commit pin，并在 governance 日志最终确定后重算 manifest。按 Task 的非自引用约定，证据提交应先于最终 Task 记录提交。

### F-06 — P2：AC4 中部分失败注入没有验证真实入口，重复路径用例也没有断言拒绝

[test_tools_fixtures.py:254](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py:254>) 的 stash 失败用例通过 helper/build-report 注入；[test_tools_fixtures.py:289](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py:289>) 的权限用例直接调用 `build_clean_report`，没有跑 CLI 主入口。`test_ac4_10_duplicate_alias_path` 对重复规范化路径只断言去重数量，没有断言候选被拒绝；同一用例后半段的 junction 候选才通过真实入口断言 `REJECT`。

**最小修正：** 为 stash/权限失败增加真实入口验证；按当前 AC4 要求，让重复 inventory identity 明确拒绝，或由用户裁定修改 AC 后再以隔离 apply 证明去重只会处理一次且不会误删。

### F-07 — P3：治理失败原因归因不准确，且 warning 含本 Task 自身文件

[HANDOFF.md](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md>) 将 `check.ps1` 的 5 个 error 归因于 worktree base 早于 `b63f22aba`。但 `b63f22aba` 没有改 `TASK_LEDGER.md`、`doc/00_INDEX.md` 或 `doc/AD-001`，也没有加入日志所指的 archive 文件；这些目标在 `b8a1e5197` 和 `b63f22aba` 中都不存在。`TASK_LEDGER.md` 本身声明 322 个 Task 中有 26 个 untracked drafts，而该干净 worktree 只有 296 个 tracked Task，能够解释前两项；其余三项是两版本都存在的失效引用。故这些 error 与 Task 实现无关，但“由早于 b63 的提交导致”未经证实。

4 个 warning 中一项是 checker 对本 Task 的 `HANDOFF.md`、日志和 manifest 未登记的警告；其余为非终态 Task、STATUS/Plan 预算。该 warning 不是错误，但应如实区分。

**最小修正：** 将原因改为“worktree 缺少主仓未跟踪 drafts/archive 内容及已有 stale references”；明确 4 个 warning 中的 Task evidence-dir warning。

## 3. AC1–AC7 判定表

| AC | 结论 | 证据 | 本轮是否真实验证 |
|---|---|---|---|
| AC1 | **部分满足** | 词法规范化、组件边界、祖先/后代保护和泛化声明 fail-closed 有实现与测试；声明 alias 未解析 realpath，见 F-01；untracked 声明不扫描，见 F-02。 | 静态查代码；测试只依据已提交日志，未复跑。 |
| AC2 | **部分满足** | source 路径、表格结构、disposition 有失败关闭逻辑；status/stash/`ls-files` 使用 checked Git 调用；destination 解析错误却可降为 warning，见 F-03。`ls-files` 非零没有找到专门故障注入测试。 | 静态查代码与测试源码；未复跑。 |
| AC3 | **部分满足** | ignored/untracked 清册逐文件记录 size/SHA-256，非空清册由 acceptance hash 校验；`--out` 位于候选内时清册会被删除，见 F-04。 | 静态查代码；隔离 apply 仅有提交日志。 |
| AC4 | **部分满足** | 11 个方法名齐全，提交日志记为 66/66；stash、权限注入未走真实入口，重复 inventory 只去重而未断言拒绝，见 F-06。 | 读取测试源码和 coverage；未复跑。 |
| AC5 | **满足（仅夹具）** | 默认 dry-run；apply 要求显式开关、时间窗、roots、候选集 digest；提交测试覆盖复算和 candidate drift。apply 实测只在 `%TEMP%` 夹具。 | 读取测试与日志；本轮未执行 apply。 |
| AC6 | **满足（证据内）** | 两个 replay JSON 均为 15/15 REJECT、0 删除、0 violation，18/18 source 覆盖且每项有原因；负向测试断言 violation/非零返回。 | 独立复算 JSON 与内部 SHA；未重跑回放命令。 |
| AC7 | **部分满足** | evidence 记录新测试 66/66、`test_ac_gate.py` 12/12；`run-resource-manifest-cases.py` 明确为 **0/32，exit 1**，没有冒充 PASS。其原因指向 TASK_LEDGER/check 基线问题，但本轮未运行基线测试。 | 只读证据复算；未复跑任何测试。 |

## 4. 是否可据此进入集成

**暂不可进入集成。** F-01、F-02、F-03 涉及保护集合可能漏掉受保护路径，必须修复并补真实入口测试；F-05 的 Canonical Evidence commit/manifest 错误也需先纠正。当前跟踪声明审计有 46 个完整性错误，真实仓库清理会 fail-closed，需另立 Task 或裁定后再考虑真实 apply。

## 5. 运行证据

本轮没有文件修改、Git 写命令、push、GC、prune 或真实清理；最终目标 worktree `HEAD` 仍是 `21715c5c0`，`git status --short --branch` 仅显示分支且 exit `0`。

| 只读命令/检查 | 结果 |
|---|---|
| `git diff --name-status b8…cf` | exit `0`；变更均在 allowed_paths 内。 |
| `git diff --name-status cf…217` | exit `0`；变更仍限于本 Task 的 Task/Handoff/evidence。 |
| Canonical Evidence blob 哈希对照 | 对声明的 `cf` commit 校验 exit `1`：10/23 不匹配；对照 `217` 时 23/23 匹配。 |
| `manifest.sha256` blob 复算 | `cf` 版 18/18；`217` 版 10/11，`governance-check.log` 失配。比较脚本 exit `0`，但输出明确列出失配。 |
| JSON 内部一致性复算 | exit `0`；coverage/environment、报告摘要和事故回放统计一致。 |
| `rg` 静态检查变更工具的清理命令 | exit `0`；发现 apply 删除路径和 `git branch -D`；未发现 push、GC、prune 或 `--force` 参数/调用。 |
| `run_evidence.py`、66 项测试、既有测试 | **NOT_RUN**。运行器会覆盖 evidence 文件；本轮只读其提交日志和源码，不把 DSH 日志当独立复跑。 |
| `check.ps1 -TaskPath` | **NOT_RUN**。其已提交 `governance-check.log` 记录 exit `1`、5 errors/4 warnings；本轮按只读约束未执行。 |

**推荐下一步：** 由 `dsh-workspace-hardening` 修复 F-01 至 F-04 并补真实入口夹具；随后先提交冻结 evidence，再提交引用该 evidence commit 的 Task 记录，最后重新请求独立 Review。