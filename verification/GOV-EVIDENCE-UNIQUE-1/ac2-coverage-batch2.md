# AC2 — AC 证据覆盖核验（第二批）

**Task**: GOV-EVIDENCE-UNIQUE-1 · **冻结 head**: `3c9ee0877` · **口径**: r18 §二
第一批见 `ac2-coverage-batch1.md`。

---

## 一、EXPORT-REVEAL-1（7 个 AC，4 个候选）—— AC 全部未勾选

| AC | 内容 | 覆盖 |
|---|---|---|
| AC1 | 在 M2-C1 契约新增 revision | `NOT_APPLICABLE`（契约改动，证据在 contracts/） |
| AC2 | host 侧实现命令 | `NOT_APPLICABLE`（代码） |
| AC3 | 新依赖仅官方 `tauri-plugin-*` | `NOT_APPLICABLE`（Handoff 声明类） |
| AC4 | 「给出真实证据：…」 | **`PARTIAL`** |
| AC5 | 不得改既有契约/暴露绝对路径 | `NOT_APPLICABLE`（约束类） |
| **AC6** | `tests/core/**` 与既有 Rust 测试全绿（**归档原始日志 + 退出码**） | **`PARTIAL`** |
| AC7 | 固定 commit + Handoff + Canonical Evidence | `NOT_APPLICABLE`（交付类） |

### 候选实际内容

| 候选 | 关键行 | 性质 |
|---|---|---|
| `pytest-core.log` | `405 passed, 1 warning in 32.00s` | **通过日志** |
| `rust-source.log` | `test ac1_bridge::... ok`（84 pass） | **通过日志** |
| `rust-packaged.log` | `test result: ok. 8 passed; 0 failed` | **通过日志（packaged）** |
| `post-merge-packaged-capture-error.log` | `error: test failed, to rerun pass --bin m2rc1-desktop` | **失败记录** |

### AC6 为什么是 `PARTIAL` 而不是 `COVERED`

AC6 要求的三样：core 日志 ✔、Rust 日志 ✔、**退出码 ✘**。

按 r18 第三条硬口径：**有日志而无退出码 → `PARTIAL`，不能按文件数判为覆盖。**

而且候选集里还有一份 `post-merge-packaged-capture-error.log` 记录着
`error: test failed`。它与三份通过日志的**时间关系未知**——
按 r18 第一条口径，我应当报告「哪次是最终依据」，但**候选集里没有时间戳可判**。

因此 AC6 = `PARTIAL`，并注明：**失败记录与通过记录的关系未确定**。

> 注意本 Task 的 AC **7 条全部未勾选**却标 `done`（r18 已裁定继续按 status 纳入，异常在 limitation 中单列）。

---

## 二、FEAT-CREATE-3（6 个 AC，1 个候选）—— 只有 Review

| 候选 | 内容 |
|---|---|
| `dsh-review-r1.md` | 独立 Review 记录，含 `PASS：assert_eq!(PRODUCTION_COMMANDS.len(), 51)` 等逐项核对 |

| AC | 覆盖 |
|---|---|
| AC1 注册 production-only 命令 | `EVIDENCE_GAP`（需代码与测试日志） |
| AC2 四处同步（49→51） | **`PARTIAL`** —— Review 记录里**明确写了**该断言 4 处一致，但那是 Review 的转述，不是测试输出本身 |
| AC3 与 Core 2.8 通信 | `EVIDENCE_GAP` |
| AC4 安全边界 | `EVIDENCE_GAP` |
| **AC5**「host 侧测试覆盖…Rust source 不回归（基线 103/0/1）…packaged 12/0 不回归…Core pytest 535 不回归」 | **`EVIDENCE_GAP`** —— 候选集**没有任何测试日志**，只有 Review 声称 |
| AC6 交付 | `NOT_APPLICABLE` |

### 一个必须说清的区分

Review 里写着「PASS：`assert_eq!(...)` 4 处一致」。**这不能当作 AC5 的证据。**

Review 是**判断**，它的价值在于「有人独立核对过」。但 AC5 要求的是
**测试覆盖与基线数字**——那需要测试日志与退出码。

**「Review 说通过了」与「有测试输出证明通过」是两种不同的证据强度。**
把前者当后者，正是本 Task 要清理的那类替代。

因此 AC2 = `PARTIAL`（Review 转述），AC5 = `EVIDENCE_GAP`（无测试输出）。

---

## 三、HOST-TTL-BOUNDARY-1（7 个 AC，4 个候选）—— 多数是失败记录

| 候选 | 关键内容 | 性质 |
|---|---|---|
| `ac3-rust-ttl-boundary-build-attempt-1.log` | **`EXIT_CODE=101`** | **构建失败** |
| `ac4-export-frozen-rust-attempt1-4662239.log` | `assertion left == right failed` | **断言失败** |
| `ac4-frozen-host-importpages.log` | `assertion left == right failed` | **断言失败** |
| `ac6-rust-tests.log` | 84 pass（与 AC6 声称的「合计 84 passed/1 ignored」吻合） | **通过日志** |

| AC | 覆盖 |
|---|---|
| AC1 / AC2 / AC5 | `NOT_APPLICABLE`（契约与约束类） |
| **AC3**「Import 与 Export 各有五个确定性边界断言」 | **`PARTIAL`** —— 唯一相关日志是 `EXIT_CODE=101` 的**构建失败**，没有通过的版本 |
| **AC4**「在协议 2.3 frozen Core 上跑通 host 签发…」 | **`PARTIAL`** —— 两份 attempt 日志都是 **assertion failed**，没有通过的版本 |
| **AC6**「`tests/core/**` 405 passed；Rust 76 passed/1 ignored；frozen packaged 8 passed；合计 84」 | **`PARTIAL`** —— `ac6-rust-tests.log` 与「84 passed」吻合，但**core pytest 405 passed 与 packaged 8 passed 的日志不在候选集**，且**无退出码** |
| AC7 | `NOT_APPLICABLE`（交付类） |

### 这一组最值得注意

4 份候选里 **3 份记录失败**（EXIT_CODE=101、两处 assertion failed），
只有 `ac6-rust-tests.log` 是对应 AC 且显示通过。

按 r18 第一条口径，我应报告「失败尝试是否被后续有效运行取代」。
**候选集里没有任何后续通过的日志**——所以无法确认这些失败已被取代。

**因此 AC3/AC4 只能是 `PARTIAL`，不能因为「Task 标了 done」就推定失败已被修复。**

---

## 四、P19-UI-FIX-1（5 个 AC，8 个候选）

| 候选 | 内容 | 性质 |
|---|---|---|
| `04-settings-before-final-code-refinement.uia.txt` | UIA 文本，`count=9` | **UIA 记录** |
| `04-settings-uia-pass-2.txt` | 同上 | **UIA 记录** |
| `04-settings-uia-pass-exit-code-blank.txt` | 同上，**文件名含 exit-code-blank** | **UIA 记录** |
| `app-err-before-final-code-refinement.log` | `[core.derived_gc] orphan_files_removed=0` | stderr |
| `app-err-namespace-mismatch.log` | `[PYI-51316:ERROR] Failed to execute script` | **启动失败** |
| `app-err-ui-a-pass-exit-code-blank-2.log` | 同第一份 | stderr |
| `app-err-ui-load-failure.log` | 同第一份 | stderr |
| `app-err-uia-pass-exit-code-blank.log` | 同第一份 | stderr |

| AC | 覆盖 |
|---|---|
| **AC1**「9 个分类按钮原生 disabled…真实 UIA 均 `IsEnabled=False`」 | **`COVERED`** —— 3 份 `04-settings-*.uia.txt` 正是 UIA 采集记录，`count=9` 与「9 项」吻合 |
| **AC2**「空书架显示明确未开放原因…真实 GUI 空书架反馈见 `import-open.uia.txt`」 | **`EVIDENCE_GAP`** —— **`import-open.uia.txt` 不在候选集**，而 AC 明确指向它 |
| **AC3**「前端 `npm test` 28 files / 277 passed / exit 0」 | **`EVIDENCE_GAP`** —— 候选集**没有任何前端测试日志** |
| **AC4**「强制重建 frozen sidecar…9 项 `IsEnabled=False`…应用退出码 0」 | **`PARTIAL`** —— UIA 记录在，但**退出码不在**；且 `app-err-namespace-mismatch.log` 记录了一次**启动失败**，它与通过记录的关系未知 |
| AC5 | `NOT_APPLICABLE`（交付类） |

### AC1 判 `COVERED` 的理由

AC1 要求的核心是「9 项 UIA 均 `IsEnabled=False`、`IsOffscreen=False`、Invoke blocked」。
候选中的三份 `04-settings-*.uia.txt` 各 11 行、`count=9`，**正是同一采集的三次尝试**。

按 r18 第一条：多次尝试保留关系、报告哪次是最终依据——三份文件名分别是
`before-final-code-refinement` / `pass-2` / `pass-exit-code-blank`，
**最终依据应为最后一份**（`pass-exit-code-blank`）。

内容层面没有歧义，因此 `COVERED`。这是本批第二个 `COVERED` 样本。

### AC2 的 `import-open.uia.txt` 缺失很关键

AC2 的原文**明确点名** `import-open.uia.txt` 作为证据。该文件**不在 61 项候选内**。

这有两种解释：
1. AC7 的分类漏了它；
2. 该文件在别的目录。

无论哪种，**都无法从候选集确认 AC2 的 GUI 证据**。记 `EVIDENCE_GAP`。

---

## 五、第二批汇总

| Task | AC 数 | `COVERED` | `PARTIAL` | `EVIDENCE_GAP` | `NOT_APPLICABLE` |
|---|---:|---:|---:|---:|---:|
| `EXPORT-REVEAL-1` | 7 | 0 | 2（AC4/AC6） | 0 | 5 |
| `FEAT-CREATE-3` | 6 | 0 | 1（AC2） | 3（AC1/AC3/AC5…含 AC4） | 2 |
| `HOST-TTL-BOUNDARY-1` | 7 | 0 | 3（AC3/AC4/AC6） | 0 | 4 |
| `P19-UI-FIX-1` | 5 | **1（AC1）** | 1（AC4） | 2（AC2/AC3） | 1 |
| **小计** | **25** | **1** | **7** | **5** | **12** |

## 六、两批合计（8 / 13 个 Task）

| 枚举 | 数量 |
|---|---:|
| `COVERED` | **2** |
| `PARTIAL` | **9** |
| `EVIDENCE_GAP` | **8** |
| `NOT_APPLICABLE` | **30** |
| **合计 AC** | **49** |

**`NOT_APPLICABLE` 占 61%。** 这与第一批的 75% 是同一结论：
多数 AC 不要求文件级证据。

## 七、本批揭示的两个新模式

### 1. 「Review 说通过」不等于「有测试输出」

`FEAT-CREATE-3` 的 Review 里写着 `PASS：assert_eq!(PRODUCTION_COMMANDS.len(), 51)`。
这是**第二手转述**。AC5 要的是测试覆盖与基线数字——需要第一手的日志与退出码。

**这个区分在治理上很重要**：Review 的价值是独立核对，不是替代证据。

### 2. 「Task 标 done」不能推定「失败尝试已被取代」

`HOST-TTL-BOUNDARY-1` 的 4 份候选里 3 份记录失败，且**没有任何后续通过的日志**。
按 r18 口径，只能记 `PARTIAL`。

**不能因为 status 是 `done` 就认为那些失败已被修复**——那是用元数据替代证据。

## 八、剩余 5 个 Task

`FEAT-CREATE-4`、`FEAT-IMPORT-MULTI-1`、`P15`、`P15-HOST-2`、`P19-UI-FIX-2`。

其中 `FEAT-IMPORT-MULTI-1`（7 份缺失 → `EVIDENCE_GAP`）与 `P15`（唯一候选是
不匹配的 cargo 日志）的结论已在 `ac2-ac-mapping-and-uniqueness.md` 给出，
但需按新枚举重新表述。
