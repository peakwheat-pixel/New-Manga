## 审查身份与 reviewed_head / 工作树状态

- **Reviewer：** Codex，全新独立上下文。
- **reviewed_head：** `226eb048006ffa804ebefd9f98e51bbc13793f31`，与 `expected_head` 一致；分支 `main`。
- **工作树：** 审查开始与结束时 `git status --porcelain` 均为空。
- **实际核验命令摘要：** `git status --porcelain`、`git rev-parse HEAD`、`git branch --show-current`、`git log --oneline --decorate -12`、`git show --stat --oneline --summary HEAD`；另以只读内存脚本读取 Task 卡并通过 `git cat-file --batch` 核验 pin。没有修改文件。

## 总结结论

**REJECT**（审计交付仍有阻断性文档与证据收口问题；这不是产品发布裁决）。

上一轮返修**部分完成**：70e92876 与 b72363aa 的 gate pins 已补齐；9 个重复 `evidence_id` 已重命名；Task 卡的 428 条 pins 均可核验。但状态摘要仍有旧值，P7 报告的计数结论仍不一致，AUDIT-14-CAND-003 的过强表述也未在所有相关文档中消除。此外，最新 076dfbb6 门禁批次尚未进入 Task Canonical Evidence，也没有 pinbackfill 后的新门禁结果。

## 发现：按严重度排序

1. **阻断接收：当前状态和计数仍互相矛盾。**  
   Task AC 区已写 AC1/AC2 `MET`、AC3/AC4 `PARTIAL` 和 428 条 pins，但 Task Rolling checkpoint 仍写 398；[STATUS](</G:/CODEX/New Manga/doc/STATUS.md:7>) 仍称 398 条、Codex `REJECT` 待修；[AUDIT_STATUS](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:6>) 又把 AC2 写为 `PARTIAL`，且把 Codex Review 写成待结果。[AUDIT_PLAN](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_PLAN.md:5>) 仍以 77310033 为最新 gate batch。  
   [P7 集成报告](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md:24>) 记录了当时 398 条，但结论仍称当前为 371/371；[Evidence Index](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:20>) 也仍有 398/398 旧口径。  
   **最小返修：** 以明确日期的当前检查点统一当前 pin 数为 428、AC2 为 `MET`、AC3/AC4 为 `PARTIAL`、Codex 复审已完成且本次结论为 `REJECT`；把旧检查点标成历史状态，并说明 P7 报告中的 371 是更正前子批次、398 是当时总数，消除二者看似互斥的表述。

2. **阻断 AC4：最新门禁结果尚未纳入 Canonical Evidence。**  
   我核对了 Task 卡 **428 条唯一 pins**：commit、path 均存在，BLOB SHA-256 **428/428 匹配**；无重复 ID。70e92876 和 b72363aa 各有 8 条 pin（四项门禁各含日志与 JSON），各自 `generated HEAD`、四项 `EXIT 0` 与元数据相符。  
   但 076dfbb6 的 default、TaskPath、`verify_pins`、API inventory 四项结果只见于 [Evidence Index](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:12>)，Task Canonical Evidence 表没有这批文件的 pin；日志所记 generated HEAD 是 `076dfbb63ad7f2b63605bfc16cdd8079e96dd6b2`，并非本次 reviewed_head。  
   **最小返修：** 将这批 8 个日志/JSON 文件纳入 Task pins，再按滚动 pinbackfill 规则在后续固定 HEAD 重跑四项治理门禁并记录结果。当前不能把 076dfbb6 的门禁说成在 reviewed_head 执行。

3. **主要追溯问题：候选决议未同步到全部详细材料，14-003 仍有过强断言。**  
   [AUDIT_ISSUES](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:3>) 的总述仍称后续由 ZCode 更新状态，多个条目仍以“请 ZCode 裁决”或“若 ZCode 接受”收尾；AUDIT-07、09、14 专项报告也仍把候选标成 `REVIEW_PENDING`。此外，[AUDIT-14 报告](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md:31>) 仍称 CI 因旧路径文件存在而可工作，[整改计划](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:47>) 写“当前 release 不会因此失败”。[AUDIT_ISSUES](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:46>) 的更正口径较谨慎，但其建议仍写“若 ZCode 接受”。  
   **最小返修：** 保留原专项报告作为当时观察，增加醒目的 Codex adjudication 后续说明并标注旧 `REVIEW_PENDING` 已被取代；将“当前 release 不会失败”改成“没有证据证明当前 release 会因此失败”，不声称 CI 成功。

## 11 个候选的逐项裁决表

| ID | 结论 | 进入 P0–P3 计数 | severity / priority | 依据 | 建议后续 Task / 验证 |
|---|---|---:|---|---|---|
| AUDIT-05-CAND-001 | INVESTIGATE | 否 | N/A | 合成相同几何产生两个 SFX Region；既有仲裁已记录该副作用，但产品去重语义未确定。[AUDIT-05/06 报告](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:32>) | 先定义相同/近似区域、人工修改及 `skip`/`translate` 语义，再用合成用例验证 Region 数和请求数。 |
| AUDIT-06-CAND-001 | INVESTIGATE | 否 | N/A | 有 StepRun 和重试上限，没有账单级 spend cap/idempotency key；没有真实 API 或双重计费证据。[报告](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:47>) | 由需求 Task 决定费用预算策略；用 fake provider 覆盖超时重试、fallback 与预算耗尽。 |
| AUDIT-06-CAND-002 | INVESTIGATE | 否 | N/A | glossary 会进入请求，但生产输出没有强制术语校验；尚无证据证明这是违背已确认需求。[报告](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:43>) | 先确定 glossary 合同语义，再用冲突词条、漏匹配和失败策略测试。 |
| AUDIT-07-CAND-001 | finding | 是 | P2 | 定向测试 127 通过、3 失败，涉及 ZIP options、JSON text override 与 hook audit events。[问题证据](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:110>) | 新实现 Task 修正有效 options 与 hook 事件；运行对应测试和 export 回归。 |
| AUDIT-07-CAND-002 | accepted limitation | 否 | N/A（限制） | `license_note` 只是备注；仓库无 tracked font assets，FEA-14-FONT-1 默认不随包分发字体；用户字体许可没有核验。[问题证据](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:117>) | 若未来要求验证用户字体许可，另开需求/实现 Task；本审计未读取用户字体。 |
| AUDIT-09-CAND-001 | finding | 是 | P3 | 合成空章节中仍显示已选作品/章节，Retry 却提示先选择；单一场景成立，根因与普遍性未知。[问题证据](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:124>) | 用隔离 Host/UI fixture 覆盖有页、零页、切换与 Retry 路径，再修正状态提示。 |
| AUDIT-12-CAND-001 | finding | 是 | P3（交付工具） | `publish.ps1` 默认输出位于仓库内，目录存在时递归删除；脚本未运行，没有已误删证据。[问题证据](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:131>) | 新 Task 将默认输出移到 workspace，并在 disposable 目录验证清理范围。 |
| AUDIT-14-CAND-001 | finding | 否（非产品 P 级计数） | P3 优先级（文档/范围） | 缺少可逐项核验的 V1 承诺总账，且当前文档有可证实漂移。[台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:28>) | 独立文档 Task 建立带日期/版本的 V1 manifest，并对齐产品说明与规划。 |
| AUDIT-14-CAND-002 | INVESTIGATE | 否 | N/A | V2 Studio 有 `NOT_WIRED` 能力，但其是否属于 V1 尚不明确。[台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:36>) | 先映射权威 V1 manifest，再决定是否释放实现 Task 和真实 Host/GUI 验收。 |
| AUDIT-14-CAND-003 | close（关闭“当前 release 会失败”断言） | 否 | N/A | workflow 不传 `IconPath`；没有证据证明缺少旧图标会使当前 CI 失败，也没有证明当前 release 使用旧 sidecar 路径。[台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:45>) | 暂不开产品修复 Task；如清理旧路径，先核实调用者并在隔离环境验证。 |
| AUDIT-14-CAND-004 | close | 否 | N/A | 多 shell 是架构观察，没有具体运行故障证据。[台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:51>) | 不开缺陷 Task；后续真实 UI 验证记录 shell × page × 关键操作矩阵。 |

## AUDIT-11-INC-001 裁决

维持 **INVESTIGATE**；不分配 severity，不计入 P0–P3 或 finding 总数。本地 reflog 和祖先关系支持私有素材对象**可能**曾随历史 main push 进入公开仓库的高置信推论。**当前远端是否可见、可下载或可 fetch 仍未知**；远端缓存/对象状态及当时授权语境也未知。不得推断为已公开或已消除。[详细台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:37>)

## P0–P3 和 finding 总计核验

- 产品 P0/P1/P2/P3：**0 / 0 / 2 / 2**。P0、P1 是当前正式分配数为零，不表示已证明不存在。
- 开放 finding：**7 项**，即 3 项原已 triage（两项 Medium / High confidence、未映射 P 级；`NM-AUD-0001` 为 P2）加 4 项新 finding。其中产品 P 级 finding 4 项，另有 1 项非产品文档 finding。
- 11 个候选：4 finding、4 INVESTIGATE、1 accepted limitation、2 close。
- `AUDIT-11-INC-001` 是额外的 INVESTIGATE 风险，不算 finding；`AUDIT11-REV-001` 是已披露关闭的非产品 P3 observation，也不算开放 finding。[计数台账](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:11>)

## R1–R4 次序意见

总体次序支持 **R1 → R2 → R3 → R4**：R1 先安排有明确授权范围的只读远端可见性调查，并分别处理两项安全/恢复 finding；R2 处理 sidecar 生命周期 P2；R3 处理已确认的导出 P2，再处理 Reader 提示和发布工具问题。R4 的 V1 manifest（14-001）应提前到任何关于 14-002 是否属于 V1 的裁决之前；不应因此推迟 R1 安全工作。[整改路线](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:50>)

## Release Gate 决定

**保持 BLOCKED，不宣告 PASS 或 CONDITIONAL。** 7 项开放 finding 尚未修复，仍有全量 pytest 失败、TestHost/sandbox 阻断、未完成的安装与 UI 验证、真实模型/API 等具名 `NOT_RUN`；AUDIT-11-INC-001 的远端可见性也未知。治理 gate 的 EXIT 0 只证明对应治理检查成功，不解除产品发布阻断。[Release Gate](</G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:9>)

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。** 固定基线、Git/environment 与源码清单已有证据。
- **AC2：MET。** AUDIT-00–14 均有结果或具名限制；这不把任何 `FAIL`、`BLOCKED` 或 `NOT_RUN` 改成 PASS。Task 顶部已记 `MET`，但 AUDIT_STATUS 的旧段落需同步。
- **AC3：PARTIAL，不可收口。** 报告、问题台账、整改路线和 Release Gate 均已落盘，但当前状态漂移、P7 计数歧义及专项报告残留旧裁决状态仍待修正。
- **AC4：PARTIAL，不可收口。** 428 pins 的对象与哈希有效，历史 Review 与 70e/b723 gate 批次已 pin；但 076dfbb6 四项门禁未 pin，也未在 pinbackfill 后重跑。当前 Task metadata 仍是 `in_progress`，`delivery_head`、`integration_commit`、canonical evidence/resource closeout 状态未完成。[Task AC](</G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:34>) [Task checkpoint](</G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:506>)

**Task 建议保持 `in_progress`，不得置 `done` 或 `closed_with_limitations`。**

## 没有执行的检查及边界

未运行测试、governance checker、`verify_pins.ps1` 或 API inventory；未访问远端、外部服务或私有素材，未读 `source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt`，未重跑重型测试、真实模型/API、GUI、安装/升级/回退/卸载或 soak。未修改文件，未 push、安装、清理或发布。SHA 核验仅读取已列入 Task 的 Git 对象和审计文件。

**建议下一步：** DSH 修正当前状态指针、P7 数字范围及候选报告的旧口径；将 076dfbb6 门禁输出纳入 pins，按滚动规则重跑治理门禁；随后以 clean head 再做 Codex 优先的独立复审。