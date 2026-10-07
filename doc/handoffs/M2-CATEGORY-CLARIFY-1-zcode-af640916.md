# M2-CATEGORY-CLARIFY-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-CATEGORY-CLARIFY-1](../tasks/M2-CATEGORY-CLARIFY-1.md)（release 见 Task frontmatter base `db8999fa`）
- Branch/worktree: `zcode/category-clarify-1` @ `G:/CODEX/New Manga.worktrees/CATEGORY-CLARIFY-1`
- Delivery head: `af640916`（单交付 commit：映射拆分+2 用例+契约注记同 commit）
- Rework head: 见文末 disposition（r1 `approve_with_conditions` 后文案返修，代码/测试零改动）

## 交付内容（一句话）

RC4-10 澄清（P4，r2 建议「落到下一轮契约澄清」）：rerender 失败 envelope 的 `MISSING_REQUIRED_INPUT` → `category="unavailable"`（required input missing 属 §8 值域中的**可用性**失败，非 `not_found` 的「目标不存在」）；`TARGET_NOT_FOUND`→`not_found`、`INPUT_REVISION_CHANGED`→`conflict`、其余→`internal` 不变。**非修订**：category 值从未被任何 revision 冻结（§8 taxonomy 表标注 Proposal），M2-C1 §5 `RerenderPage` 行尾注记登记实现口径。code 值/message/retryable/其余命令面/React/Rust 零变化。

## 逐层交付（全部 @`af640916`）

### Core
- `src/bootstrap/core_service.py`（rerender 失败映射一处）：三元映射拆分（原来 `not_found if code in (E_TARGET_NOT_FOUND, "MISSING_REQUIRED_INPUT")` 拆为两支）。
- 测试 `tests/core/test_rc4_category_clarify.py`（**2 用例**，进程内 `dispatch_request` rpc 模式）：①有 region 缺 CLEAN artifact 的 page（`missing_clean_artifact` 形状）→ `error.code=="MISSING_REQUIRED_INPUT"` 且 `error.category=="unavailable"` 且固定 message；②未知 page → `TARGET_NOT_FOUND`/`not_found` 不变（防拆分误伤）。

### 契约
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5 `RerenderPage` 行尾注记：unavailable 澄清+值域出处+「从未冻结、非修订」定性+其余四码不变声明。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 Core | DONE | focused 四目录 **432 passed**（GC 基线 430 + 本 Task 2 新用例）；raw 日志 `verification/M2-CATEGORY-CLARIFY-1/raw/focused-pytest-1.log`（HEAD=`af640916`，EXIT=0） |
| AC2 契约 | DONE | RerenderPage 行尾注记（见上）；`af640916` |
| AC3 回归 | DONE | 全量 pytest **1886 passed+1 skipped+0 failed**（base 1884+1sk +2 新用例，等量递增）；cargo **55+1ign**、vitest **136**、build EXIT=0 基线不变（零 React/Rust 改动）；raw 日志 `verification/M2-CATEGORY-CLARIFY-1/raw/{full-pytest,cargo-test,vitest-run,frontend-build}-1.log`（HEAD=`af640916`） |
| AC4 非作者 Review | r2 PENDING | r1 [approve_with_conditions](reviews/M2-CATEGORY-CLARIFY-1-af640916-dsh-r1.md)（0×P0/P1/P2；1×P3 文案+4×P4）→ 文案返修（代码/测试零改动）→ DSH r2 |

## DSH r1 逐项 disposition（r1 @`af640916`，报告 `doc/reviews/M2-CATEGORY-CLARIFY-1-af640916-dsh-r1.md`）

| 项 | 级 | 处置 |
|---|---|---|
| PR-01 Handoff 对照用例判别力表述与代码可达性矛盾（用例 2 走 dispatch 前置校验不经被改三元；「分支顺序」因果不成立） | P3 | **fixed（文案）**——设计裁定 4 与 Reviewer 关注点两处按 r1 口径改写；测试 docstring 无同款错误因果表述（PR-01 所指 :94-107 为用例函数体，无表述需改） |
| PR-02 §8 无指向本注记的交叉引用 | P4 | **deferred 登记**——下一轮契约澄清候选清单（与 RC4-08 一并跟踪） |
| PR-03 unavailable 同值不同义（宿主瞬时 vs 数据缺失，retryable 不同） | P4 | **deferred 登记**——同上；本刀注记已含「availability 失败」定性 |
| PR-04 新用例通过状态无逐条归因（-q 点阵） | P4 | **fixed**——`raw/category-clarify-attrib-1.log`（-v 两用例逐条 PASSED，EXIT=0） |
| PR-05 RC4-08 在本刀后 category 亦分叉（unavailable vs internal） | P4 | **deferred 登记**——下一轮契约澄清候选清单 |

## 设计裁定（Reviewer 请特别核验）

1. **「非修订」定性**：M2-C1 §8 分类表 taxonomy 标注 Proposal、RC-4 契约未冻结 category、r1 RC4-10 原文「契约未冻结 category、UI 按 code 消费」——改 category 值属实现口径对齐，注记登记而非 Revision history 条目。若 Reviewer 认定需要修订号，应升级为 P2（声称与事实不符风险）。
2. **unavailable 的语义依据**：§8 值域第 8 行 `category: validation | not_found | conflict | unavailable | cancelled | internal | unknown`；required input missing（clean artifact/字体/布局不可用）是「数据暂不可用」而非「寻址目标不存在」——`TARGET_NOT_FOUND` 是页 id 无效（寻址失败），二者用户可采取的动作不同（补数据 vs 改 id）。
3. **消费面零影响**：React `WorkbenchPage` 的 rerender 失败反馈条按 code 文本显示（RC-4 r1 已证实 UI 按 code 消费）；Rust `error.code` 透传不变；category 变化只影响 error envelope 的分类字段。
4. **对照行钉的是另一条路线（r1 PR-01 更正）**：用例 2 走的是 `handle_rerender_page` 前置校验（`RegionLookupError` → dispatch 硬编码 `TARGET_NOT_FOUND`/`not_found`），**不经**被修改的三元表达式——它钉的是「同一命令面的 not-found 路线保持 not_found」，不是三元链的分支顺序（三个条件是不可重叠字面量，顺序不构成回归向量；三元中 `E_TARGET_NOT_FOUND` 臂在 page 面经 `:889-890` 改写后不可达，属防御性死枝）。用例 1 的判别力真实（把 unavailable 并回 not_found 即红）。

## Reviewer 关注点提示

- 实现集中在 `core_service.py` rerender 失败映射一处（约 6 行含注释）。
- 反向推演（r1 PR-01 更正后口径）：把 unavailable 并回 not_found → 用例 1 红；用例 2 钉 dispatch 前置 `RegionLookupError → TARGET_NOT_FOUND/not_found` 路线（不经被改三元）。
- 全仓 grep `MISSING_REQUIRED_INPUT`：rendering 层 outcome 测试（`tests/rendering/test_rerender.py`）只断言 `outcome.error_code`（RenderService 层，不经 wire envelope）；pipeline/full_chain 层为 pipeline step 语义，与本 envelope 映射无关——无其他断言面受影响。
