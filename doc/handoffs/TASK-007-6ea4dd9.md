---
task_id: TASK-007
author: ZCode
recipient: Codex（转 DeepSeek Harness 独立 Review）
base_commit: 6b123fe55f2e6373335b044fc5e5f169b5d108e0
delivery_head: 6ea4dd9241c0a24f60964b570cb768bb48dfa0f3
status: in_review
---

# Handoff：TASK-007（书架领域与本地图片导入）

实现 head：`6ea4dd9`。提交列表（自 base `6b123fe`）：

| commit | 说明 |
|---|---|
| `f20503e` | docs(TASK-007): 按派单接管，Task 文件补记 in_progress（派单时仍为 proposed 的差异已记录，附切片边界声明） |
| `6ea4dd9` | feat(TASK-007): 书架领域 + 本地图片导入 + tests/library（reviewed_head） |

变更路径（全部在允许白名单内）：`src/domain/books/**`、`src/domain/pages/**`、`src/application/library/**`、`src/application/importing/images/**`、`tests/library/**`。`src/infrastructure`、`src/ports`、`src/bootstrap`、`src/ui`、`tests/core`、`tests/storage`、依赖清单、AGENTS、其他 Task：零触碰。无 QML、无 Volume、无 PDF/MOBI/网页导入（TASK-023）、无新依赖。

## 交付内容与 AC 对照

- **AC-LIB-001 新建 Book**：**满足**。`LibraryService.create_book` 接受全部批准字段（title/original_title/语言/默认类型/方向），书架列表 `list_books` 立即可见；title 非空校验。测试：`test_create_book_shows_on_shelf`、`test_book_requires_title`。
- **AC-LIB-002 自定义标签**：**满足**。新增/重命名/删除/添加/移除；删除 Tag 仅解绑，Book 存活（`test_tag_lifecycle_and_book_link`）；重名拒绝。
- **AC-LIB-003 收藏/归档与 Tag 分离**：**满足**。`is_favorite`/`is_archived` 为 Book 系统标志，`test_favorite_and_archive_are_system_states` 断言不产生任何 Tag 行，且同名用户标签与之独立。
- **AC-CH-001 层级**：**满足**。Book→Chapter→Page 固定层级；无 Volume 实体；`chapter_number` 承载 `10.5`/`番外`（`test_hierarchy_book_chapter_page`）。
- **AC-CH-002/003 类型与方向**：**满足**。领域不变量：webtoon 必须 vertical、paged 只能 rtl/ltr（直接构造即拒绝）；`webtoon` 缺省解析为 vertical，paged 继承 book 方向（vertical 默认时回落 rtl，测试 `test_type_defaults_inherit_from_book`）。
- **AC-CH-004 混合类型**：**满足**。同一 Book 下 paged+webtoon 并存（`test_mixed_types_in_one_book`）。
- **AC-IMPORT-001 Managed Copy**：**满足**。导入逐文件完成 hash→decode→Managed Copy→建 Page，记录 source_filename/source_order/sort_order/hash/width/height/managed 引用（`test_managed_copy_records_all_fields`）。
- **AC-IMPORT-002 源文件不修改**：**满足**。源文件只读；导入前后磁盘 hash 一致（`test_source_file_hash_untouched`）；Unicode 源路径同样验证。
- **AC-IMPORT-003 中断不产生坏 Page**：**满足**。用例顺序保证 Managed Copy 成功后才 `add_page`；copy 失败（注入 `OSError`）→ `COPY_FAILED`、零 Page；decode 失败（截断 PNG 经真实 QImage 解码）→ `INVALID_IMAGE`、零 Page 且零复制；取消 → 已提交页保留、未处理文件列入 pending、每页 managed 引用可解析（`test_copy_failure_leaves_no_orphan_page`、`test_corrupt_image_rejected_without_page`、`test_cancellation_keeps_committed_pages_only`）。
- **AC-IMPORT-004 Unicode 路径**：**满足**。中文/日本語/한국어/emoji/空格/括号组合路径与文件名全部导入成功（`test_unicode_paths_and_filenames`）。
- **AC-IMPORT-005 重复检测**：**满足**。source_hash 去重，策略 `skip`（默认）与 `import_as_new` 可选（`test_duplicate_detection_by_hash`）。
- **AC-PAGE-001 Page 顺序**：**满足**。source_order 冻结、sort_order 用户重排互不干扰（`test_reorder_pages_keeps_source_order`）；文件夹收集按自然排序（page2 < page10）。
- **AC4 Handoff/Review/集成**：本 Handoff 交付；状态 `in_review`，done 待 DeepSeek 非作者 Review + Codex 集成。

## 验证证据

完整记录见 [verification/TASK-007/author-verification.md](../../verification/TASK-007/author-verification.md)。摘要：

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 库/导入套件（任务计划命令） | `python -m pytest tests/library -v` | py3.12.3 任务环境；head `6ea4dd9` | PASS，退出码 0，25 passed | author-verification #1 |
| 全量回归（含 TASK-005/006 全部测试） | `PYTHONPATH=src python -m pytest tests` | 同上 | PASS，退出码 0，62 passed | 同上 #2 |
| whitespace 与范围 | `git diff --check 6b123fe 6ea4dd9 --`；`git status` | 本 worktree | PASS（0 / 仅允许路径） | 同上 #3~4 |
| 架构边界 | grep domain/application 禁用 import；全量 core 守卫 | 同上 | PASS（domain/application 无 sqlite3/PySide6 实际导入） | 同上 #5 |

NOT_RUN / N/A：SQLite BookRepository 落地与 schema 扩展（允许路径不含 infrastructure/ports；契约在 application 侧定义、fake 驱动含模拟重启——SQLite 落地需 Codex 协调 TASK-006 边界后授权）；生产 ImageDecoder 装配（端口已定义，Qt 适配器在测试中验证真实解码）；书架 UI/搜索/回收站（TASK-012+）；AC-LIB-004 阅读摘要（非本 Task 主责 AC，属阅读器切片，`last_opened_at` 字段已就位）；PDF/MOBI/网页导入（TASK-023）；容量/性能（Benchmark 阶段）。

## 边界与设计决策（供 Review 重点）

1. **Repository 契约位置**：`src/application/library/ports.py`（消费侧 Protocol）；importing 侧同（`ports.py`：ImageDecoder/ManagedCopyStore/ImportPageSink）。原因：本 Task allowed_paths 不含 `src/ports`/`src/infrastructure`，不扩大范围；SQLite 实现与 ports 汇总留给后续授权切片。
2. **decode 验证真实发生**：生产 use case 仅依赖 `ImageDecoder` 端口（不绑定成像库，application 层无 PySide6 导入）；测试适配器用 PySide6 QImage 真实解码（损坏/截断 PNG 被拒、RGBA 透明图通过、宽高来自位图）。
3. **导入顺序**：`import_files` 按调用方提供顺序编 source_order；文件夹收集经 `collect_image_files` 自然排序后作为提供顺序（`test_folder_collection_uses_natural_order`）。
4. **方向继承规则**：paged 章节在 webtoon 书（默认 vertical）下回落 rtl 而非非法继承——D03 §4.4 的实现解释，已在测试固化。

## 复审建议

重放两条 pytest 命令；重点：① `application/importing/images/service.py` 的失败顺序（hash→decode→copy→commit）与 AC-IMPORT-003 一致性；② 领域方向不变量是否与 D03 §4.4 等价；③ 契约消费侧定义（边界 1）是否接受为 TASK-007 范围内的正确形态；④ favorite/archive 与 Tag 的隔离测试充分性。

## 风险与遗留

1. 持久化尚未接 SQLite：契约 fake 不能证明真实事务/迁移行为（见 NOT_RUN 第一条）——这是本切片最大的已知边界。
2. `Page.review_state/overall_status/page_locked` 已建模但本切片无消费方（属 Pipeline/UI 后续切片）。
3. 导入去重目前限同 Chapter 范围（`existing_source_hashes(chapter_id)`）；跨书架去重策略属产品决策，未获授权前不实现。
