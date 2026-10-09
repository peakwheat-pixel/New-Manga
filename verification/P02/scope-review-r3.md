# P02 release 治理增量独立范围复核 r3

- Timestamp：2026-10-09T03:16:59Z
- Reviewer：`/root/p02_scope_review`（独立于 Codex 治理增量作者）
- Worktree：`G:/CODEX/New Manga.worktrees/P02-harness-scope`
- Branch：`codex/P02-harness-scope`
- Baseline HEAD：`241ff3b70b6fc0490ea238efd486cc707f849031`
- 审查对象：当前工作树文件，包含 staged/unstaged release 修改；不是已提交实现 head
- `doc/tasks/P02.md` SHA-256：`E870B9271A9FA4C9411E1A8C7ED1F042A43F8B6769F9C047CDCCA11E727FBF24`
- `verification/PROJECT-ROADMAP-20261008/verify_plan.py` SHA-256：`2F3588B91DDBF2960D6043D4D7073C799052C3CEF3BA046BC15F747A57605EF7`
- Decision：`changes_requested`
- Findings：P0/P1/P2/P3 = 0/0/1/0

本轮只审查 r2 后新增的 Codex-only 路线校验器治理范围。r2 的 AC/Owner 范围批准未被延伸为本增量批准；本轮也不构成后续实现的正式 DeepSeek Harness Review。

## Finding

### P02-SCOPE-R3-01 — 路线图状态漂移仍可通过新增交叉校验（P2，open）

**位置：**`verification/PROJECT-ROADMAP-20261008/verify_plan.py:89-94`。

Plan 检查在 `:80-81` 明确约束其余17个节点为 proposed；图节点检查只要求状态属于枚举，并只检查四个 live Task。其余17个图节点即使变成 ready，仍会通过。另在 `:93` 将图节点转为字典，重复出现的同一任务只保留最后一次声明；ROADMAP 当前确有两处 P03（`ROADMAP.md:34,72`），第一处与 Task/Plan 冲突时会被第二处覆盖。

这会让权威 Plan 保持 proposed 的候选在派生图中显示为 ready，或同一已完成 Task 在两张图中显示相互矛盾的状态，而 release Gate 仍打印 PASS。新增治理增量声称的 Task/Plan/ROADMAP 状态交叉一致因此没有被完整保证。

**只读复现：**通过 `unittest.mock.patch.object(Path, 'read_text', ...)` 仅替换内存中读取的 ROADMAP 文本，以当前校验器源码执行 `__main__`；磁盘 ROADMAP、Task、校验器均未修改。两次均真实执行校验器其余 Git/祖先/链接/范围检查并被接受：

```text
P04 diagram ready, Plan still proposed => ACCEPTED
roadmap declarations=[('P03', 'done / Review与Codex集成Gate通过'), ('P04', 'ready / 未释放'), ('P03', 'done / 固定Review与Gate完成')]
first P03 diagram blocked, second P03 still done => ACCEPTED
roadmap declarations=[('P03', 'blocked / Review与Codex集成Gate通过'), ('P04', 'proposed / 未释放'), ('P03', 'done / 固定Review与Gate完成')]
Disk files unchanged; product tests/build not run.
MUTATION_PROBE_EXIT=0
```

此 EXIT=0 是复现程序运行成功；两个被注入漂移的案例被错误接受，不能当作判别通过。

**最小处置：**直接逐一检查 `diagram_states` 的每次声明：四个 live Task 的预期状态取 Task，其余节点的预期状态为 proposed。保留跨图重复节点，但所有重复声明都必须一致；无需新增依赖或泛化解析框架。修订后应在正确图上 EXIT=0，上述两种漂移分别被拒绝，再固定 Hash 复核。

**释放影响：**在此 finding 关闭前，不应把本 Codex-only 治理增量视为独立批准或提交释放。原 AC/Owner 范围的 r2 approved 保留。

## 其他范围核对

- `doc/tasks/P02.md:56` 明确新增校验器路径为 Codex-only，Owner 无修改权。该路径未并入 ZCode 的 Owner allowlist；`:49-54` 的 Owner 路径与 r2 范围一致，未开放产品源码/依赖/共享契约。
- 四个 Task 的当前真实状态为 P01/P03/P08=done、P02=ready；Plan 行与图的当前实际声明一致，其余17项的当前实际声明也均为 proposed。finding 指向校验器无法阻止状态漂移，并不声称当前图已漂移。
- diff 仅替换 live 状态映射/计数与图状态交叉检查部分。固定 `BASE=e4242ecd419eb0eea098d2f63b40f709aa5caeea` 未改；`task-inventory.csv` 对 HEAD 无差量。
- 196历史节点及分类/依赖引用、105条集成祖先、协议状态枚举、Plan编号/唯一性、Mermaid DAG、局部链接、P01 frozen-base 产品范围与治理空白守卫均保留。未修改历史 inventory 或为 P02改写审计基线。图状态遗漏需按上述 finding 补齐。
- Task 的原 AC4 必要覆盖、AC6 mapping/contrast 分离、真实/Mock 边界、用户数据保护和禁止产品修复条款保留。

## 日志与独立运行证据

`route-validator-before-update.log` 记录 EXIT=1，直接失败点是旧 `verify_plan.py:63` 的 Plan 状态标签允许集合断言；日志在该处停止，没有执行到动态计数检查。其内容支持标签不兼容导致的本次失败；旧计数还需要适配 P02 是由旧源码可推知的另一问题，不能说该日志已运行并证明计数断言失败。

`route-validator-release.log` 带 PowerShell/解释器/version/command/EXIT=0，其新增状态检查 PASS 文本与当前实现一致。Reviewer 在同一工作树独立执行：

```text
shell=PowerShell 7.6.6
interpreter=C:\Python314\python.exe
command=python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py
Planning snapshot base=e4242ecd419eb0eea098d2f63b40f709aa5caeea; live HEAD=241ff3b70b6fc0490ea238efd486cc707f849031
PASS: 196 unique nodes, all classifications and dependency references
PASS: 105 new architecture/governance integration records are audit-base ancestors
PASS: live P01/P02/P03/P08 Task states match the Plan; remaining P nodes stay proposed
PASS: 21 unique planned nodes and roadmap graphs have no dependency cycles
PASS: delivery/navigation local links resolve
PASS: zero production/code delta; governance whitespace check
Product tests/build/GUI: NOT_RUN (planning-only)
REVIEWER_EXIT=0
```

正确当前数据通过与漂移数据也通过可以同时成立；release log 不足以关闭本次 finding。Task 和校验器在只读探针后再次核对 SHA-256，均与页首一致。

## 下一步与限制

推荐 Codex 仅在已登记的 Codex-only `verify_plan.py` 范围修订逐声明状态约束，记录正确图通过及两种漂移被拒绝的证据，再请求独立复核；不扩大 ZCode Owner 路径，不提前派发本治理增量。

可转发给 Codex：在 `G:/CODEX/New Manga.worktrees/P02-harness-scope`、`codex/P02-harness-scope@241ff3b70b6fc0490ea238efd486cc707f849031`，保持 BASE、历史 inventory、DAG/link/ancestor/产品范围守卫不变；仅把图状态校验改为逐一核对每次声明的 Task/proposed 预期状态，拒绝 P04-only ready 与 P03首处blocked两种内存对照。把命令/环境/Hash/EXIT及判别证据写入 P02 授权 evidence 路径，固定新 Task/校验器 SHA-256后复核，独立批准前不提交释放。

Reviewer 仅新增本报告。未运行产品测试、应用构建、真实 WebView 或实现 Review；当前治理文件尚未提交，报告结论仅适用于固定 Hash 的工作树输入。
