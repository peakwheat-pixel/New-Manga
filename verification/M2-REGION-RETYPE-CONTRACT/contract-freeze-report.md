# M2-REGION-RETYPE-CONTRACT · 契约冻结自检报告（T5a）

- owner：ZCode（subagent）；reviewer：DeepSeek Harness（非作者）；integrator：编排会话代行 Codex（用户全权授权）
- base：`4c12e8af`（release 3-task batch）；claim：`8d41d8ef`；**delivery_head（契约修订）：`a108996b`**
- 交付：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev `1.3` → `1.4` **草案**（本 Task 唯一契约变更面）
- 性质：**contract-only**——`src/**`、`tests/**`、`apps/**`、`packaging/**` 零 diff；本报告全文证据为静态源码阅读与本 Task 文本核对，无 runtime 测试（契约冻结 Task 本就不含 runtime 交付）。

## 1. AC 逐条自检

> **r1 注记**：本节自检基于原始交付 `a108996b`；DSH r1 返修后的条款状态以 §6 对照表为准。受 r1 影响的行已加「（r1：…见 §6）」尾注。

| AC | 要求（Task 合同原文摘要） | 交付落点 | 自检结论 | 证据 |
|---|---|---|---|---|
| AC1 | `SetRegionType` 冻结：请求（region_id/new_region_type/expected_revision）+响应含 `revision_no`（沿 SaveManualTranslation 先例）；错误码零新码；改标=新 revision（origin 方案定案）；撤销=既有 restore 语义引用不重定义 | M2-C1 §5 表 `SetRegionType` 行（`1.4` 指针）+ §5.4 条目 1–3 | **PASS** | wire shape：`{region_id, new_region_type, expected_revision?}` → `{region_id, revision_no, region_type, sfx_policy}`；枚举复用 `REGION_TYPE_VALUES` 六值（`src/domain/regions/entities.py:20-28`）；响应含 `revision_no` 沿 `save_manual_translation` 返回 revision_no 先例（`src/application/editing/service.py:521-529`），含生效态沿 §5.3 `settings_update_section` 一次往返先例；错误码映射表零新码（`INVALID_REQUEST`=`core_service.py:105` 既有字面量；`INPUT_REVISION_CHANGED`=`src/application/editing/errors.py:19` GuardStatus 既有；`TARGET_NOT_FOUND`=§8 表既有行；`UNKNOWN`=§5.3 同款）；改标=经 commit seam 新 revision（`service.py:202-220` 单一提交路径；`Region.apply_type` 实体层已定义 `entities.py:243-245`）；**origin 定案=恒 `user`**（RegionOrigin 四值零新增，MACHINE/RESTORED 之外无需新值；机器改标不走本命令——检测 origin=machine `core_assembly.py:1047`、仲裁以 `sfx-arb-` label 分发 `detection_sfx.py:202`）；撤销=引用既有 `RestoreRegionRevision`（§5 表既有行；`restore_revision` 产生 origin=restored 新 revision+溯源 `service.py:550-572`），明文禁止反向改标模拟 **（r1：「零新码」收紧为「零新错误语义」、`review_state=UNREVIEWED` 定案——见 §6 P3-3/P3-1）** |
| AC2 | 读取面 DTO 冻结（RC-1）：最小字段集（id/类型/policy 快照/来源 sfx-arb- 前缀/revision_no；标注状态不含——读取面不含训练语义）；扩容 vs 新命令取舍定案+理由 | M2-C1 §5 表 `ListRegions` 行+§5.4 条目 5 | **PASS** | `RegionSummary` 最小集五字段：`region_id/region_type/sfx_policy/origin/revision_no`；不含几何/文本/标注态（review_state/suspect/OCR/译文全部排除，明文条款）；**取舍定案=新命令**（三条理由：既有命令面无 region 读取通道且扩容=major 变更 §3.2；改标数据需求与画布几何通道解耦，几何缺口保持登记不越权；单 region 详情按 id 过滤避免命令面冗余）。**来源字段语义注记**：`sfx-arb-` 是检测候选 provider label 的仲裁前缀（`detection_sfx.py:202`），region 实体与 revision 快照**不持久化 label**（`entities.py:267-288` snapshot 字段集无 label）——读取面的机器/人工可区分权威=`origin` 字段（machine/user），设计稿「label 前缀」表述由 origin 承载（差异登记见 §3）**（r1：DTO 更名 `RegionListSummary`、溯源锚点改 `origin`+检测步 provenance/StepResult——见 §6 P3-2/P2-3）** |
| AC3 | 并发与人工覆盖语义冻结：①AI 任务运行期间人工改标冲突规则（人工优先+AI fail-closed+LOCK/Revision 守卫交互）②重开/重检测/撤销持久性；全部可测断言（触发+期望） | M2-C1 §5.4 条目 6（C1–C7）与条目 7（P1–P4） | **PASS** | 11 条两行式断言全文见本报告 §2；域守卫事实链：机器写乐观期望失效→fail-closed 存候选（D06 §90 `service.py:483-490`）、lock 命中→fail-closed 存候选（D06 §89 `service.py:491-496`）、用户写无乐观期望不受 lock 阻塞（`service.py:222-241` `_commit_user_or_raise`）；重检测幂等复用 live region 不重建不删除（`src/infrastructure/providers/handlers.py:246-269`）、检测单一写路径（`core_assembly.py:1006-1010`） |
| AC4 | 「忽略」定案：RegionType 六值枚举不新增；定为处理动作/过滤状态；契约注释+设计稿对齐注记（不回改设计稿，差异登记于本 Task） | M2-C1 §5.4 条目 8（RULED 契约注释）+本报告 §3 差异登记 | **PASS** | 六值闭集零新增（`entities.py:20-28`）；「忽略」=①处理动作（gate `SKIP_POLICY(reason=sfx_skip)` 派生，`gate.py:39-42`）②过滤状态（§5.2 UI-local，不写持久状态）；对未来「持久化忽略状态」方向写明预拒绝（须新授权修订）；设计稿 R-015 收窄 speech 的既成事实原样引用，不回改设计稿 **（r1：定案依据改 Task 合同 AC4 语境、明示设计稿无「忽略」表述、R-015 限定为同属闭集纪律——见 §6 P2-2）** |
| AC5 | SfxPolicy 快照规则定案（EV-8 裁决）：二选一冻结+理由（技术事实：core_assembly 强制非 SFX=SKIP，speech→sfx 必须产生新 policy 值；与设计稿 §4.2 联动表对齐） | M2-C1 §5.4 条目 4（EV-8 裁决，RULED） | **PASS** | **裁决=「按改标时全局配置重快照」**（改标为 sfx）；对称条款：改标为非 sfx 五值时强制 `skip`（维持「policy can never leak onto non-SFX regions」跨写路径，`core_assembly.py:1036-1045`）。理由三条：①gate 消费 region 快照不读全局（`gate.py:32-42`），speech 快照恒 skip——继承分支使全局 translate 对改标 region 永久不可达、静默失效无自愈；②与新建语义一致（新建 SFX 携带当时配置 `core_assembly.py:1041-1045`，改标=重新类型化）；③与设计稿 §4.2 translate 行前置条件（「仅当裁决为按当前配置重快照时本行可达」）一致，UI 零返工。设计稿 EV-8 由本裁决闭合（设计稿不回改，闭合注记见 §3）**（r1：继承分支自愈表述修正——见 §6 P2-1）** |
| AC6 | 修订纪律：不放松既有保护语义；版本记录 rev 1.4 草案段完整；明确「本修订不授权 runtime 实现」 | M2-C1 头部版本行+Revision history `1.4` 段+§5.4 末条修订纪律声明+§11 两行注记 | **PASS** | 头部明示「runtime 未实现，本修订不授权 runtime 实现」；Revision history `1.4` 段完整登记六项内容+minor 目标 `2`→`3`（沿 1.2/1.3 widening 先例，bump 归实现 Task）；§5.4 末条明示 §1–§4/§6–§10 保护语义零放松（§2 Core 权威与边界重校验、§3 版本规则、§4 互斥不变量、§10 数据保护原样适用）；§12 release boundary 原文未动（git diff 核对：仅头部/Revision history/§5 表/§5.4 新增/§11 两行变更，`git diff --stat`=1 file, +59/−3） |

## 2. AC3 断言清单（契约 §5.4 冻结全文转录，供 Reviewer/T5b 直接引用）

并发与人工覆盖（AI 任务运行期间）：

- **C1（人工优先：写通道不互斥）** — 触发：某 Run 的机器写正在执行，用户对任一 region 提交 `SetRegionType`。期望：改标立即提交成功（产生 `origin=user` 新 revision），不被运行中 Run 阻塞或排队；已进入执行的机器步骤决策不因改标回溯。
- **C2（AI 侧 fail-closed：Revision 守卫）** — 触发：机器写提交时携带的期望 revision ≠ 当前 revision（期间用户已完成改标）。期望：fail-closed——`INPUT_REVISION_CHANGED` 语义，不覆盖 region 任何字段，机器结果仅持久化为候选（StepResultCandidate），不自动重试覆盖；期望失效优先于 lock 判断（D06 §90）。
- **C3（AI 侧 fail-closed：Lock 守卫）** — 触发：机器写目标 region 处于 `translation_locked` 或 `region_locked`。期望：`LOCK_CHANGED` fail-closed，存候选不覆盖（D06 §89）；锁解除后须显式重跑才消费改标后新决策。
- **C4（乐观期望显式拒绝）** — 触发：`SetRegionType` 携带 `expected_revision` 且不匹配当前 revision。期望：typed 拒绝 `INPUT_REVISION_CHANGED`，region 状态零变化（无部分写入）。
- **C5（改标后决策生效）** — 触发：改标成功后该 region 被后续步骤/后续 Run 读取。期望：按改标后 `region_type`+`sfx_policy` 快照决策（gate 消费 region 字段）；改标只改变「此后」决策，已渲染成品图不因改标消失。
- **C6（机器改标上的人工叠加）** — 触发：对当前 revision `origin=machine` 的 region 提交 `SetRegionType`。期望：新 `origin=user` revision 叠加为当前态，机器 revision 保留历史可追溯；撤销经 restore 回机器笔（`origin=restored`）。
- **C7（目标缺失）** — 触发：`region_id` 不存在或已 soft-delete。期望：`TARGET_NOT_FOUND`（not_found）拒绝，零写入。

持久性（重开/重检测/撤销）：

- **P1（重开持久）** — 触发：改标后 Core 进程/应用重启。期望：`region_type`、`sfx_policy` 快照、revision 历史（含改标笔）与 current 指针全部保持；重新 `ListRegions` 返回改标后状态。
- **P2（重检测不回滚人工改标）** — 触发：对已含存活 region（含人工改标）的页重新执行检测步。期望：检测步幂等复用既有存活 region、不重建不删除，人工改标保持；仅当页无存活 region 时才沿单一写路径新建（origin=machine）。
- **P3（撤销完整恢复+历史保留）** — 触发：调 `RestoreRegionRevision` 至改标前 revision_no。期望：产生 `origin=restored` 新 revision（溯源），`region_type` 与 `sfx_policy` 一并回到改标前值；不删除/改写任何既有 revision。
- **P4（撤销后再改标，规则幂等适用）** — 触发：撤销后再次 `SetRegionType`。期望：按新一笔改标正常产生 `origin=user` revision；EV-8 重快照规则对新改标再次适用，不残留撤销链状态。

可测性说明：每条断言的触发条件与期望行为均为单一可观察结果，验证锚点为 Core 行为（非 UI 状态）；T5b runtime Task 应将 C1–C7/P1–P4 转录为集成测试用例表。**其中 C2/C3 各需覆盖两层验证（r1 P3-6 明示）：①service guard 层——`GuardStatus.INPUT_REVISION_CHANGED` / `GuardStatus.LOCK_CHANGED` 返回且 region 零覆盖（`service.py:483-496`）；②管线候选持久化层——fail-closed 时 payload 落 StepResultCandidate 不丢弃（候选表属 TASK-011，`errors.py:23-36` docstring 语义）**；T5b 用例表须两层各设断言，缺一层即该 AC 不闭合。

## 3. 交叉引用核对表与设计稿差异登记

### 3.1 与 UI 设计稿（M2-SFX-MISROUTE-UI-MITIGATION design.md）核对

| 设计稿项 | 内容 | 本契约处置 | 一致性 |
|---|---|---|---|
| RC-1/D2 | suspect 疑似信号字段 | **不裁决**——读取面不含训练语义（§5.4 条目 5 明文）；候选保持登记 | 一致（本修订不越权） |
| RC-2/D3 | `SetRegionType {region_id, region_type, expected_revision?}` 响应含 revision_no | **冻结为草案**——字段名 `new_region_type`（Task 合同指定），响应加生效态（沿 §5.3 一次往返先例） | 一致（命名差异：`region_type`→`new_region_type`，避免与响应回显字段歧义，Task 合同原文指定） |
| RC-3/D4/D5 | region 读取面+几何 | **部分冻结**——`ListRegions` 最小五字段；**几何不在最小集**（D5 缺口保持登记，由后续修订或 T5b 承接） | 一致（本修订明文不越权） |
| RC-4/D7 | RevisionSummary DTO+label 前缀 | **不裁决**（`ListRegionRevisions` 行未动）；label 前缀不可持久化的事实注记落 §5.4 条目 5 | 一致（见 §3.2 差异 1） |
| RC-5/D8 | reader 摘要字段 | 不裁决（候选保持登记） | 一致 |
| §1.3 改标语义表/R-001 | policy=region 自身快照；gate 权威语义 | §5.4 条目 4/条件 C5 与 `gate.py:32-42` 逐字对齐 | 一致 |
| §2.2/§2.3 | 非 SFX 强制 SKIP；Core 无 set_region_type 方法 | EV-8 对称条款的技术事实源（`core_assembly.py:1036-1045`）；Core 新方法=T5b 范围 | 一致 |
| §2.5/§3.4/A7 | 机器（sfx-arb- 前缀）vs 人工（origin=user）可区分 | 读取面由 `origin` 字段承载（§5.4 条目 5） | 一致（见 §3.2 差异 1） |
| §4.1 状态机/R5/R6 | 撤销=restore 回触发态；失败回原态来源守卫 | 撤销=RestoreRegionRevision 引用（§5.4 条目 3）；C6 撤销回机器笔 | 一致 |
| §4.2 联动表 | translate 行前置=「仅当裁决为按当前配置重快照时可达」 | EV-8 裁决=按改标时全局配置重快照 → translate 行可达 | 一致（前置条件被满足，UI 零返工） |
| §4.2 硬规则 1 | 联动单向：改标不写设置、设置不回溯既有 region | EV-8 重快照发生在**改标事务内**（读全局配置写 region 快照），不回写设置、不改其他 region | 一致（重快照是 region 自身字段的写入，非设置回溯） |
| §7.2 EV-8 | OPEN：快照沿用 vs 重快照 | **由本裁决闭合**（RULED 落 §5.4 条目 4） | 一致（闭合注记：设计稿 EV-8 转 CLOSED 属集成方动作，本 Task 不回改设计稿） |
| R-015 | 疑似警示收窄 speech（状态机只建模 SPEECH_*） | §5.4 条目 8 引用为既成事实，不回改设计稿 | 一致 |
| A1–A13 硬断言 | 13 条「违反即红」 | 契约侧对应：A6（新 revision+restore 撤销）=条目 2/3；A7（机器/人工可区分）=条目 5 origin 字段；A9（UI 不决策）=读取面只读快照；A11（SfxPolicy 三值零改动）=EV-8 重快照仅取三值之一、不改枚举/默认值/设置页 | 一致 |

### 3.2 与设计稿差异登记（不回改设计稿，按 Task 合同落本 verification）

1. **「来源 sfx-arb- 前缀」的承载方式**：设计稿 §2.5/§3.4/§5 D7 以「label 前缀（sfx- vs sfx-arb-）」表述 UI 区分机器/人工的依据之一。源码事实：provider label 仅存在于检测候选分发环节（`handlers.py:292-295`），region 实体与 revision 快照均不持久化 label（`entities.py:267-288` snapshot 字段集无 label）。契约定案（**r1 修订溯源锚点，P2-3**）：读取面 `RegionListSummary.origin` 字段承载机器/人工区分（machine/user），机器改标可追溯权威=**`origin` 字段（+ 检测步 provenance/StepResult 记录）**——`source_run_id` 不在 region 创建写路径（源码事实 r1 核实：检测/仲裁创建 region 经 `core_assembly.py:1032-1048` → `create_region` 签名无该参数，`service.py:247-256`；用户/恢复写经 `_commit_user_or_raise` 构造 revision 时 `source_run_id=None`，`service.py:222-241`；该字段仅存在于 text 写路径，`handlers.py:354/439`）；UI 设计稿 A7 的可追溯落点**限定为 `origin` 字段**；UI 不得依赖恢复 label 前缀。设计稿若需在 UI 呈现「仲裁改标」细分来源，属 RC-4（RevisionSummary 结构）候选范围，本修订不裁决。
2. **EV-8 闭合**：设计稿 §7.2 EV-8 为 OPEN 项。本契约 EV-8 裁决（§5.4 条目 4）闭合该项；设计稿文本不回改，「EV-8 转 CLOSED」由集成方在集成时处理（Task 合同依赖与风险节明示此分工）。
3. **R-015/「忽略」（r1 修订，P2-2）**：**设计稿全文无「忽略」表述**（grep 核实零命中；用户可见近义=「保留原文/停止翻译/不翻译」，design.md:41/236）；R-015 是疑似警示收窄 speech 的既成事实（design.md:86/223/317），与「忽略」无直接语义关系，仅**同属 `RegionType` 闭集纪律**。契约 §5.4「忽略」定案的依据=Task 合同 AC4（编排方案第 8 点）语境，定案为处理动作/过滤状态并预拒绝其成为 RegionType 值——与设计稿无冲突，注记备查。

### 3.3 与上游仲裁 Task（M2-REGION-OVERLAP-ARBITRATION）核对

- `ARBITRATED_LABEL_PREFIX = "sfx-arb-"`（`src/infrastructure/providers/detection_sfx.py:202`，仲裁 Task 冻结语义）：本契约不改动该前缀及其 `startswith("sfx-")` 分发语义；§5.4 条目 2 引用为「机器改标不走 SetRegionType」的依据。
- 仲裁自动改标=确定态类型决策、不新增疑似字段（上游 Task 明示）：与本契约「origin=machine 承载机器改标」一致，无语义冲突。
- 人工对机器改标 region 再次改标 → 新 user revision、机器笔保留（设计稿 A7/状态机 SFX_ARB_RELABEL）：契约 C6 断言一致。

## 4. 允许修改范围自证（git 证据）

- 变更面（`git diff --stat` @本分支）：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（+59/−3，1 file）——头部版本行、Revision history `1.4` 段、§5 表两行、§5.4 新增、§11 两行。Task/Handoff/verification 为本 Task 允许面的新增/回填。
- `git diff --check` → EXIT=0（无空白错误）。
- `src/**`、`tests/**`、`apps/**`、`packaging/**`、`doc/STATUS.md`、既有设计稿/Task 产物：零 diff。
- M2-C1 既有 §1–§4/§6–§10/§12 正文：零改动（diff 仅触及头部/Revision history/§5/§5.4/§11）。
- **r1 返修 diff 面**：本节以上记录原始交付 `a108996b` 时点；DSH r1 返修的变更面与复验命令见 §6。

## 5. 未运行项（诚实边界）

- 无 runtime 测试可运行：本 Task 交付为契约文本，`SetRegionType`/`ListRegions` 的 handler、Tauri 面、前端 pin 均未实现（rev 1.4 草案明示「本修订不授权 runtime 实现」）。C1–C7/P1–P4 是**可测断言文本**，其测试执行归 T5b（沿 Task 合同「runtime=T5b 另行释放」）。
- 一致性核对为静态文本对照（本报告 §3），非自动化检查。

## 6. DSH r1 返修记录（changes_requested → 全部处置，2026-10-04）

DSH 独立 Review r1 结论=`changes_requested`（1×P1 + 3×P2 + 6×P3 + 3×P4，全部文本级）。返修在同一 Task 分支以 `r1(RETYPE-CONTRACT):` 前缀 commit 交付；**全部为文本级修订，裁定内容零变更**（EV-8 裁决、「忽略」定案、错误码复用集、C1–C7/P1–P4 断言语义均不变）。

| R 编号 | 发现 | 处置 | 落点 |
|---|---|---|---|
| P1-1 | §5 表 `ListRegions` 行写裸数组 `RegionSummary[]`，与 §5.4 包装对象自相矛盾 | **已修**：§5 表行统一为 `{"regions": RegionListSummary[]}` 并加「result 包装形状以 §5.4 为准」注记 | 契约 §5 表 `ListRegions` 行 |
| P2-1 | AC5 理由链「继承原快照」分支下「唯一恢复手段是再改标一次」与「永久不可达」自相矛盾（继承语义下再改标仍继承 skip） | **已修**：改为「继承分支下无 region 级自愈路径（除软删除后重新检出：删除后重检测按新建语义携带当时全局配置，`core_assembly.py:1041-1045`），如需恢复须新授权修订」 | 契约 §5.4 EV-8 理由条 |
| P2-2 | AC4 依据错位：设计稿全文无「忽略」表述；R-015 与「忽略」无直接语义关系 | **已修**：定案依据改「Task 合同 AC4（编排方案第 8 点）」语境；明示「设计稿全文无『忽略』表述」（近义=「保留原文/停止翻译/不翻译」，design.md:41/236）；R-015 限定为「同属 `RegionType` 闭集纪律」。裁定内容不变 | 契约 §5.4「忽略」条；报告 §3.2 差异 3 |
| P2-3 | `source_run_id` 溯源锚点不成立：检测/仲裁创建 region 走 `core_assembly.py:1032-1048` → `create_region`（签名无该参数，`service.py:247-256`）；`_commit_user_or_raise` 构造 revision 时 `source_run_id=None`（`service.py:222-241`）；该字段仅在 text 写路径（`handlers.py:354/439`） | **已修**：契约溯源表述改「`origin` 字段（+ 检测步 provenance/StepResult 记录）」，A7 可追溯落点限定为 `origin` 字段 | 契约 §5.4 来源字段语义条；报告 §3.2 差异 1 |
| P3-1 | 改标 revision 的 `review_state` 取值未明确 | **已闭合**：定案 `UNREVIEWED` 且不触发需校对变化。理由：①源码先例——类型/几何/顺序类用户写一律 `ReviewState.UNREVIEWED`（`service.py:272/302/363/402/429`），`NEEDS_REVIEW` 仅文本内容变化写（`service.py:527/456/499`）；②改标 snapshot 仅两字段变化，`edited_confirmed`/`manual_edited` 属 snapshot text 面原样保留（`entities.py:273-282`），既有已确认译文不回退 | 契约 §5.4「改标 = 新 revision」条 |
| P3-2 | 读取面 DTO 与 `CreateRegion` result 同名 `RegionSummary`，隐式收窄其语义 | **已闭合**（采纳推荐项）：读取面 DTO 更名 `RegionListSummary`，契约内全部引用同步（§5 表两行、§5.4 条目、Revision history 1.4②）；`CreateRegion` 行 result 保持 `RegionSummary` 原名（其结构在本修订前后均未定义，不在本修订范围） | 契约 §5/§5.4/Revision history；报告 §1 AC2/§3.2 差异 1 |
| P3-3 | ①「零新码」措辞过强；②wire code 大小写未明文；③`LOCK_CHANGED` 在 C3 出现但不在错误码表 | **已闭合**：①全文收紧为「零新错误语义（wire `code` 字面量全部复用既有导出）」；②脚注 c 明文 SCREAMING_SNAKE_CASE（对齐 `core_service.py:105/98` 既有导出与 §8 表；`GuardStatus` 成员名同此形式（`errors.py:19-20`），其小写枚举值不得用作 wire `code`）；③脚注 b 消歧：`LOCK_CHANGED` 是机器写守卫内部结果值（`errors.py:20`），不是本两命令的 wire 错误码 | 契约头部/Revision history/§5 表/§5.4 错误码条 |
| P3-4 | `page_id` 不存在/不属于本书的归类缺行 | **已闭合**：选定「空列表 + 脚注 a」——`page_id` 不存在/不属于任何 book 与无存活 region 同判空列表（非错误），沿既有 `list_regions` 源码语义（无 page 存在性检查，`service.py:279-281`）；严格 page 存在性校验（对齐 `list_chapters` 的 `get_book` 先例，`library/service.py:155-160`）属读取面扩容须新授权修订 | 契约 §5.4 错误码表 TARGET_NOT_FOUND 行收窄+脚注 a |
| P3-5 | Task :22/:27 RC 编号与设计稿口径不符（设计稿：RC-1=suspect 字段 design.md:271、RC-2=改标命令 :272、RC-3=读取面 :273-275） | **已闭合**：Task 来源段改「RC-2 改标命令 / RC-3 读取面」；AC2 行改「（RC-3；RC-1 suspect 不在本 Task 范围）」 | Task 文档 |
| P3-6 | 报告未标明 C2/C3 的验证分层 | **已闭合**：§2 可测性说明明示 C2/C3 各需覆盖 service guard 层（`GuardStatus` 返回且零覆盖，`service.py:483-496`）+管线候选持久化层（StepResultCandidate 不丢弃）两层，T5b 用例表两层各设断言 | 报告 §2 |
| P4-1 | `SetRegionType` 与 `SaveManualTranslation` 的 `expected_revision` 语义缺交叉指针 | **已修**：双向指针——`SetRegionType` 条目声明两命令同模式、region 写命令面以本条目+C4 为权威；§5 表 `SaveManualTranslation` 行「精确并发策略 UNKNOWN」边界注记不变 | 契约 §5.4 `SetRegionType` 条 |
| P4-2 | （DSH r1 提出） | **登记不修**：按返修授权清单登记，本返修不改 | — |
| P4-3 | 错误码表未区分两命令的覆盖范围 | **已修**：表头注记覆盖范围——`ListRegions` 仅产生 `INVALID_REQUEST`/空列表/`UNKNOWN`，乐观冲突与目标缺失行为 `SetRegionType` 专属 | 契约 §5.4 错误码条 |

**r1 复验**：`git diff --check` EXIT=0；返修 diff 面仅 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md`、`doc/handoffs/M2-REGION-RETYPE-CONTRACT-a108996b.md`、`doc/tasks/M2-REGION-RETYPE-CONTRACT.md` 四文件（全部在本 Task 允许修改范围内）；`src/**`/`tests/**`/`apps/**`/`packaging/**`/`doc/STATUS.md`/既有设计稿零 diff。r1 源码事实复核命令：`grep -n "source_run_id" src/application/editing/service.py src/application/editing/ports.py src/infrastructure/providers/handlers.py`（创建/用户写路径无该参数，仅 `handlers.py:354/439` text 写路径）、`sed -n '95,115p' src/bootstrap/core_service.py`（`E_INVALID_REQUEST = "INVALID_REQUEST"` 大写字面量）、`grep -c 忽略 doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（0，设计稿无该表述）。
