---
document_id: FEA-00-codex-r4
kind: independent_review
reviewer: Codex
reviewer_kind: agent
reviewer_source: "/root（当前 r4 Codex 会话；运行环境未提供独立 session ID）"
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_head: 504797ba71766f07d452cc6ddc276e01e5c2e888
reviewed_state: "main；HEAD 为 504797ba。check.ps1 与 test_architecture_assertions.py 有未提交修改；两份 r2 报告及 handoff、r3 Review 和两份 Fluent 设计文档未跟踪。按该工作区及只读可访问的仓外证据字节复审。"
decision: changes_requested
---

# FEA-00 r2 修订与 r3 遗留问题独立复审（r4）

## 结论

**`changes_requested`：1 项 P1、1 项 P2。**

r2 的 AD-002 历史字节表述已修正；AD-003 的四层产品现状及共享引用限定也与相应文档和静态代码位置相符。交接列出的六份 r2 日志哈希均匹配。

当前未提交的检查器改动从代码上处理了 r3 指出的同一行 code span、图片语法和 HTML `<pre>/<code>` 伪断言；仓外作者运行日志记录了 12 个测试方法通过。但检查器逐行处理行内代码，仍能接受跨行 Markdown code span 中的伪链接或哨兵字段，故 **R3-01 未实质关闭**。本会话无法在只读文件系统中创建并清理隔离副本，不能独立执行用户要求的真实夹具回归；没有把作者日志当作独立验证。

本次只读，未修改、创建或删除任何文件，也未改变 Task 状态。审查由 DSH 派发；本报告不代替 DSH Appointment 登记、历史程序偏差 adjudication 或集成验证。

## 固定指纹

| 对象 | R2 Review / r2 handoff 固定值 | 当前工作区 SHA-256 | 核对 |
|---|---|---|---|
| `AGENTS.md` | R2 Review 记录的当时值：`678bda95e6edace4cb9311ee1eeb825fd66974d372da0e50b866530e125acea0` | `f4bff707da3587450182ba1618794c4e44f1da844ce1dbefd676ff6b32e34bfb` | 当前值不同；r2 handoff 未固定此文件 |
| `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` | handoff：`00e3025bf654edcb3a2e44ab4175992241bd850c710439a9d879ad353463d0ef` | `00e3025bf654edcb3a2e44ab4175992241bd850c710439a9d879ad353463d0ef` | 匹配 |
| `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | R2 Review：`17a89d15efc900299f1ddbc8599c401125e6596cb0d7c3a1beab24557f09da14`；handoff：`0940a41bb0f2c14f77a50e66d34d983c83b40e0375230c1e027e98de75bcce15` | `0940a41bb0f2c14f77a50e66d34d983c83b40e0375230c1e027e98de75bcce15` | 与后续修订快照匹配 |
| `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | R2 Review：`4ff0a3d25e5dc68de8b6ba16ff56ac86600181e502c8282aae16091e1a65faba`；handoff：`9d8c9548dd921f5901464c63a8be63d2fb579e2aa2980b07dd34f29947f0662c` | `9d8c9548dd921f5901464c63a8be63d2fb579e2aa2980b07dd34f29947f0662c` | 与后续修订快照匹配 |
| `tools/governance/check.ps1` | R2 Review：`77be514d3693672637100eefdfe15b4d9edfe199d64300ae588f361d43bee76d`；handoff/HEAD：`13e08555e4d7f107623f1daaea325bb8c8f776fb88e75b2ec9b87e2e25bde5f5` | `04d9373e4e9f4700eb35d12bcef75440de24042973c611bf2b2a5eefc62faf3e` | 当前字节不同于 handoff；handoff 值匹配 HEAD blob |
| `tools/governance/tests/test_architecture_assertions.py` | handoff/HEAD：`4d639ba7bc15327ede458709ccb5810987749303f85cc622742b7a9187a63601` | `b4c26ba05c38bb7c1dd2603ea890411a10f6eafa03613020b8104a2f7c399d48` | 当前字节不同于 handoff；handoff 值匹配 HEAD blob |
| `doc/reviews/FEA-00-codex-r2.md` | handoff：`632a2a63e8d6e81748db2a7aae723c7e2c5f168495d1cfda3c1e322c0c22d9a9` | `632a2a63e8d6e81748db2a7aae723c7e2c5f168495d1cfda3c1e322c0c22d9a9` | 匹配 |
| `doc/handoffs/FEA-00-codex-r2-remediation.md` | handoff 未自 pin | `dcd57adeee1fcf0d8c8d900d48727bb89d8836562666f11e143c146768ef021b` | 当前值 |
| `doc/reviews/FEA-00-codex-r3.md` | — | `e82b06eb83a64db4724587c3478f26fbebfadba4bc41205239f23212959aed92` | 当前值 |

R2 Review 固定的 `doc/00_INDEX.md`、r1 adjudication 和 r2 technical recheck 当前哈希仍分别为 `0dc43d2980666f13c32391e193f4b5450294a9e2132475b83d4ba2f05a46e306`、`ea2171de026e2399445336c129e230c1d17ecd7131869b1e98becf95ce5e728d`、`d0bf89ff045e3c35ff9bf19d16a632a2c6dba78d51b4ae7062610ed366919eb3`。

r2 handoff 固定的六份仓外证据文件均与实读字节匹配：

| 证据 | handoff / 当前 SHA-256 |
|---|---|
| `pre-change-scope.txt` | `6f0ee472732e2ff7859b77079672707784f45c0e4e3ef2bc2afcc23b0774c58d` |
| `baseline-regression.log` | `51712bf0152548daa0723923d54440a410595cafed15444f4b598a87c9887500` |
| `head-regression.log` | `3df163f0d21bb23840f126a8b6c24c3e260c976b01c000bd2e1a0f0411446597` |
| `final-regression.log` | `ad7df8b0f7fa6d09d9e7d74108de6af1022aab331382db32c5b42ec0826052a6` |
| `existing-ac-gate.log` | `fdbc5db912aecc1d04610e01d22c989aee6cee98d90a69159be6c988c8cde11a` |
| `governance-final.log` | `73f0a77c0ff8b29f6932473dbb1c8654aef15ff8f759d4ddfa9f6a3f04bcd244` |

## Findings

### P1 — 跨行行内代码仍可冒充 AGENTS 权威链接，R3-01 未完全关闭

**位置：** [check.ps1](/G:/CODEX/New%20Manga/tools/governance/check.ps1:279)、[check.ps1](/G:/CODEX/New%20Manga/tools/governance/check.ps1:352)、[check.ps1](/G:/CODEX/New%20Manga/tools/governance/check.ps1:418)、[test_architecture_assertions.py](/G:/CODEX/New%20Manga/tools/governance/tests/test_architecture_assertions.py:144)。

**触发与影响：** 在 AGENTS 产品边界段落前插入一行单反引号，保持与边界句属于同一段落；在该句的 AD-003 链接后、句号前补对应反引号。CommonMark 允许 code span 跨行，并将其中的换行转为空格；此时链接处于代码 span，不能作为导航链接。[CommonMark §6.1](https://spec.commonmark.org/spec/#code-spans)

当前 `Get-AuthorityLines` 按物理行迭代，`Hide-InlineCode` 与 `Hide-NonLinkContexts` 也各自只处理当前行；边界检查再从单行提取首句。因此上一行未闭合的反引号状态不会传递到链接所在行，行尾匹配反引号也不会遮掉它之前的链接。**按代码路径静态推演，真实 checker 会将该伪链接接受，预计 `EXIT=0`。**同一行级边界也可能让跨行 code span 内的 AD-003 sentinel 行被计为有效字段。

**复现状态：**上述触发条件和结果是静态推演，r4 未实际执行，不能冒称真实夹具 `EXIT`。现有测试覆盖同一行 code span、图片前缀和 HTML 代码块，但未覆盖跨行 code span。建议在可写的隔离环境中，用完整 checker 加入该跨行负例，并对 AGENTS 链接及 AD-003 sentinel 分别断言拒绝；修复需跨行维护代码 span 状态或采用能正确处理该受控语境的 Markdown 解析方式。

### P2 — r2 handoff 的未提交状态自述已过期

[handoff 第 15 行](/G:/CODEX/New%20Manga/doc/handoffs/FEA-00-codex-r2-remediation.md:15)写“所有修改目前仍在 `main` 工作树，未提交”。当前 `HEAD=504797ba…` 已包含 r2 后续修订文档；handoff 的 AD-002、AD-003、ADJ-001 固定哈希现与当前字节一致。`delivery_head: null` 也是交付时状态，不代表当前 HEAD。

r3 Review 第 22 行已将其说明为修订时记录；这不使固定快照本身失效，但单独阅读 r2 handoff 容易误读为当前状态。保留历史字节，建议由后续状态记录标明其截至时点和当前 HEAD。

## 逐项复核

- **R2-01 / P0：** 当前 AD-003 §2 和 AD-002 状态横幅均明确区分文件变更、正文相同与“变更前工作树字节无基线”，没有把逻辑正文相同写成原始字节证明。我在内存中移除 AD-002 顶部新增横幅并统一为 LF 后，与 `1180cdba…` blob 比较，相等。该比较仍不能证明更早工作树的原始字节；handoff 的限定正确。此项的文档误述已修正。

- **R2-02 / P1：** handoff 固定的 checker 能校验唯一、完整值字段及当前指针；当前未提交改动又加入同一行 code span、图片、HTML 属性和 `<pre>/<code>` 处理，测试也添加了对应同一行场景。作者侧 R3 修订日志记录这些测试方法通过，但跨行 code span 漏口仍未覆盖，故本项只能部分关闭，见 P1 finding。

- **R2-03 / P1：** r2 handoff 声称的六份日志哈希均匹配；日志内容与所述基线结果一致：旧 checker 基线 5 个测试方法有 6 个失败子场景，HEAD checker 同组有 8 个失败子场景，最终 8 个方法通过；AC gate 日志显示 12 个样例符合预期，治理日志为 `EXIT=0`。r3 Review 引用的修订者轨迹中，pre-change-scope、两版基线执行均先于首次 patch；事件行、UTC、call ID 与 `payload.input` 哈希均可对应。另一方面，r1 adjudication 第 57 行披露的首次修改顺序偏差仍然存在；基线矩阵第 13 行把 `$staticFiles` 写为 13→14、又称新增两项共 15，计数口径有矛盾。r2 后续 handoff 的 12→14 静态文件、scope 15（另含所选 Task）口径与其 pre-change-scope 文件相符。**历史偏差及其处置仍交 DSH adjudication；本报告不裁定其是否可接受，也不把后补证据写成首次修改前证据。**

- **R2-04 / P2 与共享引用残余：** 当前 AD-003 §4 与 ADJ-001 §7 的四层事实相符：Core 有硬删/回收站列表命令，服务层有书籍及页级软删/恢复方法，Host/V2 未接线，UI 入口显示待接入，运行行为仍为 `NOT_RUN`。所引用代码位置可找到。AD-003 §3.7 与 ADJ-001 PD-08 将 fail-closed 限定为共享引用冲突，其他预检失败仍按 M2-C1；未将文字修订表述为算法或真实删除验收。此项静态陈述成立。

## 验证命令与实际 EXIT

环境：`G:\CODEX\New Manga`，Windows PowerShell `7.6.8`、Python `3.14.6`，`main@504797ba71766f07d452cc6ddc276e01e5c2e888`。

| 命令/场景 | 结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | **实际 `EXIT=0`**；`PASS (2 warnings)`，scope 15，无历史目录扫描。两条 warning 为 7 个非终态 Task，以及 `REBASELINE_PLAN` 达预算 80%。这仅检查当前文档状态，不证明架构语义获批。 |
| `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v` | **r4 未运行。**测试 `setUpClass` 会创建 workspace 临时目录、复制文件，测试会修改夹具；本执行环境为只读，不能创建后清理所需的隔离副本。 |
| 指定三项负例：同一行 code span、`!` 图片语法、独立 `<pre>` 包裹 sentinel | **r4 独立实际 EXIT：NOT_RUN。**当前测试源码包含这些场景；R3 修订目录的作者侧 `final-regression.log`（SHA-256 `47037f51d13eecad3bf5293c27e0dc2741e6516cda2239dbce36c2f52cfa604c`）记录完整 suite 12 个测试方法及子场景通过、`EXIT=0`。这不是本会话的独立执行，也不包含本次发现的跨行负例。 |
| 正例：当前权威文件、历史 inline code 前置真实链接、代码示例中的 `<pre>`、合法历史说明 | 当前未变更文档由治理命令实际通过；作者侧 12 方法日志记录相关正例通过。**合成隔离正例的 r4 实际 EXIT：NOT_RUN。** |
| `python -B tools/governance/tests/test_ac_gate.py` | **NOT_RUN**；本轮主题是架构断言回归，不需要该测试；它同样会创建临时夹具。 |
| DSH FEA fixture | 未运行。 |

**覆盖边界与残余风险：**当前 checker 的 PASS 只覆盖其声明的 15 份输入；未扫描全部自由正文。r4 未在隔离副本运行真实负例，因此不能确认本次代码改动对各场景的实测 EXIT。作者侧日志哈希可复核，但不能替代独立执行。用户源文件、删除行为、迁移、并发、GUI 和产品运行均不在本次验证范围。

## 建议下一步

建议 DSH 先处置本报告 P1：确定修订范围，在可写的隔离环境对跨行 code span 负例及现有三项负例运行完整 checker，再安排新的独立上下文复审。R2-03 的历史程序偏差另由 DSH 裁定；本报告不激活或释放任何实现 Task。