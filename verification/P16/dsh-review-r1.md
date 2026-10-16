---
task_id: P16
title: 阅读与输出授权 Core
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P16-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 093430c75a46d28ed759ec646039bf2f55e3d429
declared_delivery_head: e2c07fa9b172c7a585653e376f309e3e39abd026
reviewed_head: 316d79eceb7723d89670f5072bb2f71996e85610
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE
date: 2026-10-16
mode: 只读审查 + 独立 Git/测试日志/安全断言复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
scale: 29 路径（含新建 Qt-free infrastructure/export 与安全 Gate）
decision: approved
---

# P16 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 093430c7..HEAD` | **29 个路径**，逐条核对全部落在契约 §12 的 P16 allowlist 内 |
| **排除项未被触碰** | 过滤 `pdf_qt\.py` / `tests/reading_export/` / `^(apps\|packaging)/` | **空** ✅ |
| **冻结契约完好** | 过滤 `M2-C1_TYPED_IPC_CONTRACT` / `P11_LONG_TASK` | **空** ✅ |
| **Qt-free 要求** | 对新建 `src/infrastructure/export/*.py` 搜 `PySide6\|PyQt\|QtCore\|QtGui` | **空** ✅（契约明确要求无 Qt） |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 完整测试集 | 独立读原始日志 | `tests/core`：**352 passed / 0 failed / exit_code=0**；P16 聚焦：**12 passed / exit_code=0** |
| 既有测试改动性质 | 读 `test_core_detect.py` / `test_page_catalog_modes.py` / `test_p13_run_runtime.py` 的 diff | **仅协议版本断言**：`{major:2,minor:0}`→`{major:2,minor:1}`、`(2,0)`→`(2,1)`；**未削弱断言** |

## 1. AC 逐项结论

| AC | 判定 | 依据 |
|---|---|---|
| AC1 Reader 投影与进度 | **接受** | `test_reader_projection_progress_modes_layouts_and_restart`；`ac-matrix.md`。原始/译文与 RTL/LTR/Webtoon、一长图一 Page、关闭重开均已覆盖 |
| AC2 五格式导出 | **接受** | `test_five_export_formats_preserve_order_hash_lineage_and_pdf_text`：PNG/ZIP（standard·fast·store）/CBZ（含 `ComicInfo.xml`）/PDF（image-only 顺序 + searchable 双层文本）/文本（JSON·TXT·Markdown），并逐项断言**页序、逐页 SHA-256、lineage 与源 revision/hash 匹配** |
| **AC3 `ExportTargetRef` 安全 Gate** | **接受（重点）** | 见 §2 |
| AC4 进度事件纪律 | **接受** | 事件仅在进度快照持久化后发出、不携带路径/Ref（`ac-matrix.md`） |
| AC5 stale / 取消 / 历史 | **接受** | `test_stale_abort_consumes_ref_and_continue_records_frozen_lineage`、`test_cancel_before_publish_keeps_existing_target_and_cleans_temporary_file` |
| AC6 协议与既有语义 | **接受** | envelope 同步为 major 2 / minor 1；既有读语义由全量 core 回归（352 passed）覆盖 |
| AC7 范围锁定 | **接受** | 见 §0 四项过滤，全部为空 |
| AC8 测试覆盖 | **接受** | 12 个聚焦用例 + 全量 core 回归，含 AC3 负向断言 |
| AC9 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review` |

## 2. AC3 安全 Gate 的独立复核（本 Review 的核心）

| 关注点 | 复核结论 |
|---|---|
| **6 类拒绝** | `test_export_target_ref_rejections_make_zero_target_writes[...]` 参数化覆盖 `REF_MALFORMED` / `REF_SIGNATURE_INVALID` / `REF_EXPIRED` / `REF_UNKNOWN_ID` / `REF_REVOKED` / `REF_ALREADY_CONSUMED`，**每类**断言：目标 **sentinel 字节完全不变**、同目录**无 `.tmp` 临时文件**、**原图与译图源文件逐字节不变**、**错误不含目标路径** ✅ |
| **原子消费** | `test_export_target_ref_scope_denial_and_atomic_concurrent_consumption`：**12 线程并发消费同一 ref → 恰好 1 个成功，其余 11 个 `REF_ALREADY_CONSUMED`**；解析/消费阶段未创建目标 ✅ |
| **成功后重放** | `test_replayed_ref_is_never_reconsumed_after_successful_export`：导出成功后重放同 ref → `REF_ALREADY_CONSUMED`，已发布文件字节不变、无临时文件 ✅ |
| **附加拒绝** | overwrite 禁止与 format 不匹配 → `REF_SCOPE_DENIED`，目标不变/不存在 ✅ |
| **stale 一致性** | `test_stale_abort_consumes_ref_and_continue_records_frozen_lineage`：stale 拒绝同样消费该次有效调用的 ref，重试须新 ref ✅ |
| **架构纪律** | 契约 §10.3 与实现一致：Core **只从注册表解析**已验证并绑定 session/format/单一目标/overwrite/expiry 的 opaque ref，再**原子消费**；**不会将 `StartExport` 中的路径字符串解释为授权**；写入走同目录 staging + 原子 replace，并对目标父目录与目标 entry 做安全复核 |

**结论：AC3 的实现与证据达到"可证伪的负向断言"标准，是本 Task 最强的安全边界证据。**

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 7 次）** | `delivery_head` 申报 `e2c07fa9`（实现提交），实际 HEAD=`316d79ec`（文档头） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | P3（后续依赖） | **Tauri host 的 issuer（签发/注入 `ExportTargetRef`）不在 P16 授权内**；Owner 已诚实地把待办写入 `verification/P16/host-issuer-todo.md`，且 Core 侧提供的是**私有注入 seam**、未公开为 JSONL 命令 | 登记为后续 host/Tauri Task 的前置；**核心消费者（P17）之前必须补齐**，否则导出链在真实产品中无法签发引用 |
| F3 | P3（边界） | AC1 的显示坐标换算（Page 原图像素 ↔ 视图坐标）归 Reader view/host，P16 只保存原图坐标 | 已在 Task 中说明；属 P17 UI 范围，合理 |
| F4 | P3（验证边界） | 真实 Provider、真实 UI、Windows smoke 与端到端导出均 `NOT_RUN` | 属 P17/P19 范围；**不得据此宣称产品级导出已可用** |
| F5 | P4 | 新增 `tests/core/test_p16_reader_export.py` 为单一较大文件 | 不阻塞；后续可按 AC 拆分 |

**无 P0/P1/P2 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `316d79eceb7723d89670f5072bb2f71996e85610`。
- **C2**：**host issuer 必须在其自身 Task 中实现**，并在 P17（Reader/Export UI）释放前完成或明确其独立 Gate（F2）。
- **C3**：P16 可标 `done`（AC1–AC8 闭合 + 本 Review + 集成）；但 F4 的真实 UI/E2E 验收仍留给 P17/P19，不得据此宣称产品级就绪。
- 实现本身无需返修。

## 5. 能力边界

- 本 Review 覆盖范围合规、测试证据真实性、AC3 安全断言的独立复核与既有测试改动性质；未重跑 352 用例（原始日志已核验 exit 0）。
- 所有 Git / 日志 / 代码 / 安全断言结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
