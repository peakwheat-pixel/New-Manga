# TASK-044 集成验证：`5784018`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `1c171dc`（Task 固定 base；开工 fast-forward 至 `33c8dd4`，无冲突） |
| reviewed head（delivery） | `7cd59d5` |
| 元数据 / 分支 head | `9c7d0fa` |
| Review 报告 commit | `731561b` → [`doc/reviews/TASK-044-7cd59d5.md`](../../doc/reviews/TASK-044-7cd59d5.md)（Reviewer=Codex，**非作者**；decision=`approved`） |
| integration commit | `5784018fb528ef7b2521134515ee7776222ffd1d`（merge，parents `731561b` + `9c7d0fa`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；`-p no:cacheprovider` |

## 作者改动范围（已核）

**14 文件 `+1849/−39`**：`src/infrastructure/sqlite/library.py`、`src/application/maintenance/{trash,ports}.py`、`tests/storage/test_purge_integrity.py`（新建 9 例）、`verification/TASK-044/**` 8 个证据文件、Handoff、Task 记录。`src/` 恰为 3 个白名单文件；**未碰** Schema/migration、依赖清单、`AGENTS.md`、其他 Task；`src`+`tests` 空白 `--check` exit 0。

## 复验结果（master `5784018`，Reviewer 独立重跑）

| # | 命令 / 方法 | 退出码 | 结果 |
|---:|---|---:|---|
| 1 | `pytest tests/storage -q -rs` | 0 | **48 passed / 0 skipped** |
| 2 | `pytest tests/storage/test_purge_integrity.py -q` | 0 | **9 passed** |
| 3 | `pytest -q -rs`（全仓） | 0 | **813 passed / 6 skipped**；6 条全为既有 `tests/network` 的 `openssl unavailable`；相对基线 `804/6` ⇒ **+9 恰为新增 9 例** |
| 4 | **判别力**：新测试 + master `src`（`git archive master` 导出树） | 1 | **8 failed / 1 passed**（唯一通过者为夹具完整性守卫，与作者说明一致） |
| 5 | **重跑作者 FK 探针** `verification/TASK-044/purge_fk_probe.py` | 0 | **E0a：6 表 / 7 FK 全部 `NO ACTION`**（与我先前独立枚举逐项一致）；E0b：pipeline 子树多为 `CASCADE`；**E1：两张表的 `current_revision_id` 清空均被触发器 `RAISE(ABORT)` 拒绝**；E2：只删 revisions 失败 |
| 6 | 纪律核对 | — | 既有测试**零断言/零测试删除**；**无新增 skip/xfail**；未碰 Schema/依赖；**无 `PRAGMA foreign_keys = OFF`**、**无吞 `IntegrityError`** |
| 7 | **集成方改动后复跑**（见下 R-01） | 0 | 改 docstring **前**全仓 **813/6**、**后**全仓 **813/6**（一致） |

## 结论来源标注

- **独立复跑**：第 1–7 项。
- **复用作者证据**：作者 5 次逐次全仓日志、`page-key-tables-scan.txt` 的全表清单（我核对其**结论**：仅 `pipeline_stage_states` 为"有 target 键而无 FK"的残留表）。

## ★ AC ① 实证修正（作者提出，Reviewer 采纳并作废我方步骤）

原 AC ① 写「**先** `UPDATE media_artifacts SET current_revision_id = NULL` 破循环」。**实测不可能**：`trg_media_artifacts_current_not_clearable`（以及 `regions` 的同名触发器）对「非 NULL → NULL」直接 `RAISE(ABORT)`（我重跑 E1 确认两条 UPDATE 均被拒）。正确路径：复合 FK `media_artifacts.current_revision_id → artifact_revisions` 是 **`DEFERRABLE INITIALLY DEFERRED`**，**同一事务内两侧同删**即在 COMMIT 时满足（E2 只删 revisions ⇒ 失败；E4 逆序全量 ⇒ 提交成功）。改 Schema 或关 FK 均被禁止 ⇒ 这是唯一合法路径。

**裁定：采纳作者修正；我方该步骤作废。** Task 文件内作者已加「AC ① 的实证修正（请 Reviewer 裁定）」段，本 Review 与本文明示认可。

**流程修正（我方）**：AC 涉及"删除/级联/清指针"时，除 `PRAGMA foreign_key_list` 外**必须枚举 `sqlite_master` 的 TRIGGER**（`SELECT name, sql FROM sqlite_master WHERE type='trigger'`）。本次我只读 FK 图 ⇒ 漏了触发器；作者用 E1 探针把它顶回来，处置正确。

## 5 项待裁定 → 结论

| # | 事项 | 裁定 |
|---|---|---|
| ① | F-10 的 port docstring 漂移（`src/application/importing/images/ports.py` 仍称两条查询都不得过滤 `deleted_at`） | **采纳作者的选项 (b)：由集成方改**（详见 R-01）。作者**正确地未自行越界**，并在 Handoff 给出建议替文 |
| ② | `max_source_order` 有意不过滤软删页 | **接受**：保留软删页的 `source_order` 槽位，避免"将来 restore 的页"与"其间新导入的页"撞号；既有测试（`tests/library/test_sqlite_library.py:205-209`，不在白名单）已把该口径写成有意行为，本切片未改它 |
| ③ | 跨页 provenance 清指针（对被清页之外的行做最小写入） | **接受**（登记 R-02）：否则"永久删除"会因该形态**永久失败**；写入面**仅限 provenance 指针**，内容/文件/哈希不动；代码 docstring 已写明 |
| ④ | `pipeline_stage_states` 一并清理（超出任务书枚举） | **接受**（非 YAGNI）：全库扫描证明它是唯一的"无 FK 残留表"，留行会复活幽灵状态；0 行 ≠ 可省 |
| ⑤ | `pipeline_runs` 不删 | **接受**：一次 run 跨多页，级联删 run 会破坏其它页的审计（登记 R-03） |

## R-01：集成方的文档落地（本文件的核心动作之一）

`src/application/importing/images/ports.py` 的 `ImportPageSink` docstring 按作者建议替文改为：

> Soft-deleted pages keep their ``source_order`` slot but no longer block re-import: ``max_source_order`` still counts them … while ``existing_source_hashes`` returns live pages only (F-10, TASK-044). …

**纯文档、行为零变更**（`+6/−6`，空白检查 exit 0）；**改前改后各跑一次全仓，均 `813 passed / 6 skipped`**。作者原始材料未改；该改动归属 TASK-044，记入本文件与 STATUS。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3 | port docstring 与 F-10 新行为矛盾（未来读者可能"修回去"） | **fixed（集成方按选项 b 落地）**（见上） |
| R-02 | P3 | `purge_pages` 首条 UPDATE 会最小写入**被清页之外**的行（只清悬空 provenance 指针） | **accepted**（代码 docstring 已写明；若产品要求"硬失败"，删该 UPDATE 与对应用例即可） |
| R-03 | P3 | `pipeline_runs` 不随页删除 ⇒ 可能累积"无 target 的运行记录" | **deferred（登记）** |
| R-04 | P3 | 行提交后若文件删除失败会抛错，且批次已从 ledger 移除 ⇒ 重试**无法再发现**孤儿文件 | **accepted**（作者已如实声明为风险 #1）；建议将来把文件清单持久化进 manifest 以获可重试性 |

## 集成结论

- [x] 非作者 Review 绑定固定 base/head；**Architecture 与 Verification 两面均覆盖**（口径按 2026-09-18 更新后的 §6）。
- [x] **F-2（P1）/ F-6 / F-7 / F-10 关闭**；TASK-044 置 `done`。
- [x] **F-2 的原始症状已根除**：行先删、文件后删 ⇒ 不会再出现"文件已失、行仍在、可 restore 出悬空活页"；删除语序与独立枚举的 FK 图逐条一致。
- [x] 边界：作者改动全在白名单内（3 个 `src/` + 1 个 `tests/`）；**唯一白名单外文件由集成方按裁决落地且为纯文档**；未改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task；未 push。
- [x] 6 条 skip 全为既有 `openssl unavailable`；未新增 skip、未放宽/删除既有断言；未把 `BLOCKED`/`NOT_RUN` 记为通过。
- [x] **在接线任何 purge UI 之前，本切片已完成**（这是 F-2 的硬前置）。
