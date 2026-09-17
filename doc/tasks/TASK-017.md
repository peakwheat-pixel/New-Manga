---
id: TASK-017
title: Translation 与上下文输出协议实验
kind: experiment
status: done
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-003, TASK-004]
base_commit: 348a48e
branch: agent/zcode/TASK-017-translation-protocol-experiment
worktree: G:/CODEX/New Manga.worktrees/TASK-017-zcode
integration_commit: d36f724
---

# TASK-017：Translation 与上下文输出协议实验

本 Task 由 2026-09-16 ZCode 全权窗口授权解冻（条款见 [STATUS](../STATUS.md)）：窗口内由 ZCode 实施、ZCode 子 agent Review（结论登记 `approved_subagent`）、ZCode 代行集成；期满后补外部 post-hoc 复审。`reviewer` 栏 DeepSeek Harness 为期满补审与后续协作的外部 Reviewer。窗口 base 取解冻时 master HEAD=`348a48e`。实验不修改正式术语/TM或真实用户数据；不自行配置付费 Provider——真实端点未配置时按 AC 只报告已测层（mock 协议层）。

## 来源与目标

D01 §5；D06 §10～18/54～57/84；D08 AC-TRANS/CONSTRAINT/TM/FALLBACK。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 以已有设计中的OpenAI-compatible/本地Sakura候选检验文本与RegionID输出协议，记录具体可用Provider/模型版本。（mock 层完成协议检验；真实 Provider/模型版本 NOT_RUN——付费端点未配置且禁止自行配置）
- [x] 对术语一致性、上下文排序、预算截断、缺失/重复/越界ID、畸形响应建立可复现样本和质量评估。（samples.py + 15 例 pytest + results.json S1~S8，全部可复现）
- [x] 明确retry/fallback输入不变、网络策略和远程数据范围；结论包含成本/时延实测或未测说明，不声称所有Provider兼容。（验证记录 AC 3：S2/S8 覆盖输入不变与显式 fallback；D06 §55 代理失败策略留给生产网络栈，本实验明确不编码；仅使用样本文本，真实 Provider 成本/时延 NOT_RUN，不声称全 Provider 兼容）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review（或 2026-09-16 窗口期内用户授权的子 agent Review，登记为 approved_subagent）与授权集成者集成验证后才能 done；窗口期交付须在期满后补外部 post-hoc 复审。（窗口内 Review `approved_subagent`；集成 `c0cf3a1`；DSH post-hoc Review `fb0bc40` approved，R-101 已关闭）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- experiments/TASK-017/**
- doc/research/TASK-017.md
- doc/tasks/TASK-017.md
- doc/handoffs/TASK-017-*.md
- verification/TASK-017/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 实际命令与本地mock协议测试；真实端点未配置则只报告已测层。
- 日/韩文本、多页上下文和单目标写回校验；人工评分规则可复现。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

实验不修改正式术语/TM或真实用户数据；不自行配置付费Provider。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-017-protocol-experiment](../handoffs/TASK-017-protocol-experiment.md)。
- Review：窗口内子 agent Review（见 doc/reviews/TASK-017-*.md）。
- 实际执行/实验/测试：[verification/TASK-017/author-verification.md](../../verification/TASK-017/author-verification.md)。
- 最近状态：2026-09-17 窗口授权收口 `done`：实验 `6a330e1`、Review 登记 `adb2093`、处置 `ae74250`（`doc/reviews/TASK-017-protocol.md`，approved_subagent）、integration=`c0cf3a1`，master 复验全仓 `536 passed` + 实验 `15 passed`；真实端点层 NOT_RUN（付费端点未配置且禁止自行配置），恢复方法见 research §4；reading_export QML 低频 flaky 已登记移交跟踪。
- post-hoc Review：DeepSeek Harness 报告 commit `fb0bc40`（reviewed_head=`ae74250a`，approved）；R-101 已关闭，验证记录见 [author-verification.md](../../verification/TASK-017/author-verification.md)。

## 尾项修订切片（2026-09-17，Review R-001 / R-002 / R-003）

**当前状态以顶部 frontmatter 的 `status` 为准（现为 `in_review`）**，本节之前的表述保留为其发生时的历史记录。**已集成主体 `c0cf3a1` 与 post-hoc Review `fb0bc40` 不因本切片失效。**

- 作者=Codex、Reviewer=DeepSeek Harness（**非作者**）；base=`754eb4f`（master）、交付 head=`971efe6`；Handoff 见 [TASK-017-971efe6.md](../handoffs/TASK-017-971efe6.md)，取证见 [verification/TASK-017/revision-971efe6.md](../../verification/TASK-017/revision-971efe6.md)。
- 动因：`doc/reviews/TASK-017-protocol.md` 把 R-001/R-002/R-003 登记为 **open（"移交生产实现 Task"）**，而研究报告 §4 要求"生产 Translate Step 引用 `protocol.py` 分类器前必须先吸收"，TASK-019（未释放）将直接消费该分类器。
- 修正：R-001 非字符串 `region_id`/`translated_text` 不再崩溃或静默 `str()` 成 `"None"`；R-002 429 独立为 `http_429` 并纳入 `RETRYABLE`、其余 4xx 显式声明不可重试；R-003 引入 `reading_order`（D06 §13）并显式声明"最近优先保留连续段"的截断策略。
- 验证（作者）：`test_protocol.py` **20 passed / 0 skipped**（15 → 20）；`test_run_experiment_cli.py` **1 passed**；`run_experiment.py` 退出码 0 且 `results.json` 与提交版本逐字段一致（仅 `latency_ms` 为测量值）；**判别力**：新增 5 例在修复前代码上全部 FAILED。
- **独立 Review（2026-09-17）**：DeepSeek Harness 在独立 linked worktree（分支 `agent/deepseek/TASK-017-tail-review`）完成，报告 commit `e50ba29` → [`doc/reviews/TASK-017-971efe6.md`](../reviews/TASK-017-971efe6.md)，结论 **`approved`**（P0=0/P1=0/P2=0，P3×1 观察 R-101 不阻塞）。Reviewer 独立复现了判别力（修复后测试 × 修复前代码 = 5 failed / 15 passed）。
- **集成（2026-09-17，Codex）**：`integration_commit=d36f724`（merge，3 parents：`754eb4f` + 作者 `387bb1e` + 评审 `e50ba29`）。集成后复验见 [verification/TASK-017/integration-d36f724.md](../../verification/TASK-017/integration-d36f724.md)：`test_protocol.py` **20 passed / 0 skipped**、`test_run_experiment_cli.py` **1 passed**、全仓 **530 passed / 6 skipped**（6 项均 `openssl unavailable`）；`results.json` 未被改写。
- **Findings 关闭**：R-001 / R-002 / R-003 **closed**（`971efe6` + 回归测试，Reviewer 复核成立）；**R-101 closed**（`experiments/TASK-017/README.md` 注明 `latency_ms` 为易变字段、比对应排除，并列出可指纹化的确定性字段；未改动 `results.json`）。
- 未完成项不变、**不得视为通过**：真实 Provider / 真实 Sakura / 真实模型质量评分仍 **NOT_RUN**（未配置付费端点、本机无 Sakura 服务；禁止自行配置）。
