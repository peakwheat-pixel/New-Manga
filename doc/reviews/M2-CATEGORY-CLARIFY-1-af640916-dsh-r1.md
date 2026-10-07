核对完毕。以下是 r1 Review 结论。

VERDICT: approve_with_conditions

（0×P0 / 0×P1 / 0×P2；1×P3 为交付文档中"对照用例判别力"的事实性表述偏差，属文案条件项，不改代码与测试；其余 4 项 P4。AC1–AC3 证据链独立复核全部成立，"非修订"定性成立、**不触发** Handoff 自列的 P2 升级条件。）

---

## 一、审查方法与限制（随结论携带）

- 本会话沙箱 **pwsh 不可用**：`pwsh -Command` 三次（含 `Get-Location`）均以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\CATEGORY-CLARIFY-1)` 失败，命令未执行；升级 `danger-full-access` 无审批通道。与 RC-4 r1 报告 `doc/reviews/M2-RC4-DOMAIN-COMMANDS-5954bb4b-dsh-r1.md:16` 记录的同一环境限制一致。**未运行任何命令、未修改任何文件**，未取得 `git status/diff/show`。
- 替代手段（因此本次证据强于"仅引用 raw 日志"）：主仓库工作区仍停在 base `db8999fa`（`.git/logs/HEAD:870`：`44859014 → db8999fa` "docs: close out M2-DERIVED-GC-1"），故我直接用 `G:\CODEX\New Manga\` 的 base 文件做 **base↔head 逐处对照**，等价于受限 diff。
- 未能验证项（残余不确定性）：工作树是否存在未提交改动；两个被改文件是否存在"净行数相同"的其他编辑。已通过主树对照 + 行数守恒 + 内联注释/契约注记/测试内容一致性把该风险压到很低，但不等于 `git diff`。

## 二、逐条发现

| ID | 级别 | 文件:行 | 触发与影响 | 证据与建议处置 |
|---|---|---|---|---|
| **PR-01** | **P3** | `doc/handoffs/M2-CATEGORY-CLARIFY-1-zcode-af640916.md:37,42`；`tests/core/test_rc4_category_clarify.py:94-107`（docstring 口径） | Handoff 对"对照行"判别力的两处表述与代码可达性矛盾：①`:37`"用例 2 钉住映射拆分不误伤 `TARGET_NOT_FOUND`（拆分最常见的回归就是把三元链写错**分支顺序**）"；②`:42`"把 not_found 误改成 unavailable → **用例 2 红**"。实际：用例 2 走的是 `handle_rerender_page` **前置校验**（`core_service.py:882-883` `raise RegionLookupError`）→ dispatch 硬编码 `TARGET_NOT_FOUND`/`"not_found"`（`core_service.py:1438-1453`，category 在 `:1447`），**根本不经**被修改的三元表达式；且三个条件是不可重叠的字面量，**分支顺序不构成回归向量**。另：该三元中 `code == E_TARGET_NOT_FOUND` 这一臂在 page 面**不可达**——页级 `RenderService.rerender_page` 仅产生 `MISSING_REQUIRED_INPUT`/`ARTIFACT_WRITE_FAILED`/`COMPOSITION_BASE_CHANGED`；`CommitStatus.TARGET_NOT_FOUND` 在 `application/rendering/service.py:596` 被映射为 `WRITE_FAILED`，随后 `core_service.py:889-890` 改写为 `ARTIFACT_WRITE_FAILED`（防御性死枝）。 | **属文案精度问题，非代码缺陷**（不会产生错误行为）。建议按同仓 RC4-02 先例口径处置：改写 `:37/:42`，如实说明用例 1 钉新臂、用例 2 钉"同一命令面的 dispatch 前置 `RegionLookupError → TARGET_NOT_FOUND/not_found` 路线"，并删除"分支顺序"因果。Task `:33` 已冻结、可不动；Handoff 属入库证据应更正，否则后续审计会据错误因果重复推演。 |
| **PR-02** | P4 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:140`（vs §8 `:325,330,337,339-345`） | 澄清落在 §5 `RerenderPage` 行尾，而 §8 才是 taxonomy 的家：§8 无任何指向本注记的交叉引用，§8 `:337`"未知或未映射错误应使用 `category="unknown"`"原样保留；且该行"错误…以 RC-4 契约为准"的指针指向的 `M2-RC4_DOMAIN_COMMANDS.md` **全文零 `category` 字样**（grep 确认）。搜索 §8 的读者学不到该实现口径。 | 非阻塞。建议下一轮（或集成收口时）在 §8 前注加一行指针（不改分类表正文，不违"§8 正文零改写"冻结），或把 category 口径登记进 RC-4 契约；本次不做也不影响 AC2。 |
| **PR-03** | P4 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:140`；`src/bootstrap/core_service.py:894-898`；`apps/desktop/src-tauri/src/library_bridge.rs:58-59` | `unavailable` 在本仓另有一处既有用法是**宿主侧瞬时传输失败**：`LibraryError::unavailable` → `CORE_UNAVAILABLE`/`unavailable`/**retryable=true**（spawn/stdio/EOF）。本刀产生的是**数据缺失且 retryable=false**（`core_service.py:1465` 固定 false，本刀未改）。同值不同义（瞬时 vs 永久）。§8 未定义任何 category 语义，且**无任何消费者按 category 分支**（见下"已核对"），故无功能影响。 | 非阻塞。建议注记补一句"此处 unavailable=输入数据缺失（非瞬时服务不可用），retryable 保持 false"，以免消费者按 HTTP 直觉把 unavailable 当可重试。若 Codex 认为该歧义值得收口，可登记为后续 taxonomy 语义条目。 |
| **PR-04** | P4 | `verification/M2-CATEGORY-CLARIFY-1/raw/focused-pytest-1.log:21`；`full-pytest-1.log:399` | 5 份 raw 日志均绑 `HEAD=af640916`（`:3`）且 `EXIT=0`，但均为 `-q` 点阵：**2 条新用例的通过状态无法逐条归因**（只能由"focused +2、full +2、全仓无其他新增用例"推断）；`1 skipped` 未用 `-rs`，skip 名不入证据（与已接受的主基线 `1884+1sk` 计数相同，无差值风险，故不按 RC4-04 升级）。 | 非阻塞建议：Gate 附一次 `pytest tests/core/test_rc4_category_clarify.py -v`（或 `--collect-only` 计数）即可闭合归因，成本极低。 |
| **PR-05** | P4 | `src/application/rendering/service.py:261-278,368-383`；`M2-C1:140` | 既有登记项 RC4-08（同一物理条件"必要输入不可用"两种 wire 码：clean 解码失败 `MISSING_REQUIRED_INPUT` vs 合成器解码失败 `ARTIFACT_WRITE_FAILED`）在本刀后**又多了 category 分叉**（`unavailable` vs `internal`）。Task `:38-40` 明确不覆盖 RC4-08，属范围外。 | 仅登记提示：建议在下一轮澄清或 §5 注记中把 RC4-08 标注为"category 层面亦受影响、仍 open"，避免 taxonomy 继续漂移。本刀无需动作。 |

## 三、"非修订"定性审讯结论（Handoff 设计裁定 1）

**定性成立，不升级 P2。** 逐条证据：

- `M2-C1 §8`（`:323-347`）整节首行明确"以下为 **PROPOSAL**"（`:325`）；分类表每行 Mapping confidence 列逐行写"taxonomy mapping is Proposal"（`:341-345`），且**表中根本没有 `MISSING_REQUIRED_INPUT` 行**——旧映射 `not_found` 从未在任何 revision 中被登记冻结，属实现自选。§8 值域 `:330` 本就含 `unavailable`，本刀**未引入新枚举值**。
- `M2-RC4_DOMAIN_COMMANDS.md` 中 `category` **零出现**（grep 全文件无匹配）；其 `rerender_page` 行（`:11`）冻结的是 DTO、错误**码**与保护语义，并原文写"缺 clean/必要原图、字体或布局不可用=MISSING_REQUIRED_INPUT"（即"不可用"语义），未冻结 category。
- r1 RC4-10 原文（`doc/reviews/M2-RC4-DOMAIN-COMMANDS-5954bb4b-dsh-r1.md:33`）："契约未冻结 category…故仅为口径建议"；r2（`…1e6b58b9-dsh-r2.md:52`）降级接受并建议"落到下一轮契约澄清"。Handoff `:34` 的转述忠实。
- 版本纪律：§3.2 `:103` 的 major 清单针对**字段**（删除/改名/类型/枚举旧值语义/必填性），category 是对**未冻结的 §8 Proposal 映射**的实现口径对齐，非 §3.2 情形；`PROTOCOL_MINOR` 仍为 6（`core_service.py:159`）与"bump=commands added"惯例一致，全量 pytest 全绿说明无 minor pin 被迁就。
- **先例支持"非修订登记"**：`M2-C1:21`（M2-PROD-DETECT-3 集成例外登记）就以"仅登记例外，不改既有条款正文"的方式登记了 §8 category 口径，无 Revision history 条目。本刀为同类更低风险（把与 §8 语义冲突的旧值改到语义更近值）。

## 四、代码审查结论

- **映射拆分正确、完备**：base（主树 `src/bootstrap/core_service.py:891-894`）为 `not_found if code in (E_TARGET_NOT_FOUND, "MISSING_REQUIRED_INPUT") else "internal"`；head（`:891-898`）拆为两支。可达码全集核对：`INPUT_REVISION_CHANGED`→conflict ✓（含 `COMPOSITION_BASE_CHANGED` 归一 `:887-888` 与 commit CONFLICT 的 `error_code="INPUT_REVISION_CHANGED"`，`infrastructure/sqlite/artifacts.py:205-215`）、`MISSING_REQUIRED_INPUT`→unavailable ✓、`ARTIFACT_WRITE_FAILED`（含 HASH_MISMATCH/DB_FAILED/TARGET_NOT_FOUND 经 `:889-890` 统一改写）→internal ✓、其余→internal ✓。无遗漏、无错分。字面量互斥 ⇒ 顺序无风险；`E_TARGET_NOT_FOUND` 臂不可达但无害。
- **code / message / retryable 零变化**：base `:895-900` 消息字典与 head `:899-904` 逐字相同；dispatch `RenderCommandError` 分支仍 `retryable=False`（`:1454-1469`，`:1465`）；`code` 值域未变（无新码、无改名）。
- **判别力反向推演**：把 unavailable 并回 not_found → 用例 1（`test_rc4_category_clarify.py:76-91`）红 ✓；把三元 `E_TARGET_NOT_FOUND` 臂误改 → **用例 2 不红**（见 PR-01）。即用例 1 判别力真实、用例 2 判别的是另一条路线。两用例均为真实端到端（`assemble_production_core` + 真实导入 + 进程内 `dispatch_request`），无 skip/xfail/`assert True`，无"测试迁就实现"。
- **其他断言面**：`tests/rendering/test_rerender.py:249,295,448,587,599` 断言的是 `outcome.error_code`（RenderService 层，非 wire envelope）；`tests/providers/test_full_chain.py:655` 是 `PipelineError.code`；`tests/workbench/test_projection.py:154`、`tests/pipeline/test_pipeline.py:228` 是 pipeline/step 语义。全仓唯一断言该 envelope category 的是新用例 `:88`。**无其他受影响断言面。**

## 五、边界检查结论

- **其余命令面零变化**：base↔head 对照显示被改文件仅此一处；`core_service.py` 总行数 1719→1723，恰为注释 2 行 + 三元展开 +2 行，**净 +4 与声明 hunk 完全吻合**。`doc/contracts/M2-C1…md` 总行数 414→414：仅 `:140` 行尾追加一句，其余未动（base 同行为无注记版本，已逐字比对）。
- **React/Rust/Legacy 零接触**：`apps/**` 中 `MISSING_REQUIRED_INPUT|error_code` **零匹配**；`category` 仅出现于 `library_bridge.rs`（结构体/透传/测试）与 `frontend/src/library/types.ts:30`（`category?: string` 仅声明，**无任何分支消费**，全 `apps/desktop/frontend` 无第二处引用）。Rust 既有 category pin（`main.rs:1715` validation、`:1760` not_found）属 retype/list 面，不受影响。**frontend build 产物与基线字节同哈希同尺寸**（`index-CbuaKdcb.js` / 198.48 kB，两侧日志一致）= React 面零改动的强证据。`src/ui/**`（Legacy）无任何 `CATEGORY-CLARIFY` 引用。
- **改动文件全集**：worktree 中引用本 Task 的仅 `src/bootstrap/core_service.py`、`tests/core/test_rc4_category_clarify.py`（base 不存在→新建）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/tasks/…`、`doc/handoffs/…`、`verification/M2-CATEGORY-CLARIFY-1/raw/*`（base 不存在→新建），与 Handoff 声明一致。

## 六、核对过、未发现问题的关键点

1. **base/head 绑定**：`.git/worktrees/CATEGORY-CLARIFY-1/HEAD` → `refs/heads/zcode/category-clarify-1` → `81a39614`；reflog `.git/worktrees/…/logs/HEAD:3-5` 链 `db8999fa → 1091c861（release）→ af640916（交付）→ 81a39614（docs+日志）`，与 Task `base_commit`/`delivery_commit`、Handoff `:8` 完全一致；main 未前进（仍在 `db8999fa`），`integration_commit: null` 如实。
2. **AC1**：focused `432 passed`（`focused-pytest-1.log:21`，HEAD=`af640916`，`EXIT=0` `:67`），与上一 Task 基线 **430**（`verification/M2-DERIVED-GC-1/raw/focused-pytest-1.log:21` @`9c9c7e55`）严格 +2。
3. **AC2**：`M2-C1:140` 注记落字，含 unavailable 澄清、§8 值域出处、"从未冻结/非修订"、其余四码不变声明——与代码行为逐条相符。
4. **AC3**：全量 `1886 passed, 1 skipped`（`:399`，`EXIT=0` `:400`）vs 基线 `1884 passed, 1 skipped`（GC 日志 `:399-400`）；cargo `55 passed; 1 ignored`（`:86-88`）与基线 `:79-81` 同；vitest `136 passed`（`:23`）与基线 `:23` 同；build `EXIT=0`（`:14`）与基线同且产物哈希相同。
5. **raw 日志 HEAD 行自述**：focused/full/cargo/vitest/build 五份 `:3` 均为 `af6409165f2cce6acbcf4cb…`（完整 `af6409165f2cce6acbcf4fb7fc79a703930b7522`），符合 Task 要求与 §6 "测试结果只适用于记录的 commit"。
6. **Hook 一致性**：`core_service.py:891-893` 内联注释、`test_rc4_category_clarify.py:1-8` docstring、`M2-C1:140` 注记三处口径一致（unavailable + 非修订 + 四码不变），无相互矛盾。
7. **`unavailable` 语义依据**：`RenderService` 对缺 clean（`service.py:154-160`）、clean/translated 不可读（`:162-165,354-359`）、字体/布局不可用（`:201-217`）统一 `MISSING_REQUIRED_INPUT`；`TARGET_NOT_FOUND` 是 region/页**寻址**失败（`service.py:297`、handler 前置 `core_service.py:882-883`）——"补数据 vs 改 id"的动作差异成立，r1 RC4-10 亦自荐 unavailable。**判定：语义可站住**（PR-03 仅记录同值不同义的边缘歧义）。
8. **授权路径**：Task `:8` 的 `user_2026-10-07_autonomous_mode_continuation（STATUS Planned next 候选②）` 与上一 Task `M2-DERIVED-GC-1.md:9` 同款先例一致；`REBASELINE_PLAN.md:20` 明确授权"RC-4 done 后按最新实测缺口选下一最高优先任务，无需逐步申请授权…均须先单独 Task 冻结范围与 Gate"；本 Task 文件即冻结范围。**非治理缺陷**；收口时须补 `REBASELINE_PLAN` 行与 `STATUS` checkpoint（完成定义已列，勿漏）。
9. **确定性纪律**：Task `:24,:39` 自述的非修订理由在仓库内可读证据中全部成立（§8 Proposal、RC-4 无 category、r1 原文），**未发现"声称与事实不符"**——即 Handoff 自列的 P2 升级条件不触发。
10. **其他**：`PROTOCOL_MINOR=6` 未 bump 与"无新命令"一致；新用例沿 `test_rc4_revision_commands.py:51-60` 同款 `_rpc`/`NOW`/`assemble_production_core` 先例（Handoff 归因于 `test_page_nav_projection`，两者皆为先例，不构成问题）；未在 `src/**` 引入 Qt/新依赖。

## 七、推荐下一步

1. **Owner（Codex Executor / ZCode 代行）**：仅做文案返修——按 PR-01 改写 `doc/handoffs/M2-CATEGORY-CLARIFY-1-zcode-af640916.md:37,42`（必要时同步新测试 docstring 口径），可选顺笔 PR-04 的归因日志；**代码/测试零改动**，返修后无需重跑全量（无 src/tests 变更），在 Handoff 追加一条更正说明即可。
2. **Integrator（Codex）**：条件项关闭后按 `完成定义` 执行 merge main + `STATUS`/`REBASELINE_PLAN` 收口，并把 PR-02/PR-03/PR-05（§8 交叉引用、unavailable 语义注记、RC4-08 category 分叉）登记进下一轮契约澄清候选清单，与 RC4-08 一并跟踪。
3. 无需本任务内的其他下一步操作。
