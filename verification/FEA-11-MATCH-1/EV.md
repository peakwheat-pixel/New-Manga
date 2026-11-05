# FEA-11-MATCH-1 交付证据（EV）

- Task：`doc/tasks/FEA-11-MATCH-1.md`（FEA-11-MATCH-1 r1 已 approved → r2 最小返修；Owner=`fea12-dsim-impl`）
- base：`2d9a4a219`（冻结释放）；release head：`71e4b42b4`（基线实跑处）
- r1 交付 commits：`7bd8efe47`（实现 scanner/matcher）、`2d61e43c3`（测试/W1/W1b）、`b4ad109da`（C8 strict params）、`c12023ab6`（r1 卡/证据/Handoff）
- r1 独立上下文 Review：**approved（P0=0/P1=0；P2×3、P3×7）**，报告 `G:/CODEX/New Manga.workspace/FEA-11/review-match-1/FEA-11-MATCH-1-r1.md`（Lead 落盘 `doc/reviews/FEA-11-MATCH-1-r1.md`）
- **r2 交付 head（实现+测试）：`e8b0b2db811828d306a263eba55416a81fb00db6`**；r2 findings 处置：R1-01/R1-02/R1-03 修复 + R1-04/R1-05/R1-06/R1-07/R1-08/R1-09/R1-10/R1-11 同批处置，R1-12 卡外登记
- 环境：Windows 11 / Python 3.14.6 / Pillow 12.3.0（`requirements.txt:12` 既有 pin，无新增依赖）/ SQLite v8 / C# .NET 10.0.401（本卡未改动 `apps/**`）
- 记录时间：2026-11-06（Asia/Shanghai）

## 1. 门禁命令与结果（r2 复跑，真实机器时间戳）

| gate | command | exit | result | log |
|---|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | 0 | **108 passed** | `logs/pytest-fea11.log` |
| 本卡测试 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_match.py -q -p no:cacheprovider` | 0 | **20 passed** | `logs/pytest-match.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 0 | **3203 passed / 10 skipped**（基线 3183/10 + 20 新增，无回归、无新增 skip） | `logs/pytest-full.log` |
| 基线口径 | 同全量，于释放 head `71e4b42b4` clean tree 实跑 | 0 | **3183 passed / 10 skipped** | `logs/pytest-baseline.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **PIN AUDIT: PASS (all 18)** | `logs/verify-pins.log` |
| 零漂移 | `git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps` | 0 | **空**（C-17/C-15/C-08/ADJ-001、契约目录与 `apps/**` 零 diff；共享工作树存在**其他 Agent** 未提交 `apps/**` WIP，不属本卡、Owner 未 add，`static-diff.log` 已注明） | `logs/static-diff.log` |
| schema/迁移/依赖 | `git diff --name-only 2d9a4a219..HEAD -- src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py requirements.txt` | 0 | **空**（v1–v8 DDL/checksum 未动，无新依赖；仓库无 `pyproject.toml`，R1-10 已从证据移除该空条件） | `logs/static-diff.log` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md` | 0 | **PASS**（r2 最终复跑见 `logs/gates.log`；gates.log 以 `SOURCE_PIN` 登记为 EV-M10） | `logs/gates.log` |
| .NET | NOT_RUN | — | `apps/**` 零 diff、无 C# 变更，按 ZScope C7 口径 .NET 不适用；不得写 PASS | 本文件说明 |

> R1-03 修正：本目录所有日志头部的 `recorded_at` 均为**本次再生成时的本机机器时间**（生成脚本直接取 `datetime.now()`），不再是人工标注；正文日志内容与 r2 实跑一致。

## 2. 变更文件（相对 base）

r1：`src/application/sources/scanner.py`、`matcher.py`（`7bd8efe47`）、`tests/fea11/test_source_match.py` + W1 `test_source_scan.py` + W1b `test_source_sync.py`/`test_source_relink.py`（`2d61e43c3`）、C8 strict params（`b4ad109da`）
r2：`src/application/sources/matcher.py`、`tests/fea11/test_source_match.py`（`e8b0b2db8`）
文档/证据：本卡、`doc/handoffs/FEA-11-MATCH-1-handoff.md`、`verification/FEA-11-MATCH-1/**`
清单：`changed-files.txt`

## 3. AC → 证据映射

| AC | 状态 | 证据 |
|---|---|---|
| AC-M1（profile 提取/持久化/降级） | MET | `tests/fea11/test_source_match.py::test_scan_extracts_frozen_profile_and_apply_persists_canonical_params`（独立 Pillow 复算 + 固定 golden `53b800d9…` + apply 落库 canonical params）、`::test_scan_normalises_exif_orientations_and_refuses_invalid`（EXIF 1–8 含镜像、9 非法）、`::test_scan_degrades_unsupported_and_missing_evidence_without_writing`、`::test_scan_decode_budget_degrades_that_entry_only`、`::test_entry_profile_failure_reason_mapping_is_closed`、`::test_unparseable_params_are_incomparable_never_disguised_as_empty`、`::test_ambiguous_evidence_can_never_be_unchanged` |
| AC-M2（7 维可比性） | MET | `::test_profiles_comparable_requires_all_seven_dimensions`、`::test_unique_pixel_requires_single_occurrence_on_both_sides`、`::test_changed_requires_complete_comparable_pixel_evidence`、`::test_publication_relation_branches_are_both_asserted`、`::test_same_container_path_stays_direct` |
| AC-M3（重复 pixel occurrence） | MET | `::test_unique_pixel_requires_single_occurrence_on_both_sides`（1:2/2:1）、`::test_byte_identity_does_not_bypass_a_duplicate_pixel_group`（R1-02 后可达形态：v7 旧行 + 字节同一新成员 + 同侧重复像素；删守卫变异即红）、`::test_duplicate_pixel_occurrences_scan_plan_defer_chain`（scan→plan→apply 全链，defer 零发布，旧 binding 保持原状态） |
| AC-M4（旧证据降级/对照缺失修正） | MET（R1-01 已修） | `::test_old_v7_evidence_degrades_to_missing_old`、`::test_counterpart_less_duplicate_members_are_missing_and_added`、`::test_renamed_incomparable_counterpart_is_ambiguous_not_missing_added`（R1-01：改名 + orientation/params/decoder_version 不可比 → `ambiguous/incomparable`，不伪证）、`::test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two` |
| AC-M5（生产迁移+真实导入 fixture/单测/只读/两代 resync） | MET | `::test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`（`default_migrations()[:7]` + `ReferencedImportPlanner`/`Runtime` 真实 zip 导入 → 迁 v8 → 旧行诚实形态 → 第二代 `unique_pixel`）、`::test_scan_degrades_unsupported_and_missing_evidence_without_writing`（scan 前后 **sqlite_master 全表**快照相等，R1-05）、`::test_two_generation_resync_reaches_pixel_matching`、`::test_apply_with_a_lost_scan_commits_no_content_binding_or_profile`（R1-07：断言 `SOURCE_PLAN_STALE`/cause=expired + 无新 operation/publication 行） |
| AC-M6（契约/门禁零漂移） | MET | 上表 gates；`logs/static-diff.log`；`logs/gates.log` |

## 4. 关键实现口径

- `pixel-digest/1`：`sha256(ASCII("WxH") + b"\x00" + RGB)`，W/H 为 EXIF 转置后栅格，`orientation` 恒 1；仅 8-bit 全不透明 RGB（非全不透明 alpha → `unsupported`，L-M7）。
- `params_digest = sha256(canonical params JSON object)`；修复 v7 `scanner.py:545-555` 对 JSON 字符串字面量二次 `json.dumps` 的双重编码缺陷；canonical 对象比较（不比较原始字符串）；非对象/非法 JSON 一律 `incomparable`，绝不伪装 `{}`（`b4ad109da` 收紧）。
- `decoder="referenced-import"`、`decoder_version="1"`：DSH 2026-11-06 裁决——卡 C9 原值 `referenced-import/1` 含 `/` 违反 C-17 §5.2/§5 ID 规则，卡级常量更正（契约字节未动）。
- 降级闭集：`encrypted`/`unsupported`（解码预算/格式）/`missing_evidence`（无内容摘要）；grant/lease/identity/integrity 错误仍 typed 上抛（C11）。**口径收窄（R1-09）**：`encrypted` 目前只有 `_reason_for_import_error` 映射层单测，zip 加密成员的扫描级端到端未构造（容器级 typed 拒绝可能先行拦截），不再声称端到端已证。
- 匹配：7 维全等；重复组按 `content_digest`/`locator`/`pixel_digest` 任一侧 ≥2 判定；`unchanged` 仅 `direct`/`unique_pixel`；无完整可比证据绝不输出 `changed`；**同名/同像素 counterpart 但 profile 不可比 → `ambiguous/incomparable`（R1-01，含改名场景）**；`ambiguous` 行永远双侧非空（C-17 §5.3）。

## 5. 残余 limitation（预登记，未变化）

L-M1 PDF 不产 profile；L-M2 导入路径不写 profile（首次 resync 不能像素匹配，第二代起可达）；L-M3 apply 遗失 live scan 时 `_entries_from_target` 保真缺陷（本卡不扩 `service.py`；已加 scan 丢失 typed 失败零提交测试）；L-M4 旧证据重算未实现；L-M5 无解码诊断计数；L-M6 性能未优化（每次 scan 重读容器，仅登记）；L-M7 EXIF 镜像不可区分 + 非全不透明 alpha 不产 profile + 不宣称“所有可解码图必有 profile”。
**卡外后续（R1-12，不修）**：非图片成员在 `scanned.entries` 中 `content_digest=None`，变更容器 apply 全量 INSERT 可能触发 `source_entries.content_digest NOT NULL`；base 已存在、不在本卡 allowed_paths，登记后续探针/修复卡。

## 6. 资源

- fixture/临时根：`G:/CODEX/New Manga.workspace/FEA-11/fixtures`（pytest `tmp_path` 与 conftest 隔离根；不提交二进制 DB）
- 共享工作树说明：`apps/**` 存在**其他 Agent** 的未提交 WIP（`SourceScanScheduler` 等），不属本卡、未纳入本卡提交；本卡 `git diff <base>..HEAD -- apps` 为空。
- 未触碰用户真实数据/AppData/回收站/外部卷；未 push。
