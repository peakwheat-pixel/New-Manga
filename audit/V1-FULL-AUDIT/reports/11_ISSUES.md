# 11 去重问题台账

**审计基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**证据来源：** AUDIT_ISSUES.md 与下列专项报告；状态按本报告撰写时仓库内容汇总。
**审计作者不重定级：** 候选项保持 REVIEW_PENDING，待 ZCode 在最终独立复核中裁决。R1–R4 仅表示推荐处置顺序，不改变严重度。

## 汇总

| 类别 | 数量 | 说明 |
|---|---:|---|
| 已 triage 的产品 finding | 3 | 2 项 Medium / High confidence；1 项 P2 |
| 未决调查风险 | 1 | AUDIT-11-INC-001；严重度和远端现状未知 |
| 等待裁决的候选 | 11 | 均未由审计作者正式定级 |
| 已披露关闭的非产品观察 | 1 | AUDIT11-REV-001，P3；不是产品 finding |
| 已正式分配 P0 | 0 | 仅表示当前台账没有已分配 P0，不证明没有未发现问题 |
| 已正式分配 P1 | 0 | 仅表示当前台账没有已分配 P1，不证明没有未发现问题 |
| 已正式分配 P2 | 1 | NM-AUD-0001 |
| 当前开放的正式 P3 产品 finding | 0 | AUDIT11-REV-001 是已关闭的非产品观察 |

P0–P3 是原审计的产品问题等级；SEG-B findings 使用既有 Medium severity / High confidence 裁决，不擅自映射到 P 等级。

## 已 triage 的产品 findings

| ID | 状态 / 等级 | 去重映射与已证实行为 | 根因 / 未知边界 | 证据 |
|---|---|---|---|---|
| SEG-B-PROBES-001 | TRIAGED；Medium / High confidence | AUDIT-03 与 AUDIT-11 共用同一 finding，不重复计数。隔离 directory junction 下，ManagedFileStorage.publish 可把新生成的 revision bytes 写到 managed root 外；现有目标文件受 exists 检查保护。 | src/infrastructure/filesystem/managed_storage.py:115-124 的 publish 路径未做 containment/reparse walk。真实用户目录、GC/归档及其他入口未测；需要外部行为者在 managed root 内创建 junction；不涉及权限提升或任意内容写入。 | reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md；reports/AUDIT-03-IMPORT-PROJECT-2026-11-13.md |
| SEG-B-PROBES-002 | TRIAGED；Medium / High confidence | AUDIT-08 与 AUDIT-11 共用同一 finding，不重复计数。restore 的隔离磁盘写失败复现为 database_changed=true、typed_error=false、rollback_id_in_error=false、pre_restore_packages=1。 | src/infrastructure/sqlite/nmbak.py:1180-1210 的逐文件 write_bytes 路径没有包装为带 pre_restore id 的 typed error。数据库有 pre_restore 包；多文件部分写入只是静态推断，没有被该单文件 probe 演示。上层 Core/wire 对裸 OSError 的映射未验证。 | reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md；reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md |
| NM-AUD-0001 | TRIAGED；P2 | AUDIT-01 与架构/安全复核共用同一 finding。受控 helper 经实际 SidecarProcess API 验证：pre-cancel 和 DisposeAsync 路径返回时，忽略 EOF 的 helper 子进程仍存活。 | apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs:81-169,299-360；HostBridge / HostRuntime 调用路径见 AUDIT_ISSUES.md。根因候选为 dispose 状态与底层 stop 顺序短路以及 spawn 后失败/取消的清理覆盖不足。真实 Python sidecar 是否忽略 EOF、生产触发概率和用户影响未测。 | reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md；reports/ZCODE-AUDIT-01-02-REVIEW-2026-11-12.md |

以上三个 finding 均未在本审计中修复；产品代码修改需要独立实现 Task。

## 未决调查风险

| ID | 状态 | 风险陈述与边界 | 证据 / 处置 |
|---|---|---|---|
| AUDIT-11-INC-001 | INVESTIGATE；严重度待定 | 本地 reflog 与提交祖先关系支持私有素材对象曾进入公开 main 历史的高置信推论。当前远端可见性、缓存/对象状态和当时完整授权语境均未核验。 | reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md、logs/stage0-resume-verification-20261112.log。未读取远端、未 push、未删除、未改写历史或做远端补救。 |

此条不等于确认当前远端可下载，也不应因未知而从发布风险中移除。

## 等待 ZCode 裁决的候选

| ID | 候选项 | 关键证据 / 去重说明 | 必须由 ZCode 回答 |
|---|---|---|---|
| AUDIT-05-CAND-001 | 同几何 primary/SFX 保留双 Region | reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md；与 M2-REGION-OVERLAP-ARBITRATION 已列取舍/去重候选相关。 | 是否为正式 finding、产品语义是否已接受、严重度与后续范围。 |
| AUDIT-06-CAND-001 | 缺少账单级 spend cap 与 provider idempotency key | 同一 AUDIT-05/06 报告；未调用 API，未证明发生重复请求计费。 | 是否属于 V1 必须要求、远端费用风险严重度及是否需新 Task。 |
| AUDIT-06-CAND-002 | glossary 优先级未由生产路径强制 | 同一 AUDIT-05/06 报告；glossary 进入请求，但没有输出强制校验；真实模型未测。 | 原始需求/契约是否要求强制匹配、是否为 finding 与严重度。 |
| AUDIT-07-CAND-001 | reader export hook options 的 3 个测试失败 | reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md；127 passed / 3 failed / EXIT 1，失败边界是 options / audit events，不是排版像素。 | 是否是既有 scope 内产品缺陷、严重度、独立复现要求。 |
| AUDIT-07-CAND-002 | 用户字体 license_note 不等于授权验证 | AUDIT-07 报告；仓库 tracked font assets=0；未读取用户字体或核验许可。 | FEA-14-FONT-1 limitation 是否已接受，是否需要新要求/Task。 |
| AUDIT-09-CAND-001 | V2 Reader Retry 提示与可见选择不一致 | reports/AUDIT-09-UI-UX-2026-11-13.md；合成空章节路径一次观察，未证明根因或真实用户影响。 | 是否是 UI finding、严重度、产品需求归属。 |
| AUDIT-12-CAND-001 | publish.ps1 默认输出位于 repo 并递归清理 | reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md；脚本未执行，未证明误删或当前发布失败。 | 对照调用方式/工作区规则后是否记为风险或新 Task。 |
| AUDIT-14-CAND-001 | V1 承诺与未来规划缺少统一逐项总账 | reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md；当前文档存在状态/路径漂移，承诺项数量不能可靠计算。 | 治理观察是否构成 finding、优先级及是否需文档 Task。 |
| AUDIT-14-CAND-002 | V2 Studio 存在 NOT_WIRED 可见能力 | 同一 AUDIT-14 报告；真实 GUI 未测，V1 需求归属未确认。 | 是否属于当前 V1 承诺、是否需实现 Task 和严重度。 |
| AUDIT-14-CAND-003 | Avalonia 发布辅助脚本仍引用旧 Tauri 路径 | 同一 AUDIT-14 报告；未执行干净发布以证明失败。 | 是否是当前发布脆弱性、严重度和隔离验证要求。 |
| AUDIT-14-CAND-004 | 多 Avalonia shell 路由增加 V2 回归面 | 同一 AUDIT-14 报告；未证明运行时故障。 | 是否为可接受迁移设计，是否需额外 shell 回归矩阵。 |

计数校验：5/6 有 3 项、07 有 2 项、09 有 1 项、12 有 1 项、14 有 4 项，总计 11 项。没有把同一 SEG-B finding 因出现在多个 AUDIT 专项而重复计数。

## 已披露关闭的非产品观察

AUDIT11-REV-001 为扫描器源 SHA 差异的 P3 observation，已由重建空白差异并披露关闭；不是产品 finding，不计入产品问题数。详见 AUDIT_ISSUES.md 和 logs/audit-11-scanner-source-hash-drift-20261112.log。
