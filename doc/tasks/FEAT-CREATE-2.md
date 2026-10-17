---
id: FEAT-CREATE-2
title: 创建作品/章节能力（2/4）——Core 实现 CreateBook / CreateChapter（Core 2.8）
kind: feature
governance_version: 2
status: in_review
approval: coordinator_release_20261017_after_FEAT_CREATE_1
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [FEAT-CREATE-1]
base_commit: a0e8683199a846715f9aa603b294dd11597768c1
branch: codex/FEAT-CREATE-2
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2
integration_commit: null
delivery_head: 5cb28a7059b547c9080ad89c0a14fa95cd95bf19
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEAT-CREATE-2
---

# FEAT-CREATE-2：Core 实现 CreateBook / CreateChapter

## 来源
`FEAT-CREATE-1`（done）已把 M2-C1 升至 **rev 2.8**，冻结 `CreateBook {title}` → `BookSummary`、`CreateChapter {book_id,title,chapter_number?}` → `ChapterNavSummary`，含 **§5.10 安全投影**、**未知字段 fail-closed**、Core 为唯一校验/写入方，并判定**无需迁移**。

## Acceptance Criteria
- [x] **AC1**：按 §5.10 **逐字**实现两条 Core 命令（命令名/DTO/响应/错误）；**未知字段 fail-closed**；`title` 非空（§5.10.2 L614 未引入最大长度 → 不设长度上限、不测超长）；`CreateChapter` 的 `book_id` 必须存在且未删除。证据：source、`test_core_create_commands.py`。
- [x] **AC2**：持久化到既有 `books`/`chapters` 表（**不新增表、不加迁移**，与 FEAT-CREATE-1 结论一致）；写入须在既有事务/约束内，失败不留半成品。证据：主键冲突反例与 production repository 写入。
- [x] **AC3**：响应**只**含 §5.10 白名单字段（`BookSummary`/`ChapterNavSummary`）；错误只走既有稳定 envelope；**不得**返回路径/Secret/原始异常。证据：安全投影与哨兵输入断言。
- [x] **AC4**：命令在 `core_service` 实现并经既有 `core_assembly` 中 `CoreServices.library` / dispatch 路径注册；协议 minor 按 **2.8** 门控；既有命令语义零变化。证据：production assembly 测试及旧 `ListBooks` 2.3 回归断言。
- [x] **AC5 测试**：成功与反例覆盖未知字段、空/仅空白 `title`、不存在/已删除 `book_id`；失败不留部分数据；§5.10.2 L616 重复标题/章节号作为正例；原子性由主键冲突验证。`pytest tests/core`：**535 passed，0 skipped，1 warning**（基线 515，净增 20）。
- [x] **AC6**：实现 commit `5cb28a7059b547c9080ad89c0a14fa95cd95bf19`、Handoff 与 Canonical Evidence 已提交；Task 状态 `in_review`。

## 允许 / 禁止
- 允许：`src/**`、`tests/core/**`、本 Task、`doc/handoffs/FEAT-CREATE-2-*.md`、`verification/FEAT-CREATE-2/**`。
- 禁止：改契约（wire 已冻结；有问题**停下上报**并引行号）；改 Schema/迁移/依赖；改 `apps/**`（host 注册属 FEAT-CREATE-3）；改 STATUS/PLAN；碰用户 19 项 dirty。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-1（done）。**后继**：FEAT-CREATE-3（host）、FEAT-CREATE-4（前端）。
- 风险：为图方便加字段/加表 → AC2 明确禁止。

### 阻塞记录（2026-10-17）
- 前状态：`ready`。按冻结契约逐字实现时，AC1/AC5 要求的“超长标题拒绝”无契约依据：§5.10.2 第 614 行明确不新增最大长度规则。不能自行增加上限或改契约，等待 Codex/用户将 Task 验收口径对齐冻结契约后再恢复。
- AC5 的“重复/冲突”需按契约解释：§5.10.2 第 616 行允许重复标题和章节号，不能把重名当失败；可覆盖允许重名，或用持久化主键冲突验证写失败原子性。
- Checkpoint：[FEAT-CREATE-2 blocker checkpoint](../../verification/FEAT-CREATE-2/codex-checkpoint-blocked-20261017.md)。

### Coordinator 恢复裁决（2026-10-17）
- Owner 对 AC/契约冲突的判断成立；按 §5.10.2 L614/L616 删除超长拒绝与重复失败断言，执行已对齐的 AC1/AC5。
- 用户裁决已将 Task 恢复为 `in_progress`；本 worktree 的 `doc/STATUS.md` 仍指向 ARCH-DOC-REBASELINE。STATUS 属本 Task 禁止修改路径，保留原文件并将此状态指针漂移交集成方处理。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。
- 2026-10-17 实现交付 `5cb28a7059b547c9080ad89c0a14fa95cd95bf19`；pytest 环境、命令、完整结果及 exit code 见 Canonical Evidence。
- Handoff：[FEAT-CREATE-2-5cb28a7](../handoffs/FEAT-CREATE-2-5cb28a7.md)；AC 结果：[verification summary](../../verification/FEAT-CREATE-2/ac-results.md)。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| C2-SOURCE | AC1–AC4 | `src/bootstrap/core_service.py` | `5cb28a7059b547c9080ad89c0a14fa95cd95bf19` | `44b5bc0e2717fe62d05e7307c80ebe945b0d0b3003400805f63d42c775a0c845` | CANONICAL |
| C2-TESTS | AC1–AC5 | `tests/core/test_core_create_commands.py` | `5cb28a7059b547c9080ad89c0a14fa95cd95bf19` | `b2963e121a6c1e57beadaf57ff5a4cd7225d1702d37e6b3e7099436a0d92229a` | CANONICAL |
| C2-REGRESSION | AC4 | `tests/core/test_core_service.py` | `5cb28a7059b547c9080ad89c0a14fa95cd95bf19` | `1ef0c292993f9640861c74c67af36d8e832ea512de3434561d8015e297282f0f` | CANONICAL |
| C2-TEST-LOG | AC5 | `verification/FEAT-CREATE-2/pytest-core.log` | `669e049e6934997e6a3f80518fe8d884fc03a8a8` | `5e834c6c59ee3a8c998c571a2fbe02082633343a810e6aebd1abc826b95bb9f5` | CANONICAL |
| C2-AC-RESULTS | AC1–AC6 | `verification/FEAT-CREATE-2/ac-results.md` | `669e049e6934997e6a3f80518fe8d884fc03a8a8` | `1ed596e0106273db907255ef47d819ac6f64f66cb4148f292329534f8671b972` | CANONICAL |
| C2-HANDOFF | AC6 | `doc/handoffs/FEAT-CREATE-2-5cb28a7.md` | `669e049e6934997e6a3f80518fe8d884fc03a8a8` | `fbc55352401c2b8ab984d3fab04753cc1aae9016a05f8c766f1475ab4dddd4bc` | CANONICAL |
