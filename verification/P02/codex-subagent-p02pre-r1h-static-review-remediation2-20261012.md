# P02PRE-R1H round-two Owner 修订独立静态 Review

Reviewer=`/root/p02_r1h_remediation_review`；Owner=`/root/p02_r1h_codex_owner`；Integrator=`/root`。Reviewer 未参与实现。Task/dispatch 指定 Reviewer 配置为 `gpt-6.1-sol/high`；本报告不以该模型声明代替证据。

VERDICT=`CHANGES_REQUESTED`。P0/P1/P2/P3=`0/0/1/0`。R1H-005 静态修复成立；R1H-006 仍 `OPEN / P2`。本 verdict 不是运行、集成、Gate 或 AC PASS。

固定 frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；parent=`4a02811d6edf9ab423d299a36c51f103e62dd5f3`；reviewed HEAD=`92c90a9ba20f7a1b4ab090837f99c191745524f6`；tree=`c70bd6c756b5d6931d07a483c958131cd2934a04`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`；branch=`agent/codex/P02PRE-R1H`。

输入 pins=`verification/P02/codex-p02pre-r1h-remediation2-review-input-pins-20261012.json`，SHA-256=`1AF1D4815B0902B3149056BFA27842FB6EBA6C318709F3A66DFB7F5B0ACC0FB9`。开始实质审查前实测 source=`8/8 MATCH`、candidate=`3/3 MATCH`，合计 `11/11 MATCH`。当前 Task=17675 bytes / `67E063CC603125E99435A11C67E18BCE111A89B2365D07CDEF2D8D198038121C`；不沿用旧 Task pin。

完整 frozen base..HEAD diff 只新增 capture/selfcheck/Handoff 三文件，共 1937 行（1287/576/74）；parent..HEAD 仅 selfcheck/Handoff。Capture SHA-256 仍为 `0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3`，与此前已逐段静态阅读的字节一致。本轮重新检查其分类、stage、缺失基线停止、inventory/skip 与上层停止传播，不仅采信旧结论。

## Finding

### R1H-006 — P2 / OPEN：外层 candidate loop 在组件循环之前仍允许漏检的目标操作

检查位置：`verification/P02/p02pre-r1h-selfcheck.ps1:292`–`:304`；限定组件循环内操作的位置为 `:207`–`:281`；mutation fixtures 位于 `:527`–`:538`。

触发位置：`verification/P02/p02pre-r1h-capture.ps1:509` 的 `$linkSkipped = $false` 与 `:510` 的组件 `for` 之间，即在外层 candidate `foreach` 内、pathLoop 外、outer continue 之前。例如插入一条 `Get-Acl -LiteralPath $full`，或 `[IO.File]::ReadAllText($full)`。

静态触发分析：当前检查从 `$pathLoop.Body` 搜索命令、成员调用、赋值和控制流；对 enclosing candidate loop 只验证存在性、pathLoop 与 continue 为相邻 direct statements，以及 continue 后的操作和唯一 `Get-FileHash` 数量。新增上述 prefix 操作不在 `$pathLoop.Body` 内，不改变两个 skip 分支或 helper，不改变 pathLoop/continue 的相邻关系，不增加 `Get-FileHash`，所以这些约束无法拒绝该变异。它会在 symlink 分类/skip 前访问该项 ACL 或内容，违反当前 Task AC2“skip 分支早于 hash/ACL/枚举，且无目标读取”和 frozen Review prompt 第5条“注意任何位于已检查 loop 外、continue 前的调用缺口”。当前缺失基线停止使此动态路径不可达；这只限制当前执行风险，不满足要求 self-check 拒绝此真实候选控制流回归的验收条件。

为何已有负例漏检：`hash before skip decision` 插在 tracked skip 分支前，仍在组件循环内部；`ACL query in component-loop to continue gap` 插在组件循环之后，会破坏 pathLoop/continue 相邻。其它 fixtures 均改变 skip block、flag、break 或 continue。没有 fixture 插在组件循环之前、外层 candidate prefix 内，因此两种现有区域负例不能覆盖该缺口。此结论是静态推断；未解析、运行或执行任何变异 fixture，不把它描述为一次已执行测试结果。

最小修复：约束真实 `$candidateLoop.Body` 从候选路径处理开始到 pathLoop 的 prefix，允许原有路径语法/规范化、staging 排除和初始化的精确操作；拒绝任何额外 hash/ACL/枚举/target read，连同该区间中的 nested block/helper/member 调用纳入检查。补充在该 prefix 插入 ACL、内容读取（以及相应 hash/枚举）的内存 source mutation negative cases，保证 fixture 成功应用/解析且 contract 拒绝。保持 capture、manifest、API、路径和执行 allowlist 不变；优先只改 selfcheck/Handoff。修后提交新 HEAD 并独立复审。

## Findings / 验收处置

| 项目 | 本轮静态结论 | 实际运行 |
|---|---|---|
| R1H-001 | `FIXED_BY_FAIL_STOP_STATIC`：capture 178–181 的两仓冻结 status/index 明确 null；401–407 在仓库路径/Git/inventory 前停止；795–823 将 main 分类为 UNPROVABLE 并阻断 scratch/后续。未把 live 值作为冻结值。完整双仓等值仍未证明。 | `NOT_RUN` |
| R1H-002 | `FIXED_STATIC`：capture 249–270 保留 mode/stage，拒绝 nonzero、重复/大小写冲突、未知 mode 与既有格式错误；521–524 再要求 stage 0。 | `NOT_RUN` |
| R1H-003 | `FIXED_STATIC`：capture 161–167 的精确 FileInfo/属性白名单与517–525的未知类型/属性停止保留。 | `NOT_RUN` |
| R1H-004 | `OPEN`，由 R1H-006 延续。AST 检查已实际绑定 skip direct block、state/flag/break、组件循环与 outer continue，但 prefix 覆盖尚不完整。 | `NOT_RUN` |
| R1H-005 | `FIXED_STATIC`：selfcheck 117–145 精确限制 helper receiver、Static、方法、参数、调用数；479–515 检查真实 helper，合法正例和外部静态文件读取/Get-Item 负例可见。纯内存 IsNullOrEmpty/Math.Max 不再被 blanket 禁令拒绝。 | `NOT_RUN` |
| R1H-006 | `PARTIALLY_FIXED / OPEN / P2`：skip block 顺序、break/flag、组件 loop 成员/命令白名单及 loop→continue gap 已约束；prefix 缺口如上。 | `NOT_RUN` |
| AC1 | 安全停止与分类静态修复成立；frozen equality 缺失仍 `UNPROVABLE`，不是完整 AC PASS。 | `NOT_VERIFIED` |
| AC2 | AST self-check 仍有 P2 覆盖缺口。 | parser/self-check `NOT_RUN` |
| AC3 | 本独立 Review 完成，尚有 P2，批准条件未满足。 | pins 已实测，不替代运行 |
| AC4 | 无本轮集成/engine 证据。 | `NOT_RUN` |
| AC5 | 未做 final pre-run。 | `NOT_RUN` |
| AC6 | 未消耗 R1H capture，未做动态/独立 post-run Review。 | `NOT_RUN` |
| AC7 | Gate 状态约束保留；无自动放行依据。 | `NOT_VERIFIED` |

Architecture：未见 capture 扩大 API、executable、input/output/path、registry/ACL 写入或产品范围。新增 selfcheck 的 ParseInput/source mutation 只操作内存；fixture 内的文件/ACL 代码是待解析文本，没有调用它执行的语句。Helper 正负例与真实候选检查分开，Handoff 如实写未运行。无新的实质异常处理发现；输出 CreateNew/失败保留与停止传播仍保持。

Verification：本轮所有 parser/self-check/preflight/capture/getter/tests/Build/Cargo/AC/OS 动态验证为 `NOT_RUN / NOT_VERIFIED`。没有沿用旧批准；当前 manifest 仍要求 Review/adjudication、集成与真实检查。Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`；`private_registry_absence=UNPROVABLE` 的 Owner waiver 未被本 Review 改写。

## 实际读取与命令

- `Get-Content`：完整 frozen prompt、11 项 pins JSON、当前 Task、manifest、Owner round2 prompt、前 adjudication、Handoff、selfcheck 逐段全部内容；旧 Review/addendum 为本 Reviewer 原已读取/编写且本次 hash 匹配的输入。Capture 前轮完整分段阅读基础上复核相同 hash与本轮相关段。
- `Get-Item`、`Get-FileHash -Algorithm SHA256`：只对 pins 已枚举 source/candidate 与 pins JSON 做 bytes/hash 核对，exit=0、11/11 MATCH。
- `git -C <owner-worktree> rev-parse HEAD HEAD^{tree}`：exit=0，结果与冻结 HEAD/tree 一致。
- `git -C <owner-worktree> diff --stat <frozen-base>..<head>`、`diff --name-status <frozen-base>..<head>`、`diff --name-status <parent>..<head>`：exit=0，范围与上文一致。完整候选按当前文件逐行阅读；并非只看 Owner 摘要或增量声明。
- 未运行 git status，未访问 `.tmp.driveupload`。没有运行 parser、自检、capture、getter、测试或 Sandbox。唯一写入本报告，候选与治理文件未改。

## 下一步

由 `/root` adjudicate，然后给原 Owner `/root/p02_r1h_codex_owner`：在 `C:/Users/49745/.codex/worktrees/p02pre-r1h-codex` / `agent/codex/P02PRE-R1H`，从当前 head `92c90a9ba20f7a1b4ab090837f99c191745524f6` 修复 R1H-006 prefix 缺口及其负例，仅三份既有授权 candidate 路径可写，优先 selfcheck/Handoff；只运行 Task 允许的 `git diff --check`。不得修改 frozen manifest/Task/Gates，不运行候选或动态步骤。交付新 HEAD/Handoff/pins，交非作者独立审查后由 Integrator 裁决。本 Reviewer 不自行集成或释放 successor。

未运行任何 parser、变异自检或动态验证；剩余 P2 使本轮仍不能批准，Build Barrier 必须保持。
