# 证据 pin 基准口径裁定提案

**状态：提交 ZCode 独立 Review 与最终 adjudication；在 ZCode 作出决定前，本文件是提案，不是生效裁定。** 本提案仅讨论后续证据 pin 口径，不授权修改 checker、Task 模板、历史 pin、`.gitattributes`、冻结契约或源码。

## 依据与快照

- 冻结基线：`verification/FEA-15-PIN-EOL-GOV-1/pin-inventory.json`，测量 HEAD `948d73e0629869e560df9a2b2d8a357cec67027f`，共 5,350 行（Task pin 5,332 + 冻结记录 18）。
- 最终交付测量 inventory：`pin-inventory.json`，测量 HEAD `e9f7bb1b48c885cb329848d2d3591e145ff3d229`，共 5,376 行（585 张 Task 卡、5,358 条 Task pin、18 条 frozen 记录）。相对基线新增 26 行、删除 0、同键字段变化 0；完整差异见 `pin-inventory-delta.json`，完整 r194 观测矩阵见 `pin-r194-baseline-matrix.json`。三项生成日志均记录命令、时间、HEAD 和 `EXIT=0`。
- 交付快照 basis 互斥计数：`WORKTREE=3,467`、`BLOB=327`、`MIXED=1,009`、其他 573。其他 573 为 `INCONSISTENT=160`、`UNPINNED=293`、`UNRESOLVED_COMMIT=68`、`EXTERNAL_UNAVAILABLE=47`、`MISSING=3`、`COMPOSITE_PATH=2`。26 条增量为旧 `FEA-15-PIN-EOL-GOV-1` 的 24 条证据行与本 Task 的 2 条 release 行；basis 差值是 `WORKTREE +16`、`MIXED +10`。
- 更早的 `pin-inventory-preliminary-da4a60b.json` 与初步差异保留作过程快照；它与交付快照计数相同，但不替代测量 HEAD=`e9f7bb1...` 的正式 inventory。
- `tools/governance/check.ps1` r194 对 lifecycle Task 的 Canonical Evidence 行先比较工作区 SHA；不匹配时，若记录 commit 确实包含该路径，再比较该 commit 的 blob SHA；任一匹配即通过。它只检查当前治理作用域/当前 Task，不会逐条执行整个历史 inventory。`verify_pins.ps1` 的 18 条 FROZEN pin 是另一条独立门禁。
- Inventory 的 `class` 辅助字段有解析限制：复制脚本只在表头归一化后精确等于 `class` 时填入该值；本 Task 现有表头 `class (CANONICAL / SOURCE_PIN)` 被归一化为另一字符串，故本 Task 两条 release row 的 `class` 在机器 JSON 中为空。历史 `class_counts` 也包含非标准值，不能作语义统计。该限制不改变 row count、source/evidence/path/commit/SHA 或 basis 比较；本 Task 不修历史脚本，Review 时需将其作为 inventory limitation 核查。
- 上游 `FEA-15-PIN-EOL-GOV-1` 的 checkout 矩阵记录 4 种样本 × 3 个 Windows checkout，共 12 条观察：head blob 12/12 匹配，pin 结果 7 PASS / 5 FAIL。样本结果只表示测量，不等于历史 pin 的有效性裁决。

## 提案一：新 pin 默认基准与文本/二元规则

### 建议结论

1. 仓库内新证据默认使用 `BLOB`：SHA-256 对准 Canonical Evidence 行记录的 commit 中该路径的**精确 Git blob 字节**。先提交证据文件，再读取 `git cat-file blob <commit>:<path>` 的字节计算 SHA-256；commit 必须包含该路径。
2. 文本文件不隐式转换 LF/CRLF，不按工作区编辑器或 `core.autocrlf` 重算。若产品需要文本证据统一 LF，必须另有路径范围明确的 `.gitattributes` Task；本 Task 不要求也不授权全局归一化。
3. PNG、ZIP、PDF 等二元文件同样按精确 blob 字节计算；不得解码、重压缩或做内容规范化。文本/二元只影响文件内容本身，不改变 `BLOB` 的哈希算法。
4. 仓外原始输入不能伪装成 Git blob：在可读取时记录精确原始字节 SHA-256，并标成明确的外部 basis；不可读取时记 `NOT_RUN`/`BLOCKED`，不得推定 PASS。`WORKTREE` 只允许在明确声明且解释其环境可复现性的例外中使用。
5. 单独释放后续实现 Task，为新 Canonical Evidence 行增加显式 `sha256_basis` 元数据并由 checker 强制校验；在实现前，上述 `BLOB` 是治理提案和人工登记要求，r194 仍会接受旧格式中的工作区 hash。

### 事实

- 基线有 3,451 条 WORKTREE-only 和 327 条 BLOB-only；999 条同时匹配，无法仅靠 hash 推断其作者当时意图。
- 初步盘点分别有 3,467 / 327 / 1,009 条；26 条增量没有增加 573 个异常类观察。
- 既有 FEA-08 对部分文本证据采用 blob/LF，并把 PNG/GIF/ZIP/PDF 按二元字节保留；它是有限范围先例，不是全仓统一规则。
- r194 以 OR 语义接受 worktree 或 commit blob；当工作区与 blob 不同，当前 Task 表没有独立列记录作者选择了哪一个。

### 推论

- `BLOB` 可把新仓库证据绑定到 commit，并避免检查结果依赖检出时的 EOL 转换；它不要求所有文本 blob 变成 LF。
- 专用 basis 字段可消除新行的歧义，同时把旧格式空缺保留为兼容状态；不用一次迁移 5,376 条历史记录。
- 对二元与文本一律哈希精确 blob，规则更容易复算，且不会把文件扩展名误当成内容类型证明。

### 未知项

- Linux fresh clone 的全量表现未测；当前矩阵只覆盖 Windows `core.autocrlf=true/false`。
- 573 个异常类行尚未逐行判定根因；47 个仓外路径不可用，不能从本机工作区推定其内容。
- 当前 Task/模板/checker 没有 basis 字段；实施前需由 ZCode 明确接受字段名、外部值域与旧格式兼容规则。
- Inventory 的 legacy `class` 列在非标准表头下不完整；如果后续方案需要依赖证据 class 作处置条件，应先修复/替代解析器并独立复算，不能从当前 `class_counts` 推出全集构成。

### 反证条件

- 若固定 commit 的 blob 字节不能在仓库对象库中稳定复取，或受支持 Git 环境中对同一 `<commit>:<path>` 算得不同 SHA，`BLOB` 提案须暂停并调查工具/对象读取实现。
- 若某类外部输入必须保持工作区状态且不能产生 Git blob，应作为显式外部/工作区例外单独裁定，不能以改写通用默认规则掩盖。
- 若显式 basis 字段导致旧 6 列 Task 行被误读或改变其 r194 结果，实施提案须撤回或修正。

### 暂停门槛

停止任何落地，直到 basis 值域与旧格式识别方式由 ZCode adjudicate；实施前完成受影响行全集、样本与 pre-change 矩阵；所有旧 Task 维持原 hash 与原文；实现不得触碰冻结契约或 18 pins。

## 提案二：既有全集分类与处置

### 建议结论

- 将 `BLOB`、`WORKTREE`、`MIXED` 视为观测分类：分别表示仅 blob 匹配、仅当前工作区匹配、两者都匹配；分类本身不改写任何旧 pin，也不声称某条记录的作者意图已知。
- 保留 `INCONSISTENT`、`UNPINNED`、`UNRESOLVED_COMMIT`、`EXTERNAL_UNAVAILABLE`、`MISSING`、`COMPOSITE_PATH` 的原观察。573 行不自动等于损坏、无效或待迁移清单；逐行处置须有对应 Task、引用检查与证据。
- 本 Task 不修补、补 hash、删除、归档或改写任何历史条目。18 条 FROZEN pin 仍由 `verify_pins.ps1` 独立保护。

### 事实 / 推论

- 基线与初步当前盘点的 573 个异常类行完全相同；当前增量 26 条落在可匹配的 WORKTREE/MIXED 分类。
- 上游 Review 对 160 条 `INCONSISTENT` 的结论是“需要分类，不是 corruption verdict”。哈希不匹配也可能由字节基准、commit/path、外部来源或缺少 pin 元信息造成。
- 所以分类要描述可复算的字节观察；要决定有效性、修复或迁移，必须另查 Task、来源和受保护数据。

### 未知项 / 反证 / 暂停门槛

- 160、293、68、47、3、2 各行的根因、当前引用者和授权目标未全部核查；这不是本 Task 的逐行迁移清单。
- 若后续核验发现同一条记录在固定输入下分类不可复现，先修订观察器并重算，不能按旧分类直接处置。
- 任何 bulk rewrite、path-wide EOL 规则或 history pin 替换均立即超出本 Task，必须停止并释放独立实施范围。

## 提案三：r194 双基准语义

### 建议结论

- **旧格式继续保留 r194 双基准兼容**，避免把 WORKTREE-only 旧条目一次改判失败；`MIXED` 仍是歧义分类，不强行归入某一意图。
- **新格式只接受显式 basis**。建议新增 `sha256_basis` 列：`BLOB`、`WORKTREE`、`EXTERNAL_SHA256`。旧 6 列表视作 legacy 并沿用 r194；新 7 列表必须逐行填写合法值。`BLOB` 比较精确 commit blob；`WORKTREE` 只比较明示的工作区字节；`EXTERNAL_SHA256` 只比较可读取外部来源字节且不得填写仓库 commit。
- 不在本 Task 实施 schema/checker；在 successor Task 独立实现、复核并通过全量回归前，不收敛旧格式语义。新行的默认 BLOB 提案由文档约束，自动强制要等该实施 Task。

### 事实 / 推论 / 未知

- `check.ps1` 当前 Canonical Evidence parser 至少接受 6 列并读取第 6 列 `class`；`task_ledger.py` 只汇总 Task frontmatter 状态，不读取 Canonical Evidence 表。可在 `class` 后追加 basis 列以保持既有 class 列位置，但 checker 仍需显式解析并验证新表头。
- 保留旧表头与新增表头的区分，可为遗留兼容定义清晰边界；但需测试旧 Task、外部路径、缺 commit、二元和混合 EOL 行。
- 具体 checker 逻辑、命令退出和跨平台对象读取仍未知，必须在隔离 clone 验证。该矩阵和 dry-run 未在本 Task 执行。

### 反证条件 / 暂停门槛

- 任一旧 6 列 Task 的现有 PASS/FAIL 发生意外变化，或新表头允许空/未知 basis 继续 PASS，均阻止实施 Task 通过。
- 若需要修改 `.gitattributes` 或改变 `verify_pins.ps1` 的 FROZEN 语义，另行冻结范围；不得把它们塞入 basis checker Task。

## 提案四：R-001

### 建议处置

将 R-001 保留为 **open / non-blocking P2 并转交后续 basis 字段与兼容性实施 Task**；不在本 Task 将其标为已修复。R-001 所列四个工作区字节 pin 与 blob 值不同，缺少显式 basis 声明；当前 r194 仍兼容，故不阻断只读裁定交付。

### 事实 / 推论

- 上游 Review `doc/reviews/FEA-15-PIN-EOL-GOV-1-r1.md` 给出了 `pin-inventory.json`、`checkout-matrix.json`、`gate-final.log`、`resource-manifest.json` 的 worktree/blob 双 hash，并登记 R-001 open P2。
- 该问题不因新增 BLOB 默认而自动消失；四条既有记录仍需保留原 pin。后续 Task 可在不改 hash 的前提下登记其明确 basis，并验证 checker 新旧格式行为。

### 关闭条件 / 反证 / 暂停门槛

- 关闭前需由后续获释 Task 对四条记录的来源、固定 commit、当前工作区字节和 blob 字节逐一复算，写入显式 basis，并证明旧数据没有被静默重写。
- 若复算与上游 Review 的值不一致、路径缺失或影响到受保护历史，应保持/重开 R-001 并停止变更；不得用 `check.ps1` 当前 PASS 代替 basis 证明。

## 范围与最终裁定

本提案不改 `.gitattributes`、`check.ps1`、`verify_pins.ps1`、`task_ledger.py`、Task 模板、冻结契约、Schema、依赖或任何历史 pin；不运行 renormalize、迁移、Linux clone 或产品测试；不 push。下一 Task 只有 ZCode adjudication 后才可按正式范围单独释放。本文件自身不解除任何门禁或授权。
