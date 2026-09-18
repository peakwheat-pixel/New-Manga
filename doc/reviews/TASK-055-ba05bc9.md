---
task_id: TASK-055
reviewer: 独立子代理（ZCode 会话内新开子对话，与作者不同对话；窗口条款 §8.2 口径）
author: ZCode
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
reviewed_head: ba05bc9
decision: changes_requested
started_at: 2026-09-19 02:02:41 +0800
superseded_by: 修订 c175657 复审（见 doc/reviews/TASK-055-c175657.md）
---

# Review：TASK-055 日志与诊断（TASK-021 冻结子集①）

独立子对话 Review（开始时间 2026-09-19 02:02:41 +0800，reviewer=独立子代理，与作者不同对话）

> 编者注（作者落盘）：以下为独立子代理报告原文；作者仅添加 frontmatter 与本注。修订处置见 Handoff「追加登记」与修订复审报告 [TASK-055-c175657.md](TASK-055-c175657.md)。

## 固定对象

- worktree：`G:/CODEX/New Manga.worktrees/TASK-055-zcode`（分支 `agent/zcode/TASK-055-diagnostics`，review 期间 `git status --short` 为空，全程未修改、未 commit、未 push）
- base：`8bf8da3`（开工 merge master `aaef5f2`，含 TASK-046/TASK-054）；reviewed_head：**`ba05bc9`**（实现 `7f13e53` + 文档 `ba05bc9`）
- 依据：`doc/tasks/TASK-055.md`（AC ①–⑥ 与允许/禁止范围）、`doc/handoffs/TASK-055-7f13e53.md`、`doc/09_COLLABORATION.md` §6、`doc/templates/REVIEW.md`、`verification/TASK-055/`

## 范围与依据

完整 diff `aaef5f2..ba05bc9`（13 文件，+772/−3）逐文件核对写集合：Task、Handoff、`src/application/maintenance/diagnostics.py`、`src/infrastructure/filesystem/bounded_log_store.py`、`tests/diagnostics/**`（conftest+2 测试文件）、`verification/TASK-055/full-suite-run{1..5}.log`，全部落在允许范围。禁止范围核对：无 requirements 改动、无 Schema/migration、未触碰 `AGENTS.md`/其他 Task/`src/ui/qml/**`/bootstrap、无放宽断言、无新增 skip（0 skipped 佐证）、无 push。

**发现 1 个写集合内意外产物**：`doc/handoffs/TASK-055-`（0 字节空文件）被提交（见 R-002）。

### 依赖零改动

`git diff aaef5f2..ba05bc9 -- requirements.txt requirements-dev.txt` 输出为空（0 行）✓。新代码 import 面：`diagnostics.py` 仅 json/re/collections.deque/dataclasses/typing；`bounded_log_store.py` 仅 threading/pathlib —— 全部 stdlib，零新依赖 ✓。

## Architecture 面（executed）

- **依赖方向**：`QML/UI → Application → Domain/Ports → Infrastructure` 无反向。`diagnostics.py` 零 infrastructure import（grep 证实）；Protocol 端口 `DiagnosticsSnapshotProvider`/`DiagnosticsBundleSink` 定义在 application 侧，方向正确 ✓。
- **实现纯度**：`bounded_log_store.py` 只做轮转/裁剪/并发串行化，不含业务策略 ✓；`src/infrastructure/network/diagnostics.py`（既有，连接阶梯诊断 DNS→TCP→TLS→HTTP）与新报告组装是不同概念，无重复实现 ✓。
- **端口位置惯例偏差（R-003）**：仓库 8 处先例将子域端口集中放在 `ports.py`（含同目录既有 `src/application/maintenance/ports.py`），本实现把 Protocol 内联在 `diagnostics.py`。方向正确、仅位置惯例偏差。
- **保护纪律（R-006）**：`BoundedLogStore` root 由调用方给定，代码不强制「root 不在用户源文件区」——模块 docstring 与 sink Protocol docstring 均声明该约束归装配方。对照同目录 `maintenance/ports.py` 的 trash 用例（trash 同样靠 docstring+类型而非运行时强制），本仓库既有口径即「边界由装配层保证」。当前生产不可达（装配 NOT_RUN 如实登记），**评估：可接受，但装配切片必须以测试钉住 root ⊆ data_root 下 log 目录**，此项列为装配切片前置要求。报告内容为白名单式调用方摘要，结构性不含用户源文件内容 ✓。

## Verification 面（executed，含 Reviewer 独立执行的命令与输出）

环境：venv `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` + `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider` + **`QT_QPA_PLATFORM` 未设**（已 echo 确认 unset）。

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 定向套件 | `pytest tests/diagnostics -q -p no:cacheprovider` | `ba05bc9` | **PASS**：19 passed / 0 skipped，EXIT=0 | 会话输出 |
| 全仓复跑 ×2（reviewer 独立） | `pytest -q -rs -p no:cacheprovider` | `ba05bc9` | **PASS** ×2：870 passed / 0 skipped，EXIT=0（42.82s / 41.60s） | 会话输出 |
| 作者日志对照 | 读 `verification/TASK-055/full-suite-run{1..5}.log` | `7f13e53` | 5/5 均 870 passed / 0 skipped / EXIT=0，与复跑一致 | 日志文件 |
| 基线不减少（AC ⑤ 算术） | `git archive aaef5f2` 导出纯树至 TEMP 后全仓 pytest | `aaef5f2` | **PASS**：851 passed / 0 skipped，EXIT=0；870 = 851 + 19 成立 | TEMP 树（已清理） |
| 相邻面 | `pytest tests/storage tests/core -q` | `ba05bc9` | **PASS**：72 passed / 0 skipped，EXIT=0 | 会话输出 |
| 脱敏探针（TEMP 一次性脚本，已删除） | 键名/值形/透传/注入四组 | `ba05bc9` | 见下 | 探针输出 |
| 有界性探针（TEMP 一次性脚本，已删除） | 30 条 append + 并发 4×50 | `ba05bc9` | 见下 | 探针输出 |

**脱敏探针结果**（独立验证，非引用作者测试）：键名 `api_key`/`API-KEY`/`apikey`/`token`/`auth_token`/`session_token`/`db_password`/`passwd`/`credentials`/`authorization` 全部 → `[redacted]` ✓；值形 `Bearer ...`/`sk-...` 遮蔽 ✓；普通 URL/路径（`https://api.example.com/v1`、`D:/MangaData`、`http://127.0.0.1:7890`）原样透传 ✓；向 `settings_summary` 注入 5 个含 `sk-probe-secret-9f8e7d6c5b4a` 的键后 `to_json_bytes()` 输出 grep 不到该串（JSON 中 sk 形态串 = 0）✓。窄覆盖确认（Handoff 已声明 deliberately narrow）：`secretKey`（camelCase）、裸 `auth`、`pwd`、`SK-`大写、`sk_live_`、`ghp_` 不遮蔽（R-005）。

**有界性探针结果**：max_files=3、cap=50、append 30 条 → 文件数=3、total_bytes=96 有界、per-file 各 32B ≤ 50、存活文件名 == 创建序最后 3 个（prune 恒删最旧、名字序==创建序）✓；4 线程×50 行并发 append → 200 行、0 丢失、0 重复 ✓。

**字段清单探针结果（关键发现）**：导出 JSON `application` 段键 = `['app_version']`（**缺 `platform_python`**）、`database` 段键 = `['schema_version']`（**缺 `database_path`**）——见 R-001。

## AC ①–⑥ 逐条判定

| AC | 判定 | 依据 |
|---|---|---|
| ① 诊断包 | **FAIL（当前 head）** | 一键导出（`DiagnosticsService.export` 单调用）✓、脱敏 ✓（探针）、不含凭据/源文件内容 ✓；但 Handoff 写明的字段清单 `application（app_version, platform_python）`、`database（schema_version, database_path 显示路径）`与实际导出不符——`platform_python`/`database_path` 被丢弃（R-001）。Task 目标句「环境与路径摘要」中数据库路径亦缺失 |
| ② 日志边界 | **PASS** | 落盘策略/上限/轮转/裁剪实现并有界（探针+8 例）；单行超 cap 例外与 `_stamp_of` 等宽前提已在 Handoff 风险段声明 |
| ③ 错误码口径 | **PASS（带注）** | `RecentError.code` 为 str 透传承载字段，未新造错误码体系 ✓；但 Handoff/测试所举 `IMPORT_FILE_MISSING` 在 `aaef5f2` 全仓不存在（既有 typed 码集中于 `src/ports/network/transport.py`、`src/ports/providers/errors.py`），示例码非真实既有码（R-007） |
| ④ 白名单收紧 | **PASS** | 实际落地三路径（`src/application/maintenance/diagnostics.py`、`src/infrastructure/filesystem/bounded_log_store.py`、`tests/diagnostics/**`）真实存在（已核实），收紧记录在 Task「交付与运行记录」与 Handoff「边界」段 |
| ⑤ 不回归+判别力 | **PASS** | 新能力无修前行为、声明不适用（诚实）；基线 851（独立验证）→ 870 不减少；作者 ×5 + 复跑 ×2 全部 870/0 EXIT=0；无新增 skip；未设 QT_QPA_PLATFORM。注：判别力缺口伴随 R-001（roundtrip 测试未断言缺失字段） |
| ⑥ Handoff/证据/Review/集成 | **PARTIAL（按流程预期）** | Handoff ✓、`verification/TASK-055/**` ✓、本独立子对话 Review ✓；集成与 STATUS 台账行属集成后步骤（Task status 仍 `in_progress`，如实）。**NOT_RUN 诚实性：PASS**——Handoff 明列「生产可达（装配）NOT_RUN（bootstrap 未注入）」，未掩盖 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `src/application/maintenance/diagnostics.py:89–99`（`to_dict`） | 任何导出/JSON 序列化即触发：`to_dict` 将 `application` 硬编码为仅含 `app_version`、`database` 硬编码为仅含 `schema_version`，并过滤掉 sections 中同名两段，导致 `platform_python` 与 `database_path` 永不出现在导出 JSON。与模块自身 docstring、Handoff 字段清单、Task 目标三处自述矛盾；AC ① 关键字段缺失，且 roundtrip 测试未断言这两键，钉不住 | 探针第 4 节：application 段键只有 app_version、database 段键只有 schema_version；`platform_python in JSON: False`、`database_path in JSON: False` | to_dict 中 application 段补 platform_python、database 段补 database_path（从 sections 或提升为 dataclass 字段），并在 roundtrip 测试补两键断言；修后由新独立子对话复审新 head | open |
| R-002 | P2 | `doc/handoffs/TASK-055-`（0 字节） | 笔误产物被提交进 `ba05bc9`，污染 handoffs 目录 | `git diff --name-status` 显示新增 `doc/handoffs/TASK-055-`；文件大小 0 | 集成前删除（或集成 cherry-pick 时剔除） | open |
| R-003 | P3 | `diagnostics.py:171,189` | Protocol 内联在 `diagnostics.py`，与 8 处既有「子域端口集中 `ports.py`」惯例（含同目录 `maintenance/ports.py`）不一致；无行为影响 | grep `Protocol` 于 `src/application/**/ports.py` 先例 | 集成或后续小提交归位 `maintenance/ports.py` | deferred |
| R-004 | P3 | `diagnostics.py:22` | `Callable` 导入未使用 | grep 全文仅 import 行命中 | 移除 | open |
| R-005 | P3 | `diagnostics.py:32–42` | 防御脱敏不覆盖 camelCase `secretKey`、裸 `auth`、`pwd`、`SK-`大写、`sk_live_`、`ghp_` 等 | 探针第 1/2 节输出 | Handoff 已声明「deliberately narrow」且主防线为白名单结构性排除；保持现状可接受，可在装配切片按需扩宽 | deferred |
| R-006 | P3 | `bounded_log_store.py:7–8`、`diagnostics.py:189–192` | root/落盘位置不强制排除用户源文件区，仅 docstring 声明、归 sink 实现；与 trash 用例同为本仓库「装配层保证」口径，且当前生产不可达（NOT_RUN） | 源码注释自述「enforcing that is the sink implementation's job」 | **装配切片前置要求**：注入时以测试钉住 root ⊆ data_root 下 log 目录 | deferred（附前置） |
| R-007 | P3 | `test_report.py:156`、Handoff 验证表 AC ③ 行 | 示例码 `IMPORT_FILE_MISSING` 在 `aaef5f2` 全仓不存在（`git grep` 零命中），非真实既有 typed 码；另有 `DiagnosticsSnapshotProvider.recent_errors()` 在 Service 中未被使用（`DiagnosticsService.export` 用 `_errors.recent()`）；`test_report_is_frozen` 用 `pytest.raises(Exception)` 过宽 | `git grep -c IMPORT_FILE_MISSING aaef5f2 -- src` 零命中 | 示例改用真实码（如 `PROVIDER_AUTH_FAILED`/`TRANSPORT_FAILED`）或 Handoff 措辞改「占位示例」；清理死 Protocol 方法与宽捕获 | open |

## 结论与复审

**Architecture 面**：PASS——分层与依赖方向正确，端口在 application 侧，无 infrastructure 反向依赖，基础设施文件纯实现；R-003/R-006 为惯例与装配前置项，不阻塞。

**Verification 面**：FAIL（仅因 R-001）——脱敏、有界性、基线算术、5 次稳定性全部独立复现通过；但 AC ① 写明字段清单与实际导出产物不符，属 P1。

固定 head `ba05bc9` **不可交 Codex 集成**：R-001（P1）未解决。R-002 顺手可修。修复方向明确（约数行 + 断言补齐），修后需**新开独立子对话**对固定新 head 复审（本结论不延用）。剩余风险：R-006 的 root 约束依赖装配切片兑现，已列为装配前置。

**decision: `changes_requested`**
