# FEAT-CREATE-2 独立 Review（R1，Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | FEAT-CREATE-2（创建能力 2/4：Core 实现 `CreateBook`/`CreateChapter`，Core 2.8） |
| Owner | Codex |
| 交付 | `5cb28a705`（feat(core)）+ Handoff `FEAT-CREATE-2-5cb28a7.md` + 证据 |
| 结论 | **approved** |

## 我亲做的验证

| # | 项 | 结果 |
|---|---|---|
| V1 | 范围 | **PASS**：`core_service.py` + 2 测试文件 + Handoff/证据；**契约 0 变更、迁移 0 变更** |
| V2 | **无长度上限**（L614） | **PASS**：源码/测试中 `max_length/MAX_TITLE/len(title) >` **命中 0** |
| V3 | **重复是正例**（L616） | **PASS**：`test_create_chapter_defaults_and_allows_duplicate_titles_and_numbers` 明确允许重复；无"重名即失败"断言 |
| V4 | fail-closed | **PASS**：`test_invalid_create_payload_fails_closed_without_writes`（拒绝 + **零写入**）|
| V5 | book_id 校验 | **PASS**：`test_create_chapter_rejects_missing_or_deleted_book` |
| V6 | **minor 2.8 门控** | **PASS**：`_CREATE_PROTOCOL_MINOR = 8`、`_CREATE_COMMANDS` 集合；测试 `..._require_protocol_2_8_before_side_effects` 证明门控**先于副作用** |
| V7 | **原子性** | **PASS**：`test_primary_key_write_failure_leaves_no_partial_entity`（主键冲突不留半成品）——正是我在裁决中指定的验证方式 |
| V8 | **套件回归** | **PASS（我亲测）**：`pytest tests/core` **535 passed**（基线 515 → +20，零回归） |
| V9 | 契约逐字 | **PASS**：复用既有 `list_books` 投影（`test_create_book_uses_the_list_books_projection`），未新增响应字段 |

## 结论
实现严格贴合冻结契约（无长度上限、重复允许、fail-closed、minor 8 门控、原子性），**零迁移、零契约改动**，测试覆盖到反例与原子性，我复跑 **535 passed**。**批准集成**。

## 过程记录（正向）
Owner **两次**在动手前引行号指出我方 AC 与契约冲突（L614 无长度上限、L616 允许重复）并停止上报；我按其引用更正 AC 后恢复。**执行方拒绝写与契约冲突的测试**，是本 Task 质量的关键。