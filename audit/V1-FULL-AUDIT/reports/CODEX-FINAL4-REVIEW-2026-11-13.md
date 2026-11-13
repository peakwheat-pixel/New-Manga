## 审查身份与 reviewed_head / 工作树状态

**reviewed_head=`1ae79bb99534e3a06fc77a284c3a5089e12fce34`；branch=`main`；工作树 clean。**

核验命令摘要：初始及结束时运行 `git status --porcelain`（均为空）和 `git rev-parse HEAD`（均为 expected_head）；另用 `git branch --show-current` 确认分支为 `main`。本次只读审查，没有修改文件。

## 总结结论

**REJECT。**

Candidate 裁决、483 条 Canonical Evidence 的 Git blob 哈希及 Release Gate 结论基本自洽。但**当前摘要仍报 462 条 pins，专项报告和证据索引仍留有“待 ZCode 裁决”措辞**。这些是交付文档中的当前事实冲突，超过了用户允许作为 limitation 的“最新门禁尚未回填”边界。

## 发现：按严重度排序

**F1｜阻断 AC3/AC4 的状态摘要不一致。** [Task 卡](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:38>)与[证据索引](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:26>)记录当前为 483 pins；[根 STATUS](<G:/CODEX/New Manga/doc/STATUS.md:7>)和[AUDIT_STATUS](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:4>)仍写 462。`AUDIT_STATUS`、[AUDIT_PLAN](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_PLAN.md:5>)、[Release Gate](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:5>)及[最终报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md:3>)也仍以四轮 Review、旧门禁批次为当前摘要。

最小返修：统一当前 pin 数为 483，引用最新门禁检查点；将本轮第五次独立 Review 结论纳入摘要，并保留四轮作为历史记录。**无需为最后一次门禁尚未 pinbackfill 单独返修**：`6c177343` 的四项门禁输出已记入 `AUDIT_RESUME`，均 EXIT 0；依滚动规则，尚未回填只是可接受 limitation。

**F2｜候选处置仍有未标历史的旧措辞。** [AUDIT-05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:34>)仍称 05、06 候选“待裁决”；[AUDIT-07 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md:72>)仍把 07-001 写成 `REVIEW_PENDING`、交 ZCode 复核，下一段也保留相同口径。[AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md:25>)仍称 14-002 待 ZCode 定级。证据索引的[05/06 描述](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:41>)和[07 描述](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:147>)也仍称候选待 ZCode 裁决，尽管各报告顶部或问题台账已经记录 Codex 裁决。

最小返修：将这些段落明确标为阶段快照，并指向当前处置；不得删去原观察和 `NOT_RUN` 限制。[11_ISSUES](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:43>)和[12_REMEDIATION_PLAN](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:25>)中的当前裁决可作为对齐依据。

P7 集成核验报告明确标为早期快照；其中 371/398/441 等为历史检查点，我没有将其误判为当前 pin 数。

## 11 个候选的逐项裁决表

| ID | 结论 | 是否进入 P0–P3 计数 | severity / priority | 依据 | 建议后续 Task / 验证 |
|---|---|---|---|---|---|
| AUDIT-05-CAND-001 | INVESTIGATE | 否 | N/A | 合成 same-geometry 的 primary/SFX 会保留双 Region；既有仲裁记录了副作用，但产品去重语义未定。[专项报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:34>) | 先定义相同/近似区域、人工修改及 `skip`/`translate` 语义，再以合成用例验证 Region 数和请求数。 |
| AUDIT-06-CAND-001 | INVESTIGATE | 否 | N/A | 有 StepRun 与 provider 重试上限，没有美元级预算；未调用付费 API，也无重复计费证据。[专项报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:49>) | 先裁决是否要求费用上限；之后用 fake provider 验证重试和预算耗尽，不推断远端扣款。 |
| AUDIT-06-CAND-002 | INVESTIGATE | 否 | N/A | glossary 会进入请求，但生产响应路径没有严格校验；原始需求是否要求逐项强制匹配、真实模型效果均未知。[专项报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:45>) | 明确 glossary 合同后，以 fake provider 覆盖冲突词条、漏匹配和无效输出。 |
| AUDIT-07-CAND-001 | finding | 是 | P2 | 定向测试 127 passed / 3 failed：ZIP `store`、JSON text override 和空 options 的 hook audit events 不符预期。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:28>) | 新实现 Task 修复 options/hook 行为；重跑对应单测及真实 export 回归。 |
| AUDIT-07-CAND-002 | accepted limitation | 否 | N/A | `license_note` 是备注而非许可验证；tracked font assets 为 0，默认不随包分发字体，未发现未授权分发证据。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:46>) | 若未来决定随包字体，再做许可来源核验；当前不据此开缺陷 Task。 |
| AUDIT-09-CAND-001 | finding | 是 | P3 | 空章节观察中，界面显示作品/章节已选中，但 Retry 提示先选择；根因和普遍性未知。[专项报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md:41>) | 用隔离 Host/UI fixture 验证有页、零页、切换选择和 Retry 路径，再修正状态与提示。 |
| AUDIT-12-CAND-001 | finding | 是 | P3（交付工具） | `publish.ps1` 默认输出在仓库内并递归清理；脚本未运行，没有误删证据。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:30>) | 新 Task 将默认输出移至相邻 workspace，并在 disposable 目录验证清理范围。 |
| AUDIT-14-CAND-001 | finding | 否（非产品） | P3 优先级 | README、AD-003 与状态清单存在漂移，缺少可计数的 V1 承诺总账；这是文档 finding，不并入产品 P0–P3。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:31>) | 建立带日期/版本的 V1 manifest，对齐 README、AD-003、STATUS 和索引。 |
| AUDIT-14-CAND-002 | INVESTIGATE | 否 | N/A | V2 Studio 有静态 `NOT_WIRED` 能力，但其 V1 归属未定，真实 GUI 未测。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:47>) | 先建立权威 V1 manifest；只有确认属于 V1 后才释放 wiring Task 和 GUI 验收。 |
| AUDIT-14-CAND-003 | close | 否 | N/A | 未证明当前发布会因旧 `IconPath` 路径失败，也未证明发布会成功；workflow 不传该参数，旧辅助路径只作未证实维护债务。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:48>) | 不开产品修复 Task；如清理旧路径，先核实调用者并纳入维护 Task。 |
| AUDIT-14-CAND-004 | close | 否 | N/A | 多 shell 扩大回归面，但没有具体运行故障证据。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:49>) | 不开缺陷 Task；后续真实 UI 验证记录 shell × page 矩阵。 |

## AUDIT-11-INC-001 裁决

维持 **INVESTIGATE**，无 severity，不计入 finding 或 P0–P3。仓库记录支持“私有素材对象可能曾随历史 main push 传播”的高置信推论，**但当前远端是否可见、可下载或可 fetch 仍未知**；远端缓存/对象状态及当时授权语境也未知。不得据此推断为已公开或已消除。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:37>)

最小后续步骤是另开范围冻结、授权的只读调查 Task，记录核验目标、时间、方法和结果。任何删除、历史改写或其他补救须另行裁决。

## P0–P3 和 finding 总计核验

[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:12>)的边界成立：

- 产品已分配等级：P0=0、P1=0、P2=2（`NM-AUD-0001`、07-001）、P3=2（09-001、12-001）。P0/P1 为当前已分配数，不代表已证明不存在。
- 开放 finding 共 7：3 个原 triaged findings（两项 SEG-B Medium / High confidence，不映射 P 级；`NM-AUD-0001` 为 P2）加 4 个裁为 finding 的候选。
- 14-001 是开放的非产品文档 finding，P3 优先级不并入产品 P3 计数。
- `AUDIT-11-INC-001` 不计 finding；已关闭的非产品观察 `AUDIT11-REV-001` 为 P3 observation，也不计开放 finding。

## R1–R4 次序意见

总体同意[整改路线](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:52>)：

1. **R1**：先通过单独授权的只读 Task 核验远端可见性，再处理 junction 越界和 restore 失败语义；调查不得顺带删除或改写历史。
2. **R2**：处理 sidecar 取消、dispose 和 Host shutdown 生命周期问题。
3. **R3**：先处理 07-001 P2，再处理 09-001 与 12-001；05/06 和 14-002 仍须先澄清需求或范围。
4. **R4**：做 V1 manifest 与文档治理。赞同将 14-001 manifest 工作排在 14-002 的 V1 归属裁决之前；关闭的 14-003/004 不应按缺陷修复。

## Release Gate 决定

**保持 BLOCKED；不宣告产品发布 PASS。** 七项未修复 finding、全量 pytest 的 16 个失败、Avalonia TestHost 未进入测试、若干关键 GUI/安装/模型检查 `NOT_RUN` 或 `BLOCKED`，以及远端可见性未知，共同支持此结论。[Release Gate](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:7>)

最新 `6c177343` 门禁记录四项 EXIT 0，只证明治理、pin 和 API inventory 的窄面；其尚未回填到下一次 pinbackfill 是本轮认可的 limitation，不解除产品 Gate。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。**
- **AC2：可收口为 MET。** 15 项均有结果或具名限制；保留各自 `FAIL`、`BLOCKED`、`PARTIAL` 与 `NOT_RUN`，不能将其概括为通过。
- **AC3：PARTIAL，不可收口。** 当前摘要和候选状态存在上述冲突。
- **AC4：PARTIAL，不可收口。** 483 pins 及本轮门禁可核验，但本轮 Review 结果尚未进入固定仓库证据并完成相应同步/closeout。
- Task 继续 `in_progress`，不要标为 done。建议 DSH 先完成 F1/F2 最小文档返修、记录本轮 Review 结果并按既定滚动规则处理门禁证据，然后再固定新 HEAD 复审和集成。

## 明确未执行的检查及边界

- 直接只读解析 Task 卡并用 Git object batch 校验：483 行、483 个唯一 ID，460 `CANONICAL`、23 `SOURCE_PIN`，全部 `sha256_basis=BLOB`；106 个引用均解析为 commit，483 个 path 均解析为 blob，483/483 SHA-256 匹配。
- 14 条 AUDIT-03/04 更正按 BLOB 基准是必要且正确的：当前更正后的 pin 全部匹配 Git blob；更正前 CRLF/worktree 根因依据仓库已有对照记录，本次未重跑归一化实验。398 条是历史检查点，[历史复算日志](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/logs/task-card-pin-recompute-20261113-final.log:8>)记为 398/398；当前数为 483。
- `ed17a790`、`52b86d39` 批次在 Task 卡内的路径、commit、哈希均通过上述核验；各自四项日志显示 EXIT 0，verify_pins 为 18/18、API inventory 为 1/79/6=86。
- ZCode 额度失败记录显示 provider `1310`、HTTP `429`、EXIT 1、无 session/response；它不是 Review，且 Codex-first 已启用。[attempt JSON](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/evidence/zcode-audit05-06-review-attempt-20261113.json>)
- 未运行测试、治理检查器或仓库 pin verifier（后者会写日志和 JSON）；未访问远端或其他外部系统，未读取/重建私有素材，未安装、发布或运行应用。只做仓库文档读取和只读 Git 对象检查。