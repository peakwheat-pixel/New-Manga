# 12 整改与验证路线（Codex 裁决后版本）

本计划是在审计授权范围内形成的建议，**不授权本 Task 修改产品代码、契约、Schema、依赖、远端或用户数据**；修复必须由新的 Task 冻结范围。R1–R4 表示建议处理顺序，不等同于 P0–P3 severity。候选处置已由 Codex 最终 Review（`reports/CODEX-FINAL-REVIEW-2026-11-13.md`）作出：4 项 finding、4 项 INVESTIGATE、1 项 accepted limitation、2 项 close。

## R1：数据安全与发布暴露风险（最高优先级，Codex 维持）

| 工作项 | 当前证据与根因状态 | 影响文件/范围 | 建议改动与依赖 | 风险 | 验收与回归 |
|---|---|---|---|---|---|
| SEC-01：AUDIT-11-INC-001 传播风险调查 | 本地历史证据支持高置信推论；远端当前可见性未知，不能断言仍公开。**Codex 维持 INVESTIGATE，不分配 severity。** | Git 对象/历史与发布来源；对象范围见 `reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md`。 | 由独立、授权范围冻结的安全/集成 Task 固定只读核验目标、时间、方法与允许边界；本计划不执行远端请求、删除或重写。 | 过早清理破坏取证；不澄清则分发风险无法判断。 | 记录可复核的远端可见性结论；任何删除/rewrite/通知/补救需另行显式 Task 与审查。 |
| SEC-02：SEG-B-PROBES-001 containment | junction probe 实测新 revision bytes 可越出 managed root；锚点 `managed_storage.publish` 缺 containment/reparse walk。 | `src/infrastructure/filesystem/managed_storage.py:115-124`；实现范围由修复 Task 冻结。 | 写入前增加与 remove_managed / nmbak 等效的 containment/reparse 防线；先复核 ReferencedSource / Managed Copy 调用边界。 | 仅词法检查仍可能被 junction/reparse 绕过；扩大删除路径会改变保护语义。 | 隔离临时目录建 managed/books junction，断言 publish 不在 root 外创建文件；普通 Managed Copy 成功、已有目标不覆盖、外部文件未改；路径变体回归 + Core/Host tests。 |
| SEC-03：SEG-B-PROBES-002 恢复失败语义 | 隔离磁盘写失败在 DB 已切至备份点后抛裸 OSError；pre_restore 包保留但错误无 rollback ID。 | `src/infrastructure/sqlite/nmbak.py:1180-1210`；上层 Core/wire 映射待 tracing。 | 将文件 I/O 失败收敛到冻结错误合同（如 `BACKUP_RESTORE_INCOMPLETE`）并返回可用 pre_restore `backup_id`；先核对 C-07 / nmbak 冻结语义。 | 失败清理可能误删唯一恢复包；未经合同裁决不得改共享字节。 | 故障注入验证错误为 typed、含 rollback ID、pre_restore 包可用；覆盖单/多文件失败、数据库状态、重开恢复与既有成功 restore；不改冻结契约字节。 |

## R2：核心资源与状态可靠性

| 工作项 | 当前证据与根因状态 | 影响文件/范围 | 建议改动与依赖 | 风险 | 验收与回归 |
|---|---|---|---|---|---|
| CORE-01：NM-AUD-0001 sidecar 生命周期 | 受控 helper 经实际 SidecarProcess API 复现取消/Dispose 后仍存活；真实 sidecar 行为未知；**Codex 维持 P2**。 | `apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs`；`HostBridgeClient.cs`；`HostRuntime.cs`。 | 新实现 Task 建立幂等 stop/cleanup 所有权；spawn 后取消/异常接入 finally；明确 HostRuntime shutdown 次序。 | 错误的 kill/超时处置影响正常 sidecar 关闭与 Host 生命周期。 | helper 覆盖 pre-cancel、spawn 后 cancel、EOF 正常退出、忽略 EOF 超时、Host shutdown；断言 dispose 后 child/tree 已退出；恢复 Avalonia TestHost 对应测试。 |

## R3：功能、交互与交付行为

Codex 裁决后，以下 3 项已确认 finding，可按各自范围释放实现 Task；`AUDIT-05/06/14-002` 维持 INVESTIGATE，必须先有需求裁定，不得按候选文字直接改代码。

| 已确认 finding / 待调查项 | 裁决 | 根因/需求状态 | 可能影响范围 | 下一工作与验收 |
|---|---|---|---|---|
| `AUDIT-07-CAND-001`（P2） | finding | 定向测试 127 passed / 3 failed：ZIP `store`、JSON text override、空 options 的 hook audit events 不符预期；不涉及排版像素。 | reader export hooks/options 与 audit events。 | 独立实现 Task 修正有效 options 与 hook 事件；ZIP/text override + 空 options audit event 的 unit 与真实 export 回归。 |
| `AUDIT-09-CAND-001`（P3） | finding | 合成空章节路径中界面显示已选作品/章节，Retry 却提示先选择；根因与普遍性未知。 | V2 Library selection、Reader retry state。 | 隔离 Host/UI fixture 复现有页/零页、切换作品/章节、Retry/返回；按真实 selection 状态修正提示。 |
| `AUDIT-12-CAND-001`（P3，交付工具） | finding | `publish.ps1` 默认输出位于仓库并递归清理；脚本未运行，无已误删证据。 | `apps/desktop-avalonia/scripts/publish.ps1` 与调用方。 | 新 Task 将默认输出移到相邻 workspace 并校验规范化目标/专用目录；仅用 disposable 目录验证清理；本 Task 禁止执行 publish/install/uninstall。 |
| `AUDIT-05-CAND-001` | INVESTIGATE | same-geometry primary/SFX 产生双 Region；既有仲裁任务已记录副作用，产品去重语义未定。 | SFX overlap arbitration 与 Region creation seam。 | 对照 M2 仲裁语义定义相同/近似、人工修改、`skip`/`translate` 规则；合成用例测 Region 数与请求数。 |
| `AUDIT-06-CAND-001` / `-002` | INVESTIGATE | 无账单级预算（有 StepRun/provider 重试上限）；glossary 无严格输出校验；均未调用真实 API。 | provider transport、translation payload/response policy 与需求。 | 先由需求 Task 决定费用控制与 glossary 合同语义；再用 fake provider 测重试/预算耗尽、冲突词条/漏匹配；不得声称远端双扣款。 |
| `AUDIT-14-CAND-002` | INVESTIGATE | V2 Studio 静态 `NOT_WIRED` 能力；V1 归属未知，GUI 未测。 | V2 Studio composition 与各页面。 | 先映射权威 V1 manifest；仅当纳入 V1 才开实现 Task 与真实 Host/GUI 验收。 |

### R3：补足关键验证证据

| 工作项 | 当前缺口 | 依赖 | 验收 |
|---|---|---|---|
| VAL-01 核心用户旅程 | AUDIT-13 仅部分 synthetic A/D/E/G/H；B/C/F、全 UI chain 与真实页面流程未跑。 | 独立验证 Task、可用 synthetic fixtures、Host/TestHost 前置条件。 | 每项记录步骤、预期/实际、generated HEAD/EXIT、失败与 skip；不得用 fake adapter 替代真实依赖结论。 |
| VAL-02 GUI 可用性 | Fluent Host 未 ready；reader/edit/OCR/translation/export 操作及 accessibility/DPI 未测。 | Host startup blocker 消除或具名归因；专用隔离 fixture。 | Legacy/V2/Fluent 各入口可达性、键盘、缩放、多屏与异常恢复分别记录。 |
| VAL-03 Windows install | 无当前基线 installer/package provenance；安装、升级/回退与卸载未执行。 | 新发布验证 Task、隔离安装环境、可核对产物来源。 | 固定 commit 与产物 hash，干净 Windows/权限/中文路径/运行时缺失/启动/卸载矩阵全部有结果。 |
| VAL-04 质量与安全扫描 | AUDIT-02 工具缺失、analyzers disabled；AUDIT-11 部分面 PARTIAL/NOT_TESTED。 | 独立 Task 决定允许的扫描工具与环境，不在本 Task 安装依赖。 | 工具版本、范围、退出码、false positive 处置与未覆盖面完整可复核。 |

## R4：文档治理与后续架构观察

| 项 | 裁决 | 先决裁决 | 建议 Task 与验收 |
|---|---|---|---|
| `AUDIT-14-CAND-001` | finding（P3 优先级，非产品 P0–P3 计数） | 确认 V1/未来范围权威来源 | 独立文档 Task 建立有日期/版本的逐项 manifest，对齐 README/AD-003/STATUS/索引与未来规划，阻止未来项目误计入 V1。Codex 建议将其提前到 14-002 归属裁定之前。 |
| `AUDIT-14-CAND-002` | INVESTIGATE | 判定 NOT_WIRED surfaces 是否属于当前 V1 | 先做 V1 manifest 映射；纳入 V1 才释放 Studio wiring/实现 Task 并做真实 shell 验收。 |
| `AUDIT-14-CAND-003` | close | — | 不开产品修复 Task（当前 release 不会因此失败）；如清理旧辅助路径，归 R4 维护 Task 并先核实调用者。 |
| `AUDIT-14-CAND-004` | close | — | 不开缺陷 Task；后续真实 UI 验证记录 shell × page × 关键操作矩阵。 |

## 排序说明（Codex 意见）

1. **R1 最高**：先以独立只读 Task 查清 `AUDIT-11-INC-001` 远端现状；再分开处理 junction containment 与 restore 失败语义。传播风险调查不得顺带删除或改写历史。
2. **R2**：随后处理 `NM-AUD-0001` sidecar 生命周期，覆盖取消、Dispose、EOF、spawn 后失败与 Host shutdown。
3. **R3**：先处理已确认的导出 P2（07-001），再安排 Reader 提示（09-001）与 publish 输出路径（12-001）的窄范围修复/验证；05/06 与 14-002 需先有需求裁定。
4. **R4**：保留架构与长期文档治理；但把 V1 承诺总账（14-001）提前到后续范围裁定之前。shell × page 矩阵与旧辅助路径清理可随后纳入验证/维护 Task。

所有修复的验收须由新 Task 明确文件范围、reviewer、证据和回归矩阵。本路线不宣称整改已实施。
