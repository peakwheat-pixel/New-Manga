# RERUN 类 blocked 闭合（第 1 批）— 证据

Task：`AC-RERUN-CLOSE-1`（Owner：DSH）｜基线 `35a9f6c8d`｜r1 复核后修订

## 1. 本轮复跑（全部在当前架构、工作区 clean 状态下执行）

| 套件 | 命令 | 结果 | 日志 |
|---|---|---|---|
| `M2-REGION-RETYPE-CORE` 11 断言 | `pytest tests/editing/test_region_retype.py tests/providers/test_retype_redetect_persistence.py tests/pipeline/test_retype_candidate_persistence.py` | **27 passed / 0 failed**（0.39s） | `m2-region-retype-rerun.log` |
| `TASK-056` cleanup 单元 | `pytest tests/maintenance/test_cleanup.py` | **12 passed / 0 failed**（0.26s） | `task-056-cleanup-rerun.log` |
| `TASK-056` **wire 级** | `tests/core/test_core_cleanup_wire.py`（16 例，在真实 production assembly 上） | 含于全仓 3569 passed | `full-suite-run1.log` |
| `CHAPTER-MANUAL-SORT` chapter-reorder | `pytest tests/storage/test_chapter_reorder_atomic.py` | **5 passed / 0 failed**（0.79s） | `chapter-manual-sort-rerun.log` |
| **全仓 Python 套件** | `pytest tests/ -q -p no:cacheprovider` | **3569 passed / 0 failed / 10 skipped**（338.61s） | `full-suite-run1.log` |

复用 r1 复核者的独立复跑（337.85s：3568 passed + 1 偶发 `PermissionError`，单跑通过）作为交叉验证。

**执行环境**：Windows 11 / pwsh 7 / Python 3.14 / pytest 9.1.1；`QT_QPA_PLATFORM` 未设置。
执行后 `git status` 仅显示本证据目录（无测试产物污染）。

## 2. 改判 6 条（`blocked` → `verified`）

### 2.1 `M2-REGION-RETYPE-CORE` AC3

27 passed 覆盖 service guard 返回 + 管线候选持久化两层。
**nuance（r1 F-04）**：`verification.md:24` 披露 pipeline 层用例在红态即绿（场景守护），
故「先红后绿」主要体现于 service guard 层；两层覆盖本身仍成立。

### 2.2 `TASK-056` AC①–④（r1 复核 F-02 指出原「缺装配接线」已过时）

r1 复核指出：作者沿用 2026-09 卡面的「装配接线与模型目录 NOT_RUN」，**未复核当前树**。
实测当前树：

| AC | 支撑证据 |
|---|---|
| ① 范围与安全边界 | `core_assembly.py:1404` 构造 `CleanupService`；wire 测试 `test_run_skips_business_files_and_dotdot_traversal`（业务文件/`..` 被跳过）+ `test_missing_service_fails_closed_with_core_unavailable`（fail-closed） |
| ② 预览与结果 | wire 测试 `test_preview_lists_targets_bytes_and_pending_count`、`test_run_removes_cache_generations_and_returns_structured_counts`、`test_preview_empty_cache_reports_zero_and_removes_nothing` |
| ③ 瓦片缓存跨代回收 | `WebtoonTileCacheSweeper@src/infrastructure/imaging/tile_cache_sweep.py:22` + 单元用例 + wire 级各代回收验证 |
| ④ 幂等与失败 | wire 测试 `test_run_is_idempotent`、`test_failed_removal_is_persisted_as_pending`、`test_retry_clears_pending_after_the_fault_is_gone` |

**「模型目录」的处理**：受控范围由 `is_safe_relative_path@cleanup.py:229` + `_safe_targets@:193` 界定；
模型目录不在受控清理范围内 —— 这正符合 AC①「仅在受控副本/缓存/生成资产范围内」，**不是缺口**。

### 2.3 `TASK-056` AC⑤

当前全仓 3569 passed / 0 failed；历史 ≥5 次记录（各 900 passed）为旧套件时代。
**限制说明（r1 F-01）**：两者是跨测试集比较，非同集重复 5 次 —— 已在卡面注释中如实写明。

## 3. 未改判项及原因（AC3 要求）

| 条目 | 为什么仍 blocked |
|---|---|
| `CHAPTER-MANUAL-SORT` AC10 | AC 要求 **CoreClient（C#）也跑**；本轮只跑了 Python 侧（`NewManga.CoreClient.Tests.csproj` 存在且可跑，需 `dotnet test`） |
| `TASK-056` AC⑥ | 「STATUS 台账行」为机制性过时要求，待 DSH 裁决（见 `AC-BLOCKED-CLASSIFY-1`） |
| `M2-REGION-RETYPE-CORE` AC6 | 含 cargo + vitest（旧壳面已冻结）；pytest 三套件可复算但这不构成 AC 全部 |
| `MICA-FIX-1` AC2/AC4 | AC2 需 `--diagnostics` 原始日志重跑；AC4 需 `scripts/test.ps1` 回归日志（脚本存在可跑，延期而非不可行） |

## 4. 计数变化

```
改判前（AC-BLOCKED-CLASSIFY-1 收口时）：verified 182 / blocked 72 / NA 6
本轮第 1 次改判（e476f210a）：        verified 184 / blocked 70
本轮 r1 复核后改判 AC①–④：           verified 188 / blocked 66
先存 8 条 EOL/numstat FAIL 不变（非本轮引入）
```

## 5. 治理边界（r1 F-06 更正）

初版 README 称「`M2-REGION` AC3 因不带 `**` 未被 §4.3 识别」——**因果不准**。
更准确的口径：`check.ps1` 的 §4.3 / §4.3.1 AC 门禁**只在 `governance_version == '3'` 时执行**
（`:928` / `:953`），而 `M2-REGION-RETYPE-CORE` 与 `TASK-056` 都是 lifecycle **v1** 卡 →
它们的 AC 行**本就不受** `check.ps1` 的 AC 门禁约束，与是否带 `**` 无关。
`verify_final.py` 按 checkbox 统计（不要求 `**`），故 188/66 的计数变化是真实的文档层判定。

## 6. 不回归

```
check.ps1（全局）                → PASS (3 warnings)
check.ps1 -TaskPath M2-REGION    → PASS (4 warnings)
check.ps1 -TaskPath TASK-056     → PASS (4 warnings)
verify_pins.ps1                  → PASS (all 18)
generate_api_inventory.py --check → OK (1/80/6=87)
verify_final.py（AC_BASE=0b517259e）→ 40/40 卡、260/260 AC、188 verified / 66 blocked / 6 NA
```

## 7. 已知（r1 的 P3 观察）

1. 全仓存在 **Windows temp `PermissionError` 偶发**（`test_export.py`，单跑通过）——与本次改动无关，
   建议后续登记为 flaky。
2. `M2-REGION-RETYPE-CORE` 卡 frontmatter 有**重复 `integration_commit` 键**（L6 与 L16）——既存缺陷，未改。
3. 证据日志已补「命令 / 环境 / 结果」头（r1 F-05）。
