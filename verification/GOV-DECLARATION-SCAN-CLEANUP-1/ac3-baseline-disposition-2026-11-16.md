# GOV-DECLARATION-SCAN-CLEANUP-1 · AC3 归属表（冻结快照）

- 冻结时点（UTC）：2026-11-16T10:53:25Z
- 冻结 head：`ac34da5a5352b921360a31328a79f499634a1ee8`
- 依据审计件：`--audit-declarations` 报告 `report_sha256 = afddd7ccb94fe75471e6e33f3d60aeca4fb5e61d1f10e3aa4d2ee8f073d04962`，`generated_at = 2026-11-16T15:55:51+08:00`（原始 JSON 在仓外 `G:/CODEX/New Manga.workspace/tmp-dsh/decl-audit-final/declaration-audit.json`，244 KB）
- 计数：errors **154**；warnings 732；declarations 6755；protected_roots 5593
- 桶分布：**B1 64 / B2 79 / B3 11**（按 Ruling B 的 code→桶冻结映射）

## 0. 一一对应规则（可机械核验）

本表按审计 JSON 的 `errors` **原始顺序**编号 `ERR-001…`，每行的 `(文件, code, locator)` 三元组与 JSON 对应项逐一相等。
核验方法：重新运行

```powershell
python -B tools/governance/clean_workspace.py --audit-declarations --out <dir>
```

然后把新 JSON 的 `errors` 与本表逐行比对（同一 head 下应得到同一 `report_sha256`；本表冻结后，
任何 `errors` 数量变化都必须伴随本表的 append-only 变更记录）。

## 1. code × 桶 汇总

| code | 桶 | 条数 |
|---|---|---:|
| `TABLE_SCHEMA_INCOMPLETE` | B1 | 53 |
| `DECL_RELATIVE_UNRESOLVED` | B2 | 26 |
| `DECL_ENV` | B2 | 16 |
| `DECL_GLOB` | B2 | 16 |
| `DECL_DESTINATION_UNRESOLVED` | B2 | 11 |
| `TABLE_DELIMITER` | B1 | 10 |
| `DECL_UNKNOWN_DISPOSITION` | B3 | 8 |
| `DECL_TRAVERSAL` | B2 | 7 |
| `JSON_PARSE` | B3 | 2 |
| `DECL_BARE_NAME` | B2 | 1 |
| `DECL_MISSING_SOURCE` | B2 | 1 |
| `DECL_RELATIVE_AMBIGUOUS` | B2 | 1 |
| `FILE_UNREADABLE` | B3 | 1 |
| `TABLE_ROW_ARITY` | B1 | 1 |
| **合计** | — | **154** |

## 2.1 B1（64 条）

| err_id | code | 文件 | 位置 | 活 pin（卡 证据@commit） | 审计原文（截断） |
|---|---|---|---|---|---|
| ERR-001 | `TABLE_DELIMITER` | `doc/tasks/CHAPTER-SELECTOR-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-003 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/DESIGN-V2-IMPL-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-005 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/EXPORT-E2E-CLOSE-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-006 | `TABLE_DELIMITER` | `doc/tasks/F11-HOTKEY-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-032 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-09-UI-1.md` | — | 无 | table at line 4 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-033 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-HOST-AUTH-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-036 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-037 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-038 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-039 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-040 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-041 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-042 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-043 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-044 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-045 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-046 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-047 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-048 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-049 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-050 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-051 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-052 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-053 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-054 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-055 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-059 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-060 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-061 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-062 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-063 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2A.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-064 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-065 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-066 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2C-PREREQ-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-067 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2C-PREREQ-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-068 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2C.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-069 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-RUN-GRANT-2C.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-071 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-SCAN-RH-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-072 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-11-SCAN-RH-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-073 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-074 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-075 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-076 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-077 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-078 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-079 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | — | 无 | table at line 2 declares resource identity columns but lacks source_path; incomplete resource schemas cannot be trusted for protection |
| ERR-080 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-081 | `TABLE_ROW_ARITY` | `doc/tasks/FEA-12-UI.md` | — | 无 | table row at line 7 has 7 columns, header has 6; non-standard tables cannot be trusted for protection |
| ERR-112 | `TABLE_DELIMITER` | `doc/tasks/GPU-ORT-PROBE-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-113 | `TABLE_DELIMITER` | `doc/tasks/GRANT-ISSUER-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-115 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/IMPORT-EXPORT-UI-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-118 | `TABLE_DELIMITER` | `doc/tasks/MICA-FIX-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-119 | `TABLE_DELIMITER` | `doc/tasks/NS-WIRE-A1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-120 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/NS-WIRE-B2.md` | — | 无 | table at line 4 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-121 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/PLUGIN-RUNTIME-SANDBOX-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks evidence_id; incomplete schemas cannot be trusted for protection |
| ERR-122 | `TABLE_DELIMITER` | `doc/tasks/READER-PROGRESS-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-124 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-125 | `TABLE_DELIMITER` | `doc/tasks/RELEASE-PACKAGE-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-129 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks evidence_id; incomplete schemas cannot be trusted for protection |
| ERR-130 | `TABLE_DELIMITER` | `doc/tasks/SETTINGS-OPEN-B-1.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-131 | `TABLE_DELIMITER` | `doc/tasks/SETTINGS-OPEN-B-2.md` | — | 无 | table at line 2 has an invalid delimiter row |
| ERR-134 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/UIUX-V2-RUNTIME-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-135 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/UIUX-V2-RUNTIME-REALCORE-1.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |
| ERR-136 | `TABLE_SCHEMA_INCOMPLETE` | `doc/tasks/UIUX-V2-RUNTIME-REALCORE-2.md` | — | 无 | table at line 2 declares canonical-evidence identity columns but lacks path; incomplete schemas cannot be trusted for protection |

## 2.2 B2（79 条）

| err_id | code | 文件 | 位置 | 活 pin（卡 证据@commit） | 审计原文（截断） |
|---|---|---|---|---|---|
| ERR-002 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/D-14-STATUS-COLOR-FIX.md` | line 5 | 无 | declared relative path '未创建/未访问' is not an existing repo top-level entry; identity is ambiguous |
| ERR-007 | `DECL_TRAVERSAL` | `doc/tasks/FEA-00A-PREP-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-008 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-00A-PREP-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-009 | `DECL_TRAVERSAL` | `doc/tasks/FEA-01-FREEZE-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-010 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-01-FREEZE-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-011 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 4 | 无 | declared relative path '无 linked worktree；main checkout G:\\CODEX\\New Manga' is not an existing repo top-level entry; identity is ambiguous |
| ERR-012 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 6 | 无 | declared relative path '未创建 / 未使用' is not an existing repo top-level entry; identity is ambiguous |
| ERR-013 | `DECL_ENV` | `doc/tasks/FEA-06-RESIDUAL-1.md` | line 7 | 无 | declared path '测试 %TEMP% 临时根' contains an environment variable or shell home token |
| ERR-014 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 4 | 无 | declared relative path '无 linked worktree；main checkout G:\\CODEX\\New Manga' is not an existing repo top-level entry; identity is ambiguous |
| ERR-015 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 6 | 无 | declared relative path '未创建 / 未使用' is not an existing repo top-level entry; identity is ambiguous |
| ERR-016 | `DECL_ENV` | `doc/tasks/FEA-06-RESIDUAL-2.md` | line 7 | 无 | declared path '测试 %TEMP% 临时根' contains an environment variable or shell home token |
| ERR-017 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06.md` | line 4 | 无 | declared relative path '无 linked worktree；main checkout G:\\CODEX\\New Manga' is not an existing repo top-level entry; identity is ambiguous |
| ERR-018 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-06.md` | line 6 | 无 | declared relative path '未创建 / 未访问' is not an existing repo top-level entry; identity is ambiguous |
| ERR-019 | `DECL_GLOB` | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 5 | 无 | declared path '%TEMP%\\nm-fea07-*（应用隔离根/截图中转）' contains a glob wildcard |
| ERR-020 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 6 | 无 | declared relative path '2K/4K 模式与缩放（临时切换）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-021 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | line 6 | 无 | declared relative path '2K 100% / 4K 150%；AOC 保留原生 2560×1440（用户决定）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-022 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | line 5 | 无 | declared relative path '复测期间做过模式/缩放试验（ChangeDisplaySettingsEx / Settings UIA）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-023 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-07-RESIDUAL-2.md` | line 4 | 无 | declared relative path 'NOT_APPLICABLE（main；base 0a39a78f0，impl 85207730e/bacf6c307/a03a6794a）' is not an existing repo top-level entry; identity i… |
| ERR-024 | `DECL_GLOB` | `doc/tasks/FEA-07-RESIDUAL-2.md` | line 6 | 无 | declared path '%TEMP%/nm-fea07-perf-*、%TEMP%/nm-fea07-draft-window-*、%TEMP%/nm-fea07-window-lifecycle-*' contains a glob wildcard |
| ERR-025 | `DECL_ENV` | `doc/tasks/FEA-07-RESIDUAL-4.md` | line 5 | 无 | declared path '%TEMP%\\nm-legacy-ui-<guid>（测试隔离根，进程退出清理）' contains an environment variable or shell home token |
| ERR-026 | `DECL_ENV` | `doc/tasks/FEA-07-RESIDUAL-4.md` | line 7 | 无 | declared path '真实 %APPDATA% 只读比较' contains an environment variable or shell home token |
| ERR-027 | `DECL_GLOB` | `doc/tasks/FEA-07-V2-F11-1.md` | line 5 | 无 | declared path '%TEMP%\\nm-v2-f11-*（应用隔离根）' contains a glob wildcard |
| ERR-028 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-07.md` | line 4 | FEA-07-RESIDUAL-3 EV-R4B-07@8e9420f41 | declared relative path '无 linked worktree；main checkout G:\\CODEX\\New Manga' is not an existing repo top-level entry; identity is ambiguous |
| ERR-029 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-07.md` | line 6 | FEA-07-RESIDUAL-3 EV-R4B-07@8e9420f41 | declared relative path '未创建 / 未访问' is not an existing repo top-level entry; identity is ambiguous |
| ERR-030 | `DECL_GLOB` | `doc/tasks/FEA-08.md` | line 7 | 无 | declared path 'workspace FEA-08\\{r2-*,r3-*,impl-*,scope-*}.log/prompt' contains a glob wildcard |
| ERR-031 | `DECL_ENV` | `doc/tasks/FEA-08.md` | line 8 | 无 | declared path 'G: $RECYCLE.BIN（lab 前缀）' contains an environment variable or shell home token |
| ERR-034 | `DECL_GLOB` | `doc/tasks/FEA-11-HOST-AUTH-2.md` | line 6 | 无 | declared path 'verification/FEA-11-HOST-AUTH-2/tools/*（含 crash-ack.ps1 骨架）+ Host.Tests' contains a glob wildcard |
| ERR-035 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-11-HOST-AUTH-3.md` | line 5 | 无 | declared relative path 'pytest / gated IPC 临时目录' is not an existing repo top-level entry; identity is ambiguous |
| ERR-056 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-11-LINEAGE-1.md` | line 5 | 无 | declared relative path 'NOT_APPLICABLE（实现与证据均在仓库内；pytest 使用 :memory:/tmp_path）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-057 | `DECL_GLOB` | `doc/tasks/FEA-11-RENDITION-1.md` | line 6 | 无 | declared path 'tests/fea11/test_source_rendition_*.py（tmp_path 运行时生成真实 PNG/zip）' contains a glob wildcard |
| ERR-058 | `DECL_GLOB` | `doc/tasks/FEA-11-RESIDUAL-4A.md` | line 5 | 无 | declared path 'G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\r4a-*（gated IPC 隔离数据根）' contains a glob wildcard |
| ERR-070 | `DECL_GLOB` | `doc/tasks/FEA-11-SCAN-1.md` | line 6 | 无 | declared path 'G:\\CODEX\\New Manga.workspace\\FEA-11\\fixtures\\ipc-*（隔离 IPC fixture，含真实 zip/v8 DB）' contains a glob wildcard |
| ERR-082 | `DECL_ENV` | `doc/tasks/FEA-14-AI-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-083 | `DECL_ENV` | `doc/tasks/FEA-14-EDIT-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-084 | `DECL_ENV` | `doc/tasks/FEA-14-FONT-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-085 | `DECL_ENV` | `doc/tasks/FEA-14-LIB-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-086 | `DECL_ENV` | `doc/tasks/FEA-14-READ-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-087 | `DECL_ENV` | `doc/tasks/FEA-14-READ-2.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-088 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-14-SET-1.md` | line 6 | 无 | declared relative path 'worktree bin/obj（可重建）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-089 | `DECL_ENV` | `doc/tasks/FEA-14-SET-1.md` | line 7 | 无 | declared path '%APPDATA%\\NewManga（真实目录，只读访问）' contains an environment variable or shell home token |
| ERR-090 | `DECL_ENV` | `doc/tasks/FEA-15-A2-1.md` | line 6 | 无 | declared path '%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga' contains an environment variable or shell home token |
| ERR-091 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-15-A3-1.md` | line 4 | 无 | declared relative path '复用 G:\\CODEX\\New Manga.workspace\\FEA-15-A2-1\\out\\NewManga-0.1.1-win-x64（A2 staging）' is not an existing repo top-level … |
| ERR-092 | `DECL_ENV` | `doc/tasks/FEA-15-A3-1.md` | line 6 | 无 | declared path '%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga' contains an environment variable or shell home token |
| ERR-093 | `DECL_ENV` | `doc/tasks/FEA-15-A4-1.md` | line 5 | 无 | declared path '%APPDATA%\\com.newmanga.desktop、%APPDATA%\\NewManga' contains an environment variable or shell home token |
| ERR-094 | `DECL_GLOB` | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | line 14 | 无 | declared path 'G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/*.log' contains a glob wildcard |
| ERR-095 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/FEA-15-PREREQ-2.md` | line 5 | 无 | declared relative path 'pytest/dotnet 临时目录' is not an existing repo top-level entry; identity is ambiguous |
| ERR-096 | `DECL_TRAVERSAL` | `doc/tasks/FEA-C10-DRAFT.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-097 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-C10-DRAFT.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-098 | `DECL_TRAVERSAL` | `doc/tasks/FEA-C11-PREREQ-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-099 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-C11-PREREQ-1.md` | line 7 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-100 | `DECL_TRAVERSAL` | `doc/tasks/FEA-C14-DRAFT.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-101 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-C14-DRAFT.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-102 | `DECL_TRAVERSAL` | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-103 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-104 | `DECL_TRAVERSAL` | `doc/tasks/FEA-D06-GAP.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-105 | `DECL_DESTINATION_UNRESOLVED` | `doc/tasks/FEA-D06-GAP.md` | line 9 | 无 | declared path '..\\New Manga.workspace\\tmp' traverses with '..' |
| ERR-106 | `DECL_GLOB` | `doc/tasks/FEA-DOC-RECONCILE-1.md` | line 6 | 无 | declared path '%TEMP%\\fea-shots、%TEMP%\\chrome-prof-fea*' contains a glob wildcard |
| ERR-107 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/GATE4-PAGES-UPGRADE-1.md` | line 4 | 无 | declared relative path '待填（workspace\\task-envs\\GATE4-PAGES-UPGRADE-1）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-108 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/GATE4-READER-PAGE-1.md` | line 4 | 无 | declared relative path '待填（workspace\\task-envs\\GATE4-READER-PAGE-1）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-109 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | line 6 | 无 | declared relative path '上述task-env/source-export' is not an existing repo top-level entry; identity is ambiguous |
| ERR-110 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | line 8 | 无 | declared relative path '上述task-env中的缓存/输出' is not an existing repo top-level entry; identity is ambiguous |
| ERR-111 | `DECL_BARE_NAME` | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | line 8 | 无 | declared path 'CON' is a bare name, not an absolute or resolvable repo-relative path |
| ERR-116 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/INSTALLER-MATRIX-1.md` | line 4 | 无 | declared relative path '待填（workspace\\task-envs\\INSTALLER-MATRIX-1）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-117 | `DECL_RELATIVE_AMBIGUOUS` | `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md` | line 5 | 无 | declared path 'archive/history/legacy-shell/README.md' looks workspace-relative; it may mean the workspace root or the repository root and is refused |
| ERR-126 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/RELEASE-PACKAGE-PROBE-1.md` | line 4 | 无 | declared relative path '待填（workspace\\artifacts\\publish）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-132 | `DECL_RELATIVE_UNRESOLVED` | `doc/tasks/SIDECAR-REBUILD-1.md` | line 4 | 无 | declared relative path '待填（workspace\\task-envs\\SIDECAR-REBUILD-1）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-133 | `DECL_GLOB` | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md` | line 5 | 无 | declared path '%TEMP%/nm-software-smoke-*、%TEMP%/nm-bundled-hook-*' contains a glob wildcard |
| ERR-140 | `DECL_GLOB` | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | $.resources[2].disposition | 无 | declared path '%TEMP%/nm-fea07-perf-*, %TEMP%/nm-fea07-draft-window-*, %TEMP%/nm-fea07-window-lifecycle-*' contains a glob wildcard |
| ERR-141 | `DECL_RELATIVE_UNRESOLVED` | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | $.resources[0].disposition | 无 | declared relative path 'NOT_APPLICABLE（main checkout G:\\CODEX\\New Manga；base 8855baaac）' is not an existing repo top-level entry; identity is amb… |
| ERR-142 | `DECL_GLOB` | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | $.resources[3].disposition | 无 | declared path 'G:\\CODEX\\New Manga.workspace\\FEA-07-RESIDUAL-3\\（fixtures/a03-*、crash/*、startup-matrix/*、mutation-backup/）' contains a glob wildcard |
| ERR-143 | `DECL_ENV` | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | $.resources[5].disposition | 无 | declared path '%APPDATA%\\NewManga、%APPDATA%\\com.newmanga.desktop' contains an environment variable or shell home token |
| ERR-144 | `DECL_DESTINATION_UNRESOLVED` | `verification/FEA-11-AC4-GAPS-1/RESOURCE-MANIFEST.json` | $.resources[1].destination_path | 无 | declared relative path 'Same source location (G:\\CODEX\\New Manga.workspace\\FEA-11-AC4-GAPS-1\\)' is not an existing repo top-level entry; identi… |
| ERR-145 | `DECL_GLOB` | `verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json` | $.resources[2].disposition | 无 | declared path 'verification/FEA-11-HOST-AUTH-2/tools/* + Host.Tests fixtures' contains a glob wildcard |
| ERR-148 | `DECL_DESTINATION_UNRESOLVED` | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | $.resources[1].destination_path | FEA-11-RENDITION-1 EV-7@3eda60ac8 | declared relative path 'Same source location (G:\\CODEX\\New Manga.workspace\\FEA-11-RENDITION-1\\\\)' is not an existing repo top-level entry; ide… |
| ERR-149 | `DECL_GLOB` | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | $.resources[2].disposition | FEA-11-RENDITION-1 EV-7@3eda60ac8 | declared path 'tests/fea11/test_source_rendition_*.py（tmp_path 运行时生成）' contains a glob wildcard |
| ERR-150 | `DECL_MISSING_SOURCE` | `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json` | $.resources[3].disposition | FEA-11-RUN-GRANT-2 EV-18@8e1883655 | resource row has placeholder source '-' with disposition 'PRESERVE_REFERENCED' |
| ERR-151 | `DECL_RELATIVE_UNRESOLVED` | `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json` | $.resources[4].disposition | FEA-11-RUN-GRANT-2 EV-18@8e1883655 | declared relative path 'NOT_APPLICABLE（未触碰真实用户数据 / AppData / 外部卷 / 回收站）' is not an existing repo top-level entry; identity is ambiguous |
| ERR-152 | `DECL_DESTINATION_UNRESOLVED` | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | $.resources[1].destination_path | FEA-12-UI-RESIDUAL-1 EV-10@323001fec | declared relative path 'Same source location (G:\\CODEX\\New Manga.workspace\\FEA-12-UI-RESIDUAL-1\\)' is not an existing repo top-level entry; ide… |
| ERR-154 | `DECL_GLOB` | `verification/FEA-15-ACCEPT-1/resource-manifest.json` | $.resources[5].disposition | FEA-15-ACCEPT-1 SRC-26@1ecd613325cf69db7900fabb5fedb2302e47e84f | declared path '用户级 AppContainer profiles（具体实例与路径未知；*）' contains a glob wildcard |

## 2.3 B3（11 条）

| err_id | code | 文件 | 位置 | 活 pin（卡 证据@commit） | 审计原文（截断） |
|---|---|---|---|---|---|
| ERR-004 | `DECL_UNKNOWN_DISPOSITION` | `doc/tasks/EXPORT-E2E-CLOSE-1.md` | line 6 | 无 | resource 'verification/EXPORT-E2E-CLOSE-1/artifacts/book-fixture-20261027-134723.zip' has unknown disposition 'PRESERVE' |
| ERR-114 | `DECL_UNKNOWN_DISPOSITION` | `doc/tasks/IMPORT-EXPORT-UI-1.md` | line 6 | 无 | resource 'verification/IMPORT-EXPORT-UI-1/artifacts/ui-export-exp-583026330d98.zip' has unknown disposition 'PRESERVE' |
| ERR-123 | `DECL_UNKNOWN_DISPOSITION` | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | line 6 | 无 | resource 'Windows Credential Manager NewManga/provider/3819f991…/<ref>' has unknown disposition 'PRESERVE' |
| ERR-127 | `DECL_UNKNOWN_DISPOSITION` | `doc/tasks/RUN-BINDING-FIX-1.md` | line 5 | 无 | resource 'G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64-models/app/core-sidecar' has unknown disposition 'RE… |
| ERR-128 | `DECL_UNKNOWN_DISPOSITION` | `doc/tasks/RUN-BINDING-FIX-1.md` | line 6 | 无 | resource 'G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data' has unknown disposition 'READ_ONLY_REFERENCED' |
| ERR-137 | `FILE_UNREADABLE` | `verification/FEA-06-PREREQ-1/delivery-notes.md` | — | 无 | tracked markdown g:\codex\new manga\verification\FEA-06-PREREQ-1\delivery-notes.md contains NUL bytes; refusing a binary file as text |
| ERR-138 | `JSON_PARSE` | `verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-083908.json` | — | 无 | unparsable tracked JSON declaration file; protection cannot be enumerated and it is not in the explicit path+sha256 non-declaration exception manif… |
| ERR-139 | `JSON_PARSE` | `verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-083909.json` | — | 无 | unparsable tracked JSON declaration file; protection cannot be enumerated and it is not in the explicit path+sha256 non-declaration exception manif… |
| ERR-146 | `DECL_UNKNOWN_DISPOSITION` | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json` | $.resources[2].disposition | FEA-11-L-S1-B-RECOVERY-REAUTH-1 EV-14@80d2799de；FEA-11-L-S1-B-RECOVERY-REAUTH-1 EV-13@8a249538a | resource 'apps/desktop-avalonia/{src/NewManga.App/, tests/NewManga.App.Tests/, tests/NewManga.Host.Tests/}' has unknown disposition 'MODIFIED_IN_PL… |
| ERR-147 | `DECL_UNKNOWN_DISPOSITION` | `verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/RESOURCE-MANIFEST.json` | $.resources[1].disposition | FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 EV-08@4e8bda6e1 | resource 'G:\\CODEX\\New Manga.workspace\\FEA-11-L-S4-LOCATION-AUTH-REFRESH-1' has unknown disposition 'NOT_CREATED_NO_SCRATCH' |
| ERR-153 | `DECL_UNKNOWN_DISPOSITION` | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | $.resources[5].disposition | FEA-12-UI-RESIDUAL-1 EV-10@323001fec | resource 'verification/FEA-09/logs/wire-redacted.ndjson (pre-existing WireLogSourceRedactionTests side effect)' has unknown disposition 'RESTORED_I… |

