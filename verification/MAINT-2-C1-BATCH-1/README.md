# MAINT-2-C1-BATCH-1 证据索引（C1 批次 7 项，2026-11-14）

- Task：`doc/tasks/MAINT-2-C1-BATCH-1.md`（`in_progress`，base `1e272c5f6`）
- 环境：Windows；`C:\Python314\python.exe`（pytest 9.1.1）；仓库 `G:\CODEX\New Manga` 主工作树
- 本批范围：AC2 / AC3 / AC6 / AC7 / AC8（Python/Core 批）。**AC4 / AC5 = BLOCKED（需改冻结契约 M2-C1）**，见 `AC4-AC5-CONTRACT-BLOCKER.md`。AC1（READ-2 可见控件，Avalonia）按 DSH 安排另行派发。

## 1. 逐项结果

| AC | 结论 | commit | 判别测试 | 实测 |
|---|---|---|---|---|
| **AC2** FONT wire 负例 | **PASS** | `e0a3537a8` | `tests/core/test_font_wire.py::test_font_wire_delete_failure_is_typed_and_retryable` | 该文件 3 passed |
| **AC3** FONT 大文件/并发 | **PASS** | `461cd097d` | `tests/storage/test_fonts.py::test_import_byte_limit_boundary_accepts_exact_and_rejects_beyond` / `::test_import_rejects_a_real_oversized_file` / `::test_interleaved_same_content_imports_cannot_duplicate_a_row` | 该文件 9 passed |
| **AC4** LIB `kind` 投影 | **BLOCKED（STOP）** | —（无改动） | — | `M2-C1_TYPED_IPC_CONTRACT.md:201` 冻结 `list_chapters` 结果键集（`1.8`） |
| **AC5** `custom_rank` 读回 | **BLOCKED（STOP）** | —（无改动） | — | 同上（同一 result 行） |
| **AC6** LIB 64 位边界 | **PASS** | `859f12bcb` | `tests/core/test_library_wire.py::test_chapter_metadata_rejects_64_bit_overflow_as_typed_and_atomic` | 该文件 5 passed |
| **AC7** AI-1 清理 | **PASS** | `2bcd1ed66` | `tests/storage/test_prompt_templates.py::test_store_exposes_only_the_single_transaction_reassign_path` | 定向 14 passed |
| **AC8** PIN-BASIS 专项 suite | **PASS（留证）/ 基线漂移** | 本 commit | —（复跑留证） | main 工作树 **12 failed / 56 passed / 60 subtests**；历史为 validation clone `4ed7f32` 的 **3 failed / 61 passed / 2 skipped / 62 subtests** —— 见 §4 |

AC9（回归与门禁）见 §2/§3：**全量 pytest 0 failed**、`check.ps1` / `verify_pins` / `generate_api_inventory --check` 均未降级。

## 2. 门禁与全量测试（真实输出）

| 命令 | 结果 | 证据 |
|---|---|---|
| `C:\Python314\python.exe -m pytest -q` | **`3543 passed, 10 skipped, 11 warnings in 273.40s` / EXIT=0**（基线 3537 → +6：AC7 1 + AC6 1 + AC2 1 + AC3 3） | `logs/pytest-full.log` |
| `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` / EXIT=0 | 本 README §2 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` / EXIT=0 | 同上 |
| `C:\Python314\python.exe tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc` / EXIT=0（`1/80/6 = 87`，本批未动 C-07） | 同上 |

## 3. 判别力（不是"只断言不抛异常"）

- **AC2**：断言的是**具体 typed code** `FONT_DELETE_FAILED` + 行仍 active + 重试成功。任何把 `FontLibraryError` 吞成通用错误的回退都会让它变红。
- **AC3**：把 `MAX_FONT_BYTES` 关掉（模拟回退）后同一文件会被接受 → 边界断言变红（已实测）；并发用例断言 v11 `idx_font_assets_sha` 唯一索引存在 + 同一字节内容永不产生两行，索引被删或去重被绕过即变红。
- **AC6**：关掉两个 guard（模拟回退）后同一 wire 调用返回 **`UNKNOWN`** 且章节数 0→1（半写）—— 正是 R3-001 的症状；修复后为 `INVALID_REQUEST` + 零行。已实测。
- **AC7**：`hasattr` 守卫；把死方法加回去即变红（已实测）。

## 4. AC8 基线漂移（必须如实登记，不得写成"复跑通过"）

- 历史基线（卡面 `:179` + `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac2ac3-full-pytest-4ed7f32.log`）：命令 `python -m pytest tools/governance/tests -q`，**在 validation clone** `G:\CODEX\New Manga.workspace\FEA-15-PIN-BASIS-ENFORCE-1\validation-ac2ac3`、HEAD `4ed7f32b3` 上得 `3 failed, 61 passed, 2 skipped, 62 subtests passed`。
- 本次复跑（主工作树、HEAD 含本批提交）：`12 failed, 56 passed, 60 subtests passed` / EXIT=1，原始输出 `logs/pin-basis-governance-suite.log`。
- 差异原因（可复核）：
  1. **地点不同**：历史是 clean validation clone；本次是主工作树（含未跟踪证据目录、且 `core.autocrlf=true` 的 EOL 语义不同）。
  2. 失败集中在 `test_canonical_evidence_basis.py`（blob/EOL 字节口径）与 `test_residual_runtime_identity.py`（3 条历史即 FAIL，卡面明示"failures retained as FAIL"）。
  3. 本批未改 `doc/**` 证据、契约、task 卡或 `verification/**` 既有字节，故这些失败与本批改动无因果关系（本批 4 个 commit 只改 `src/application/library/service.py`、`src/infrastructure/sqlite/prompt_templates.py` 与 4 个测试文件）。
- **待 DSH 裁决**：是否接受"以 validation clone 为可比基线、主工作树的 12F 属环境/EOL 观测"，或要求先修 `test_canonical_evidence_basis` 的 EOL 口径（与 C-07 pin 的 `GOV-EOL-PIN` 债同源）。

## 5. NOT_RUN / 未做

- **AC1（READ-2 可见控件）**：按 DSH 安排另派，未在本批实施。
- **AC4 / AC5**：BLOCKED，未写任何契约或实现字节（见 `AC4-AC5-CONTRACT-BLOCKER.md`）。
- **占用文件压测**（FONT）：保留 `KEEP`（`MAINT-1-C4-WAIVER-CARRIER` W4），不在本批。
- **.NET 侧测试**：本批未改 `apps/**`，未复跑 `dotnet test`（AC1 落地时须跑）。
- **pytest 证据在仓外**（`workspace/flea-loop/pytest-full-ro1.log`，MAINT-1 遗留）：本批已改为仓内留证，见 `logs/pytest-full.log`。