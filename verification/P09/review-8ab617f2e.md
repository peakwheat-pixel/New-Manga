---
task_id: P09
reviewer: Codex Reviewer（非作者，独立审查）
author: Codex
base_commit: d7fe920272d48eb4761347a5e18789dcbbdd05d6
reviewed_head: 87179691cbab8b97d30282c0d8d0b20d9d81122c
original_reviewed_head: 8ab617f2e996e99a4a4ddac82fe71863d4b0684e
decision: blocked
findings_disposition: R-01_closed_by_contract_alignment_R-02_fixed
---

# P09 固定实现审查

本次变更将生产图片解码改为真实 Qt decoder，增加绝对路径来源工厂，并在 PDF 写入任何 Managed Copy 前完整渲染所有页。MOBI 从生产装配及文档 importer 中移除；不新增 IPC 或缩略图。

## 最终复审结论（87179691c）

最终固定 head：`87179691cbab8b97d30282c0d8d0b20d9d81122c`；base 不变。已审查原固定 head 至该 commit 的修订差异。最终 **open findings：P0/P1/P2/P3 = 0/0/0/0**。初审 2 项 P2 均已闭合，原始证据保留在下方，不代表最终 head 仍有这些缺陷。

本节最终结论 **supersedes（取代）初审 R-01/R-02 的 open 判断及修订建议**；下方原始 findings 仅供追溯。AC 与 Verification 表统一描述最终固定 head；明确标注“初审”的证据行仍只适用于原 head。

- R-01：新增契约已改为明确规定 SQLite Page 写入异常传播，并允许完整孤儿 Original，与既有 port/实现及故障测试一致。未发现上位 AC 要求 DB 异常必须转换为 ImportReport；故按契约对齐闭合。DB 故障仍会中断批次且不给 ImportReport，这是当前声明的恢复限制，不能声称已实现逐页 DB 失败报告。
- R-02：`sorting.py:120`～`:124` 已将读取阶段重新校验的 ValueError 转为 OSError，两个 importer 均会报告 `SOURCE_READ_FAILED`。工厂阶段仍以 ValueError 拒绝非法路径。新增真实 symlink 替换测试覆盖拒绝且零副作用；作者 [日志 40](logs/40-path-replacement-race.txt) 为 9 passed / exit=0，[日志 41](logs/41-p09-full-target-tests-py312-review-fix.txt) 为全目标 91 passed / exit=0。本次独立内存复核得到 `PATH_SWAP_FIXED imported=2 failed=[('second.png', 'SOURCE_READ_FAILED')] store_calls=['first.png', 'third.png'] pending=()`：前后两个合法来源成功，中间拒绝来源未 copy/提交；不再中断批次或丢失报告。
- 历史测试冲突：作者 [日志 42](logs/42-out-of-scope-legacy-stub-test.txt) 实际执行得到 **1 failed / exit=1**，确认 `tests/core/test_stub_decoder.py:38` 要求非法字节通过，而真实 decoder 正确拒绝。`tests/core/**` 超出 P09 修改授权，该文件未改，且不在指定 91 项目标集合；作为残余风险保留，不冒记全仓通过。

**Architecture：本次实现范围内无待修发现。Verification：AC3 项目永久删除仍为 BLOCKED，完整 pytest/UI/运行时并发容量未独立复跑。** 因原 AC3 未裁决，本报告 `decision=blocked` 仅表示不能批准 Task 全 AC 关闭；不表示最终 head 存在未修实现 finding。Coordinator 可依据范围内实现审查与剩余 Gate 的明确处置决定后续集成，不能引用本报告声称 AC3 已通过。

修订差异之外没有扩大审查范围；报告完成时 HEAD 为最终固定 head，Task 仍有作者未提交修改。报告文件名按最初指定路径保留。

## 初审记录（8ab617f2e；以下 findings 已于最终复审闭合）

初审发现 **2 项 P2 实现/契约问题**；未发现 P0/P1。另有一项超出 P09 修改授权的历史测试冲突，单列为残余风险。AC3 的项目永久删除验证仍为 `BLOCKED`，本报告不把它提升为完成。

## 初审 Findings（历史记录，最终均已关闭）

### R-01 · P2 · Page 提交失败使整个导入调用外抛，违背新增失败报告契约

最终状态：`closed_by_contract_alignment`，修订 commit=`87179691cbab8b97d30282c0d8d0b20d9d81122c`。以下要求及建议引用初审契约，已由最终契约和上方复审结论取代。

- 位置：`src/application/importing/documents/service.py:203`；同一问题位于 `src/application/importing/images/service.py:112`。要求来源：`doc/contracts/P09_IMPORT_CONTRACT.md:37` 明确承诺“Copy/DB 失败返回逐文件/逐页失败”。图片侧行为在 base 已存在，P09 新契约与新增安全验收没有闭合该行为。
- 触发：第一张图片或 PDF 第一页成功，第二次 `add_page` 因 SQLite operational error（例如磁盘写入失败）抛异常。两个 importer 都只保护 copy 调用，没有保护 Page sink。
- 影响：此前已提交的完整 Page 保留，失败页可能留下允许的完整孤儿 Original；但调用者拿不到成功、失败、待处理清单，后续来源/页直接停止。本问题不表示出现“Page 有而 Original 无”，它影响失败诊断及恢复。
- 证据：本次只使用内存 store/sink 的故障探针得到 `IMAGE_DB OperationalError committed=1 store_calls=['first.png', 'second.png'] ImportReport=not returned`；PDF 同样得到 `PDF_DB OperationalError committed=1 store_calls=['a-page-0001.png', 'a-page-0002.png'] ImportReport=not returned`。新增测试 `tests/library/test_p09_managed_copy_safety.py:67` 明确断言异常外抛，因而其通过并不证明契约中的失败报告。
- 最小修订：在持久化边界用既有 application port 可表达的失败语义转换数据库失败，在 importer 中形成失败和剩余 pending，保留已成功页及完整孤儿策略；不要为捕获 SQLite 异常把 application 层直接耦合到 SQLite。若需扩大 port 修改范围，先由 Coordinator 冻结授权。补充“第二项提交失败”的报告断言，不能只检查空库。

### R-02 · P2 · 来源读取时的重新校验抛 ValueError，绕过两条 importer 的失败处理

最终状态：`fixed`，修订 commit=`87179691cbab8b97d30282c0d8d0b20d9d81122c`。以下传播行为及测试缺口仅指初审 head；最终修复及证据见上方复审结论和日志 40。

- 位置：`src/application/importing/images/sorting.py:119`（调用 `:121`，异常源为 `:101` / `:105`）；消费者为 `src/application/importing/images/service.py:73` 和 `src/application/importing/documents/service.py:85`。
- 触发：`sources_from_selection` 返回后、某一来源读取前，该文件被删除，或被替换为 symlink/junction。重新检查会正确拒绝读取，但 `_reject_reparse_path` 把检查失败转换为 `ValueError`；importer 只捕获 `OSError`。文件删除也是普通操作，不要求攻击者竞争最后一次 read 的时间窗口。
- 影响：如果前一来源已导入，它保持提交；当前来源拒绝后整个批次外抛，后续来源没有失败/pending 记录，调用者拿不到 ImportReport。拒绝检查本身没有读取链接目标，本 finding 不声称链接目标被读取或源数据被修改。
- 证据：本次内存探针令第二来源在 `_read_selected` 的 reparse 校验处抛出真实同型 `ValueError`，结果为 `PATH_SWAP ValueError committed=1 store_calls=['first.png'] ImportReport=not returned`。`tests/library/test_import_sources.py` 只覆盖工厂调用时已有的不合法路径，没有覆盖工厂返回后的来源变化。
- 最小修订：保留工厂阶段的 `ValueError` 拒绝；把读取阶段的校验失败转换为来源读取异常（例如在 `_read_selected` 边界转 `OSError`），使现有两个 importer 都能按逐文件失败处理。增加“工厂返回后删除来源”和“第一项已成功、第二项重新校验拒绝”的断言。

## 范围限制：历史生产装配测试仍要求占位 decoder

- 位置：变更点 `src/bootstrap/core_service.py:370`；受影响测试 `tests/core/test_stub_decoder.py:30`，具体失败调用 `:38`。
- 触发：执行现有 `test_production_stub_decoder_returns_valid_decoded_image`。该测试通过真实 `assemble_production_core` 取 decoder，调用 `decode(b"fake")` 并要求 width/height 均为 1。
- 影响：P09 正确接入的 QtImageDecoder 会对这组非法字节抛 `ImageDecodeError`，所以仓库现有测试仍与产品要求矛盾。作者最终 91 项集合只覆盖 `tests/import_formats`、`tests/library`、`tests/storage/test_managed_storage.py`，没有包含此测试。
- 证据：最终固定 head 的该测试仍保留上述调用；Reviewer 的无文件写入真实 Qt 解码探针输出 `ImageDecodeError: Unsupported image format`。作者 [日志 42](logs/42-out-of-scope-legacy-stub-test.txt) 已实际执行该 pytest 测试，记录 1 failed / exit=1；Reviewer 未独立复跑它。
- 范围与处置：`tests/core/**` 不在 P09 允许修改路径内；本项作为历史测试冲突及残余风险，不要求 Owner 在当前授权中修改。Coordinator 如另行授权，最小修订是把该生产装配测试改为合法图片的真实尺寸断言，并保留直接构造 `_PassthroughImageDecoder` 的测试用途；不得恢复生产占位 decoder 来迎合旧测试。当前目标测试集不包含此冲突，91 passed 不代表全仓测试通过。

## AC1–AC9 最终覆盖（87179691c）

下表区分代码/归档证据审查与 Reviewer 实际执行。没有将作者日志中的 passed 计为本次独立运行。

| AC | 本次结论 | 核对依据与限制 |
|---|---|---|
| AC1 真实尺寸/元数据 | 代码与归档证据支持；历史测试冲突保留 | `core_service.py:370` 注入 QtImageDecoder；`infrastructure/importing.py:98` 真实解码；`tests/library/test_production_adapters.py` 有 17×23 生产 Core 验证。归档日志 29 记录 1 passed。本次只独立执行非法字节拒绝探针。 |
| AC2 受控来源/逃逸 | 代码与归档证据支持；R-02 已修复 | 根/显式文件 containment、绝对路径、祖先 reparse 检查在来源创建时完成；文件夹一级展开且链接整组拒绝。读取阶段校验失败现转换为 OSError，返回 SOURCE_READ_FAILED；作者日志 40 的真实链接替换测试通过，Reviewer 内存复核确认中间拒绝项零写入且前后合法项成功。Reviewer 未独立创建 junction/symlink。 |
| AC3 源零修改 | `BLOCKED`，保持原状态 | 哈希证据 `evidence/AC3-source-hashes.json` 覆盖导入、软删、Page 永久清理、翻译/重修/重渲染；两组样本各阶段 hash 一致。现有 `LibraryService.delete_book` 是软删除，没有项目级永久删除用例，不能证明该项完整 AC。 |
| AC4 Managed Copy→Page | 不变量代码审查支持；R-01 已按契约对齐关闭 | `ManagedCopyStoreAdapter.store_original` 先 write_temp/verify_temp/publish，两个 importer 后 add_page；SQLite 用事务插入。发布失败不会触达 sink。Page 失败允许完整孤儿，不会因当前顺序生成缺失 Original 的 Page；最终契约明确 DB 异常传播，不再承诺转换为 ImportReport。 |
| AC5 Unicode | 代码与归档证据支持 | 新 safety test 覆盖中文、日文、韩文、Emoji、空格括号目录/文件，经 SQLite + Managed Copy。该测试替换 decoder，生产 decoder 另由 AC1 覆盖。 |
| AC6 重复 | 代码与归档证据支持 | SHA-256 为 Chapter 活动 Page 去重键，同批成功项更新集合；默认跳过，显式 IMPORT_AS_NEW 使用新 UUID Original；保留旧副本。PDF 去重键是渲染 PNG，符合新增契约。 |
| AC7 PDF | 文件级解码屏障代码与归档证据支持 | 全页先渲染再 copy；加密/open 失败、零页、任何页 render 失败、无有效像素均在写入前拒绝；stub 中间页损坏测试及真实 PDFium/Qt 测试覆盖。Copy/取消阶段允许保留此前完整页，符合契约，不能误当损坏 PDF 半成品。归档日志 30 为 17 passed；本次不重新生成 PDF 文件。 |
| AC8 范围 | 代码审查通过 | diff 未改冻结 IPC、Schema 或依赖；生产 assembly 不再注入 MOBI，文档 importer 仅识别 PDF；无新增缩略图。历史 `MobiDocumentRaster` 基础设施仍保留但没有本生产导入绑定，不将历史代码存在视为新增 MOBI 实现。 |
| AC9 固定 head Review/集成 | Review 已完成；集成 NOT_RUN | 本报告最终固定 87179691cbab8b97d30282c0d8d0b20d9d81122c，Reviewer 为非作者；当前范围内 open findings 为零。Coordinator 集成与集成后验证未由本 Reviewer 执行；AC3 仍 BLOCKED，不能因此关闭全部 AC。 |

## Architecture 与 Verification

Architecture：新增来源工厂位于 application importing，依赖标准库及自身 ports；Qt/PDFium 位于既有 infrastructure adapter，通过生产装配注入。React/Tauri 无新增 OS 路径/数据库入口。没有发现冻结 IPC 的语义变更；新契约明确 UI 可达性仍需后续授权，不能把本切片宣称为已完成 UI 导入。

审查负载假设：本机单用户 Windows 桌面 Core。PDF 全页缓存在内存和路径校验到 read 之间的 TOCTOU 窗口均有具名 `shortcut:`，本次没有容量证据推翻前者，也没有运行并发替换攻击证明后者。因此将它们记录为已知限制，不编造额外 P1。已关闭的 R-02 针对重新校验拒绝后的异常传播；修复没有消除最后一次检查与读取之间已声明的竞争窗口。

| 实际执行/核对 | 环境/结果 |
|---|---|
| Git root/common dir/branch/HEAD/status/worktree 只读核对 | root=`G:/CODEX/New Manga.workspace/worktrees/P09-IMPORT-CORE`；common dir=`G:/CODEX/New Manga/.git`；branch=`codex/P09-import-core`。初审为 8ab617f2e；复审与此次报告一致性修订时 HEAD 均为最终 reviewed_head。契约、sorting、路径测试及日志 40～42 已包含于最终固定 commit；Task 的作者未提交修改不在审查范围，Reviewer 未触碰它。 |
| 初审三个内存故障探针（8ab617f2e） | PowerShell；`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -B -`；exit=0（探针捕获并打印被审异常）。无 DB/Managed Storage/临时文件写入；结果作为 R-01/R-02 的初审历史保留，不能作为最终 head 的 open finding。 |
| 最终路径报告复核（87179691c） | Reviewer 同解释器纯内存探针 exit=0；2 imported、second.png 为 SOURCE_READ_FAILED，store 仅收到 first.png/third.png。作者真实链接替换测试见日志 40，9 passed / exit=0；Reviewer 未独立运行该 pytest。 |
| 真实 Qt 非法字节探针 | 同解释器，`QtImageDecoder().decode(b'fake')`；捕获 `ImageDecodeError: Unsupported image format`；exit=0。 |
| 初审 `git diff --check d7fe920 8ab617f -- src/application/importing src/bootstrap tests` | PASS，exit=0；这条检查没有重新运行于最终 head。 |
| 初审整个 base→8ab617f `git diff --check` | FAIL：保留的原始失败日志内有尾随空格。它们是原始运行 artefact，未把此噪声列为代码 finding，也未改写日志。 |
| 作者最终测试日志核对（87179691c） | [日志 41](logs/41-p09-full-target-tests-py312-review-fix.txt) 为 **91 passed / exit=0**；此前日志 38 的 90 passed 为初审历史结果，新增来源变化测试后总数为 91。29、30、35、37、40 及 README 提供场景映射。原始日志没有各次 shell/venv 头，解释器口径集中写在 README/Task；不完全符合协作协议 Q-009 的逐日志头要求。Reviewer 未独立复跑完整目标集。 |
| 授权范围外的旧 stub 测试 | 作者 [日志 42](logs/42-out-of-scope-legacy-stub-test.txt) 记录 **1 failed / exit=1**，非法 b'fake' 被真实生产 decoder 拒绝；该测试位于 tests/core，未包含于 91 项目标集合。Reviewer 核对日志与调用链，未独立复跑。 |
| 完整 pytest、真实 junction、UI/Tauri、故障断电/大 PDF | NOT_RUN；本任务禁止执行可能改写工作区的命令。没有安装依赖、创建样本、改生产/测试/Task/Handoff 或提交。 |

可复核的故障探针做法：将 store 替换为只追加显示名到 list 并返回 `managed/<name>` 的内存对象；sink 替换为 list，在第二次 `add_page` 前抛 `sqlite3.OperationalError`；image decoder 返回 `DecodedImage(1,1,'image/png')`；PDF raster 返回三页不同字节的 `RenderedDocumentPage`。路径案例中第二来源调用真实 `_read_selected(Path('G:/selected/second.png'), Path('G:/selected'))`，用 `unittest.mock.patch.object` 使 `_reject_reparse_path` 抛其现有 `ValueError`。各案例调用真实 importer 并捕获打印类型、已提交数及 store 调用清单。这些探针不模拟磁盘原子性，仅证明控制流和报告是否返回；真实存储安全判断另以实现与已存在测试核对。

## 行为保持型简化机会

- **S-01（可选，无需阻断）**：`src/application/importing/documents/service.py:210` 的 `and page_count > 0` 可删。`page_count <= 0` 已在预检设置 decode_error 并在 `:145`～`:154` 跳过文件，到达提交阶段时页数必定为正。只删除这段冗余条件，不改重复报告。
- 不建议删除 `_PassthroughImageDecoder`：它已退出生产装配，但 `tests/core/test_core_detect.py`、`test_sfx_assembly.py`、`test_sfx_policy_settings.py`、`test_stub_decoder.py` 仍直接使用它；删除会扩出本 Task 范围。没有证据支持新增共享导入框架或重写存储基础设施。

## 下一步与边界

最终建议：由 Coordinator 处置 AC3 项目永久删除缺口及超出范围的历史测试冲突；若需修改 `tests/core/test_stub_decoder.py`，另行冻结授权。最终 head 的范围内 findings 已闭合，无需再为 R-01/R-02 开修订任务；未启动任何新 Task。此次审查交付不代表集成授权，也不表示 P09 全 AC 关闭。

未检查：完整 pytest、UI/Tauri、真实并发链接替换和超大 PDF。已知风险：AC3 项目永久删除仍无验证入口；旧生产 stub 测试失败；DB 提交异常按最终契约向调用者传播。
