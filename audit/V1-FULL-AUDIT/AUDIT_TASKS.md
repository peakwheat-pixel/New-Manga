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

- `pytest`（Python Core 限定证据）：EXIT 1；3,519 passed / 16 failed / 10 skipped / 11 warnings；失败详情见 `logs/pytest-segment-b-20261112T081732598825Z.log`，汇总见 `reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md`
- `probes`（审计工具探针）：EXIT 1；2 项隔离 probe 确认为 Medium / High confidence 风险，1 项目录穿越覆盖预期未复现且防线已验证；详见 `reports/PROBES-RESULT-SEGMENT-B.md` 与 `reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`
- `dotnet`（Avalonia headless，8 个测试项目逐项）：`BLOCKED-TESTHOST-ACCESS`；8/8 runner EXIT 1、TRX 0 tests、status guard 8/8 identical；原始结果与 ZCode 裁决见 `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`
- `smoke-core,wire`：EXIT 1 / 程序 FAIL；10 项限定 PASS（Core 4、Wire 6）；7 项 Core 检查记 `BLOCKED-SANDBOX-GRANT`，未能执行预期 hook 行为；frontend/packaged 显式 SKIP。ZCode adjudication 与证据边界见 `reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md`
- `governance`：已在 2026-11-12 当前裁决证据 HEAD 复核，default/TaskPath、18 pins、API 退出码均为 0；最终交付前需再绑最终审计 HEAD 复跑
- `frontend/rust/desktop/npm-audit/packaged`：NOT_RUN-legacy
- 真实 GUI：BLOCKED（headless 测试不替代真实 UI 会话）
