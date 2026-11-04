# FEA-11 AC-MATRIX（实施中；DSH 维护）

状态：**in_review**（Phase A/B/C1–C5 完成；C6 门禁证据见 `logs/dsh-C6-final.log`；AC11-1/3/7/10 如实为 PARTIAL，其余 MET）。
隔离根：`G:/CODEX/New Manga.workspace/FEA-11/`；C-17 v1.0 FROZEN（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`）。

## 证据基线（实跑）

| 命令 | 结果 | 记录 |
|---|---|---|
| `pytest tests/fea11` | **31 passed** | Phase A/B/C5 |
| `pytest tests`（全量） | **3042 passed / 0 failed / 10 skipped** | 含 FEA-09 identity 统一、conftest 冲突修复、v8 迁移 |
| `pytest tests/fea09`（多次 + 冷启动） | **142 passed** 稳定 | 物理身份归一化（`identity.py`） |
| `dotnet build` | 0 warnings / 0 errors | Release |
| `dotnet test`（全量） | **1355 passed / 0 failed / 75 skipped**（App.Tests 偶发 1 flaky，单独 671/0） | C1/C2/C3 |
| `NEWMANGA_FEA11_IPC=1` Host.Tests | **3 passed**（真实 Python Core） | `Fea11SourceIpcTests`（fail-closed / grant+scan / 全链 scan→plan→confirm→apply→ACK→resolve v2） |
| `pwsh tools/governance/check.ps1` | PASS（2 warnings） | 指针治理 |
| `pwsh tools/governance/verify_pins.ps1` | PASS 18/18 | C-17 第 18 pin |

## 逐 AC 状态

| AC | 当前证据 | 状态 |
|---|---|---|
| AC11-1 变化检测/强验证/Dirty | scan 测试：同 mtime/size 不同字节可发现；过期 grant typed 拒绝；watcher 消费者属 FEA-11-SCAN-1 | **PARTIAL** |
| AC11-2 scan/diff/plan | `test_source_scan.py`（8）：数量=明细、scope all 冻结引用、plan 预览/确认 | **MET（seam）** |
| AC11-3 页匹配（C-15 §3.2） | unique_pixel/added/missing、重复组、旧证据降级（matcher 层） | **PARTIAL**（PDF/ZIP 重排/旧库 fixture 待补） |
| AC11-4 CAS/原子性/零写 | stale 零写逐表快照、replay 拒绝、事务发布 | **MET（seam）** |
| AC11-5 守恒/tombstone/lineage | tombstone、captured_v7/legacy_unverified 冻结、relink 保序（lineage 2 测试） | **MET（seam；在途 Run/draft 交错待生产装配）** |
| AC11-6 relink/repoint/resync | 4 测试：保续/拒绝内容变/repoint 需确认/成功发布 | **MET（seam）** |
| AC11-7 缺失/诊断出口 | missing observation、tombstone 保留；管理诊断接线待 Phase C 尾 | **PARTIAL** |
| AC11-8 durable operation/双确认 | operation 恢复/伪造摘要拒绝/ACK 开门/cancel；Host journal（C1/C3：DPAPI 原子 journal、状态机、测试） | **MET（seam + Host journal 单测；真实 HostCore ACK 链待 C4 尾）** |
| AC11-9 生产链路/读图/回归 | **真实 IPC 全链 3/3**：fail-closed、Host 发 grant + ScanSourceSync、scan→plan→preview→confirm→ResyncSource→ACK→resolve（v2 键）；`test_source_resolve.py` 5 测试（键确定性/同键不同 bytes 拒绝） | **MET** |
| AC11-10 范围/冻结/证据 | check/pins 18/18、冻结契约零改动、v8 迁移测试、AC-MATRIX/Handoff；最终门禁/Review 待做 | **PARTIAL** |

## 未完成清单（收尾）
1. C4 尾：C# 构造 plan body（reference_set_digest/decisions/confirmation）+ host authorization JSON → plan→preview→confirm→apply→ack→resolve（新图 v2 键；旧键旧摘要不变）。
2. C6：全量 pytest + 全量 .NET + `NEWMANGA_FEA11_IPC=1` 一次全绿证据日志；App.Tests flaky 定位（若复现）；AC-MATRIX 终版；Handoff 更新；Task status → in_review。
3. 债务：AC11-1 watcher 消费者（FEA-11-SCAN-1）、AC11-3 PDF/ZIP 重排 fixture、AC11-7 诊断查询接线。

## 已知缺口（非阻断，登记）
- FEA-11-SCAN-1 承接定时扫描/后台调度（proposed）。
- 真实 HostCore ACK 链（C4 尾）与 C-17 未覆盖细节由 Phase C 测试验证。
