---
task_id: TASK-017
reviewer: ZCode 子 agent（窗口授权 2026-09-16）
author: ZCode
base_commit: 348a48e
reviewed_head: 6a330e1
decision: approved_subagent
---

# Review：TASK-017（Translation 与上下文输出协议实验）

> Reviewer 不能是变更作者。decision 为 pending / changes_requested / approved / blocked；只有对该 reviewed_head 的实际审查才有效。本 Review 属同体（ZCode 实施、ZCode 子 agent Review），按 2026-09-16 用户全权窗口授权条款执行，结论只能登记 `approved_subagent`（不写 `approved`），期满后必须补外部 post-hoc 复审（DeepSeek Harness，见任务文件 reviewer 栏）。因此本结论的独立性弱于常规非同体 Review，此定性为结论的一部分，不是免责套话。

## 范围与依据

- 对象：`git diff 348a48e..6a330e1`（11 个文件，全部新增/修改于白名单：`experiments/TASK-017/**`、`doc/research/TASK-017.md`、`doc/tasks/TASK-017.md`、`doc/handoffs/TASK-017-protocol-experiment.md`、`verification/TASK-017/**`）。未触及生产 `src/`、`tests/`、依赖清单、AGENTS、其他 Task 文档。
- 依据：[TASK-017](../tasks/TASK-017.md) 四条 AC 与允许/禁止范围；D06 §13/§16/§18.1-18.2（Translate Step 输入/输出、Context Builder 职责、token budget 算法目标）、§54（默认不自动跨 Provider fallback）、§56.1/§56.2（retry 分类）、§57（retry 相同输入）、§84（Context Group 输出映射回 Page ID/Region ID）原文抽查；D08 AC-TRANS/FALLBACK 口径。
- 审查方法：全文读 protocol.py / mock_provider.py / samples.py / test_protocol.py / run_experiment.py / results.json 与四份文档；对照 D06 原文逐条核对；边界行为用一次性脚本实际验证（非字符串 region_id、429 分类），未在仓库落地任何脚本文件。
- 未审到的部分：真实 Provider/模型行为（NOT_RUN，见下）；PySide6 生产运行时交互（本任务不涉及）；D08 全文逐条（按任务文件引用的 AC-TRANS/FALLBACK 口径抽查）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | experiments/TASK-017/protocol.py:203-208 | 当请求 Region 全部命中且响应含**非字符串**额外 `region_id`（int、list 等）时，EXTRA_IDS 分支的 `', '.join(extra)` 抛未分类 `TypeError`，校验器崩溃而非返回结构化报告；report.translations 无法取回部分结果。实际验证：expected=('r-1',) 响应含 r-1 + int 123 → `TypeError: sequence item 0: expected str instance, int found`。 | Reviewer 复现（一次性脚本，`validate_response` 对 `{r-1, 123}` 返回异常） | 生产 Translate Step 采用该分类器前，先对 `rid` 做类型归一（非 str 视为 extra 并以 `repr` 进 detail）；可顺带覆盖 `translated_text=null` 被静默转成 `"None"` 的口径 | open（移交生产实现 Task） |
| R-002 | P2 | experiments/TASK-017/mock_provider.py:206；protocol.py:126-139 | D06 §56.1 点名 `ProviderRateLimitError` 可重试，但 `ProtocolClient` 将非 401 的 4xx 归为 `http_4xx`，该 kind 不在 RETRYABLE 也不在 NOT_RETRYABLE → `report.retryable=False`，**429 会被判不可重试**，与 §56.1 冲突。mock 未注入 429、测试未覆盖，故本实验结论未受影响；但 research 报告建议"直接采用 retryable 集合"，若照单全收将带入此偏差。 | Reviewer 验证：`'429' not in ProtocolClient.complete` 源码；`'http_4xx' in RETRYABLE == False` | 集合显式补 `http_429`/RateLimit；`http_4xx` 落入哪个集合也要显式声明而非依赖 `in RETRYABLE` 的默认 False | open（移交生产实现 Task） |
| R-003 | P2 | experiments/TASK-017/protocol.py:95,103-107 | `build_request` docstring 声称"最远的上下文页先被丢弃"，实现实为"逐页试探加入、加入后超预算的那页被丢"的贪心——远端小页可能保留而近端大页被丢；且排序键是 `page_id` 字符串序，不是 D06 §13 的 `reading_order`。当前样本仅 2 页（page-0/page-2），两种语义结果一致，测试未暴露差异。 | 代码走读；`sorted(..., key=(position, page_id))` | 生产实现按 reading_order 排序并明确丢弃策略（远端优先或性价比优先），补一个"近端大页 vs 远端小页"的对抗样本 | open（移交生产实现 Task） |
| R-004 | P2 | verification/TASK-017/author-verification.md:30-31 | AC3 对照行声称"D06 §55 代理失败不自动 Direct 的分类规则已编码（NOT_RETRYABLE/RETRYABLE 集合）"——实验代码中不存在任何 proxy 相关分类（无 ProxyFailure / allow_proxy_failure_direct_fallback 概念），该表述超出实际编码范围，属验证记录的过度声明。 | 代码检索无 proxy 项；protocol.py RETRYABLE/NOT_RETRYABLE 集合内容 | 将该句改为"§55 未编码，代理失败分类留待生产实现"；一词之改，作者或 Codex 集成时顺手处理 | open |
| R-005 | P2 | experiments/TASK-017/protocol.py:212-218 | `glossary_hits` 只检查目标术语是否出现在译文中，不检查源术语残留或误用他词；对 mock 规则翻译（构造上保证 target 出现）恒为全命中，术语一致性断言在 mock 层是弱断言。research 报告已声明不声称模型质量，诚实性无问题，仅记录方法局限。 | 代码走读 | 真实端点复跑时补充"源术语残留计数"与负样本（模型未套用术语）用例 | deferred（方法局限，已由作者声明） |
| R-006 | P2 | experiments/TASK-017/run_experiment.py:71-75；test_protocol.py:60-68 | S2 的 `payloads_identical` 用解析后再 `sort_keys` 序列化比较而非 mock 已记录的 `raw_bodies` 字节比较——解析等价已足以证明 §57 输入不变，字节比较会更硬；`test_context_order` 的 `report_ids` helper 名为校验"输出映射回 Region"，实为回显请求 ids，真正的映射证明由 `validate_response` 的 expected-ids 校验承担。两处均不构成错误结论。 | 代码走读 | S2 增加 raw_bodies 字节级比对；helper 改名或删除以免误导 | deferred |
| R-007 | P2 | tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer（仓库既有，非本任务 diff） | Reviewer 复跑全仓 3 次：首跑 1 failed（该用例）+ 535 passed；同内容 master（2727ea3）536 passed；worktree 复跑 536 passed；单跑该用例 passed。判定为既有顺序敏感/偶发失败，与本任务无关（TASK-017 diff 不触碰 src/tests），但说明作者验证记录的"536 passed"在本环境非 100% 稳定。 | 本报告验证表 V3 三行 | 独立于本任务跟踪 flaky（建议登记给 Codex/后续维护 Task） | open（移交 Codex 裁量，非本任务阻塞项） |

除上述条目外，在记录范围内未发现问题。无 P0/P1。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| V1 协议测试套件 | `python -m pytest test_protocol.py -q`（CWD=experiments/TASK-017，解释器 `G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe`） | Python 3.12.3 / pytest 9.1.1 / win32 / 6a330e1 | PASS：**15 passed, 0 skipped，退出码 0**（7.22s），与作者记录一致 | 本 Review 执行记录 |
| V2 实验 S1~S8 | `python run_experiment.py`（同上 CWD） | 同上 | PASS：**退出码 0**；S1~S8 全部 match/ok；S2 `payloads_identical=true`、`payload_hash=7c5c50cd…` 与 research 报告一致；`not_run` 三项在机读结果中。复跑产物与已提交 results.json 逐字段一致（仅 `latency_ms` 实测值 47.0→15.0 属测量值波动），比对后已还原原文件，worktree 保持干净 | 本 Review 执行记录 + 备份比对 |
| V3 全仓回归 | `PYTHONPATH=src python -m pytest tests -q`（CWD=worktree 根，同解释器），共 3 次：worktree 两跑 + master（2727ea3）一跑 | 同上 | **worktree 第 1 次：535 passed + 1 failed（见 R-007，无关 flaky）**；worktree 第 2 次：**536 passed, 0 skipped，退出码 0**；master 基线：536 passed, 退出码 0。作者记录的 536 passed 可复现 | 本 Review 执行记录 |
| V4 范围核对 | `git diff --name-status 348a48e..HEAD` 逐项对照任务白名单 | 348a48e..6a330e1 | PASS：11 个文件全部在允许路径内；无 src/tests/依赖清单/AGENTS/正式术语/TM/真实用户数据/付费端点配置 | diff 输出 |
| V5 边界验证 | 一次性脚本（未落地）：非字符串 region_id 走 `validate_response`；检查 `ProtocolClient` 429 处理与 retryable 集合 | 同上 | R-001 崩溃路径与 R-002 分类缺口均按描述复现 | 本 Review 执行记录 |
| V6 真实 Provider 层 | 未执行（无付费端点，禁止自行配置） | — | NOT_RUN：与作者 NOT_RUN 声明一致，实验未声称该层结论 | results.json `not_run`；research §4 |

## 三轴结论

- **Spec（AC 对照）**：AC1、AC2 在 mock 层达成且可复现（15 例 pytest + S1~S8 机读结果；术语 3/3、上下文序、预算截断不截 Region、缺失/重复/越界/畸形五类分类全部命中）。AC3 的"输入不变、网络策略、远程数据范围、未测说明"均已交付（S2/S8 + NOT_RUN 三项；成本/时延为未测说明，符合 AC 的"实测**或**未测说明"措辞），建议作者勾选该 checkbox。AC4 由本 Review 与后续集成闭环。NOT_RUN 声明诚实：results.json、research §4、verification 三处一致，明确不声称模型质量、真实 Provider 兼容性——**通过（窗口范围）**。
- **Architecture（来源对齐）**：§54（默认无自动 fallback、显式 Primary→Secondary）、§57（payload hash + 逐字节记录证明相同输入）、§84（Group 内输出映射回 Page/Region ID，Region 不被预算截断）、§13/§16（Region 全量优先、上下文按 budget 裁剪、truncated provenance）均一致；§18.1 的 TM matches 未显式建模（实验聚焦输出协议，可接受）。偏差为 R-002（429 未入可重试集）与 R-003（截断顺序/排序键与 §13 reading_order 的差异），均为生产落地前必须吸收项，不影响实验结论成立——**通过（含 R-002/R-003 交接注记）**。
- **Verification**：V1/V2 完整独立复现且与作者记录一致；V3 多数复跑 536 passed 全绿，一次无关 flaky 已记录（R-007）；边界验证（V5）发现 R-001/R-002 两个真实缺口，均不推翻 mock 层测试结论，但 research 报告"直接采用分类器/retryable 集合"的建议须附 R-001/R-002/R-003 为前置条件——**通过（含观察项）**。

## 结论与复审

**decision：`approved_subagent`**（同体窗口审查定性，非独立 `approved`；依据 2026-09-16 用户全权窗口授权条款）。

固定 head `6a330e1` 可交 Codex（窗口内由 ZCode 代行）集成。理由：四条 AC 在 mock 层真实达成，测试与实验结果全部独立复现，交付严格限于白名单，NOT_RUN 声明诚实且不越界声称；全部 findings 为 P2，无一阻断实验结论。

剩余风险与移交条件：
1. mock 层结论**不得**外推至真实 Provider 行为、模型翻译质量或跨 Provider 兼容性；真实层待用户提供端点后按同一样本协议复跑。
2. research 报告建议生产 Translate Step 直接采用 `protocol.py` 分类器/retryable 集合——生产实现 Task 必须先吸收 R-001（非字符串 id 崩溃）、R-002（429 可重试分类）、R-003（reading_order 与截断策略），否则不得照搬。
3. R-007（全仓既有 flaky）需 Codex 另行登记跟踪，与本任务集成解耦。
4. 期满后必须补外部 post-hoc 复审（DeepSeek Harness，任务文件 reviewer 栏），复审针对同一 head `6a330e1` 追加记录，不抹掉本报告。

复审：本节为窗口内首次（也是唯一一次）同体 Review；外部 post-hoc 复审追加新记录后本 Task 方可进入 done 流程的终态（集成验证由 Codex 另行记录）。
