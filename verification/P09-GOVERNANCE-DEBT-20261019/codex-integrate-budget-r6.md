# GOV-PLAN-BUDGET-1 集成与 closeout 指令（r6）

对象：主 checkout G:\CODEX\New Manga；主分支 antigravity/P09-AC3-DELETE-HARDEN-1，预期 HEAD 85a1886bf2c1484ea3d36f328c8ac4f157cd57cd。来源 worktree：G:\CODEX\New Manga\.agents\worktrees\GOV-PLAN-BUDGET-1，来源分支 GOV-PLAN-BUDGET-1，评审交付 head 126af54e7ed478bb3a0470ac32b931a6509acd14。本文件是集成决策与执行指令，不代表 merge 已执行。

## 1. Plan READY 指针及 STATUS

以下为 closeout 成功后的完整 doc/REBASELINE_PLAN.md。完成集成、证据与资源 closeout 后，以此替换 Plan：GOV-PLAN-BUDGET-1 的 DAG 状态为 done，并从 READY 节点移除。未登记 29 个暂缓 Task；GOV-DEBT-CLEANUP-2 approved 行原样保留。

```markdown
# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。范围/裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账 / P03 SFX入口 / P05 契约注记|—|done|
|P02 WebView|P08|限定关闭|
|P04 并发验收|P22|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|closed_with_limitations（R3 changes_requested；HARDEN-1 接手）|
|P10 凭据通道 / P11 长任务契约|P08|**done**（c46c0df0 / ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置/Core/host|P15-C1/P10/UI|done（含 FU、HOST-1/2）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2门槛、AC5阻塞）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|P20-AC4-FPS-1|P20|closed_with_limitations（AC3 PASS；AC5 依裁决）|
|GOV-DEBT-CLEANUP-1|P19/P20|blocked（待用户裁决）|
|GOV-DEBT-CLEANUP-2|—|approved（AC6 的 P19-UI-FIX-1 格式债务；AC7 的 61 项归属未结）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|done|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20。in_review：HARDEN-2。done：**34 项**。
```

doc/STATUS.md 不需要改动：主 checkout 当前为 3142 bytes / 27 lines（预算 3200 / 45），其当前 Task/READY 指针没有登记 GOV-PLAN-BUDGET-1；DAG 与 READY 权威指针只需在 Plan 更新。不得为本 Task 改写 STATUS。

## 2. 集成形式与确切命令

使用 git merge --no-ff GOV-PLAN-BUDGET-1，在主 checkout 的 antigravity/P09-AC3-DELETE-HARDEN-1 分支、有效 lease 下执行。不要 cherry-pick，不要在来源 worktree 内合并。

已核实 merge-base(HEAD, GOV-PLAN-BUDGET-1) = 85a1886bf2c1484ea3d36f328c8ac4f157cd57cd，且 git rev-list --count HEAD..GOV-PLAN-BUDGET-1 = 3。85a1886bf 是共同基点且已在主分支，不会作为重复提交重新应用；实际纳入的是其后的 126f9f31c、ab925051b、126af54e7 三个来源提交，另生成一个 merge commit。

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --porcelain
git merge --no-ff GOV-PLAN-BUDGET-1 -m "integrate GOV-PLAN-BUDGET-1"
git rev-parse HEAD
```

成功后，integration_commit 填 git rev-parse HEAD 输出的完整 merge commit hash；不要填 126f9f31c 或 126af54e7。目前无法预知 merge commit hash。

## 3. 终态、Canonical Evidence 与 closeout 字段

建议终态为 done：实现 Review 针对精确 delivery head 126af54e7... 为 APPROVED，AC1/AC3 边界证据及 AC4 原始检查输出已入库；Plan READY 指针由 Codex 修正后，集成检查可完成最后治理门。只有集成后 global 与 TaskPath 检查通过（允许 STATUS 预算 warning）且资源清单如实完成，才设置 done。填写：

- integration_commit：上节 merge 后 git rev-parse HEAD 的完整值。
- canonical_evidence_status: complete
- resource_closeout_status: complete
- Task status: done

Canonical Evidence 占位表需要补登。建议保留以下现有文件并按实际 commit pin；仓内证据 SHA-256 同列提供便于核对。AC4 还需保存集成后通过的两次检查完整输出，不能把交付 head 上“READY DAG 不匹配”的旧输出当作最终通过证据。新输出建议路径为 verification/GOV-PLAN-BUDGET-1/ac4-closeout-governance-output.txt；DSH 执行后填入实际 commit 和 SHA-256。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| GOV-PLAN-BUDGET-1-AC1-AC3 | AC1, AC3 | verification/GOV-PLAN-BUDGET-1/ac1-ac3-budget-and-boundary.md | 126f9f31c857a728c5818b01aab91071dc7ed273 | A2E7C7B4C4083405436581F83B569157390E7769E06944FBEFF7240C63344026 | CANONICAL |
| GOV-PLAN-BUDGET-1-AC2 | AC2 | doc/handoffs/GOV-PLAN-BUDGET-1-126f9f31c.md | ab925051bb59bc5607d73c6f643e0da66594a998 | 4D1D26D3B248E26525A11637759CFD874AEA00FC5594B17AF3A1D052D00836CF | CANONICAL |
| GOV-PLAN-BUDGET-1-AC4-DELIVERY | AC4（delivery head 结果及其单一待修 READY 错误） | verification/GOV-PLAN-BUDGET-1/ac4-governance-output.txt | 126f9f31c857a728c5818b01aab91071dc7ed273 | ED62E77EAEE076377CF9A4E0B25DFD72E675CA0A14E5A3157FD002B64EF1D988 | CANONICAL |
| GOV-PLAN-BUDGET-1-AC4-CLOSEOUT | AC4（集成后 global + TaskPath 检查） | verification/GOV-PLAN-BUDGET-1/ac4-closeout-governance-output.txt | DSH 创建后填写 | DSH 创建后填写 | CANONICAL |
| GOV-PLAN-BUDGET-1-AC5-REVIEW | AC5（独立 Review） | doc/reviews/GOV-PLAN-BUDGET-1-126f9f31c-antigravity-r1.md | 126af54e7ed478bb3a0470ac32b931a6509acd14 | 098EDFA3DD4B495835BB2C72F575C2FC616193F4217BBB3B2CAE57134773D023 | CANONICAL |

现有 AC1–AC3 证据末尾把 Floor(64 * 0.8) = Floor(51.2) 写作“51.2→52 行”；检查器实际比较门槛是 51 行（Floor 结果），达到 51 行即 warning。DSH 应在 Task Closeout Record 中记明算术更正，不得声称 52 行；已有 fixture 的 7000/64、7001 bytes、65 lines 及 5600 bytes 观察仍按原记录，不改写原始证据文件。

## 4. Worktree 与派生资源处置

建议保留来源 worktree，当前不移除、不移动、不清理。worktree 有 33 个镜像的未入库 doc/ + archive/ 文件，且状态为 33 条 untracked；它们用于复现主 checkout 检查环境，不属于本 Task 交付物，也不是可因 merge 而删除的副本。Resource Manifest 将 worktree disposition 记为 PRESERVE_UNKNOWN（说明 33 个镜像文件未经逐项迁移授权，保留原位）；来源分支在 merge 后的历史可达性不构成删除 worktree 的许可。agent-output/exchange 只有在核实不存在或无本 Task 资源后，才记 NOT_APPLICABLE。不运行 git worktree remove 或 prune。

以上 preserve 项有明确 disposition 和原因后，资源 closeout 可标 complete，这表示资源均已逐项处置记录，并不表示已删除。若实查发现其他来源、用户数据或独有文件，按实际情况补入 manifest 并保留；不得覆盖或清理。

## 5. DSH 执行顺序（可直接转发）

1. 开始写入前确认有效 coordinator lease；不要调用 coordinator-lease.py。核对主 checkout 仍为 antigravity/P09-AC3-DELETE-HARDEN-1 / 85a1886bf2c1484ea3d36f328c8ac4f157cd57cd，来源 branch 与固定 delivery_head 一致。记录两处 checkout 的 git status --porcelain，与本报告第 6 节初始基线比较；不要清理已有 dirty/untracked 内容。
2. 主 checkout 保持现有分支和所有既有工作区文件。将 Task 从 in_progress 更新到 Review 已批准的集成窗口状态 approved；将 Plan READY 声明移除本 Task，DAG 行暂记 approved（集成/closeout 中）。此为 merge 前过渡，不要此时标 done。AC2 保持 29 个暂缓 Task 与 GOV-DEBT-CLEANUP-2 不变。Canonical Evidence 先登记现有 AC1–3、AC2、AC4 delivery、AC5 Review；AC4 closeout 项待步骤 6。
3. 按第 2 节命令在主 checkout 执行 git merge --no-ff GOV-PLAN-BUDGET-1。如 Git 因现有工作区状态拒绝，停止并报告原始错误，不 stash、不覆盖、不 reset。记录成功后的完整 integration_commit。
4. 核对 merge 结果含来源三个提交和预期文件；确认 Plan 与 STATUS 没有被 Owner 提交改写，GOV-DEBT-CLEANUP-2 行原样，29 个暂缓 Task 未登记。补全 Task Closeout Record：终态建议、集成 commit、证据 pin、资源 disposition；记录 Floor(51.2)=51 的算术更正。
5. 按第 1 节最终全文更新 Plan：GOV-PLAN-BUDGET-1 DAG 行为 done，READY 声明只列 ARCH-DOC-REBASELINE、P20。不修改 doc/STATUS.md。
6. Plan 更新后运行并保存完整输出、stdout/stderr、exit code：pwsh -NoProfile -File tools/governance/check.ps1 与 pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-PLAN-BUDGET-1.md。两项均应无 error；STATUS 80% budget warning 可如实保留。结果保存至建议的 ac4-closeout-governance-output.txt，再将文件 commit/hash pin 补入 Canonical Evidence。
7. 对照 Resource Manifest 逐项登记；保留 worktree 和 33 个镜像文件，不删不移。确认所有资源均有 disposition 后，设 canonical_evidence_status: complete、resource_closeout_status: complete、Task status: done，Plan DAG 保持 done。最终再记录两处 git status --porcelain，并确认未清理或覆盖任何已有状态。

## 6. 动手前状态基线

采样方式：git status --porcelain 全量输出，计算行数及 UTF-8 输出 SHA-256。主 checkout 已含大量原有 dirty/untracked 内容；摘要 hash 用于前后对照，不替代清单。

| checkout | branch / HEAD | porcelain 条目 | porcelain SHA-256 |
|---|---|---:|---|
| 主 checkout G:\CODEX\New Manga | antigravity/P09-AC3-DELETE-HARDEN-1 / 85a1886bf2c1484ea3d36f328c8ac4f157cd57cd | 1234 | FC547F6684F9BD67DC2523100E320141660F2D0A5468DB8E1943BD169EFE8050 |
| 来源 worktree G:\CODEX\New Manga\.agents\worktrees\GOV-PLAN-BUDGET-1 | GOV-PLAN-BUDGET-1 / 126af54e7ed478bb3a0470ac32b931a6509acd14 | 33 | 5BAAB63E9BDD1EB59AE49ECF38F256D93E43F32E599C02678404C4B614D4008A |

动手后已在两处再次采样。主 checkout porcelain 新增的唯一条目是本报告；worktree 状态未变化。摘要 SHA-256 按 git status --porcelain 全量输出的 UTF-8 字节计算。

| checkout | 动手前条目 / SHA-256 | 动手后条目 / SHA-256 | 差异 |
|---|---|---|---|
| 主 checkout | 1234 / FC547F6684F9BD67DC2523100E320141660F2D0A5468DB8E1943BD169EFE8050 | 1235 / 4AC1A27A6658E57AEB2E6A05DB86D68CA1AC7C38DE0BEB688A5CF9E087DDA061 | 新增 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-integrate-budget-r6.md` |
| 来源 worktree | 33 / 5BAAB63E9BDD1EB59AE49ECF38F256D93E43F32E599C02678404C4B614D4008A | 33 / 5BAAB63E9BDD1EB59AE49ECF38F256D93E43F32E599C02678404C4B614D4008A | 无变化；33 条均为未入库镜像文件 |

不为制造 clean 状态而清理文件。