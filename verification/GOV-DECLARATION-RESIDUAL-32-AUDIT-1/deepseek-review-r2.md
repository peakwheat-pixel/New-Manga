# GOV-DECLARATION-RESIDUAL-32-AUDIT-1 第二轮独立复审

## 结论

**approved**（仅批准32项只读研究切片；附1项非阻塞 P2 格式项）

固定点：

- base：`c0a9cb7962669cb4e987af51260f68850f4fe3b0`
- 修订内容：`e2b8d19ed47a5ecde53d53f7fa17be6a2e10c29f`
- reviewed_head：`927e06f8b25563afbc7acbcc25d19fe775d1ded6`
- `e2b8d19ed..927e06f8b` 仅修改 Task 与 Handoff 两个文件，符合“其后只有 pins 元数据”。
- 当前 HEAD 即 `927e06f8b`，main。

## 五项修正核验

| 项 | 结果 | 实测要点 |
|---|---|---|
| P1-1 R23/R24 tracked 属性 | **PASS** | R23 `tracked=false`，明确“未跟踪、归原作者、不提交”；R24 `tracked=true`，明确“tracked、现有 Git blob 保留、不改写/截取/提交替代”；两条原 `message` 未变 |
| P1-2 NDJSON 计数 | **PASS** | `matrix.json`、`matrix.md`、`report.md` 均明确：R23 共6值，`meta=1/observation=4/closed=1`；R24 共64值，`1/62/1`；不再表述为“6/64个同一种对象” |
| P2-1 checkpoint 登记 | **PASS** | Canonical Evidence 现有10行；EV10 为 `checkpoint.md`，class=`SOURCE_PIN`；`check.ps1` 不再报告未登记过程文件 |
| P2-2 初始36项表述 | **PASS** | `initial_attempts.evidence_count=1`，措辞为“初始审计曾为36项；保留一份失败输出，不宣称两份独立运行记录”；report/Handoff 已删除“两次”；新增完整32 `error_identities`，与 scope 逐 `code/file/locator/message` 顺序及多重集完全一致，32项唯一；按声明算法复算 SHA=`918929061f1520c57a3a992f2df85d883dc2c655b409948ece40c36f5b47a873`，与 `error_identities_sha256` 一致 |
| P2-3 R30/R31 同一用户源根 | **PASS** | 明确 `resources[2]` 与 `resources[3]` 共享同一 `%APPDATA%` `source_path`；区别仅为 destination 是隔离副本或原位置；明确只能计一个用户数据源根 |

## 10个 Canonical Evidence pin

按 Task 文档中 `|EV` 行取 `split('|')[3:6]`，逐项用 `Path.read_bytes()` 与 `subprocess.check_output(['git','show',commit+':'+path])` 比较原字节及 SHA：

- **10/10 PASS**：磁盘 SHA、Git blob SHA、表中 pin 三者一致。
- 全部10个 pin 指向 `e2b8d19ed`；其后的 `927e06f8b` 未改证据文件。
- EV9 为 R1 独立 review，EV10 为 checkpoint；两者 class 均为 `SOURCE_PIN`。
- EV1–EV4 原 pin 不变；EV5/EV7/EV8 因修订而更新；EV6 同步更新。

## 仓库与门禁

- `git diff --check base..head`：**exit 2**。仅 `verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/deepseek-review-r1.md` 第121、128、131、134行有 Markdown 行尾双空格；这是 R1 原文未改造成的格式项，不影响32项研究内容。
- `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS（2 warnings）**。仅剩“14个非终态 Task”和“STATUS 达到预算80%”两项既有警告；checkpoint 未登记警告已消失。
- 98 heads / 136 worktrees：**PASS**，未新增 branch/worktree。
- `base..head` diff 仅本 Task 文档、Handoff、evidence 及 `STATUS/REBASELINE_PLAN/TASK_LEDGER` 治理元数据，无代码、工具源码或原始 source 修改。

## 实测 / 复用 / 未测

**本轮实测：**

- 五项修正文本与字段。
- 10个 EV pin 的磁盘/Git blob/SHA。
- 32个 `error_identities` 与 scope 的逐项一致性、唯一性及 SHA 复算。
- `git diff --check`、diff 范围、`check.ps1`、98/136、`e2b8d19ed..927e06f8b` 范围。

**复用 R1 实测，未重新大扫来源：**

- 17个来源 raw SHA、15 tracked / 2 untracked、3个 EOL 差异、5个 direct-reference-facts、NDJSON 完整消费、NUL/UTF-8、P14 抬头及作者 UNKNOWN 结论。  
  依据：`scope.json`、`source-facts.json`、`direct-reference-facts.json` 在 `22bd5e07a..927e06f8b` diff 中未变化，可沿用 R1 的字节核验结果；不冒充本轮新测。

**未测：**

- 未重新运行声明审计；`preservation-validation.json` 的 `audit_exit=2`、`same_32_error_multiset=true` 以及完整32身份来自 Owner 先前审计落盘记录，本轮只验证记录完整性和哈希，不冒充复跑。
- 历史绝对 `%APPDATA%` 用户根、copy→source 历史映射仍未确认。
- 任何清理/删除安全性、父 Task done、只剩 main 均未证明也不批准。
- 生成脚本是否绝对未用 `text=True` 未静态审计；10个 pin 的产物字节与 SHA 已复算一致。

## P0/P1/P2

- **P0：无。**
- **P1：无。** 上轮 P1-1、P1-2 均已按要求修正。
- **P2：** `git diff --check` 因 R1 原文4处行尾双空格非零。属于非阻塞格式项；建议保持 R1 原文不变，若仓库强制要求 `diff --check` 为零，另以路径级 whitespace 策略处理，不回写 R1。

## 批准边界

本批准仅覆盖 **32项只读研究切片**。剩余32 errors、`STATUS`/r212 保护、清理禁令继续有效；不批准后续工具、例外表、原始 source/pin 写入，不批准清理/迁移，不批准父 Task done，也不批准“只剩 main”。

**建议下一步：** Codex 接受本 review 并完成 Handoff/核销；P2 行尾空格另行决定是否接受，不得因此改写 R1 原文或原始 source。
