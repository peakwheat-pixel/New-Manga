# FEA11-ENTRY-MISSING-1 收口 / MAPMINT-ERROR-FIDELITY-1 supersede 独立复核

| 字段 | 值 |
|---|---|
| task_id | `FEA11-ENTRY-MISSING-1`、`MAPMINT-ERROR-FIDELITY-1` |
| reviewer_kind | `subagent`（DSH 派发的独立上下文子 agent；未参与实现） |
| author | `DSH`（两卡收口/建卡提交作者） |
| reviewed_head | `c9599f761`（`c9599f7610b30e1ad84d83726d60d85830d18002`，main） |
| reviewer | `reviewer-fea11`（DSH 子 agent；独立上下文；**未参与** `FEA11-ENTRY-MISSING-1` / `MAPMINT-ERROR-FIDELITY-1` / `MINT-FAILURE-DIAG-1` 的任何实现、诊断、收口、测试编写或裁定） |
| reviewed_at | `2026-11-17T18:49:52+08:00` |
| 复核范围 | 只读；除本报告外未修改任何文件；未 commit / push / checkout；未改卡面、源码、测试、证据 |
| 被审对象 | `doc/tasks/FEA11-ENTRY-MISSING-1.md`（`closed_with_limitations`）、`doc/tasks/MAPMINT-ERROR-FIDELITY-1.md`（`superseded`） |
| 结论 | FEA11：**ACCEPTED_WITH_FINDINGS**；MAPMINT：**ACCEPTED_WITH_FINDINGS**；两卡均可保持当前状态，但 FEA11 须先处置 3 项 P1（纯文档，不改 AC 标记） |

> 边界声明：**本复核不构成产品发布验收**，不改变 `Technical Gate=NOT_SATISFIED`，不表示条件 3 通过，也不声称任何产品缺陷已修复。

---

## 0. 复核方法

- 只读读取 Task、Review、Handoff、源码、测试与 `verification/**`；所有结论以 head `c9599f761` 的实际字节/实跑为准，不采信卡面自述。
- 重跑 opt-in 测试 3 次；重跑 `MapMintFailureDiagnosticsTests` 1 次（3 facts）。
- 测试环境变量按要求指向仓库外：

```powershell
New-Item -ItemType Directory -Force -Path "G:\CODEX\New Manga.workspace\tmp\review-fea11\" | Out-Null
$env:NEWMANGA_EVIDENCE_DIR="G:\CODEX\New Manga.workspace\tmp\review-fea11\"
$env:NEWMANGA_READER_OVERLAY_EVIDENCE_DIR="G:\CODEX\New Manga.workspace\tmp\review-fea11\"
$env:NEWMANGA_FEA11_IPC="1"
```

- 跑前/跑后 `git status --porcelain` 均为空（报告落盘前最后一次测量：空）。测试日志只写入 `G:\CODEX\New Manga.workspace\tmp\review-fea11\`，未进入仓库。

### 五项逐条判定（摘要）

| # | 复核项 | 判定 | 关键实测 |
|---|---|---|---|
| 1 | FEA11 收口是否成立 | **有条件成立**（ACCEPTED_WITH_FINDINGS；P1×3） | `blocked` 的诊断前提已由 `c68a67216` 真实解除；但 L-FE11-1 事实错误、AC3 测试已改判、PLAN 仍写 BLOCKED |
| 2 | MAPMINT `superseded` 是否成立 | **成立，有差额**（ACCEPTED_WITH_FINDINGS；P2×4） | 能力等价（`OriginalExceptionType` + 3 facts 3/0/0）；AC5 无原始 red 日志等证据形式差额 |
| 3 | 历史证据字节是否未动 | **PASS** | `git diff c9599f761^ c9599f761 -- verification/` 为空；三个 BLOB pin 与卡面一致 |
| 4 | 门禁 `check.ps1` | **PASS (3 warnings) / EXIT=0（两卡）** | 但 PASS 不覆盖 `PLAN:60` 的 `BLOCKED` 与终态卡冲突 |
| 5 | 审查者字段真实性 | **FEA11 有本报告为来源；MAPMINT 为 null** | FEA11 字段为预约式署名，本报告使其成立；MAPMINT 无 Review，如实为 null |

---

## 1. FEA11-ENTRY-MISSING-1 收口判定

### 1.1 关键实测

#### （a）`MINT-FAILURE-DIAG-1` 确实在 `c68a67216` 交付了诊断能力

`git show c68a67216 --stat` 实测：

```
 .../NewManga.Host/Sources/SourceReadCoordinator.cs |  8 +--
 .../src/NewManga.Host/Sources/SourceSecurity.cs    | 18 +++++-
 .../MapMintFailureDiagnosticsTests.cs              | 64 ++++++++++++++++++++++
 doc/REBASELINE_PLAN.md                             |  2 +-
 verification/MINT-FAILURE-DIAG-1/README.md         | 54 ++++++++++++++++++
 5 files changed, 140 insertions(+), 6 deletions(-)
```

`git show c68a67216`（完整 diff）确认：

- `SourceSecurity.cs`：`SourceAccessException(string code, Exception? inner = null)`；新增
  `public string? OriginalExceptionType => InnerException?.GetType().Name;`；并
  `public override string Message => Code;`（head 行号：`SourceSecurity.cs:9,20,27`）。
- `SourceReadCoordinator.cs`：`MapMintFailure` 的**每个**分支（含 `_ =>` 兜底）都把 `error` 作为 inner 传入
  （head 行号：`SourceReadCoordinator.cs:357-364`；兜底在 `:363`）。
- 新增 `MapMintFailureDiagnosticsTests.cs`（3 个 `[Fact]`），断言公共码不变且原始类型可观察。

⇒ 该提交不是“卡面声称”，而是真实代码 + 测试入库。**AC2 的交付来源属实，且卡面明确写成“由 MINT-FAILURE-DIAG-1 交付”，没有把 AC2 写成本卡自己交付。**

#### （b）opt-in 测试实测

命令（第 1 次，含 build）：

```powershell
$env:NEWMANGA_FEA11_IPC="1"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved"
```

实测输出：

```
已通过! - 失败: 0，通过: 1，已跳过: 0，总计: 1，持续时间: 3 s - NewManga.Host.Tests.dll (net9.0)
EXIT=0
```

随后以 `--no-build` 在同一 head 再跑 2 次：

- 第 2 次：`失败: 0，通过: 1，已跳过: 0，总计: 1，持续时间: 4 s`，`EXIT=0`
- 第 3 次：`失败: 0，通过: 1，已跳过: 0，总计: 1，持续时间: 3 s`，`EXIT=0`

⇒ **数值上“连续 3 次通过 / 1 passed / 0 failed / 0 skipped / EXIT=0”成立**（当前 head 实测 3/3）。

#### （c）诊断测试实测

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~MapMintFailureDiagnosticsTests"
```

实测：

```
已通过! - 失败: 0，通过: 3，已跳过: 0，总计: 3，持续时间: 3 ms - NewManga.Host.Tests.dll (net9.0)
EXIT=0
```

⇒ 卡面 AC2 的“3 facts 实测 3 passed / EXIT=0”属实。

### 1.2 AC1–AC4 逐条核对

| AC | 卡面断言 | 实测 | 判定 |
|---|---|---|---|
| AC1 | 失败点在 `SourceReadCoordinator.DescribeContainer` 的 `FileStream` 打开处；排除种子未生成 `new_zip` / 路径非绝对 / schema 不符 | `SourceReadCoordinator.cs:378` 为 `DescribeContainer`，`:384` 为 `new FileStream(...)`；`verification/FEA11-ENTRY-MISSING-1/README.md` §1–§3 记录了基线堆栈与种子排除项。本轮未独立重跑种子，但 opt-in 测试通过说明 fixtures 能正常生成并打开容器 | 字面成立；排除项为既有证据，未另行复测 |
| AC2 | 诊断能力由 `MINT-FAILURE-DIAG-1`（`c68a67216`）交付：`OriginalExceptionType`、`Message` 严格等于 `Code`、3 facts 3 passed | 见 §1.1(a)(c)；代码与测试均在该提交；实测 3/0/0、`EXIT=0` | **成立**；来源归属正确，未据为己有 |
| AC3 | 触发本卡的 `ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`（`NEWMANGA_FEA11_IPC=1`）在当前 head 连续 3 次通过 | 数值 3/3 通过、`EXIT=0`；但该测试在 `2d34914c2` 已被改成**断言 typed 拒绝**（见 §1.3），当前断言的是 `SOURCE_PLAN_UNAVAILABLE`，不再是原 ACK 成功链 | **数值成立；作为“复现复核”的语义不成立（P1-2）** |
| AC4 | 不虚报：不声称历史失败根因已定位（当前仅“不可复现”）；不声称条件 3 MET 或产品无缺陷 | 卡面确实没有声称条件 3 MET 或产品无缺陷；但把“根因未定位”写成限制项（L-FE11-1），与仓内已 `done` 的根因定位证据冲突（见 §1.3） | **AC4 字面成立**（未做那三项声称），但限制项文本错误（P1-1） |

### 1.3 核心问题：L-FE11-1 与 AC3 的“复现”不属实

#### 事实链（均可复验）

1. **根因已被定位为 E-9**：
   - `doc/tasks/FEA11-RECOVERY-ROOT-PATH-1.md`（`status: done`，commit `6cb4cc5fb`）标题即“定位恢复路径把 registry root 当容器（产品缺陷 E-9，P2）”，并写“已确认 `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain...` 因此失败”。
   - `verification/FEA11-RECOVERY-ROOT-PATH-1/README.md:20-49,72` 给出完整调用链与根因：`MintRecoveryGrantsAsync` 把 `roots[0]` 当 `sourcePath`，`DescribeContainer(目录)` 触发 `UnauthorizedAccessException`，修复前被兜底成 `SOURCE_ENTRY_MISSING`。
   - `verification/MINT-FAILURE-DIAG-1/README.md` §3 也写明“被拒绝的是 fixture 的 root 目录……某处把目录当容器传给 `DescribeContainer`”。

2. **触发测试的原始期望已被改判，不是在“复现”原失败**：
   - `git show 2d34914c2 -- .../Fea11Residual4AIpcTests.cs` 把步骤 (5) 从 `Assert.Equal("acknowledged", ...)` 改为：
     ```csharp
     var ackFailure = await Assert.ThrowsAsync<SourceAccessException>(...);
     Assert.Equal("SOURCE_PLAN_UNAVAILABLE", ackFailure.Code);
     ```
     并新增状态无损 / 幂等 / catalog 空断言（head：`Fea11Residual4AIpcTests.cs:172-206`）。
   - 该测试的 fixture 仍然注册**目录**：`runtime.Registry!.Register("fea11-r4a", [root])`（`Fea11Residual4AIpcTests.cs:67`）。
   - 当前产品实现 `SourceOperationCoordinator.IsRecoverableRoot` 为 `sourceKind == "folder" || File.Exists(root)`（`:204-205`）；对 `zip` + 目录 root 返回 false，`MintRecoveryGrantsAsync` 抛 `SOURCE_PLAN_UNAVAILABLE`（`:312-315`）。
   - 因此该测试是“**目录 root + 容器 kind → 断言 typed 拒绝**”的测试，而不是“原 ACK 成功链复现并通过”。`E9-PRODUCT-ADJUDICATION-zcode-2026-11-15.md` §测试口径与 `E9-KNOWN-LIMITATION-TESTS-1.md` 均明确记录“旧 acknowledged 期望从未可达”，改为断言拒绝是**产品约束改判**。

3. **“根因未定位”与仓内状态冲突**：
   - `MAINT-1-EXISTING-FINDINGS-2026-11-14.md` 的 E-9 节标题写“**已修复**，2026-11-15 定位 / 2026-11-15 解锁”，修复 commit `366704138`；其修复范围是**文件型 root** 的恢复路径（`IsRecoverableRoot` 的 `File.Exists(root)` 分支）。
   - 本卡测试使用**目录 root**，仍在 fail-closed 分支；`E9-LIMITATION-DOC-1`/`E9-KNOWN-LIMITATION-REGISTER.md` 承载“目录 root + 容器 kind 仍 typed 拒绝”的边界。
   - 因此准确表述不是“根因未定位”，而是：**根因已定位为 E-9；生产文件型 root 的恢复已按方案 E 解锁；本卡测试的目录 root 场景仍按 fail-closed typed 拒绝，测试断言已改判，不能据此声称原 ACK 成功链可用，也不能声称本卡测试场景已修复。**

4. **不可写成“已修复”**：本复核不建议、也不认为可以把 L-FE11-1 改成“已修复某缺陷”。E-9 的“已修复”只覆盖文件型 root 路径；FEA11 触发测试的目录 root 场景仍是 typed 拒绝。正确的收口口径应是“根因已定位 + 测试口径已改判 + 本卡不声称该测试场景修复”，而不是“已修复”。

> 结论：**L-FE11-1 的“历史根因未复现 / 根因未定位”不属实**。它既与 `FEA11-RECOVERY-ROOT-PATH-1`（done）冲突，也掩盖了 `2d34914c2` 的测试改判。该问题属于收口记录的事实错误，属于 P1；**不要求也不建议把 AC 改成非 MET**（AC3 数值确实 3/3；问题在证据语义与限制文本）。

### 1.4 权威指针冲突

- `doc/REBASELINE_PLAN.md:60` 仍写：
  ```
  READY 节点：无；ACTIVE：MAINT-1；BLOCKED：FEA11-ENTRY-MISSING-1
  ```
- 但 `doc/STATUS.md:7` 已把 `FEA11-ENTRY-MISSING` 计入 `closed_with_limitations`；`doc/TASK_LEDGER.md` 的 non-terminal 只有 `MAINT-1-RELEASE-MONITOR` 与 `RELEASE-GATE4-SIGNED-MATRIX-1`。
- 收口 commit `6619e70b9` 只改了 PLAN 第 61 行（表外节点枚举），**没有改第 60 行的 `BLOCKED`**；`check.ps1` 仍 PASS（见 §4），说明该检查不校验“终态 Task 仍列在 BLOCKED”。
- `doc/handoffs/NEXT-SESSION-STARTER.md:1251` 也仍把 FEA11 标为 `blocked`（历史表行未同步），会误导下一会话。

⇒ 这是权威 DAG 与卡面/STATUS 的直接矛盾，属于 P1 集成收口缺陷；仅改文档即可修复。

### 1.5 FEA11 结论与 findings

**decision：`ACCEPTED_WITH_FINDINGS`**

核心理由：本卡 `blocked` 的唯一前提（产品诊断能力不足）已由真实提交 `c68a67216` 解除；AC2 归属正确；AC3 数值 3/3 通过；AC4 未做禁止的声称。但收口的**限制文本**、**AC3 证据语义**与**权威指针**均有 P1 级问题。

| ID | 级别 | finding |
|---|---|---|
| FEA-P1-1 | P1 | L-FE11-1 写“历史根因未复现 / 根因未定位”，与 `FEA11-RECOVERY-ROOT-PATH-1`（done）及 `MINT-FAILURE-DIAG-1` 证据冲突；根因已定位为 E-9（目录 root 被当容器），且触发测试在 `2d34914c2` 已改为断言 `SOURCE_PLAN_UNAVAILABLE`。不得改写成“已修复”；应改成“根因已定位 + 测试口径已改判 + 不声称该场景修复”。 |
| FEA-P1-2 | P1 | AC3 的“复现复核 / 连续 3 次通过”只证明改判后的测试通过；测试断言已是 E-9 typed 拒绝，不是原 ACK 成功链。卡面未披露 `2d34914c2` 与 `E9-PRODUCT-ADJUDICATION`，证据语义误导；不得据此声称历史失败已消失。 |
| FEA-P1-3 | P1 | `doc/REBASELINE_PLAN.md:60` 仍 `BLOCKED：FEA11-ENTRY-MISSING-1`，与卡面 `closed_with_limitations`、`STATUS.md:7`、`TASK_LEDGER` 冲突；`check.ps1` PASS 未覆盖此矛盾。 |
| FEA-P2-1 | P2 | `depends_on` 只列 `FEA11-SEED-PIXEL-1`，未列 AC2/EV-FE11-03 实际依赖的 `MINT-FAILURE-DIAG-1`；证据链在依赖字段上不可追溯。 |

---

## 2. MAPMINT-ERROR-FIDELITY-1 的 `superseded` 判定

### 2.1 卡面状态与实现事实

- 卡面：`status: superseded`、`owner: null`、`reviewer: null`、`base_commit: null`、`evidence_dir: verification/MAPMINT-ERROR-FIDELITY-1`（该目录不存在）、`canonical_evidence_status: complete`、`resource_closeout_status: complete`。
- 卡面 6 个 AC 全部标 `[ ]` + `<<NOT_APPLICABLE: 已由 MINT-FAILURE-DIAG-1（commit c68a67216）交付>>`；测试要求表全部 `NOT_RUN`；无自己的证据与测试。
- `MINT-FAILURE-DIAG-1` 的实际交付见 §1.1：`OriginalExceptionType` + `Message => Code` + 每个分支传 inner + 3 个 facts；实测 3/0/0、`EXIT=0`。

### 2.2 AC1–AC6 逐条等价性

| AC | 卡面要求 | MINT 实际交付/证据 | 等价性 |
|---|---|---|---|
| AC1 现状取证 | 定位 `MapMintFailure` 与 `_ =>` 兜底（给行号），用现有测试复现“无法区分内层异常类型” | 代码在 `SourceReadCoordinator.cs:357-364`（head 实测行号），兜底 `:363`；修复前无法区分的事实由 FEA11 基线证据（`8ca6a36ff`）与 `c68a67216` commit message 记录。**但 MINT 的 verification README 未记录行号，也无“修复前 red”的原始日志** | **实质等价，证据形式部分** |
| AC2 内层类型保真 | 兜底路径把 `FileNotFoundException` / `UnauthorizedAccessException` / 其他写入内部诊断；不改公共码 | `OriginalExceptionType` + `InnerException`；所有分支含 `_ =>` 都传 `error`；公共码逐字未变。测试实测 3/0/0 | **等价** |
| AC3 公共契约零变更 | `git diff` 证明 wire/Schema/公共错误码表未改 | `git show --name-only c68a67216` 仅 5 个文件：两个 Host 源码、1 个测试、PLAN、verification README；`git diff c68a67216^ c68a67216 -- doc/contracts doc/design` 为空；错误码字符串未改 | **按卡面“wire/Schema/错误码表”口径等价**；但 `SourceAccessException` 作为 public 类新增了可选构造参数与 `OriginalExceptionType` 属性，属**加法式公共表面**，不是字面“零变更”（P2-M3） |
| AC4 回归断言 | 三类内层异常各一条映射断言；断言不写绝对路径/敏感消息 | `MapMintFailureDiagnosticsTests` 覆盖 `FileNotFoundException`、`UnauthorizedAccessException`、`IOException`、`ArgumentException`、`InvalidOperationException`；断言只用 `"probe"`/`"gone"`/`"nope"` 等短消息，未写路径；产品 `Message` 仍等于 `Code` | **等价** |
| AC5 判别力 | 临时回退保真逻辑 → 新测试变红；还原 → 通过 | commit message 与 MINT README 均写“去掉两个 `SOURCE_ENTRY_MISSING` 分支的 `, error` → 2 failed / 1 passed；恢复 → 3 passed”；**没有落盘原始日志**。静态核对：3 个 fact 分别断言 `InnerException` 非空与 `OriginalExceptionType` 精确值，去掉 `, error` 必然变红，断言确有判别力 | **能力等价，证据形式不足（无日志）** |
| AC6 证据与边界 | 跑相关测试套件并记录 pass/fail/skip；不宣称 FEA11 归因结论已改变 | commit message 记录“无夹具 Host.Tests 325 / 0 / 74 / 399”；MINT README 又写“本卡未跑三项目全量”，两项口径不完全一致；无原始日志。MINT commit/README 还明确宣称“FEA11 的 blocked 由此解除 / 原因不再是未知”，**超出** AC6“不宣称归因结论已改变”的边界（虽然该结论是真实的） | **部分等价（P2-M2）** |

### 2.3 结论

`MINT-FAILURE-DIAG-1` 的**能力**与 MAPMINT 的 AC1–AC6 实质等价：内层异常类型已保留、公共错误码未变、映射断言存在且可判别、边界清楚。差额集中在**证据形式**（无 AC5 回退 red 日志、AC1 行号/修复前记录不在 MINT README、AC6 边界措辞被突破）与**元数据**（MAPMINT 自己的 `evidence_dir` 不存在、reviewer 为 null）。这些差额不足以否定 `superseded`，因为需要实现的能力已真实入库并经本复核实测。

**decision：`ACCEPTED_WITH_FINDINGS`**

| ID | 级别 | finding |
|---|---|---|
| MAP-P2-1 | P2 | AC5 的“回退 → 变红”只有 commit message 与 README 自述，没有原始测试日志；本复核只能静态确认断言有判别力，**不能**把它当作已复跑的执行证据。 |
| MAP-P2-2 | P2 | AC1/AC6 的证据形式不完整：MINT README 未给行号、未留“修复前 red”日志；AC6 的“不宣称 FEA11 归因结论已改变”被 MINT commit/README 的“blocked 由此解除 / 原因已知”突破。 |
| MAP-P2-3 | P2 | AC3 的“公共契约零变更”按 wire/Schema/错误码表成立，但 `SourceAccessException` 新增了可选构造参数与 `OriginalExceptionType` 公共属性；属加法式公共表面，不是字面零变更。应把“内部诊断属性、非 wire/Schema/不改变既有 Message 文本”写清楚。 |
| MAP-P2-4 | P2 | 卡面 `evidence_dir: verification/MAPMINT-ERROR-FIDELITY-1` 指向不存在的目录，而 `canonical_evidence_status: complete`；`reviewer: null` 且无本卡 Review。资源清单写了“本卡未产生证据目录”，字段层面仍不一致。 |

---

## 3. 历史证据字节未动

命令与结果：

```powershell
git diff c9599f761^ c9599f761 -- verification/
# 输出为空，EXIT=0
```

补充按卡面 `sha256_basis: BLOB` 复核（`git show <commit>:<path>` 后计算 SHA-256）：

| 证据 | 卡面声明 sha256 | 实测（BLOB at cited commit） | 结果 |
|---|---|---|---|
| `verification/FEA11-ENTRY-MISSING-1/README.md` | `9bc1fd03…29f660` | `9bc1fd03…29f660` | 一致 |
| `verification/FEA11-ENTRY-MISSING-1/opt-in-rerun-2026-11-17.log` | `19942321…b4efd` | `19942321…b4efd` | 一致 |
| `verification/MINT-FAILURE-DIAG-1/README.md` | `a7c04126…146f5d` | `a7c04126…146f5d` | 一致 |

说明：工作树因 `core.autocrlf=true` 可能是 CRLF；卡面基准写明 `BLOB`，按 BLOB 复核一致。**本轮没有改动任何 `verification/**` 字节。**

**判定：PASS。**

---

## 4. 门禁（check.ps1）实测

### FEA11

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA11-ENTRY-MISSING-1.md
```

输出（逐字）：

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA11-ENTRY-MISSING-1.md
WARN: 存在 2 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3169 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6742 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

### MAPMINT

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAPMINT-ERROR-FIDELITY-1.md
```

输出（逐字）：

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAPMINT-ERROR-FIDELITY-1.md
WARN: 存在 2 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3169 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6742 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

**判定：两卡均 PASS (3 warnings) / EXIT=0。** 但该 PASS **不覆盖** `REBASELINE_PLAN.md:60` 的 `BLOCKED：FEA11-ENTRY-MISSING-1` 与终态卡冲突（见 FEA-P1-3）；检查器只证明它检查的范围通过，不证明收口指针一致。

---

## 5. 审查者字段真实性

| 卡 | 字段实测 | 判定 |
|---|---|---|
| FEA11 | `reviewer: reviewer-fea11（DSH 子 agent，独立上下文，未参与实现；2026-11-17 收口复核）` | **有真实来源**：本报告即该字段所指复核；本 reviewer 未参与三卡任何实现/诊断/收口。时序说明：字段在 `6619e70b9` 收口提交时已写入，当时报告尚未落盘，属“预约式署名”；本报告使其实质成立。 |
| MAPMINT | `reviewer: null` | **如实为 null**；本卡未实施、无 Review。本复核不冒充 MAPMINT 的实现 Review，也不替 Lead 改字段。 |

未修改两张卡的任何 frontmatter 字段。

---

## 6. 结论

### 6.1 两项 decision 与计数

| 卡 | 当前状态 | decision | P0 | P1 | P2 |
|---|---|---|---:|---:|---:|
| `FEA11-ENTRY-MISSING-1` | `closed_with_limitations` | **ACCEPTED_WITH_FINDINGS** | 0 | 3 | 1 |
| `MAPMINT-ERROR-FIDELITY-1` | `superseded` | **ACCEPTED_WITH_FINDINGS** | 0 | 0 | 4 |
| 共同项（MINT 卡缺失） | — | — | 0 | 0 | 1 |
| **合计** | — | — | **0** | **3** | **6** |

共同 P2：

| ID | 级别 | finding |
|---|---|---|
| X-P2-1 | P2 | 两张卡都把 `MINT-FAILURE-DIAG-1` 当“他卡”引用，但仓库中**没有** `doc/tasks/MINT-FAILURE-DIAG-1.md`（`git log --all -- doc/tasks/*MINT*` 无记录）；该能力只有 commit `c68a67216` + `verification/MINT-FAILURE-DIAG-1/README.md`，无 owner/reviewer/status。能力本身真实，但卡面级的“他卡交付”不可追溯，建议在 FEA11 的 Closeout 或 MAINT 台账中补一条最小登记。 |

### 6.2 明确回答：两卡能否保持当前状态

- **FEA11-ENTRY-MISSING-1：可以保持 `closed_with_limitations`，但有条件。**
  必须先把 FEA-P1-1（L-FE11-1 事实错误）、FEA-P1-2（AC3 未披露 E-9 测试改判）、FEA-P1-3（PLAN 仍写 `BLOCKED`）以**纯文档**方式处置。处置前，卡面、STATUS 与权威 PLAN 互相矛盾，不能算“正确闭合”。处置时：**不要改 AC 标记**（AC3 数值确实 3/3）；**不要把“根因已定位”写成“已修复该测试场景”**；**不要声称条件 3 MET**；可以在卡尾追加一段更正（不修改已 pin 的证据字节），说明“根因已定位为 E-9；测试已按裁决改为断言 typed 拒绝；本卡不声称该测试场景修复”。

- **MAPMINT-ERROR-FIDELITY-1：可以保持 `superseded`。**
  `MINT-FAILURE-DIAG-1` 的能力已真实交付并经实测（`OriginalExceptionType` + 3 facts 3/0/0 + 公共码不变）；MAPMINT 无需重开实现。P2 差额（AC5 无原始 red 日志、AC1/AC6 证据形式、AC3 加法式公共表面、卡面 `evidence_dir` 不存在）记录即可，不构成状态阻断。

- **总体：两卡均可保持当前状态；FEA11 是“有条件保持”，MAPMINT 是“直接保持”。**

### 6.3 本复核不构成产品发布验收

**本复核不构成产品发布验收。** 不改变 `Technical Gate=NOT_SATISFIED`；条件 3 仍是 `AGENT_ADJUDICATION_PENDING`；不声称 E-9 全部修复；不声称 `Fea11Residual4AIpcTests` 的 ACK 成功链可用；不声称“不可复现”等于“已修复”。

### 6.4 建议下一步

1. Lead 在本报告基础上追加 FEA11 的 P1 处置（L-FE11-1 更正 + AC3 的 E-9 披露 + `REBASELINE_PLAN.md:60` 改为 `BLOCKED：无` 或与终态一致），不修改 AC 标记与已 pin 证据。
2. MAPMINT 保持 `superseded`，在卡面补记 P2 差额；无需重开实现。
3. 在台账或 MAINT 卡补一条 `MINT-FAILURE-DIAG-1`（commit `c68a67216`）的最小登记，避免“他卡交付”无卡可查。
