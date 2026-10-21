# GOV-DECLARATION-RESIDUAL-32-AUDIT-1 独立只读 Review

## 结论

**changes_requested**

32项研究切片的主体事实基本成立，但矩阵中至少有两处会误导“文件是否被跟踪”和“NDJSON对象计数”的明确表述错误。修正这些文档表述后可再复审。本次不批准工具、例外表、历史 source/pin 写入，也不批准清理、父 Task done 或“只剩 main”。

固定点：

- base：`c0a9cb7962669cb4e987af51260f68850f4fe3b0`
- 证据内容交付：`22bd5e07af5710af2359827a45fdf658186f578d`
- reviewed_head：`f6184f3babf473d639932016fba328224e5d7fe6`
- 当前 HEAD：`f6184f3babf473d639932016fba328224e5d7fe6`（main）
- 提交序列：`1681489e8` 冻结 → `049fe5aa0` 认领 → `22bd5e07a` 32项证据 → `f6184f3ba` 元数据/Handoff。

## P0

无。

未发现审查期间修改 source、工具源码、ACL、refs、租约或配置；未发现把原32 errors消解成清理 PASS；未发现删除、迁移、apply、GC/prune/push。

## P1

### P1-1 R24 被错误描述为“未跟踪文件”

`matrix.json` 的 R24：

- 原错误 message 明确是 `unparsable tracked JSON`
- `tracked` 为 `true`
- `source-facts.json` 中该 P02 文件同样为 `tracked: true`

但 R24 的 `protection_impact` 写成“未跟踪文件仍归原作者”。这把 R23 的未跟踪属性错误复制到了 R24。当前实际未跟踪来源只有两个：P02 的 `run-baseline-20261014T0430CST-ac3fix.json` 和 P22 的 `codex-p22-task-r4-malformed-snapshot-7ebd7d40.md`。

建议精确改为：

> R24 为 tracked 原始日志，不得改写、截取或提交替代版本；未跟踪的 R23 原文件归原作者，不提交。

R24 的 `tracked=true` 与原 `message` 保持不变。

### P1-2 “6/64个meta-observation-closed对象”表述不准确

`matrix.json` 的 R23/R24 `finding` 及 `report.md` 第11行均写成类似：

> 分别6/64个meta-observation-closed对象

独立逐行解析的实际结果是：

- R23：6个值，`meta=1`、`observation=4`、`closed=1`
- R24：64个值，`meta=1`、`observation=62`、`closed=1`

也就是说，6和64是**对象总数**，不是“6/64个都是 meta-observation-closed”。每份流各有1个 meta、1个 closed，其余为 observation；全部值被完整消费，指定 resource 身份键命中为0。

建议改为：

> R23/R24 分别完整消费6/64个 NDJSON 值；每流为1个 meta、1个 closed，其余为 observation；未命中 resources/resource_type/source_path/destination_path/resource_manifest/resourceManifest 身份键。

这样既保留“完整消费、0命中”的结论，也不会把对象类型扩大。

## P2

### P2-1 `checkpoint.md` 是未登记过程文件

`verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/checkpoint.md` 已随本 Task 提交，但不在 Canonical Evidence 表，也不在用户给出的 scope 文件清单内。`check.ps1` 明确警告：

> evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：...\checkpoint.md

建议将其移入 workspace 自有输出，或在证据清单中登记为 SOURCE_PIN/过程文件；不要让它处于“已提交但不登记”的模糊状态。

### P2-2 “最初两次审计36项”缺少两份可核验记录

初始失败文件确实存在，且可解析：

- 36 errors
- 相对 scope 的32项：**多4条、少0条**
- 4条新增错误全部来自 `source-facts.json` 的 `$.sources[...].relevant_resources[...].record.*`
- 当前 `source-facts.json` 已改为4个 `verbatim_record_json` 字符串，结构化声明键为0

这说明“4条重复来自把原 resource 记录以对象引用递归扫描”的解释是正确的，方向也正确。

但当前只能看到一份 `initial-observation-duplicate-audit.json`，其 `generated_at` 为一个时间点；“两次审计36项”没有两份独立输出可核验。建议要么补第二份运行记录，要么把表述改为“初始审计曾为36项（保留一份失败输出）”。

同时，`preservation-validation.json` 只给出 `same_32_error_multiset: true` 和截断的 `audit_output`，没有完整32错误身份多重集。若要让后续审查者仅凭版本化证据复核，建议附完整 error 身份列表或其稳定 hash。

### P2-3 R30/R31 的“隔离副本源/真实用户源”措辞不够精确

`verification/P19-UI-FIX-1/resource-manifest.json` 中：

- `resources[2]`：`resource_type=isolated-user-data-copy`，`source_path` 为 `%APPDATA%/...`，destination 是隔离副本目录
- `resources[3]`：`resource_type=user-data-source`，`source_path` 同为 `%APPDATA%/...`，destination 为 `Same source location`

两条记录的 `source_path` 实际相同。矩阵“分别是隔离副本源与真实用户源”容易被读成两个不同源根。结论“不能重复计成两套同一用户数据”是对的，但建议改成：

> `resources[2]` 与 `resources[3]` 共享同一 `%APPDATA%` source_path；前者 destination 为隔离副本，后者 destination 为原位置。故只能计为一个用户数据源根，副本不能替代源保护。

## 实际核验结果

| 项目 | 结果 |
|---|---|
| scope 32 vs matrix 32 的 code/file/locator/message | **PASS**，0处不等；matrix 额外保留 id，R01–R32完整 |
| 分类计数 | **PASS**：6格式/非资源 + 12广域 + 7历史身份 + 2模板 + 2 NDJSON + 3 NUL = 32 |
| 12广域错误=6声明/5唯一根 | **PASS**：5根为 workspace 根、task-envs、worktrees、review-scratch、temp |
| 17来源集合 | **PASS**：15 tracked、2 untracked；来源集合与 scope 完全一致 |
| 17来源 raw SHA | **PASS**：全部用 `Path.read_bytes()` 复算一致 |
| 15个 tracked 来源的 `git show base:path` blob | **PASS**：按 stdout bytes 复算，SHA 与记录一致 |
| 3个既有 EOL 差异 | **PASS**：`P09-MANAGED-READ-ROOT-TRUST-1.md`、`ENV-BUNDLE-1-FU1/resource-manifest.json`、`P19-UI-FIX-1/resource-manifest.json`；磁盘 raw 与 base blob 不等，未用归一化字节替代 pin |
| 2个未跟踪来源 | **PASS**：仍为 `??`，未被提交；P02 ac3fix 与 P22 malformed snapshot |
| 5个 direct-reference-facts | **PASS**：5个文件均存在，SHA 全部一致 |
| 作者归属 | **PASS**：32项 `actual_file_writer` 均为 UNKNOWN；未把 Git 用户名 `peakwheat-pixel` 或快照内 owner 当作实际文件作者 |
| NDJSON 完整消费 | **PASS**：R23 6/6、R24 64/64 行解析成功；指定身份键命中0 |
| 3个 NUL 文件严格 UTF-8 | **PASS**：均可 UTF-8 解码；NUL 计数为1/1/2；P14 两文件抬头“非独立Review”保持 |
| 初始36→32机制 | **PASS（结构层面）**：36 = 原32 + 4条来自 `relevant_resources[].record` 的递归新声明；当前已改为 `verbatim_record_json` 字符串 |
| `git diff --check base..head` | **PASS**，exit 0 |
| diff 范围 | **PASS**：仅本 Task 文档、Handoff、verification 证据及 `STATUS/REBASELINE_PLAN/TASK_LEDGER` 治理元数据，无代码 |
| 98 heads / 136 worktrees | **PASS** |
| `check.ps1` | **PASS（3 warnings）**；其中 `checkpoint.md` 未登记，需按 P2-1 处理 |
| 产品/工具测试 | **NOT_RUN 合理**：无代码变更，未把它写成 PASS |

## 未核验 / 明确限制

1. **当前审计的 exit2 与原32完整多重集未由 Reviewer 实测。**  
   我按授权尝试运行 `--audit-declarations --out ...\reviewer-audit`，但在创建输出目录时被拒绝：

   `REFUSED: OUT_CREATE_FAILED: ... [WinError 5] 拒绝访问`

   未重试、未改 ACL、未改运行环境。因此 `preservation-validation.json` 的 `audit_exit=2`、`same_32_error_multiset=true` 仍是 Owner 证据，不冒充 Reviewer 实测。初始36文件本身已由我解析核对。

2. **Task8 pin 的生成代码未静态审计。**  
   未在证据中找到名为“Task8”的独立 pin 文件；但全部15个 tracked 来源的 base blob、磁盘字节和 SHA 已按字节复算一致。只能证明产物一致，不能从现有证据证明生成实现绝对没有使用 `text=True`。

3. **R30/R31 历史绝对用户根未确认。**  
   只能确认当前记录中的 `%APPDATA%`、两个 JSON record 及其相对文件/hash；不能证明历史执行账户、绝对用户根或 copy→source 的唯一历史映射。

4. **清理安全性未证明。**  
   本轮不证明任何资源可删除，不证明父 Task 可 done，不证明“只剩 main”。

## 裁决边界

- 修正仅限文档、证据说明和 Handoff 的精确措辞；不改原始 source、不改工具、不改例外表、不改 pin、不改 ACL。
- 修正后仍需在新固定 head 上复审。
- 即使复审通过，批准的也只是 **32项只读研究切片**，不授权工具/例外表/历史 source/pin 写入，不授权清理、迁移、父 Task done 或“只剩 main”。
- `STATUS`/r212 禁令、全部资源保护、原32 errors fail-closed 状态继续有效。

**建议下一步：** Codex 按 P1/P2 精确修正 `matrix.json`/`matrix.md`/`report.md`/`preservation-validation.json`/`checkpoint.md` 的状态或措辞，提交后固定新 head，交 DSH 复审；不要修改任何被审 source 或运行 cleanup。
