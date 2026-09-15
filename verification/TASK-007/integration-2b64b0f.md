# TASK-007 Codex 集成验证

日期：2026-09-15（Asia/Shanghai）
任务：TASK-007 书架领域与本地图片导入
基线：`6b123fe55f2e6373335b044fc5e5f169b5d108e0`
Review 对象：`reviewed_head=6ea4dd9241c0a24f60964b570cb768bb48dfa0f3`
集成提交：`2b64b0f7e419d8179633bd86928a49195b09414e`

## Git 集成

- ZCode 实现以 `--no-ff` 合并，产生实现集成提交 `f69de2f`。
- DeepSeek Harness approved Review 报告以 `--no-ff` 合并，产生 `2b64b0f`。
- Review 报告为 `doc/reviews/TASK-007-6ea4dd9.md`，未修改。
- F-01～F-03 的收口修改属于用户明确允许的 TASK-007 集成范围；F-04 仅记录端口位置规则，未迁移代码。

## 实际验证

执行环境：`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`，Python 3.12.3，Windows。

| 检查 | 命令 | 结果 |
|---|---|---|
| TASK-007 library | `python -m pytest tests/library` | PASS，25 passed，退出码 0 |
| 全量回归 | `PYTHONPATH=src python -m pytest tests` | PASS，62 passed，退出码 0 |
| 原 Review 范围 whitespace | `git diff --check 6b123fe 6ea4dd9 --` | PASS，退出码 0 |
| 收口后 whitespace | `git diff --check` | PASS，退出码 0 |
| Task 范围 | 集成差异、F-01～F-03 与文档收口路径核对 | PASS；未修改其他 Task、Provider、QML、打包或 CI |

## Finding disposition

- F-01：**resolved**。删除无调用且无法接收未设置字段的 `Chapter.with_inherited_defaults`；方向继承只保留 application service 的实际路径。
- F-02：**resolved**。更正服务重启测试名称/注释，并覆盖 Book 默认 `ltr` 到 paged Chapter 的继承。
- F-03：**resolved**。测试辅助模块将 PySide6 导入延迟到 Qt 解码与 PNG 工厂使用处。
- F-04：**deferred**。application consumer-side Protocol 留在 `src/application/**/ports.py`；共享 infrastructure/repository ports 留在 `src/ports/repositories/**`。SQLite adapter 前由后续获批 Task 统一或明确映射。

## 未执行项

SQLite BookRepository 真实落地、Schema/迁移、生产 ImageDecoder 装配、UI、PDF/MOBI/网页导入、性能/容量、打包与产品级验收均为 `NOT_RUN` / `N/A`，不因本次集成测试通过而改标 PASS。
