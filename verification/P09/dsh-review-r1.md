---
task_id: P09
title: 导入 Core
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P09-role.json` 指定；role_exclusion 已机器排除 owner=codex）
owner: codex
base_commit: d7fe920272d48eb4761347a5e18789dcbbdd05d6
declared_delivery_head: 87179691cbab8b97d30282c0d8d0b20d9d81122c
reviewed_head: 54d40e6686ba2006f8506b519d00672ee75adfeb
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P09-IMPORT-CORE
base_worktree: G:/CODEX/New Manga（用户 dirty 未被触碰）
date: 2026-10-16
mode: 只读审查 + 独立 Git/SHA-256/证据复核 + 范围与冻结契约核对；未修改被审分支或主仓任何文件
object_binding: VERIFIED
architecture_axis: PASS
verification_axis: PASS（AC1/2/4/5/6/7/8 有真实证据；AC3 受限）
decision: approved_with_conditions
---

# P09 导入 Core — 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/P09-import-core`，`d7fe9202..54d40e66`（Owner=**codex**，router `--prefer-agent codex` per DIR-2）。
- 交付链：`8ab617f2`（实现）→ `87179691`（路径替换拒绝硬化）→ `54d40e66`（证据与 Handoff 归档）。
- Reviewer 实际执行 Git、SHA-256、范围与证据复核；**未采信 Owner 自述**。

### 0.1 实际执行的复核

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only d7fe9202..HEAD` | **69 个路径，100% 落在授权范围**（含 `doc/contracts/P09_IMPORT_CONTRACT.md` 新增、`src/application/importing/**`、指定的 `src/bootstrap/*`、指定测试、`verification/P09/**`） |
| **冻结 IPC 契约** | 过滤 `M2-C1_TYPED_IPC_CONTRACT` | **未被触碰** ✅ |
| 越界路径 | 反向过滤授权集合 | **空** ✅（未动 MOBI 实现、未加缩略图、未改其他模块） |
| worktree 洁净 | `git status --porcelain` | **空（clean）** |
| 主仓零改动 | `git status --porcelain --untracked-files=no` | **19 项，与开工前逐行一致** |
| 完整目标测试集 | 独立读取 `logs/41-…review-fix.txt` 末尾 | **`91 passed in 3.59s`，`EXIT_CODE=0`** ✅ |
| **19 条 Canonical Evidence** | 逐条独立 `Get-FileHash` + `class` 白名单 | **19/19 通过**（`class` 仅 `CANONICAL`/`SOURCE_PIN`；sha256 与工作区一致） |
| AC 勾选诚实性 | 读 Task AC 区块 | AC3/AC9 **保持未勾选** ✅（未越权标完成） |

## 1. AC 逐项结论

| AC | Owner | Reviewer 判定 | 依据 |
|---|---|---|---|
| AC1 真实尺寸 | 完成 | **接受** | `29-ac1-production-core-decoder.txt`：生产装配导入 17×23，尺寸/hash/Managed Original 与实际一致；已消除恒 1×1 占位 |
| AC2 受控来源/逃逸拒绝 | 完成 | **接受** | `test_import_sources.py` 9 passed（显式范围、junction/symlink、相对穿越、**路径替换竞态** `40-path-replacement-race.txt`） |
| AC3 源 hash 零变化 | **BLOCKED** | **接受（受限）** | 两样本在 导入/项目软删除/Page 软删除/Page 永久清理/`TRANSLATE_ALL`/`REINPAINT_REGION`/`RERENDER_SINGLE` 后 hash **完全一致**；**「项目级永久删除」操作在产品中不存在**，无法验证该阶段（`evidence/AC3-project-permanent-delete-availability.txt`） |
| AC4 Copy 中断无坏 Page | 完成 | **接受** | 故障注入：发布中断 + Page 写入失败，均无"有 Page 无 Original" |
| AC5 Unicode 路径 | 完成 | **接受** | 中文/日本語/한국어/Emoji/空格/括号全通过 |
| AC6 重复检测 | 完成 | **接受** | 按 SHA-256 去重；默认跳过，显式 `IMPORT_AS_NEW` 新建（策略写入新契约） |
| AC7 PDF | 完成 | **接受** | 按页渲染导入 + 加密/损坏 PDF 零半成品拒绝（真实 encrypted PDF 用例） |
| AC8 范围锁定 | 完成 | **接受** | 首发=图片/文件夹+PDF；MOBI 仅有拒绝守卫测试；无缩略图实现 |
| AC9 Review + 集成 | **NOT_RUN** | **本 Review 闭合 Review 部分；集成由 Coordinator 执行** | Task 保持 `in_review`，未越权标 done |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P1（流程/权威）** | Task frontmatter 写 `owner: Codex`、`reviewer: Codex Reviewer (non-author)` —— 与项目权威参与状态（`.orchestrator/tasks/P09-role.json`：`owner=codex`、Reviewer 由 router 定为 **dsh**）不一致。Owner 在自身会话内启用了子 Reviewer（gpt-6.1-sol）做内部自检，**该内部 review 不能替代项目要求的独立非作者 Review** | closeout 把 `owner` 改为小写 `codex`、`reviewer` 改为 `dsh`；内部自检报告可作为 Owner 证据保留，但不计入项目 Review 链 |
| **F2** | **P1（基线破坏，必须 follow-up）** | `tests/core/test_stub_decoder.py::test_production_stub_decoder_returns_valid_decoded_image` **实测失败**：旧断言要求非法输入 `b"fake"` 被解成 1×1（占位行为），而新真实 decoder 正确**拒绝**非法输入。`tests/core/**` 不在 P09 授权范围，Owner 未越界修改（正确） | **必须**另立 follow-up 更新该测试，否则全仓 pytest 基线为红。这不是 P09 缺陷，而是行为变更的正确后果 |
| **F3** | P2（AC 受限） | AC3 的「项目级永久删除」阶段无对应产品操作，无法验收 | 登记 BACKLOG；P09 以 **`closed_with_limitations`** 收口，AC3 保持未勾选并在 Task 中写明受限原因 |
| F4 | P3 | TOCTOU 残留：Owner 自述"最终路径校验到 `read_bytes` 仍有 TOCTOU 窗口" | 登记 BACKLOG，供后续硬化；当前 9 个路径用例（含替换竞态）已通过，不阻塞集成 |
| F5 | P3（流程，第 4 次） | `delivery_head` 记 87179691（实现 head），实际 HEAD=54d40e66（证据/Handoff 归档） | 本次 Task 已明确区分"实现 head"与"归档 head"（比 P11/P10/P06 更清晰）；closeout 仍须冻结实际 HEAD |
| F6 | P4 | `git diff --cached --check` exit 1（历史 pytest 原始日志含尾随空格）；Owner 选择不改写原始日志 | 认可（原始证据优先于格式整洁）；closeout 记录该事实 |

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `54d40e6686ba2006f8506b519d00672ee75adfeb`，并修正 F1 的字段。
- **C2**：**F2 必须立即建立 follow-up**（更新 `tests/core/test_stub_decoder.py` 以匹配真实 decoder 语义），否则仓库测试基线保持红色。
- **C3**：AC3 受限（F3）与 F4 登记 BACKLOG；P09 以 `closed_with_limitations` 收口，不得标 `done`。
- 实现本身无需返修。

## 4. 能力边界

- 本 Review 覆盖代码范围合规、证据真实性与 AC 逐项结论；**不代表**全仓 pytest、UI/Tauri、断电恢复或大 PDF 压力验证（均未执行）。
- 所有 Git / SHA-256 / 路径 / 证据结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
