---
task_id: TASK-059
reviewer: Codex
author: ZCode
base_commit: 4c81dca6186f9b47f2771e5033a5d6ecfa986dd6
reviewed_head: db366da095d3cb6ed6e234e87b842092ba506c0b
decision: changes_requested
---

# Review：TASK-059

Reviewer=`Codex`（非作者）。固定 base=`4c81dca`、reviewed_head=`db366da`。本次只读审查作者工作区；Review 报告在独立分支 `agent/codex/TASK-059-review`。

## 范围与依据

审查范围：`4c81dca..db366da` 全量 diff、TASK-059 AC、契约、五候选离线参考、JSON 令牌、Handoff、审计脚本与截图证据。

重点按用户指定执行：

1. A～E 主视图与工作台视图并排目检，判断视觉语言/IA 是否真实换方向。
2. 核对契约 §6A/§6B 的代价取舍，特别是 D 顶栏、E 命令面板 ND-9 与 26px 触达例外 ND-10。
3. 把审计数字与截图目检分开；数字不得代替视觉结论。

未审部分：真实 Qt/QML 渲染、焦点遍历、屏幕阅读器、真实 Windows 多屏设备矩阵均属未来实现 Task；本设计 Task 不要求其 PASS。

## Standards

`executed`。变更仅落在 `doc/**` 与 `verification/TASK-059/**`，没有改 `src/**`、`tests/**`、Schema、依赖或产品文档，符合 TASK-059 的范围边界。代码层面不适用；文档真值链、证据口径和机器可读副本是本次主要 standards 面。

## Spec

`executed`。五候选在视觉语言/IA 上确有实质差异，AC ② 的“不是同一方案换密度”成立；D 的顶栏和 E 的表格+命令面板是范式差异。但 AC ② 的代价取舍、AC ④ 的对比度硬事实以及 AC ⑥ 的验证证据仍有缺口，故不能批准。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `doc/contracts/UI_UX_GUI_DESIGN.md:153,193`；`doc/design/ui-reference.html:365-367,1379-1385` | 契约声明状态徽标为 `*-soft` 底 + `st-*` 字且文本对比度 ≥4.5:1，但审计实际拿 `st-*` 与 `--bg-panel` 比较，没有测徽标真实背景；真实小字号徽标在多个亮色主题低于 4.5:1。 | 按 badge 实际 `*-soft` 半透明底叠加当前 `bg-panel` 独立复算：A/C 亮色 `warn=4.22`、`ok=4.44`、`lock=4.35`、`block=4.32`；B 亮色 `warn=4.29`、`ok=4.41`；D 亮色 `warn=4.33`、`block=4.44`、`lock=4.47`；E 亮色 `run=4.42`、`ok=4.35`、`warn=4.14`、`fail=4.49`、`lock=4.27`、`block=4.24`。徽标使用 `--fs-sm` 小字号，不能按大字号的 3:1 门槛豁免。 | 审计改为读取 DOM 中 badge 的实际前景/背景；修正 `*-soft` alpha 或状态文字令牌；重新生成 JSON、截图与审计结果。 | open |
| R-002 | P2 | `doc/contracts/UI_UX_GUI_DESIGN.md:126,133,202,238-244,274` | E 的命令面板被定义为“新交互机制”，但 §6B 只给“需要命令注册与搜索 VM、成本中等”的高层描述；§10 同时写“不新增必需 objectName”，§11 又要新增 `S-CMDPALETTE` VM。没有命令注册、可用/禁用、危险动作、查询/筛选、焦点恢复、IME/CJK 组合输入、快捷键冲突和 objectName 契约。用户无法据此完整裁决 ND-9，后续实现也缺少稳定交接面。 | 对照 §6B 与 §10/§11；`e-dark-palette.png` 只展示静态面板分组和快捷键，没有验证上述交互语义。 | 在 §6B 补齐命令面板的 VM/命令模型、状态与失败语义、快捷键优先级、IME/焦点策略、危险动作确认和测试切面；在 §10 明确新增 objectName 或明确复用规则。 | open |
| R-003 | P2 | `doc/contracts/UI_UX_GUI_DESIGN.md:238-244` | 实现切片矩阵没有覆盖 D/E 的完整视觉差异：`S-WB-INSPECTOR` 只列 A/B/C，`S-SHELF-BOOK` 也只覆盖 A/B/C。D 的编辑部页头、hairline 工作台和 E 的字段表 Inspector 没有对应切片；若用户选择 D/E，Gap→实现计划会断链。 | `S-TOPNAV` 只负责导航重排，`S-SHELF-TABLE` 只负责 E 表格；D 书架页头/E Inspector 无落点。 | 扩展 `S-SHELF-BOOK`/`S-WB-INSPECTOR` 到 D/E，或新增 D-shelf/D-workbench、E-inspector 等独立切片，并写依赖与验收面。 | open |
| R-004 | P2 | `doc/design/ui-reference.html:1401-1422`；`doc/tasks/TASK-059.md:63`；`doc/handoffs/TASK-059-three-candidates.md:44` | 任务/Handoff 声称做了“溢出/重叠审计”，但脚本只初始化 `overlap:0`，从未检测元素两两相交；审计 JSON/终端输出只含 `outside`、`clipped`。因此“重叠审计通过”没有实现基础。 | `layoutAudit()` 从未修改 `issues.overlap`；`audit-result.txt` 也不输出 overlap。 | 实现实际重叠检测并输出失败元素；若本切片不做，则把“重叠”改为人工截图检查并记 `NOT_RUN`，不得写成自动审计 PASS。 | open |
| R-005 | P2 | `verification/TASK-059/audit-result.txt:1-6`；`doc/handoffs/TASK-059-three-candidates.md:43` | Handoff 声称 `audit-result.txt` 含 `EXIT=0` 与 shell 头，但文件实际直接以 `== 1) JS 语法门 ==` 开始，没有 shell/venv 头，也没有显式 EXIT。该证据不满足仓库 Q-009 证据纪律。 | 文件首 6 行只有审计阶段和首项结果，无运行环境/解释器与退出码。 | 用固定 shell/venv 重跑并把环境头、命令、EXIT 写入同一日志；同步修正 Handoff 的“含 EXIT=0 shell 头”声明。 | open |
| R-006 | P3 | `doc/contracts/UI_UX_GUI_DESIGN.md:18,153,193,283`；`doc/handoffs/TASK-059-three-candidates.md:31,44,45`；`verification/TASK-059/run-reference-audit.sh:4`；`verification/TASK-059/export-tokens.py:4,89` | R2 后仍有多处 R1 真值残留：契约 §1 仍写“30 组合/26 截图”，§7.2/§9 仍写三候选，DDR-1 仍写“交付三个”，脚本头仍写 3 候选，导出脚本说明仍只写 `{a,b,c}`，D/E JSON 的非玻璃说明仍写“候选 A/B 不启用”。这些会与 §15/Handoff R2 段的五候选、50 组合、41 截图冲突。 | 同文件内 R2 口径与 R1 口径并存；`tokens-cand-d/e.json:11` 均写“候选 A/B”。 | 全量把 R1 计数更新到五候选/50 组合/41 截图；DDR-1 注明 R2 由 DDR-8 扩展；导出脚本和 D/E JSON 的说明改为通用“非 C 候选不启用玻璃”。 | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定点校验 | `git rev-parse` | review worktree @ `db366da` | PASS | base/head 均解析成功 |
| 变更范围 | `git diff --name-status` | `4c81dca..db366da` | PASS | 仅 `doc/**` 与 `verification/TASK-059/**` |
| 空白/补丁卫生 | `git diff --check` | `4c81dca..db366da` | PASS | 退出码 0 |
| HTML 语法门 | `node -e` 提取最后一个 `<script>` 并执行 `new Function` | Node + worktree @ `db366da` | PASS | `syntax ok` |
| 矩阵/截图数量 | 读取审计结果和文件清单 | `db366da` | PASS | 50 条矩阵结果、41 张 PNG |
| 五候选视觉目检 | A～E bookshelf/workbench contact sheet + E palette | `db366da` 截图 | PASS | D 顶栏、E 表格/命令面板确实为范式差异；其余候选也有可辨差异 |
| 真实徽标对比度 | 对 `*-soft` 半透明底与 `st-*`/`ink-2` 前景独立复算 | `db366da` 令牌 + CSS | FAIL | 多个亮色主题状态徽标低于 4.5:1，见 R-001 |
| 重叠审计 | 阅读 `layoutAudit()` 与 `audit-result.txt` | `db366da` | FAIL/BLOCKED | `overlap` 无检测逻辑，证据未输出该指标 |
| 审计证据纪律 | 检查日志头/尾 | `audit-result.txt` | FAIL | 无 EXIT 与 shell/venv 头，见 R-005 |
| 作者工作区只读 | 不在 `TASK-059-zcode` 写入 | - | PASS | Review 报告在独立分支 |

## 结论与复审

**Architecture/流程面**：设计产物未越界，未触碰 `src/**`、`tests/**`、Schema、依赖或产品文档；但 E 命令面板缺少可实现的 VM/objectName/交互契约，D/E 的实现切片不完整。

**Verification 面**：五候选视觉方向确实成立，但 AC ④ 的对比度结果被错误审计方式高估，且“重叠审计通过”和 `EXIT=0 shell 头`两项证据声明不成立。P1 未解决，关键验证缺口仍存在。

**决定：`changes_requested`。** 修订后固定新 head，至少关闭 R-001～R-005；R-006 可同批文档收口。复审时重点确认真实 DOM 徽标对比度审计、命令面板契约与 D/E 切片闭环。
