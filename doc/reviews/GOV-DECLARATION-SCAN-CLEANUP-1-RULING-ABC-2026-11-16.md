---
ruling_id: GOV-DECLARATION-SCAN-CLEANUP-1-RULING-ABC
task_id: GOV-DECLARATION-SCAN-CLEANUP-1
kind: lead-ruling
author: DSH（DeepSeek Harness，项目 Lead / Architect / Integrator）
author_kind: lead
date: 2026-11-16
timezone: Asia/Shanghai
basis: doc/reviews/GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md（adjudicator-decl，独立上下文）§2(c) 主路径 + 本轮实测
status: A 已裁定并已执行；B/C 已裁定（实施在后续轮）
---

# Ruling A / B / C：声明扫描债务清理的三项前置裁定

> 依据：`doc/reviews/GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md` 判「保持 BLOCKED + 另立
> `GOV-DECLARATION-SCAN-CLEANUP-1` 是唯一推荐主路径」，并明确 **「不做 Ruling A，后面全白做」**。
> 本文出三项书面裁定，署名 DSH（Lead）。所有数字均为 **2026-11-16 本轮实测**，不是沿用旧文。

## 0. 本轮实测基线（Ruling 的事实底座）

命令：`python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>/tasks/RULING-ABC/out`
结果：**EXIT=2**，`errors = 167`，`warnings = 721`，`declarations = 6729`，`protected_roots = 5582`。

| error code | 条数 |
|---|---:|
| `TABLE_SCHEMA_INCOMPLETE` | 53 |
| `DECL_RELATIVE_UNRESOLVED` | 27 |
| `DECL_ENV` | 20 |
| `DECL_GLOB` | 16 |
| `DECL_DESTINATION_UNRESOLVED` | 12 |
| `TABLE_DELIMITER` | 10 |
| `DECL_UNKNOWN_DISPOSITION` | 10 |
| `DECL_TRAVERSAL` | 7 |
| `FILE_UNREADABLE` | 4 |
| `DECL_RELATIVE_AMBIGUOUS` | 2 |
| `JSON_PARSE` | 2 |
| `TABLE_ROW_ARITY` / `DECL_BARE_NAME` / `DECL_MISSING_SOURCE` | 各 1 |
| **`SOURCE_DRIFT`** | **1** |
| **合计** | **167** |

**关键实测**：`DECL_RESIDUAL_RUNTIME_PRESERVED` warning 数 = **0**
⇒ 证实裁决报告 L1 的推断：residual 层因 HIE 政策错误**整段早退**，7 条裁定身份未降级、APPDATA 三根未注册。

唯一那条 `SOURCE_DRIFT` 的完整身份（实测原文）：

```
code    SOURCE_DRIFT
message historical input tracking changed: verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md
file    tools/governance/historical-evidence-interpretation.json
```

---

## Ruling A（跟踪状态语义）—— 判 **(i)：更新绑定到 tracked 并重批 digest**

### 事实（本轮实测，逐项可复现）

`tools/governance/historical-evidence-interpretation.json` 共 4 条 origin 绑定。
对每条实测「`raw_sha256` 是否仍匹配」与「`expected_tracking` 是否等于实际跟踪状态」：

| 绑定 | origin | `raw_sha256` 匹配 | 实际 tracking | `expected_tracking` | 一致 |
|---|---|:--:|:--:|---|:--:|
| `HIE-T01` | `verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md` | ✅ | tracked | tracked | ✅ |
| `HIE-O01` | `verification/P14/owner-initiated-dsh-self-review-r1.md` | ✅ | tracked | tracked | ✅ |
| `HIE-O02` | `verification/P14/owner-initiated-dsh-self-review-r2.md` | ✅ | tracked | tracked | ✅ |
| **`HIE-O03`** | **`verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md`** | **✅** | **tracked** | **untracked** | **❌** |

入库提交：`ee755d4bb verification: commit the remaining 406-file evidence backlog`。

⇒ **漂移只发生在「政策对跟踪状态的期望」这一个字段上，历史证据字节一个都没变**（4 条 `raw_sha256` 全匹配）。

### 裁定

采纳 **(i)**：把 `HIE-O03.expected_tracking` 由 `"untracked"` 改为 `"tracked"`，并把
`clean_workspace.py` 的 `HISTORICAL_EVIDENCE_DIGEST` 重批为新值 `5cc683589476c689c00d7eb8c5740b8c8f8533ec69300ad7f92052c501cdaadd`
（旧值 `3f4cae13…4b7d`；计算口径 = `sha256(canonical_json)`，`sort_keys=True, separators=(",",":")`，本轮实测已复现旧值一致）。

### 为什么不是 (ii) 或 (iii)

- **(ii) `git rm --cached` 恢复 untracked**：会**反悔 `ee755d4bb` 的 406 文件入库决策**，
  且该文件已经成为仓库历史的一部分；为了让一条过期的「期望」成立而把证据改回未跟踪，
  方向是反的 —— **应当让政策追上事实，而不是让事实退回政策**。
- **(iii) 改成 tracking-agnostic（去掉 `expected_tracking` 或放宽为任意值）**：
  这会把一条**真实的 fail-closed 检查**削弱成 fail-open。跟踪状态变化本身是值得被发现的信号
  （本次正是它把漂移暴露出来的）；正确做法是**更新被批准的期望值**，而不是取消检查。

### 不违反字节保留的论证（关键）

AGENTS.md:27/:32 与 `09_COLLABORATION.md:112-113/234` 禁止改的是**历史证据字节**。
本次改的是 **`tools/governance/historical-evidence-interpretation.json`（治理政策）** 与
**`clean_workspace.py` 的常量**，两者都不是证据产物；且四条绑定的 `raw_sha256` 实测全部仍匹配
⇒ **历史证据零字节改动**。裁决报告 §2(a) 否掉的「改历史卡/证据字节」路径与本裁定**不是同一件事**。

### 执行状态：**已在 R14 执行并逐步验证**

**执行中发现第二处「真值重复」（重要，必读）**：只改政策字段**不够** —— 改完后 audit 把
`SOURCE_DRIFT` 换成了另一条同义错误：

```
code    POLICY_INVALID
message historical source tracking policy changed
file    tools/governance/historical-evidence-interpretation.json
```

根因：`clean_workspace.py:1848-1850` 把「第 4 条必须 `untracked`」**硬编码**在扫描器里：

```python
require(b["expected_tracking"] ==
        ("untracked" if number == 3 else "tracked"), "POLICY_INVALID",
        "historical source tracking policy changed")
```

⇒ 这是 **policy 之外的第二个真值**，`ee755d4bb` 之后必然过期；而且它与 `read():1718` 的
`tracked(relative) == (expected_tracking == "tracked")`（`SOURCE_DRIFT`）**功能重复**。
**Ruling A 的完整执行必须同时消掉这份重复**，否则等于「改一处、被另一处挡住」。

处置：把该处改为**政策驱动**的取值合法性校验（`expected_tracking in ("tracked","untracked")`），
字段值与真实跟踪状态的比对**仍由 `read()` 负责** ⇒ **fail-closed 不变，只去掉硬编码副本**。

**三步实测结果（同一命令 `--audit-declarations`，逐步收窄）**：

| 步骤 | `SOURCE_DRIFT` | `POLICY_INVALID` | `ERROR_MISMATCH` | residual warning | `protected_roots` |
|---|:--:|:--:|:--:|:--:|:--:|
| 基线（改前） | **1** | 0 | 0 | **0** | 5582 |
| 改 policy 字段 + 重批 digest | **0** | **1** | 0 | 0 | 5582 |
| 再消掉硬编码副本（= Ruling A 完整执行） | **0** | **0** | **1** | 0 | **5582（未缩小）** |

⇒ **L1 已彻底清除**（两条同义错误都归零），**L3 成为唯一剩余阻塞**（`ERROR_MISMATCH`，即 `:2172`
的「全仓错误恰好 7 条」耦合，正是 Ruling C 要改的那处）。
这**精确验证了**裁决报告的三层模型，并实证「L1 确实是第一层」：清掉它之后才暴露出 L3。

**字节保留核验**：`git status --porcelain` 实测只有
`tools/governance/clean_workspace.py` 与 `tools/governance/historical-evidence-interpretation.json`
两个治理文件被改；**`verification/**` 与 `doc/tasks/*` 零改动**，四条绑定的 `raw_sha256` 仍全部匹配。
⇒ Ruling A 全程**未触碰任何历史证据字节**。

**L1 已清，但 residual 层仍未恢复（诚实登记）**：`DECL_RESIDUAL_RUNTIME_PRESERVED` 仍为 0。
原因是 `ERROR_MISMATCH` 在 residual 层可应用之前就把它挡住了 —— 也就是说
**AC2 的目标（no SOURCE_DRIFT + residual warning = 7 + APPDATA 三根回归）需要 Ruling A 与 Ruling C 同时完成**，
单独 A 不足。这一点在裁定之初并未预见到，按 §4.4「核验结果与假设不符则假设作废」，此处**更正**：
**A 是必要不充分条件；A + C 才解 AC2。**

---

## Ruling B（166 条历史声明债务的分类口径）—— 判：**按 error code 冻结三分类，先冻结后实施**

### 裁定

**分类口径按 error code 冻结**，不允许逐条自由裁量（否则就是「为清零而清零」）：

| 类 | 语义 | 本轮归属（按 code） | 处置原则 |
|---|---|---|---|
| **B1** 历史形态 | 旧形态产物，可由**解释层绑定**为非声明或已保全；**不得改字节** | `TABLE_SCHEMA_INCOMPLETE`(53)、`TABLE_DELIMITER`(10)、`TABLE_ROW_ARITY`(1) —— 共 **64** | 在解释层新增绑定（形如 HIE 绑定：绑到具体 origin + 行号 + raw sha），绑定后该表**不再作为声明源** |
| **B2** 真实缺陷 | 真实声明写错/失效，需修数据，但**不得毁活 pin** | `DECL_RELATIVE_UNRESOLVED`(27)、`DECL_ENV`(20)、`DECL_GLOB`(16)、`DECL_DESTINATION_UNRESOLVED`(12)、`DECL_TRAVERSAL`(7)、`DECL_RELATIVE_AMBIGUOUS`(2)、`DECL_BARE_NAME`(1)、`DECL_MISSING_SOURCE`(1) —— 共 **86** | 先判「该件是否仍被**活 pin** 引用」；被引用则**只登记不修**（转 B1 或等 pin 失效），未引用才修 |
| **B3** 扫描器规则误报 | 规则本身过严/过宽，需单独裁定**规则**而非数据 | `DECL_UNKNOWN_DISPOSITION`(10)、`FILE_UNREADABLE`(4)、`JSON_PARSE`(2)、`SOURCE_DRIFT`(**1**，即 Ruling A 那条) —— 共 **17** | 逐 code 出**规则裁定**；`SOURCE_DRIFT` 的处置已由 Ruling A 完成，不占 B3 预算 ⇒ B3 实为 **16** |

合计校验：64 + 86 + 16 = **166** = 167 − 1（`SOURCE_DRIFT`）。

### 两条硬约束（写进裁定，后续实施不得绕过）

1. **先冻结后实施**：B1/B2/B3 的归属表必须落盘并与 `--audit-declarations` 的 JSON **一一对得上**
   （`file` + `code` + `locator`），才允许开始处置。
2. **B2 不得毁 pin**：任何「修数据」动作前，必须实测该件是否仍被**活 pin** 引用
   （`FEA-11-RENDITION-1.md:198` 的 EV-7 pin 就是活 pin 的实例：其 `RESOURCE-MANIFEST.json` sha256 当前完全匹配）。
   被活 pin 引用者一律**只登记、不修改**。

### 未决点（诚实登记，不在本轮假装解决）

`TABLE_SCHEMA_INCOMPLETE` 归 B1 还是 B3 **存在解释空间**：它既可以是「旧形态」（B1），
也可以是「规则把旧形态当错误报」（B3）。本裁定的口径是 **B1** ——
因为这些表**真实存在于终态卡**且**不可信作保护来源**，fail-closed 行为是**正确的**；
要消除错误，应当由解释层「承认这是历史形态、不把它当声明源」，而不是放宽规则。

---

## Ruling C（持久化不变量是否重写）—— 判：**批准重写为「成员不变量」**

### 现状（被裁定要改的两处）

```
clean_workspace.py:2172  require(len(removed) == 7 and len(index.errors) == 7, "ERROR_MISMATCH", ...)
clean_workspace.py:2189  require(not staged.errors, "POLICY_INVALID", ...)
clean_workspace.py:2191  require(all(root in staged.protected for root in index.protected), "PROTECTION_REGRESSION", ...)
clean_workspace.py:2194  require(len(staged.protected) >= len(index.protected), "PROTECTION_REGRESSION", ...)
```

`:2172` 的后半句把「residual 层可应用」绑到「**全仓错误恰好 7 条**」——仓库一增长就击穿（已实际发生一次）。
这与本卡 AC5「不以绝对计数为断言」**自相矛盾**。

### 裁定

**批准重写**，具体设计（不等价于放宽，必须保 fail-closed）：

1. **保留** `len(removed) == 7`（必须恰好移除 7 条裁定身份）。
2. **替换** `len(index.errors) == 7` 为**成员不变量**：7 条被裁定的错误身份
   （按 `code` + `file` + `locator` 三元组）必须**全部存在于** `index.errors` 中；
   缺任何一条 ⇒ 仍然 `ERROR_MISMATCH`（**fail-closed 不变**）。
3. **删除**对「全仓错误总数」的任何依赖 —— 与 residual 层无关的错误**不阻塞** residual 层，
   但仍原样保留在 `staged.errors` 里继续让 `--audit-declarations` 报错（不静默吞掉）。
4. `:2189` 与 `:2191-2195` 两条**保持不变**（本次 R13 已为 `PROTECTION_REGRESSION` 补上负例，
   证明它们真的会拦）。
5. **必须补的负例**：① 7 条身份中少一条 ⇒ `ERROR_MISMATCH`；② 无关错误存在但 7 条齐全 ⇒
   residual 层**正常应用**且那 7 条被降级、无关错误仍在。第 ② 条正是当前绝对计数耦合下**不可能通过**的用例。

### §4.4 要求的两项实测（本裁定附）

**(a) 受影响调用面全集（本轮 `git grep` 实测，逐条列出，不省略）**：

- **精确形式 `len(index.errors) == 7` 全仓只有 1 处**：`clean_workspace.py:2172`。
- 其它出现 `len(index.errors)` 的位置（**均非该不变量**，仅供报告/日志）：
  `clean_workspace.py:1440`（构造扫描结果）、`:2850`（`declaration_error_count`）、`:2859`（打印）、
  `consolidate.py:297`（打印）、`tests/test_residual_runtime_identity.py:184/191/197/203/217/266/275`
  （测试自身的期望值，属测试断言，随 Ruling C 的实施需同步复核）。
- **`_apply_residual_runtime_identity` 的生产调用点全仓只有 1 处**：`clean_workspace.py:2303`
  （其余出现在测试的 `mock.patch.object` 里）。
  ⇒ Ruling C 的改动面收敛，可控。
**(b) 基线错误矩阵**：见 §0 表（167 条按 code 分解 + protected_roots=5582 + warnings=721），
该矩阵即为重写前后的对照基线。

### 若不做 C 的后果（写进裁定）

清理完成当天 `--audit-declarations` 会绿，**下一张卡一加文件就再红**（已发生过一次）。
⇒ C 不是可选项，是**止损项**。

---

## 执行顺序（冻结）

1. **Ruling A**（消除 L1，1 处政策字段 + 1 处常量）—— **已完成**（R14）。
2. **Ruling C**（消除 L3 绝对计数耦合，含两条新负例）—— 未开始。
3. **Ruling B**（166 条分类与分批处置，B1 → B3 → B2）—— 未开始；**必须先落 B1/B2/B3 归属表**。
4. 以上三步完成后，`GOV-DECLARATION-SCAN-CLEANUP-1` 的 AC2/AC3/AC4 才有判定地面；
   AC1（本裁定落盘）在本文提交后即可闭合。

## 边界声明

本裁定只处理**声明扫描债务的治理口径**，不构成对方案/契约/范围的再批准，
也不改变任何产品行为；`protected_roots = 5582` 的**不得缩小**约束继续有效。
