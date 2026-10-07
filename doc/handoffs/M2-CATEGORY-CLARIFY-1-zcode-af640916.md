# M2-CATEGORY-CLARIFY-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-CATEGORY-CLARIFY-1](../tasks/M2-CATEGORY-CLARIFY-1.md)（release 见 Task frontmatter base `db8999fa`）
- Branch/worktree: `zcode/category-clarify-1` @ `G:/CODEX/New Manga.worktrees/CATEGORY-CLARIFY-1`
- Delivery head: `af640916`（单交付 commit：映射拆分+2 用例+契约注记同 commit）

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
| AC4 非作者 Review | PENDING | DSH r1（本文档即派发依据） |

## 设计裁定（Reviewer 请特别核验）

1. **「非修订」定性**：M2-C1 §8 分类表 taxonomy 标注 Proposal、RC-4 契约未冻结 category、r1 RC4-10 原文「契约未冻结 category、UI 按 code 消费」——改 category 值属实现口径对齐，注记登记而非 Revision history 条目。若 Reviewer 认定需要修订号，应升级为 P2（声称与事实不符风险）。
2. **unavailable 的语义依据**：§8 值域第 8 行 `category: validation | not_found | conflict | unavailable | cancelled | internal | unknown`；required input missing（clean artifact/字体/布局不可用）是「数据暂不可用」而非「寻址目标不存在」——`TARGET_NOT_FOUND` 是页 id 无效（寻址失败），二者用户可采取的动作不同（补数据 vs 改 id）。
3. **消费面零影响**：React `WorkbenchPage` 的 rerender 失败反馈条按 code 文本显示（RC-4 r1 已证实 UI 按 code 消费）；Rust `error.code` 透传不变；category 变化只影响 error envelope 的分类字段。
4. **对照行的必要性**：用例 2 钉住映射拆分不误伤 `TARGET_NOT_FOUND`（拆分最常见的回归就是把三元链写错分支顺序）。

## Reviewer 关注点提示

- 实现集中在 `core_service.py` rerender 失败映射一处（约 6 行含注释）。
- 反向推演：把 unavailable 分支并回 not_found → 用例 1 红；把 not_found 误改成 unavailable → 用例 2 红。
- 全仓 grep `MISSING_REQUIRED_INPUT`：rendering 层 outcome 测试（`tests/rendering/test_rerender.py`）只断言 `outcome.error_code`（RenderService 层，不经 wire envelope）；pipeline/full_chain 层为 pipeline step 语义，与本 envelope 映射无关——无其他断言面受影响。
