# T3.2.1 Legacy Closure / Supersession Audit

- 日期：2026-09-26（Asia/Shanghai）
- 审计集成基线：`master` @ `ad003bb3c7489632772f452855ac7fa173ee698f`
- Legacy integration evidence：`verification/T3.2.1/integration-6519125/integration-evidence.md`
- 输入固定为交付分支 `codex/T3.2.1-clean-release-gate-20260925` @ `b18fa0e70ec4356a207fd7d941cdcf0cb2f1c285`，固定构建输入 `08f9bd85137965df922db524bc92917af513bd24` 未重新构建；Qoder Review 分支 `agent/qoder/T3.2.1-review-78aba7c` @ `b66788a813b04c0305226331c54327e178093664` 的批准范围仅为「可作集成输入」。
- M2 架构依据：[AD-001](../../doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md)；M2-I1、M2-I2、M2-R1、M2-UI1 均已完成并集成。

## 1. 最终状态与裁决

T3.2.1 TaskStatus=`closed_with_limitations`；closure disposition=`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`。现有 TaskStatus 没有这一收口状态，本次在 `doc/09_COLLABORATION.md §4` 作最小增量：增加一个仅用于架构取代/明确裁决收口的终态，不改变已有状态的含义。

PySide6/QML + PyInstaller Windows Release Gate 不再是未来正式产品发布架构。**关闭 T3.2.1 不代表所有 Legacy AC PASS，而是因为旧桌面发布架构被已批准的 M2 目标架构取代。T3.2.1 未完成的 Legacy AC 不再阻塞 M2。**这不是 Release approval；不授权 push、上传、安装器、签名或发布。AC 与 Finding 的原始 `PASS`、`PARTIAL`、`NOT_RUN`、`BLOCKED`、`MEASURED_WITH_LIMITATIONS` 状态均不因收口而改变。

历史集成证明仍有效但范围有限：AC10 仅证明 Handoff、Qoder Review（approved for integration input only）、Codex 集成与集成后验证闭环；固定包没有重建。旧门后续的完整 Release Gate 没有通过，本次未重跑旧 Gate。

## 2. AC 分类

分类解释：`LEGACY_ONLY` 只适用于被取代的 PySide6/QML + PyInstaller 验收路径；`MIGRATE_TO_M2_ACCEPTANCE` 表示同一用户能力必须在 React/Tauri/Python Core 验收中重定义；`CORE_REQUIREMENT` 是跨架构的长期正确性/安全要求；`DEFERRED` 表示未来 Release Gate 再决定或测量。组合行明确拆分分类，不合并不同事实。

| AC / 子项 | 集成时保留的原始状态 | 分类 | 收口裁定 |
|---|---|---|---|
| AC1 固定 PyInstaller 构建身份、版本和构建输入 | PASS | LEGACY_ONLY | 仅证明旧包构建来源；保留原 PASS，不要求对旧包重跑。未来产物身份需在 M2 Release Gate 定义。 |
| AC2 PyInstaller onedir 产物、清单和文件哈希 | PASS | LEGACY_ONLY | 旧包事实保留；不能推断未来 Tauri 产物已验证。 |
| AC3 PyInstaller 固定包启动（本机模拟路线） | PASS（本机模拟路线；非干净机覆盖） | LEGACY_ONLY | 本机模拟裁决只适用该已记录路线；完全未装 Python 的干净 Windows 启动仍 `NOT_RUN`。 |
| AC3 等价的新桌面安装/启动能力 | 尚未测试 | MIGRATE_TO_M2_ACCEPTANCE | 在未来 Tauri + Python Core/sidecar 打包验收中检验无系统 Python 前提；当前不声称已覆盖。 |
| AC4 Qt/QML 资源闭包 | PASS（本机包体验证） | LEGACY_ONLY | Qt DLL、QML import 与旧包资源闭包特属于已退出的运行形态。 |
| AC5 Provider 缺失时 fail-closed 并诊断 | PASS（旧包诊断路径） | CORE_REQUIREMENT | Python Core 长期要求：Provider 缺失不得伪成功或破坏主程序；诊断应可复核。 |
| AC5 旧桌面可选依赖启动边界 | PASS（受本机模拟范围限制） | LEGACY_ONLY | 旧打包启动行为保留为历史证据。 |
| AC6 完整业务主流程；当前缺成功 Pipeline 步骤 | PARTIAL（11/12） | MIGRATE_TO_M2_ACCEPTANCE | 确定性成功 Pipeline、保存、重启恢复、Reader 核验和导出核验必须在 M2 验收中完成定义和证明；fail-closed 诊断不代替成功路径。 |
| AC6 干净 Windows 上运行旧 PyInstaller 主流程 | NOT_RUN | LEGACY_ONLY | 不再为旧包补覆盖；等价目标包流程覆盖列入 M2 验收。 |
| AC7 源文件、Managed Copy、Secret、Lock 与 Revision 安全 | PASS（本机模拟路线；非干净机覆盖） | CORE_REQUIREMENT | 保留现有 PASS 的证据边界；未来仍必须验证 source hash integrity、Lock、current/pinned Revision 和人工修改保护。 |
| AC8 旧包 `%LOCALAPPDATA%`、只读程序目录、`--data-root` 路径验证 | PARTIAL；干净 Windows 覆盖 `NOT_RUN` | LEGACY_ONLY | 旧 PyInstaller 路径组合不再补测。 |
| AC8 数据根隔离、正常退出、无残留进程及 SQLite 解锁语义 | PARTIAL（本机观察） | CORE_REQUIREMENT | 数据路径安全、退出排空和数据库资源释放跨架构持续有效。 |
| AC8 等价目标桌面路径与清洁安装覆盖 | 尚未在 M2 验收 | MIGRATE_TO_M2_ACCEPTANCE | 在新安装/运行封装中验证适配后的路径、退出和 SQLite 行为。 |
| AC9 暖缓存重复启动指标 P50=1.102 s / P95=1.156 s | PARTIAL（MEASURED_WITH_LIMITATIONS；非冷启动） | LEGACY_ONLY | 原数值与 warm-cache 标签保留，不改称冷启动。 |
| AC9 真正冷启动 | NOT_RUN | DEFERRED | 新产品发布 Gate 再定义冷启动边界、环境和 P50/P95。 |
| AC9 Windows 10 x64 旧包矩阵 | NOT_RUN | LEGACY_ONLY | 不为被取代的 PyInstaller 产品补测。 |
| 未来 M2 Windows 支持矩阵 | 尚未裁定/测试 | DEFERRED | 由未来产品支持范围与 Release Task 决定，不能从旧矩阵推断。 |
| AC10 Review、集成与集成后检查 | PASS（仅 AC10 子门） | LEGACY_ONLY | 仅关闭旧 Task 的治理交付项，不表示 AC1–AC9 全部通过或可发布。 |

## 3. 特别挂账事项

| 项目 | 原始状态 | 分类与处理 |
|---|---|---|
| Windows 10 x64 matrix | `NOT_RUN` | Legacy PyInstaller 矩阵为 `LEGACY_ONLY` 并退役；未来 M2 平台矩阵为 `DEFERRED`，须由支持矩阵和 Release Gate 重新确定。 |
| 真实 docTR 权重成功路径 | `NOT_RUN` | `CORE_REQUIREMENT`；执行延后到有受控权重、环境与质量标准的 Core/provider 验收。Mock/Local 成功不能代替真实权重能力证明。 |
| 完全未装 Python 的干净 Windows 启动 | `NOT_RUN` | 旧 PyInstaller 路径为 `LEGACY_ONLY`；未来 Tauri/Python Core 安装与启动等价覆盖为 `MIGRATE_TO_M2_ACCEPTANCE`。 |
| AC6 / AC8 clean-machine coverage | `NOT_RUN` | 旧包覆盖 `LEGACY_ONLY`；在 M2 的新安装路径覆盖成功业务流程、数据根、退出和 SQLite 解锁为 `MIGRATE_TO_M2_ACCEPTANCE`。 |
| AC9 real cold-start | `NOT_RUN` | `DEFERRED` 到未来 M2 Release Gate；旧 warm-cache 数值保留为 `MEASURED_WITH_LIMITATIONS`。 |
| `console=True` | 已观察，发布前待决 | PyInstaller 配置项属 `LEGACY_ONLY`，不为旧包修改；未来 GUI/no-console 与日志呈现策略为 `DEFERRED`，由 D08/新 Release Task 裁定。 |
| ICU 从宿主 System32 解析 | 已观察，旧 Qt 依赖边界问题 | Qt/ICU/System32 具体问题属 `LEGACY_ONLY`，不修改 Qt/ICU；未来目标包依赖闭包与宿主依赖清单应纳入 M2 Release Gate。 |
| Provider missing fail-closed | 已有诊断证据；成功路径未由此证明 | `CORE_REQUIREMENT`，迁移到 Core/Pipeline 验收；缺依赖必须明确失败且持久化/可诊断，不能用假成功状态。 |
| 数据安全、源 hash、Lock / Revision | AC7 本机模拟范围内 `PASS`；干净机覆盖未跑 | `CORE_REQUIREMENT`，迁移到 M2 Acceptance；需保护 source hash、Managed Copy、人工修改、Lock、current/pinned Revision 和重启恢复。 |

## 4. Review findings 分类

Finding 原文与原 Review 状态保留在 [Qoder Review `78aba7c`](../../doc/reviews/T3.2.1-78aba7c.md) 及其复审记录中；本表仅给出本次关闭后的分类/处置，不回写 Review/Handoff，也不把历史 finding 状态伪装成 PASS。REPAIR-9/11 的具体历史状态仍以各自 Task/Review 为准；本次只裁定其旧 PyInstaller/交付证据范围不再阻塞未来 M2。

| Finding | 分类 | 收口处置 |
|---|---|---|
| R-001 | LEGACY_ONLY | 原始运行日志已在集成修订中归档；这是旧包证据归档问题，记录保持不动。 |
| R-002 | LEGACY_ONLY | 应用版本 `0.1.0` 的旧包证据更正已集成；不转成新产品版本结论。 |
| R-003 | MIGRATE_TO_M2_ACCEPTANCE | 维持 AC6 `PARTIAL (11/12)`；fail-closed diagnostic 只证明 AC5；成功 Pipeline 路径迁移。 |
| R-004 | LEGACY_ONLY | 本机模拟裁决仅适用于 AC3；AC6/AC8 不因本机观察转成干净机 PASS。目标安装覆盖迁移至 M2。 |
| R-005 | LEGACY_ONLY | 旧运行退出码文字已修正，历史原始日志只读。 |
| R-006 | LEGACY_ONLY | 重复截图已标注为同帧；无旧包补采任务。 |
| R-007 | CORE_REQUIREMENT | 旧 artifact 凭据扫描证据已补；不泄露 Secret 的要求持续适用 Core、日志与所有新产物。 |
| R-008 | DEFERRED | warm-cache repeat 口径保留；true cold-start 按未来 M2 Release Gate 定义。 |
| R-009 | LEGACY_ONLY | 旧包全产物 verifier 日志已归档；不重跑完整 Legacy Gate。 |
| R-010 | MIGRATE_TO_M2_ACCEPTANCE | Reader export book/chapter lineage 是跨架构有效需求；REPAIR-15 不释放，纳入 Reader/Export 验收。 |
| R-011 | MIGRATE_TO_M2_ACCEPTANCE | Bookshelf page count 与 unknown/count 状态表示纳入 M2 Library parity acceptance；REPAIR-16 不释放。 |
| R-012(a) QML accessibility/clipboard warnings | LEGACY_ONLY | 旧 QML 告警分诊保留；无 Legacy 修复。 |
| R-012(b) `console=True` | LEGACY_ONLY | 旧 PyInstaller 开关不修改；目标 GUI/no-console 策略单独 DEFERRED。 |
| R-012(c) Qt ICU via host System32 | LEGACY_ONLY | 不改 Qt/ICU；通用未来 bundle dependency closure 由新 Release Gate 再验。 |
| R-013 | LEGACY_ONLY | 构建宿主 `git` 依赖声明已修订；属旧包构建可复现性。 |
| R-014 | LEGACY_ONLY | Qoder 本轮非作者 Review 执行方 attribution 已更正；历史记录不改写。 |
| R-015 | LEGACY_ONLY | STATUS AC3 口径同步已完成；保留本机模拟与非干净机限定。 |
| R-016 | MIGRATE_TO_M2_ACCEPTANCE | REPAIR-15 建议范围曾更正为 VM 层传参；实际 book/chapter export lineage 验收迁移至 M2，不实施旧 QML/VM 修复。 |
| R-017 | LEGACY_ONLY | 旧 artifact scan 的 526/528 计数差异仍为非阻断历史记录；结论不依赖该计数，不再修 Legacy 材料。 |
| R-018 | LEGACY_ONLY | PyInstaller 包含 Qt dev tools/stubs 的发现仅适用于旧包；不再瘦身该包。 |
| R-019 | LEGACY_ONLY | 旧 Handoff AC 表已由后续 checkpoint 覆盖；Handoff 保持原样，不要求再修订。 |
| F-003 | LEGACY_ONLY | 未改写的固定源 Handoff SHA 措辞属于旧 Task/Handoff 证据链；原 `open / deferred` 状态保留，未来通用 Handoff 仍遵循 commit/blob 可追溯要求，但不再单独释放 Legacy repair。 |
| REPAIR-9 F-2/F-4/O-3 | LEGACY_ONLY | 历史旧包测试路径 Review findings；原 Task/Review 状态不回写，不再发起 Legacy 修复。 |
| REPAIR-11 F-11-1/F-11-2 | LEGACY_ONLY | 历史交付/Handoff 文档 finding；原 `changes_requested` 状态保留，不再发起 Legacy 修复。 |

## 5. REPAIR-17 disposition 与 M2 Acceptance Backlog

[T3.2.1-REPAIR-17](../../doc/tasks/T3.2.1-REPAIR-17-mock-local-pipeline-smoke.md) 保持 `status: proposed`、`release_state: NOT_RELEASED`，并登记 `disposition: SUPERSEDED`、`release_decision: DO_NOT_RELEASE`。不针对 Legacy PyInstaller 包实现该 Task。以下需求从该候选中提取，登记为**未来 M2 Acceptance Backlog**，不构成 M2-C1 contract 修改、实现授权或新增 Task：

1. 使用显式、可识别的 deterministic Mock/Local test provider 跑通成功 Pipeline；不得冒充真实 docTR 权重路径或模型质量。
2. 验证结果保存与应用重启后的恢复。
3. Reader 内容/Revision 核验。
4. Export 文件与 export lineage 核验（book/chapter/page scope）。
5. source hash integrity 与源文件不可变性。
6. Lock、current/pinned Revision、人工编辑和 Managed Copy 完整性。
7. Provider 缺失时 fail-closed、诊断明确并留下可恢复状态。
8. 新桌面安装/启动、clean-environment 适配、AC6/AC8 等价业务路径、退出排空和 SQLite 解锁；目标包不依赖宿主安装 Python 的具体契约由后续 Release Task 冻结。
9. 真实 docTR 权重成功路径的受控 Core/provider 验收；冷启动指标、GUI console 策略、平台矩阵及依赖闭包由未来 Release Task/D08 裁定。

M2-C1 当前是独立 Task，状态 `in_review`，候选位于 branch `agent/codex/M2-C1-typed-ipc-contract` @ `531647ee93f04694e83e3911af92940c12e55ce8`，固定待审 head=`ac38dede84ff22290c9b9d579c1372c8184a7bd5`。Qoder 正式 R3 Review/evidence 未交付前，Task 不算通过或已集成。本关闭审计不会改变它。

## 6. 受保护的历史状态与范围

- `Windows 10 x64 matrix`、真实 docTR 权重成功、完全未装 Python 的干净 Windows 启动、AC6/AC8 clean-machine coverage、AC9 true cold-start 均仍是 `NOT_RUN`；暖缓存数据仍是 `MEASURED_WITH_LIMITATIONS`，AC6/AC8 仍是 `PARTIAL`。
- 保留原有 AC1/2/3/4/5/7/10 的 PASS；AC3 文案必须始终写作「PASS（本机模拟路线；非干净机覆盖）」；AC10 PASS 只属于 Review/集成子门。
- 既有 `verification/T3.2.1/integration-6519125/**`、checkpoint、Review、Handoff 和全部历史门证据不重写；本文件是新增 closure evidence。
- 本次只修改治理文档和新增本审计证据；不修改 QML、PyInstaller、Qt/ICU、Schema、M2-C1 contract，不创建/释放 REPAIR-18/19，不启动 M2-S1，不 push/上传/制作安装器/签名/发布，不重跑完整 Legacy Release Gate。
- M2-C1 不依赖 T3.2.1；**T3.2.1 未完成的 Legacy AC 不再阻塞 M2。**
