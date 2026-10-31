# FEA-C12 治理检查器职责边界（草案）

状态：**DRAFT / 未冻结**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-12、`tools/governance/check.ps1`（863 行 / 52 KB）、[09_COLLABORATION](../09_COLLABORATION.md)

**边界声明**：本文件是**职责边界说明**，不改检查器代码、不冻结契约。

---

## 1. 检查器是什么

`tools/governance/check.ps1` 是**只读机械检查器**：它解析仓库内文档的**结构**，断言治理指针/证据/预算的一致性，输出 `PASS / FAIL (n errors, m warnings)`。

**它检查的是形式，不是内容。**

## 2. 断言面（当前）

| 类别 | 断言 | 失败级别 |
|---|---|---|
| **STATUS 指针** | 当前 Task 可解析、指向非终态 Task、上一 Task 存在 | Error |
| **PLAN 指针** | `READY 节点` 与 READY Task 一致；`当前 DAG` 合法 | Error |
| **Task front matter** | 必填字段、status 合法性、depends_on 存在 | Error |
| **Canonical Evidence** | 6 列、path 存在、commit 格式、sha256 格式；**blob(LF) 基准**比对 | Error |
| **Resource Manifest** | 引用唯一、JSON v1 schema、disposition 规则、`ALREADY_ABSENT` 语义 | Error |
| **done Task 的 evidence_dir** | 不得含未登记文件 | Error |
| **TASK_LEDGER** | 非终态计数与各卡一致（生成器 `task_ledger.py`） | Error |
| **AD-003/ADJ-001 哨兵** | 字符串存在、唯一 | Error |
| **预算** | STATUS ≤ 3200 B **且 ≤ 45 行**；PLAN ≤ 7000 B / 64 行 | **超预算 = Error**；80% 起 = Warning |
| **非终态 Task 计数** | 提示用（不据此批量关闭） | Warning |

## 3. 检查器**不**做什么（语义层）

| 不做 | 归谁 |
|---|---|
| 判断契约条款是否正确/一致 | 独立 Review（上下文独立）+ DSH 裁决 |
| 判断证据是否**真实**（日志是否伪造） | 独立 Review 复跑 |
| 判断实现是否符合契约 | 实现 Task 的 AC + Review |
| 判断 Architect 决策是否合理 | 用户裁决 |
| 解析主题包 / `nm.fluent.visual/1` 语义 | ThemeEngine 内校验器（C-02 §4） |
| 校验 AD-002 的正文语义 | 独立 Review |

**准则**：`check.ps1 PASS` 只证明「文档结构自洽」，**不构成**契约语义证据（C-01b 的边界声明已写明）。

## 4. 扩展规则

- 新增断言须走**独立治理 Task**（不得在实现 Task 中顺手改检查器）。
- 新断言的**判定必须是可机械判定的**（字符串/格式/计数/存在性），不得引入主观判断。
- 每新增一条 Error 断言，必须在同一次提交中更新本文档 §2 表。
- 检查器**不写仓库工作树/索引**（当前实现会写 `%TEMP%` 临时文件做 blob 比对，属允许的临时副作用）。

## 5. 与 Review 的分工

| 问题 | 检查器 | Review |
|---|---|---|
| 证据 pin 是否指向正确提交 | ✅ 机械比对 | 复核「该提交是否真的包含该内容」 |
| STATUS 是否指向正确 Task | ✅ 机械 | 复核「该 Task 是否真的在进行」 |
| 契约条款是否与方案一致 | ❌ | ✅ |
| 冻结条件是否全部满足 | ❌（除结构） | ✅ + 用户裁决 |

## 6. 冻结条件

1. 独立复核通过；
2. 检查器现有断言与本文档 §2 表一致（可机械核对）；
3. `check.ps1` PASS。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：断言面 10 类、不做清单 6 条、扩展规则 4 条、与 Review 分工 4 行、冻结条件 | DSH |
