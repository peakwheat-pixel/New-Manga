# FEAT-CREATE-2 AC 证据摘要

- Task：`FEAT-CREATE-2`
- Implementation commit：`5cb28a7059b547c9080ad89c0a14fa95cd95bf19`
- Tested commit：`5cb28a7059b547c9080ad89c0a14fa95cd95bf19`
- Test command：`python -m pytest tests/core -q -p no:cacheprovider`
- Environment：PowerShell；`C:\Python314\python.exe`；Python 3.14.6
- Result：`535 passed, 0 skipped, 1 warning`；exit code `0`。Task 基线为 515，净增 20 个通过用例。

| AC | Result | Evidence / basis |
|---|---|---|
| AC1 | PASS | `core_service.py` 实现 CreateBook/CreateChapter 的闭合 payload 校验、Unicode 空白拒绝、minor 8 门控和冻结错误映射；没有最大长度限制。反例覆盖未知字段、缺失/错型/空白字段。 |
| AC2 | PASS | 使用既有 `books`/`chapters` 表和 `CoreServices.library`；未增加 Schema、迁移或依赖。两条单行写入复用 `SqliteLibraryRepository` 的事务；主键冲突测试确认失败返回 `LIBRARY_WRITE_FAILED` 且表中无半成品。 |
| AC3 | PASS | 成功响应白名单只含 `BookSummary` / `ChapterNavSummary` 字段；错误 envelope 不含 `message`、输入值或原始异常。未知字段测试包含路径哨兵并断言不回显。 |
| AC4 | PASS | 在 `core_service` 分发新增两个命令，仅接受 major 2/minor 8；`CoreServices` 已由 `core_assembly` 装配现有 `LibraryService`，新 handler 复用该注册；ListBooks 的旧 2.3 读取面回归断言通过。 |
| AC5 | PASS | 新增 20 个创建命令用例，包含重复作品标题/章节标题与编号正例、未知字段/空白/错型/父作品不存在或已删除反例、2.8 门控和主键冲突原子性。全量 `tests/core` 为 535 passed。 |
| AC6 | PASS | 本证据摘要、全量测试日志及 Handoff 已归档；最终 Task 状态更新为 `in_review`。 |

唯一 warning 来自未改动的 `tests/core/test_rc4_stdio_render_preview.py:245`，内容为 Pillow `Image.getdata` 的弃用提示；没有 skip。
