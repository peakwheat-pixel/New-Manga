# CMD-COVERAGE-ASSERT-FIX 独立复核 r2

## 0. 审查者、来源与范围

- **审查者**：DSH 子 agent `review-cmd-coverage`（独立上下文；未参与本卡实现或 r2 返修；由 root agent `lead` 派发）。
- **被审 head**：`073f00b022dd41631a78ccdee7dfa385a8e2827f`（父提交 `f1835e437`）。
- **基线**：`9a79b2a69`；工作区在复核开始时 `git status --short` 为空。
- **范围**：`073f00b02` 对 `f1835e437` 的 diff、r1 报告、卡面/README/`four-pieces.log`，以及 P2-1 的重叠实验。
- **约束**：所有实验改动均用 `git checkout --` 还原，并核对 blob 与 HEAD 一致；除本报告外未保留工作区改动。

## 1. verdict

**ACCEPT_WITH_LIMITATIONS**

P2-1 的**功能缺口已闭合**：新增的 `Assert.Empty(covered.Intersect(families))` 经我重现的 `create_region` 重叠实验确实使测试变红（2 failed / 3 passed，失败包含该守卫本身）。P2-3 的更正准确；FEA-09 已回退到基线，无新增越界文件；TASK_LEDGER 计数已与生成器一致。

但仍有 **P3 级**残留：

1. `P2_1_AnOverlappingRoute_IsReported` 本身是自证的：它临时把 victim 加入本地 `familiesWithOverlap`，再断言 `covered.Intersect(familiesWithOverlap)` 包含 victim；这只是在测试 BCL 的 `Intersect`，不构成独立证据。真正有效的证据是 `EveryUncoveredCommand...` 里的 `Assert.Empty` 与我的变异实验。
2. "5/5 变红"与"186/0/26/212"是错误/过期数字；实际为 **2 failed / 3 passed** 和 **187 passed / 0 failed / 26 skipped / 213 total**。
3. README §4.1 已更正性质，但测试类注释、README §1/§2、任务卡标题/正文仍残留"生产可达性 / 两通路"表述；README §2/§3 仍写"4 个 Fact / 4 passed"；任务卡称 README §4.2 说明了 AC3 的边界，但 README §4.2 实际没有该说明。

按"P2-1 功能已闭合、P2-2/P2-3 实质更正确已落地，剩余为表述/登记"的标准，我判定为 ACCEPT_WITH_LIMITATIONS，而不是 REJECT；若项目把上述错误数字也视为 P2 证据问题，则应在集成前修正。

## 2. r1 findings 的 r2 状态

| r1 finding | r2 状态 | 依据 |
|---|---|---|
| **P2-1** 未强制 exactly one route | **CLOSED（功能）**；新增测试自证为 **P3** | 见 §3；`EveryUncovered...:110` 的 `Assert.Empty` 在变异下失败 |
| **P2-2** "生产可达性/两通路"表述过强 | **PARTIAL**：README §4.1 已正确；测试类注释、README §1/§2、卡面标题仍有残留（P3） | `CommandCoverageRoutingTests.cs:7`；`README:18,29`；卡面 `:3,44` |
| **P2-3** 错误归因 `extract-command-surface.py` | **CLOSED** | README §4.3 与实测一致；无残留保证句 |
| **P3** FEA-09 越界证据 | **CLOSED** | `git diff 9a79b2a69..073f00b02 -- verification/FEA-09/logs/wire-redacted.ndjson` 为空 |
| **P3** 186/0/26 未进日志 | **PARTIAL**：行已进日志，但数字是旧的 186/212 | `four-pieces.log:15-18`；实际 187/213 |
| **P3** TASK_LEDGER 过期 | **CLOSED** | 账本 608/608/0、non-terminal 7；与 `task_ledger.py` 输出一致 |
| **P3** AC3 自证 | **NOT CLOSED**：卡面称 README §4.2 说明了边界，README §4.2 实际没有 | 卡面 `:115`；`README:51-58` |

## 3. P2-1 闭合实验（我亲自重做）

### 实验步骤

1. 在 `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:505-513` 的公开 `SourceSyncCommandNames` 中加入 `"create_region"`（`create_region` 是 Region 域命令，已被六个 typed service 覆盖）。
2. 运行：
   `dotnet test tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Debug --filter "FullyQualifiedName~CommandCoverageRoutingTests" --nologo`
3. 还原：`git checkout -- apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`；核对 blob 与 HEAD 一致；`git status --short` 为空。

### 实验结果

**失败：2 failed / 3 passed（共 5）**：

- `EveryUncoveredCommand_BelongsToADispatcherRoutedFamily` 在 `CommandCoverageRoutingTests.cs:110` 的 `Assert.Empty(covered.Intersect(families, StringComparer.Ordinal))` 失败，集合为 `["create_region"]`；
- `P2_1_AnOverlappingRoute_IsReported` 在 `:160` 的同形 baseline `Assert.Empty` 失败，集合同样为 `["create_region"]`；
- `SixServices...`、`EveryDomain...`、`AC3...` 仍通过（它们不检查服务/族重叠）。

**结论：重叠现在确实会被抓到，P2-1 的功能缺口闭合。** 但 evidence/卡面/commit 所称的 **"5/5 变红" 不成立**；正确表述是"2/5 failed，含专门的重叠守卫与新增测试的 baseline；其余 3 条不检查该不变量"。

### 新增测试是否只是自证？

**是。** `P2_1_AnOverlappingRoute_IsReported`（`:149-167`）：

```csharp
var familiesWithOverlap = new HashSet<string>(families, StringComparer.Ordinal) { victim };
Assert.Contains(victim, covered.Intersect(familiesWithOverlap, StringComparer.Ordinal));
```

`familiesWithOverlap` 是测试本地构造的集合，`victim` 又是从真实 registry 选出的已覆盖命令；随后断言"把它加进去后交集包含它"只是在验证 `System.Linq.Enumerable.Intersect` 的行为，并没有调用生产代码或生产守卫。它前面那行 `Assert.Empty(covered.Intersect(families))` 与 `EveryUncovered...:110` 是同一个断言；在变异实验中它确实先失败，因此这个测试的唯一有效部分是重复守卫，后面的"真实数据探针"是死代码（baseline 失败后不会执行到）。

**判定**：P2-1 的闭合来自 `EveryUncovered...:110` 的 `Assert.Empty`，不是这个新测试。建议删除 `P2_1_AnOverlappingRoute_IsReported`，或把它改为对共享谓词的直接测试（例如把 `Overlaps` 提取为 helper 并对空集/单元素集/真实集分别断言），不要再以"真实数据探针"作为证据。

## 4. 表述与证据残留（P3）

### 4.1 "生产可达性 / 两通路"仍未清干净

- `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandCoverageRoutingTests.cs:7`：仍写
  `every production command is reachable through exactly one route — either one of the six typed HostDomainService ports, or the HostCommandDispatcher direct family`。
  这正是 r1 P2-2 指出的过强说法；README §4.1 已更正，但测试类注释未同步。
- `verification/CMD-COVERAGE-ASSERT-FIX/README.md:18`（"断言与现行两通路架构不符"）和 `:29`（"说明 E-1 与两通路架构"）仍使用"两通路架构"，与同一文件 `:44-49` 的更正自相矛盾。
- `doc/tasks/CMD-COVERAGE-ASSERT-FIX.md:3`（标题"恢复命令可达性守卫"）与 `:44`（"现行两通路架构"）仍在用旧口径；卡面 `:110` 的 r1 处置表虽然写了"不证明生产可达性"，但标题/来源段未同步。
- 这些都是文档/注释层面，不改变测试行为；判为 **P3**。

### 4.2 测试数量与全量数字过期/错误

| 位置 | 写的 | 实际（本次实测） |
|---|---|---|
| `README:28` | "4 个 `[Fact]`" | **5** 个 |
| `README:37` | "4 passed（76 ms）" | **5 passed**（16 ms；时间随运行变化） |
| `README:56` | 重叠实验 "**5/5 变红**，此前 4/4 绿" | **2 failed / 3 passed**；r1 时 4/4 绿 |
| `four-pieces.log:15-16` | "186 passed / 0 failed / 26 skipped / 212 total" | **187 / 0 / 26 / 213** |
| `doc/tasks/...:86` | AC1/AC2 "4 passed（76 ms）" | 5 passed |
| `doc/tasks/...:90` | AC6 "186 / 0 / 26" | 187 / 0 / 26 / 213 |
| `doc/tasks/...:109` | "5/5 变红" | 2/5 failed |
| commit message | "5/5 变红"；"P3：four-pieces.log 补上 186/0/26/212" | 2/5 failed；187/0/26/213 |

这些是**证据准确性**问题，不改变 P2-1 的闭合结论；但集成记录若引用旧数字，会与当前树不符。判为 **P3**，建议在集成前统一修正为"5 passed"、"2 failed / 3 passed"、"187/0/26/213"。

### 4.3 AC3 边界说明未实际落地

卡面 `:115` 写"已在 README §4.2 说明其证明的边界（谓词有效，非独立证据源）"，但 README §4.2 `:51-58` 只有"AC3 已证：合成命令与从真实覆盖集移除一条命令两种方式都能报出"，没有任何"非独立证据源/自证边界"的表述，反而再次强化了 AC3 的证明力。该 P3 登记与文本不一致，建议要么在 README §4.2 补一句边界说明，要么修正卡面。

## 5. 范围与回归检查

- `git show --stat 073f00b02` 含：测试文件、TASK_LEDGER、r1 报告、卡面、README、`four-pieces.log`、FEA-09 日志（-1 行）。
- **无 `src/**` 改动**：`git diff --name-only 9a79b2a69..073f00b02 -- 'apps/desktop-avalonia/src/**'` 为空。
- FEA-09 的 -1 行是**回退修复**：`git diff 9a79b2a69..073f00b02 -- verification/FEA-09/logs/wire-redacted.ndjson` 为空；净 diff 不含该文件。不是新增越界。
- `doc/reviews/CMD-COVERAGE-ASSERT-FIX-review-r1.md` 是 r1 复核产物，属于允许的 `doc/reviews/CMD-COVERAGE-ASSERT-FIX-*.md`。
- 未见新增 skip/xfail；新测试均为 `[Fact]`。
- TASK_LEDGER 已与 `python tools/governance/task_ledger.py` 一致：608 files / tracked 608 / untracked 0 / non-terminal 7。

## 6. 复跑结果

| 项 | 结果 |
|---|---|
| `CommandCoverageRoutingTests`（无夹具） | **5 passed / 0 failed / 0 skipped** |
| 重叠变异后同 filter | **2 failed / 3 passed**（见 §3） |
| `DomainServices_CoverEveryCommandExactlyOnce`（旧 sidecar） | **1 passed**（623 ms） |
| 无夹具全量 `NewManga.CoreClient.Tests` | **187 passed / 0 failed / 26 skipped / 213 total**（21 s） |
| `check.ps1` | PASS（3 warnings） |
| `verify_pins.ps1` | 18/18 PASS |
| `generate_api_inventory.py --check` | exit 0 |
| `extract-command-surface.py --check` | exit 0 |
| `task_ledger.py` 汇总 | 608 / tracked 608 / untracked 0 / non-terminal 7（与账本一致） |

实验和全量运行后均已还原 FEA-09 日志；最终 `git status --short` 为空（写入本报告前）。

## 7. 我没有验证的面

- 未做真实 GUI/Host 对 21 条命令的端到端调用；未验证带 sidecar 的整包套件（E-2 限制）。
- 未逐条核对 21 条命令的 Python Core handler；README §4.3 已明确属未验证面。
- 未重跑 r1 的 `settings_get` 重叠实验（新断言是任意 `covered ∩ families`，逻辑上覆盖；`create_region` 实验已足够）。
- 未检查 `core-command-probe.json` 25 条之外的 Core 路由。

## 8. 能否进入集成

**可以进入集成，按 ACCEPT_WITH_LIMITATIONS 处理。**

建议在集成提交或集成记录中同时完成以下 P3 清理（不需要生产代码改动）：

1. 删除或改写自证的 `P2_1_AnOverlappingRoute_IsReported`，明确真正的证据是 `EveryUncovered...:110` 的 `Assert.Empty` 与本次变异实验；
2. 把"5/5 变红"改为"2 failed / 3 passed"；把全量数字改为"187/0/26/213"；把"4 个 Fact / 4 passed"改为 5；
3. 同步测试类注释、README §1/§2、任务卡标题/来源段的"生产可达性/两通路"措辞；
4. 在 README §4.2 补上 AC3 的边界说明，或修正卡面 `:115` 的登记。

如果项目把上述证据数字/表述视为 P2 而不是 P3，则应在完成第 2、4 项后再集成；就我的判定，P2-1/P2-3 的实质问题已闭合，当前可带 P3 进入集成。
