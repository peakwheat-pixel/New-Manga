# AC2 — AC 证据覆盖核验

**Task**: GOV-EVIDENCE-UNIQUE-1（按 r18 修订后的目标）
**冻结 head**: `3c9ee0877` · **性质**: 只读 · **口径**: r18 §二

本文以 **AC 为单位**判定覆盖。枚举：`COVERED` / `PARTIAL` / `EVIDENCE_GAP` /
`UNKNOWN` / `NOT_APPLICABLE`。

判定依据三条硬口径（r18）：

1. 多次尝试保留时间与结果关系；报告哪次是最终依据；
2. 命令 + 环境 + 日志 + 退出码作为**一组**核验；
3. 只有日志而无退出码 → `PARTIAL` 或 `UNKNOWN`，**不按文件数判为覆盖**。

---

## 一、P14（6 个 AC，2 个候选）

| AC | 内容摘要 | 覆盖 |
|---|---|---|
| AC1 | 六元素 / 布局 / 状态矩阵 / TaskProgressPanel 形状冻结 | `NOT_APPLICABLE`（设计实现类，证据在代码与 Handoff，非 evidence 目录） |
| AC2 | 未交付缺口必须"禁用而非发明" | `NOT_APPLICABLE`（需读前端代码与 Handoff） |
| AC3 | WebView 不得触碰 DB / 任意路径 | `NOT_APPLICABLE`（架构约束，由 Review 判定） |
| AC4 | 事件后必须重查快照 | `NOT_APPLICABLE`（同上） |
| **AC5** | ① `npm test` 全绿（**归档原始日志与退出码**）② `npm run build` 成功（归档日志）③ Core/Rust 不回归 ④ … | **`PARTIAL`** |
| AC6 | 固定 commit + Handoff + Canonical Evidence | `NOT_APPLICABLE`（交付类，证据在 Task/Handoff） |

### AC5 为什么是 `PARTIAL`

候选恰好是两份日志：

| 候选 | 大小 | 对应 AC5 的哪一条 |
|---|---:|---|
| `frontend-tests.log` | 59694 B / 882 行 | ① 的**日志**部分 |
| `frontend-build.log` | 412 B / 12 行 | ② 的**日志**部分 |

**但 AC5 ① 明确要求「归档原始日志**与退出码**」，而候选集里没有任何 exit-code 文件。**

按 r18 第三条硬口径：**只有日志而无可复核退出码 → `PARTIAL` 或 `UNKNOWN`，
不能按文件数判为覆盖。**

因此 AC5 = `PARTIAL`。缺口是**退出码**，不是日志。

另外 AC5 ③ 要求「`tests/core/**` 与 Rust 套件不回归」——候选集里**没有**这两类日志，
所以即使补上退出码，3 也仍缺。**缺口至少两个。**

---

## 二、P15-CORE-1C（6 个 AC，5 个候选）—— 唯一一个证据组完整的样本

| 候选 | 内容 | 角色 |
|---|---|---|
| `pytest-core-focused.command.txt` | 2 行，完整命令行 | 命令 |
| `pytest-core-focused.environment.txt` | 11 行，shell / python / worktree | 环境 |
| `pytest-core-focused.exit-code.txt` | 2 行，内容 `0` | **退出码** |
| `pytest-core-focused.log` | 6 行，`100 passed in 4.58s` | 日志 |
| `canonical-hash-verification.txt` | 19 行，`result=PASS; verified 12 files` | 制品哈希核验 |

| AC | 覆盖 |
|---|---|
| AC1–AC5 | `NOT_APPLICABLE`（实现与安全约束，由测试覆盖，非 evidence 文件直接证明） |
| **AC6**「按下述替身反例与完整回归执行并归档证据」 | **`COVERED`** |

### 为什么这一个能判 `COVERED`

因为它的五份候选构成一个**完整的四件套 + 制品核验**：

```
命令 + 环境 + 退出码(0) + 日志(100 passed) + 制品哈希(12 files PASS)
```

r18 的三条硬口径在这个样本上**全部满足**：有退出码、有环境、有命令、
日志与退出码一致（0 且 100 passed）。

**这是 13 个 Task 里唯一一个证据组闭合的样本。** 它同时证明：
「一个 AC 由多份文件共同证明」这个形态是**真实存在且可判定的**——
只要这组材料齐备。

---

## 三、P19-BOOT-1（6 个 AC，1 个候选）—— 完全无证据

| 候选 | 内容 | 能否证明 AC |
|---|---|---|
| `.gitignore` | 32 行，`/runtime*/` 等忽略规则 | **不能** |

配置/忽略规则文件**永远不是 AC 证据**（r18：证据是日志、退出码、环境、交付说明）。

| AC | 覆盖 |
|---|---|
| AC1「真实 Cargo debug host 启动成功，WebView2 到达四页，见真实窗口截图」 | **`EVIDENCE_GAP`** —— 截图、stderr、exit code 都不在候选集 |
| AC2「真实 stderr 无裸 FileNotFoundError」 | **`EVIDENCE_GAP`** —— 无 stderr 文件 |
| AC3 / AC4 | `NOT_APPLICABLE`（实现约束） |
| AC5「进程内测试与真实 host 启动的差距已说明」 | `NOT_APPLICABLE`（需 Handoff） |
| AC6「真实运行记录 exit code、stderr、UIA 标题和四页窗口截图」 | **`EVIDENCE_GAP`** —— 这四样**一样都不在候选集** |

**结论：本 Task 的 AC1/AC2/AC6 都在候选范围内无任何证据。**

注意：这不代表 Task 没做。它的 AC 全部勾选，且 Task 里可能有证据引用。
**本判定只说明「在 AC7 冻结的 61 项候选里，没有它的证据」。**
这正是「存在候选 ≠ AC 已满足」的反面：**无候选 ≠ AC 未满足**，
只能说候选集不覆盖。

---

## 四、P15-HOST-1（6 个 AC，3 个候选）

| 候选 | 内容 | 角色 |
|---|---|---|
| `.gitattributes` | 3 行 | 配置，非证据 |
| `core-pytest-full-suite-extra.txt` | 53650 B，**37 个 FAILURES 段** | 测试输出，但显示失败 |
| `resource-manifest.json` | 29 行 | 配置，非证据 |

| AC | 覆盖 |
|---|---|
| AC1 []（未勾选） | `NOT_APPLICABLE`（实现类） |
| AC2 / AC3 / AC4 | `NOT_APPLICABLE`（实现与安全约束） |
| **AC5**「Rust source 与 frozen packaged 两套件**正确口径**下全绿；Core pytest …」 | **`PARTIAL`** |
| AC6「固定 commit + Handoff + Canonical Evidence」 | `NOT_APPLICABLE` |

### AC5 为什么是 `PARTIAL` 而不是 `COVERED`

唯一与测试相关的候选是 `core-pytest-full-suite-extra.txt`，而它**包含 37 个 FAILURES 段**。
从内容看它记录的是**失败**，不是「全绿」。

三种可能：
1. 这是修复前的失败记录（那么修复后全绿的证据不在候选集）；
2. 这是最终状态（那么 AC5 未满足）；
3. 它有部分通过、部分失败。

**我无法从这一份文件确定是哪一种**——缺少后续运行的日志与退出码。
按 r18 口径，这种情况记 `PARTIAL`。

同时 AC5 要求的 **Rust source 与 packaged 两套件**在候选集中**都没有**，
所以缺口不止一处。

---

## 五、已核验 4 / 13 个 Task 的汇总

| Task | AC 数 | `COVERED` | `PARTIAL` | `EVIDENCE_GAP` | `NOT_APPLICABLE` |
|---|---:|---:|---:|---:|---:|
| `P14` | 6 | 0 | 1（AC5） | 0 | 5 |
| `P15-CORE-1C` | 6 | **1（AC6）** | 0 | 0 | 5 |
| `P19-BOOT-1` | 6 | 0 | 0 | **3（AC1/AC2/AC6）** | 3 |
| `P15-HOST-1` | 6 | 0 | 1（AC5） | 0 | 5 |
| **小计** | **24** | **1** | **2** | **3** | **18** |

**剩余 9 个 Task 未核验**（`EXPORT-REVEAL-1`、`FEAT-CREATE-3`、`FEAT-CREATE-4`、
`FEAT-IMPORT-MULTI-1`、`HOST-TTL-BOUNDARY-1`、`P15`、`P15-HOST-2`、
`P19-UI-FIX-1`、`P19-UI-FIX-2`）。

按 `GOV-EVIDENCE-UNIQUE-1` AC1 的 batch 定义，`FEAT-IMPORT-MULTI-1` 的结论
已在上一版文档给出（7 份缺失 + 1 份 Review，可判 `EVIDENCE_GAP`），此处不重复。

---

## 六、这批核验揭示的三件事

### 1. `NOT_APPLICABLE` 占了 75%

24 个 AC 里有 18 个不要求文件级证据（实现类、架构约束类、交付类）。
**这意味着「AC 证据覆盖率」这个指标本身对多数 AC 无意义**——
`evidence/` 目录从来不是所有 AC 的证据存放处。

### 2. 唯一 `COVERED` 的样本说明「完备」是可达的

`P15-CORE-1C` 的四件套 + 制品核验证明：只要材料齐备，覆盖是可以判定的。
**它同时也是模板**——后续若要把某 AC 补到 `COVERED`，缺什么一目了然。

### 3. `EVIDENCE_GAP` 与「Task 没做」是两回事

`P19-BOOT-1` 的 AC 全部勾选，但它在 61 项候选里只有一份 `.gitignore`。
**候选集不是全部证据集**——它只是 `GOV-DEBT-CLEANUP-2` AC7 从 `evidence/` 目录
列出来的文件。**别的目录里的证据不在本次范围内。**

这条必须写进 limitation，否则会被误读成「这个 Task 没证据」。
