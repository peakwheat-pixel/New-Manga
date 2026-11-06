# CONTRACT-UNFREEZE-2026-11-06-C17：C-17 v1.1（冷启动扫描目标枚举命令层）

> 载体用途：按 [C-17 冻结记录](../plan/FEA-CONTRACT-FROZEN-C17.md) 的 UNFREEZE 流程，提出 C-17 v1.1 字节修订；须经独立上下文 fresh subagent 做 byte-level 复核 + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「让 Codex 判断下一部任务，由 DSH 执行」→ Codex 裁决 `NEXT-TASK=FEA-11-SCAN-2`（先独立 scope review，优先 B1）；scope review `doc/reviews/FEA-11-SCAN-2-scope-r1.md` 结论 **READY-WITH-UNFREEZE**、推荐 B1；DSH 裁决 B1 采纳 / S-1 取选项② / S-2 采纳 / S-4 登记 limitation。
> 授权链：用户 2026-11-06 指令（Codex 决定、DSH 执行）→ Codex 明确「B1 按 C-17 v1.1 正式 UNFREEZE/重冻，更新现有 C17 pin，仍 18 pins」。
> 顺序约束：本载体与 C-17/冻结记录/矩阵为 UNFREEZE 提交；SCAN-2 运行时实现另卡（`FEA-11-SCAN-2`）另起 commit。

## 1. 背景与目标

SCAN-1（done，`7080167e1`）只覆盖「本会话导入后的目标」，重启后目标集为空（L-A）。SCAN-2 需在冷启动后由 **Core 权威枚举**给出可扫描目标，Host 再用持久 registry 核验授权、取得 locator、铸造新会话 grant。scope review 已证明：

- **B1 可行**：Core 已持有 `source_id/source_kind`（`schema.py:619-626`）、`registry_id/generation/identity facts/content_digest`（`:629-645`、`library.py:2276-2291`、`source_sync.py:656-665`）、`project_ids`（`page_bindings:698-724`、`source_sync.py:427-463`）、`identity_digest_of`（`model.py:255-268`）。只缺一个只读枚举命令 + C-17 登记；无 schema/migration；M2-C1 无增量。
- **B2 不推荐**（无法覆盖升级前旧库、复制 Core 业务事实、需对账）。
- Host registry 已持久化/可恢复（`SourceAccessRegistry.cs:13-52,98-139,141-173`），但不含 source_id/project_ids/kind 映射；`identity_facts` 字段从未写入，本卡不使用。

## 2. 提议修订（C-17 v1.1）

### A. 头部与 §0 版本
- 头部状态行：`DRAFT v0.1 / 未冻结` → `FROZEN v1.1 / 2026-11-06 UNFREEZE 重冻`（同时修正 v1.0 冻结记录与 header 的既有漂移；v1.0 冻结见冻结记录）。
- §0 表「文档」行：`C-17 v0.1；候选冻结版本 v1.0` → `C-17 v1.1（v1.0 已冻结 2026-11-04）；本修订走 UNFREEZE 载体 doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md`；并在 §0 末尾追加一句：「v1.1 仅新增冷启动扫描目标枚举只读命令 `source_list_scan_targets` 及其 DTO；不改变既有命令/守卫/错误闭集/§6 CAS/§7 lineage。」

### B. §4 命令版本、能力与兼容
- `core.ping.capabilities` additive 列表追加 `source.sync.enumerate/1`。
- 明确：**§5.2 `Capabilities` DTO 仍恰好 7 项**（scan/plan/apply/relink/repoint/resync/operation），**不新增第 8 项**；枚举能力只经 `core.ping` 列表公告，Host 以 ping 列表判定；缺失 → `CORE_CAPABILITY_MISSING`，不得以 UNKNOWN_COMMAND 探测。
- 明确枚举命令走 **application 面**（非 host-control）；Host 内部直连，不登记 HostCommandRegistry/C-07，不新增 UI 命令面。

### C. §5.1 命令表新增一行
| `ListScanTargets` / `source_list_scan_targets` | `{}`（closed shape；未知键拒绝） | `ScanTargets` | 只读枚举；零 DB 写、不建 plan/apply、不铸 grant；失败按 §8 闭集 |

### D. §5.2 DTO 新增两行
| ScanTarget | source_id! ID; registry_id! ID; generation! G; source_kind! ID; identity_digest! H; project_ids! ID[] |
| ScanTargets | targets! ScanTarget[]（按 source_id 升序、唯一；空数组合法） |

（**去掉**草案 `identity_facts`；`version` 不是 Core 事实，排除；`source_kind` 补入；`project_ids` 1..20 唯一按 ID 排序规则沿用 §5 类型缩写与 §5.3。）

### E. §5.3 组合守卫与界限追加
- 枚举只读：单次 SELECT 级投影，零写；不产生 scan/plan/operation/receipt/grant/journal。
- `targets` 按 `source_id` 升序、唯一；`source_id` 必须来自 Core `sources`（`src-<uuid>`），禁止 Host 用 `StableSourceId`/folder registry_id 冒充（S-2）。
- 每 target 的 `identity_digest = identity_digest_of(location facts)`（`model.py:255-268`）；location facts 缺失/损坏 → 该 target **typed skip**（不伪造 identity）；超过数组上限 10000 或 8MiB → `SOURCE_BUDGET_EXCEEDED`（不静默截断）。
- registry 缺失/撤销/代次不可核验由 **Host** fail-closed（`CORE_CAPABILITY_MISSING` 或既有 registry 错误），Core 枚举不返回未授权结论；Core 不返回路径/secret/grant。
- 生产 file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` 属 fail-closed（S-1 选项②：**不**声称"启动前缺失 → missing"，L-G 保留）。

### F. §8 / §9
- §8：**不新增错误码**；复用既有闭集（`INVALID_REQUEST`、`SOURCE_BUDGET_EXCEEDED`、`CORE_CAPABILITY_MISSING` 等），并在 §8 表后注明本命令零新增。
- §9：追加 P3（只读/无副作用）、P7（Host registry 核验授权，不凭 Core 返回直接使用 locator）、P8（脱敏：不返回路径/secret/异常原文）的适用声明。

### G. 冻结记录/矩阵
- `doc/plan/FEA-CONTRACT-FROZEN-C17.md`：sha256 更新为 v1.1 实际字节；增补 v1.1 修订记录（触发/授权/复核 r1…、最终 pin）；保留 v1.0 历史 sha `86b89ff8…`。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-17 行 `DRAFT` → `FROZEN v1.1`（2026-11-06）。
- `verify_pins.ps1`：**18 pins**（pin #18 重算），其余 17 契约与 ADJ-001 字节零 diff。

## 3. 兼容与影响
- 旧 Core（无 C-17 v1.1）→ `core.ping` 无 `source.sync.enumerate/1` → Host fail-closed；不因全局 minor=3 推断支持。
- 新 Host × 旧 Core：既有同步命令与 SCAN-1 周期扫描不受影响（旧面继续，枚举不可用）。
- 无 schema/migration/依赖；无 M2-C1/C-16/C-15/C-06 字节变化；不影响 SCAN-1 已交付行为。
- 旧 v7 Core 的 schema gate、C-16 导入、C-15 读规则不变。

## 4. 风险与回退
- 风险：①18 pins 之一重冻，须独立 byte-level 复核；②Capabilities DTO 7 项约束不得违反；③枚举结果集合大小/潜在大库 IO 需实现侧预算（本契约只给上限与 typed 错误）；④S-1 registry resilience 未解决（limitation 保留，另立缺陷卡）；⑤S-4 死代码 `refresh_source_location_auth` 未修（limitation）。
- 回退：若独立复核否决或用户要求回退，恢复 C-17 v1.0 字节（sha `86b89ff83c9a818311d9d7f498a83e7984a77856cddc8b60bf9308bfb10f2c36`）与冻结记录/matrix；SCAN-2 实现卡不释放。

## 5. 独立复核要求
- Reviewer：未参与本提案/实现/前轮复核的 fresh subagent；只读；记录 session。
- 复核对象：**最终字节**（工作树）C-17 v1.1、冻结记录、矩阵与本载体；核对 §2 各项是否真实落地、pins 18/18、其它 17 契约零 diff、Capabilities DTO 7 项不变、无新错误码、无 schema/依赖变化。
- 通过标准：APPROVE（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 提交（本载体 + C-17 + 冻结记录 + 矩阵），再冻结/释放 SCAN-2 实现卡。
