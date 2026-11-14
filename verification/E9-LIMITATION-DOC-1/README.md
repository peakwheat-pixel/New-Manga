# E9-LIMITATION-DOC-1 证据

基线 `2d34914c2`。执行 ZCode 裁决要求的**最小产品动作：文档**。

## 做了什么

新建 `doc/reviews/E9-KNOWN-LIMITATION-REGISTER.md`，按 ZCode 核实的**真实口径**登记限制，
并在其中建立与 C-17（冻结契约）、E-9 finding、两份证据目录的引用关系。

## 为什么**不改** C-17

核实发现 `doc/plan/FEA-CONTRACT-FROZEN-C17.md` **被 pin 覆盖**：
其附录 §"v1.2 UNFREEZE 重冻记录" 明确写着 `verify_pins` 三指纹
（工作树 `cdeee4872e29b56c7d67de65dabd6ca9b31006eecde61d99b83e29fe5a4fc96c`、blob `2cccc3c6…`、58134 bytes）
与 `truth 17 OK + C17 OK = 18/18`。

`tools/governance/verify_pins.ps1` 的动态 pin 逻辑（`$rec = Join-Path $root "doc/plan/FEA-CONTRACT-FROZEN-$id.md"`）
覆盖 C-17，**改它会让 18/18 变红**。

改动冻结契约需要**正式 UNFREEZE**（新载体 + 独立字节复核 + 三指纹重算）。
而本限制**不需要改契约语义** —— 契约定义的是"恢复需要容器路径"，产品只是**暂时无法提供**。
故用独立登记文件承载，**不动冻结字节**。

## 表述纪律（写进登记文件本身）

**不得**写"仅崩溃恢复不可用"：ZCode 核实 `AcknowledgeAsync:468` 与 `RecoverAsync:581` 是同一路径，
**正常 ACK 同样不可用**。写窄了就是错误陈述。

## 未做

- 未改 C-17（有意）。
- 未实现 mint-time 路径映射（ZCode 列为后续 Task 候选）。
- 未跑测试（本次只加文档）。
