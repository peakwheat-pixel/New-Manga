---
document_id: FEA-00-codex-r2
kind: independent_review
reviewer: Codex
author: DSH
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_head: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_state: uncommitted_worktree_bytes_pinned_below
decision: changes_requested
---

# FEA-00 DSH r2 修订独立复审

## 结论

**`changes_requested`：1 项 P0、2 项 P1、1 项 P2。** R-01 的共享引用范围、R-02 的单条/批量形状和 R-03 的链接已有实质修订；但 AD-003 正文仍无依据地声称 AD-002 原始字节保留，且与其自己新增的三口径说明相反，按本轮用户要求对历史证据误述记 **P0**。检查器的断言面和权威指针仍可由无关文本满足，属于 **P1**。不得将本文解释为批准、运行时验收或 Task 释放。

本次只复审 DSH 撰写或修订的对象；Codex 是 Fluent 方案作者，不对自己的方案签发独立批准。结论绑定下表各文件的工作树字节；`main` HEAD 不能单独重建未提交的审查对象。与 r1 一样，不修改被审文件或其他人的未提交内容。

## 固定指纹与审查范围

| 对象 | SHA-256 |
|---|---|
| `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | `4ff0a3d25e5dc68de8b6ba16ff56ac86600181e502c8282aae16091e1a65faba` |
| `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | `17a89d15efc900299f1ddbc8599c401125e6596cb0d7c3a1beab24557f09da14` |
| `tools/governance/check.ps1` | `77be514d3693672637100eefdfe15b4d9edfe199d64300ae588f361d43bee76d` |
| `doc/00_INDEX.md` | `0dc43d2980666f13c32391e193f4b5450294a9e2132475b83d4ba2f05a46e306` |
| `doc/reviews/FEA-00-codex-r1-adjudication.md` | `ea2171de026e2399445336c129e230c1d17ecd7131869b1e98becf95ce5e728d` |
| `doc/reviews/FEA-00-dsh-r2-technical-recheck.md` | `d0bf89ff045e3c35ff9bf19d16a632a2c6dba78d51b4ae7062610ed366919eb3` |

源码 `main@1180cdba79e4d610521dde13f0c8a458220f9d90`，common dir `.git`。对照的 Codex r1 hash `f2fd02e0dcff49337c9251315aef3f3480446f98e567b594c63e2eee17693ba2`；冻结 M2-C1 hash `dfcd47cabe9831b270fb0a6f985e50ea9e5a34b165f2c776a8f1e34c777bae72`。`AGENTS.md`、`doc/STATUS.md` 的复核时 hash 分别为 `678bda95e6edace4cb9311ee1eeb825fd66974d372da0e50b866530e125acea0`、`e8fe3affdabe315394a53f0d710e5ba16d480650716ea97f541977ade3de4a64`。开始时工作区已有多项 dirty/untracked 内容；它们的存在不是本轮授权修改的依据。

## Findings

### R2-01 — P0：AD-003 §2 仍把未经证实的原始字节保留写成事实

- **事实**：`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:28` 仍断言 AD-002 的“正文与哨兵字符串保持**原字节**”。同一文件 `:145-146` 的 r2 更正明确承认 AD-002 添加了横幅、变更前工作树原始字节没有独立基线，不能声称每个原始字节未变；`doc/reviews/FEA-00-codex-r1-adjudication.md:31` 也承认没有该基线。AD-002 当前工作树与 HEAD blob 的行尾口径分别为 CRLF 与 LF；此前仅验证去横幅并归一行尾后正文相同。
- **反例与影响**：读者只读 AD-003 §2 会得到“原始字节已证明保留”的结论；读 §7 又得到无法证明的相反结论。逻辑正文相同不能证明变更前工作树的原始字节相同。这里的 P0 针对权威文档中**仍然误述历史证据**，不是断言已经证实历史正文被篡改。
- **建议**：对所有 AD-002 字节保留陈述逐处统一为已证实的口径：文件已追加横幅、去横幅并归一行尾后与 HEAD 正文一致、变更前工作树字节未固定。若要声称原字节一致，先提供并核验变更前同口径 hash；不改写冻结历史证据。
- **状态**：open，交 DSH 修订。

### R2-02 — P1：检查器的“显式断言面”仍可由同一行正文或注释满足

- **事实**：`tools/governance/check.ps1:277-306` 通过 `.Contains($Marker)` 找行，再通过 `.Contains($Expected)` 判断；不要求标记出现在独立、唯一、非注释字段，不比较字段值。AGENTS 行只检查包含 `ReferencedSource` 与 AD-003 文件名；INDEX 的 AD-003/ADJ-001 指针仍是全文 `-like` 子串。`doc/00_INDEX.md:57-59` 和 DSH 处置记录 `:28,63` 将检查范围描述为受控断言面，正文不扫描。
- **可复现反例**：本轮从实际脚本**原样抽取** `Assert-ArchitectureSurface`，只在内存中替换 `Get-Content`/`Test-Path` 供其读取合成行，未改被审文件。`<!-- Architecture sentinel: `Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource` -->` 返回 0 错；`Architecture sentinel: React + Tauri (history: Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource)` 也返回 0 错。正确字段 0 错、只有错误字段 1 错。另按脚本原条件求值：INDEX 只有 `History: AD-003_REFERENCED_SOURCE_ARCHITECTURE.md ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` 时双指针条件为真；AGENTS 产品边界声称 React/Tauri，同一行仅以历史说明包含 `ReferencedSource` 和 AD-003 文件名时也通过两个 `.Contains`。
- **影响**：此前“全文无关提及”绕过只被缩小到含 Marker 的行；注释、历史或错误当前值旁的旧文字仍能冒充当前断言。断言面正确而自由正文陈旧的已披露限制可接受为审查边界，但上述反例发生在**脚本声称正在验证的断言面和指针条件内部**，不是要求重新扫描全部自由正文。`doc/reviews/FEA-00-dsh-r2-technical-recheck.md:160` 的“断言面内无误报”也不能由五个单函数样本推广。
- **建议**：定义并精确解析唯一、非注释、带状态的字段及其完整值；对 INDEX 检查有效的当前权威 Markdown 链接及目标，而不是任意提及；AGENTS 的当前技术栈与链接同样应限定到真实字段。保留历史说明并避免全文扫面；用实际 checker 和临时隔离副本覆盖上述同一行、HTML 注释、错误值+旧值、无权威链接、重复字段、合法历史及正确值正例。不得以本次规则级 mock 冒充完整端到端测试。
- **状态**：open。

### R2-03 — P1：检查器的事前核验与本轮残余覆盖尚不足以关闭 R-04

- **事实**：`doc/reviews/FEA-00-codex-r1-adjudication.md:57,83-89` 披露第一次 checker 扩展在书面定义受影响全集前落地，随后补基线矩阵并撤销正则。直接引用的 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/checker-change-baseline-matrix.md` §1 同一行既写“变更后 14 项”又说原 13 项新增 2 项“共 15 项”；本次对脚本数组实际计数为 HEAD **12** 项、r2 **14** 项，当前运行 scope 15 另含所选 Task，不应混同为 `$staticFiles` 数量。矩阵 §2 B3 仅写“见交付报告（期望 PASS）”；§3 的五例只抽取 `Assert-ArchitectureSurface`，不测试 AGENTS 条件、两个 INDEX 子串条件或完整脚本。`doc/09_COLLABORATION.md:163-177` 要求影响既有 PASS/FAIL 的修改在实施授权生效前有受影响全集、代表性及边界样本与基线错误矩阵。
- **时序证据**：本机 DSH 会话 `session-86b838c7-6d6f-417b-9f36-3fc5f4235d1b` 中，r2 checker 的 `edit` 调用为事件 `seq=986/991/1071`，矩阵文件的 `write` 调用为 `seq=1104`。这证明矩阵文件在这些编辑之后写入；**不单凭此断言此前不可能存在其他未发现的事前草稿**。处置记录明确披露的是第一次扩展的顺序偏差，尚未提供可固定的 r2 事前全集证据。R2-02 还给出了五例未覆盖的反例。
- **影响**：承认并撤回旧正则是有效披露，但事后补表及 5/5 单函数样本不能自动证明新规则对受影响全集判别正确，也不能消除第一次修改的过程偏差。不能把 r1/r2 两次改变已有判定的检查器称为已完成 §4.4 的全部前置验证。
- **建议**：由 DSH 固定并交叉核对变更前/后真实静态文件集合、两版完整脚本的基线结果与既有判定变化；修正 13/14/15 口径，补可复验的事前证据或明确登记无法追溯与需 DSH 处置的程序偏差。对新断言面、链接和冲突样本完成真实脚本隔离回归，再决定是否可作为治理门禁；不能把事后证据改写成事前证据。
- **状态**：open。

### R2-04 — P2：ADJ-001 的四层表已改正，但 AD-003 仍保留相反的产品面陈述

- **事实**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:98-107` 现在区分 Core 命令、服务层、Host 和 V2 UI，并指出 V2 删除/恢复待接线；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:119` 仍说“现有产品面只有不可逆硬删与回收站列表”，同一行又说 V2 删除/回收站 `NOT_WIRED`。`AD-003:139` 称 R-05 已引用 ADJ 四层现状表，但 `:119` 没有该引用且旧句未更正。
- **反例与影响**：`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs:105-107,793-796,1214-1224` 的删除、回收站、恢复和永久删除入口均为能力待接入；`src/application/maintenance/trash.py:119,188`、`src/application/library/service.py:97-100` 存在服务层方法。把 Core 命令或旧产品面笼统称为当前 V2 产品能力，会误导后续拆任务与验收；上述为静态核验，不宣称已做运行测试。
- **建议**：AD-003 直接采用与 ADJ 一致的四层表或准确引用该表，明确 Core 已有硬删/列表与 V2 不可达的区别，同时保留服务层已存在的事实和 `NOT_RUN`。
- **状态**：open。

## 对 r1 逐项复核

| r1 项 | r2 结果与边界 |
|---|---|
| R-01 | **文本已针对原 P0 修订**。`ADJ-001:28,68` 和 `AD-003:97-100` 明确安全可拆分的共享引用不因其存在而阻断；不一致、不可安全拆分或未列明目标外引用 fail-closed，与 `M2-C1:734,752,764` 的限定方向一致。外部原文件继续由独立授权流程处理。`PD-08` 的“只有……才使整批失败”位于共享引用条款内，应在后续契约冻结时进一步明确只限定此类引用冲突，不覆盖 `BOOK_BUSY`、不存在目标等其他预检失败；算法、并发与运行时回归仍为 **NOT_RUN**。本项不因文本修订而宣称功能已实现。 |
| R-02 | **文本已修订**。`ADJ-001:26,59-62,78-82` 区分单条 `book_id` 与批量有序三字段，明确单条拒收批量字段、全库防护仅批量，并将 digest 字段和协议版本标为提案。现行 M2-C1 `:684-695,723` 的单条 closed shape 目前没有 digest；新字段必须经版本化契约冻结，不能宣称现行协议已经接受。 |
| R-03 | **链接已逐条解析**：ADJ-001 全部 10 个本地 Markdown 目标均存在，其中 r1 的 5 个头部断链全部修复；AD-003 16、INDEX 44、DSH 技术复核 4 个本地目标也均存在。只核验路径存在，不证明链接目标语义及锚点均正确。ADJ-001 已纳入 `check.ps1:169-175`。 |
| R-04 | 正则撤销、范围收窄和其自由正文不扫描限制已披露；**原绕过问题未完全关闭**，见 R2-02/R2-03。 |
| R-05 | ADJ 的四层表与所核对静态证据基本一致；AD-003 仍有旧产品面陈述，见 R2-04。 |
| R-06 | 已按证据更正：`doc/reviews/FEA-00-dsh-r2-technical-recheck.md:154-163` 承认 FEA-04b 依赖已声明，四页设计和 Gate 尚未完成。本次核验原版 r2 Review 的 hash `8974c94ddb7490554919632aaa27f85913f568f95d4b4fd30f2ef09556181e93` 能由当前文件前 151 行原始字节复现；更正为追加，未改原记录前缀。 |
| R-07 | §7 改为三口径是进展，但 §2 仍误述原字节，见 R2-01。 |

## 授权、写域与过程

**事实**：本次只读核验 DSH 原始会话 `session-86b838c7-6d6f-417b-9f36-3fc5f4235d1b` 的事件 `seq=538`：`user/message`、`source.kind=user`，消息 ID `e86dc466-751f-48b3-9053-67dc6584d3ca`，消息文本 UTF-8 SHA-256 `08ec092bd23a3609a75473d5c0ee20572a477262e95692bd82a1efb27d85acd2`。该用户消息确实包含处置记录 `§2:37-40` 引文，授权 DSH 修改正式记录和裁定所必需的权威文档及治理指针，同时要求先列范围、保留他人未提交内容、不改生产代码、不释放实现 Task、不 push。尽管相同文字最初出现在 Codex 提供的可转发提示词中，该 DSH 原始用户事件证明用户随后确实提交了它；不能因为提示词出自 Codex 就否定此次授权。

同一会话 `seq=608` 的 DSH 可见文本在 `seq=609` 首次写入前列出八项文件范围，与处置记录 `:42-53` 相符。`seq=856` 可见用户后来向 DSH 提供 Codex r1 报告 hash。以此证据可支持处置记录所引用的用户授权及首次动手前列明范围；不能仅凭这些事件证明每个更早未提交字节的原作者，也不能把 reviewer 指出的问题自动视作已获得实现授权。§4.4 的 checker 前置核验仍有 R2-03。

## Verification 与残余风险

| 检查 | 实际结果 / 限制 |
|---|---|
| 目标指纹、分支与 HEAD | `Get-FileHash` / `git rev-parse`：六个指定 hash 和 `main@1180cdba…` 均匹配；初始 `git status` 保留既有 dirty/untracked。 |
| 治理检查器 | `pwsh -NoProfile -File tools/governance/check.ps1`：`EXIT=0`，`PASS (2 warnings)`，scope 15；警告为 7 个非终态 Task 和 `REBASELINE_PLAN` 达到预算 80%。PASS 不覆盖 R2-02 的同一行反例，也不证明语义正确。 |
| 链接 | Python 对指定文档逐行提取相对 Markdown 目标并逐个解析；ADJ 10/10 存在，其他数量见 R-03 行。未核查页面内锚点。 |
| 检查器反例 | 使用实际脚本中的函数体在 PowerShell 内存中注入受控行；`comment_only=0 errors`、`wrong_value_with_historical_expected=0`、`correct_field=0`、`wrong_field=1`；INDEX 历史文字和错误 AGENTS 边界两条件均为 `True`。未替换仓库文件，未运行完整 checker 隔离负例。 |
| 原始记录 | 上述 DSH 用户授权、事前列范围、checker 编辑与矩阵写入顺序为只读解析会话事件；会话文件可能继续增长，消息文本和序号比整个会话文件的变动 hash 更适合定位本次证据。 |
| 并发工作区变化 | 初始 `git status` 未显示 `doc/templates/REVIEW.md` 修改，结束检查时该文件显示 dirty；本 Review 未编辑该文件，其变动来源与授权不由本报告推断，保持原样。六个固定被审对象的复核前后 hash 均未变化；请 DSH 协调该并发变动。 |
| 其他 | 所有功能、真实删除、迁移、备份、并发与 GUI 测试 **NOT_RUN**；未运行 DSH 的 fixture 脚本（其会递归删除固定 TEMP 子目录），仅只读检查其源码和既有日志。用户仅允许写本 Review，未额外保存运行日志/判别力 artefact；按 `doc/templates/REVIEW.md:49-53` 上述即时输出为审查观察，不能冒充已入库运行时测试证据。 |

**Architecture**：R2-01 为用户要求的历史证据 P0，R2-02 为检查器判别 P1，R2-03 为过程与验证 P1，R2-04 为现状表述 P2。**Verification**：治理脚本执行与只读规则反例已观察；隔离端到端回归、功能实现和数据迁移均未验证，不予批准。

## 交回 DSH

请 DSH 先处置 R2-01 与 R2-02/R2-03，再处理 R2-04；逐项给事实、修订或反证，保留历史证据，并将新文件 hash 与原始过程证据固定后交未参与修订的 Reviewer 复审。继续维持现有实现 Gate 和任务状态；本报告不释放或激活任何实现 Task，不 push。
