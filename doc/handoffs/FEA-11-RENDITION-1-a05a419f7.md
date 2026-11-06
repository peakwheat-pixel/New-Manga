---
task_id: FEA-11-RENDITION-1
author: rendition-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 4360fbcdb
delivery_head: a05a419f7
status: in_review
---

# Handoff — FEA-11-RENDITION-1（Core 侧 referenced rendition 图源）

- Task：`doc/tasks/FEA-11-RENDITION-1.md`（Owner=`rendition-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-06（Asia/Shanghai）
- 交付基线：`base_commit 4360fbcdb`（main）；**未 push、未创建 worktree**
- 交付实现 commit：`693ab469b`（`src/` 3 文件，I-1…I-4）、`a05a419f7`（3 个新测试文件，37 用例，I-5）
- 证据/卡面/本 Handoff：`verification/FEA-11-RENDITION-1/**` + `doc/tasks/FEA-11-RENDITION-1.md` + 本文件（同批文档提交；`delivery_head` 只指向实现+测试提交）
- 环境：Windows 11 10.0.26300 / PowerShell 7 / CPython 3.14.6 / .NET（net9.0 测试目标）；无新依赖、无 schema/migration/契约/wire 改动
- 范围依据：冻结卡 `In`（I-1…I-5）与 `doc/reviews/FEA-11-RENDITION-1-scope-r1.md`（READY-TO-FREEZE）+ delta「Lead 裁决」节（U1/U2 不 UNFREEZE；§3.3 码按既有 family；`prepared["cache_key"]` 禁令；原 I-5 commit-guard 投影改造出域）

## 1. 交付结果（逐项对照 AC）

| 项 | 结果 | 交付内容 |
|---|---|---|
| **I-1** referenced 目标进入 | 完成 | `src/infrastructure/sqlite/pipeline.py`：`_page_or_error` 增选 `p.source_mode`；**纯 referenced 页**（`managed_original_ref IS NULL`）由 `_ensure_referenced_target_readable` 准入 = `source_hash` 非空 + 复用 **C-15 §4.1 V**（注入 `page_visibility`，assembly 实现为 `repository.get_page(page_id) is not None`，不手写第三份谓词）+ 唯一 `read_gate` open；managed 页与**遗留混合页**（仍有 managed original，L-R5）保持既有门槛逐字节不变；`_region_or_error` SQL 改 `(managed_original_ref IS NOT NULL OR source_mode='referenced')`，保留 `width/height` 与 `_ensure_lineage_readable`；`TargetSnapshot.metadata` 键集合不变；`source_gate_reader`/`page_visibility` 为 `None` 时 fail-closed 保持旧拒绝（沿 `guard_reader` 先例） |
| **I-2** provider 像素源 | 完成 | `src/bootstrap/core_assembly.py`：`_ManagedPageImageSource.__init__` 增 `source_access`/`read_gate`/`image_decoder`/`document_raster`（全部默认 `None`，旧构造不变）；referenced 分支 = `read_gate` → `prepare_referenced_rendition`（唯一选择入口）→ `claim_secret_for_binding`（加密源一次性 Secret-G；缺失即 reader typed `SOURCE_PASSWORD_REQUIRED`，L-R2）→ `render_prepared_rendition` → PNG→Pillow；所有 `SourceImportError` → **固定安全文本** `ProviderInputError`（只带 code；禁路径/locator/entry 名）；managed 分支逐字节不变（并用 `getattr` 修正 F7 的 `PageView` 安全性）。**不发布 catalog、不写 `rendition_cache`、不新增 wire/key/kind、不使用 `prepared["cache_key"]`** |
| **I-3** 单一 gate 谓词 | 完成 | `core_assembly.assemble_core_services` 内唯一定义 `read_gate(page_id) -> unavailable/pending/open`，由 `run_source_guard`、`_ManagedPageImageSource`、`pipeline._catalog.source_gate_reader` 三处共用（装配级 identity 断言）；`run_source_guard` 改用该谓词；Run 面失败沿用既有 `TARGET_NOT_FOUND`/`PROVIDER_FAILED`/`INVALID_INPUT` family（C-17 §8:352），**不新增 `SOURCE_*` 命令码** |
| **I-4** detect 前置复核 | 完成 | `src/infrastructure/providers/handlers.py`：`HandlerDependencies.commit_guard` 可选；`handle_detect` 在 `region_creator` **之前**用 `step_run.input_refs["__fea10_guard__"]` 与当前 `run_guard_value` digest 比对，不一致 → `StepExecutionError("INPUT_REVISION_CHANGED")` 且**零 region/revision/lineage 写**；`None`/无 ref 时跳过（旧单测构造不变）；assembly 注入 `commit_guard=run_guard_value`（该 reader 定义前移到 handler 表构建之前，行为不变） |
| **I-5** 测试/证据 | 完成 | 新增 `tests/fea11/test_source_rendition_{source,run,gates}.py`（37 用例）+ `verification/FEA-11-RENDITION-1/**`（EV.md、RESOURCE-MANIFEST.json、changed-files.txt、`logs/` 6 份） |

| AC | 判定 | 判据（摘要） |
|---|---|---|
| **AC-R1** | **MET** | 纯 referenced 页 page-scope、混合 chapter-scope（managed+referenced=2 targets）、region-scope 均进入；`current(page_id)` 返回快照；`integrity_status≠complete`/`verified_digest≠entry.content_digest` 仍 `TARGET_NOT_FOUND`；`width/height` NULL 时 region-scope 仍 `TARGET_NOT_FOUND`（message=region_id），page-scope 不落 `SOURCE_BUDGET_EXCEEDED` |
| **AC-R2** | **MET** | 真实 PNG A(30×20, managed copy)/B(12×7, 当前 entry)/C(20×9, 旧 entry) + 真实 zip + 真实 grant；`page_frame`/`page_png`/`region_crop` 尺寸与像素只匹配 B；重指 binding→像素随 binding 变 C；混合页 `ManagedRootTrust.read_bytes` 哨兵证明不读 managed；真实 production pipeline + run_source_guard 接线下**记录型 detector** 收到的 frame 尺寸/像素 = B、OCR crop = B 蓝块、detect 产出的 native lineage 绑定 `pb-pr` |
| **AC-R3** | **MET** | managed 页 metadata 键集合不变（5 键 + 既有 `context_pages`）；`page_frame/page_png` 与旧实现一致；`_ForbiddenAccess`/`_forbidden_gate` 探针证明 managed 分支零 grant/gate 调用；`tests/providers` 559 passed/4 skipped、`tests/fea11` 基线全绿 |
| **AC-R4** | **MET** | ①prepare→accept 变化 → `RUN_STALE_PREVIEW`；②⑤decode→write 窗口变化 → step FAILED `INPUT_REVISION_CHANGED` 且 region/revision/lineage 零写；③无 grant/revoked → 读图前 `INVALID_INPUT` + detail 含 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`，`read_entry_bytes` spy 0 次；④gate pending/unavailable → 目标展开 `TARGET_NOT_FOUND` 且零解码；⑥entry 消失（V 假）/损坏（`SOURCE_FORMAT_UNSUPPORTED`）/预算超限（`SOURCE_BUDGET_EXCEEDED`）均 typed |
| **AC-R5** | **MET** | spy `prepare_referenced_rendition`：provider 调用恰 1 次且选择元组（source/version/entry/decoder/version/params_digest/verified_digest/kind）与 resolve 面逐字段一致；`RenditionCache.acquire` 探针 0 次；`rendition_cache`/`media_artifacts` 零行；provider 源码不含 `"cache_key"` 字面 |
| **AC-R6** | **MET** | `doc/plan`/`doc/contracts`/`schema.py`/`apps/`/依赖文件/`core_service.py`/conftest/冻结测试 全空 diff；pins 18/18；API inventory PASS |
| **AC-R7** | **MET** | 门禁数字见 §2；**L-R1 负向用例**：无 live grant 时 Run 为 typed 失败（`INVALID_INPUT`/`PROVIDER_FAILED`）且 region/revision/lineage 零写、detector 0 次；Handoff 明写 L-R1/L-R2；未宣称产品级可用、未回填 FEA-11 AC |

## 2. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC-R1…R5/R7 判别性 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings --tb=short` | CPython 3.14.6 / Win11；`a05a419f7` | **PASS（145 passed；基线 108，+37）** | `logs/gates-feature.log` |
| 三个新测试文件 | `python -m pytest tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_rendition_gates.py -q -p no:warnings` | 同上 | **PASS（37 passed）** | 同上 |
| 全量 Python | `python -m pytest tests -q -p no:warnings --tb=short` | 同上 | **PASS（3249 passed, 10 skipped；基线 3212/10）**；跑后 `git checkout -- verification/FEA-09` 恢复 tracked 字节 | `logs/gates-full-pytest.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | 同上 | **PASS（1527 通过 / 0 失败 / 86 跳过；8 项目：21+38+253+117+31+185+167+715）** | `logs/gates-dotnet.log` |
| 治理 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`... check.ps1`；`python tools/generate_api_inventory.py --check` | 仓库根 | **PASS 18/18**；**PASS(3 warnings：9 非终态 Task / STATUS 80% / PLAN 80%)**；**PASS EXIT=0** | `logs/gates-governance.log` |
| 范围 | `git diff --name-only 4360fbcdb..HEAD`；`git diff 4360fbcdb..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/`；依赖文件/cored 面 | 同上 | 6 个允许文件 + 卡/证据；禁止面**全空** | `logs/scope-validation.log` |
| 判别性（实现者自检，非权威） | `python "G:/CODEX/New Manga.workspace/FEA-11-RENDITION-1/discriminate.py"`（破坏→跑目标用例→内存原文恢复，不触碰 worktree 其他改动） | 同上；运行时临时改 `src/` 3 分支，随即恢复 | **4/4 变红**（I-1 准入 / I-2 分支 / I-4 调用 / `read_gate` 恒 open） | `logs/discrimination.log` |

未运行项与原因：无（全部门禁实跑）。skip 说明：全量 pytest 10 skipped 为**既有环境门控**（无 provider 权重/GPU 等既有 skipif 条件），本卡未新增/改变 skip；.NET 86 skipped 为既有 Host/UI 环境门控（read-only 策略、UI 集成），本卡零 C# 改动。

## 3. 已知 limitation（本卡**不**修复，closeout 必须保留）

- **L-R1（产品级 blocker）**：Run 无 source-read grant 通道（scope review F1）→ 生产环境 referenced 页 Run 仍会在读图/提交被 typed 拒绝（`INVALID_INPUT`/`PROVIDER_FAILED`，提交面 `DB_FAILED`）；本卡只交付 Core 侧，后续候选 `FEA-11-RUN-GRANT-1`（Host 铸 grant 切片，需 .NET 门禁）。
- **L-R2**：加密 referenced 源无法 Run（无 Secret-G 通道）→ typed `SOURCE_PASSWORD_REQUIRED`，不崩溃。
- **L-R3**：chapter/book-scope 行为变化 —— 含 referenced 页的章节/书从「整批失败」变为「包含 referenced 页」，成本/产物范围变化。
- **L-R4**：EXIF 方向不一致（frame 尺寸=rendition 转置后尺寸，可能 ≠ `pages.width/height`）。
- **L-R5**：混合页（referenced + managed_original_ref 非空）provider 从此按 binding 图，旧 managed 副本被忽略（Run 目标进入层仍沿旧门槛）。
- **L-R6**：detect 的 region 写仍在 step commit 之外；I-4 只把竞态窗口缩到「guard 复核 → 写 region」之间，不提供事务回滚。
- **L-R7**：provider 不走 `rendition_cache`（有意；重复解码；预算按 grant `max_decode_bytes`）。
- **L-R8**：Run 面错误码沿用既有 family，无 `SOURCE_*` 投影；commit 期 guard 失败仍为 `DB_FAILED`（原 I-5 出域）。
- **L-R9**：Run 快照不含 binding/rendition 观测（metadata 形状不变）。
- **L-R10**：`width/height` NULL 的 referenced 页 page-scope 可进入（像素由解码得出），region-scope 仍 `TARGET_NOT_FOUND`。

**不夸大**：本卡**不得**表述为「referenced 页 Run 产品可用」或「L10 全部修复」；FEA-11 AC11-5/AC11-9 未回填。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；base `4360fbcdb`，实现 head `a05a419f7`（未 push、未建 worktree）。
- 复现（期望值）：
  1. `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings` → **145 passed**
  2. `... -m pytest tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_rendition_gates.py -q` → **37 passed**
  3. `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=short` → **3249 passed / 10 skipped**（跑后 `git checkout -- verification/FEA-09`）
  4. `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` → **1527 / 0 / 86**
  5. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → 18/18；`... check.ps1` → PASS(3 warnings)；`C:/Python314/python.exe tools/generate_api_inventory.py --check` → EXIT=0
  6. `git diff --name-only 4360fbcdb..HEAD`（须 ⊆ 卡面 allowed_paths）；`git diff 4360fbcdb..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/`（须为空）
- 前置条件：CPython 3.14 + 现有依赖（Pillow/pytest 等）；测试全部使用 `tmp_path` 隔离库与运行时生成的真实 PNG/zip，不触碰真实用户数据/AppData/外部卷。
- 已批准依赖变化：**无**。
- 接收者下一步具体检查：① 逐条核对卡面 AC 与测试名（`EV.md` §4 映射表）；② **独立上下文**运行 §4 命令并记录 session ID/来源；③ 至少复跑一次判别性破坏（§2 判别行）确认用例真会变红；④ 判定 AC-R1…R7 与 limitation 登记是否充分；⑤ Lead 判定 `in_review` → closeout 与 `integration_commit`。

## 5. 下一任务建议

- Task ID / 标题：**无（本卡尚未 Review/集成，不释放后续实现卡）**；候选 `FEA-11-RUN-GRANT-1`（Host 为 Run 铸 source-read grant 的切片，需 .NET 门禁）由 Lead 决定是否立项，且必须在本卡 Review/集成后另行释放。
- 推荐 Agent / Reviewer：Reviewer 由 DSH 指派**独立上下文**（非本会话/非实现者；fresh subagent 或未参与实现的 ZCode/Codex）；实现 Owner 不自审。
- 推荐原因与前置依赖：本卡是 `FEA-11-LINEAGE-1` L10 的直接承接与 `FEA-11-RUN-GRANT-1` 的前置；`FEA-11-RUN-GRANT-1` 需要本卡 Core 侧读路径先落地。
- Recovery point：`G:\CODEX\New Manga`，`main`；base `4360fbcdb`，实现 head `a05a419f7`（未 push）；未创建 worktree。
- 允许修改路径：本卡 `allowed_paths` 不变（`src/infrastructure/sqlite/pipeline.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/providers/handlers.py`、`src/infrastructure/sqlite/library.py`（本卡未用到）、3 个新测试文件、卡/Review/Handoff、`verification/FEA-11-RENDITION-1/**`）。
- 禁止范围与新增授权条件：不得改 `core_service.py`、`apps/**`、`schema.py`、`doc/plan`、`doc/contracts`、依赖文件、`tests/fea11/conftest.py`、`test_source_lineage_run.py`、STATUS/PLAN/LEDGER、18 pins；不 `git add -A`；不 push。
- 交付物：独立 Review 报告（`doc/reviews/FEA-11-RENDITION-1-r*.md`，含运行证据、负向/判别性复跑结果、Reviewer 身份与来源）。
- 验证命令、环境与完成 Gate：同 §4；Gate = Review approved（P0/P1=0）+ DSH 集成验证 + scope diff ⊆ allowed_paths + pins 18/18 + 全量门禁不减少。
- 可直接转发给 Agent 的指令：

  > 对 `FEA-11-RENDITION-1` 做**独立上下文** Review（只读，不实现）：被审对象 `G:\CODEX\New Manga` `main` 的 `4360fbcdb..a05a419f7`（实现 `693ab469b` + 测试 `a05a419f7`；证据/卡面/Handoff 见 `verification/FEA-11-RENDITION-1/**` 与 `doc/tasks/FEA-11-RENDITION-1.md`）。按 `doc/reviews/FEA-11-RENDITION-1-scope-r1.md` 的 AC-R1…R7 与 I-1…I-5 逐条核验，重点检查：①`pipeline.py` 纯 referenced 准入是否真的复用 C-15 §4.1 V（未手写第三份）且 managed/混合页零回归；②`core_assembly._ManagedPageImageSource` referenced 分支是否只用 `prepare_referenced_rendition`、未发布/未写 cache/未用 `prepared["cache_key"]`、错误文本无路径；③`read_gate` 是否确实只有一份并被三处共用；④I-4 是否在 `region_creator` 之前复核且零写；⑤像素判别测试是否真实（非 stub）、判别性是否成立（自行破坏一条分支复跑）；⑥limitation L-R1/L-R2/L-R5/L-R7/L-R10 登记是否充分、是否有夸大声明。独立复跑：`pytest tests/fea11 -q`（期望 145）、三新文件（37）、`pytest tests -q`（3249/10，跑后 `git checkout -- verification/FEA-09`）、`dotnet test apps/desktop-avalonia/NewManga.sln -c Release`（1527/0/86）、`verify_pins.ps1`（18/18）、`check.ps1`（PASS）、`generate_api_inventory.py --check`。报告写入 `doc/reviews/FEA-11-RENDITION-1-r1.md`，记录 reviewer session/来源与 P0/P1/P2/P3 findings。

## 6. Errata（DSH closeout，2026-11-06；Review r1 处置，不改历史交付字节）

> 独立 Review `doc/reviews/FEA-11-RENDITION-1-r1.md`：**approved（P0=0/P1=0/P2=1/P3=8）**，无代码返修。以下为本 Handoff 与证据的更正/补充（详细处置见 `EV.md` §7 与卡面 Closeout Record）：

1. **R1-01（P2，更正 §3 L-R10 表述）**：本 Handoff §1 AC 行与 §3 中「`width/height` NULL 的 referenced 页 page-scope 可能可进入（像素由解码得出）」**不成立**。事实：纯 referenced 页 `width/height` NULL ⇒ V 为假 ⇒ page-scope 与 region-scope 均 `TARGET_NOT_FOUND`；**遗留混合页**（referenced + `managed_original_ref` 非空）可进入目标层（A-1 旧门槛），但 provider 因 V 读返回 None 而 typed 拒绝（`INVALID_INPUT`，detail 沿用 "has no managed original"），**像素不解码**、不产生错误像素/lineage。
2. **R1-02/R1-03（P3，证据归因与日志元数据）**：`verification/FEA-09/logs/wire-redacted.ndjson` 的 tracked 字节改写来自**全量 .NET** 的 `WireLogSourceRedactionTests`，不是全量 pytest；恢复与最终 clean 证明见 `verification/FEA-11-RENDITION-1/logs/final-scope-validation.log`（EV-9）。`gates-full-pytest.log`/`gates-dotnet.log` 是原始运行输出、无 shell/EXIT 头部；命令/基线/退出结果以本 Handoff §2/§4 与 EV.md §1 为准。
3. **R1-04（P3）**：仓外隔离根现有 **10** 个文件（新增 `final-scope-validation.log`），`RESOURCE-MANIFEST.json` 已登记并重算聚合 sha256 `448272d6…`；该文件已复制为 canonical 证据（卡面 EV-10 / EV.md EV-9）。
4. **R1-05（P3）**：卡面 AC-R2/AC-R4 的「source.py 8/10 用例」计数更正为 **5/8**（另列 run/gates 文件，勿重复计数）；「retryable 稳定」改为「message 稳定」（`PipelineError` 只有 `code`/`detail`）。
5. **R1-06（P3）**：新 `read_gate` 与 resolve 面 `core_service._assert_source_sync_gate` 在「healthy binding 但无 publication 行」的损坏形态下语义分歧 → 新登记 limitation **L-R11**；本卡 Out 不碰 `core_service.py`，后续卡统一。
6. **R1-07/R1-08（P3）**：`page_png` docstring 过时、V 假诊断文本「has no managed original」语义误导、run 级 `run_source_guard` 为行为等价复刻（真实装配 identity/guard 由 `gates.py` 覆盖）——本卡不改代码，登记 follow-up；卡面/EV 已注明证据边界。
7. **R1-09（P3）**：既有 flaky `tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（测试内已注 `FLAKY-PYTEST-1`）；非本卡回归，集成验证按首跑/复跑记录。
