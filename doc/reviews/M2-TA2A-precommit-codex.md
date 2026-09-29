---
task_id: M2-TA2A
reviewer: Codex subagent（非变更作者；补充只读审查）
author: Codex Desktop
base_commit: eb41a352c03df84400d90a78c29d2dfbe28a76c9
reviewed_head: 642b559beff535b005c3e644d732e500ba2122ca
decision: approved
---

# Review：M2-TA2A 当前工作树快照

## 范围与依据

2026-09-29 在 `C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga` 审查。`reviewed_head` 是审查时的 HEAD，**实现仍未提交**：当时约 87 个 staged 路径、7 个 unstaged 路径，另有 `verification/M2-TA2A/integration-checks.log`、`source-audit.md` 未跟踪。审查覆盖 `assets.py`、JA manifest/inventory、ignore 规则、`tests/m2_test_assets`、README、Task、来源与运行记录，以及相关调用点。当前结论仅对所读工作树代码快照有效；正式固定交付 commit 和本报告之后的文档修改须由独立 DeepSeek Harness 复审。

## Architecture

**APPROVED（当前代码快照）**。改动处于 Task 允许的测试资产、测试、验证和 Task 文档路径；未见生产 Schema、migration、Pipeline、Provider、UI 或依赖锁变更。Git index 未跟踪漫画图像/ZIP；JA 原始媒体命中本地 ignore，76 个 XML/许可文本是明确白名单。公开页下载限制 HTTPS 官方域及重定向，路径/ZIP 条目/大小/CRC 有边界检查，已有文件不会静默覆盖。Manga109 无授权时保持 gated 状态。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `verification/M2-TA2A/run-results.md:7,18,20,30` | 审查时运行摘要仍称 `19 passed`、`INVENTORY verified=88` 和不存在的 source-group checksum；新代码与新日志实际为 `21 passed`、`INVENTORY checked=88 missing=0 failures=0`、仅逐文件哈希。交接阅读者会误解最新验证口径。 | 本次 `pytest` 为 21 passed；JA smoke `verify` 输出 `checked=88 missing=0 failures=0`；inventory 不含聚合 checksum。 | 在交付前同步运行摘要，并引用最新 raw log。 | open；主线程正在更新，未复审其后修改 |

未发现 P0/P1。`status(case)` 单独调用不会自动读取 inventory，但仓库外暂无调用方；当前 CLI 的 `verify/list/missing` 均先校验并传递异常路径，因此此点是后续 Loader 接入时须保持的调用约束，当前不列为阻断 finding。

## Verification

| 场景 | 命令或步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 资产测试 | `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/m2_test_assets -q -p no:cacheprovider` | Windows PowerShell / Python 3.14；HEAD `642b559b` + dirty diff | PASS：21 passed，EXIT 0 | 本次 Reviewer 实际 stdout；作者最新 raw log 见 `verification/M2-TA2A/integration-checks.log` |
| JA L0 文件 | `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke` | 同上 | PASS：10 READY；inventory checked=88、missing=0、failures=0；EXIT 0 | 本次 Reviewer 实际 stdout |
| 哈希漂移影响 CLI | 在 `TemporaryDirectory` 构造完整 manifest/inventory，保持 JPEG 和 SVG ZIP 格式合法，只改变 ZIP 文本后调用 `assets.main()` 的 `list`、`missing`、`verify` | 同上；临时目录，不修改仓库资产 | PASS：三个命令均为该 Case 输出 `PARTIAL`，EXIT 1，未输出 READY | 本次 Reviewer 实际 stdout：三行均 `EXIT 1 PARTIAL True READY False` |
| inventory 覆盖 | 对 10 个公开页的 20 个 JPEG/ZIP 路径逐一比对 inventory | 同上 | PASS：20/20；inventory 共 88 个唯一文件 | 本次 Reviewer Python 只读检查 |
| Git 原图边界 | `git ls-files test_assets/comic_golden_suite | rg -i '\\.(jpg|jpeg|png|webp|zip|cbz)$'` | 同上 | PASS：无跟踪媒体；EXIT 1 是 `rg` 无匹配，包装检查输出 `NO_TRACKED_MEDIA` | 本次 Reviewer 实际 stdout |
| 应用 Pipeline | OCR、检测、翻译、消字、排版等 | 本 Task 未执行 | NOT_RUN | README/Task/运行记录均按资产 READY 与 Pipeline 状态分离 |

## 结论与复审

当前代码快照 **APPROVED**，R-001 属交付文档 P2，合入前需完成同步。此批准不等同于固定交付 commit 的治理批准；DeepSeek Harness 仍须审查固定实现 HEAD，Codex 仍须在主工作区完成集成验证。后续任何实现或文档修改均不由本次快照批准自动覆盖。
