# TASK-019 集成验证：`3755af9`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `36242fb00f9f432ec66cc3c33afc167578d0f341`（代码基线） |
| reviewed head（delivery） | `726baf5` |
| 元数据 / 分支 head | `6c981c2` |
| Review 报告 commit | `7c635d5` → [`doc/reviews/TASK-019-726baf5.md`](../../doc/reviews/TASK-019-726baf5.md)（decision=`approved`，F-1～F-7） |
| implementation merge / integration commit | `3755af9`（merge，parents `7c635d5` + `6c981c2`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1` |

## 复验结果（master `3755af9`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/providers -q -p no:cacheprovider -rs` | 0 | **110** | **0** | `110 passed` | 无 |
| 2 | `…python.exe -m pytest tests/pipeline tests/core tests/storage -q -p no:cacheprovider -rs` | 0 | **78** | **0** | `78 passed` | 无 |
| 3 | `…python.exe -m pytest -q -p no:cacheprovider -rs`（全仓） | 0 | **640** | **6** | `640 passed, 6 skipped`；较集成前基线 530 增加 110，全部为本 Task 新增 | 6 项全部位于既有 `tests/network`：`openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`） |
| 4 | **独立装配验证**（Reviewer 自写脚本，`%TEMP%`，不经作者测试）：`bootstrap.app.assemble_services(tmp/app.db, tmp/managed)` → `providers.status()` | 0 | — | — | 真实装配成功；12 个 Provider：`ready` 2（`inpaint-simple-fill`/`inpaint-edge-bleed`）、`missing_dependency` 2（`manga-ocr`/`paddleocr-korean`）、`not_configured` 4（`openai-vision-detection`/`openai-vision-ocr`/`openai-compatible-translation`/`sakura-local`）、`not_ready` 4（四条学习型修复路线，均 `PROVIDER_NOT_IMPLEMENTED`）；GPU `unavailable` / `DEVICE_UNAVAILABLE` |
| 5 | 离线与替身边界 | — | — | — | `rg "socket\|urlopen\|requests\.\|http\.client" tests/providers` 无真实网络调用；替身仅用于集成语义，未作为端点或质量证据 |

## 验收结论

- [x] 非作者独立 Review 已完成并绑定固定 base/head；结论 `approved`，findings F-1～F-7 已在 Task 文件登记处置。
- [x] 集成后三条命令通过，pass/skip 分列；6 项 skip 均为既有 `openssl unavailable`，与本次变更无关。
- [x] 生产装配独立验证通过：缺 `torch`/`numpy`/OCR 运行时下不崩（AC-OPTIONAL-001）；四条学习型路线 fail-closed **未回落**到基线（与 TASK-018 R-007 口径一致）；GPU 不可用如实报告（无伪造执行）。
- [x] 白名单：作者改动 56/56 全部在允许范围内、禁止路径 0；`git diff --check` 无输出；未改依赖清单、Schema、pipeline seam 本体、`AGENTS.md`。
- [x] 未 push。
- [ ] **AC-RFULL-001 完整链仍 `BLOCKED`**（缺 `color`/`term_extract`/`render` handler，见 F-2；另受 F-1 影响）；真实模型质量/成本/时延、真实权重下载、真实 Sakura 服务验证仍 `BLOCKED`/`NOT_RUN`——**不得视为通过**。

## 未关闭项

| ID | 级别 | 内容 | 归属 |
|---|---|---|---|
| F-1 | **P0（既有，跨 Task）** | 新建 Region 默认 `sfx_policy='skip'` + planner 不检查 `region_type` → 真实默认下整条链路被 `SKIP_POLICY` 跳过 | 待用户/Codex 裁决后作为独立 Task 释放；涉及 `domain/`、`application/tasks`、`application/editing`、`infrastructure/sqlite/schema.py`、`tests/pipeline` |
| F-2 | P2 | AC-RFULL-001 的 `color`/`term_extract`/`render` handler | 后继切片，需用户批准释放并明确允许路径 |
| F-4 | P2 | 彩色/高复杂度场景不降级的产品取舍 | 用户裁决 |
| F-5 | P3 | 页级 mask artifact 与 Region 一对多 | Schema / D03 §16 裁决 |
| F-6 | P3 | prepare-only 残余并发窗口 | 需 seam 提供"内容+指针同事务"入口 |
