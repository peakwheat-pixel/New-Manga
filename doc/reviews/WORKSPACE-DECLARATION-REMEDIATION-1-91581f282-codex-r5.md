---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R5
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: 91581f282e896ed20cdba378b7a5b0ca7e9f0284
implementation_head: aac8cb52b6e3185bdffedf46ce1561441bbd4de8
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–E）

- **A — TRIAGE：实现已修复，夹具覆盖不完整。** `after_index` 按 `(file, locator, role)` 保存状态列表，精确 code 优先，其次显式 transition；未匹配的多 code 状态会标为 `ambiguous`。GOV-DEBT-CLEANUP-2 的 `TABLE_ROW_ARITY` 归因正确；WORKSPACE-CONSOLIDATION-1 同 locator 的 source/destination 也区分正确。[TRIAGE.md:7](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md:7>) [TRIAGE.md:48](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md:48>) 但 ambiguous 夹具混用了 `TABLE_*` 与 `DECL_*`，它们属于不同 role，没有模拟同一 role 的碰撞；见 Finding F-03。
- **B — 锚点/证据：E8 可复算，Handoff 有矛盾。** E8 的 32 条 Canonical Evidence pin 全部与 blob 字节一致；manifest 的 30 个唯一条目全部复算通过，未含 `.pyc`。E8 到 reviewed head 仅有 Task 更新与 Handoff 改名/更新，目标 worktree 干净。4 点 snapshot 的当前内容指纹重算与记录一致；Handoff 正文仍声称 pins 指向旧提交，见 F-02。
- **C — 回归：记录通过，未发现安全语义削弱。** 固定日志记录 26/26 新测试、80/80 既有测试；两种 replay 均为 15/15 REJECT、0 删除、0 violation、18/18 source；`protection_delta` 为 0 dropped。审计从 163 errors/54 warnings 变为 76 errors/236 warnings。测试和 runner 本轮未重跑，按只读要求检查了已 pin 日志。
- **D — 边界：通过。** base 到 reviewed head 的变更均在 `allowed_paths` 内，无文件删除或历史文件/旧证据修改；E8 到 reviewed head 仅 Task 和 Handoff。两份 replay 记录为零删除；本次未执行任何 Git 写命令、push、GC 或 prune。`git diff --check` 另报两处文件末尾多余空行，见 F-04。
- **E — 残余 76 条：可作为 fail-closed 限制保留，不应为降数豁免。** 它们继续阻止真实 apply/清理。当前提交包暂不应进入集成；修正 findings 并更新受影响的证据锚点后，可以在保留这 76 条阻断状态的前提下集成解析器。

## 2. Findings

### Standards

1. **F-01 · P2：Resource Manifest 漏记资源，却标记 closeout complete。** Task 登记了 linked worktree，runner 还创建了 `G:\CODEX\New Manga.workspace\temp\WORKSPACE-DECL-REMEDIATION\pycache`（当前目录存在但为空）；Resource Manifest 却只有 `NOT_APPLICABLE`，并标记 `resource_closeout_status: complete`。协作协议 §4.2 要求在 Resource Manifest 记录 worktree/temp，并在 approved 集成窗口逐项裁定。请如实登记并将 closeout 状态留待 Codex 核销；本次未删除该目录。[Task:14](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md:14>) [Task:159](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md:159>) [run_evidence.py:42](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py:42>)

2. **F-02 · P2：Handoff 正文证据锚点过期。** Handoff frontmatter 指向 E8，但正文 §5 写旧 commit `2deab2f...`，并称 32 条 pin 都指向它；Task 的 32 条 pin 实际全部指向 E8。请统一正文锚点及相关旧轮次元数据。[Handoff:10](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/handoffs/WORKSPACE-DECLARATION-REMEDIATION-1-aac8cb5.md:10>) [Handoff:78](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/handoffs/WORKSPACE-DECLARATION-REMEDIATION-1-aac8cb5.md:78>)

3. **F-04 · P3：diff whitespace 检查失败。** `git diff --check` 报告 `REMEDIATION.md:95` 和 `tests/test_declaration_remediation.py:410` 文件末尾多余空行。

### Spec

4. **F-03 · P2：ambiguous 回归夹具没有覆盖同 role 状态碰撞。** 夹具把 `TABLE_ROW_ARITY`（table role）和 `DECL_SOMETHING_ELSE`（source role）传给 `match_status()`；实际 `after_index` 会先按 role 分组，因此这两个状态不会通过同一索引键相遇。实现逻辑看起来能处理同 role 的未匹配多 code，但该关键分支尚未由符合场景的夹具锁定。请改成同 role 的多 code 输入，或通过 `after_index`/`decision_for` 做集成级夹具；测试文件是 E8 pin，修后需重新固定证据。

**双轴摘要：Standards 3 项（2×P2、1×P3）；Spec 1 项（P2）。** 未发现其他值得单列的代码 smell。

## 3. AC1–AC7 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **PARTIAL** | TRIAGE 的列表、精确匹配和 transition 逻辑正确；GOV-DEBT-CLEANUP-2 与 source/destination 归因正确。ambiguous 夹具未模拟同 role 碰撞。 |
| AC2 | **PASS** | 固定审计记录与 JSON path+SHA 豁免规则未见削弱。 |
| AC3 | **PASS** | 未见放宽 path-like source / generalized junction 的 fatal 语义。 |
| AC4 | **PASS** | 固定证据记录 GB18030 与损坏二进制拒绝结果；未见降级为静默跳过。 |
| AC5 | **PASS** | `TABLE_ROW_ARITY` 与 `TABLE_SCHEMA_INCOMPLETE` 均保留 fatal；新增匹配逻辑未把两者相互覆盖。 |
| AC6 | **PASS** | `RESIDUAL.md` 列出 76 条错误、原始 message 和处置理由。 |
| AC7 | **PARTIAL** | E8 pin、manifest 和回归日志可复算；Handoff 正文指向旧 evidence commit，且本轮未重跑测试/runner。 |

## 4. 残余裁定

76 条均是无法安全自动消解的声明问题，应继续作为 fatal 保留：44 条 `TABLE_SCHEMA_INCOMPLETE`、1 条 `TABLE_ROW_ARITY`；6 条 `DECL_GENERALIZED`、6 条 `DECL_DESTINATION_GENERALIZED`、1 条 `DECL_DESTINATION_UNRESOLVED`；6 条 `DECL_RELATIVE_UNRESOLVED`、1 条 `DECL_RELATIVE_AMBIGUOUS`；4 条 `DECL_ENV`、2 条 `DECL_UNKNOWN_DISPOSITION`、3 条 `FILE_UNREADABLE`、2 条 `JSON_PARSE`。

其中历史表结构问题应由权威方决定补齐或明确标为叙述表；环境、路径、JSON 和不可读文件问题需逐项解决来源或完整性问题。不得修改历史文件或添加豁免来降低计数。接受这 76 条作为当前 limitation，不代表允许任何真实清理操作。

## 5. 运行证据

**本轮只读命令与结果：**

- `git status --short --branch`（目标 worktree）：exit 0，干净。
- `git diff --name-status f0f19596f..91581f282e896ed20cdba378b7a5b0ca7e9f0284`：exit 0；变更路径均属允许范围。
- `git diff --name-status aac8cb52b6e3185bdffedf46ce1561441bbd4de8..91581f282e896ed20cdba378b7a5b0ca7e9f0284`：exit 0；仅 Task 更新和 Handoff 改名/更新。
- `git diff --check f0f19596f..91581f282e896ed20cdba378b7a5b0ca7e9f0284`：exit 1；报告 F-04 两处末尾空行。
- `python -B -c <E8 pins/manifest blob 校验>`：exit 0；32/32 pins、30/30 manifest 条目一致，0 个 `.pyc` 条目。
- `python -B -c <snapshot 算法只读复算>`：exit 0；7416 tracked、1504 untracked、8920 总输入，`scanned_input_sha256` 与四点记录相同，`same_snapshot=true`。

**本轮未执行：** `NOT_RUN` 新/既有测试、incident replay、`run_evidence.py`。固定证据记录为新测试 26/26、既有测试 80/80、双 replay 均 15/15 拒绝/0 删除/18 source、`protection_delta` 0 dropped、`run-evidence.exitcode=0`；真实审计 exit 2，before 为 163 errors/54 warnings，after 为 76 errors/236 warnings。主仓已有未提交状态保留；本次没有修改文件或执行 Git 写命令。

**推荐下一步：** 由 `workspace-hardening` 修正 F-01 至 F-04，补跑受影响的测试与证据生成，提交新的 evidence commit 并更新 Task pins/Handoff，再交 Codex 复审；76 条残余继续阻断真实清理。