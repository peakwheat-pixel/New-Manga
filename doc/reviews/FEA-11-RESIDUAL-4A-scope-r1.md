# FEA-11-RESIDUAL-4A scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立只读 fresh subagent（未参与 FEA-11 及承接卡实现；DSH 落盘） |
| 被审 head | `c5bd49276`（clean） |
| 结论 | **`NOT_RECOMMENDED`**（按 DSH 草案现状）；完成 §5.3 五项强制修订后 → `READY-TO-FREEZE` |
| 落盘说明 | 正文由该子代理产出；DSH 已按其 §5 冻结 R3 卡（见 `doc/tasks/FEA-11-RESIDUAL-4A.md`） |

## 0. 四条阻断理由（均独立核到 file:line）

1. **L-M4「按冻结参数重算旧证据」不是 0 pin 项**：`FEA-11-MATCH-1.md:188` 自述「需旧字节 + 新 grant」；`FEA-C17_SOURCE_SYNC_DRAFT.md:213`（`ScanSourceSync` 请求闭集只给**目标侧** `grant_ids`）、`:238`（`SourceBase` 仅 (source_id,version_id,content_digest)）；`scanner.py:540-587` 只保留首个 grant、`:324-328/401-407` 旧条目只从 DB 行读 ⇒ 实现必须动 pinned C-17（18 pins 之一）。
2. **`needs_confirmation` 在生产中零写入者（新发现，非文档既有）**：`source_sync.py:885-911` 与 `library.py:2461-2471` 两处 insert 的调用点全传 `'healthy'`（`service.py:597/620/664/696`、`importing/referenced/runtime.py:884`）；`supersede_binding`→`superseded`、`mark_binding_missing`→`missing`。后果：`service.py:536-537` 的 `defer` 不改状态 ⇒ 旧 binding 仍 `healthy` ⇒ 歧义页仍满足 **C-05 P8**（`FEA-C05_PAGE_VISIBILITY_DRAFT.md:78-83`）而可见，与 `C-17:273`「defer 后旧绑定保持 needs_confirmation」不符。
3. **AC11-7 无既有查询面**：应用面命令闭集 `core_service.py:374-383`、host-control `:355-371`、Host 侧 `HostCommandRegistry.cs:243-256` 均无 binding-status 读；`IHostController` grep `Source|Sync|Missing` 0 命中。唯一可复用：`source_get_operation` → `CommitReceipt.bindings[].status ∈ {healthy,needs_confirmation,missing}`（`FEA-C17…:255-257`、`service.py:699-708`），但**仅 operation 作用域**；Core 侧 `source_sync.py:1030-1047 tombstone_pages_of_source` 是**零调用者死代码**。若加 `IHostController` 方法 → 改 `FEA-C07_API_INVENTORY.md` → **C-07 是 18 pins 之一** → 1 pin（与 0 pin 矛盾）。
4. **治理前置被低估**：`check.ps1:838-845` 规定 `[x] <<MET>>` **不得带原因**（limitation 只能进 closeout/ADJ）；`doc/STATUS.md:8`、`doc/REBASELINE_PLAN.md:53` 仍写 HOST-AUTH-1 `closed_with_limitations`（实际已于 `5cbec0e82` 翻 done）→ 需一并修正。

## 1. FEA-11 九条未勾选 AC 三分类

### 1.1 可仅回填 MET（5 条）
| AC | 证据锚点 | 限制 |
|---|---|---|
| AC11-1 | `FEA-11.md:243-247` 终态裁决（MET 带 limitation）；SCAN-1 `7080167e1` / WATCH-1 `00083a977` / SCAN-2 `555f57b8d`；`tests/fea11/test_source_scan.py` | **L-STARTUP → 子项 `NOT_APPLICABLE`（契约解释+产品范围，保留 NOT_RUN）** |
| AC11-3 | `FEA-11-MATCH-1` done（`FEA-11-MATCH-1.md:244`）；`scanner.py:376-381/802-887`、`matcher.py:66-88` | **L-M1（PDF 插页）→ BLOCKED 具名 re-home，不得 NA**；L-M4 → re-home |
| AC11-4 | `FEA-11-AC4-GAPS-1` done（`FEA-11.md:236`，delivery `2d9a4a219`）；`tests/fea11/test_source_sync.py` | L-5 已由该卡关闭 |
| AC11-5 | `FEA-11-LINEAGE-1` done（`:121-123`、r4 `:169/:186-187`）；`test_source_rendition_run.py:551`、`test_source_sync.py:1445-1462` | 引用 LINEAGE-1 的 L1/L6/L7/L10/L11；**L10（真实 AD-003 纯图源被 managed 门槛拒绝）须写明未覆盖** |
| AC11-8 | `FEA-11-HOST-AUTH-1` 已 done（`:6`、`:140-145`）；承接 `FEA-11-HOST-AUTH-2` `f7016d3fb`（ACK fresh + gated 2/2 + 二次 0 帧） | **崩溃点矩阵 `NOT_RUN` → 已 re-home `FEA-11-HOST-AUTH-3`；不得写 PASS** |

### 1.2 需新做（4 条）
- **AC11-6**：folder relink typed 拒绝**无测试**（`test_source_relink.py` 全为 zip 容器）；成员重排/多项目**无用例**；folder 走 repoint/resync 的逃生路径**无证据** ⇒ 纯测试 + `L-S4-2` 登记（不改 Core 语义）。
- **AC11-7**：见 §0-3（需 DSH 裁决；0 pin 只能 operation 作用域）。
- **AC11-9**：现有 gated 用例**Core 直连**、未走 HostRuntime/dispatcher、且 sync 前未 resolve 旧绑定 ⇒ 纯测试（有 `Fea09ProductionFixture` 先例）。
- **AC11-10**：证据/manifest 停在旧 head；r1–r7 全 `changes_requested`，最终 head 无 approved Review ⇒ 流程/证据。

### 1.3 需 NA：**0 条整 AC**
仅 L-STARTUP 子项可 NA；`L-M1` 按 ADJ W-09 为 **BLOCKED 不 NA**；L-11 flaky 不属节点 AC；W-12 非本节点。**R3 不得把任一整 AC 写 NA。**

## 2. AC11-7 最小可行方案（评审建议，DSH 采纳）
1. Host 只读投影：从 durable journal 的 `Operation`/`CommitReceipt` 取 `bindings[].status ∈ {missing,needs_confirmation}`（需给 `SourceOperationCoordinator` 加只读枚举；当前仅 `Get(operationId)` `:528`），**不新增 Core 命令、不进 `IHostController`**；
2. Core 死 seam `tombstone_pages_of_source`（`source_sync.py:1030-1047`）接线或删除（二选一，写明结论）；
3. 断言「不扩 V(p,t)」：缺失页在 reader/`list_chapter_pages` 投影仍不可见（P8）；
4. 明文限制：**operation 作用域**（无全局枚举）+ **`needs_confirmation` 零生产者缺陷登记** → re-home `FEA-11-DIAG-SURFACE-1`（需 C-17 additive）。

## 3. AC11-9 最小增量（评审）
- 复用 **`Fea09ProductionFixture.cs:11-118`**（csc 编译 launcher + 跑仓内当前 `src` 的 Core，绕过过期 bundled sidecar；门禁 `NEWMANGA_FEA09_IPC=1`）。**更正草案事实：仓库不存在 `Fea11ProductionFixture`。**
- 经 `HostRuntime.Commands.InvokeAsync`（`HostRuntime.cs:154`、`HostCommandDispatcher.cs:128`）走生产 dispatcher + Registry durable 授权；**sync 前** `ReadPageImageAsync` 读旧绑定（记录 resource id + sha256），**ACK 后** resolve 同页断言新键/新字节 + 旧资源键/摘要不可变（DB 行级，沿用 `RunPythonAsync` 查库手法）；源 hash/mtime/文件数守恒；缺能力/撤销 fail-closed；skip 原因登记。

## 4. L-M4 与 AC11-6 / L-S4-2 判定
- **L-M4**：不可 0 pin 实现（见 §0-1）→ **口径裁决 + 具名 re-home `FEA-11-LEGACY-RECOMPUTE-1`**（需 C-17 UNFREEZE + 新 capability）；R3 不得写「已按冻结参数重算」。
- **AC11-6**：fail-closed 复核成立（`service.py:467-478`：folder relink 缺 `container_facts` → `SOURCE_SYNC_STATE_CONFLICT`）；C-17 `:278` 允许「无法证明同一 → 转 repoint」，故**不是违约**；`L-S4-2` 确认成立（`runtime.py:986-991` 用首成员 facts vs `C-15:216` 目录 identity）→ **补 4 类用例 + 登记缺陷**即可判 MET（带 limitation），不改 Core 语义。

## 5. 冻结口径（DSH 采纳）
AC-R3-1（AC11-7 投影 + 不扩 V + 死 seam 处置 + 缺陷 re-home）；AC-R3-2（AC11-9 Host 级 gated 全链路 + 旧/新字节不可变 + 守恒 + fail-closed）；AC-R3-3（AC11-6 四类用例 + L-S4-2 登记）；AC-R3-4（L-M4 裁决 + re-home，不得写完成）；AC-R3-5（AC 回填与翻转：MET 不带原因、L-STARTUP 子项 NA、L-M1/L-M4 re-home）；AC-R3-6（证据/治理 + 修正 STATUS/PLAN 的 HOST-AUTH-1 陈旧表述 + 最终 head 独立 Review）。

## 6. 预计成本与不确定
- 实现 2–3 轮 + 审查 2 轮；pytest +4~8、.NET gated +2~4；生产代码 0（推荐）或 2 文件（Host journal 枚举）。
- **不确定**：旧 v2 键在 supersede 后能否仍可读（需卡内探针先定断言形式）；Host 级 gated 用例本机稳定性/flake（L-11 先例）；真实旧库是否曾写入 `needs_confirmation`（代码无生产者，需真实库核对）；AC11-1 的「整 AC MET + L-STARTUP 子项 NA」双口径需在 R3 写清。
