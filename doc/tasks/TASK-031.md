---
id: TASK-031
title: 生产 ImageDecoder 与 Managed Copy 适配器
kind: implementation
status: in_review
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [TASK-006, TASK-007, TASK-029]
base_commit: 29b146f76b46682c6e9de3c40631fd7a5debed16
branch: agent/codex/TASK-031-production-import-adapters
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-031：生产 ImageDecoder 与 Managed Copy 适配器

## 授权与目标

2026-09-16，用户授权实现此前阻塞 TASK-030 的两个生产依赖；授权仅覆盖本 Task 白名单，不释放 TASK-030，不启动 TASK-013/TASK-015 或其他冻结 Task。目标是让现有 `ImageDecoder` 与 `ManagedCopyStore` Protocol 有可审查的 Windows/PySide6/ManagedFileStorage 生产实现，供后续入口装配使用。

## Acceptance Criteria

- [x] `G:/CODEX/New Manga/src/infrastructure/importing.py` 提供 `QtImageDecoder`：用 PySide6 Qt image plugin 解码，返回实际宽高与 MIME；损坏/不可解码 bytes 抛 `ImageDecodeError`。
- [x] 同一文件提供 `ManagedCopyStoreAdapter`：由 `book_id_for_chapter` resolver 补齐 D03 路径所需的 `book_id`，通过既有 `ManagedFileStorage` 完成 temp 写入、Hash 校验、不可覆盖 publish；返回 `books/{book_id}/chapters/{chapter_id}/original/` 相对引用，不修改源文件。
- [x] 生产两个适配器驱动现有 `ImportImagesUseCase`，并证明 copy 成功后才有 Page、copy 内容逐字节等于输入、完整性失败不留 temp/original 孤儿。
- [ ] 保持 `src/application`、`src/domain`、Protocol、Schema、依赖清单、`src/bootstrap`、`src/ui` 与冻结 Task 不变；独立 Review 和 Codex 集成复验完成前不得置 `done`。

## 允许修改范围

- `G:/CODEX/New Manga/src/infrastructure/importing.py`
- `G:/CODEX/New Manga/tests/library/test_production_adapters.py`
- `G:/CODEX/New Manga/doc/tasks/TASK-031.md`
- `G:/CODEX/New Manga/doc/handoffs/TASK-031-*.md`
- `G:/CODEX/New Manga/verification/TASK-031/**`
- Codex 仅可按协作协议维护 `G:/CODEX/New Manga/doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md` 的状态/导航/链接。

## 禁止范围

不得修改 `src/ui/qml/Main.qml`、`src/bootstrap/app.py`、`src/application/**`、`src/domain/**`、`src/ports/**`、Schema/migration、依赖清单、`AGENTS.md`、TASK-012 已审实现、TASK-030 业务实现、TASK-013/TASK-015 或其他 Task。不得 push、不得使用测试 fake 作为生产实现、不得绕过 Managed Copy。

## 测试要求

| 场景/AC | 命令 | 环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| Qt 解码 + Managed Copy 适配器 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/library/test_production_adapters.py -q` | Windows；Python 3.12.3；PySide6 6.11.2；默认 Qt | `6 passed, 0 skipped` | [author-verification-c67a105.md](../../verification/TASK-031/author-verification-c67a105.md) |
| 现有 library/import 回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/library -q` | Windows；默认 Qt | `38 passed, 0 skipped` | [author-verification-c67a105.md](../../verification/TASK-031/author-verification-c67a105.md) |
| TASK-030 入口 smoke | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test` | Windows 默认 Qt；不设置 offscreen | `BLOCKED`，本 Task 不装配入口 | 由 TASK-030 执行 |
| `tests/ui_shell -v` | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | Windows 默认 Qt | `46 passed, 0 skipped`；本 Task 未修改 UI | [author-verification-c67a105.md](../../verification/TASK-031/author-verification-c67a105.md) |
| 全量 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | Windows | `374 passed, 6 skipped`；6 项均因 `openssl unavailable` | [author-verification-c67a105.md](../../verification/TASK-031/author-verification-c67a105.md) |

所有结果中的 `passed` 与 `skipped` 分列；没有 skip 时仍写 `0 skipped`。未执行项保持 `NOT_RUN`/`BLOCKED`/`N/A`，不得用局部通过替代入口集成证据。

## 依赖、风险与阻塞

- TASK-006 提供 D03 固定目录、temp、hash 与不可覆盖 publish；TASK-007 提供 import Protocol/use case；TASK-029 提供后续装配可用的统一 SQLite library adapter。
- `ManagedCopyStore` 当前只传 `chapter_id`，不扩充共享 Protocol；本 Task 要求入口装配提供 `book_id_for_chapter` resolver，避免伪造或硬编码 book 层级。
- 本 Task 不负责把适配器接入 `Main.qml`/`bootstrap/app.py`；TASK-030 在独立 Review、集成和真实入口验证前继续保持 BLOCKED/未释放。

## 交付与运行记录

- Handoff：[TASK-031-c67a105](../handoffs/TASK-031-c67a105.md)，delivery_head=`c67a105`。
- Review：尚无；Reviewer=`DeepSeek Harness`，不得自审冒充批准。
- 实现提交：`c67a105`（`feat(TASK-031): add production image import adapters`）。
- integration_commit：null。
