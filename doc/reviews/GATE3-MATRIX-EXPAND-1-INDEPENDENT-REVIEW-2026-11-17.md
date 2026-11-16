# GATE3-MATRIX-EXPAND-1 独立复核（2026-11-17）

| 项 | 值 |
|---|---|
| 复核者 | `gate3-reviewer`（DSH 子 agent，上下文独立，未参与本卡实现与返修） |
| 复核对象 | 卡片 `doc/tasks/GATE3-MATRIX-EXPAND-1.md`；交付物 `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §10 |
| 被审 head | `41a68b00d47d6101c1cff703a3eae7033ad5cfdf` |
| 卡片交付 commit | `eb8b5c82a`（唯一改动本卡的提交） |
| 基线 commit（卡片声明） | `13d295f69` |
| 环境 | Windows / pwsh 7 / dotnet `10.0.401` / 无 sidecar、无 opt-in 门禁变量 |
| 复核方式 | 只读 + 实跑 `dotnet test`；不修改仓库受版本控制的文件，不 commit |
| **verdict** | **REJECTED** |

## 0. 只读声明与副作用披露

- 除本报告外，**未写入任何仓库文件，未 commit、未 push、未改卡片**。
- `dotnet build` / `dotnet test` 会写 `bin/`、`obj/`（已 gitignore，`git check-ignore` exit=0 确认），属构建产物。
- **需披露的副作用（已复原）**：跑全量 App.Tests 时，仓库内测试自身改写了
  `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`（mtime `2026-11-17 03:40:22`，
  把「渲染 HEAD」由 `a1233003b` 改写为 `41a68b00d`，并删除了文件末尾的回归段）。
  该文件属 `READER-OVERLAY-HEADLESS-PNG-1` 的既有证据，**不是本卡的改动**。
  我已用 `git checkout -- <该文件>` 复原，复核结束时 `git status` 仅剩本会话前**已存在**的
  `M doc/tasks/GATE3-MATRIX-EXPAND-1.md`（见 §6）。⇒ 该测试存在**写穿仓库证据**的副作用，建议另开卡处置。

## 1. 逐条结论

| # | 复核项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 数字真实性：组合 filter「80 / 0 / 0」 | **FAIL** | 实测 **79 / 0 / 0 / 79**（两次，含重建后一次），非 80；且卡面对「多 1」的解释被实测证伪 |
| 1a | 五个类各自数字 47 / 18 / 4 / 9 / 1 | **PASS** | 逐类实跑全部一致，合计 79 |
| 2 | §10.1 / §10.2 是否含五流程实测与逐流程缺口；有无把「类名存在」写成「语义完整覆盖」 | **PASS**（附缺陷：§10.1 组合行沿用了错误的 80） | §10.1 五流程 + 组合行；§10.2 四流程逐条「覆盖了什么 / 仍缺什么」；§10.3 明确 class 级数字不证明语义完整 |
| 3 | 诚实性（AC3 / AC4）：未声称条件 3 MET，并列出未覆盖内容 | **PASS** | 卡片 AC4 与「未达成」段、§5、§10.3 均明写「条件 3 仍不判 MET」；缺口逐条列出 |
| 4 | 无代码改动 | **PASS（本卡提交为纯文档）**；按字面命令则为「非空」 | 本卡 commit `eb8b5c82a` 只改 6 个 `doc/` 文件、`apps/` 命中 0；但题面字面命令 `13d295f69..HEAD -- apps/desktop-avalonia/src` **非空**（15 files / +426 −74），成因见 §5 |
| 5 | 终态（`done`）材料完备性 | **FAIL（未就绪）** | 见 §7 逐条清单：AC 标记 0/5、Canonical Evidence 0 行、`integration_commit: null`、两处 `*_status: pending`、`reviewer: null`、声明的 `evidence_dir` 不存在 |

**总判定：REJECTED。** 主要理由是第 1 项：本卡的核心 AC1 自称「所有数字来自
`dotnet test --filter`，不用源码推断」，但其**招牌数字 80 无法复现（实测 79）**，并附带一句
被 `--list-tests` 直接证伪的成因解释。数字错误还已随 `eb8b5c82a` 进入交付物 §10.1。

## 2. 实测 #1：组合 filter（最关键项）

### 2.1 题面指定命令（原样执行）

```
cd "G:\CODEX\New Manga\apps\desktop-avalonia"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --filter "FullyQualifiedName~TrashUiTests|FullyQualifiedName~SourceRecoveryUiTests|FullyQualifiedName~V2ImmersiveReaderTests|FullyQualifiedName~F11HotkeyTests|FullyQualifiedName~FluentCommandPaletteFocus" 2>&1 | Select-Object -Last 5
```

首次（沿用既有 `bin/`）：

```
已通过! - 失败:     0，通过:    79，已跳过:     0，总计:    79，持续时间: 1 s - NewManga.App.Tests.dll (net9.0)
```

为确保不是陈旧程序集，执行 `dotnet build tests/NewManga.App.Tests/NewManga.App.Tests.csproj`（0 警告 0 错误，10.56 s）后
**原命令重跑**：

```
已通过! - 失败:     0，通过:    79，已跳过:     0，总计:    79，持续时间: 1 s - NewManga.App.Tests.dll (net9.0)
```

⇒ **79 passed / 0 failed / 0 skipped / 79 total**（两次一致）。

### 2.2 逐类实测

```
foreach ($c in @('TrashUiTests','SourceRecoveryUiTests','V2ImmersiveReaderTests','F11HotkeyTests','FluentCommandPaletteFocus')) {
  dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --filter "FullyQualifiedName~$c"
}
```

| 测试类 | 卡片自述 | 实测 | 一致？ |
|---|---|---|---|
| `TrashUiTests` | 47 / 0 / 0 | **47 / 0 / 0** | ✅ |
| `SourceRecoveryUiTests` | 18 / 0 / 0 | **18 / 0 / 0** | ✅ |
| `V2ImmersiveReaderTests` | 4 / 0 / 0 | **4 / 0 / 0** | ✅ |
| `F11HotkeyTests` | 9 / 0 / 0 | **9 / 0 / 0** | ✅ |
| `FluentCommandPaletteFocus` | 1 / 0 / 0 | **1 / 0 / 0** | ✅ |
| **五类之和** | 79 | **79** | ✅ |
| **组合 filter** | **80 / 0 / 0** | **79 / 0 / 0** | ❌ **不一致** |

### 2.3 为什么「80」不是环境差异，而是数字错误

1. **组合 filter 命中的类被枚举出来只有 5 个、合计 79 条**：

   ```
   dotnet test ... --no-build --list-tests --filter "<同一 filter>"
   total listed: 79
   F11HotkeyTests = 9
   FluentCommandPaletteFocusTests = 1
   SourceRecoveryUiTests = 18
   TrashUiTests = 47
   V2ImmersiveReaderTests = 4
   ```

   79 = 9 + 1 + 18 + 47 + 4，**没有任何第 6 个类**。

2. **卡面的成因解释不成立**。卡片第 52–53 行称「比五类之和 79 多 1，多出的那条来自
   `~CommandPalette` 还匹配到的其它类」。但：
   - 该 filter 里**根本没有 `~CommandPalette`**，只有 `FluentCommandPaletteFocus`；
   - `FullyQualifiedName~FluentCommandPaletteFocus` 是**子串匹配**，只命中 `FluentCommandPaletteFocusTests`；
   - 若把过滤词放宽成 `~CommandPalette` 才会有额外匹配，而题面/卡片给出的命令并未这样写。

3. **不是「当时是 80、后来改动」**。五个测试文件自卡片提交以来**未被任何提交改动**
   （`git log --oneline eb8b5c82a..HEAD -- <5 个测试文件>` 均为 0 commits），故在 `eb8b5c82a`
   与 `41a68b00d` 上该 filter 的测试总体应完全相同。

⇒ 「80/0/0」是**未经实测或抄写错位**的数字，并配了一句**推断出来的成因**——这正是本卡 AC1
（「不用推断、以实测为准」）自己禁止的做法。

## 3. 实测 #2：全量 App.Tests（AC5）

```
cd "G:\CODEX\New Manga\apps\desktop-avalonia"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build
```

```
已通过! - 失败:     0，通过:   962，已跳过:    11，总计:   973，持续时间: 5 m 2 s - NewManga.App.Tests.dll (net9.0)
```

| 口径 | 卡片自述（§AC5 / 卡面） | 实测 @ `41a68b00d` | 判定 |
|---|---|---|---|
| passed | 951 | **962** | ❌ 不一致（+11） |
| failed | 0 | **0** | ✅ |
| skipped | 11 | **11** | ✅ |
| total | 962 | **973** | ❌ 不一致（+11） |

- **实质结论仍成立**：0 failed、skip 仍 11、无新增 skip ⇒ 「无回归」的**性质**未被推翻。
- **但字面数字在 head 上不可复现**。且 `951 / 0 / 11 / 962` 与交付物 §9.1「无夹具回归：App.Tests
  **951 / 0 / 11 / 962**」（第 253 行）**逐字相同**，看起来是从上一张卡**复制**而非本卡重测。
  卡片把该数字写成「仍 951…」（现在时回归结论），属**未经 head 重测就作答**。
- 成因可查：`eb8b5c82a..HEAD` 之间共 **340 个 commit**，其中 ≥10 个改过
  `apps/desktop-avalonia/tests/NewManga.App.Tests`，总数因此增长 11 条。

## 4. §10 内容评审（第 262 行起）

### 4.1 是否真的包含五流程实测与逐流程缺口

- **§10.1**（第 266–278 行）：五行「流程 × 测试类 × 实测」覆盖回收站 / 源恢复 / 沉浸阅读窗口 /
  F11 沉浸开关 / 命令面板焦点，并加一行组合 filter ⇒ **五个流程/测试类都在**，与卡面一致
  （47/18/4/9/1）。**缺陷**：组合行沿用错误的 `80 / 0 / 0`。
- **§10.2**（第 280–287 行）：按流程给「覆盖了什么 / 仍缺什么」，四个流程行（F11 并入「沉浸阅读」行，
  写明「4 个 + 9 个」）。缺口写得具体且可核，例如：
  - 回收站：「ADJ-001 的完整保护矩阵是否逐条有测试，**未逐条核对**；真实文件层行为不在本类」；
  - 源恢复：「Host/Core 侧的 `source_resync` 编排在 **Host.Tests**（`Fea11HostAuthTests` / `Fea11HostAuthIpcTests`），本卡**未跑**它们」；
  - 沉浸：`headless` 不可验真实窗口全屏/边框切换，真机走查仍缺；
  - 命令面板：条目逐项执行未覆盖。
- 我抽查了 §10.2 的两处事实断言，**均属实**：
  - 源恢复 18 条方法名确实围绕 reauthorize / reset / diagnosis / scan-refresh（`--list-tests` 已列全）；
  - Host 侧 `Fea11HostAuthTests.cs`、`Fea11HostAuthIpcTests.cs` 确实存在于
    `tests/NewManga.Host.Tests/`，且本卡确实未跑它们。
- **§10.3** 明写「上表**只**证明这些流程有可执行的 GUI 测试且当前全绿，**不**证明它们语义完整」，
  并说明「47 / 18 是类级数字，未逐条核对」。

### 4.2 有没有把「类名存在」写成「语义完整覆盖」

**没有。** 全节无「已覆盖 / 全覆盖 / 语义完整」一类结论；§10.2 标题即
「**类名存在 ≠ 语义完整**」，覆盖列还自限为「从类与方法名可对应」，缺口列逐条标注
「本卡未验证」。这一节的口径是诚实的。⇒ 第 2 项 **PASS**（唯 §10.1 组合行数字需随 §2 一并改）。

## 5. 无代码改动核查

### 5.1 题面字面命令（非空）

```
git diff --stat 13d295f69..HEAD -- apps/desktop-avalonia/src
```

```
 .../ViewModels/V2/Console/ConsoleViewModel.cs      |   9 ++
 .../Views/V2/Console/ConsoleView.axaml             |   4 +
 .../V2/Studio/Controls/StudioHudRingControl.cs     |   2 +-
 .../V2/Studio/Controls/StudioInspectorPanel.cs     |   2 +-
 .../Views/V2/Studio/Controls/StudioLeaveModal.cs   |   6 +-
 .../src/NewManga.CoreClient/Bridge/HostBridgeClient.cs |  57 ++++++--
 .../src/NewManga.CoreClient/CoreServiceClient.cs   | 161 ++++++++++++++++-----
 .../src/NewManga.CoreClient/Issuer/HostIssuer.cs    |  27 +++-
 .../Transport/SidecarProcess.cs                    |  46 +++++-
 .../src/NewManga.Host/AssemblyInfo.cs              |   6 +
 .../src/NewManga.Host/Resources/TileChannel.cs      |  20 +++
 .../src/NewManga.Host/Sources/SourceAccessRegistry.cs |  58 +++++++-
 .../Sources/SourceOperationCoordinator.cs           |  35 +++++
 .../src/NewManga.Host/Sources/SourceReadCoordinator.cs |  29 +++-
 .../src/NewManga.Host/Sources/SourceSecurity.cs    |  38 ++++-
 15 files changed, 426 insertions(+), 74 deletions(-)
```

**不空 ⇒ 字面检查不通过。** 但成因与本卡无关：

- `13d295f69` 是**很早**的基线，`13d295f69..HEAD` 含 340 个提交；改动全部来自其它卡
  （`HOST-CONCURRENCY-FLAKY-1`、E7-1/E7-2、R-002/R-005、E-8/E-9 等）。
- **本卡唯一的提交 `eb8b5c82a` 只动 6 个文件，全在 `doc/` 下，`apps/` 命中 0**：

  ```
  doc/REBASELINE_PLAN.md | 2 +-
  doc/STATUS.md | 2 +-
  doc/TASK_LEDGER.md | 13 +--
  doc/checkpoints/GOAL-PROGRESS-2026-11-02.md | 13 +++
  doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md | 33 ++++++
  doc/tasks/GATE3-MATRIX-EXPAND-1.md | 118 ++++++++++++++++++++
  ```

⇒ 结论：**本卡确为纯文档改动（PASS）**；但「`13d295f69..HEAD` 的 src diff 为空」这个**检查判据本身
不成立/不可用于放行**，建议改用「本卡提交的 paths 里是否含 `apps/`」这类按卡归因的判据。

## 6. 工作区异常：本卡有**未提交**改动（非我所为）

复核开始（`2026-11-17 03:39:18`）时 `doc/tasks/GATE3-MATRIX-EXPAND-1.md` 即为 `M`（dirty），
与 head 版不同。差异（`git diff -- doc/tasks/GATE3-MATRIX-EXPAND-1.md`）三类：

1. 五条 AC 行尾补 `<<MET>>`（head 版 0/5）；
2. Canonical Evidence 填入 2 行（head 版为空表）：

   | evidence_id | path | commit | sha256 | class | sha256_basis |
   |---|---|---|---|---|---|
   | EV-G3MX-01 | `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` | `f9be610de` | `50a654d3…` | CANONICAL | raw |
   | EV-G3MX-02 | `doc/tasks/GATE3-MATRIX-EXPAND-1.md` | `eb8b5c82a` | `1a614cc8…` | CANONICAL | raw |

3. Resource Manifest 的 `待填` 改为 `—`，检查结果补「2026-11-17 复核确认只需仓库内文档」。

**我实测校验了这两个 sha256，均正确**（复刻结果，省得返修再算）：

```
doc/reviews/MAINT-1-...md（工作区，与 f9be610de 一致）= 50a654d30ecae2c43cc419430d28164e0d8abd8a0259b949b060f0615fe90d17  ✅ 与声称一致
git show eb8b5c82a:doc/tasks/GATE3-MATRIX-EXPAND-1.md（原始字节）= 1a614cc8c7ea1d814599d7daa1115841a74db14e030cfa8eecbac2577d2d5369  ✅ 与声称一致
HEAD 的该卡 blob 与 eb8b5c82a 相同（git diff --quiet eb8b5c82a HEAD -- 该卡 ⇒ 相等）
```

**但这批改动未提交，不在被审 head 内**，且**没有**修正 §2 的「80」——working tree 的卡面
（第 52–53 行）仍是 `80 passed`。故本复核以 **head 版**为准判定。

> 提示：`sha256` 校验时勿用 `git show … | Out-File` 之类的管道重编码（我第一次即因此得到
> `2d53b08…` 的伪结果），应用二进制重定向。

## 7. 终态（`done`）材料缺口清单

按 `tools/governance/check.ps1`（1580 行）的终态规则逐条核（行号为规则所在行）：

| # | 缺口 | head 现状 | 规则 | 补齐动作 |
|---|---|---|---|---|
| 1 | **AC 状态标记** | head 版 5 条 AC **0/5** 带 `<<MET>>` | `1531–1549`：gv3 且 status ∈ `in_review/approved/done/closed_with_limitations` 时，每条 AC 行末必须有 `<<MET>>` / `<<PARTIAL: 原因>>` / `<<BLOCKED: 原因>>` / `<<NOT_APPLICABLE: 原因>>`，缺失即 `Add-Error`（1547） | 5 条均补 `<<MET>>`（工作区版已补，需**提交**）。注意：`MET` 不得附原因（1557） |
| 2 | **Canonical Evidence 行** | head 版表为**空**（0 数据行） | `1092–1157`：0 行 ⇒ `'进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence'`（1157） | 提交 ≥1 条完整行（`evidence_id`/`path`/`sha256` 均非空，1171–1176）；工作区版 2 行已核正确，需提交 |
| 3 | **Resource Manifest 可验证行** | head 版 `source_path = 待填`（NOT_APPLICABLE 分支不校验，故 check.ps1 不报错，但属不可验证占位） | `1442–1504`；结果列不得为空或 `待关闭/todo/pending/tbd`（1485） | 把 `待填` 换成 `—` + 说明（工作区版已做，需提交），保持 6 列 |
| 4 | **`integration_commit`** | `null` | `1435`：`DONE 必须记录 integration_commit` | 填入集成验证后的提交 SHA |
| 5 | **`delivery_head`** | `null` | frontmatter 一致性（交付可追溯） | 填交付 head |
| 6 | **`canonical_evidence_status`** | `pending` | `1436`：done/closed_with_limitations 必须 `complete` | 提交证据表后改 `complete` |
| 7 | **`resource_closeout_status`** | `pending` | `1438`：终态必须 `complete` | 资源收口后改 `complete` |
| 8 | **`reviewer`** | `null` | 生命周期要求独立复核（本文即复核，但结论为 REJECTED） | 返修后重新复核并登记 reviewer |
| 9 | **证据目录不存在** | 卡面 `evidence_dir: verification/GATE3-MATRIX-EXPAND-1`，**该目录 `Test-Path` = False** | 声明了证据目录应可查；且终态证据路径必须存在（`1309/1322`） | 落盘本次原始测试输出（79 / 962-973 两段）到该目录，并把 evidence 行指向它 |
| 10 | **数字需按 head 重测/改口径** | 卡面「80 / 0 / 0」与「951 / 0 / 11 / 962」 | AC1/AC5 自身要求 | 改为实测 **79 / 0 / 0** 与 **962 / 0 / 11 / 973**，或明确标注为「`eb8b5c82a` 快照，当前 head 已变」 |
| 11 | **Closeout Record 与 frontmatter 自相矛盾** | Closeout 段写「canonical_evidence_status：`complete`」，frontmatter 为 `pending`，且 head 版证据表为空 | 诚实性/一致性 | 二者统一，且 `complete` 只能在证据表落地后写 |
| 12 | **无未勾选 AC** | `checked=5 / unchecked=0`，已满足 | `1441` | 无需动作（若届时仍存在未达成项，须改 `closed_with_limitations`，`1564` 禁止 done 带非 MET AC） |

补充：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GATE3-MATRIX-EXPAND-1.md`
在**当前工作区版**下输出 `PASS (3 warnings)`——**这只说明 `in_progress` 不触发终态规则**，
不构成终态就绪的证据（warnings 为 11 个非终态卡提示 + STATUS/PLAN 预算 80%）。

## 8. 复核结论与最小返修建议

**verdict: REJECTED。**

不是因「条件 3 被虚报」——诚实性这一项本卡做得对；而是因**核心 AC（AC1）自称的实测数字错了一条，
且错误成因是推断出来的**，并已进入交付物 §10.1。返修量很小：

1. 卡片第 52–53 行与 §10.1 第 275 行：`80 / 0 / 0` → `79 / 0 / 0`，**删掉**「多出的那条来自
   `~CommandPalette` 另匹配到的类」这句（filter 无该词，`--list-tests` 实测无第 6 个类）
   ——或若确有另一次不同 filter 的 80，则贴出那次命令原文，否则按 79 记。
2. AC5 与卡面总表：按 head 重测为 `962 / 0 / 11 / 973`，或显式标注快照 commit 与「当前 head 已漂移」。
3. 把已改好的 `<<MET>>`、两条 sha256 已核正确的证据行、Resource Manifest `—` **提交**。
4. 补 `integration_commit` / `delivery_head` / 两个 `*_status`，消除 Closeout 段与 frontmatter 的矛盾。
5. 在 `verification/GATE3-MATRIX-EXPAND-1/` 落盘本次两段原始测试输出（可引用本报告 §2/§3）。

另：`dotnet test` 会改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`（§0），
建议单独登记为测试副作用缺陷。

---

复核者：`gate3-reviewer`（独立上下文，未参与实现/返修）｜head `41a68b00d`｜2026-11-17

---

## 第二轮（窄确认）

| 项 | 值 |
|---|---|
| 复核者 | `gate3-reviewer`（同一独立上下文，未参与本次更正） |
| 被审 head | `9a2e7fea3`（`fix(gate3): 复核 REJECTED —— 更正 79/0/0 与 962/0/11/973 两个实测数字`） |
| 工作区 | 干净（`git status` 无 tracked/untracked 改动），工作树 == head |
| 范围 | 只核两条数字与终态材料；**未重跑**测试（沿用首轮实测 79/0/0 与 962/0/11/973） |
| **verdict2** | **REJECTED**（数字两条已修好；终态材料有 3 处**必改**项，其中 1 处会让 `done` 直接被 check.ps1 判红） |

### 1. 组合 filter 是否已写成 79/0/0/79 并注明原记 80 有误 —— **PASS**

| 位置 | 原文（grep 命中行） |
|---|---|
| 矩阵 §10.1 组合行（`MAINT-1-…md:275`） | `\| 组合 filter（以上全部） \| — \| **79 / 0 / 0**（独立复核 2026-11-17 实测：--list-tests 命中恰好 5 个类共 79 条；原记「80，比五类和多 1，来自 ~CommandPalette」**有误**——…80 从来不可复现） \|` |
| 卡片表格行（`GATE3-…md:52`） | `\| 组合 filter（上列全部）实测 **79 passed / 0 failed / 0 skipped**（2026-11-17 复核更正：原记 80 有误，`--list-tests` 命中恰好 5 类 79 条） \| — \| 79 / 0 / 0 \|` |
| 结论（`:114`） | `**结论（限定）**：…合计 **79 个通过 / 0 skip**（2026-11-17 复核更正：原记 79–80，实测组合 filter 为 79）` |
| Closeout（`:119`、`:125`） | `**复核更正（2026-11-17）**：…组合 filter 为 **79/0/0/79**（非 80）`；`① 组合 filter 原记 **80/0/0** → 实测 **79/0/0/79**（…原「~CommandPalette 多匹配 1 条」的解释不成立）` |

残留检查：head 版卡片中 `80` 的 4 处出现（L52/L114/L119/L125）**全部是更正注记**，无一处仍把 80 当实测值 ⇒ PASS。

### 2. 全量 App.Tests 是否已写成 962/0/11/973 并注明原记 951 系旧数 —— **PASS（卡片）；§10 无此口径（N/A）**

| 位置 | 原文 |
|---|---|
| 卡片 AC5（`:64`） | `- [x] **AC5 不回归**：无夹具 App.Tests 为 **962 / 0 / 11 / 973**（2026-11-17 复核实测；原记 951/0/11/962 系旧数）；本卡只读不写代码。 <<MET>>` |
| 卡片测试要求表（`:81`） | `\| AC5 \| App.Tests 全量 \| 同上 \| 962/0/11/973（2026-11-17 复核实测；原记 951/0/11/962 系抄自 §9.1 旧数） \| 实测 \|` |
| Closeout（`:119`、`:126`） | `全量为 **962/0/11/973**（非 951/0/11/962）`；`② 全量 App.Tests 原记 **951/0/11/962** → 实测 **962/0/11/973**` |

- 矩阵 §10 内**没有**任何 App.Tests 全量数字（`Select-String '962|973'` 在 §10 段零命中），故「§10 相关处」无可改：**N/A**（不是漏改）。
- 唯一留在矩阵里的 `951 / 0 / 11 / 962` 在 **§9.1 第 253 行**，是 `GATE3-SETTINGS-SHORTCUT-1` 自身当时的回归口径，属历史记录，**不应改**；若希望 §10 也带全量口径，可加一句「全量见卡片 AC5」，非阻塞。

### 3. 终态材料 —— **FAIL**（结构齐了，但有 3 处必改，其中 1 处翻 `done` 必红）

已具备（实测确认）：

| 项 | 现状 |
|---|---|
| AC1–AC5 `<<MET>>` | **5/5**，且均 `[x]`（未勾选 AC = 0），符合 `check.ps1:1545-1557` |
| Canonical Evidence 行数 | **2 行**（EV-G3MX-01/02），7 列齐 |
| Resource Manifest | `agent-output \| — \| NOT_APPLICABLE \| — \| — \| 本卡无新增派生物；2026-11-17 复核确认只需仓库内文档` ⇒ 结果列非占位，符合 `check.ps1:1485` |
| `integration_commit` / `delivery_head` | 均为 `41a68b00d`（非 null） |
| `canonical_evidence_status` / `resource_closeout_status` | 均 `complete` |

**必改 1（硬阻塞）：`sha256_basis` 的值 `raw` 非法。**
卡片证据表是 **7 列**，我把 `check.ps1:1148-1152` 的表头判定原样套到该表上，结果为 `header cells = 7`、`basisEvidenceSchema = True`
⇒ 必走 `check.ps1:1188` 新七列分支，而该分支第 **1191–1193** 行要求：

```
if ($basis -cnotin @('BLOB', 'WORKTREE', 'EXTERNAL_SHA256')) {
    Add-Error "EVIDENCE_BASIS_INVALID: sha256_basis 必须严格为 BLOB、WORKTREE 或 EXTERNAL_SHA256：$path"
```

两行的 `sha256_basis` 都是 `raw`（原文：`| EV-G3MX-01 | … | CANONICAL | raw |`、`| EV-G3MX-02 | … | CANONICAL | raw |`）
⇒ **一旦 status 离开 `in_progress`，立即 2 条 `EVIDENCE_BASIS_INVALID`**。
现在 `check.ps1` 输出 `PASS (3 warnings)` 只是因为证据块整段被 `check.ps1:1092`（仅 `in_review/approved/done/closed_with_limitations` 才校验）挡住，**不代表合规**。
（受「只允许写本报告」约束，无法把 status 临时改为 `done` 再跑；结论来自上述代码路径 + 表头判定的实跑复刻。）

**必改 2：两条证据 pin 指向的是「更正前」的字节，等于用证据固定了错误版本。**

| 行 | 声称 sha256 | 实测 | 判定 |
|---|---|---|---|
| EV-G3MX-01（矩阵 @ `f9be610de`） | `50a654d3…` | `git show f9be610de:…` = `50a654d30ecae2c4…` ✅ 与其 commit 自洽；**但该 blob 内仍是 `80 / 0 / 0` 与 `951 / 0 / 11 / 962`** | pin 的是**含 80 的旧版**，不是含更正的版本（当前矩阵 = `197c3c1a…`） |
| EV-G3MX-02（本卡 @ `eb8b5c82a`） | `1a614cc8…` | `git show eb8b5c82a:…` = `1a614cc8…` ✅ 自洽；**但该 blob 内是 `80 passed / 0 failed / 0 skipped` 与 `AC5 … 951 / 0 / 11 / 962`** | 同上；当前卡片 = `3f01c785…` |

即：两个 hash 都「对自己的 commit 正确」，但**两条证据都不覆盖本卡修正后的 AC1/AC5 主张**——
拿它们去证明「已改成 79/962」是反证。建议改 pin 到含更正的提交（矩阵 `197c3c1a…`、卡片 `3f01c785…`），
更稳妥的是把 `verification/GATE3-MATRIX-EXPAND-1/` 里的实测日志作为证据行（顺带补上仍不存在的 `evidence_dir`，`Test-Path` = False），避免「卡片 pin 自己」的自引用。

**必改 3：`integration_commit` / `delivery_head` 指向更正前的提交。**
两者均为 `41a68b00d`，而两条数字的更正提交是 **`9a2e7fea3`**（当前 head，diff 为
`…INDEPENDENT-REVIEW….md \| 279 +`、`MAINT-1-…md \| 2 +-`、`GATE3-…md \| 45 ++--`）。
交付物实际内容是 `9a2e7fea3` 及之后的字节，两个字段需同步（或等最终收口提交后回填）。

### 第二轮结论

- **数字**：两条都已按首轮实测改对，且都保留了「原记 80 / 原记 951」的更正说明，口径清楚 ⇒ **1 PASS、2 PASS**。
- **终态材料**：清单结构齐备（MET 5/5、证据 2 行、Manifest 可验证、两个 status `complete`），但
  `sha256_basis: raw` 会让 `done` 直接判红，证据 pin 固定在含错误的旧字节上，`integration/delivery` 也未指向更正提交
  ⇒ **3 FAIL**。
- **verdict2: REJECTED**。三处均为一两行的改法，建议按
  ① `raw` → `BLOB`（并把 commit 改到含更正的提交，hash 用该 commit 的 blob）或 `WORKTREE`（AC/Gate 列需含 `WORKTREE_ENV=…`，`check.ps1:1214`）、
  ② 证据改 pin 更正后字节（优先 pin `verification/GATE3-MATRIX-EXPAND-1/` 的实测日志）、
  ③ `integration_commit` / `delivery_head` → `9a2e7fea3` 或最终收口提交；
  改完再窄确认一次，即可 `done`。`status: in_progress` 的保留是对的。

复核者：`gate3-reviewer`（独立上下文，未参与实现/返修）｜head `9a2e7fea3`｜2026-11-17（第二轮窄确认）
