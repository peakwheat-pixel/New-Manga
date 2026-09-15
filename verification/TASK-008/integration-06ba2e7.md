# TASK-008 Codex 集成验证

日期：2026-09-15（Asia/Shanghai）
任务：TASK-008 Region 编辑、Revision 与人工保护
基线：`f129ae96900fb567288f91a78d55c0ff4ecafe6d`
Review 对象：`reviewed_head=1f373ac2240fb5fc6304e447b7d0fd873310aef1`
Review 报告提交：`f9e59770e7617744178b0f56fc10af558a416298`
集成提交：`06ba2e7322e5f565feda1808094e9edd282b3c0b`

## Git 集成

- 主工作区为 `G:/CODEX/New Manga`，分支为 `master`，集成前工作区干净。
- ZCode 分支 `agent/zcode/TASK-008-region-editing` 以 `--no-ff` 合并，产生实现集成提交 `604ca6deedc1fb26b5bf42ddf4665d871835c42d`。
- DeepSeek Harness 分支 `agent/deepseek/TASK-008-review` 以 `--no-ff` 合并，产生 Review 集成提交 `06ba2e7322e5f565feda1808094e9edd282b3c0b`。
- Review 报告 `doc/reviews/TASK-008-1f373ac.md` 的 front matter 为 `reviewed_head=1f373ac2240fb5fc6304e447b7d0fd873310aef1`、`decision=approved`；报告提交 `f9e5977` 的父提交为 `f7becb4`，与 ZCode 分支头一致。
- `1f373ac..f7becb4` 仅包含 Handoff、Task 元数据和作者验证，不包含源码或测试变化；分支与两个 linked worktree 保留供审计。

## 集成后验证

执行环境：Windows；`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`；Python 3.12.3；pytest 9.1.1。

| 检查 | 命令 | 结果 |
|---|---|---|
| TASK-008 编辑套件 | `python -m pytest tests/editing` | PASS，17 passed，退出码 0 |
| 全量回归 | `PYTHONPATH=src python -m pytest tests` | PASS，79 passed，退出码 0 |
| reviewed head 到分支头 | `git diff --name-status 1f373ac f7becb4` | PASS，仅 3 个交付元数据文件 |
| 集成范围 whitespace | `git diff --check f129ae9 06ba2e7 --` | PASS，退出码 0 |

## Review Findings disposition

- **R-201：noted / deferred**。合并后的 Region 保留最强人工锁，但两个已确认源合并后 `edited_confirmed` 不自动继承；不阻塞本切片，后续产品语义裁决时明确确认态继承规则。
- **R-202：noted / deferred**。拆分后的 parts 使用源 `reading_order + index`，可能与既有 Region 重叠；不阻塞本切片，后续编辑器切片考虑归一化。

## 未执行项与边界

SQLite Region/Revision Repository 与 schema 扩展、StepResultCandidate 落库、Page Lock 消费、完整 TextStyle、UI/autosave 计时器和性能验证均为本切片范围外的 `NOT_RUN` / `N/A`，不因本次集成测试通过而改标 PASS。

后续建议：单独协调统一 SQLite 持久化落地切片，明确 TASK-006/007/008 三个消费侧契约的收敛方式；该建议不释放新的 Task，也不扩大 TASK-008 范围。
