# FEA-11-MATCH-1 交付证据（EV）

- Task：`doc/tasks/FEA-11-MATCH-1.md`（FEA-11-MATCH-1 r1，Owner 实施）
- base：`2d9a4a219`（冻结释放）；release head：`71e4b42b4`（基线实跑处）；实际父提交：`9bf3fcb42`（docs-only closeout 补充）
- 交付 head（实现+测试）：`b4ad109dabb9fb99ab2193e9d83c703b72d27438`；实现 commit `7bd8efe47a306ad25e63089a669da5d6a7698260`、测试 commit `2d61e43c34f08930ae46d6f0150b220336747792`、C8 strict params 修正 commit `b4ad109dabb9fb99ab2193e9d83c703b72d27438`；docs/证据/Handoff 紧随其后的文档提交
- 环境：Windows 11 / Python 3.14.6 / Pillow 12.3.0（`requirements.txt:12` 既有 pin，无新增依赖）/ SQLite v8 / C# .NET 10.0.401（本卡未改动 `apps/**`）
- 记录时间：2026-11-06（Asia/Shanghai）

## 1. 门禁命令与结果

| gate | command | exit | result | log |
|---|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | 0 | **107 passed** | `logs/pytest-fea11.log` |
| 本卡测试 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_match.py -q -p no:cacheprovider` | 0 | **19 passed** | `logs/pytest-match.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 0 | **3202 passed / 10 skipped**（基线 3183/10 + 19 新增，无回归、无新增 skip） | `logs/pytest-full.log` |
| 基线口径 | 同全量，于释放 head `71e4b42b4` clean tree 实跑 | 0 | **3183 passed / 10 skipped** | `logs/pytest-baseline.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **PIN AUDIT: PASS (all 18)** | `logs/verify-pins.log` |
| 零漂移 | `git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps` | 0 | **空**（C-17/C-15/C-08/ADJ-001、契约目录与 `apps/**` 零 diff） | `logs/static-diff.log` |
| schema/迁移/依赖 | `git diff --name-only 2d9a4a219..HEAD -- src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py requirements.txt pyproject.toml` | 0 | **空**（v1–v8 DDL/checksum 未动，无新依赖） | `logs/static-diff.log` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md` | 0 | **PASS**（最终复跑见 `logs/gates.log`；gates.log 本身已按 `SOURCE_PIN` 登记进 Canonical Evidence） | `logs/gates.log` |
| .NET | NOT_RUN | — | `apps/**` 零 diff、无 C# 变更，按 ZScope C7 口径 .NET 不适用；不得写 PASS | 本文件说明 |

## 2. 变更文件（相对 base）

生产：`src/application/sources/scanner.py`、`src/application/sources/matcher.py`（`7bd8efe47`；C8 strict params 增补在 `b4ad109da`）
测试：新增 `tests/fea11/test_source_match.py`（`2d61e43c3`，C8 非对象 params 回归在 `b4ad109da`）；W1 窄批 `tests/fea11/test_source_scan.py`；W1b 窄批 `tests/fea11/test_source_sync.py`、`tests/fea11/test_source_relink.py`（`test_source_sync_storage.py` 经共享 helper 自动恢复，未改行）
文档/证据：本卡、`doc/handoffs/FEA-11-MATCH-1-handoff.md`、`verification/FEA-11-MATCH-1/**`
清单：`changed-files.txt`

## 3. AC → 证据映射

| AC | 状态 | 证据 |
|---|---|---|
| AC-M1（profile 提取/持久化/降级） | MET | `tests/fea11/test_source_match.py::test_scan_extracts_frozen_profile_and_apply_persists_canonical_params`（独立 Pillow 复算 + 固定 golden `53b800d9…` + apply 落库 canonical params）、`::test_scan_normalises_exif_orientations_and_refuses_invalid`（EXIF 1–8 含镜像、9 非法）、`::test_scan_degrades_unsupported_and_missing_evidence_without_writing`、`::test_scan_decode_budget_degrades_that_entry_only`、`::test_entry_profile_failure_reason_mapping_is_closed`、`::test_unparseable_params_are_incomparable_never_disguised_as_empty`、`::test_ambiguous_evidence_can_never_be_unchanged` |
| AC-M2（7 维可比性） | MET | `::test_profiles_comparable_requires_all_seven_dimensions`、`::test_unique_pixel_requires_single_occurrence_on_both_sides`、`::test_changed_requires_complete_comparable_pixel_evidence`、`::test_publication_relation_branches_are_both_asserted`、`::test_same_container_path_stays_direct` |
| AC-M3（重复 pixel occurrence） | MET | `::test_unique_pixel_requires_single_occurrence_on_both_sides`（1:2/2:1）、`::test_byte_identity_does_not_bypass_a_duplicate_pixel_group`、`::test_duplicate_pixel_occurrences_scan_plan_defer_chain`（scan→plan→apply 全链，defer 零发布） |
| AC-M4（旧证据降级/对照缺失修正） | MET | `::test_old_v7_evidence_degrades_to_missing_old`、`::test_counterpart_less_duplicate_members_are_missing_and_added`、`::test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`（真实 v7 导入 → `missing_old`） |
| AC-M5（生产迁移+真实导入 fixture/单测/只读/两代 resync） | MET | `::test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`（`default_migrations()[:7]` + `ReferencedImportPlanner`/`Runtime` 真实 zip 导入 → 迁 v8 → 旧行诚实形态 → 第二代 `unique_pixel`）、`::test_scan_degrades_unsupported_and_missing_evidence_without_writing`（scan 前后全表快照相等）、`::test_two_generation_resync_reaches_pixel_matching`、`::test_apply_with_a_lost_scan_commits_no_content_binding_or_profile` |
| AC-M6（契约/门禁零漂移） | MET | 上表 gates；`logs/static-diff.log`；`logs/gates.log` |

## 4. 关键实现口径

- `pixel-digest/1`：`sha256(ASCII("WxH") + b"\x00" + RGB)`，W/H 为 EXIF 转置后栅格，`orientation` 恒 1；仅 8-bit 全不透明 RGB（非全不透明 alpha → `unsupported`，L-M7）。
- `params_digest = sha256(canonical params JSON object)`；修复 v7 `scanner.py:545-555` 对 JSON 字符串字面量二次 `json.dumps` 的双重编码缺陷；canonical 对象比较（不比较原始字符串）；非对象/非法 JSON 一律 `incomparable`，绝不伪装 `{}`（`b4ad109da` 收紧）。
- `decoder="referenced-import"`、`decoder_version="1"`：DSH 2026-11-06 裁决——卡 C9 原值 `referenced-import/1` 含 `/` 违反 C-17 §5.2/§5 ID 规则，卡级常量更正（契约字节未动）。
- 降级闭集：`encrypted`/`unsupported`（解码预算/格式）/`missing_evidence`（无内容摘要）；grant/lease/identity/integrity 错误仍 typed 上抛（C11）。
- 匹配：7 维全等；重复组按 `content_digest`/`locator`/`pixel_digest` 任一侧 ≥2 判定；`unchanged` 仅 `direct`/`unique_pixel`；无完整可比证据绝不输出 `changed`；`ambiguous` 行永远双侧非空（C-17 §5.3）。

## 5. 残余 limitation（预登记，未变化）

L-M1 PDF 不产 profile；L-M2 导入路径不写 profile（首次 resync 不能像素匹配，第二代起可达）；L-M3 apply 遗失 live scan 时 `_entries_from_target` 保真缺陷（本卡不扩 `service.py`；已加 scan 丢失零提交测试）；L-M4 旧证据重算未实现；L-M5 无解码诊断计数；L-M6 性能未优化（每次 scan 重读容器，仅登记）；L-M7 EXIF 镜像不可区分 + 非全不透明 alpha 不产 profile + 不宣称“所有可解码图必有 profile”。

## 6. 资源

- fixture/临时根：`G:/CODEX/New Manga.workspace/FEA-11/fixtures`（pytest `tmp_path` 与 conftest 隔离根；不提交二进制 DB）
- 未触碰用户真实数据/AppData/回收站/外部卷；未 push。
