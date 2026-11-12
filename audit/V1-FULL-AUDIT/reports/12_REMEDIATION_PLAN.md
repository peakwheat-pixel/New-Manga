# 12 整改与验证路线

本计划是在本轮审计授权范围内形成的建议；不授权本 Task 修改产品代码、契约、Schema、依赖、远端或用户数据。修复必须由新的 Task 冻结范围。R1–R4 表示建议处理顺序，不等同于 P0–P3 severity；候选项仍待 ZCode adjudication。

## R1：数据安全与发布暴露风险

| 工作项 | 当前证据与根因状态 | 影响文件/范围 | 建议改动与依赖 | 风险 | 验收与回归 |
|---|---|---|---|---|---|
| SEC-01：AUDIT-11-INC-001 传播风险调查 | 本地历史证据支持高置信推论；远端当前可见性未知，不能断言仍公开。 | Git 对象/历史及发布来源；具体对象范围见 reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md。 | 由独立 security / integration Task 固定只读核验问题与允许边界，再形成处置方案；本计划不执行远端请求、删除或重写。 | 过早清理可能破坏取证；不澄清则无法完成分发风险判断。 | 记录可复核的远端可见性结论、证据时间/方法和授权边界；任何删除、rewrite、通知或补救需另有显式 Task 与审查。 |
| SEC-02：SEG-B-PROBES-001 containment | junction probe 实测新 revision bytes 可越出 managed root；实现根因锚点为 managed_storage.publish 缺 containment/reparse walk。 | src/infrastructure/filesystem/managed_storage.py:115-124；具体实现范围由修复 Task 冻结。 | 在真实路径解析与写入前增加与 remove_managed / nmbak 等效的 containment/reparse 防线；先复核 ReferencedSource / Managed Copy seam 的调用边界。 | 仅做 lexical 检查可能仍被 junction/reparse 绕过；扩大到删除路径会改变保护语义。 | 隔离临时目录创建 managed/books junction，断言 publish 不在 root 外创建文件；验证普通 Managed Copy 成功、已有目标不覆盖、外部文件未改变；增加路径变体回归并跑相关 Core/Host tests。 |
| SEC-03：SEG-B-PROBES-002 恢复失败语义 | 隔离磁盘写失败在 DB 已切至备份点后抛裸 OSError；pre_restore 包保留，但错误没有 rollback ID。 | src/infrastructure/sqlite/nmbak.py:1180-1210；上层 Core/wire error mapping 尚待 tracing。 | 将文件 I/O 失败收敛到冻结错误合同，如 BACKUP_RESTORE_INCOMPLETE，并返回可用 pre_restore backup_id；实现 Task 必须先核对 C-07 / nmbak 冻结语义及上层映射。 | 失败清理/回滚策略可能误删唯一恢复包；未经合同裁决不得改共享字节。 | 通过故障注入验证错误为 typed、含 rollback ID、pre_restore 包可用；覆盖单文件/多文件失败、数据库状态、重开恢复和现有成功 restore；不得改变历史冻结契约字节。 |

## R2：核心资源与状态可靠性

| 工作项 | 当前证据与根因状态 | 影响文件/范围 | 建议改动与依赖 | 风险 | 验收与回归 |
|---|---|---|---|---|---|
| CORE-01：NM-AUD-0001 sidecar 生命周期 | 受控 helper 经实际 SidecarProcess API 复现取消/Dispose 后仍存活；根因候选见 AUDIT_ISSUES.md，真实 sidecar 行为未知。 | apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs；HostBridgeClient.cs；HostRuntime.cs。 | 新实现 Task 建立幂等 stop/cleanup 所有权；把 spawn 后取消/异常接入 finally；明确 HostRuntime shutdown 次序。 | 错误的 kill / 超时处置会影响正常 sidecar 关闭和 Host 生命周期。 | helper 覆盖 pre-cancel、spawn 后 cancel、EOF 正常退出、忽略 EOF 超时和 Host shutdown；断言 dispose 返回后 child/tree 已退出，且 shutdown error 可收敛；恢复 Avalonia TestHost 对应测试。 |

## R3：功能、交互与交付行为

先由 ZCode 处置候选，再创建对应实现或验收 Task；不要在新范围释放前按候选文字直接改代码。

| 候选 / 验证包 | 根因/需求状态 | 可能影响范围 | 下一工作与依赖 | 验收 / 回归要求 |
|---|---|---|---|---|
| AUDIT-05-CAND-001 | 合成 same-geometry primary/SFX 产生双 SFX Region；已有任务列过去重候选，是否缺陷待裁决。 | SFX overlap arbitration 与 Region creation seam；以 reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md 为代码地图。 | 先核对既有 M2-REGION-OVERLAP-ARBITRATION 语义，再决定去重 Task。 | 相同几何/近似几何、人工修订保护、skip / translate 策略及请求数量测试；真实模型只在有标注条件时验准确率。 |
| AUDIT-06-CAND-001/002 | 账单上限/idempotency 与 glossary 强制优先级均存在证据缺口，未证明发生重复计费或实际翻译违约。 | provider transport、translation payload/response policy 与需求/契约；具体锚点见 AUDIT-05/06 报告。 | ZCode 确认产品要求和远端语义；再分离成本保护与术语一致性 Task。 | fake provider 测超时重放、幂等 key、预算耗尽；glossary 冲突、匹配与失败策略；若无服务端合同，不声称保证远端恰好一次扣费。 |
| AUDIT-07-CAND-001/002 | 三个 hook/options case 失败尚未归因；license_note 不是许可证核验，但未证明发行包含未授权字体。 | reader export hooks、用户字体登记/消费；准确实现路径见专项报告与原代码搜索。 | 先独立确认三例实际语义；字体由需求 owner 明确是记录提示还是许可门控。 | ZIP/text overrides 和空 options audit event 有 unit + real export regression；字体验证采用合成许可元数据，不读取私人字体并证明未授权字体不随包。 |
| AUDIT-09-CAND-001 | 合成空章节中的 Retry 提示与可见选择不一致；根因和真实影响未确认。 | V2 Library selection、Reader retry state。 | 在 Host ready 的隔离会话中复现、跟踪选中状态生命周期后再释放修复 Task。 | 有页与空章节、切换作品/章节、Retry/返回等路径的 UI regression；提示需与真实 selection state 一致。 |
| AUDIT-12-CAND-001 | publish.ps1 默认输出位于 repo 且存在递归删除；预期清理的专用目录语义未核实。 | apps/desktop-avalonia/scripts/publish.ps1 与其调用方。 | 先映射调用方与路径 contract；在新 Task 的 workspace isolated build 路径中验证。 | 用 disposable output 证明产物可生成；检查脚本不删除 repo 外或非专用数据；当前 Task 禁止执行 publish/install/uninstall。 |

## R3：补足关键验证证据

| 工作项 | 当前缺口 | 依赖 | 验收 |
|---|---|---|---|
| VAL-01 核心用户旅程 | AUDIT-13 仅部分 synthetic A/D/E/G/H；B/C/F、全 UI chain 与真实 page 流程未跑。 | 独立验证 Task、可用 synthetic fixtures、Host/TestHost 前置条件。 | 每项记录步骤、预期/实际、generated HEAD/EXIT、失败与 skip；不得用 fake adapter 替代真实依赖结论。 |
| VAL-02 GUI 可用性 | Fluent Host 未 ready；reader/edit/OCR/translation/export 操作及 accessibility/DPI 未测。 | Host startup blocker 消除或具名归因；专用隔离 fixture。 | Legacy/V2/Fluent 各入口可达性、键盘、缩放、多屏与异常恢复结果分开记录。 |
| VAL-03 Windows install | 没有当前产品基线 installer / package provenance；安装、升级/回退和卸载未执行。 | 新发布验证 Task、明确隔离安装环境、可核对产物来源。 | 固定当前 commit 和产物 hash，干净 Windows/权限/中文路径/运行时缺失/启动/卸载矩阵全部有结果。 |
| VAL-04 质量与安全扫描 | AUDIT-02 工具缺失、analyzers disabled；AUDIT-11 部分面 PARTIAL / NOT_TESTED。 | 独立 Task 决定允许的扫描工具与环境，不在本 Task 安装依赖。 | 工具版本、范围、退出码、false positive 处置与未覆盖面完整可复核。 |

## R4：文档治理与后续架构观察

| 候选 | 先决裁决 | 建议 Task 与验收 |
|---|---|---|
| AUDIT-14-CAND-001 | 确认 V1/未来范围权威来源 | 建立逐项 manifest 和生效日期；与 README/STATUS/规划文档映射，并阻止未来项目误计入 V1。 |
| AUDIT-14-CAND-002 | 判定 NOT_WIRED surfaces 是否属于当前 V1 | 若属于 V1，释放独立 Studio wiring/实现 Task；若不属于，文档说明范围和用户可见状态。两种路径都需按真实 shell 验收。 |
| AUDIT-14-CAND-003 | 验证 clean release 是否依赖旧 Tauri 资产 | 映射 workflow 调用和当前资产 owner；若确认脆弱，移除旧路径假设并用 isolated clean build 验证。 |
| AUDIT-14-CAND-004 | 确认多个 shell 是否为正式回退/迁移设计 | 固定 shell × 页面 × 关键操作回归矩阵；以真实 Host 会话验证可达性与能力差异。 |

## 排序说明

1. R1 先对可能影响用户数据边界、恢复能力和私有材料分发的事项完成范围裁决与隔离修复设计。
2. R2 修复受控进程生命周期问题，并补齐可运行的回归环境。
3. R3 完成候选 adjudication、产品行为修复与缺失的关键运行验证。
4. R4 在确定产品承诺后处理文档基线与 shell 维护性风险。

所有修复的验收须由新 Task 明确文件范围、reviewer、证据和回归矩阵。本路线不宣称整改已实施。
