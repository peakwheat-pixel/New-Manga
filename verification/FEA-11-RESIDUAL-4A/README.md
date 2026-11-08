# FEA-11-RESIDUAL-4A：证据索引

> 卡片：`doc/tasks/FEA-11-RESIDUAL-4A.md`（AC-R3-1…R3-6）。本目录只放**门禁日志与 needed evidence**；Canonical EV / Resource Manifest / Delivery Manifest 由 **DSH closeout** 生成（本卡不伪造 EV）。

## 结构

| 路径 | 内容 |
|---|---|
| `DEFECTS.md` | 缺陷、L-M4 裁决、re-home 清单、限制（D-1…D-7；D-1a/b/c 修复记录与 before/after） |
| `tools/build_plan_body.py` | AC-R3-2：从真实 scan JSON 构造显式 `bind` 的 PlanBody（复用 `tests/fea11/conftest.py` 构造规则） |
| `tools/inspect_state.py` | AC-R3-2：只读查询隔离 v8 库（bindings/entries/rendition_cache/pages/versions/locations） |
| `tools/probe_png.py` | AC-R3-2：解码生产服务返回的 rendition（尺寸/像素/sha256） |
| `evidence/after-full-chain.txt` | **修复后** gated 全链真实输出（`scan_via=dispatcher`/`apply_via=dispatcher`，无 defect key） |
| `evidence/after-failure-record.txt` | **修复后** `source_record_operation_failure` 失败路径输出（D-1c） |
| `evidence/d-1-fixed-wire.txt` | **修复后** wire：`ScanSourceSync`/`ResyncSource` payload 字段平铺 |
| `evidence/dispatcher-defect-wire.txt` | **修复前** wire before 证据（已订正归因：`<invalid frame>` 是 D-1b ping 帧；D-1a 为客户端异常） |
| `evidence/real-ipc-full-chain.txt` | 修复前主链路输出（保留为 before 证据，含 fallback defect key） |
| `evidence/real-ipc-capability.txt` | 缺能力 fail-closed 真实运行输出（零 wire 帧） |
| `logs/pytest-fea11.log` | `pytest tests/fea11 -q` |
| `logs/pytest-full.log` | `pytest tests -q`（全量） |
| `logs/dotnet-host-tests.log` | `dotnet test …/NewManga.Host.Tests.csproj -c Release`（定向；含 skip 原因） |
| `logs/dotnet-full.log` | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`（全量） |
| `logs/fea11-ipc-r4a.log` | `NEWMANGA_FEA11_IPC=1` 定向 `Fea11Residual4AIpcTests`（全 dispatcher 4 用例） |
| `logs/mutation-m{1,2,3}.log` | AC 层变异自检（删 folder 拒绝 / ack 前放行 gate / 投影返回全部页） |
| `logs/mutation-d1-m{4,5}.log` | D-1 层变异自检（dispatcher 嵌套 / capability ping 未闭合） |
| `logs/mutation-d1c.log` | D-1c 变异自检（`RecordSourceOperationFailure` 嵌套；gated + 哨兵双 RED） |

## 运行环境

- Windows 本机；`C:/Python314/python.exe`；.NET 9 Release。
- 隔离根：`G:/CODEX/New Manga.workspace/FEA-11/fixtures/r4a-production-<guid>/`（不进仓库；`ipc_seed.py` 只允许该前缀）。
- gated 门禁：`NEWMANGA_FEA11_IPC=1`（默认 skip 并给出原因）。

## 结论摘要（详见卡片交付记录）

- AC-R3-1：Host journal 只读投影 + 死 seam 删除 + 不扩 V(p,t)；`needs_confirmation` 零生产者 re-home `FEA-11-DIAG-SURFACE-1`。
- AC-R3-2：真实 Host/Core 全链路（全 dispatcher：scan→plan→preview→confirm→apply→ACK→resolve；新 v2 键/新字节/旧摘要不可变/源守恒/撤销与缺能力 fail-closed）。**D-1a/D-1b 已修复（`5c2ac5eeb`）；D-1c（P1-1 残留）已修复（`RecordSourceOperationFailure` payload 平铺）**，均有 gated/哨兵判别测试与变异证据。
- AC-R3-3：folder relink typed 拒绝、folder resync 逃生、SC-S11 保序、多项目不误改；`L-S4-2` 登记。
- AC-R3-4：L-M4 不实现，re-home `FEA-11-LEGACY-RECOMPUTE-1`；L-M1 re-home `FEA-11-PDF-RECONCILE-1`。
- AC-R3-5：`doc/tasks/FEA-11.md` AC11-1…10 → `<<MET>>` + `status: done`（append-only 登记）。
- AC-R3-6：日志/证据落盘；HOST-AUTH-1 陈旧表述核对为已修正（无需改）。
