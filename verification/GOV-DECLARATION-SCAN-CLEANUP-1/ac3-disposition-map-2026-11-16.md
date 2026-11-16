# GOV-DECLARATION-SCAN-CLEANUP-1 · AC3 逐条处置映射（154 → 0 的中间态快照）

- 基线：`report_sha256 = afddd7ccb94fe75471e6e33f3d60aeca4fb5e61d1f10e3aa4d2ee8f073d04962`（2026-11-16T15:55:51+08:00），errors = 154
- 本表与 `ac3-baseline-disposition-2026-11-16.md` 的 `ERR-nnn` 一一对应（同一 JSON 顺序、同一 report_sha256）。
- 机制：B1 = `table_bindings`（逐表，Codex 裁决 Q1）；B3 = 别名表（Q3）+ `raw_non_declaration_bindings`（Q2）；
  B2 活 pin ⇒ 保留态；B2 未钉住 ⇒ AC7 单元修复（Q4）。

| ERR | code | 桶 | 文件 | 处置机制 |
|---|---|---|---|---|
| ERR-001 | `TABLE_DELIMITER` | B1 | `doc/tasks/CHAPTER-SELECTOR-1.md` | 表级绑定 `HIE-B001` |
| ERR-002 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/D-14-STATUS-COLOR-FIX.md` | B2 ⇒ AC7 单元修复 |
| ERR-003 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/DESIGN-V2-IMPL-1.md` | 表级绑定 `HIE-B002` |
| ERR-004 | `DECL_UNKNOWN_DISPOSITION` | B3 | `doc/tasks/EXPORT-E2E-CLOSE-1.md` | 别名表 `PRESERVE` → `PRESERVE_UNKNOWN` |
| ERR-005 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/EXPORT-E2E-CLOSE-1.md` | 表级绑定 `HIE-B003` |
| ERR-006 | `TABLE_DELIMITER` | B1 | `doc/tasks/F11-HOTKEY-1.md` | 表级绑定 `HIE-B004` |
| ERR-007 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-00A-PREP-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-008 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-00A-PREP-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-009 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-01-FREEZE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-010 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-01-FREEZE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-011 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06-RESIDUAL-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-012 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06-RESIDUAL-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-013 | `DECL_ENV` | B2 | `doc/tasks/FEA-06-RESIDUAL-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-014 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06-RESIDUAL-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-015 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06-RESIDUAL-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-016 | `DECL_ENV` | B2 | `doc/tasks/FEA-06-RESIDUAL-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-017 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06.md` | B2 ⇒ AC7 单元修复 |
| ERR-018 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-06.md` | B2 ⇒ AC7 单元修复 |
| ERR-019 | `DECL_GLOB` | B2 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-020 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-021 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-07-AC5-NATIVE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-022 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-023 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-07-RESIDUAL-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-024 | `DECL_GLOB` | B2 | `doc/tasks/FEA-07-RESIDUAL-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-025 | `DECL_ENV` | B2 | `doc/tasks/FEA-07-RESIDUAL-4.md` | B2 ⇒ AC7 单元修复 |
| ERR-026 | `DECL_ENV` | B2 | `doc/tasks/FEA-07-RESIDUAL-4.md` | B2 ⇒ AC7 单元修复 |
| ERR-027 | `DECL_GLOB` | B2 | `doc/tasks/FEA-07-V2-F11-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-028 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-07.md` | B2 活 pin ⇒ 保留态（`FEA-07-RESIDUAL-3 EV-R4B-07@8e9420f41`） |
| ERR-029 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-07.md` | B2 活 pin ⇒ 保留态（`FEA-07-RESIDUAL-3 EV-R4B-07@8e9420f41`） |
| ERR-030 | `DECL_GLOB` | B2 | `doc/tasks/FEA-08.md` | B2 ⇒ AC7 单元修复 |
| ERR-031 | `DECL_ENV` | B2 | `doc/tasks/FEA-08.md` | B2 ⇒ AC7 单元修复 |
| ERR-032 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-09-UI-1.md` | 表级绑定 `HIE-B005` |
| ERR-033 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-HOST-AUTH-1.md` | 表级绑定 `HIE-B006` |
| ERR-034 | `DECL_GLOB` | B2 | `doc/tasks/FEA-11-HOST-AUTH-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-035 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-11-HOST-AUTH-3.md` | B2 ⇒ AC7 单元修复 |
| ERR-036 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | 表级绑定 `HIE-B008` |
| ERR-037 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | 表级绑定 `HIE-B007` |
| ERR-038 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | 表级绑定 `HIE-B010` |
| ERR-039 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | 表级绑定 `HIE-B009` |
| ERR-040 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | 表级绑定 `HIE-B012` |
| ERR-041 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | 表级绑定 `HIE-B011` |
| ERR-042 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | 表级绑定 `HIE-B014` |
| ERR-043 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` | 表级绑定 `HIE-B013` |
| ERR-044 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | 表级绑定 `HIE-B016` |
| ERR-045 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | 表级绑定 `HIE-B015` |
| ERR-046 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | 表级绑定 `HIE-B018` |
| ERR-047 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | 表级绑定 `HIE-B017` |
| ERR-048 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | 表级绑定 `HIE-B020` |
| ERR-049 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | 表级绑定 `HIE-B019` |
| ERR-050 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | 表级绑定 `HIE-B022` |
| ERR-051 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | 表级绑定 `HIE-B021` |
| ERR-052 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | 表级绑定 `HIE-B024` |
| ERR-053 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-B-PREREQ-1.md` | 表级绑定 `HIE-B023` |
| ERR-054 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md` | 表级绑定 `HIE-B026` |
| ERR-055 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md` | 表级绑定 `HIE-B025` |
| ERR-056 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-11-LINEAGE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-057 | `DECL_GLOB` | B2 | `doc/tasks/FEA-11-RENDITION-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-058 | `DECL_GLOB` | B2 | `doc/tasks/FEA-11-RESIDUAL-4A.md` | B2 ⇒ AC7 单元修复 |
| ERR-059 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md` | 表级绑定 `HIE-B028` |
| ERR-060 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md` | 表级绑定 `HIE-B027` |
| ERR-061 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-1.md` | 表级绑定 `HIE-B029` |
| ERR-062 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2.md` | 表级绑定 `HIE-B030` |
| ERR-063 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2A.md` | 表级绑定 `HIE-B031` |
| ERR-064 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` | 表级绑定 `HIE-B033` |
| ERR-065 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` | 表级绑定 `HIE-B032` |
| ERR-066 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2C-PREREQ-1.md` | 表级绑定 `HIE-B035` |
| ERR-067 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2C-PREREQ-1.md` | 表级绑定 `HIE-B034` |
| ERR-068 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2C.md` | 表级绑定 `HIE-B037` |
| ERR-069 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-RUN-GRANT-2C.md` | 表级绑定 `HIE-B036` |
| ERR-070 | `DECL_GLOB` | B2 | `doc/tasks/FEA-11-SCAN-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-071 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-SCAN-RH-1.md` | 表级绑定 `HIE-B039` |
| ERR-072 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-11-SCAN-RH-1.md` | 表级绑定 `HIE-B038` |
| ERR-073 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | 表级绑定 `HIE-B041` |
| ERR-074 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | 表级绑定 `HIE-B040` |
| ERR-075 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | 表级绑定 `HIE-B043` |
| ERR-076 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | 表级绑定 `HIE-B042` |
| ERR-077 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | 表级绑定 `HIE-B045` |
| ERR-078 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | 表级绑定 `HIE-B044` |
| ERR-079 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | 表级绑定 `HIE-B047` |
| ERR-080 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | 表级绑定 `HIE-B046` |
| ERR-081 | `TABLE_ROW_ARITY` | B1 | `doc/tasks/FEA-12-UI.md` | 表级绑定 `HIE-B048` |
| ERR-082 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-AI-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-083 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-EDIT-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-084 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-FONT-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-085 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-LIB-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-086 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-READ-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-087 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-READ-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-088 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-14-SET-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-089 | `DECL_ENV` | B2 | `doc/tasks/FEA-14-SET-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-090 | `DECL_ENV` | B2 | `doc/tasks/FEA-15-A2-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-091 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-15-A3-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-092 | `DECL_ENV` | B2 | `doc/tasks/FEA-15-A3-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-093 | `DECL_ENV` | B2 | `doc/tasks/FEA-15-A4-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-094 | `DECL_GLOB` | B2 | `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-095 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/FEA-15-PREREQ-2.md` | B2 ⇒ AC7 单元修复 |
| ERR-096 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-C10-DRAFT.md` | B2 ⇒ AC7 单元修复 |
| ERR-097 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-C10-DRAFT.md` | B2 ⇒ AC7 单元修复 |
| ERR-098 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-C11-PREREQ-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-099 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-C11-PREREQ-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-100 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-C14-DRAFT.md` | B2 ⇒ AC7 单元修复 |
| ERR-101 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-C14-DRAFT.md` | B2 ⇒ AC7 单元修复 |
| ERR-102 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-103 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-CONTRACT-WRAP-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-104 | `DECL_TRAVERSAL` | B2 | `doc/tasks/FEA-D06-GAP.md` | B2 ⇒ AC7 单元修复 |
| ERR-105 | `DECL_DESTINATION_UNRESOLVED` | B2 | `doc/tasks/FEA-D06-GAP.md` | B2 ⇒ AC7 单元修复 |
| ERR-106 | `DECL_GLOB` | B2 | `doc/tasks/FEA-DOC-RECONCILE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-107 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/GATE4-PAGES-UPGRADE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-108 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/GATE4-READER-PAGE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-109 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-110 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-111 | `DECL_BARE_NAME` | B2 | `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-112 | `TABLE_DELIMITER` | B1 | `doc/tasks/GPU-ORT-PROBE-1.md` | 表级绑定 `HIE-B049` |
| ERR-113 | `TABLE_DELIMITER` | B1 | `doc/tasks/GRANT-ISSUER-1.md` | 表级绑定 `HIE-B050` |
| ERR-114 | `DECL_UNKNOWN_DISPOSITION` | B3 | `doc/tasks/IMPORT-EXPORT-UI-1.md` | 别名表 `PRESERVE` → `PRESERVE_UNKNOWN` |
| ERR-115 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/IMPORT-EXPORT-UI-1.md` | 表级绑定 `HIE-B051` |
| ERR-116 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/INSTALLER-MATRIX-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-117 | `DECL_RELATIVE_AMBIGUOUS` | B2 | `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-118 | `TABLE_DELIMITER` | B1 | `doc/tasks/MICA-FIX-1.md` | 表级绑定 `HIE-B052` |
| ERR-119 | `TABLE_DELIMITER` | B1 | `doc/tasks/NS-WIRE-A1.md` | 表级绑定 `HIE-B053` |
| ERR-120 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/NS-WIRE-B2.md` | 表级绑定 `HIE-B054` |
| ERR-121 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/PLUGIN-RUNTIME-SANDBOX-1.md` | 表级绑定 `HIE-B055` |
| ERR-122 | `TABLE_DELIMITER` | B1 | `doc/tasks/READER-PROGRESS-1.md` | 表级绑定 `HIE-B056` |
| ERR-123 | `DECL_UNKNOWN_DISPOSITION` | B3 | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | 别名表 `PRESERVE` → `PRESERVE_UNKNOWN` |
| ERR-124 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` | 表级绑定 `HIE-B057` |
| ERR-125 | `TABLE_DELIMITER` | B1 | `doc/tasks/RELEASE-PACKAGE-1.md` | 表级绑定 `HIE-B058` |
| ERR-126 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/RELEASE-PACKAGE-PROBE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-127 | `DECL_UNKNOWN_DISPOSITION` | B3 | `doc/tasks/RUN-BINDING-FIX-1.md` | 别名表 `READ_ONLY_REFERENCED` → `PRESERVE_REFERENCED` |
| ERR-128 | `DECL_UNKNOWN_DISPOSITION` | B3 | `doc/tasks/RUN-BINDING-FIX-1.md` | 别名表 `READ_ONLY_REFERENCED` → `PRESERVE_REFERENCED` |
| ERR-129 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md` | 表级绑定 `HIE-B059` |
| ERR-130 | `TABLE_DELIMITER` | B1 | `doc/tasks/SETTINGS-OPEN-B-1.md` | 表级绑定 `HIE-B060` |
| ERR-131 | `TABLE_DELIMITER` | B1 | `doc/tasks/SETTINGS-OPEN-B-2.md` | 表级绑定 `HIE-B061` |
| ERR-132 | `DECL_RELATIVE_UNRESOLVED` | B2 | `doc/tasks/SIDECAR-REBUILD-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-133 | `DECL_GLOB` | B2 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md` | B2 ⇒ AC7 单元修复 |
| ERR-134 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/UIUX-V2-RUNTIME-1.md` | 表级绑定 `HIE-B062` |
| ERR-135 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/UIUX-V2-RUNTIME-REALCORE-1.md` | 表级绑定 `HIE-B063` |
| ERR-136 | `TABLE_SCHEMA_INCOMPLETE` | B1 | `doc/tasks/UIUX-V2-RUNTIME-REALCORE-2.md` | 表级绑定 `HIE-B064` |
| ERR-137 | `FILE_UNREADABLE` | B3 | `verification/FEA-06-PREREQ-1/delivery-notes.md` | raw 绑定 `HIE-O04` |
| ERR-138 | `JSON_PARSE` | B3 | `verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-083908.json` | raw 绑定 `HIE-O05` |
| ERR-139 | `JSON_PARSE` | B3 | `verification/FEA-07-AC5-NATIVE-1/evidence/displays-baseline-20261109-083909.json` | raw 绑定 `HIE-O06` |
| ERR-140 | `DECL_GLOB` | B2 | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-141 | `DECL_RELATIVE_UNRESOLVED` | B2 | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-142 | `DECL_GLOB` | B2 | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-143 | `DECL_ENV` | B2 | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-144 | `DECL_DESTINATION_UNRESOLVED` | B2 | `verification/FEA-11-AC4-GAPS-1/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-145 | `DECL_GLOB` | B2 | `verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json` | B2 ⇒ AC7 单元修复 |
| ERR-146 | `DECL_UNKNOWN_DISPOSITION` | B3 | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json` | 别名表 `MODIFIED_IN_PLACE` → `PRESERVE_IN_REPO` |
| ERR-147 | `DECL_UNKNOWN_DISPOSITION` | B3 | `verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/RESOURCE-MANIFEST.json` | 别名表 `NOT_CREATED_NO_SCRATCH` → `ALREADY_ABSENT` |
| ERR-148 | `DECL_DESTINATION_UNRESOLVED` | B2 | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | B2 活 pin ⇒ 保留态（`FEA-11-RENDITION-1 EV-7@3eda60ac8`） |
| ERR-149 | `DECL_GLOB` | B2 | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | B2 活 pin ⇒ 保留态（`FEA-11-RENDITION-1 EV-7@3eda60ac8`） |
| ERR-150 | `DECL_MISSING_SOURCE` | B2 | `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json` | B2 活 pin ⇒ 保留态（`FEA-11-RUN-GRANT-2 EV-18@8e1883655`） |
| ERR-151 | `DECL_RELATIVE_UNRESOLVED` | B2 | `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json` | B2 活 pin ⇒ 保留态（`FEA-11-RUN-GRANT-2 EV-18@8e1883655`） |
| ERR-152 | `DECL_DESTINATION_UNRESOLVED` | B2 | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | B2 活 pin ⇒ 保留态（`FEA-12-UI-RESIDUAL-1 EV-10@323001fec`） |
| ERR-153 | `DECL_UNKNOWN_DISPOSITION` | B3 | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | 别名表 `RESTORED_IN_PLACE` → `PRESERVE_IN_REPO` |
| ERR-154 | `DECL_GLOB` | B2 | `verification/FEA-15-ACCEPT-1/resource-manifest.json` | B2 活 pin ⇒ 保留态（`FEA-15-ACCEPT-1 SRC-26@1ecd613325cf69db7900fabb5fedb2302e47e84f`） |

## 汇总

- B1 64 / B2 79 / B3 11 = 154
- 已由机制消除：B1 64（表级绑定）+ B3 11（别名 8 / raw 绑定 3）= 75
- 剩余需 AC7：B2 79 中未钉住者；活 pin 者只登记
