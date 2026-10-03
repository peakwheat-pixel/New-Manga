## Verdict
**approved_with_conditions**

R-001..R-018 **18/18 全部闭合，未闭合 = 0**。r2 声称的处置与文档实际内容逐条对上，且 r1 中 R-001/R-003 两条**事实修正**的底层事实经源码复核成立（非仅措辞）：
- `core_assembly.py:1041-1045`（非 SFX 强制 `SfxPolicy.SKIP`）+ `editing/service.py:254`（`create_region` 默认 `SKIP`）→ design.md「speech 快照恒 skip」成立；
- `gate.py:32-42`（skip/manual 同判 `SKIP_POLICY`）、`detection_sfx.py:202/723-753`（`sfx-arb-` 前缀）+ `core_assembly.py:1047`（`origin=RegionOrigin.MACHINE`）→「机器改标 = 确定态 + prefix + origin=machine」成立；`entities.py:31-37` RegionOrigin 四值、M2-C1 L120 `SaveManualTranslation → {revision_no}` 先例均已核实。

附 2×P3 + 2×P4 新增项（见下），全部为**文档级精度/证据一致性**，不含语义翻转、不含契约 widening，可在集成 commit 一并修，故不升 changes_requested。

核验方式与限制：本会话 `pwsh` 被文件沙箱拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，任何 cwd 均失败），**无法运行 `git diff/status`**；改为直读 `.git/worktrees/M2-SFX-MISROUTE-UI-MITIGATION-zcode/logs/HEAD` 核验提交链，确认 `fb5d56c6 → 8d844726(claim) → c92eaddd(delivery) → 519a5019(handoff) → 42be3c11(r1 rework) → 3f589a0b(handoff r1 record, 当前 tip)`，即 `rework_head=42be3c11` 实测存在。r1 返修的 diff 面（零产品代码）本轮**未能独立核验**。

## 逐条闭合表

| 编号 | 级别 | 结论 | 证据（文件+位置） |
|---|---|---|---|
| R-001 | P2 | 闭合 | `design.md` §4.2 L231「表键 = 改标后该 region 自身的 policy 快照值」、L237 translate 行前置「仅当 RC-2/EV-8 裁决为重快照」、L241-242 全局降为不一致辅助解释；§1.3 L47 补快照口径注记（speech 恒 skip） |
| R-002 | P2 | 闭合 | §4.1 mermaid L212/L213 守卫②双来源回退（SFX_TYPE←/SFX_ARB←）、L216 `SFX_ARB_RELABEL --> SFX_ARB`（restore 至机器笔）、L217 反向出边；R5 L226 守卫①回触发态、R6 L227 守卫②明文（mermaid 回退边缺口见 N-1） |
| R-003 | P2 | 闭合 | §5 D2 L270 `source: "human"\|"heuristic"` + 「不含 arbitration」；§4.1 R1 L222「仲裁不在来源枚举内」；§7.2 EV-1 L316「新增来源值=契约修订」；§2 第 5 条 L59 `sfx-arb-`+origin=machine（三处一致） |
| R-004 | P2 | 闭合 | §6 A13 L302 拆 (a) 徽标合成底 ≥4.5:1 / (b) E1 对 `bg-canvas` 非文字 ≥3:1 + 双载体强制；§3.5 L170-175 同步双档口径 |
| R-005 | P3 | 闭合 | §3.1 E3 行 L74「组合无既有审计证据，由 A13(a) 首次取证」；§3.5 L174「既有审计不覆盖不构成豁免」；A13(a) L302 点名 R-005 |
| R-006 | P3 | 闭合 | §6 A9 L298 限定「不得前端**决定**是否翻译/如何渲染」+ 明示查找表映射与决策的分界 |
| R-007 | P3 | 闭合 | §3.3 L150「数据来源依赖 §5 D8/RC-5 的 reader 摘要字段——OPEN；**非 D6**，D6 是 policy 生效态」 |
| R-008 | P3 | 闭合 | §3.2 L88 同位共存优先级（左上 E2>E3 独占；八态徽标右下角、工具 pill 在工具条内）+「三层既有+本设计两层=五层」；§2 第 6 条 L60 五层计数 |
| R-009 | P3 | 闭合 | §5 D3 L271 响应含 `revision_no`（沿 `SaveManualTranslation→{revision_no}` 先例，M2-C1 L120 已核实）+ undo=restore 到改标前 revision 的注记 |
| R-010 | P3 | 闭合 | Task L5 `status: in_review`、L17 `rework_head: 42be3c11`；Handoff L7-8 同步；Task L69-73 返修记录段；`logs/HEAD` 证实 42be3c11 为 r1 rework commit（残留 NOT_RUN 见 N-2） |
| R-011 | P4 | 闭合 | §3.1 L68 hex「仅写作时点对照参考，**非定义来源**，真值链冲突以 token 真值链为准」 |
| R-012 | P4 | 闭合 | §1.1 L30「BJ15 **ref1** 更深盲形态…（ref2 仅 3 候选且最高 sfx 0.0000）」；§6 A2 L291 同步限定 ref1 |
| R-013 | P4 | 闭合 | §5 D7 L275 写全 `machine/user/imported/restored` 四值并注明本设计涉及 user/machine |
| R-014 | P4 | 闭合 | §5 D8 L276「`GetReaderProjection` 结果 DTO 结构未定义（契约仅列命令名与 AS-IS 证据），无 region 摘要面」 |
| R-015 | P4 | 闭合 | §0 L15「限 speech region」；§3.2 L86 R-015 收窄+其余类型出口不在范围；§4.1 R1 L222 非 speech 不建模；§7.2 EV-1 L316 登记未来扩展 |
| R-016 | P4 | 闭合 | §3.1 E2 行 L73 与 E3 行 L74「20px/3px 8px 字面量实现时登记为组件常量，沿 M2-UI1 D-2 先例，升令牌归实现 Task 裁决」 |
| R-017 | P4 | 闭合 | §4.1 mermaid L183-218 全文无半角分号（对 design.md 全文 grep `;` 零命中），标签统一中文括号/冒号 |
| R-018 | P4 | 闭合 | 头部依据链 L7「M2-C1 rev 1.3（§5.3 settings 通道 = 与 region policy 相关的唯一已落地 IPC 面）」，与 M2-C1 L150「范围仅此两命令」一致 |

同步声明核验：Handoff L88-113「DSH r1 修订段」18 行对照表齐备；`ac-self-check.md` §4 L43-54 已补；Task L66/L69-73 已补（均与 design.md 实际内容一致）。

## 新发现
- **P0/P1/P2：无。**
- **N-1（P3）**：`design.md` §4.1 mermaid 缺 U 型回边——L217 新增 `SFX_ARB_RELABEL --> CONFIRM_X2S : 入口触发（反向）`，但 `CONFIRM_X2S` 的取消/失败出边只有 L212 `→ SFX_TYPE` 与 L213 `→ SFX_ARB`（L213 标注「自 `SFX_ARB` 触发」），**没有 `→ SFX_ARB_RELABEL`**；而 R6 L227 明文要求「自 `SFX_ARB`/`SFX_ARB_RELABEL` 触发回原态」。按图实现会把取消后的呈现落回 `SFX_ARB`，丢失「人工改标叠加在机器笔上」的当前态（与 A7 可区分原则及 §7.3 冻结的状态机拓扑不一致）。修法：补 `CONFIRM_X2S --> SFX_ARB_RELABEL : 取消或失败（守卫②来源回退：自 SFX_ARB_RELABEL 触发，人工笔保留）`。规约文字已正确，故不判 R-002 未闭合。
- **N-2（P3）**：`doc/tasks/M2-SFX-MISROUTE-UI-MITIGATION.md` L54 测试要求表「实际结果」列仍写「DSH review **NOT_RUN（待派发）**」，与同文件 L66/L69-73（r1 verdict 已出、`in_review`、rework=42be3c11）**互相矛盾**；集成方若只读该表会误判 review 未执行。应更新为「r1 = approved_with_conditions（18 条已返修）；r2 闭合复核 = 本报告」。
- **N-3（P4）**：`design.md` §3.5(b) L175「E2 徽标 pill 自带 `bg-raised` 衬底」与 §3.1 E2 行 L73（底 `warn-soft`）、同段 (a) L174（「`*-soft` 以 alpha 叠 **panel** 合成后比较」）三处衬底基不一致，A13(a) 取证时合成基不明。建议删去 `bg-raised` 或明确 E2 的唯一合成基。
- **N-4（P4，流程）**：`doc/reviews/` 全表（230 项）**无本 Task 的 r1 review 文件**（grep `MISROUTE` 零命中），而 Handoff L61「接收方式」要求复核产出落 `doc/reviews/`。后果：R-001..R-018 的**原始条件文本**仅存于作者自述对照表，后续审计无法回溯原始口径。建议本 r2 报告落盘为 `doc/reviews/M2-SFX-MISROUTE-UI-MITIGATION-3f589a0b-dsh-r2.md`。

推荐下一步：集成方按 N-2 更新 Task 测试表（一行）并连同 N-1 补边（一行 mermaid）合入，然后依 r1 R-010 口径把该 Task 流转 `in_review → done`；N-3/N-4 可随集成 commit 或后续文档整理处理。
