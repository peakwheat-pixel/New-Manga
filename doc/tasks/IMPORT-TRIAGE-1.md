---
id: IMPORT-TRIAGE-1
title: REPACK-5 导入 BLOCKED 诊断（HEAD 回归 vs 数据根）
kind: diagnosis
governance_version: 3
status: done
approval: user_authorized_2026-10-28_diag
suggested_owner: route-research
owner: route-research
reviewer: dsh
depends_on: []
base_commit: 3be9ff938
branch: task/IMPORT-TRIAGE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/IMPORT-TRIAGE-1
integration_commit: 87fdc2246
delivery_head: 24e5a3f04ce66f81f8f14639a4a4568fa5005231
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/IMPORT-TRIAGE-1
allowed_paths:
  - doc/tasks/IMPORT-TRIAGE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/IMPORT-TRIAGE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/IMPORT-TRIAGE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/IMPORT-TRIAGE-1/**
---

# IMPORT-TRIAGE-1：导入 BLOCKED 诊断

## 背景
RELEASE-REPACK-5（HEAD \6120f91e5\，含三布局主题合并）真机烟测中**导入失败**：UI 状态卡「正在导入文件…」>40s、DB pages 不增、wire 仅 \RegisterImportSource\/\RevokeImportSource\、**无 \ImportPages\**。书架/工作台/默认主题/重复 fixture 均可复现；\ImportExportPanels/HostController\ 相对 REPACK-4 无 diff。REPACK-4（\
1b89c5e5\）同流程导入正常（9→10 页）。

## Acceptance Criteria
- [x] **AC1 干净数据根复测**：用**全新空数据根**（非 REPACK-4 副本）执行一次真实 UI 导入（fixture 书），记录 wire 帧（须出现 `ImportPages` 或明确错误）。 <<MET>>
- [x] **AC2 判定**：干净根成功 → 结论「数据根/catalog 状态导致」；仍失败 → 结论「HEAD 回归」并继续 AC3。实际：干净根成功 ⇒ **非 HEAD 回归**。 <<MET>>
- [x] ~~AC3 二分定位~~（仅回归时）：在 `f1b89c5e5`（REPACK-4，导入正常）与 HEAD 之间二分，重点怀疑三布局主题合并对 `Pages.cs/MainWindow.axaml(.cs)` 的替换，给出首个失败提交与根因。 <<NOT_APPLICABLE: AC2 判定非回归，无需二分>>
1b89c5e5\（REPACK-4，导入正常）与 HEAD 之间二分（重点怀疑三布局主题合并对 \Pages.cs/MainWindow.axaml(.cs)\ 的替换），给出首个失败提交与根因（如页面 host/事件接线、\ImportPages\ 未发出）。
- [x] ~~AC4 修复或隔离~~：若为产品回归且可安全修复 → 最小修复 + 测试（headless 覆盖真实接线）+ 真机复验；否则给精确 root cause + 建议补丁范围。 <<NOT_APPLICABLE: 无回归，无需产品修复；烟测硬化建议见 REPORT §4>>
- [x] ~~AC5 门禁~~：修好时 `test.ps1` ≥249、pytest 无新增、check PASS、64-hex pin、Handoff（含 Evidence 与 Record Decision）。 <<NOT_APPLICABLE: 无代码改动，check.ps1 PASS、pin 已入库>>

## 允许修改范围
\pps/desktop-avalonia/**\（仅诊断/最小修复）、本卡、STATUS/PLAN/LEDGER、\
erification/IMPORT-TRIAGE-1/**\、workspace。

## 禁止范围
不改 Core/协议/Host 契约/旧壳、不 push、不 gc/prune、不伪造证据；**禁止 \git add -A\**。


## 结论（2026-10-28）

**非 HEAD 回归、非数据根/catalog 缺陷，产品无需修复。** REPACK-5 干净根真实 UI 导入成功：`RegisterImportSource`→`ImportPages`（16–18 ms），pages 8→9；**与烟测完全同 sha 的输入文件**（`ui-import-2.png`, sha256 `e1b6787b…`, 134 B）导入成功。烟测 BLOCKED 为烟测脚本/安装环境产物（grant 有效 299 s、同秒 client revoke、无 ImportPages）。详见 `verification/IMPORT-TRIAGE-1/REPORT.md` 与 Handoff。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| R1 | AC1-AC4 | verification/IMPORT-TRIAGE-1/REPORT.md | - | e1cc4e0a7b00e419f38ee839dc6942f5845acbaae1d08fd47633260b0b12ee27 | CANONICAL |
| R2 | AC1/AC2 | verification/IMPORT-TRIAGE-1/evidence/evidence.json | - | 246b00e9e37734253b83c16957d8cc736260273352945db440828b618fe98912 | CANONICAL |
| R3 | AC1 | verification/IMPORT-TRIAGE-1/evidence/ac1-fixture.json | - | 64e50036f721a9144e576f3b166c81eaceae47d9ba9a6c687cee5db1a2de3d18 | CANONICAL |
| R4 | AC1 | verification/IMPORT-TRIAGE-1/evidence/logs/core-service.wire.ndjson | - | c1fa0f82db715ead7e979c49fa8b54ab77bbda6eb1967be27b736921b2ec9d36 | CANONICAL |
| R5 | AC1 | verification/IMPORT-TRIAGE-1/evidence/logs/host.log | - | 44d48db0bfd6497465891172a9acf842133cf88cef02c39f89c1a9d73fe69148 | CANONICAL |
| R6 | AC1 | verification/IMPORT-TRIAGE-1/evidence/grants/import-20261028T011658627.json | - | a805e833a6999bd69fd4754da7ee7eb3c75b6a8119c08abbba28e71a25127d92 | CANONICAL |
| R7 | AC1 | verification/IMPORT-TRIAGE-1/evidence/grants/import-20261028T012110946.json | - | e1d7288753750c7afde7decec932838004227d75e723510868570c019216400e | CANONICAL |
| R8 | AC1 | verification/IMPORT-TRIAGE-1/evidence/screens/01-bookshelf.png | - | a355e288b3f78f4961c9a64a92e1a22c4bf24a57da2857b81a0c0122c27d3372 | CANONICAL |
| R9 | AC1 | verification/IMPORT-TRIAGE-1/evidence/screens/03-import-panel.png | - | bb077143fc9e3089185e7d258b362955a5357ca9edb5a061d9ceb9d83e70a72b | CANONICAL |
| R10 | AC1 | verification/IMPORT-TRIAGE-1/evidence/screens/04-import-result.png | - | 394436b52a1d1015c2420fd31de17f319fd668104a683254db263cb41c01139c | CANONICAL |
| R11 | AC1 | verification/IMPORT-TRIAGE-1/evidence/screens/06-tiny-result.png | - | f41b9303908f13a14e8de21387f9ea54bc38d89e20e81a74e25e82ee62ffb6ab | CANONICAL |
## Review（DSH 集成复核，2026-10-28）— PASS

- **结论：非 HEAD 回归、非数据根/catalog 缺陷，产品无需修复。**
- AC1：new-test-book.ps1 全新空数据根（8 页）真机 UI 导入 → wire RegisterImportSource -> ImportPages（16-18ms）、DB 8->9 页；烟测同 sha 输入（ui-import-2.png，134B）亦成功。
- AC2：干净根成功 => 非回归；AC3/AC4 N/A；AC5：check.ps1 -TaskPath PASS、11 份证据 pin。
- 烟测失败签名：grant 注册后剩 299s（未过期）、同秒 client RevokeImportSource、无 ImportPages => 烟测自动化/安装环境半途 revoke；REF_MALFORMED 未能本地复现（已如实记录）。
- 建议：烟测脚本断言三选择器可用 + 点 ImportStartButton 后断言状态行与 DB 增量。
- 集成：87fdc2246。
