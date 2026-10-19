# `GOV-PIN-LINEAGE-1` 释放前置条件核查

**产出**: 2026-10-20 · **性质**: 只读分析 · **依据**: Codex r25「释放前核实依赖、回归清单、预算及独立 Reviewer」

## 一、r25 要求核实四项

> 推荐下一步：Codex 核实依赖、回归清单、预算及独立 Reviewer 后，
> 更新 `GOV-PIN-LINEAGE-1` 的范围与 AC，再决定是否冻结并释放。

范围与 AC 已在 `fc469b152` 更新（6 条 AC）。本文核实其余三项，
第四项（独立 Reviewer 可用性）需要实际派发测试，不在本文展开。

## 二、回归清单（AC5 要求的「具体既有夹具」）

`tools/governance/tests/` 现有：

| 文件 | 大小 | 用途 |
|---|---:|---|
| `run-resource-manifest-cases.py` | 6131 B | Resource Manifest 语义用例 |
| `test_ac_gate.py` | 6347 B | v3 AC 门禁 12 例 |
| `fixtures/` | — | 目录（内含 resource-manifest/cases.json 等） |

**AC5 要求的新增用例**（六类）：

| # | 情形 | 期望 |
|---|---|---|
| 1 | 历史 blob 匹配，但工作区被修改 | **pin 通过**，另有 workspace-drift 诊断 |
| 2 | LF/CRLF 转换（blob LF / 工作区 CRLF） | **pin 通过** |
| 3 | pin 的 commit 不存在 | **FAIL**（保持现有语义） |
| 4 | commit 中不存在该路径 | **FAIL** |
| 5 | blob 的 SHA 与 pin 不符 | **FAIL** |
| 6 | 工作区与 pin 一致 | **通过**，无漂移诊断 |

**这六类必须用确定性夹具覆盖，且不得破坏既有两个测试脚本的行为。**

## 三、依赖

| 依赖项 | 状态 |
|---|---|
| `git cat-file -p <commit>:<path>` 可读 blob | **可用**（已在 `pin-inventory.py` / `diag-unexplained.py` 使用） |
| `check.ps1` 现有校验路径 | 约 L313–315（r25 §2 定位） |
| `pin-inventory.json`（63+6 的输入） | **已就绪**，`verification/GOV-PIN-LINEAGE-1/` |
| `pin-inventory-and-scope.md`（分类依据） | **已就绪** |
| 既有测试脚本 | 2 个，均需回归不破 |

**无外部依赖。** 不需要新包、不需要网络。

## 四、受影响范围（修正 checker 后会翻 PASS 的 Task）

**实测：当前 313 个 Task 中 83 个 FAIL。**

其中 **pin-only（仅因 `Evidence SHA-256 不匹配` 而红）的是 19 个**：

| Task | 当前错误数 |
|---|---:|
| `HOST-ISSUER-1` | 6 |
| `ENV-BUNDLE-1` | 2 |
| `HOST-CORE-1` | 1 |
| `HOST-ISSUER-1-C1` | 2 |
| 其余 15 个 | 各 1–2 |

**这 19 个在修正语义后应转 PASS。**

### 为什么不是 63 个

因为 63 个 `TIME_BASED` pin 分布在 **28 个 Task** 上，但其中多数 Task **还有别的错误**
（未登记文件、缺 manifest、未完成 AC 等），**修正 pin 只消除其中一条**。

**这个区别很重要**：它决定了「修正后有多少 Task 变绿」不是 63，而**最多 19**。
如果有人期待「改一处 checker 让 63 个 Task 变绿」，那是错的期待。

## 五、预算

| 文件 | 现状 | 上限 | 余量 |
|---|---:|---:|---:|
| `doc/STATUS.md` | 3139 B / 30 行 | 3200 B / 45 行 | **61 B / 15 行** |
| `doc/REBASELINE_PLAN.md` | 4035 B / 46 行 | 7000 B / 64 行 | 2965 B / 18 行 |
| `doc/09_COLLABORATION.md` | 27419 B | 无硬上限 | — |

**本 Task 计划的产物**：

| 产物 | 位置 | 是否影响预算 |
|---|---|---|
| `pin-lineage-registry.json`（63+6 条） | `verification/GOV-PIN-LINEAGE-1/` | **否**（证据目录，不限） |
| checker 最小 diff | `tools/governance/check.ps1` | 否 |
| 新增测试用例 | `tools/governance/tests/` | 否 |
| Plan 行更新 | `doc/REBASELINE_PLAN.md` | 是，但有余量 |
| STATUS | 无需改（本 Task 非 Active） | — |

**预算充分。**

## 六、一个必须提前说明的风险

**修正 `check.ps1` 的 pin 校验语义，是本 Session 反复被警告的那类改动。**

具体风险：

1. **它会让 19 个 Task 从红变绿。** 如果某个 Task 的 pin 其实是**真的损坏**
   （不是时间性），新语义可能把它放过。**AC2 要求「blob 不符时保留 error 语义」，
   就是为了防这个。**
2. **它可能掩盖工作区漂移。** r25 §8 要求把漂移作为**独立诊断**报出，
   而不是吞掉。**AC5 用例 1 就是测这个。**
3. **它是治理基础设施，不是产品代码。** 改错的代价是「检查器不再可信」。

**这三条都写在 AC2/AC5 里了**，但它们值得在此重复，因为这是本 Task 的唯一真实风险。

## 七、结论

| r25 要求 | 状态 |
|---|---|
| 核实依赖 | **完成**（无外部依赖，输入已就绪） |
| 回归清单 | **完成**（六类用例已列出，既有 2 个脚本需回归） |
| 预算 | **完成**（证据目录不限；Plan 有余量；STATUS 不需改） |
| 独立 Reviewer | **待定**——需要实际测试 Antigravity / ZCode 可用性 |

**前三项已就绪。第四项是释放决策的必要条件，由 Codex 或用户确认。**
