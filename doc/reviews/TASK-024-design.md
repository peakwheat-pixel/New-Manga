---
task_id: TASK-024
reviewer: ZCode 子 agent（2026-09-16 全权窗口授权，同体审查；期满补外部 post-hoc 复审）
author: ZCode
base_commit: 116e682
reviewed_head: d840075
decision: approved_subagent
---

# Review：TASK-024（扩展能力及验收覆盖边界，仅设计）

Reviewer 为作者（ZCode）派生的同体子 agent。依 [STATUS](../../STATUS.md)「ZCode 全权窗口授权（2026-09-16）」条款（T0=2026-09-16 23:30 ～ T1=2026-09-17 08:30 Asia/Shanghai，窗口目标 TASK-015/024/017），本结论登记为 `approved_subagent`，**不等同协作协议 §1 的跨 Agent 独立批准**；窗口期满后须由外部 Reviewer（frontmatter 登记为 DeepSeek Harness）补 post-hoc 复审。审查仅针对固定 `reviewed_head=d840075`，diff 范围 `116e682..d840075`。

## 审查背景与窗口定性

- TASK-024 为 kind=design：交付物是设计文档与追踪表事实性回写，不含生产代码；验证以引用完整性、范围边界与一致性为主，不涉及产品行为验收。
- 本次审查为同体审查：作者与 Reviewer 同属 ZCode。窗口条款明确子 agent Review 结论只登记 `approved_subagent`，本报告遵循该定性，不写 `approved`。
- 本 Review 是任务 AC4（非作者独立 Review / 窗口子 agent Review）的执行环节；AC4 本身仍为未勾选，需集成验证后才能 done。

## 范围与依据

- 需求/AC：[doc/tasks/TASK-024.md](../tasks/TASK-024.md) 四条 AC、允许修改白名单、禁止范围、测试要求。
- diff：`git diff 116e682..d840075`，共 5 文件（13_ACCEPTANCE_TRACEABILITY.md、contracts/extensions.md、handoffs/TASK-024-design-boundaries.md、tasks/TASK-024.md、verification/TASK-024/author-verification.md），经 `--name-status` 独立复核全部落在白名单内，无白名单外文件，无 STATUS/其他 Task/源码/测试改动。
- 引用核查：对设计声称的来源逐条 grep 原文并核对章节归属，抽查覆盖（超出最低 6 条要求）：
  1. D01 §2 补充扩展能力行（01_FUNCTIONAL_ARCHITECTURE.md L164，§2=L141-170）——网页导入/PDF-MOBI/AI 插件 Agent/字体上传/Sakura 五条目逐一存在；
  2. D02 §12（02_TECHNICAL_ARCHITECTURE_.md L933-956）：扩展点六组 before/after detect→export、原则清单、原文"Plugin Agent 如保留，只负责生成/管理插件，不进入漫画翻译主链路"（L952）逐字一致；
  3. D02 §6.2（L629 网络代理与统一网络访问）及 §6.2.2（L669 Firecrawl/gallery-dl、L677 本地 Sakura）、§6.2.3 Provider 级覆盖、§6.2.5 连接测试——§0.2 总边界成立；
  4. D02 §3 四个一级页面（L226-229）；D02 §11 设备与模型管理（L917）；D02 §2/§6 Sakura 为翻译 Provider（L27/L485）；D02 §13 运行时拓扑统一网络口径（L956 起）；
  5. D03 §47 明确不建立的实体（L2656-2676：User/Account/Role/Permission、Volume、Character Studio、Manga Insight/Vector Store/RAG、Permanent Webtoon Tile）；D03 ProviderProfile 枚举含 `Sakura-本地`（L1631 起 §25，L1639）；
  6. D04 §8 首节点"选择本地图片 / 文件夹 / PDF / MOBI"（L327）；D04 §54 明确不引入的用户流程（L1939-1952）；
  7. D05 §43 设置页 12 固定二级分类含 Plugin/Hooks（L1431-1456）；D05 §47 Network Connection Test Window（L1551）；D05 §48 字体"Source Han Sans K Bold/字体选择"（L1588/L1601）；D05 §52 Import Window 支持图片/文件夹/PDF/MOBI（L1713-1733）；
  8. D07 §71 文件安全边界（L1813）；§72 Plugin/Hook 稳定性"不得让 Core Domain / SQLite 损坏""Plugin Error→当前扩展失败→应用仍可运行"（L1833-1851）；§80 版本兼容（L2032）；§83 可选依赖（L2100）；§84 Model Download"不得注册为 Ready"（L2121-2143）；§88 远程 Provider 数据提示（L2209）；
  9. G17（doc/10_CURRENT_STATE_AND_GAPS.md L99：D01 扩展覆盖不完整、建追踪表与范围决定）；
  10. ACG-EXT-SAKURA 原文"Sakura服务监控、模型/设备就绪状态"（13_ACCEPTANCE_TRACEABILITY.md L247，base 侧同样存在）——§1.6"健康探测+就绪状态"裁定与其匹配；
  11. 设计引用的实现 seam `src/infrastructure/rendering/font_catalog.py`、`src/infrastructure/network/diagnostics.py` 均实际存在。
- 未审到的部分：gallery-dl/Firecrawl/mobi/pdfium/PyMuPDF 等外部依赖的许可与维护状态属设计自行声明的"未知契约"，其表述准确性不在本次核查范围；未验证 worktree 之外的分支状态；无产品行为可执行验证（设计任务）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | doc/contracts/extensions.md L119；doc/handoffs/TASK-024-design-boundaries.md L16；verification/TASK-024/author-verification.md L15/L35 | §3 与 handoff、verification 三处声称"11 条 AC 草案"，实际 §1 定义 15 条（IMPORT-001~004、PLUGIN-001~003、AGENT-001~002、FONT-001~003、SAKURA-001~003）。若用户按"11 条"字面批准 §3 回写，D08 新增 §44 将漏收 4 条，制造新的追溯缺口；V1 断言同名"AC 草案 11 条"仅覆盖 13 个编号，漏检 SAKURA-002/003 | `grep -o "AC-EXT-[A-Z]*-[0-9]*" doc/contracts/extensions.md \| sort -u` 输出 15 个编号；V1 脚本源码 L35 断言列表无 SAKURA-002/003 | 将三处"11 条"更正为"15 条"，V1 断言补全 SAKURA-002/003；属事实性更正，不涉及需求裁决，可随集成元数据提交一并修订 | open |
| R-002 | P2 | doc/contracts/extensions.md L100 | §1.6 已有要求行引用"D03 §17.3 Provider Profile 枚举含 Sakura-本地"，但 D03 §17.3 实为"Revision 保留策略"（03_DATA_MODEL.md L1136）；`Sakura-本地` 枚举实际位于 D03 §25 ProviderProfile（L1631/L1639）。内容真实存在，仅章节号错，损害本 Task 核心 AC（逐项标明已有要求）的可核查性 | `grep -n "^## 25\." doc/03_DATA_MODEL.md` → L1631；`grep -n "Sakura-本地" doc/03_DATA_MODEL.md` → L1639；`sed -n '1136p'` → "### 17.3 Revision 保留策略" | L100 的"D03 §17.3"更正为"D03 §25"；属事实性更正 | open |
| R-003 | P2 | doc/13_ACCEPTANCE_TRACEABILITY.md L247 | ACG-EXT-SAKURA 行"后续处理"写"TASK-024已裁定健康探测级范围"，而 extensions.md 自身定性为"草案，待用户批准"（§1.6 裁定列于支持矩阵草案，U-6 待决）。"已裁定"措辞略强于实际状态，虽同句已写明"待用户批准（U-6）"，仍建议弱化以免被误读为已完成需求裁决 | 对照 extensions.md L3"草案，待用户批准"与 L102"支持矩阵（草案）…范围裁定为健康探测+就绪状态" | 改为"TASK-024已定义草案边界（健康探测级建议）"，与 IMPORT/PLUGIN/FONT 行"已定义边界"句式对齐 | open |
| R-004 | P2 | doc/contracts/extensions.md L102 | §1.6 支持矩阵草案写"工作台 Provider 选择器显示 就绪/不可用/未知 三态"，但 D05 工作台既有职责（L75：翻译、OCR、Region 编辑、修复、渲染、任务进度）及工作台固定区域/悬浮窗描述中无"Provider 选择器"既有条目。设计未将其冒充为已有要求（已有要求行未引 D05 工作台），属待批准的草案 UI 建议，但落点需核对 | `grep -n "Provider 选择\|工作台" doc/05_UI_MAPPING.md` 无工作台 Provider 选择器既有映射 | 在 §1.6 注明"工作台三态指示的具体落点（Provider 选择器或设置页）待 TASK-019 释放前与 D05 核对"，避免实现 Task 误以为入口已定 | open |
| R-005 | P2 | doc/13_ACCEPTANCE_TRACEABILITY.md L249 | ACG-EXT-CONTRACT 行仍写"精确AC待TASK-003/024补齐"，本次设计交付未覆盖该组（状态/复合写回/Pin/TM/Review/SFX，来源 D03/D06+G06~G13，不属本 Task AC 列举的五组条目），该遗留指向未被更新或澄清。不违反本 Task AC，但批准回写时若不同步处理，追踪表将留下过时指向 | 对照 TASK-024.md AC 条目清单（仅五组扩展条目）与 L249 行原文 | 在 §3 批准后回写时一并澄清该行指向（改指 D03 契约冻结或后续 Task），或在 §3 表中显式声明 CONTRACT 组不在本设计范围 | open |

没有发现 P0/P1 问题；上述 5 条均为 P2 事实性/措辞级修订，不阻断。R-001/R-002 建议在集成元数据提交中随本 Review 登记一并更正。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| V1 引用核对脚本复跑 | 作者脚本原样：`PYTHONPATH=src "G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe" - <<'PY' … PY`（12 项断言） | Git Bash，CWD=`G:/CODEX/New Manga.worktrees/TASK-024-zcode`，HEAD=d840075 | PASS：退出码 0，输出 `all reference checks passed: 12` | 本报告验证记录；与 author-verification.md V1 声称一致 |
| V1 断言覆盖复核 | 人工比对断言编号与 §1 实际 AC 编号 | 同上 | 发现缺口：SAKURA-002/003 未在断言内 → R-001 | Findings R-001 |
| V2 白名单复核 | `git diff --name-status 116e682..HEAD` | 同上 | PASS：5 文件均在白名单（13 追踪表、contracts/extensions.md、handoffs/TASK-024-*.md、tasks/TASK-024.md、verification/TASK-024/**），无越界改动 | 本报告"范围与依据" |
| V3 全仓测试复跑 | `PYTHONPATH=src "G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe" -m pytest tests -q` | 同上（task-env TASK-014-py312） | PASS：`536 passed in 23.41s`，与作者声称 `536 passed, 0 skipped` 一致 | 本报告验证记录 |
| 引用真实性抽查 | 对 D01/D02/D03/D04/D05/D07/G17/ACG-EXT 行逐条 grep+sed 核对原文与章节归属（11 组，见"范围与依据"） | 同上 | PASS（含 1 处章节号错误 R-002、1 处弱来源 R-004，均已立 finding） | 本报告"范围与依据"第 1-11 条 |
| 自我批准边界核查 | 通读 extensions.md §3/§4 与追踪表 diff；核对 STATUS 及 TASK-023/025/019/022 frontmatter | 同上 | PASS：§3 全部标注"待用户批准后执行"，§4 U-1~U-6 完整交用户；追踪表仅改"后续处理"列（事实性指向），"已有来源/内容"列未动；D08/D01/D02/D12-Roadmap 未被修改；四个下游 Task 仍 proposed/pending_user_review，未被解冻 | Findings R-003/R-005 为措辞级残留 |

## 三轴结论

- **Spec（需求覆盖）**：AC1 满足——§1.1~1.6 每条目均有"已有要求/未知契约"两行，五组条目（网页、PDF/MOBI、Plugin/Hooks、AI Plugin Agent、字体上传、Sakura）全覆盖（唯 R-002 章节号错误）。AC2 满足——各条目支持矩阵/入口/授权失败边界/AC 草案齐备；§1.4 对 Plugin Agent 同时给出四项保留条件与不保留判据，裁决权交 U-4，未默认删掉也未默认扩建；§2 排除项均有来源且明确"非删除"。AC3 满足（窗口口径）——§4 U-1~U-6 与 §3 回写计划构成用户审批入口；"更新权威文档"部分被有意置为 NOT_RUN（待批准后回写），作者已在 AC 证据注记与 verification NOT_RUN 表中透明登记，设计不自我批准的立场正确。AC4 未完成（进行中），本 Review 即其环节，诚实勾选。两条红线均守住：未引入新一级页面（§0.1 与 D02 §3/D05 L15 一致）、无产品团队权限系统、全部条目可追溯到 D01 §2 补充扩展能力行。
- **Architecture（架构一致性）**：§0 总边界与 D02 §3/§6.2/§12、D07 §71/§72/§83 一致；网络统一走 Network/Proxy Manager 与 D02 §13 口径一致；Plugin/Hook 权限"声明缺失=不加载"与 Agent 产物"不自动加载、逐个手动启用"均为 fail-closed；Sakura"健康探测+就绪状态"与 ACG-EXT-SAKURA 原文"模型/设备就绪状态"匹配，且显式排除无来源的深度指标；设计入口均在既有 12 固定分类/Import Window/既有面板内，不触碰 `tests/ui_shell/test_qml_shell.py::test_settings_page_lists_twelve_fixed_categories` 约束；未解冻任何冻结 Task（diff 未触碰 STATUS 或下游 Task 文件）。
- **Verification（验证充分性）**：V1/V3 均实际复跑通过且与作者声称一致；V2 独立复核通过；NOT_RUN 清单（权威文档回写、产品级 AC、真实 Sakura 探测）登记诚实且理由成立。V1 脚本存在 R-001 所述断言缺口与一处方向性断言（"D03 §47 排除项引用"断言的是设计文档自身含该句而非 D03 原文，D03 §47 原文已由本 Review 人工核实存在），不构成关键验证缺失。

## 结论与复审

结论：`approved_subagent`（窗口内同体审查）。reviewed_head=`d840075` 的设计交付可交授权集成者（ZCode 代行）进入集成收口：5 条 P2 findings 不阻断，其中 R-001/R-002 属事实性更正，建议随集成元数据提交一并修订；R-003/R-004/R-005 可在用户批准后的回写提交中处理或由 Codex 裁定 deferred。本结论不等同跨 Agent 独立批准；按 STATUS 窗口条款，窗口期满后必须由外部 Reviewer（DeepSeek Harness）对本设计及本报告做 post-hoc 复审，U-1~U-6 的产品裁决权完整保留于用户。剩余风险：若用户对 U-2/U-4 作出不同于 §1 建议的决定，extensions.md 对应小节须修订后下游 Task 才能释放（handoff 已声明）；ACG-EXT-CONTRACT 的遗留指向（R-005）需在回写阶段显式澄清。


---

## Findings 处置记录（作者处置，head=修订提交）

| ID | 处置 | 说明 |
|---|---|---|
| R-001 | fixed | "11 条"更正为 15 条（IMPORT 4 + PLUGIN 3 + AGENT 2 + FONT 3 + SAKURA 3），§3/handoff/verification 三处同步；V1 断言扩为 15 条全查 |
| R-002 | fixed | D03 §17.3 → §25（Sakura-本地 枚举实际位置），V1 增加存在性断言 |
| R-003 | fixed | 追踪表措辞改为"已定义草案边界（健康探测级）"，与设计"草案待批准"定性一致 |
| R-004 | fixed | 工作台三态标注为草案落点，TASK-019 释放前核对，不得据此改一级页面结构 |
| R-005 | deferred | ACG-EXT-CONTRACT 行属 TASK-003/024 联合补齐项，不属本 Task 四条 AC 列举范围；留待用户批准回写时一并澄清 |

处置为作者自查（P2 级，机械修正）；decision 维持 approved_subagent，期满补外部 post-hoc 复审。
