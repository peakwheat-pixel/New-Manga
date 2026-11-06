# FEA-11-RENDITION-1 Canonical Evidence（Core 侧 referenced rendition 图源）

> 结论先行：本卡交付 **Core 侧能力** —— `source_mode='referenced'` 且 V 为真、binding healthy、publication gate open 的页可作为 Run 目标进入；provider 的 `page_frame` / `region_crop` / `page_png` 像素来自**当前持久化 binding** 对应的真实 source entry rendition（真实 PNG/zip/grant、真实 production 类，无 stub）；detect 在写 region 前复核 commit guard。**不宣称**「referenced 页 Run 产品可用」或「L10 全部修复」：**L-R1（Run 无 source-read grant 通道）** 仍使生产环境 referenced Run 在读图/提交被 typed 拒绝（负向用例在本卡证据内）。

| 项 | 值 |
|---|---|
| task | `FEA-11-RENDITION-1`（冻结卡 `doc/tasks/FEA-11-RENDITION-1.md`） |
| Owner | `rendition-impl`（DSH Agent Teams teammate） |
| base | `4360fbcdb` |
| 实现 commit | `693ab469b`（src 3 文件）、`a05a419f7`（tests 3 文件） |
| 证据 commit | 本目录所在 `docs(fea-11-rendition-1): evidence …` |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree） |
| 解释器 | CPython 3.14.6 / Windows 11 10.0.26300；.NET SDK=`dotnet`（net9.0 测试目标） |
| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`schema.py`、`apps/**` 全空 diff；pins 18/18） |
| 依赖 | **零新增**（Pillow/pypdfium2 已在既有闭包） |

## 1. 门禁实测（before → after）

| Gate | Before（基线） | After（本卡） | 结果 |
|---|---|---|---|
| `pytest tests/fea11 -q` | **108 passed** | **145 passed**（+37，只增不减） | PASS |
| 三个新测试文件 | — | **37 passed** | PASS |
| 全量 `pytest tests -q -p no:warnings --tb=short` | 3212 passed / 10 skipped | **3249 passed / 0 failed / 10 skipped**（3249-3212=37，恰为本卡新增） | PASS |
| 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | 1527 通过 / 0 失败 / 86 跳过 | **1527 / 0 / 86**（8 个测试项目合计：21+38+253+117+31+185+167+715） | PASS |
| `verify_pins.ps1` | 18/18 | **18/18 PASS** | PASS |
| `check.ps1` | PASS(3 warnings) | **PASS(3 warnings)**（9 非终态 Task / STATUS 80% / PLAN 80%） | PASS |
| `generate_api_inventory.py --check` | PASS | **PASS（EXIT=0）** | PASS |
| scope diff ⊆ `allowed_paths` | — | 6 个实现/测试文件 + 卡/Handoff/证据（全部在卡面 allowed_paths） | PASS |
| `doc/plan`/`doc/contracts`/`schema.py`/`apps/` diff | — | **空** | PASS |
| 依赖文件（`pyproject.toml`/`requirements*`）diff | — | **空** | PASS |
| `src/bootstrap/core_service.py` / `tests/fea11/conftest.py` / `test_source_lineage_run.py` diff | — | **空** | PASS |

**skip 原因（全量 pytest 10 skipped，与基线一致）**：均为既有环境门控跳过（无 provider runtime 权重 / 无 GPU 等既有 `pytest.mark.skipif` 条件），本卡未新增或改变任何 skip 条件；逐条明细见 `logs/gates-full-pytest.log`。**.NET 86 skipped**：既有 Host/UI 环境门控（read-only 策略、UI 集成），本卡零 C# 改动。

**已知副作用已恢复（R1-02 更正）**：tracked `verification/FEA-09/logs/wire-redacted.ndjson` 的字节改写来自**全量 .NET** 的 `WireLogSourceRedactionTests`（`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs:33`），**不是**全量 pytest；每次全量 .NET/pytest 后均执行 `git checkout -- verification/FEA-09`。最终 clean 状态与 HEAD 由 `logs/final-scope-validation.log`（2026-11-06T19:41:46，HEAD=`75dace4c2`，worktree status 空）固化（EV-9）。原始门禁日志 `gates-full-pytest.log` / `gates-dotnet.log` 是原始运行输出、不含 shell/EXIT 头部（R1-03）；命令、基线与退出结果见 Handoff §2/§4 与本节。

## 2. 判别性验证（删掉实现必须变红）

`logs/discrimination.log`（脚本与运行命令见该日志；仓外副本 `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\discriminate.py`）逐个破坏一条生产分支后运行目标用例，**4/4 全部变红**，随后从内存原文恢复文件（未使用 `git checkout`，避免丢弃其他未提交改动）：

| Case | 破坏点 | 期望变红的用例 | 实测 |
|---|---|---|---|
| A | 删除 `_page_or_error` 的 referenced 准入（I-1） | 目标进入 / 混合 chapter / region-scope / V 假拒绝 | **3 failed**（EXIT=1） |
| B | 删除 `_ManagedPageImageSource` 的 referenced 分支（I-2） | 像素/尺寸/裁剪/binding 重指 | **4 failed**（EXIT=1） |
| C | 删除 `handle_detect` 的 `_ensure_input_guard` 调用（I-4） | decode→write 窗口与 handler 级复核 | **2 failed**（EXIT=1） |
| D | 让唯一 `read_gate` 恒返回 open（I-3） | pending gate 目标展开 / commit guard | **3 failed**（EXIT=1） |

## 3. Evidence 索引（sha256）

| evidence_id | AC/Gate | path | sha256 |
|---|---|---|---|
| EV-1 | AC-R1/R2/R3/R4/R5/R7（fea11 145 / 三文件 37；真实图与装配） | `verification/FEA-11-RENDITION-1/logs/gates-feature.log` | `dff05bcfc9459412465e22b604bdc1cdca9009202d9157a7f929ea19bc31b403` |
| EV-2 | AC-R7（全量 pytest 3249/10；含 EXIT 与 FEA-09 恢复） | `verification/FEA-11-RENDITION-1/logs/gates-full-pytest.log` | `9afbe6a9375a4cba7db6a51589326b914553854ce92503df044797ff35dc99eb` |
| EV-3 | AC-R7（.NET 1527/0/86） | `verification/FEA-11-RENDITION-1/logs/gates-dotnet.log` | `ddf6593612cc702ba608846eef06632a3ffd038add0e6e6c1790564e2571d244` |
| EV-4 | AC-R6/R7（pins 18/18、check PASS(3 warnings)、API inventory PASS） | `verification/FEA-11-RENDITION-1/logs/gates-governance.log` | `b9e87be18819ba2ba13a4fc062ed7527a26241da713d7057fc94b1a5724277ec` |
| EV-5 | AC-R6（scope diff ⊆ allowed_paths；禁止面空；工作树快照） | `verification/FEA-11-RENDITION-1/logs/scope-validation.log` | `4294f8ce24ce1e06eb91ed141b6dc06288dea7d92a28a4daf91772a950e0a484` |
| EV-6 | 判别性（4/4 破坏变红，内存恢复） | `verification/FEA-11-RENDITION-1/logs/discrimination.log` | `c2e961cde3905e8d04e5bf0494b2fdc3935cf9b7d1126b1af68cd964c0e35f7d` |
| EV-7 | Resource Manifest（仓外隔离根聚合 sha256 + 资源处置） | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | `37b7f8680e4f8eb8cda3ddf9ae2416c5fb52bfce99a3097933c4d7f0540a5190` |
| EV-8 | 变更清单（base..证据 commit，逐文件） | `verification/FEA-11-RENDITION-1/changed-files.txt` | `36e3a73cfb0dd719df093f25464a55b07997853e0df6dfd819c9e4a017291bc9` |
| EV-9 | Review R1-02/R1-04 最终范围与工作树复原证明（HEAD=`75dace4c2`、worktree 空；FEA-09 tracked 字节已恢复） | `verification/FEA-11-RENDITION-1/logs/final-scope-validation.log` | `507cdec26046222f139105701fd6cbae1fca4937ee1eb0d6b74add4faec53d12` |

`logs/scope-validation.log` 记录的是实现+测试 commit（HEAD=`a05a419f7`）时点；证据/卡面/Handoff 提交只新增 `allowed_paths` 内文件，不改变禁止面（复核命令见 Handoff §门禁）。

## 4. 实现与证据对应（AC → 测试 → 证据）

| AC | 判定 | 判别性测试（真实 fixture，非 stub） | 证据 |
|---|---|---|---|
| **AC-R1** 目标进入 | **MET** | `test_pure_referenced_page_enters_page_scope_with_an_unchanged_metadata_shape`、`test_mixed_chapter_scope_expands_to_managed_and_referenced_pages`、`test_region_scope_admits_a_referenced_page_region`、`test_unverifiable_referenced_pages_stay_target_not_found`、`test_region_scope_with_null_dimensions_stays_a_stable_target_not_found`；真实装配层 `test_pending_gate_blocks_the_real_run_target_and_opens_when_acknowledged` | EV-1/EV-2 |
| **AC-R2** 像素来自当前 binding | **MET** | `test_page_frame_pixels_are_the_binding_rendition_not_the_managed_copy`、`test_page_png_is_the_rendition_png_of_the_current_binding`、`test_region_crop_is_taken_in_the_rendition_coordinate_system`、`test_mixed_page_never_reads_the_stale_managed_copy`、`test_repointing_the_binding_changes_the_pixels`、`test_run_detector_receives_the_binding_rendition_pixels`（记录型 detector + 记录型 OCR crop）、`test_detect_regions_register_native_lineage_for_the_current_binding`、`test_real_assembly_provider_reads_the_binding_rendition_end_to_end`；**run 级 `run_source_guard` 为测试内行为等价复刻**（assembly 内闭包不可导入），真实装配的 identity/guard 由 `test_source_rendition_gates.py:226-321` 覆盖（R1-08） | EV-1/EV-2 |
| **AC-R3** managed 零回归 | **MET** | `test_managed_page_reads_the_managed_copy_and_never_touches_grant_or_gate`（access/gate 探针：任何调用即 AssertionError）、`test_managed_page_without_a_managed_original_stays_the_historical_refusal`、目标 metadata 键集合断言（page/chapter 用例）、既有 `tests/providers/test_bootstrap_providers.py` 与 `tests/fea11` 基线全绿 | EV-1/EV-2 |
| **AC-R4** typed 拒绝与零写 | **MET** | `test_binding_change_between_prepare_and_accept_is_run_stale_preview`（①）、`test_binding_change_between_decode_and_region_write_is_input_revision_changed`（②⑤ + 行数快照）、`test_missing_live_grant_is_typed_and_reads_zero_bytes`、`test_revoked_session_grant_is_typed_and_reads_zero_bytes`、`test_refusal_detail_never_leaks_a_path_or_entry_name`（③）、`test_pending_gate_refuses_before_reading_the_source`、`test_unavailable_gate_refuses_before_reading_the_source`（④）、`test_page_whose_bound_entry_disappeared_is_typed_and_reads_zero_bytes`、`test_corrupt_entry_is_a_typed_refusal`、`test_decode_budget_refusal_is_typed`（⑥）、`test_real_run_commit_guard_refuses_pending_gate_and_missing_grant` | EV-1/EV-2 |
| **AC-R5** 不建第二套选择规则 | **MET** | `test_provider_reuses_the_single_selection_function_and_never_caches`（spy `prepare_referenced_rendition` 选择元组与 resolve 面逐字段一致、`RenditionCache.acquire` 探针 0 次、无 catalog 发布、源码不含 `"cache_key"` 字面）、真实装配 identity 断言（provider 的 gate 就是 catalog 的 gate） | EV-1/EV-2 |
| **AC-R6** 零契约/schema/依赖/wire 漂移 | **MET** | `git diff 4360fbcdb..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/` 空；pins 18/18；API inventory PASS；依赖文件空 diff；`test_run_target_face_never_introduces_a_source_star_error_code` | EV-4/EV-5 |
| **AC-R7** 门禁/证据/不夸大 | **MET** | 全部门禁实测（§1）；**L-R1 负向用例** `test_run_without_a_live_source_grant_is_typed_and_writes_nothing`（无 live grant 时 Run typed 失败、零 region/revision/lineage 写、detector 0 次）；Handoff 写明 L-R1/L-R2 且不宣称产品可用 | EV-1…EV-8 |

## 5. 保留 limitation（不适用本卡修复）

L-R1（Run 无 source-read grant 通道 → 生产 referenced Run 仍被 typed 拒绝；本卡只交付 Core 侧，候选 `FEA-11-RUN-GRANT-1`）、L-R2（加密源无 Secret-G 通道 → typed `SOURCE_PASSWORD_REQUIRED`）、L-R3（chapter/book-scope 行为变化）、L-R4（EXIF 方向）、L-R5（混合页按 binding 图；目标层保持旧门槛，V 假混合页进入后在 provider typed 拒绝、不解码）、L-R6（detect region 写在 step commit 之外）、L-R7（provider 不走 rendition_cache）、L-R8（Run 面沿用既有错误码 family，无 `SOURCE_*`）、L-R9（Run 快照不含 binding 观测）、L-R10（**R1-01 更正**：纯 referenced 且 width/height NULL → V 假 → page/region-scope 均 `TARGET_NOT_FOUND`；混合页可进入目标层但 provider typed 拒绝、像素不解码；不存在「NULL 尺寸 page-scope 可进入解码」）、**L-R11（R1-06 新登记）**：assembly 新 `read_gate` 对「healthy binding 但无 publication 行」返回 open，而 resolve 面 `core_service._assert_source_sync_gate` 在 previous binding 有 publication 时 fail-closed；该损坏形态下两读面语义不一致（provider/target 首次可达），本卡 Out 不碰 `core_service.py`，后续卡统一 gate。详见卡面「已知 limitation」。

## 6. 资源处置

- 仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\`（agent 脚本 + 判别日志 + 最终范围证明）**PRESERVE_REFERENCED**，聚合 sha256 `448272d64059f26444bf2bcd9e4e8f99ce6eb58c989192cf01438895e5aceca8`（10 文件；R1-04 重算）。
- 测试像素/zip/grant 全部在 pytest `tmp_path` 运行时生成，仓库不提交二进制 fixture。
- 未触碰真实用户数据 / AppData / 外部卷 / 回收站；未删除/移动/归档任何资源（`RESOURCE-MANIFEST.json`）。

## 7. Review r1 处置（DSH，2026-11-06）

- 独立 Review：`doc/reviews/FEA-11-RENDITION-1-r1.md` → **approved（P0=0/P1=0/P2=1/P3=8）**；无代码返修。
- **R1-01（P2）**：L-R10 更正为「纯 referenced NULL 尺寸 → page/region-scope 均 `TARGET_NOT_FOUND`；混合页可进目标层但 provider typed 拒绝、不解码」；L-R5 补全同一后果；Handoff 追加 Errata 节。
- **R1-02/R1-03（P3）**：FEA-09 tracked 字节 churn 归因更正为 .NET `WireLogSourceRedactionTests`；最终 clean 证明纳入 EV-9（`logs/final-scope-validation.log`）；原始日志无 header/EXIT 的事实已在 §1 注明。
- **R1-04（P3）**：`RESOURCE-MANIFEST.json` 登记第 10 个文件并重算聚合 sha（`448272d6…`）；canonical 副本 `logs/final-scope-validation.log` 已入证据目录。
- **R1-05（P3）**：AC/EV 用例计数（AC-R2 source.py 5、AC-R4 source.py 8）与「retryable 稳定」措辞已更正（`PipelineError` 无该成员）。
- **R1-06（P3）**：登记 limitation **L-R11**（`read_gate` vs `core_service._assert_source_sync_gate` 在损坏形态下分歧；本卡 Out 不碰 `core_service.py`）。
- **R1-07/R1-08（P3）**：`page_png` docstring 过时、V 假 diagnosed 文本「has no managed original」语义误导、run 级 guard 为行为等价复刻——**不改代码**，登记 follow-up（见卡面 Closeout Record）并在卡面/本文件写明实际证据边界。
- **R1-09（P3）**：既有 flaky `test_sandbox_job_kills_grandchildren`（非本卡回归）；集成验证按首跑/复跑记录。
