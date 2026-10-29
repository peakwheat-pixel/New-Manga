# V11R-F0-1 契约差异与偏差记录

对照基线：`doc/tasks/V11R-F0-1.md`、审计 §5/§5.1、`doc/plan/V11R_AVALONIA_CONTRACT.md`（FROZEN）。

## 1. 命令面差异

| 项 | 基线（审计 §5 / Registry） | 本任务 | 性质 |
|---|---|---|---|
| Region 命令数 | 6（C042–C047） | 16（+10） | 追加，C042–C047 语义逐字节不变 |
| Host 注册命令总数 | 66（冻结 Rust 快照） | 76 = 66 冻结迁移集 + 10 追加集 | 快照 JSON **未编辑**；追加集由 `HostCommandRegistry.RegionWriteCommandNames` 显式声明 |
| 新增命令 | 无 | `create_region` / `delete_region` / `save_region_geometry` / `merge_regions` / `split_region` / `reorder_regions` / `save_manual_translation` / `confirm_region_final` / `set_region_lock` / `pin_revision` | 均 core 通道、同名 Core wire 命令 |
| 契约编号 | C001–C066 | 追加 **C067–C076**（本文件即其引用节；总契约 `V11R_COMMAND_CONTRACT_V1.md` 由 V11R-A-3 维护） | 经 Lead 批准的拆分 |

## 2. 协议版本策略差异（明确裁定）

- **基线惯例文本**（历史文档，如 `M2-RC4_DOMAIN_COMMANDS.md`）写“新增命令 → envelope minor bump”。
- **本任务决定**：10 条命令全部 **minor=3（零 bump）**，Core `PROTOCOL_MINOR` 保持 3。
- 依据：当前源码中 Core 的严格 minor 门只覆盖 Create（8）/Delete（10）/P15 settings（7）三族；
  Region 族按 major=2 受理任意整数 minor；`cleanup.*`/`backup.*`/`plugins.*`/`rerender_page`/
  `list_region_revisions`/`resolve_page_resource` 等后加命令面都落在 minor 3（已固化先例）。
  bump 会变更所有客户端声明的 envelope 版本，属本任务未授权的共享契约变更。
- 影响：V11R-A-3 总契约中 C067–C076 的 `minor` 列必须写 **3**，不得写 4/11 等。

## 3. AC7 偏差（经 Lead 批准）

任务卡 AC7：“契约文档更新（与 V11R-A-3 命令契约合并）”。
Lead 裁定（2026-10-30 协调消息）：`doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 归 core-bridge
（V11R-A-3），本任务**不得**修改该文件，只写独立
`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`；A-3 在总契约中添加 C067–C076 节引用本文件。
本任务按此执行。

## 4. 与既有 RC4/retpye 命令的兼容性（已验证）

- C042 `set_region_type`：未改 handler/语义；`RegionLookupError` 仅增加可选 `message` 参数
  （默认 "region not found"，既有调用与 wire 消息完全不变）。
- C043 `list_regions`、C044 `list_region_revisions`、C045 `restore_region_revision`、
  C046 `rerender_page`、C047 `resolve_page_resource`：未改。
- `RegionEditingService` 既有公开方法签名只加 keyword-only 默认参数，既有 Python 调用点零变化；
  全量 pytest 2661 passed 为回归证据。

## 5. 数据安全相关差异

- 既有 `save_manual_translation` 只写文本级 translation lock（GAP-3，未改）；
  新 `set_region_lock` 同步文本级 + Region 列两份投影（见契约 §2 C075 / GAPS GAP-3）。
- 无任何命令删除/upsert 历史 revision；`delete_region` 仅软删、`pin_revision` 仅翻 `is_pinned`。
- 未新增对用户源文件 / Managed Copy / OS 路径的读写。

## 6. 未实现项（诚实声明，见 GAPS.md）

- GAP-2：Region 文本只读投影仍缺（超范围，需 follow-up 决策）；
- GAP-5：`IHostController` 便捷方法不在本任务（写权归属 core-bridge）；
- 未做 UI/ViewModel、未接 Studio Page 视图（由 ui-studio 任务消费本契约）。
