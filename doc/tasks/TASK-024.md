---
id: TASK-024
title: 明确扩展能力及验收覆盖边界（仅设计）
kind: design
status: done
approval: approved_by_user
suggested_owner: Codex
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-001, TASK-003]
base_commit: 116e682
branch: agent/zcode/TASK-024-extension-boundaries-design
worktree: G:/CODEX/New Manga.worktrees/TASK-024-zcode
integration_commit: 61c33e2
---

# TASK-024：明确扩展能力及验收覆盖边界（仅设计）

本 Task 由 2026-09-16 ZCode 全权窗口授权解冻（条款见 [STATUS](../STATUS.md)）：窗口内由 ZCode 实施、ZCode 子 agent Review（结论登记 `approved_subagent`，不等同跨 Agent 独立批准）、ZCode 代行集成；期满后补外部 post-hoc 复审。`reviewer` 栏 DeepSeek Harness 为期满补审与后续协作的外部 Reviewer。窗口 base 取解冻时 master HEAD=`116e682`。

## 来源与目标

D01 §2/5；D02 §6.2/11/12；D05 §43；D07 §72/84；G17。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

本 Task 的 4 条 AC 衡量设计交付；扩展契约原有 15 条 AC-EXT-* 草案，其中 IMPORT-001/002 已按 U-1 退役且不复用。其余 13 条中，8 条边界明确的 P2 已纳入 D08 §78 正式编号；AGENT-001/002 依 U-4 延后，FONT-003 删除/回退行为及 SAKURA-002/003 轮询/失败细节仍为草案。两组 AC 属于不同层级，不得合并计数；产品 AC 不计入本 Task 的 4 条设计 AC。

## Acceptance Criteria

- [x] 对网页/PDF/MOBI、Plugin/Hooks、AI Plugin Agent、字体上传、Sakura服务监控逐项标明已有要求与未知契约。（contracts/extensions.md §1.1~1.6 逐项来源/缺口表）
- [x] 提出支持矩阵、入口、授权/失败边界和AC草案，说明D02中Plugin Agent“如保留”的条件，不默认删掉也不默认扩建。（§1 各条目矩阵 + §1.4 四项保留条件与裁剪判据；§2 明确有来源排除项；§4 用户待决清单 U-1~U-6）
- [x] 将产品取舍交用户审核并更新权威文档；为TASK-023/025及019/022涉及的扩展范围明确释放条件。（§3 回写计划与 §4 待决清单已交用户审核；追踪表 ACG 行已指向本设计；需求裁决待用户批准后执行，本设计不自我批准）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review（或 2026-09-16 窗口期内用户授权的子 agent Review，登记为 approved_subagent）与授权集成者集成验证后才能 done；窗口期交付须在期满后补外部 post-hoc 复审。（窗口内子 agent Review `approved_subagent`；集成 `61c33e2`；DSH post-hoc Review `9454cec` approved，R-101～R-103 已关闭；纯文档，不适用测试）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- doc/01_FUNCTIONAL_ARCHITECTURE.md
- doc/02_TECHNICAL_ARCHITECTURE_.md
- doc/05_UI_MAPPING.md
- doc/08_ACCEPTANCE_CRITERIA.md
- doc/contracts/extensions.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/tasks/TASK-024.md
- doc/handoffs/TASK-024-*.md
- verification/TASK-024/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 每个扩展条目有D01/D02来源、用户决定和对应AC或正式延期记录。
- 审核未引入新一级页面、产品团队权限系统或无来源功能。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-001](TASK-001.md)、[TASK-003](TASK-003.md)。依赖必须已经集成 done 才可开始。

本Task只输出设计/决定，不执行插件生成、下载或网站采集。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-024-design-boundaries](../handoffs/TASK-024-design-boundaries.md)。
- Review：窗口内子 agent Review（见 doc/reviews/TASK-024-*.md）。
- 实际执行/实验/测试：[verification/TASK-024/author-verification.md](../../verification/TASK-024/author-verification.md)。
- 最近状态：2026-09-17 窗口授权收口 done：设计 d840075、Review 修订 86072c3（doc/reviews/TASK-024-design.md，approved_subagent）、integration=61c33e2，master 复验 536 passed；用户已裁决 U-1～U-6。后续 AC 整理已将 8 条边界明确的 P2 纳入 D08 §78，5 条保留为草案（AGENT-001/002、FONT-003、SAKURA-002/003）；TASK-023/025/022 继续冻结，TASK-019 仍 blocked 且未释放。
- post-hoc Review：DeepSeek Harness 报告 commit `9454cec`（reviewed_head=`86072c30`，approved）；R-101～R-103 已处置，验证记录见 [author-verification.md](../../verification/TASK-024/author-verification.md)。
- 状态说明：frontmatter `status: done` 由关闭提交 `348a48e`（integration=`61c33e2`）确定；Review 所见 fixed head `86072c30` 的 `ready` 已被后续关闭记录取代，当前保持 `done`。
