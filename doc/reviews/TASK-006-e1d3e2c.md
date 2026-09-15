---
task_id: TASK-006
reviewer: DeepSeek Harness
author: ZCode
base_commit: fb29dfedc496cde61cea9ea2558ef274e94eb49e
reviewed_head: e1d3e2c99116d9b65140b0ae64a2188555f3c791
decision: approved
---

# Review：TASK-006 复审（e1d3e2c）

本报告是 [首次 Review](TASK-006-ba1e769.md)（decision=`changes_requested`）的复审，只覆盖 `fb29dfe..e1d3e2c`。`ba1e769` 已拒，其 Handoff 结论不再有效。未修改被审实现、测试或验证脚本，未触碰 ZCode worktree；本报告是 Reviewer 新增的唯一文件。

## 范围与依据

**固定对象**：`base_commit = fb29dfe`、`reviewed_head = e1d3e2c99116d9b65140b0ae64a2188555f3c791`；作者分支 `agent/zcode/TASK-006-persistence-artifact`（`ba1e769` → `1e695af` → **`e1d3e2c`** → `af6deef` 元数据，后者不在被审范围）。

**变更**：`git diff --stat fb29dfe e1d3e2c` = 22 路径、`+2118/−16`；修订增量 `ba1e769..e1d3e2c` = 14 路径、`+295/−38`（源码 8 文件 + 测试 4 文件 + Task/Handoff/证据）。全部落在 TASK-006 `allowed_paths`；`src/domain`、`src/ui`、`src/bootstrap`、`tests/core`、依赖清单、AGENTS、STATUS、D03、D08、其他 Task、TASK-005 代码 **零触碰**。

**Reviewer 环境**：Windows `10.0.26200`；Reviewer venv（Python `3.12.3`）与系统 Python `3.14.6`；一次性 detached 检出 `%TEMP%/nm-task006-e1d3e2c`（审查后已移除）；2 组独立探针（临时目录）。

## R-101～R-106 逐条 disposition 确认

| ID | 原级别 | 处置 | Reviewer 独立确认 |
|---|---|---|---|
| R-101 | P1 | **fixed** | 新增 `ARTIFACT_TYPE_DIRS` 显式映射（10 类型）并补 `books/` 层级；`export` 落 book 级 `books/{book_id}/exports/`；未知类型抛 `ValueError`；两处 docstring 已同步。**独立 10 类型探针全部 OK**：`original→original`、`thumbnail→thumbnails`、`mask→masks`、`clean→clean`、`translated→translated`、`render_preview→previews`、`detection_overlay→previews`、`debug_ocr/debug_detection→debug`、`export→books/BK1/exports/RV1.png`；全部章节类路径形如 `books/BK1/chapters/CH1/<D03 目录>/RV1.png`，目录名全部落在 D03 §18 的固定集合 `{original,masks,clean,translated,thumbnails,previews,debug}` 内；`sticker` 等未知类型被拒绝。作者新增 `test_revision_paths_follow_d03_layout` 与我的探针结论一致 |
| R-102 | P2 | **fixed** | 删除契约外码：`CommitStatus.TARGET_NOT_FOUND` + `error_code="TARGET_NOT_FOUND"`，复用契约 §10 既有码（`TARGET_NOT_FOUND / TARGET_DELETED`）。独立检索确认源码中已无 `ARTIFACT_NOT_FOUND`；测试断言同步 |
| R-103 | P2 | **fixed（登记）** | `artifacts.py` 模块 docstring 由「follows the frozen §8.1 sequence」改为明确「artifact current-pointer **子集**」，并逐项登记未实现部分与承接切片（Lock 重读→TASK-007/008 落库、TASK-011 消费；`StepResultCandidate`→TASK-011），且冲突仍以 Port 级结果返回、不建 candidate 行。差异已进入代码内唯一事实源，不再只存在于 Handoff 正文 |
| R-104 | P2 | **fixed** | `_split_statements` 改用 `sqlite3.complete_statement` 逐行累积。**独立验证**：v1 迁移在 Reviewer 探针中完整应用（`applied=1`），`sqlite_master` 中存在 `trg_media_artifacts_current_not_clearable` —— 含 `BEGIN...END` 体的触发器被完整执行，正是朴素 `split(";")` 会截断的场景；DB 内 `schema_migrations.checksum` 与 `default_migrations()[0].checksum` 一致 |
| R-105 | P2 | **fixed** | `backup_records.managed_path` 改为 `{backup_root.name}/{backup_id}.db`（如 `backups/{id}.db`），不再是裸文件名；测试 `test_post_schema_backup_is_recorded` 断言等值且可按相对路径解析到文件 |
| R-106 | P2 | **fixed** | 裁决为**由 DB 触发器负责**：v1 DDL 新增 `trg_media_artifacts_current_not_clearable`（`BEFORE UPDATE ... WHEN OLD 非空 AND NEW 为 NULL → RAISE(ABORT)`）。**独立双向探针**：A 首版 `current_revision_id=NULL` 合法 = True；B 首次提交 `committed` 且 current 非空；**C 清空已建立的 current 被拒**（`IntegrityError: media_artifacts.current_revision_id cannot be cleared once set`）；D 被拒后 current 仍为原 revision（状态未被破坏）；E 首版 NULL 的 artifact 之后仍能正常提交（路径 `books/…/chapters/…/masks/….bin`）；F `PRAGMA integrity_check = ok` |

**六项全部 resolved，无 unresolved、无 regressed。**

## 本轮新 findings

| ID | 级别 | 文件/行 | 问题 | 影响 | 复现 | 建议 | disposition |
|---|---|---|---|---|---|---|---|
| F-01 | P2 | `src/infrastructure/filesystem/managed_storage.py:24-35`（`ARTIFACT_TYPE_DIRS` 中 `"detection_overlay": "previews"`） | D03 §16.1 定义了 `artifact_type=detection_overlay`，但 §18 的固定目录集中没有对应目录；实现把它归入 `previews/`，与 `render_preview` 共用同一目录 | 两类语义不同的产物（检测覆盖图与渲染预览）落在同一目录，仅靠文件名区分；后续按目录枚举产物时无法区分二者。不影响 R-101 的"路径必须落在 D03 目录集内"结论，也不影响当前测试 | 阅读 `ARTIFACT_TYPE_DIRS`；对照 D03 §16.1 的 10 个类型与 §18 的 7 个目录名；探针输出 `detection_overlay -> .../previews/RV1.png` | 在 D03 §18 补充 `detection_overlay` 的目录归属（或在代码注释中写明"检测覆盖图按预览类产物归置"的理由），使映射有权威依据；不要求本 Task 再改代码 | open（非阻塞） |

P0 = 0，P1 = 0，P2 = 1（F-01），不阻塞集成。

## 验证

| 场景 | 命令或步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|
| 必需检查 1 | `git diff --check fb29dfe e1d3e2c --` | Git 2.52.0 | PASS，退出码 0 | 无输出 |
| 必需检查 2 | `git diff --stat fb29dfe e1d3e2c` | 同上 | PASS | 22 files changed, 2118 insertions(+), 16 deletions(−) |
| 必需检查 3 | `python -m pytest tests/storage`（任务命令字面） | 系统 Python `3.14.6` | **PASS，退出码 0，31 passed** | 一次性检出 `e1d3e2c` |
| 同命令（项目固定环境） | `python -m pytest tests/storage` | Reviewer venv Python `3.12.3` | **PASS，退出码 0，31 passed** | 与作者证据一致 |
| 全量回归 | `PYTHONPATH=src python -m pytest tests` | Python `3.12.3` | **PASS，退出码 0，37 passed**（core 6 + storage 31） | 与作者证据一致 |
| R-101 独立探针 | 10 类型 + 未知类型，对照 D03 §18 固定目录集 | Python `3.12.3` | **PASS** | 10/10 路径含 `books/` 前缀且目录落在 D03 集合内；`export` 在 book 级；未知类型 `ValueError` |
| R-104 独立探针 | 应用 v1 迁移并检查 `sqlite_master` 触发器与 checksum | 同上 | **PASS** | `applied=1`；触发器存在；DB checksum == 代码 checksum |
| R-106 独立探针 | 首版 NULL / 首次提交 / 清空 NULL / 状态不变 / NULL 后提交 / integrity_check | 同上 | **PASS** | 见上表 R-106 行 |
| 范围与越界 | `git diff --name-status fb29dfe e1d3e2c` 过滤 D03/D08/AGENTS/STATUS/其他 Task/TASK-005 代码/domain/ui/bootstrap/tests/core/requirements | 同上 | PASS | 0 命中 |
| 测试真实性 | 阅读 4 个测试文件的修订 diff | 同上 | PASS | 新增测试断言真实行为（路径字符串、`IntegrityError`、状态不变、相对路径解析），无 mock/monkeypatch 绕过 |
| WAL 多连接并发竞争 | 未执行 | — | **NOT_RUN** | 单连接切片；属 TASK-011 与集成验证 |
| v1→v2 升级链 / 迁移失败恢复端到端 | 未执行 | — | **NOT_RUN** | 当前仅 v1；端到端由 TASK-021 补足 |
| Restore / 清理对 current/pinned 的执行保护 | 未执行 | — | **N/A** | 属 TASK-021；本切片提供字段与备份入口 |
| 性能 / 大数据量、模型质量、打包、交互式 UI | 未执行 | — | **N/A / NOT_RUN** | 无对应 AC 或实现 |

## 三轴结论

**Spec**：首次 Review 的 P1（R-101）已按「改实现对齐 D03 §18」修复，10 个 artifact_type 全部映射到 D03 §18 的固定目录集并补齐 `books/` 层级，未知类型被显式拒绝，两处 docstring 与实际一致；R-102～R-106 均按 fixed（R-103 为登记式修复）落实。TASK-006 四条 AC 中 AC1～AC3 由实现与测试支撑，AC4（Handoff/非作者 Review/集成）由本次结论与后续 Codex 集成完成。未引入契约外错误码，未扩大产品范围。

**Architecture**：分层与依赖方向不变（`ports` 纯 stdlib、`infrastructure → ports` 单向）；`ManagedFileStorage` 的布局策略现在集中在单一映射表，未知类型拒绝生成目录外路径，这一改动同时把「布局不得分叉」变成可实现约束。R-106 选择 DB 触发器而非应用层守卫是正确取舍——应用层无法阻止直接 SQL，而复合 deferred FK 在 NULL 方向按 MATCH SIMPLE 不可见；触发器把 §2.1 的「不得改变已建立的 current」下沉到数据库本身，且不影响首版 NULL 与正常提交流程（探针 E 已证）。R-104 的 `complete_statement` 修复使迁移器能承载含 `BEGIN...END` 的 DDL，本轮触发器正是其首个真实用例。

**Verification**：任务命令在 **3.14.6 与 3.12.3 两个环境均 31 passed**；3.12 全量 37 passed，与作者证据一致（首轮我另在 3.14 观察到 2 项 `tests/core` 失败，系该解释器缺 PySide6 的环境问题，本轮全量仅以项目固定环境计）。三项重点（R-101 路径、R-104 触发器 DDL、R-106 双向）均由 Reviewer 独立探针复现，未依赖作者摘要。测试改动全部为真实断言，删除的 `test_failed_commit_reports_status_enum_coverage` 名不副实（只覆盖单一状态），由两个更有针对性的 R-106 测试取代，属合理调整。NOT_RUN/N/A 项按实记录。

## 结论与复审

**`e1d3e2c` 可交 Codex 集成：decision = approved。**

- 首次 Review 的 R-101（P1）与 R-102～R-106（P2）全部 **fixed**，经独立探针与测试复核无回归。
- 本轮新增 F-01（P2）不阻塞：`detection_overlay` 与 `render_preview` 共用 `previews/`，建议在 D03 §18 补该目录归属或注明归置理由；可在集成前后的文本提交中关闭，不需新的 reviewed head。
- v1 DDL 因新增触发器导致 checksum 变化；`ba1e769` 从未集成主线（master 未含该 head），不存在已应用迁移的漂移，作者"无需升版本号"的论证成立。

**集成时须由 Codex 完成**：核对 `e1d3e2c` 为当前 head、按协议 §6.6 串行集成、记录 `integration_commit`，把本次 decision 与 F-01 disposition 回填 `doc/STATUS.md`、`doc/tasks/TASK-006.md` 与两份 Handoff，并勾选 AC1～AC4（AC4 需集成验证完成后）；集成后执行该切片的集成检查。

**剩余风险**：多连接并发（WAL/busy_timeout）、真实升级链与迁移失败恢复、清理器与恢复流程对 current/pinned 的执行保护均未验证，已在作者证据与 Task 中标为 NOT_RUN/N/A，属 TASK-011/021 与集成验证范围。`backup_records.managed_path` 的前缀取 `backup_root.name`，其规范性依赖调用方传入 `backups` 目录；后续装配时应在 Port 文档或调用约定中固定该前缀。四个一级页面、Provider、打包与发布均未实现，也未获本 Task 授权。本报告事实仅适用于 `e1d3e2c`；分支后续变化（含 `af6deef`）不延用本批准。
