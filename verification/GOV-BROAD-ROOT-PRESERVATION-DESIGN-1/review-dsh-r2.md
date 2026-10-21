# DeepSeek R2

session: session-89d9de3e-714e-4a87-b0b0-b60526ec5eae；exit0；web_visibility=unverified

**changes_requested（仅 metadata；设计本体未发现新增 P0/P1）**

固定基准：
- `diff_base`: `3d0a36ac04d30eba0906e70218ef9491c5b9ffbc`
- R2 `reviewed_head`: `1670b34ec39bd72c5b663d42193faea96836e22a`，实测 `HEAD` 一致
- 设计交付 source: `e33a51b4df4856b9bdfe2dd8e57b84f1c395a797`
- canonical cwd: `G:/CODEX/New Manga`

## R1 逐条关闭情况

| R1 项 | 关闭证据 | 结论 |
|---|---|---|
| P1-1 诊断承载/计数 | `design.md` 已冻结每 record source/destination 各 `add_warning` 一次，共 12 条；不新增 diagnostics schema；模型 `warnings 254→266`，实际内存模拟同样 `+12` | **CLOSED** |
| P1-2 untracked policy | `design.md` 第 30 行已冻结：untracked 存在=`POLICY_UNTRACKED` fatal；tracked 丢失=`MISSING`；Git 失败 fatal；非 Git scanner 继续 fatal；直接 `ProtectionIndex`/model 不加载 policy | **CLOSED（设计层）** |
| P2-1 相邻断言 | 模型 `adjacent_assertion_scope` 已写明“仅无新增根命中”；T11/T16 已改为只看新增根差集，不要求 `evaluate(repo)==[]` | **CLOSED** |
| P2-2 原子发布/计数 | `design.md` 第 32–34 行已冻结 `new_index/new_scanned` 隔离、两阶段发布、异常回滚、scanned 在最终统计前收口；T01/T12 增加注入异常要求 | **CLOSED（设计层，异常注入 NOT_RUN）** |
| P2-3 非 Git fixture | T14 已限定“仅有效 Git RepoFixture 的未安装保持旧行为”；nonGit/Git 失败 fatal；直接 index/model 不触发 Git | **CLOSED（设计层）** |

## 残留 P2（本次唯一未关闭项）

**Handoff 的下一 Task 恢复路径仍写旧 delivery。**

`doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md`：
- 顶部 `delivery_head` 已是 `e33a51b4...`；
- 但第 14 行下一 Task 建议仍写 `delivery c9d6b19514c7e3ea2b21dc40c37bf705729c69d7`。

这会误导后续 `GOV-BROAD-ROOT-PRESERVATION-IMPL-1` 从 R1 旧设计交付启动。它不是设计安全阻断，但属于自有 metadata 不一致；作为“只批准设计和自有 metadata”的审查，不能把该行一起批准。改为 `e33a51b4...`（或明确当前 R2 设计 head）并重新固定 metadata head 后即可转 approved。

另：`preservation-validation.json` 的 `actual_guard_counts=2467/1797` 是 `12e3a4` 旧快照，不是当前值；只要保持 snapshot 标注即可，不按实时计数处理。

## 实测（只读）

- 当前真实 guard：`declarations=2476`、`protected_roots=1806`、`errors=24`、`warnings=254`；24 个错误 identity 与“12 removed + 12 remaining”完整并集逐项一致，且 24 个均唯一。
- 当前内存模拟：`2476/1806 → 2488/1811`，新增恰 `12` Declaration、`5` 根、`12` warnings；错误 `24→12`，其余 12 与模型完全一致；旧保护集合为子集。
- 模型快照：`2474/1804 → 2486/1809`，`warnings 254→266`，`modeled_warnings=12`；与当前差异来自当前已有 9 个 EV，符合“快照/当前增加分开”。
- 15 项覆盖：12 项 root/future-descendant、ancestor、两个相邻路径“无新增根命中”全部为真；不要求 `evaluate(repo)` 为空。
- 9 份 EV：9/9 path 存在、commit `e33a51b4...` 可取、current raw SHA = committed SHA = pin；全部 tracked、status clean；实际 `parse_markdown_declarations` 得到 `EVIDENCE_PIN=9`、`errors=0`。
- 两历史源及 7 个只读输入：raw SHA、base blob SHA、status、base..HEAD 内容均未变。
- `tools/governance/broad-root-preservation.json` 磁盘不存在、未被跟踪；`tools` 在 base..HEAD 与 worktree 均无 diff。
- `99` branches、`137` worktrees；不是“只剩 main”。r212/父 blocked 未被本设计触碰。
- `git diff --check 3d0a36...HEAD` exit 0；`pwsh -NoProfile -File tools/governance/check.ps1` exit 0，PASS，2 个 warning（14 个非终态 Task、STATUS 预算 80%）。
- PowerShell stderr 仍有 ConstrainedLanguage 非核心类型告警，但所有命令 exit 0；未将其当作实现或测试通过证据。

## 未测

- T01–T18 仍全部 `PLANNED / NOT_RUN`；原子注入、untracked/missing policy、漂移、realpath、负例均未真实执行。
- `policy_schema_matcher_negative_tests`、`atomic_loader_negative_tests` 仍为 NOT_RUN。
- 109 回归、clean/remove 双 15 回放未跑。
- loader/schema/绑定/漂移拒绝/三个 CLI 真实行为均未实现；模型不是 runtime。
- 产品/构建测试 NOT_RUN；无任何真实清理、迁移、GC、prune、push、ACL 或 Legacy 运行。

## 范围与结论

设计本体对 R1 两 P1/三 P2 的修订成立，`SIMULATION 24→12` 仍**不是**当前真实 24 已消解；当前仍 24 errors，99 heads/137 worktrees、r212、父 blocked 全部保留。

**因此：设计内容可批准，但当前 metadata 因 Handoff 第 14 行仍指旧 delivery 而不能整体批准。请 Codex 修正该行并重新固定 metadata head 后，再转 approved；本结论不批准任何工具实现、runtime policy 发布或资源清理。**
