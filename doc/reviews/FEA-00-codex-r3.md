---
document_id: FEA-00-codex-r3
kind: independent_review
reviewer: Codex
reviewer_kind: subagent
reviewer_source: /root/fea_r3_review
author: Codex remediation session; DSH original documents
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_head: 504797ba71766f07d452cc6ddc276e01e5c2e888
reviewed_branch: main
decision: changes_requested
---

# FEA-00 r2 修订复审（r3）

## 结论与边界

**changes_requested：0 项 P0、1 项 P1。** R2-01 历史字节误述、R2-04 四层现状和共享引用残余文字已经修正；本次修订的事前定义与完整 checker 基线有原始轨迹支持。但是 R2-02 尚未完全关闭：AGENTS 的“真实 Markdown 链接”仍能被行内代码或图片语法冒充，HTML 代码块里的哨兵也被当成权威字段（R3-01）。8 项既有架构测试通过并不足以排除这些反例。

审查者 canonical agent ID 为 `/root/fea_r3_review`，由 `/root` 派发的独立上下文 Codex 子 agent；未参与实现或返修。本轮用户授权新上下文复审、只写本文。DSH 的 Appointment 登记、findings 处置、历史程序偏差裁定和集成验证仍由 DSH 负责，本文不代替这些职责。

开始与结束前核对均为 `main@504797ba71766f07d452cc6ddc276e01e5c2e888`，Git common dir `.git`。当前修订已在该 HEAD 内；交接所写“仍未提交工作树”和其 `delivery_head: null` 是修订时记录，不是当前状态。被审哈希全部匹配，无漂移。开始时仅四份既有 untracked 文件（两份 Fluent 设计、r2 Review、修订交接）；它们均保留。本文创建前确认不存在。未修改生产代码、原报告、交接、Task、他人内容；不迁移、不释放 Task、不 push。

## Findings

### R3-01 — P1：真实链接与代码语境仍可冒充权威断言

**位置**：`tools/governance/check.ps1:279-305`、`:334-336`；相关回归 `tools/governance/tests/test_architecture_assertions.py:129-132`。

**事实**：`Get-AuthorityLines` 仅剔除 HTML 注释和 fenced code；AGENTS 首句随后用未排除 code span、未排除图片前缀的正则寻找 `[AD-003...](...)`。因此它并未验证链接确为正文可导航的 Markdown 链接。HTML `<pre>` 代码块中的字段也会进入 `Assert-ArchitectureSurface`。

**完整 checker 隔离复现**：复用现有测试的 `ArchitectureAssertions.setUpClass()` 创建随机隔离目录，逐次保存原字节，仅改夹具并断言 `before != after`，运行该夹具的真实 `check.ps1`，finally 恢复并由 `tearDownClass()` 清理。没有抽取函数、mock 或改仓库输入。

| 夹具变化 | 期望 | 实际 |
|---|---|---|
| AGENTS 首句唯一 AD-003 链接整体包入一对反引号，成为 code span | 缺少真实链接，FAIL | `MUTATED=True EXIT=0`，`PASS (2 warnings)` |
| 同一链接前增加 `!`，成为图片语法 | 缺少导航链接，FAIL | `MUTATED=True EXIT=0`，`PASS (2 warnings)` |
| AD-003 唯一 sentinel 行外包独立 `<pre>` / `</pre>` 行 | 代码示例不能声明权威字段，FAIL | `MUTATED=True EXIT=0`，`PASS (2 warnings)` |

第一、二例对实际 AGENTS 使用以下替换，避免依赖中文链接标题：

```python
pattern = r'(\[AD-003[^\]]*\]\(doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE\.md\))'
after = re.sub(pattern, r'`\1`', before, count=1)  # 第二例改为 r'!\1'
assert before != after
```

第三例将 `Architecture sentinel: ` 后的当前完整哨兵原行替换为 `<pre>\n` + 原行 + `\n</pre>`。三个场景各自运行完整 checker，scope 均 15。两条警告均为既有非终态 Task 数和 Plan 80% 预算。

**影响**：作者要求的“首句真实 ADR 链接”和“非代码有效断言”仍可被示例文字冒充。这不是要求扫描自由历史正文，而是当前受控字段/指针自己的语法语境未验证；r2 同类 P1 不能关闭。现有测试仅将链接替换成纯文字，没有覆盖“看起来像链接但实际是代码/图片”的边界。

**建议**：在受控格式范围内验证有效 Markdown 链接语境，拒绝 code span/图片/HTML 代码块中的伪字段；保留自由历史正文不扫描的边界。修订前按 §4.4 固定新增边界的完整 checker 基线，补真实脚本正负回归。Reviewer 本轮不实施修复。

## r2 逐项处置复核

| 原项 | 本轮结果 |
|---|---|
| R2-01 / P0 | **fixed（文档口径）**。AD-003:28 与 AD-002 顶部横幅明确无变更前工作树原字节基线；AD-003:146 区分文件变更、逻辑正文保留和未知原字节。实际去除横幅、CRLF→LF 后，AD-002 与 `1180cdba79e4d610521dde13f0c8a458220f9d90` blob 完全相等，blob SHA-256 `853c95113eca398186b883ebf1e914da3dba349fadea1b013d53e56b71c063ee`。该结论不是原工作树字节证明；当前 HEAD 已含横幅，历史描述中的 HEAD 应理解为当时基线，精确基线以本行固定。 |
| R2-02 / P1 | **partially_fixed / open**。原 HTML 注释、同一行错误值加历史正确值、重复字段、fenced code、HISTORICAL 指针等负例现在拒绝；实际架构字段按完整值校验。仍有 R3-01。 |
| R2-03 / P1 | **本次修订的先核验顺序有证据；历史程序问题 pending DSH adjudication**。实际静态集合旧基线 12、当前 14；选定 Task 再加 1，分别 scope 13/15。本次事前范围、r2 六个失败子场景、旧 HEAD 八个失败子场景均有完整 checker 日志；原始轨迹见下。旧 DSH 矩阵的 13/14/15 混写及 r1 先改后列全集仍保留，不能拿新证据证明旧过程合规；旧 r2 事前全集仍无法追溯。本次计划也没有覆盖 R3-01。 |
| R2-04 / P2 | **fixed（静态事实）**。AD-003:119 已采用 Core/服务层/Host/V2 的区分并链接 ADJ §7。核对 core_service.py:298,4403,4559；trash.py:119,188；library/service.py:97-100；IHostController 和 LibraryViewModel.cs:105-107,791-796,1214-1224。Core 有硬删/列表，服务层有软删/页恢复，Host 缺相应能力，V2 入口只通知待接入。未宣称运行验收。 |
| 共享引用残余 | **fixed（文字限定）**。ADJ PD-08:68、AD-003 §3.7:100 将“只有”限定在共享引用冲突，不排除 `BOOK_BUSY`、不存在目标等既有预检失败；可安全拆分的引用保留共享原文件，不因共享本身阻断。与 M2-C1:734,752,764 对齐。算法、并发、真实删除均 NOT_RUN。 |
| 历史记录及冻结契约 | M2-C1 当前工作树 SHA-256 仍为 `dfcd47cabe9831b270fb0a6f985e50ea9e5a34b165f2c776a8f1e34c777bae72`；DSH r2 技术复核前 151 行原始字节 SHA-256 仍为 `8974c94ddb7490554919632aaa27f85913f568f95d4b4fd30f2ef09556181e93`。r2 Review hash 匹配。本轮没有全历史文件逐字节基线，不能推广为全部日志/manifest/原工作树字节都已证明未变；`git diff 1180cdba… HEAD -- src apps doc/tasks doc/contracts` 仅列新增 ADJ-001，未列生产源码和旧冻结契约变更。 |

AD-003 的 17 个、ADJ-001 的 10 个本地 Markdown 目标均存在；只验证目标路径，不涵盖锚点语义或产品能力。

## 事前过程的独立证据

仅定点读取修订者原始轨迹 `C:/Users/49745/.codex/sessions/2026/10/31/rollout-2026-10-31T17-24-25-01a19146-4ae6-7093-85ba-6fe125429794.jsonl`，不把文件时间戳或交接自述当作唯一顺序证据。该轨迹可能继续增长，以下以行号、UTC 时间、call_id 和该事件 `payload.input` UTF-8 SHA-256 定位：

| 行号 / UTC | 行为 / call_id | input SHA-256 |
|---|---|---|
| 1977 / 12:45:29.081 | 写 pre-change-scope；`call_dc939b09a33f4dc394e5e1e516f297fe` | `57c8db76d606e4a6ef239445e48d40ac47c73df30308f403b826b00d9f31f584` |
| 1984 / 12:45:32.867 | 实跑 r2 baseline；`call_072ae5d89b674bf2a62c4f3cc0adce9a` | `30fa2ffb691a947318a00d7ffca976991bcac0b2e223611491a03a8aed8aa2c8` |
| 2006 / 12:45:55.471 | 固定旧 HEAD checker 并实跑；`call_6d39c1962e934342987157bec1285131` | `ed2ef0f56b44fab4b9943c38d5a93f1a6d4b326d95969371472e5d288653a3de` |
| 2019 / 12:46:32.392 | 首次 patch checker；`call_9152001d05394f44933c57f36a723e25` | `5953730a92270e5e97e0123159075a43c41533abcea70c2c18c12b118b439dcb` |
| 2060 / 12:47:15.716 | 后补未闭合 HTML 注释边界；`call_ec9f915c1a704778be3db44765d69451` | `e9107fcedd40c652c5e8f7927b58c90f80f7aefddfc38429705b39b86cf3fa73` |

固定日志显示 baseline 5 个测试方法、6 个失败子场景，旧 HEAD 同组 8 个失败子场景；最终 8 个方法全部通过。方法数与子场景数不是同一口径。新增 3 个方法及未闭合注释等后补场景没有全部事前基线，交接已经披露，不能把最终全量测试倒写成事前完成。

**仍交 DSH 裁定**：保留原 DSH 第一次变更先实施后列全集、r2 事前证据不能追溯、原矩阵计数及“期望 PASS”当基线等历史偏差；决定是否接受、如何登记程序处置。历史报告不应原地改写。本轮证据只支持本轮顺序，不洗掉原 R2-03，也不等于获得实现 Task 授权。

## Verification

环境为本机 Windows、PowerShell；Python 命令均 `-B`，未生成 pycache。被审精确 HEAD 见 frontmatter。

| 命令/检查 | 实际结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT=0；scope 15；`PASS (2 warnings)`。警告：7 个非终态 Task、Plan 达预算 80%（6624 bytes / 58 lines）。 |
| `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v` | EXIT=0；`Ran 8 tests in 15.864s`，`OK`；全部方法通过，无 skip。 |
| `python -B tools/governance/tests/test_ac_gate.py` | EXIT=0；12/12 cases behaved as specified。TMP/TEMP 指向 workspace/agent-output/codex；测试随机目录由脚本清理。此脚本专判 AC gate，夹具会故意触发无 DAG 登记/仓外 commit pin 等非 AC 错误，不能称完整检查全 PASS。 |
| R3-01 完整 checker 隔离负例 | 三场景均确认输入发生变化，却各自 EXIT=0/PASS；判别失败。即席脚本只从现有 fixture 类加载并在 finally 清理。 |
| 字节/链接/集合检查 | 固定哈希匹配；AD-002 去横幅归一后正文相同；M2-C1 与历史前缀匹配；静态集合 12→14；本地目标 17/17、10/10 存在。 |
| 其他既有测试 | 只读检查 test_path_header_compat.py、test_residual_runtime_identity.py，作用于 clean_workspace 而非本次 check.ps1 架构修改，未扩跑。 |
| 产品、真实删除、并发、GUI、迁移、备份 | NOT_RUN；没有实现授权，也没有以治理测试替代产品验收。 |

本轮用户只允许新建本文，没有另存运行日志/判别力 artefact。上述输出为本轮实际审查观察，完整 checker 反例的输入和结果已记入本文；并非新 canonical 运行时验收证据。按 Review 模板证据纪律，未入库的正式产品判别力证据保持 NOT_RUN。被审交接的既有六份日志则已逐份核验 hash，不冒充本轮新产物。

**Architecture**：原文字修订可接受；真实权威字段/链接判别仍有 P1，不能批准。**Verification**：指定检查与既有回归实跑通过，但补充负例判别失败，证明关键边界仍有缺口。

## 固定 SHA-256

以下为本轮实际读取的审查对象/依据；所有交接固定对象逐项匹配。仓外证据目录前缀为 `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/`。

| 路径 | SHA-256 |
|---|---|
| `AGENTS.md` | `f4bff707da3587450182ba1618794c4e44f1da844ce1dbefd676ff6b32e34bfb` |
| `doc/STATUS.md` | `e8fe3affdabe315394a53f0d710e5ba16d480650716ea97f541977ade3de4a64` |
| `doc/REBASELINE_PLAN.md` | `b29ec44b7f724c8d74eca07c01be4dbcab9ce6d0eb89ff601be05ca296248233` |
| `doc/09_COLLABORATION.md` | `35bfcb72f418a1b4e066b9b041f298c6bded64854b9303735762250e05e8e66f` |
| `doc/templates/REVIEW.md` | `fa5827bec92979b10b82ff445f6e60514defc6f807c6bff5a8dd548b914b66b9` |
| `doc/00_INDEX.md` | `0dc43d2980666f13c32391e193f4b5450294a9e2132475b83d4ba2f05a46e306` |
| `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` | `00e3025bf654edcb3a2e44ab4175992241bd850c710439a9d879ad353463d0ef` |
| `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | `0940a41bb0f2c14f77a50e66d34d983c83b40e0375230c1e027e98de75bcce15` |
| `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | `9d8c9548dd921f5901464c63a8be63d2fb579e2aa2980b07dd34f29947f0662c` |
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `dfcd47cabe9831b270fb0a6f985e50ea9e5a34b165f2c776a8f1e34c777bae72` |
| `doc/reviews/FEA-00-codex-r2.md` | `632a2a63e8d6e81748db2a7aae723c7e2c5f168495d1cfda3c1e322c0c22d9a9` |
| `doc/handoffs/FEA-00-codex-r2-remediation.md` | `dcd57adeee1fcf0d8c8d900d48727bb89d8836562666f11e143c146768ef021b` |
| `doc/reviews/FEA-00-codex-r1-adjudication.md` | `ea2171de026e2399445336c129e230c1d17ecd7131869b1e98becf95ce5e728d` |
| `doc/reviews/FEA-00-dsh-r2-technical-recheck.md` | `d0bf89ff045e3c35ff9bf19d16a632a2c6dba78d51b4ae7062610ed366919eb3` |
| `tools/governance/check.ps1` | `13e08555e4d7f107623f1daaea325bb8c8f776fb88e75b2ec9b87e2e25bde5f5` |
| `tools/governance/tests/test_architecture_assertions.py` | `4d639ba7bc15327ede458709ccb5810987749303f85cc622742b7a9187a63601` |
| `tools/governance/tests/test_ac_gate.py` | `d9960f96e0b61a3f44a220a0d0e6071c8d22964431e4b6aa4e151879211314dc` |
| `tools/governance/tests/test_path_header_compat.py` | `36264f4268a1f777964f6247cfc4ebb9167de88dee9a209951acf4e0a58440a2` |
| `tools/governance/tests/test_residual_runtime_identity.py` | `03cd671d9ebd05b36fd67719269b19264e6c62400ec21aa2446630e41f06a7c2` |
| `src/bootstrap/core_service.py` | `196bb65fc390f2fd23a0d09e1192566f05bbf20f708b7bc606b977b9e69ab07e` |
| `src/application/maintenance/trash.py` | `2e3c431db59fc516a7a7b9015a10497449ac9215f55a8be8a2cbf80775a737c2` |
| `src/application/library/service.py` | `0ebcfe3277938935b63103c93be930fec7de2c6f6bbd71b5d09713acbd5c31c7` |
| `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` | `5ada8cfc79fdc575257bea1af66284dd2d2899315078d4aebfbda079fa2a84e0` |
| `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs` | `7ad710ce320674c5f5998ba930d6023ad9931dfffb81aa62eb9a87f489ff6b96` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/pre-change-scope.txt` | `6f0ee472732e2ff7859b77079672707784f45c0e4e3ef2bc2afcc23b0774c58d` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/baseline-regression.log` | `51712bf0152548daa0723923d54440a410595cafed15444f4b598a87c9887500` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/head-regression.log` | `3df163f0d21bb23840f126a8b6c24c3e260c976b01c000bd2e1a0f0411446597` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/final-regression.log` | `ad7df8b0f7fa6d09d9e7d74108de6af1022aab331382db32c5b42ec0826052a6` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/existing-ac-gate.log` | `fdbc5db912aecc1d04610e01d22c989aee6cee98d90a69159be6c988c8cde11a` |
| `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-00-R2-remediation/governance-final.log` | `73f0a77c0ff8b29f6932473dbb1c8654aef15ff8f759d4ddfa9f6a3f04bcd244` |
| `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/checker-change-baseline-matrix.md` | `17c2c6b6705eb51905b890ed5b586c58ad49613307b1c3237b712db62174d3fc` |

## 交回 DSH 与推荐下一步

请 DSH 处置 R3-01，指定 Codex 在另一次获授权的修订会话完成受控 Markdown 语境检查及三组真实脚本回归，然后安排独立上下文复审新的精确 head/hash；同时明确登记历史 R2-03 程序偏差的裁定。当前 Source 线 D05/G-CONTRACT 继续 blocked，REALUSE-DATA-SAFETY-6 保持 ready，本报告不改变任何 Gate 或 Task 状态。实现 Task 无需下一步操作；本轮未完成或关闭任何 Task。
