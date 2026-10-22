---
task_id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
author: DeepSeek Harness
base_commit: 345c86857f6ea80153ead49271e84ff234a4963f
reviewed_head: ac0bd5a740a0ea9bd89f29d0a5ca25056cda1e42
decision: approved
---

## 结论

**approved**

- `reviewed_head = ac0bd5a740a0ea9bd89f29d0a5ca25056cda1e42`
- `diff_base = 345c86857f6ea80153ead49271e84ff234a4963f`
- `delivery = 88a8a7b0fb78c2ec04d74caca49cf2ce736a94f9`
- canonical main：`b4c1e07d81b121928640d17d1407d99f5a25f2e0`

本 Task 是设计而不是实现；未发现阻断性架构/验证或保护缺口，P0/P1=0。批准仅设计 metadata 与未来实现契约；不批准任何运行例外、原件修改、真实清理、父 Task done、r212 解除或 push。未来实现 Task 仍需 Codex 另冻。

## P0 / P1 / P2

- **P0：0。**
- **P1：0。**
- **P2-1（计数快照口径）**：`validation.json` 的 `counts`/`current_protected_count` 为 `2575/1882`，这是 7 EV 登记前的快照；当前实际为 `2582 declarations / 1889 protected roots / 12 errors / 272 warnings`（7 EV 已计入）。`Task` 已把 1882 描述为 baseline，但 `validation.json` 仍写 `current`，建议改为 snapshot 或注明 EV 前时点。未把 Owner 的 1882 全保护集合比较说成 Reviewer 独立重建。
- **P2-2（适用性边界）**：设计只规定“前序 broad fatal 则不发布”，未明确 broad policy **absent+untracked/no-op** 时是否应继续解释。当前 canonical 有 broad 且为 12，故本设计成立；若未来在无 broad 的 24 错误环境运行，helper 可能仍移除这 5 条、剩 19 条，虽不减少保护但不是 `12→7`。建议实现 Task 明确要求 broad active/当前 12 baseline，或把该场景写为显式 NOT_RUN/拒绝条件。

## Architecture

- 采用“现有 broad 收口之后一个 helper”的最小 seam；无新引擎、无 CLI/env 绕过、无通用 Markdown/NUL 开关。
- schema 精确冻结：顶层六键、`approved_design` 六字段、1 个模板 binding（HIE-T01，R25/R26 两行）、3 个 NUL/C0 原始空 parse binding（HIE-O01/02/03）、2 个 reference guard（HIE-REF01/02）。
- 模板 binding 绑定整文件 rawSHA/byte_length、fence 117..239、draft line115、物理行 228/229、locator line7/8、完整 parser snapshot（1 声明/2 错误/2 warning）；line227 worktree 声明与既有保护必须保持，不允许整文件/围栏忽略。
- 三 NUL 源绑定严格 UTF8、原 NUL/C0 精确 offset、0 声明空 parse snapshot；`read_text` 仍拒绝 NUL，不剥离/不转码/不把空 parse 升级为通用非声明规则。
- P14 两源 `PRESERVE_REFERENCED`，P22 untracked `PRESERVE_UNKNOWN`；P22 作者 unknown，不提交/接管。
- 未来效果为只移除 5 个完整错误、新增 6 Declaration（4 源整文件 + 2 目录）与 4 warning；其余 7 个历史错误、原 1882 保护集合与 line227 保护不减。当前 6 个 guard 根已存在，新增 protected 根为 0。
- 原子发布：全部验证后复制所有 mutable 容器/scanned，暂存注册与 warning，只移 5 个完整错误，最后复读源/策略/设计/facts/real/tracking；失败只在原输入 +1 fatal，无原 index warning 副作用。前序 broad fatal 不发布。
- 明确禁止整文件/围栏忽略、NUL 剥离/转码、全文件排除、生产绕过；P22 与七历史身份/r212 保持。

## Verification

**实际只读执行**

- `validate_design.py` 实际运行 **exit 0**，stdout 为 `DESIGN_DATA_ASSERTIONS_PASSED`；未调用未来 helper，无写入。
- 重新计算 `binding-specimen.json` canonical SHA：`b7ce39be57d1e0ee4b682bbba5b7341a3448329f6f53c24b1eee359b0184cfd0`，与 Task/Handoff/validation 一致。
- canonical 当前 scan：`12 errors / 2582 declarations / 1889 protected roots / 272 warnings`；R25/R26/R27/R28/R32 与旧矩阵完整 `code/file/locator/message` 匹配，剩余 7 项保持原身份。
- 模板 P09 内存 parse：**1 declaration / 2 errors / 2 warnings**；line227 worktree 声明存在且原始 index 中 exact 受保护；source guard 受保护。
- 三个 NUL 源内存 parse 均为 **0/0/0**；P14 NUL `[286]`、P22 NUL `[12330,20486]` 及 C0 列表与 specimen 一致。
- 六个 guard 根（四源 + `tools/governance/tests` + `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`）当前均 exact 受保护；两个 reference 目录存在。
- 7 EV 逐项 `raw = blob = pin` 全部成立；Task 实际 `EVIDENCE_PIN 7 / errors 0`（11 declarations）。
- `validation.json` 的 design SHA/source-facts 固定 commit/rawSHA 均匹配；`approved_design.design_raw_sha256` 与 design.md 一致。
- 运行 policy 路径 **不存在**；`tools/**` 在 `345c..ac0b` diff 为空；WT `status --porcelain` 为空。
- canonical `check.ps1`：**PASS（2 个既有 warning）**。
- `git diff --check 345c…ac0b`：**exit 0**。

**Owner 证据 / 沿用**

- Owner 证据：`validation.json`、`execution.json`、`validate_design.py`、binding specimen、7 EV pins；`execution.json` 记录 design-data/governance/diff 均 exit 0。
- 沿用已审研究 R1/R2：四源 raw SHA、NUL/C0、五完整错误、P14 `SOURCE_PIN` 未实际登记、P22 untracked/作者 unknown、7 历史身份；本设计未重复全部研究。
- Owner 1882 全保护集合比较：记录在 Task/agent-output baseline；**Reviewer 未独立重建 1882 全集合**，只核当前 12、6 guard exact 保护与当前 1889 根快照。

**NOT_RUN**

- 未来 `_apply_historical_evidence_interpretation`、实际 `12→7`、`+6 Declaration/+4 warning`、T01–T18 全部 **PLANNED_NOT_RUN**。
- 产品构建、旧 127 回归、fixture、全 102 heads/140 WT 完整盘点、进程/文件句柄、真实 apply/清理：**NOT_RUN**；不据此授权删除。
- 未创建任何临时文件/目录/探针/fixture，未改 ACL，未执行 Git mutation。

## 范围与下一步

- 本批准仅设计契约与 metadata；未来实现 Task 必须另冻，并先固定最终批准的 canonical 摘要、真实 branch/base、自有 fixture/TMP 边界与测试矩阵。
- 可继续 Codex 正常 merge/main 复核并 done；建议在 main 复核时修正 P2-1 的快照口径，并在实现 Task 中补 P2-2 的 broad-active/12 baseline 适用条件。设计通过不实施 T01–T18，不授权运行例外、原件修改、清理、父 done、r212 解除或 push；102/140 全部原位保留。