已完成静态只读审查（沙箱禁命令，`git diff` 类运行级证据无法复核；契约文本、源码锚点、设计稿交叉引用均已逐条核对）。

# M2-REGION-RETYPE-CONTRACT 独立 Review（非作者：DeepSeek Harness）

审查边界：只读、无文件修改；`pwsh`/`git` 在本沙箱不可执行，故报告 §4 的 `git diff --stat`(+59/−3)、`git diff --check`、`src/**` 零 diff 声明**未验证**（仅能确认交付物落在允许面、文本层未见代码改动痕迹）。runtime 行为按用户声明未验证。

## Verdict

**changes_requested**（理由：契约冻结的核心价值是 wire 口径唯一，但 §5 表与 §5.4 对 `ListRegions` result 给出**两种不兼容形状**（P1）；另有 3 项 P2 为契约正文的事实性/逻辑性错误——AC5 理由链自相矛盾、AC4 引用了设计稿中不存在的「忽略」表述、`source_run_id` 溯源锚点在检测路径不成立。全部为**文本级修复、零代码**，但按 Handoff「Review 要求改契约须回 owner 分支修订」的纪律，不能由集成方静默闭合，故不判 approved_with_conditions。契约主体方向、保护语义纪律、错误码族复用、范围纪律均合格。）

## 发现清单

**P1-1｜M2-C1:120 vs M2-C1:176｜`ListRegions` result 形状自相矛盾（阻塞）**
§5 表行写 `{page_id}` → `RegionSummary[]`（裸数组），§5.4 写 result 为 `{"regions": RegionSummary[]}`（包装对象）。两者同为 transport-neutral 口径、同命令名、同 DTO，不属 §5.3 那种「表行 transport-neutral 名 vs 产品面」的抽象级差异，且 §5 表该行**没有**「以 §5.4 为准」的注记（§5.3 先例有）。
建议：统一为 `{"regions": RegionSummary[]}`，或在该行加「result 包装形状以 §5.4 为准」注记。

**P2-1｜M2-C1:175｜AC5 理由链内部矛盾**
在「继承原快照」假设分支下写「全局 `translate` … 永久不可达……无自愈路径（唯一恢复手段是再改标一次）」。继承语义下再改标仍是继承 skip，**不构成恢复手段**，与同句「永久不可达」直接冲突（也与 ②「改标=重新类型化」的论证无关）。技术锚点本身成立（`gate.py:32-42` 消费 region 快照、`core_assembly.py:1036-1045` 非 SFX 强制 skip）。
建议：删除/改写括号句，改为「继承分支下无 region 级自愈路径（除软删除后重新检出），须新授权修订」。

**P2-2｜M2-C1:214 + 报告 §3.2 差异 3｜AC4 的事实前提不成立**
契约写「设计稿语境中以「忽略」描述的用户可见语义」。实测：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md` 全文 grep「忽略」**零命中**；用户可见近义表述是「保留原文/停止翻译/不翻译」（design.md:41/236），而 R-015（design.md:86）是「疑似警示收窄 speech」，与「忽略」无直接语义关系。「忽略」的真实出处是 Task 合同 AC4 所称「Codex 第 8 点」。
建议：依据改标为 Task/Codex 语境，并在 §5.4/报告 §3.2 明示「设计稿无该表述」，R-015 与「忽略」的关联限定为「同属 RegionType 闭集纪律」。裁定内容（六值零新增、处理动作/过滤状态、预拒绝持久化）本身正确，无需改。

**P2-3｜M2-C1:189 + 报告 §3.2 差异 1｜`source_run_id` 溯源锚点不成立**
契约称机器改标可追溯权威 = `origin=machine`「（+ revision 链 `source_run_id` 溯源）」。源码事实：检测/仲裁创建 region 走 `core_assembly.py:1032-1048` → `RegionEditingService.create_region`，该路径**无 `source_run_id` 参数**，经 `_commit_user_or_raise`（`service.py:222-241`）构造 revision 时 `source_run_id=None`；`source_run_id=run.run_id` 只出现在 text 写路径（`handlers.py:354/439`），且 revision 无回填路径（`add_revision` 单点 `service.py:135`）。即 `sfx-arb-`/检测产出**没有**该溯源字段。
建议：删除该锚点或改为「（+ 检测步 provenance/StepResult 记录）」，并把 A7 可追溯落点限定为 `origin` 字段（`entities.py:267-288` 无 label 的判断正确、应保留）。

**P3-1｜M2-C1:169-171｜改标 revision 的 `review_state` 未规定**
契约冻结「snapshot 仅 `region_type`/`sfx_policy` 两字段变化」，但 `RegionRevision.review_state` 是 revision 级字段（`save_manual_translation`=NEEDS_REVIEW、`save_geometry`=UNREVIEWED），改标笔取值未定；设计稿「叠加语义不合并」含 Review State 层（design.md:60）。建议明确取值与是否触发"需校对"变化，否则 T5b 自由裁量可能产生 UI 可见漂移。

**P3-2｜M2-C1:120-121 + 176-186｜`RegionSummary` 单一定义隐式收窄 `CreateRegion` result**
`CreateRegion` 的 result 类型即 `RegionSummary`，本修订把它首次定义为**不含几何**的最小集，故 `CreateRegion` result 也随之不含几何；而画布 overlay 正需几何（设计稿 D5 缺口，本契约声称"保持登记、不越权"）。注记声明"CreateRegion result 语义不在本修订改变范围"与类型复用事实相抵。建议：读取面另立 DTO 名（如 `RegionListSummary`），或明示"CreateRegion result 即本最小集、几何由 D5 缺口另行承接"。

**P3-3｜M2-C1:7/196、C3:204｜「零新码」措辞与字面量大小写**
①`INPUT_REVISION_CHANGED` 此前未以 `ErrorEnvelope.code` 出现在 M2-C1（§8 表无行），本修订首次写入协议 code 位；"零新码"严格说是"复用既有 GuardStatus 语义"，建议措辞收紧为"零新错误语义"。②`errors.py:19` 的 **value** 是小写 `input_revision_changed`（C3 的 `LOCK_CHANGED` 同理 = `lock_changed`），而 §8 要求"源 code 保持 Core 原值"，契约 wire 用大写 name。建议明文规定 wire code 取哪个字面量，避免 T5b/前端大小写不匹配。③错误码表未含 `LOCK_CHANGED`（C3 使用，虽属机器写而非本命令响应），建议加脚注消歧。

**P3-4｜M2-C1:195-197｜`page_id` 本身无效未归类**
表行只覆盖"`region_id` 不存在/soft-delete → `TARGET_NOT_FOUND`"与"`page_id` 无存活 region → 空列表"；`page_id` 不存在/不属于本书章节未映射，实现可返回空列表或报错。建议补一行。

**P3-5｜doc/tasks/M2-REGION-RETYPE-CONTRACT.md:22/27｜Task 的 RC 编号与设计稿错位**
Task 写"核心（RC-1/RC-2）冻结"、AC2 标"读取面 DTO 冻结（RC-1）"，但设计稿编号为 RC-1=suspect(D2)、RC-2=改标命令(D3)、RC-3=读取面(D4/D5)。契约与报告已采用设计稿口径（RC-1 不裁决、读取面落 RC-3），**处理正确**；Task 文本待集成收口时修正编号。

**P3-6｜M2-C1:203｜C2 的候选持久化验证点归属**
`service.py:483-496` 只返回 `GuardedWriteOutcome`；候选表写入属管线层（`errors.py:23-30` 明示 candidate table belongs to TASK-011）。建议报告 §2 转录测试用例时标明 C2/C3 需覆盖两层（service guard 返回 + 管线候选持久化），否则 T5b 只测前者。

**P4-1｜M2-C1:123 vs 169｜`expected_revision` 语义不对称**：`SetRegionType` 被冻结为会 typed 拒绝，`SaveManualTranslation` 仍标 UNKNOWN/NOT_FROZEN。无冲突，建议加交叉指针。
**P4-2｜M2-C1:202｜C1「不被运行中 Run 阻塞或排队」**：「不排队」依赖未实现的 Core 调度（stdio JSON-lines 单进程），建议 T5b 落为可观察事件序（用户写不等待 Run 写完成）。
**P4-3｜M2-C1:195｜错误码表混排 SetRegionType/ListRegions 校验行**，建议分列或在表头注明覆盖两命令。

范围与报告质量：交付面 = 契约 1 文件 + Task + Handoff + `verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md`（glob 确认仅此 1 份），全部落在允许面；报告 §5「诚实边界」、§3.3 与上游仲裁 Task（`sfx-arb-`/IoU 0.90）核对、Handoff 的 Gate 与 Recovery point 均合格。`src/**`、`tests/**`、`apps/**`、`packaging/**`、`doc/STATUS.md` 零 diff **未验证**（沙箱禁 git）。

## 逐 AC 结论

- **AC1 PASS** — §5 表 `SetRegionType` 行（M2-C1:119）与 §5.4（169-171）请求 `{region_id,new_region_type,expected_revision?}`、响应含 `revision_no`+生效态、origin 恒 `user`、改标=经 commit seam 新 revision、撤销=引用既有 `RestoreRegionRevision` 不重定义，与 `service.py:202-241/521-529/550-572`、`entities.py:31-37/243-245` 逐条吻合；四值枚举零新增，协议 minor 目标 2→3 与 `core_service.py:92 PROTOCOL_MINOR=2` 自洽。附 P3-3、P4-1 观察。
- **AC2 PARTIAL** — DTO 五字段（`region_id/region_type/sfx_policy/origin/revision_no`）与"读取面不含训练语义"、取舍=新命令的三条理由、`reading_order` 升序（`service.py:279-281`）、label 不持久化的纠正（`entities.py:267-288`）均成立；但 **P1-1**（result 形状 §5 表 vs §5.4 冲突）、**P2-3**（`source_run_id` 锚点不成立）、**P3-2**（`RegionSummary` 隐式收窄 `CreateRegion` result）使该 AC 未达冻结标准。
- **AC3 PASS** — C1–C7/P1–P4 共 11 条两行式断言与源码吻合：`_commit_user_or_raise` 无期望/无 lock（`service.py:222-241`）、committer 仅在 `lock_snapshot is not None` 时检查 lock（`service.py:105-128`）⇒「用户写不受 lock 阻塞」成立；C2 期望优先于 lock（`service.py:483-496`，同序二次确认于 committer:105-128）；C7（`_require_region`→`RegionNotFound`，`service.py:174-178`）；P2 幂等复用（`handlers.py:246-269`）；P3 快照含 `sfx_policy`（`entities.py:284`）。附 P3-6、P4-2。
- **AC4 PARTIAL** — 裁定内容正确（六值闭集零新增、处理动作=`SKIP_POLICY(reason=sfx_skip)`（`gate.py:39-42`）/过滤状态=§5.2 UI-local、对持久化方向预拒绝）；但 **P2-2**：设计稿全文无「忽略」，差异登记的归因对象错位。
- **AC5 PARTIAL** — 裁决=「按改标时全局配置重快照」+「非 sfx 强制 skip」结论正确，技术链成立（`gate.py:32-42` + `core_assembly.py:1036-1045`，非 SFX 强制 SKIP 与 speech 快照恒 skip 核对一致），与设计稿 §4.2 translate 行前置（design.md:238）**确为零返工**；但 **P2-1** 理由链含自相矛盾句，需修正后方可作为 RULED 条款长期引用。
- **AC6 PASS** — 三处明示不授权 runtime（M2-C1:3/7/167、216），§5.4 末条明示 §1–§4/§6–§10 原样适用，§12 未见改动痕迹，minor 2→3 与源码自洽；§11 两行注记（376/378）为收紧而非放松。`git diff` 面未验证（沙箱）。

**给作者的最小返修清单（文本级，零代码）**：P1-1、P2-1、P2-2、P2-3 必须在 Revision history `1.4` 段注记后修订；P3-1/P3-2 建议同批处理（均属冻结口径完整性）。返修后由集成方复跑命名/形状一致性核对，再行集成收口。
