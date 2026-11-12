# 专项状态

## 段 A（历史基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`）

- AUDIT-00: PASS（仅段 A 基线与清单；语义覆盖后续核对）
- AUDIT-01–14: NOT_TESTED（未完成；不迁移为段 B 结论）

## 段 B（当前产品基线 `10e4ee013835605800d3830fb960ae8d3aa04167`）

- AUDIT-00: PASS（当前 Git/environment/source inventory；边界见 `reports/00_BASELINE-SEGMENT-B.md`）
- AUDIT-01: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-02: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-03: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-04: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-05: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-06: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-07: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-08: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-09: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-10: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-11: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试；含私有素材传播风险调查；不作远端处置）
- AUDIT-12: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-13: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）
- AUDIT-14: BLOCKED-ORIGINAL-CHECKLIST-MISSING（未测试）

## 段 B suite 级状态（与 AUDIT-01–14 逐项状态分离）

- `pytest`（Python Core 限定证据）：NOT_RUN
- `probes`（审计工具探针）：EXIT 1；2 项隔离 probe 确认风险，1 项目录穿越覆盖预期未复现；severity pending，详见 `reports/PROBES-RESULT-SEGMENT-B.md`
- `dotnet`（Avalonia headless，8 个测试项目逐项）：NOT_RUN；仓库默认 `obj/project.assets.json` 8/8 存在
- `smoke-core,wire`：NOT_RUN
- `governance`：已在 2026-11-12 当前裁决证据 HEAD 复核，default/TaskPath、18 pins、API 退出码均为 0；最终交付前需再绑最终审计 HEAD 复跑
- `frontend/rust/desktop/npm-audit/packaged`：NOT_RUN-legacy
- 真实 GUI：BLOCKED（headless 测试不替代真实 UI 会话）
