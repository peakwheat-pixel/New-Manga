---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58
turn_id: turn_1906daf6-5292-4047-a690-c4824de52240
decision: REFRESH_UNIVERSE_AND_REQUIRE_INDEPENDENT_BASELINE
---

# 释放 Addendum：刷新影响全集

旧 `e9f7bb1b48c885cb329848d2d3591e145ff3d229` 的 5,376 行为历史快照。当前表行只读初计约 5,438，仅作线索，未经正式 inventory 核实。ZCode 裁定：在固定 base `2df8db7a4d19b591e919ecc6e8f8651167800ef0` 的隔离副本正式重测并与旧快照逐行做 added/deleted/changed delta；逐条归因新增行，deleted=0、changed=0 且无无法归因项后，冻结当前影响全集。历史文件不得改写。

AC1a 正式 inventory/delta；AC1b 逐行归因及冻结；AC1c 实际 default、本卡与四个代表历史 TaskPath、pins、API 及样本矩阵；AC1d 由未参与实现、且不同于最终 Review 的 ZCode 独立会话确认基线。AC1d 通过前禁止任何实现 commit。模型结果与 checker 实跑分开标注，不能把模型称为全量 checker PASS/FAIL。

停止条件：基线 delta 存在删除、同键字段变化或无法归因新增；或实施后锚定的历史行出现未解释判定变化、除本 Task 自证行之外的行键增减。Task 新增自证行单列增量层，不混入历史不变性断言。其他冻结禁区保持不变。
