## Verdict
approved（可集成）

r1 提出的 12 条（P1-1、P2-1/2/3、P3-1..P3-6、P4-1、P4-3）逐条核对后**全部闭合**；所附源码事实引用（`service.py`、`entities.py`、`handlers.py`、`core_assembly.py`、`gate.py`、`errors.py`、`core_service.py`、`library/service.py`、`detection_sfx.py`）我逐行复核，行号与断言一致。未发现 P0–P3 级新问题。

## 逐条闭合表

| 条目 | 状态 | 证据（文件+位置） |
|---|---|---|
| P1-1 | 闭合 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:120` §5 表行为 `{"regions": RegionListSummary[]}` 并带「result 包装形状以 §5.4 为准」；与 `:176` §5.4「result 形状唯一权威=本条目」互指，裸数组矛盾已消除。 |
| P2-1 | 闭合 | 同文件 `:175` 改为「继承分支下**无 region 级自愈路径**（除软删除后重新检出…），如需恢复须新授权修订」；全文 grep「再改标一次/唯一恢复手段」零命中，矛盾表述已不存在。 |
| P2-2 | 闭合 | 同文件 `:219` 依据改为「Task 合同 AC4（Codex 编排方案第 8 点）」+「UI 设计稿全文无『忽略』表述」+ R-015「仅同属 `RegionType` 闭集纪律」；报告 `:67` 一致；grep `design.md` 「忽略」零命中（近义确在 `:41/:236`），定案内容（处理动作/过滤状态）未变。 |
| P2-3 | 闭合 | 同文件 `:189` 溯源权威改 `origin` 字段（+ 检测步 provenance/StepResult）；源码逐行核实：`service.py:247-256` `create_region` 签名无 `source_run_id`、`service.py:222-241`+`:186` 经 `_build_revision` 默认 `None`、仅 `handlers.py:354/439` text 写路径携带；报告 `:65` §3.2 差异 1 同步。 |
| P3-1 | 闭合 | 同文件 `:170` 定案 `review_state=UNREVIEWED` 且不触发需校对；先例核实 `service.py:272/302/363/402/429` 全为 `UNREVIEWED`，`:456/499/527`（文本写）为 `NEEDS_REVIEW`，`entities.py:273-282` 校对标志属 snapshot text 面原样保留。 |
| P3-2 | 闭合 | 读取面 DTO 在 §5 表（`:120`）、§5.4（`:176`）、Revision history `1.4②`（`:7`）全部为 `RegionListSummary`；`RegionSummary` 仅存于 `CreateRegion` 行 `:121` 与历史注记，解耦成立。 |
| P3-3 | 闭合 | 同文件 `:191` 收紧为「零新错误语义」、`:202` 脚注 b 明示 `LOCK_CHANGED` 为守卫内部值不作 wire code、`:203` 脚注 c 明文 SCREAMING_SNAKE_CASE 并给出 `core_service.py:105/98` 与 `errors.py:19-20`（已核实大写字面量、枚举值为小写）；契约正文「零新码」字面零残留。 |
| P3-4 | 闭合 | 同文件 `:201` 脚注 a：`page_id` 不存在/不属于任何 book 与无存活 region 同判空列表（非错误），依据 `service.py:279-281`（已核实无 page 存在性检查）；`:197` TARGET_NOT_FOUND 行收窄为 `region_id`；`:191` 表头覆盖范围注记。 |
| P3-5 | 闭合 | `doc/tasks/M2-REGION-RETYPE-CONTRACT.md:22` 改「RC-2 改标命令 / RC-3 读取面；RC-1 suspect 字段不在本 Task 范围」、`:27` 改「（RC-3；RC-1 suspect 不在本 Task 范围）」；与 `design.md:271/272/273` 口径（RC-1=suspect/RC-2=改标/RC-3=读取面）一致。 |
| P3-6 | 闭合 | `verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md:40` 末注明明示 C2/C3 各需 service guard 层（`service.py:483-496`）+ 管线候选持久化层两层断言，缺一层即 AC 不闭合。 |
| P4-1 | 闭合 | 契约 `:169` 加双向交叉指针：`SetRegionType` 与 §5 表 `SaveManualTranslation` 的 `expected_revision` 同模式、region 写命令面以本条目+C4 为权威，后者「精确并发策略 UNKNOWN」边界注记（`:123`）未动。 |
| P4-3 | 闭合 | 契约 `:191` 表头注记覆盖范围（`ListRegions` 仅 `INVALID_REQUEST`/空列表/`UNKNOWN`；乐观冲突与目标缺失为 `SetRegionType` 专属）。 |

## 新发现

- **P4（文本一致性，不阻断集成）**：`doc/tasks/M2-REGION-RETYPE-CONTRACT.md:27`（AC2 行）仍以「来源 sfx-arb- 前缀」作为最小字段集要求，未随 P2-3 改为 `origin` 承载。该行属 Task 合同 AC 原文、且契约/报告已定案，故不计未闭合；建议集成时或下一修订在该行补一行 r1 注记，避免 T5b 实现者单读 AC 时误以为读取面须暴露 label 前缀。
- **P4（同上）**：报告 `:14`（§1 AC1 行）仍保留「错误码映射表零新码」字面，已有 r1 注记与表头「本节基于原始交付」声明，误读风险低；可顺带统一措辞。
- 无 P0–P3。

推荐下一步：由集成方（编排会话代行 Codex）执行收口——回填 `integration_commit`、`status: done`，并按 Task 合同分工在 `design.md` 落「EV-8 转 CLOSED」集成注记；上述两条 P4 可在同一次集成提交中一并处理。
