# Pin basis 实施影响面方案（仅计划，不执行）

**状态：供 ZCode Review/adjudication。** 本文件为 `FEA-15-PIN-POLICY-1` AC2 的方案输入；不创建/释放 successor Task，不修改 checker、模板、历史 pin、`.gitattributes` 或数据。

## 1. 建议的后续实施边界

候选名称：`FEA-15-PIN-BASIS-ENFORCE-1`（仅草案，不是已登记 Task）。目标是让**新 Canonical Evidence** 明示 basis 并由 checker 验证，同时让既有 6 列历史表保持 r194 兼容。

建议纳入的文件面（Task 释放时重新冻结）：

- `doc/templates/TASK.md`：在 Canonical Evidence 表 `class` 后增加 `sha256_basis` 列，并写清 `BLOB` 默认、`WORKTREE` 例外、`EXTERNAL_SHA256` 外部来源语义。
- `tools/governance/check.ps1`：识别旧 6 列与新 7 列表；旧表继续 r194 双基准，新表必须逐行填写 basis 并按所选字节源校验。仓库内 `BLOB` 需有包含路径的 commit；外部 SHA 不得冒充仓库 blob。
- `tools/governance/tests/test_path_header_compat.py`、`tools/governance/tests/test_ac_gate.py` 与新建的 pin-basis 夹具/测试：覆盖旧格式兼容、新格式缺值/非法值、BLOB-only、WORKTREE-only、外部来源不可用、binary 与 mixed-EOL 行为。
- 必要时补充治理文档中的编写约定；经检查 `tools/governance/task_ledger.py` 仅读取 Task 状态/ID，不解析 Canonical Evidence 表，当前方案预计无需修改它。

明确排除：历史 SHA/commit/path 重写、历史表批量补列、`.gitattributes` 全局或路径规则、`git add --renormalize`、18 条 `FROZEN_PIN` 与 `verify_pins.ps1` 语义、冻结契约/Schema/API、产品源码/依赖、资源清理、push。若后续策略要改变任一排除项，必须另行释放范围。

## 2. 实测影响全集与基线

冻结基线 `948d73e0629869e560df9a2b2d8a357cec67027f` 的全量 inventory 为 5,350 行；delivery measurement HEAD `e9f7bb1b48c885cb329848d2d3591e145ff3d229` 的 [`pin-inventory.json`](pin-inventory.json) 为 5,376 行：585 张 Task 卡 / 5,358 个 Task pin 行 + 18 条 frozen 记录。相对基线 26 行新增、0 删除、0 同键字段变化；完整差异为 [`pin-inventory-delta.json`](pin-inventory-delta.json)，模型矩阵为 [`pin-r194-baseline-matrix.json`](pin-r194-baseline-matrix.json)。命令/时间/HEAD/EXIT 见各自 run log。

delivery snapshot 基础分类（互斥，单位为 pin 行而非文件）：

| 类别 | 行数 | 当前观测 |
|---|---:|---|
| `WORKTREE` | 3,467 | 仅当前工作区字节匹配 |
| `BLOB` | 327 | 仅记录 commit 的 blob 匹配 |
| `MIXED` | 1,009 | 工作区与 blob 都匹配 |
| `INCONSISTENT` | 160 | 两者都不匹配 |
| `UNPINNED` | 293 | 无有效 SHA-256 |
| `UNRESOLVED_COMMIT` | 68 | 无可用 commit 且工作区 hash 不匹配 |
| `EXTERNAL_UNAVAILABLE` | 47 | 当前机器不可读取外部来源 |
| `MISSING` | 3 | commit 与当前工作区均无目标文件 |
| `COMPOSITE_PATH` | 2 | 单行合并多个路径 |
| **合计** | **5,376** | `3,467 + 327 + 1,009 + 573` |

The exception subtotal is `160 + 293 + 68 + 47 + 3 + 2 = 573`; it must not be added again as a separate basis class. Current inventory also reports 4,758 unique repository paths, 4,664 present, with worktree pin-row EOL profiles `BINARY=453`, `CRLF=3,115`, `LF=1,298`, `MIXED_EOL=198`, `MISSING=145`, `NO_EOL=167`. EOL profile counts are a different dimension from the mutually exclusive basis rows; `MISSING` EOL profile does not mean the 3 `basis=MISSING` rows.

### r194 预变更匹配矩阵

按当前 r194 的 SHA 谓词（工作区匹配 **或** 可用 commit blob 匹配）套用 delivery inventory 的观测值，模型为：`MATCH_BOTH=1,009`、`MATCH_WORKTREE_ONLY=3,467`、`MATCH_BLOB_ONLY=327`，合计 4,803 行命中 predicate；其余 573 行未形成可通过匹配，其中 `NO_PIN=293`，`PIN_PRESENT_NO_MATCH_OR_UNAVAILABLE=280`。逐行样本、运行时间与 hash 比对见 [`pin_r194_matrix.py`](pin_r194_matrix.py)、`pin-r194-baseline-matrix.json` 和 run log。

**限制：** 这是由 inventory 的 hash 比较字段计算出的 r194 predicate 模型，不是对 5,376 行逐条执行 `check.ps1` 的日志。`check.ps1` 只验证当前 Task 作用域；真实 delivery gate 结果见 [`delivery-gates-e9f7bb1.log`](delivery-gates-e9f7bb1.log)：在 HEAD `e9f7bb1b48c885cb329848d2d3591e145ff3d229`，default/current TaskPath/prior TaskPath 均 PASS、各 3 warnings、EXIT 0；18 pins `18/18` EXIT 0；API `1/79/6=86` EXIT 0。

## 3. 代表与边界样本

最终 JSON 矩阵会从 delivery snapshot 复取这些记录及 SHA。下面路径和 hash 来自当前 preliminary inventory；`FEA-15-PIN-EOL-GOV-1` 的 12 行 checkout observation 另见其 `checkout-matrix.json` 与 `README.md`。

| 样本 | Task / evidence_id | pin basis | pin 与字节观察 | 边界意义 |
|---|---|---|---|---|
| Blob-only 文本 | `AGPL-RELEASE-1` / `delivery-report`，`verification/AGPL-RELEASE-1/REPORT.md` | `BLOB` | pin/blob `c7309d2b…`；worktree `803ac9db…`；worktree CRLF、blob LF | LF 检出匹配 blob；当前 CRLF 工作区不匹配 pin。 |
| Worktree-only 文本/JSON | `AD002-FOLLOWUPS-1` / `release-0.1.1-verify`，`verification/RELEASE-REPACK-6/verify.json` | `WORKTREE` | pin/worktree `39b0c6a1…`；blob `0329a81b…`；worktree CRLF、blob LF | `autocrlf=true` 与 `false` checkout 的工作区结果分歧；同一路径另有 `RELEASE-REPACK-6` pin 行。 |
| 混合 EOL 文本 | `FEA-06-PREREQ-1` / `E-P1-APPEARANCE`，`apps/desktop-avalonia/src/NewManga.Appearance/AppearanceJson.cs` | `WORKTREE` | pin/worktree `b0a02a18…`；blob `8e251bed…`；worktree `MIXED_EOL`、blob `LF` | 两种新 checkout 都不复现原混合字节；不能把混合 EOL 当作可通用规范化。 |
| 二元 PNG | `CHAPTER-SELECTOR-1` / `CS1-SHOT-BOOKSHELF`，`verification/CHAPTER-SELECTOR-1/screens/01-bookshelf-two-books.png` | `MIXED` | pin/worktree/blob `e5e79583…`；两侧 `BINARY` | 三个 Windows checkout 字节一致；二元样本要求 exact bytes，不转码。 |

缩写 SHA 仅便于阅读，机器完整 hash 与每行的 `pin_sha256`/`worktree_sha256`/`blob_sha256` 在 inventory 中核对。以上样本是已知边界输入，不代表随机抽样，也不代表所有文件都具有相同 EOL 规则。

## 4. 固定 pre-change 基线错误矩阵与 dry-run

后续 Task 释放后，在任何实现变更前冻结 exact delivery HEAD 与 5,376-row inventory。先生成上节的 hash outcome matrix，再在隔离 clone 运行**实际 checker**，把以下字段逐行记录：source Task、evidence ID、path、旧/新表头、basis、预期状态、当前 `check.ps1` 实际状态、commit-path 可用性、worktree/blob SHA、差异原因。模型矩阵与真实 checker 结果分开保存，不能把前者命名为“全量 check PASS/FAIL”。

计划步骤（本 Task 不运行）：

1. 仅在 successor Task 获释后，于 `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/` 创建隔离环境；基线 clone 固定到该 Task 的 `base_commit`，记录 Git/Pwsh/Python 版本、`core.autocrlf` 与 clean 状态。
2. 保存未变更 checker 的 pre-change 全量/样本矩阵与 default、当前 TaskPath、代表 legacy TaskPath、18 pins、API 的命令/HEAD/EXIT。该矩阵作为唯一对照，修改后不可覆写。
3. 在另一个隔离候选 clone 应用 successor Task 的实现；用 legacy 6 列、new 7 列 `BLOB`/`WORKTREE`/`EXTERNAL_SHA256`、缺 basis/非法 basis、路径缺失、commit 不含 path、binary PNG、CRLF 文本、mixed-EOL 文本等固定夹具逐项比较。
4. Windows 至少用 `core.autocrlf=true` 与 `false` 两种新 checkout；若 Task 释放时包含 Linux 支持声称，再增加 Linux fresh clone。逐项比较 pre/post matrix：旧格式的既有预期结果不得无故变化；新 `BLOB` 只认精确 commit blob，新 `WORKTREE` 只认声明的工作区字节，外部来源不可读取不得 PASS。
5. 检查意外 PASS、意外 FAIL、缺失/重复/路径变化及 binary/mixed-EOL 任何变异。任何不一致即停止，candidate clone 保留作证据，不合并、不 push、不在主工作树执行 renormalize。

本 Task 未创建 clone、未执行上述 dry-run，状态为 **NOT_RUN**。

## 5. 回退与停止规则

- 所有候选改动只在新 Task 专属隔离 branch/worktree 中；保留原始基线日志与 SHA。失败时放弃候选 commit/分支，不 cherry-pick、不改 `main`，修订新 Task 或重新冻结影响集。
- 若新字段无法区分旧 6 列与新 7 列、任何旧行门禁结果变化、外部/混合 EOL 行为不符预期、全量受影响集增减、或出现需要 `.gitattributes`/历史 pin rewrite 的要求，立即暂停，先由 ZCode adjudicate 是否另立 Task。
- 资源清理不属于回退动作；Task 结束前按 Worktree Safety Inventory 与 Resource Manifest 逐项处置。任何数据来源不清或用户数据一律保留。

## 6. 实施 Task 冻结输入草案

- 目标：对新 Canonical Evidence 行显式记录并校验 basis；旧 6 列表继续按 r194 兼容；不迁移历史 SHA。
- AC 草案：旧行结果回归；新 basis 值域和字节源测试；完整受影响清单 + 固定错误矩阵；binary/mixed-EOL boundary matrix；default/TaskPath/18 pins/API gates；Handoff、上下文独立 Review、ZCode adjudication。
- 允许范围候选：仅 `doc/templates/TASK.md`、经释放列出的治理说明、`tools/governance/check.ps1`、限定的 `tools/governance/tests/**` 与 successor 自身 `verification/**`；`task_ledger.py` 当前不解析 Evidence 表，除非新证据证明需要，否则不改。
- 禁止候选：FEA frozen contract、`verify_pins.ps1`、现存历史 pin/hash/commit/path、`.gitattributes`、renormalize、Schema/API、产品源码/依赖、资源删除和 push。
- 复核要求：新 ZCode CLI Review 上下文只读固定 delivery head；最终 adjudication 用与 Review 不同的 ZCode session。当前文档不创建 Task 卡、不登记 READY 节点、不预先释放范围。
