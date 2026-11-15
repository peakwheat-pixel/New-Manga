---
id: FEAT-CREATE-2
title: 创建作品/章节能力（2/4）——Core 实现 CreateBook / CreateChapter（Core 2.8）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261017_after_FEAT_CREATE_1
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [FEAT-CREATE-1]
base_commit: null
branch: null
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2
integration_commit: ebe47ff86
delivery_head: ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEAT-CREATE-2
---

# FEAT-CREATE-2：Core 实现 CreateBook / CreateChapter

## 来源
`FEAT-CREATE-1`（done）已把 M2-C1 升至 **rev 2.8**，冻结 `CreateBook {title}` → `BookSummary`、`CreateChapter {book_id,title,chapter_number?}` → `ChapterNavSummary`，含 **§5.10 安全投影**、**未知字段 fail-closed**、Core 为唯一校验/写入方，并判定**无需迁移**。

## Acceptance Criteria
- [x] **AC1**：按 §5.10 **逐字**实现两条 Core 命令（命令名/DTO/响应/错误）；**未知字段 fail-closed**；`title` **非空**（**契约 §5.10.2 L614 明确未引入最大长度 → 不设长度上限、不测超长**）；`CreateChapter` 的 `book_id` 必须存在且未删除。 <!-- verified: 闭合字段校验（未知字段→unknown_field、空白 title→blank）、无长度上限（max_length/len(title)> 命中 0）、CreateChapter 经 get_book 拒缺失或已删除 book_id；与契约 §5.10.2 逐字对齐：test:test_invalid_create_payload_fails_closed_without_writes@tests/core/test_core_create_commands.py:139 + test:test_create_chapter_rejects_missing_or_deleted_book@tests/core/test_core_create_commands.py:161 + grep:def _create_validation_details@src/bootstrap/core_service.py:1214 + grep:#### 5.10.2 Field validation and entity rules@doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:694 -->
- [x] **AC2**：持久化到既有 `books`/`chapters` 表（**不新增表、不加迁移**，与 FEAT-CREATE-1 结论一致）；写入须在既有事务/约束内，失败不留半成品。 <!-- verified: 复用既有 books/chapters 表与 LibraryService/SqliteLibraryRepository，实现提交 5cb28a705 仅改 core_service.py 与 2 个测试文件（零 Schema/迁移/新表）；主键冲突注入断言失败不留半成品：test:test_primary_key_write_failure_leaves_no_partial_entity@tests/core/test_core_create_commands.py:198 + grep:def create_chapter@src/application/library/service.py:132 + file:verification/FEAT-CREATE-2/pytest-core.log -->
- [x] **AC3**：响应**只**含 §5.10 白名单字段（`BookSummary`/`ChapterNavSummary`）；错误只走既有稳定 envelope；**不得**返回路径/Secret/原始异常。 <!-- verified: 响应键集严格等于 BookSummary/ChapterNavSummary 白名单（set 相等断言），错误只走封闭 envelope（无 message、不回显 private/path 输入，断言零写入）：test:test_create_book_uses_the_list_books_projection@tests/core/test_core_create_commands.py:57 + test:test_invalid_create_payload_fails_closed_without_writes@tests/core/test_core_create_commands.py:139 + grep:def handle_create_book@src/bootstrap/core_service.py:1752 -->
- [x] **AC4**：命令在 `core_service` 实现**并**在 `core_assembly`/分发处注册（与既有导航命令同机制）；协议 minor 按 **2.8** 门控；既有命令语义零变化。 <!-- verified: core_service 分发处注册（_CREATE_COMMANDS 分支、minor 8 门控先于副作用），core_assembly 既有 LibraryService 装配复用；既有 ListBooks 2.3 读取面回归断言通过：grep:_CREATE_PROTOCOL_MINOR = 8@src/bootstrap/core_service.py:326 + test:test_create_commands_require_protocol_2_8_before_side_effects@tests/core/test_core_create_commands.py:184 + grep:library = LibraryService(repository)@src/bootstrap/core_assembly.py:1246 -->
- [x] **AC5 测试**：覆盖成功路径 + 反例（未知字段、**空/仅空白 title**、不存在/已删除 `book_id`），并断言**失败不留部分数据**；**契约 §5.10.2 L616 允许重复标题与章节号 → 重复必须作为正例**（不得断言重名失败）；原子性用**主键冲突或注入写失败**验证（不得与契约冲突）；`pytest tests/core` **不得回归（基线 515）**。 <!-- verified: 覆盖成功路径+反例（未知字段/空或仅空白 title/不存在或已删除 book_id）、重复标题与章节号作为正例、主键冲突原子性；pytest tests/core 535 passed（基线 515，零回归，EXIT_CODE=0）：file:verification/FEAT-CREATE-2/pytest-core.log + test:test_create_chapter_defaults_and_allows_duplicate_titles_and_numbers@tests/core/test_core_create_commands.py:80 + test:test_primary_key_write_failure_leaves_no_partial_entity@tests/core/test_core_create_commands.py:198 -->
- [x] **AC6**：commit + **Handoff（必须）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。 <!-- verified: Handoff status=in_review；4 条 Canonical Evidence sha256 磁盘复算 4/4 与卡一致，且 commit ebe47ff86 包含所列路径（git cat-file -e 通过）；40 位原样 SHA（BL-17）：file:doc/handoffs/FEAT-CREATE-2-5cb28a7.md + grep:status: in_review@doc/handoffs/FEAT-CREATE-2-5cb28a7.md:7 + file:verification/FEAT-CREATE-2/ac-results.md -->

## 允许 / 禁止
- 允许：`src/**`、`tests/core/**`、本 Task、`doc/handoffs/FEAT-CREATE-2-*.md`、`verification/FEAT-CREATE-2/**`。
- 禁止：改契约（wire 已冻结；有问题**停下上报**并引行号）；改 Schema/迁移/依赖；改 `apps/**`（host 注册属 FEAT-CREATE-3）；改 STATUS/PLAN；碰用户 19 项 dirty。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-1（done）。**后继**：FEAT-CREATE-3（host）、FEAT-CREATE-4（前端）。
- 风险：为图方便加字段/加表 → AC2 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。

## Canonical Evidence

R3-006 于 2026-10-18 回填。以下 SHA-256 按当前磁盘字节计算；对应 40 位 commit 均包含所列路径，且其 Git blob 与当前磁盘字节一致。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| FEAT-CREATE-2-AC-RESULTS | AC1–AC4 | verification/FEAT-CREATE-2/ac-results.md | ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c | 83300ff41776b67502893c8bfe08e4e852edf40fb9ee9d766c361d54f0b52212 | CANONICAL |
| FEAT-CREATE-2-CHECKPOINT | Recovery | verification/FEAT-CREATE-2/codex-checkpoint-blocked-20261017.md | ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c | 829ee2b8f01ecf5fa4eb0f1763ca07fccd44b883f25102408b81ee95fa767a1f | CANONICAL |
| FEAT-CREATE-2-DSH-REVIEW-R1 | Review | verification/FEAT-CREATE-2/dsh-review-r1.md | ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c | 47b8804d859f11fe12e72b337c79b149a09c52392819479d665c83245d75a9b6 | CANONICAL |
| FEAT-CREATE-2-PYTEST-CORE | AC5 | verification/FEAT-CREATE-2/pytest-core.log | ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c | 5e834c6c59ee3a8c998c571a2fbe02082633343a810e6aebd1abc826b95bb9f5 | CANONICAL |

## Coordinator 裁决（2026-10-17）：AC 与冻结契约对齐

Owner 在动手前引 §5.10.2 **L614/L616** 指出我方 AC 与契约冲突，**判定正确**。裁决：
1. 契约权威：	itle **无最大长度**（L614）→ 不设上限、**删除超长反例**；只验**非空**。
2. 契约**允许重复**标题/章节号（L616）→ **重复是正例**，**不得**断言重名失败；原子性改以**主键冲突/注入失败**验证。
3. 其余 AC 不变。

## Resource Manifest

由 `GOV-DEBT-CLEANUP-2` AC6 补录；来源 `verification/P09-GOVERNANCE-DEBT-20261019/
missing-manifest-resource-facts.md`（实测）。**本表不构成任何删除/移动/归档授权**。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `PRESERVE_UNKNOWN` | `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `6cfa304013dcc41fd39978cf95dc1aa81be4db1c206594fe80bf2c030e683aa0` | 实测存在且已注册；dirty=0，untracked=0；HEAD 已在当前分支历史中 |
| task env | 无 | `NOT_APPLICABLE` | — | `6cfa304013dcc41fd39978cf95dc1aa81be4db1c206594fe80bf2c030e683aa0` | 实测 `New.Manga.workspace/task-envs/FEAT-CREATE-2` 不存在 |
| agent output | 无 | `NOT_APPLICABLE` | — | `6cfa304013dcc41fd39978cf95dc1aa81be4db1c206594fe80bf2c030e683aa0` | 实测 agent-output（coordinator 与根）均不存在 |
| evidence | `verification/FEAT-CREATE-2/` | `PRESERVE_REFERENCED` | `verification/FEAT-CREATE-2/` | `6cfa304013dcc41fd39978cf95dc1aa81be4db1c206594fe80bf2c030e683aa0` | 目录存在，4 个文件；未登记文件见 evidence-dir-classification.md |
