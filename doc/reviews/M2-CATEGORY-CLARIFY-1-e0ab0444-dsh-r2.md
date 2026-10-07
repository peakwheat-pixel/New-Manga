## r2 复核（返修验证轮）

VERDICT: approve

**方法与环境限制（随结论携带，与 r1 同源）**：本会话 `pwsh` 仍不可用——`Get-Location` 与 4 条 `git -C … ` 命令、以及委派子代理重试（workdir 改 `C:\Windows\Temp`）均逐字失败于沙箱准备阶段：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\CATEGORY-CLARIFY-1)`，未执行任何命令、未修改任何文件。因此本轮的"零代码/测试改动"结论由 **可读 Git 元数据（worktree reflog）+ r1 已审内容与当前工作树逐处等价核对** 建立，而非 `git diff`（残余不确定性见文末）。

---

### 一、逐项判定（PR-01..05）

| 项 | 判定 | 证据（一句） |
|---|---|---|
| **PR-01**（P3） | **fixed** | Handoff `:48`（设计裁定 4）与 `:53`（Reviewer 关注点）已按 r1 口径改写：明写用例 2 走 `handle_rerender_page` 前置校验 `RegionLookupError →` dispatch 硬编码 `TARGET_NOT_FOUND`/`not_found`、**不经**被改三元，且明写"不是三元链的分支顺序（不可重叠字面量）"；两处技术断言我独立复核成立（`core_service.py:882-883,1438-1453`；`:1447` category）。全仓 `分支顺序` 仅剩该否证句，`tests/` 零匹配。 |
| **PR-02**（P4） | **deferred-accepted** | Handoff `:38` 登记 "deferred——下一轮契约澄清候选清单（与 RC4-08 一并跟踪）"；契约 §8 现状确实仍无反向指针（`M2-C1:325,337` 未动），与 r1 建议的延后口径一致。 |
| **PR-03**（P4） | **deferred-accepted** | Handoff `:39` 登记 deferred，并如实指出本刀注记已含"可用性失败"定性（`M2-C1:140` 逐字核对成立）；**保留项**：r1 原话中"非瞬时/unavailable 语义 + `retryable` 保持 false"两点未落注记，须随 deferral 原样带入下一轮清单（该行未声称已闭合，故不构成不实）。 |
| **PR-04**（P4） | **fixed** | `raw/category-clarify-attrib-1.log:4` 命令确为 `-v (PR-04 attribution)`，`:11` `collected 2 items`，`:13-14` 两用例逐条 `PASSED`，`:16` `2 passed in 0.92s`，`:17` `EXIT=0`；带 SHELL/PYTHON/HEAD 头（`:1-3`）。 |
| **PR-05**（P4） | **deferred-accepted** | Handoff `:41` 登记 deferred 至同一候选清单（RC4-08 在本刀后 category 亦分叉 `unavailable` vs `internal`），未声称本刀闭合，与 `Task:38-40` 范围一致。 |

**额外两项（r2 清单）**：

- **docs-only 核实（部分可证，判定成立）**：reflog `.git/worktrees/CATEGORY-CLARIFY-1/logs/HEAD:5-6` 显示 `81a39614 → e0ab0444`，且 e0ab0444 的 commit message 即 `docs(category-clarify): r1 disposition PR-01 wording fix + attribution log (code/test zero change)`；三处代码/测试 artefact 与 r1 已审 head 逐处等价（见下"核对过"清单第 2 条），**未发现任何代码/测试改动迹象**。与之相符的是：本提交可观测到的三个文件变化（Handoff 改写、attrib 日志新增、r1 报告入库）全部落在 `doc/**` 与 `verification/**`。
- **处置表如实性**：PR-01/04 的 "fixed" 与 PR-02/03/05 的 "deferred" 逐行比对证据成立，无"把 deferred 记为已闭"或"把文案修正声称成代码修正"的措辞；`Task`/`Handoff` 的 `delivery_commit=af640916` 未被篡改。

### 二、新发现

- **N-01｜P4｜`doc/handoffs/M2-CATEGORY-CLARIFY-1-zcode-af640916.md:9`｜`Rework head` 是悬空引用**：`:9` 写 "Rework head: 见文末 disposition"，但 `:35-41` 的处置表只有 PR 行、**没有登记返修 commit hash `e0ab0444`**（全 Handoff/`Task`/`STATUS` 均无该 hash）。当前只能从 reflog/分支 tip 推得。**建议**（不阻塞、可并入集成收口 commit）：在 `:9` 直接写 `e0ab0444`（沿 `M2-DERIVED-GC-1` 的 `rework 4edec70a` 先例）。
- **N-02｜P4｜PR-04 处置行未写归因日志的绑定 commit，而该日志自述 `HEAD=81a39614`（`raw/category-clarify-attrib-1.log:3`）**，既非 delivery head `af640916`，也非 tip `e0ab0444`。日志自带 HEAD 头符合证据纪律、归因本身有效（81a39614 相对 af640916 为 docs-only，且 r1 复核的代码/测试内容与该 head 逐处一致），但与另外 5 份 `@af640916` 日志并排易被误读为同一绑定。**建议**：`Handoff:40` 补一句 "HEAD=81a39614（docs-only 差值，被测测试文件同 `af640916`）"。

**两项均为记账精度级 P4，不阻塞集成。无 P0/P1/P2。**

### 三、核对过、未发现问题的关键点

1. **返修 commit 存在与顺序**：reflog `:3-6` 链 `db8999fa → 1091c861（release）→ af640916（交付）→ 81a39614（handoff+raw 日志）→ e0ab0444（r1 处置返修）`；worktree `HEAD` 仍指 `refs/heads/zcode/category-clarify-1`，与 `Task:6,14-16`、`Handoff:7-8` 一致。
2. **代码/测试与 r1 已审 head 逐处等价（零改动的最强可用证据）**：`src/bootstrap/core_service.py` 总行 1723，`:891-898` 注释 2 行+三元拆分、`:899-904` message 字典、`:1438-1453` dispatch 硬编码 `TARGET_NOT_FOUND`/`not_found`（`:1447`）、`:1465` `retryable=False`，与 r1 记录逐字相同；`tests/core/test_rc4_category_clarify.py` 总行 107，用例 1 `:76-91`（`:88` category 断言）、用例 2 `:94-107`（`:105` not_found 断言）、docstring `:1-9` 与 r1 引用完全对齐；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 总行 414、`:140` 注记完整。
3. **PR-01 新措辞的技术正确性（独立复核，非沿用 r1）**：页级路径 `service.py:147-286` 不产生 `TARGET_NOT_FOUND`（`:297` 属 `rerender_region`）；`infrastructure/sqlite/artifacts.py:126` 的 `CommitStatus.TARGET_NOT_FOUND` 在 `service.py:596` 映射为 `RenderStatus.WRITE_FAILED`（`"write_failed"`），随后被 `core_service.py:889-890` 改写为 `ARTIFACT_WRITE_FAILED` ⇒ "`E_TARGET_NOT_FOUND` 臂不可达/防御性死枝" 成立；用例 2 的 `RegionLookupError` 路线（`:882-883`）确在 `:884` 调渲染**之前**，故"不经被改三元"成立。
4. **PR-01 处置行自述如实**："测试 docstring 无同款错误因果表述（PR-01 所指 :94-107 为用例函数体）"——实读 docstring `:1-9` 只有 unavailable/非修订定性，`tests/` 内 `分支顺序|order of the ternary` 零匹配。
5. **r1 报告入库与链接**：`doc/reviews/M2-CATEGORY-CLARIFY-1-af640916-dsh-r1.md` 存在且内容为该轮结论（含 `:11` 的 pwsh 环境限制，与本次实测逐字复现，可信）；`Handoff:31` 相对链接 `reviews/…-dsh-r1.md` 解析正确。
6. **Handoff 其他断言未因返修引入新不实**：AC1/AC3 行仍引 `HEAD=af640916` 的 focused/full/cargo/vitest/build 五份日志（本轮无代码变更，无需重跑，与 r1 "返修后无需重跑全量" 结论一致）；`:31` AC4 仍如实标 `r2 PENDING`；`:37-41` 表头 "r1 @`af640916`" 标注正确。
7. **未越权/未扩大范围**：返修只触及 `doc/handoffs/**`、`doc/reviews/**`、`verification/M2-CATEGORY-CLARIFY-1/raw/**`；`src/**`、`apps/**`、`tests/**`、`doc/contracts/**`、`doc/tasks/**` 无返修期改动迹象（`Task` frontmatter `delivery_commit=af640916`、`integration_commit: null` 保持原样）。

### 四、残余不确定性（如实登记，非 finding）

`git diff --name-only af640916 e0ab0444` 无法执行，故不能排除"保持行号与全部被引内容不变的等价改写"；结合 reflog commit message、上述逐处内容等价、以及三处可观测变化均为文档/证据路径，该风险被压至极低，但**不等于** git 级证明。建议集成方在 merge 前的范围核对中以 `git diff --stat af640916 e0ab0444 -- src tests apps`（预期空）一次性闭合。

### 五、推荐下一步

1. **Integrator（Codex）**：条件项已闭，按 `Task:49-51` 完成定义执行 merge main + `STATUS`/`REBASELINE_PLAN` 收口；收口时**顺手闭合 N-01/N-02**（补 `e0ab0444` 与 attrib 日志绑定说明），并把 PR-02/PR-03（含"非瞬时 + `retryable=false` 明说"）/PR-05 登记进下一轮契约澄清候选清单，与 RC4-08 一并跟踪；同 commit 内跑一次 `git diff --stat af640916 e0ab0444 -- src tests apps` 作为零代码改动的 git 级证据。
2. **无需本任务内的其他下一步操作**（不再需要 r3 复审）。
