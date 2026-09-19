---
task_id: TASK-059
author: ZCode
recipient: Codex（Reviewer，非作者）
base_commit: 4c81dca6186f9b47f2771e5033a5d6ecfa986dd6
delivery_head: 5578a01（R1 参考+证据） / ddaf865（R1 契约） / dd455c0（R2 参考+证据） / af91e06（R2 契约） / 07397ac（R3 返修：审计与令牌修正+文档收口） / 本次提交（R4 组合候选 F：Graphite Atelier + 全量重审计）
status: in_review
---

# Handoff：TASK-059（三候选设计交付）

> **R2 修订（2026-09-19，交付后追加）**：用户在本 Handoff 提交后指示「再增加两种完全不一样的设计」。R2 已交付候选 **D · Vermilion 朱砂**（一级导航 rail→顶部导航条 + 编辑部印刷网格；导航范式变化，ND-8）与 **E · Amber 琥珀**（全 UI 等宽 + 书架表格化 + Ctrl+K 命令面板；新交互机制 ND-9、26px 触达显式例外 ND-10）。契约以 R2 为准（§6A/§6B、DDR-8）；候选总数 3→5，**AC② 的「2–3 个」由用户指示扩展为 5**，Task 文件已记录该口径变更。证据矩阵 30→50 组合（ALL PASS，`EXIT=0`）、截图 26→41 张。R2 提交：`dd455c0`（参考+证据）、`af91e06`（契约）。以下正文为 R1 内容，R1 的 AC 对照对 D/E 同样成立（对照关系见文末 R2 补充表）。

## 交付结果

按开工指令交付 **3 个在视觉语言或 IA 上实质不同的候选方向**（不是同一方案的三种密度），全部落在允许修改路径内；未触碰任何禁止路径（`src/**`、`tests/**`、Schema、D01～D08、ui-baseline 等零改动，`git diff --check` 退出码 0）。

**提交列表（base `4c81dca` 之后，分支 `agent/zcode/TASK-059-ui-redesign`）**：

| commit | 内容 |
|---|---|
| `5578a01` | `doc/design/ui-reference.html`（离线视觉参考，单文件）、`doc/design/tokens-cand-{a,b,c}.json`（机器可读令牌）、`verification/TASK-059/**`（审计脚本、审计结果、26 截图、令牌导出脚本）<!-- R1 时点数字；R2 起为 5 JSON/41 截图，现行口径见文末 R2/R3 节 --> |
| `ddaf865` | `doc/contracts/UI_UX_GUI_DESIGN.md`（契约，240 行：方向宣言/三候选规格/令牌/状态映射/组件映射含 Q-011/Gap/DDR/待决项/AC④ 对照/证据索引） |
| 本次提交 | 本 Handoff + TASK-059 置 `in_review` + STATUS 台账行 |

**三候选**：A · Graphite 石墨（暗色优先高密度工作室；Inspector 译文置顶）/ B · Atelier 画廊（亮色优先暖纸白 `#f7f5f1` + 青瓷 `#0f766e`，章节大卡）/ C · Duo 双面+玻璃（画廊×车间双主题 + 浮层玻璃 blur 22–26px，书架两级浏览；唯一含实现风险的候选）。

**AC 对照**（逐条证据见下表）：

- **AC ①** ✅ 契约 §2 逐条回答 R-1/R-2/R-3，每条指认到候选的具体差异（R-1→§3 强调色行；R-2→A 的 Inspector 重排/B 大卡/C 两级浏览；R-3→提案为主体、取证压缩为 §11 Gap 矩阵）。
- **AC ②** ✅ 3 候选 × ①角色定位 ②完整令牌表（JSON 每份 42 色 × 2 主题 + 20 几何）③五页视图截图（书架/工作台/阅读器/设置/状态矩阵，超过「至少 3 页」）④IA 说明（契约 §4–§6）⑤代价取舍（各候选末节）。
- **AC ③** ✅ `doc/design/ui-reference.html` 单文件离线可开，带评审 chrome（候选/主题/玻璃/DPI/审计/工具窗按钮）；复用并扩展 TASK-047 的自检工具思路（语法门+审计矩阵），未复用其方案内容。
- **AC ④** ✅ 契约 §12 对照表：DPI 硬事实、对比度、三重编码、截断规则、4Hz 节流、九态语义**沿用**；ui-baseline 色板作为目标方向被**显式推翻**（授权范围内），As-Is 文档未改动。
- **AC ⑤** ✅ 契约 §13：ND-1～ND-7（必须用户裁决）+ 设计可自决项；TASK-047 Q-1～Q-10 复核结论并入（视觉细节项转实现切片自决，产品语义项仍归用户）。
- **AC ⑥** ✅ 契约**替代** TASK-047 版本（后者未合并入 master，本契约为新写非补丁）；`verification/TASK-059/**` 齐全；本 Handoff；未触碰 `src/**`（设计身份未授实现权）。

**建议契约章节结构（用户会话清单）采纳情况**：11 章全部覆盖——1 方向宣言=契约§2；2 令牌表=§7（含玻璃开/关）；3 状态映射=§7.2（三重编码）；4 组件规范含 VM/objectName=§10（含 Q-011）；5 IA 与分区差异=§4–§6 IA 节 + §8.1；6 布局适配=§8；7 动效=§9；8 可访问性=§9；9 Gap/切片=§11；10 DDR=§14；11 待决项=§13。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 参考可加载（JS 语法门） | `node -e "new Function(script)"`（`run-reference-audit.sh` 第 1 段） | 无头 Chrome + Node，worktree @ `5578a01` | **PASS**（syntax OK） | `verification/TASK-059/audit-result.txt`（**R3 勘误**：R1 交付时该文件并无 shell 头与 EXIT——见 Review R-005；R3 重跑后同日志含环境头/命令/`AUDIT_EXIT=0`，见文末 R3 节） |
| 对比度+溢出审计 | `bash verification/TASK-059/run-reference-audit.sh`（30 组合：3 候选 × 2 主题 × 5 视图 × 15 令牌对）<!-- R1 时点数字；R3 现行=50 组合 × 22 对（含徽标合成底）+ overlap 检测，见文末 R3 节 --> | 同上 | **PASS**（30/30 PASS，contrast 15/15、outside=0、clipped=0） | 同上 |
| 无头截图 | 同脚本第 3 段（26 张：15 默认 + 3 第二主题 + 4 玻璃对照 + 2 DPI + 2 工具窗）<!-- R1 时点数字；R3 现行=41 张 --> | 同上 | **PASS**（26/26 生成，关键张人工目检） | `verification/TASK-059/screenshots/*.png` |
| 令牌副本一致性 | `python verification/TASK-059/export-tokens.py` 前后字节比对 | Python 3.12 @ `ddaf865` | **PASS**（无漂移） | `export-tokens.py`；核对脚本内嵌于 Handoff 会话，结果见下「交叉核对」行 |
| 契约引用核对 | 链接目标存在性 + 截图引用 ↔ 实际目录 + 关键色值抽查（A accent/B ink-3 修正/C 玻璃参数） | Python 3.12 | **PASS**（CROSS-CHECK: ALL OK） | 本行（脚本输出原样：`CROSS-CHECK: ALL OK / EXIT=0`） |
| 工作区整洁 | `git diff --check` | Git Bash @ 交付前工作区 | **PASS**（退出码 0，无空白错误） | 本行 |
| Qt 实际渲染/pytest | **NOT_RUN** | — | NOT_RUN | 不适用：本切片纯设计（HTML/Chromium 呈现），无 `src/**` 改动；Qt 呈现属未来实现 Task 的验证范围 |

审计驱动修正记录（判别力证据）：A 暗色 accent 初稿 `#5b76f7`（白字 3.9:1）→ `#4d63e8`（4.92:1）；B 暗色 `ink-3` 初稿 `#8a8478`（4.32:1）→ `#948e80`（4.92:1）。两处均由审计矩阵 FAIL→PASS 驱动，历史见会话，终值已入 JSON/HTML。

## 接收方式

- 分支：`agent/zcode/TASK-059-ui-redesign`；worktree：`G:/CODEX/New Manga.worktrees/TASK-059-zcode`；交付 head=本次提交（含 Handoff），实现 head=`5578a01`、契约 head=`ddaf865`。
- 复现：浏览器直接打开 `doc/design/ui-reference.html`（或 `?cand=c&mode=dark&glass=on&page=workbench&dpi=150&audit=1`）；`bash verification/TASK-059/run-reference-audit.sh` 复跑全量审计（需 Chrome 与 Node，路径见脚本头）。
- Reviewer（Codex）建议检查优先级（TASK-059 风险条款）：**先判断「是否真的换了方向」**（A/B/C 并排打开书架+工作台各 2 分钟），再核对 AC 与引用完整性；审计数字不构成视觉结论（曾出现「矩阵全 PASS 但 states 页常显叠盖」的前科，靠截图目检抓出并修复）。
- 裁决入口：契约 §13 ND-1（选候选）为一切后续的前提；ND-2/ND-3 决定 C 的形态。

## 风险与遗留

- **全部值为 HTML/Chromium 呈现，非 Qt**。玻璃（仅 C）在 Qt Quick 无 backdrop-filter 原生等价物，S-GLASS PoC 必须先于任何玻璃实现切片；PoC 不过的降级路径已写入契约 §6/§11。
- 150% + 双工具窗超物理窗容量（`c-glass-both` 因此改用 125% 演示，DDR-5）；窗口管理策略为 ND-7 待决。
- 评审 chrome（framecap/审计按钮）属参考页工具，不是产品画面；`#page-states` 曾因 ID specificity 常显叠盖（已修复为 `.on` 门控），Review 截图时若见状态页叠盖请报告。
- TASK-047 分支（`980ae7d`）按任务要求未合并、未触碰；本交付仅复用其工具思路与硬事实，未复制其方案内容。
- 本 Task 与任何实现 Task 无写集合冲突（只写 `doc/**`、`verification/TASK-059/**`）。

## R2 补充：D/E 的 AC 对照与验证

| AC | D/E 对照 |
|---|---|
| AC ① | 契约 §2 R1/R2/R3 回答已扩为五候选口径：R-1 → D 朱砂 `#b3391b`、E 琥珀 `#e2b34d`（新色板，非既有灰蓝）；R-2 → D 顶栏导航重排、E 表格书架+命令面板（范式级，非换色）；R-3 → 提案主体继续扩大 |
| AC ② | D/E 各含 ①角色定位 ②完整令牌（`tokens-cand-{d,e}.json`，42 色 × 2 主题）③五页视图截图 ④IA 声明（契约 §6A/§6B）⑤代价取舍（含 26px 触达例外、字体 fallback、实现成本）；D/E 与 A/B/C 的差异是**范式**（导航位置/字体体制/信息形态/交互入口），不是密度变体 |
| AC ③ | 同一 `ui-reference.html`：chrome 候选按钮 D/E；`?cand=d` / `?cand=e` / `pal=1` 可复现 |
| AC ④ | 无新增硬事实推翻；E 的 26px 触达在 §9 显式记录为「低于本仓 28 底线、高于 WCAG 2.5.8 的 24」并挂 ND-10 |
| AC ⑤ | ND-8（顶栏导航）/ ND-9（命令面板）/ ND-10（触达例外）新增为用户裁决项 |
| AC ⑥ | 证据矩阵 50 组合（`5 候选 × 2 主题 × 5 视图`）**ALL PASS**、41 张截图、`audit-result.txt`（`EXIT=0`，尾随空白已在脚本源头 trim）；`git diff --check` 退出码 0 |

R2 审计驱动修正：E 暗色 `--ink-3` 初稿 `#737d8d`（4.47:1，FAIL）→ `#7b8595`（≥4.5，PASS）。D 全部组合一次通过。

R2 目检记录：`d-light-bookshelf.png`（顶栏 tab+朱砂指示条+衬线页头）、`e-dark-bookshelf.png`（命令条+表格行+状态徽标三重编码）、`e-dark-palette.png`（命令面板分组/快捷键/页脚）、`d-dark-workbench.png`（暖黑朱砂 hairline 工作台）均按预期呈现；`#page-states` 无叠盖复发。

## R3 返修记录（2026-09-19，Review `TASK-059-db366da` 判 `changes_requested` 之后）

Reviewer=Codex（非作者）固定 base=`4c81dca`、被审 head=`db366da`。以下为逐 finding disposition；全部改动仍只落在 `doc/**` 与 `verification/TASK-059/**`（`src/**`/`tests/**`/Schema/依赖零改动）。

| Finding | 处置 | 证据 |
|---|---|---|
| R-001（徽标对比度按错误底审计；多亮色组合 <4.5:1） | **closed**：审计 `tokenPairs()` 新增 7 个徽标对——真实前景/背景＝徽标实际文字令牌 × `*-soft` rgba 以 alpha 叠加 panel 的合成底（与浏览器渲染一致）；修正方式＝**五个候选亮色状态文字令牌统一加深一档**（`st-run→#0550ae`、`st-ok-t→#116329`、`st-warn-t→#7d5200`、`st-fail→#c01c28`、`st-lock→#6639ba`、`st-block→#953800`；B 亮色个性字面值一并对齐），`*-soft` alpha 与暗色主题不动；修正后徽标底全候选 ≥5.1:1，50 组合 × 22 对（15 直底 + 7 徽标）全 PASS；JSON/截图/审计全部重生成 | 修前复算数值与复审独立复算一致（warn=4.22 等）；判别 D1（回退旧令牌 → `badge-warn/st-warn-t=4.22` FAIL）；契约 §7.2 修正记录 |
| R-002（命令面板契约缺口；§10/§11 矛盾） | **closed**：契约 §6B 新增「命令面板契约」7 条（命令模型 `CommandDef`、`CommandPaletteViewModel` 面、状态与失败语义、危险动作只经既有确认流、Ctrl+K 焦点策略与还原、IME composition 语义、objectName 清单、测试切面）；§10 规则加**显式例外**：ND-9 批准后 S-CMDPALETTE 新增 `commandBarHost/commandPaletteHost/commandPaletteInput/commandPaletteList` 并在实现 Task 登记，未批准前不得预建 | 契约 §6B/§10（R3 版） |
| R-003（D/E 实现切片断链） | **closed**：`S-SHELF-BOOK` 扩展补 D 编辑部页头/黑规则线网格、E 表格行视觉语言；`S-WB-INSPECTOR` 扩展补 D hairline 网格面板、E 等宽字段表；表后新增「D/E 范式切片与共享切片边界」注记（导航→S-TOPNAV、表格 IA→S-SHELF-TABLE、命令面板→S-CMDPALETTE），每切片验收面＝§7–§9 条款 + §15 截图组合 | 契约 §11（R3 版） |
| R-004（overlap 从未检测却声称通过） | **closed（按复审建议实现）**：`layoutAudit()` 实现真实同级两两相交检测（交集宽高均 >2px 记一次，按父容器分组，父子包含与跨容器有意叠层不在同级判定内），JSON 输出 `overlap` 计数与 `overlapPairs` 相交元素对；`run-reference-audit.sh` 判定与输出同步加 overlap。判别 D2：向 states 页注入两个相交徽标 → `overlap=1` 且输出 `badge[⚠ OV-A] × badge[✓ OV-B] (37x12px)` | [discriminate-r001-r004.sh](../../verification/TASK-059/discriminate-r001-r004.sh)；audit-result.txt 50 行均含 `overlap=0` |
| R-005（audit-result.txt 无 shell 头/EXIT，Handoff 声明不实） | **closed**：按 Git Bash 5.2 (msys) + Chrome 153 headless + `TASK-012-py312` venv Python 3.12 口径重跑全量（50 组合 + 41 截图 + 判别脚本）；同一日志内含环境头、命令、全量输出与 `AUDIT_EXIT=0`/`DISCRIM_EXIT=0`；本 Handoff 上表的「含 `EXIT=0` shell 头」已更正并注明 R1 时点不实。标准重跑命令已写入审计脚本头注释 | `verification/TASK-059/audit-result.txt`（R3 重跑版） |
| R-006（R1 计数残留） | **closed**：契约 §1 证据行 → 判别脚本/50 组合（含徽标合成底）/41 截图；§7.2/§9 → 五候选 × 22 对口径；DDR-1 → 注明 R2 由 DDR-8 扩展；§2/§15 徽标口径同步；`run-reference-audit.sh:4` 脚本头 → 5 候选；`export-tokens.py:4,89` → `{a,b,c,d,e}` 与「非 C 候选不启用玻璃」；D/E JSON note 经重导自动修正；Task AC④/AC⑥ 与测试要求表同步 | 契约 R3 版；Task（R3 版）；grep 复核无「30 组合/26 张/3 候选」残留于现行口径句 |

R3 判别力证据（Q-009，同日志入库）：D1 回退 A 亮色 warn 旧令牌 → `badge-warn/st-warn-t=4.22` FAIL（与复审复算一致）；D2 注入相交徽标 → `overlap=1` 检出。`DISCRIM_EXIT=0`。

## R4 交付：组合候选 F · Graphite Atelier（2026-09-19，用户 ND-1 裁决之后）

**背景**：Review [TASK-059-07397ac](../reviews/TASK-059-07397ac.md)（分支 `agent/codex/TASK-059-review` @ `9d3b0f2`）对 R3 复审 **`approved`**，附唯一非阻塞 P2 **R3-001**（22 对审计未覆盖直接使用 `--st-skip` 的状态文本；B 亮色选中行合成底上独立复算约 4.17:1，open 移交后续）。随后用户作出 **ND-1 裁决**：配色/状态色/亮暗主题/视觉语言＝**A · Graphite**；字号/控件高/行高/间距/面板尺寸等几何比例＝**B · Atelier**；IA＝**A**（不继承 B 章节大卡）；不启用 C 玻璃、D 顶栏、E 命令面板。按契约 ND-1「组合稿必须重新做一致性审计，不能把 A/B 两份候选拼成实现规范」条款，交付组合候选 **F · Graphite Atelier**；候选总数 5→6（DDR-9），A–E 保留为候选档案。

**六项交付**：

| # | 交付 | 结果 |
|---|---|---|
| ① | `ui-reference.html` 新增候选 F | 几何块逐项取 B 的 20 项密度令牌；色板逐**字面值**取 A（dark/light 两块完整复制）；书架 `--card-w` 取 A 档（IA 继承 A，不取 B 章节大卡）；无任何 C/D/E 覆写（玻璃/顶栏/命令面板规则均绑定原候选选择器，不波及 F）；切换按钮 `F · Graphite Atelier` |
| ② | `doc/design/tokens-cand-f.json` | `export-tokens.py` 生成（CAND_NAMES 与循环扩到 `abcdef`）；python 断言 `f['modes']==a['modes']` 且 `f['geometry']==b['geometry']` → **OK**；`glass.enabled=false`；name 注明「ND-1 组合稿：A 色彩 + B 几何，IA 继承 A」 |
| ③ | 契约更新 | §头部 R4 版本行、§1 证据行、§2、§3 改六候选总览（F 列）、新增 **§6C**（F 构成规则 + R3-001 审计口径）、§7.2（60 组合/24 对 + 扩展对记录）、§7.3、§8.1/§8.2、§9、§10、§11（F 切片映射：S-TOKEN 灌 f JSON + A 形态切片；不涉及 L2/GLASS/TOPNAV/CMDPALETTE/TABLE）、§13（ND-1 标已裁决；ND-2/3/8/9/10 对 F 不适用；ND-4/5/6/7 仍待决）、§14 DDR-9、§15 证据索引重写 |
| ④ | **R3-001 disposition＝closed（本轮闭合）** | `tokenPairs()` 仅对 F 追加 2 对：`st-skip-direct/panel`（`--st-skip` 直接文本 × panel，前景用真 `--st-skip` 而非 Review 指出的 `--ink-2`）与 `ink/selected-row`（`.sel` 行底 `accent-soft` 叠 panel 合成 × `--ink`，覆盖 Review 指出的选中行上下文），阈值 4.5:1；实测 **7.22 / 11.34 PASS**（A 色板下无 B 的 4.17 风险）；A–E 维持 22 对既有证据口径不变。Review 原建议「随所选实现切片补齐」，因 F 即 ND-1 已选方向且缺口属审计覆盖而非实现缺陷，在组合稿审计口径中直接闭合 |
| ⑤ | 全量审计重跑 | **60 组合（6 候选 × 2 主题 × 5 视图）ALL PASS**——F 每组合 `contrast=24/24 outside=0 clipped=0 overlap=0`；环境头/命令/`AUDIT_EXIT=0` 同日志入库；截图 41→**49** 张（+8 F：`f-dark-{bookshelf,workbench,reader,settings,states}`、`f-light-workbench`、`f-dark-workbench-dpi150`、`f-dark-workbench-taskdetail`） |
| ⑥ | 判别力扩展 | **D1/D2/D3 全 FAIL（预期方向）**，`DISCRIM_EXIT=0`；新增 **D3**＝把 F/A 暗色 `--st-skip` 全局回退为 `#6b6b76` 后跑 `cand=f` 审计 → `st-skip-direct/panel=3.01` FAIL，证明新扩展对非恒 PASS |

**F 抽验目检**：`f-dark-workbench.png` / `f-light-workbench.png`＝石墨底 + indigo 强调（A 色板）× 36px 控件 / 42px 行高（B 几何），徽标、选中行、进度条均正常，无叠盖、无截断异常。

**改动范围**：仍仅 `doc/**`（契约/参考 HTML/tokens-f JSON/Task/Handoff/STATUS 台账行）+ `verification/TASK-059/**`（审计与判别脚本、日志、49 截图）；`src/**`、`tests/**`、Schema、依赖、D01～D08、ui-baseline 零改动；未 push。

**Reviewer（Codex）复审建议**：① 核对 R3-001 闭合是否成立（两对扩展的定义与实测值、D3 判别）；② 核对 F 构成规则（`tokens-cand-f.json` 与 A/B JSON 的断言可独立复算）；③ `git diff 07397ac..HEAD -- doc/contracts/` 对照 §6C/§15。复审通过后本 Task 可进入集成（候选裁决已由 ND-1 完成，ND-4/5/6/7 仍待用户，其中 ND-6 为 F 实现前待决）。
