---
task_id: TASK-059
author: ZCode
recipient: Codex（Reviewer，非作者）
base_commit: 4c81dca6186f9b47f2771e5033a5d6ecfa986dd6
delivery_head: 5578a01（R1 参考+证据） / ddaf865（R1 契约） / dd455c0（R2 参考+证据） / af91e06（R2 契约）
status: in_review
---

# Handoff：TASK-059（三候选设计交付）

> **R2 修订（2026-09-19，交付后追加）**：用户在本 Handoff 提交后指示「再增加两种完全不一样的设计」。R2 已交付候选 **D · Vermilion 朱砂**（一级导航 rail→顶部导航条 + 编辑部印刷网格；导航范式变化，ND-8）与 **E · Amber 琥珀**（全 UI 等宽 + 书架表格化 + Ctrl+K 命令面板；新交互机制 ND-9、26px 触达显式例外 ND-10）。契约以 R2 为准（§6A/§6B、DDR-8）；候选总数 3→5，**AC② 的「2–3 个」由用户指示扩展为 5**，Task 文件已记录该口径变更。证据矩阵 30→50 组合（ALL PASS，`EXIT=0`）、截图 26→41 张。R2 提交：`dd455c0`（参考+证据）、`af91e06`（契约）。以下正文为 R1 内容，R1 的 AC 对照对 D/E 同样成立（对照关系见文末 R2 补充表）。

## 交付结果

按开工指令交付 **3 个在视觉语言或 IA 上实质不同的候选方向**（不是同一方案的三种密度），全部落在允许修改路径内；未触碰任何禁止路径（`src/**`、`tests/**`、Schema、D01～D08、ui-baseline 等零改动，`git diff --check` 退出码 0）。

**提交列表（base `4c81dca` 之后，分支 `agent/zcode/TASK-059-ui-redesign`）**：

| commit | 内容 |
|---|---|
| `5578a01` | `doc/design/ui-reference.html`（离线视觉参考，单文件）、`doc/design/tokens-cand-{a,b,c}.json`（机器可读令牌）、`verification/TASK-059/**`（审计脚本、审计结果、26 截图、令牌导出脚本） |
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
| 参考可加载（JS 语法门） | `node -e "new Function(script)"`（`run-reference-audit.sh` 第 1 段） | 无头 Chrome + Node，worktree @ `5578a01` | **PASS**（syntax OK） | `verification/TASK-059/audit-result.txt`（含 `EXIT=0` shell 头） |
| 对比度+溢出审计 | `bash verification/TASK-059/run-reference-audit.sh`（30 组合：3 候选 × 2 主题 × 5 视图 × 15 令牌对） | 同上 | **PASS**（30/30 PASS，contrast 15/15、outside=0、clipped=0） | 同上 |
| 无头截图 | 同脚本第 3 段（26 张：15 默认 + 3 第二主题 + 4 玻璃对照 + 2 DPI + 2 工具窗） | 同上 | **PASS**（26/26 生成，关键张人工目检） | `verification/TASK-059/screenshots/*.png` |
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
