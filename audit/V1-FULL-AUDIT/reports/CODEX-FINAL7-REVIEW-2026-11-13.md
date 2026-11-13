## 审查身份与 reviewed_head / 工作树状态

**Reviewer：** Codex，全新独立上下文。  
**reviewed_head：** `6b09ca1f42a0145fa63fa317c2beb3b0596fe848`，与 `expected_head` 一致；branch=`main`。开始和结束时执行 `git status --porcelain` 均无输出，工作树 clean。

**核验命令摘要：** `git status --porcelain`、`git rev-parse HEAD`、`git branch --show-current`；只读 Git 对象哈希核验及仓库文件读取。未修改文件。

## 总结结论

**REJECT。** P7 的问题计数、11 个候选处置和 522 条证据 pin 基本可核验，但当前摘要仍有实质性的状态与裁决措辞漂移，AC3 不能收口；AC4 也尚未完成 Review 记录与 DSH 集成 closeout。产品 Release Gate 应继续 **BLOCKED**。

## 发现：按严重度排序

### F1 — 当前摘要与裁决内容不一致（阻断审计交付收口）

- Task 卡 AC3/AC4 仍写“六轮 Review”、最新 `c2f5bc827`；Rolling checkpoint 也仍以第六轮 REJECT 描述状态，但卡片后文已追加第七轮 `9bd7264ca` 记录。[Task 卡 AC3/AC4 与 Rolling checkpoint](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:32>)、[第七轮记录](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:712>)
- Release Gate 开头记七轮，阻断依据第 7 条却写“五轮 Review”和第五轮的 483 pins 状态。[13_RELEASE_GATE.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:5>)
- 最终报告前文称候选已裁决，AUDIT-05/06 汇总行仍写“待裁决”，AUDIT-14 又称待 ZCode 裁决，与现行候选台账不一致。[FINAL_AUDIT_REPORT.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md:33>)、[现行候选台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:1>)
- `AUDIT_STATUS` 顶部仍称第七轮提出的 F1 未同步项“剩余”，没有准确反映本轮同步后的当前状态。[AUDIT_STATUS.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:4>)

**最小返修：** 统一 Task 卡 AC3/AC4、Rolling checkpoint、`AUDIT_STATUS`、Release Gate 和最终报告中的当前轮次、Review 结论及候选状态；保留旧记录为明确标注的历史快照。无需改写历史审计证据或 P7 快照。

### F2 — `6b09ca1f` 门禁结果在仓库内不可核验（当前按已接受的滚动限制处理）

仓库中没有以 `6b09ca1f` 为 generated HEAD 的门禁日志或 Canonical Evidence pin。仓库内最新可核验的完整四项门禁批次是 `9b0be2cd`，四项均 EXIT 0；该批次生成于 522-pin 回填前。[AUDIT_RESUME.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_RESUME.md:23>)、[Task 卡对应 pins](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:553>)

因此，我**不能确认**派发说明所称“`6b09ca1f4` 四项 EXIT 0”。此前 Review 已接受滚动门禁未回填这一 limitation，本项不单独作为本次 REJECT 的返修条件；最终 DSH 集成 closeout 仍应记录集成后的门禁结果。

## 11 个候选的逐项裁决表

裁决与计数依据现行 [11_ISSUES.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:8>)、详细 [AUDIT_ISSUES.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:1>) 及专项报告。`INVESTIGATE` 不视为已证实缺陷。

| ID | 结论 | 进入 P0–P3 计数 | severity / priority | 依据 | 建议后续 Task / 验证 |
|---|---|---:|---|---|---|
| AUDIT-05-CAND-001 | INVESTIGATE | 否 | N/A | 合成同位 primary/SFX 产生双 Region；产品去重语义未确定，不能据此定为缺陷。 | 先裁定相同/近似区域及人工修改、`skip`/`translate` 规则；再用合成用例核验 Region 与请求数。 |
| AUDIT-06-CAND-001 | INVESTIGATE | 否 | N/A | 有 StepRun 和 provider 重试上限；未发现账单级预算，也没有真实 API 或重复扣费证据。 | 需求先决定是否要求 spend cap/idempotency；用 fake provider 测重试与预算耗尽。 |
| AUDIT-06-CAND-002 | INVESTIGATE | 否 | N/A | glossary 会进入请求，但没有严格输出匹配校验；原始需求和真实模型表现未知。 | 先确定 glossary 合同语义；再以冲突/遗漏词条用例验证。 |
| AUDIT-07-CAND-001 | finding | 是 | P2 | 定向组 127 passed / 3 failed：ZIP `store`、JSON text override、空 options 的 hook audit events 与预期不符。 | 独立修复 Task；补选项与 hook 单测，并跑真实 export 回归。 |
| AUDIT-07-CAND-002 | accepted limitation | 否 | N/A | `license_note` 只是备注；tracked font assets 为 0，默认不随包分发字体；无未授权分发证据。 | 暂不立缺陷 Task；若产品要求验证字体许可，再单独定义导入/打包检查。 |
| AUDIT-09-CAND-001 | finding | 是 | P3 | 一个合成空章节 UI 场景中仍显示已选书/章，但 Retry 提示先选择；根因和普遍性未知。 | 用隔离 Host/UI fixture 覆盖选中、零页、切换、Retry/返回路径，再修状态提示。 |
| AUDIT-12-CAND-001 | finding | 是 | P3（交付工具） | `publish.ps1` 默认输出在仓库内并递归清理；脚本未执行，没有误删证据。 | 单独修复默认输出位置并用 disposable 目录验证清理边界；不执行当前危险路径。 |
| AUDIT-14-CAND-001 | finding | **否** | P3 优先级，非产品 P0–P3 | README、架构决策等存在可核验漂移，缺少权威 V1 逐项总账，完成率无法计数；不是已证实运行缺陷。 | 建立有版本/日期的 V1 manifest，并对齐 README、AD-003、STATUS 与索引。 |
| AUDIT-14-CAND-002 | INVESTIGATE | 否 | N/A | V2 Studio 有静态 `NOT_WIRED` 能力，但其是否属 V1 承诺、真实 GUI 行为均未知。 | 先完成 V1 manifest 映射；仅纳入 V1 时再立实现与真实 UI 验证 Task。 |
| AUDIT-14-CAND-003 | close | 否 | N/A | 缺少旧图标不会由当前调用链证明 release 失败；旧 sidecar 路径也未证明为当前 release 所用。 | 不开缺陷修复 Task；如清理旧路径，先核实调用者并隔离验证。 |
| AUDIT-14-CAND-004 | close | 否 | N/A | 多 shell 路由是架构观察，没有具体运行故障证据。 | 不开缺陷 Task；后续 UI 验证记录 shell × page × 操作矩阵。 |

11 个候选当前分布为 **4 finding / 4 INVESTIGATE / 1 accepted limitation / 2 close**；不应再标为 `REVIEW_PENDING`。`AUDIT-11-INC-001` 是独立调查风险，不在这 11 个候选中。

## AUDIT-11-INC-001 裁决

保持 **INVESTIGATE**，不分配 severity，不计入 P0–P3 或 finding。仓库内本地 reflog、提交祖先关系支持“素材对象可能曾随历史 main push 进入当时公开仓库”的高置信推论，但以下事实仍然未知：

- 当前远端是否能看到、下载或 fetch 这些对象；
- 远端缓存及对象状态；
- 当时执行者的完整授权语境。

不得据此写成“当前仍已公开”或“风险已消除”。本审查没有访问远端。后续应由授权的独立只读调查固定目标、时间和结果；任何删除、历史改写或补救均需另行裁决。

## P0–P3 和 finding 总计核验

- 原有 triaged finding：`SEG-B-PROBES-001`、`SEG-B-PROBES-002`（均 Medium / High confidence，保持独立量表）、`NM-AUD-0001`（P2）。
- 开放 finding：共 **7 项**，即上述 3 项加 4 个候选 finding。
- 产品计数：P0=0、P1=0、P2=2（`NM-AUD-0001`、`AUDIT-07-CAND-001`）、P3=2（`AUDIT-09-CAND-001`、`AUDIT-12-CAND-001`）。P0/P1 的 0 仅表示当前未分配，不证明不存在。
- `AUDIT-14-CAND-001` 是 P3 优先级文档 finding，不计产品 P0–P3；`AUDIT-11-INC-001` 不计 finding；关闭的非产品观察 `AUDIT11-REV-001` 不计开放 finding。

## R1–R4 次序意见

同意先处理 R1 数据与安全风险，再处理 R2 sidecar 生命周期；R3 处理已确认的导出、Reader 提示和发布工具问题，并补关键验证；R4 处理长期文档和架构治理。`AUDIT-14-CAND-001` 的 V1 manifest 应提前到决定 `AUDIT-14-CAND-002` 是否属于当前承诺之前。详见 [整改路线](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:9>)。

## Release Gate 决定

**保持 BLOCKED；不宣告产品发布 PASS。** 仍有未修复 findings，Python Core pytest 记录 16 个失败且 EXIT 1，Avalonia TestHost 未进入测试用例，真实模型/API、完整 GUI、当前安装包及安装/升级/回退/卸载等关键面仍有具名 `NOT_RUN`/`BLOCKED`。`AUDIT-11-INC-001` 的远端可见性也未知。门禁与限制见 [13_RELEASE_GATE.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:7>)。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。**
- **AC2：MET。** 15 个专项均有结果或具名阻断；不能将任何 `NOT_RUN`/`BLOCKED` 转写为 PASS。
- **AC3：PARTIAL。** 报告和台账存在，但上文 F1 的当前状态与候选措辞冲突，不能收口。
- **AC4：PARTIAL。** 已核验 522/522 pins，但 Task 仍为 `canonical_evidence_status: pending`、`resource_closeout_status: pending`，且 integration/delivery commit 为空。[Task frontmatter](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:17>)

本次不建议转 `approved`。先修 F1 并在新 clean HEAD 做独立复审；通过后转 `approved`，由 DSH 集成。最终 `done` 前应补齐集成 commit/delivery head、最终门禁日志与对应 pins、Review 结果 pin、资源 closeout 清单，并将 `canonical_evidence_status` 与 `resource_closeout_status` 更新为 complete。

## 明确列出的未执行检查及边界

未访问远端或外部系统；未读取或重建私有漫画素材、模型或用户数据；未运行历史重型测试、build、GUI、安装/发布/卸载脚本、治理门禁脚本或依赖安装。未运行 pin 重算脚本，因为该脚本会写日志和 JSON；改为使用内存中的只读检查对 522 条 `BLOB` pin 执行 `git cat-file` 与 SHA-256 比对，并对 14 条更正核验旧值 CRLF、新值 BLOB。门禁结论来自仓库已提交日志，不代表本次重跑。