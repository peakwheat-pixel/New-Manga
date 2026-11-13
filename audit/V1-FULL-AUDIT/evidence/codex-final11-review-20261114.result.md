## 审查身份与 reviewed_head / 工作树状态

- Reviewer：Codex，新独立上下文；**ZCode 不可用、Codex 回退**。此前的额度失败有历史证据，但本次最新 headless 探测记录为 `Select a model` / `ERA_NEGOTIATION_FAILED`，无 session 或 response，不构成 Review。
- `branch=main`；`expected_head` 与 `reviewed_head` 均为 `89e16b9d6289b58ea1d5f0faa28e060124dda86d`。
- 审查开始与结束时，`git status --porcelain` 均为空；工作树 clean，未修改文件。

## 总结结论

**ACCEPT_WITH_LIMITATIONS**

交付文档、候选分类和计数整体自洽；535 条 Canonical Evidence 均通过只读 Git 对象与 SHA-256 核验。当前限制是本次 Review 尚未入库 pin、最终四项治理门禁尚未在 DSH delivery head 执行。它们是后续集成与 closeout 项，不构成要求返修审计内容的阻断项。

## 发现：按严重度排序

**无阻断性文档缺陷。** 当前有效摘要与 Task 均指向第十一轮 Review 和 535 pins；P7 集成核验记录明确是带固定 head 的历史快照，其 371/398/428/441 计数和 `REVIEW_PENDING` 描述属于各自检查点，不应当作当前状态。

有一项非阻断的当前状态同步：Task、`AUDIT_STATUS`、`AUDIT_PLAN`、Final 与 Gate 仍以早前 `1310/429` 描述 ZCode 当前不可用原因；较新的诊断记录了 `Select a model` 和缺少 `@zcode/tui`。保留 quota 证据作为历史尝试，在 DSH 记录本次 Review 时同步当前不可用原因即可；这不改变审计交付内容或本次回退授权。

## 11 个候选的逐项裁决表

| ID | 结论 | 进入 P0–P3 计数 | severity/priority | 依据 | 建议后续 Task / 验证 |
|---|---|---:|---|---|---|
| `AUDIT-07-CAND-001` | finding | 是，P2 | P2 | 定向 export 组 `127 passed / 3 failed`：ZIP/text options 与空 options 的 hook events 不符合测试预期。证据确认测试行为不符；尚未独立证明生产环境影响或根因。见 [AUDIT-07 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md>)。 | 单独实现 Task 核对冻结行为与测试预期、修复后重跑 export 回归；不宣称像素质量已验证。 |
| `AUDIT-09-CAND-001` | finding | 是，P3 | P3 | 合成 UI 的已选中零页章节在 Retry 后仍提示先选择；是单一路径的可见不一致，根因和普遍性未知。见 [AUDIT-09 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md>)。 | 隔离 Host/UI fixture 覆盖有页、零页、切换选择与 Retry，再决定窄范围修正。 |
| `AUDIT-12-CAND-001` | finding | 是，按当前台账计入 P3 交付工具 finding | P3 | `publish.ps1` 默认输出目录在仓库内且存在递归删除逻辑；脚本未运行，未证实发生误删或当前发布失败。见 [AUDIT-12 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md>)。 | 新 Task 将默认输出移至 workspace，在 disposable 目录验证目标路径与清理范围。 |
| `AUDIT-14-CAND-001` | finding | 否 | P3 文档优先级；非产品 P0–P3 | README、AD-003、STATUS 等存在可核对的文档漂移，且缺少可计数的 V1 commitment manifest；未证明由此直接造成运行故障。见 [AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md>)。 | 建立带日期/版本的 V1 manifest，再对齐 README、AD-003、STATUS 和索引。 |
| `AUDIT-05-CAND-001` | INVESTIGATE | 否 | N/A，未分配 | 合成同几何 primary/SFX 保留双 Region；默认 `skip` 可避免自动翻译，显式 `translate` 会分别处理。是否违反产品去重语义未确定。见 [AUDIT-05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md>)。 | 先裁定相同/近似几何的 Region 与翻译规则，再测 Region 数和请求数。 |
| `AUDIT-06-CAND-001` | INVESTIGATE | 否 | N/A，未分配 | 有 step/retry 上限，但无账单级 spend cap 和 provider idempotency key；没有调用真实 API，不能推断重复扣费。见 [AUDIT-05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md>)。 | 先由需求裁决费用控制语义，再用 fake provider 测超时重试；不声称远端双扣款。 |
| `AUDIT-06-CAND-002` | INVESTIGATE | 否 | N/A，未分配 | glossary 会进入请求，但生产提示和响应路径未强制术语匹配；需求是否要求强制优先级未知，未调用真实模型。见 [AUDIT-05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md>)。 | 先裁定 glossary 合同语义，再以 fake provider 覆盖冲突词条和漏匹配。 |
| `AUDIT-07-CAND-002` | accepted limitation | 否 | N/A | `license_note` 是备注而非授权验证；tracked font assets 为 0，现行政策默认不随包分发字体。本轮未核验外部许可或用户字体。见 [AUDIT-07 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md>)。 | 保留“备注不等于许可”的边界；若未来随包字体，另开许可核验 Task。 |
| `AUDIT-14-CAND-002` | INVESTIGATE | 否 | N/A，未分配 | V2 Studio 有静态 `NOT_WIRED` 能力，但是否属于 V1 承诺未知，真实 GUI 未测。见 [AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md>)。 | 先用 14-001 的 manifest 映射范围；仅确认属于 V1 后再决定是否开实现与 GUI 验收 Task。 |
| `AUDIT-14-CAND-003` | close | 否 | N/A | 没证明缺旧图标会使当前 release 失败，也没证明旧 sidecar 默认路径被当前 workflow 使用；同时未验证当前 release 成功。见 [AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md>)。 | 不开缺陷 Task；如清理旧路径，先核实调用者并在隔离环境验证。 |
| `AUDIT-14-CAND-004` | close | 否 | N/A | 多 shell 增加回归面是架构观察；没有实际运行故障证据，真实 GUI 矩阵仍未测。见 [AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md>)。 | 不开缺陷 Task；后续验证记录 shell × page × 关键操作矩阵。 |

以上四项 finding、四项 `INVESTIGATE`、一项 accepted limitation、两项 close，与 [11_ISSUES](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md>) 和 [AUDIT_ISSUES](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md>) 的裁决一致。`finding` 只表示已有审计观察达到相应裁决，不把未验证的生产影响写成已证实缺陷。

## AUDIT-11-INC-001 裁决

维持 **INVESTIGATE**，不分配 severity，不计 P0–P3 或 finding。

本地 reflog 与提交祖先关系支持“私有素材对象可能曾随历史 main push 进入公开仓库”的高置信推论；**当前远端是否可见、可下载或可 fetch，远端缓存/对象状态，以及当时的完整授权语境仍未知**。不得据此写成已公开，也不得写成已消除。

本次未访问远端、未 fetch、未尝试删除或改写历史。后续应由 DSH 单独冻结只读调查的目标、方法与允许边界；任何补救另行授权和审查。

## P0–P3 和 finding 总计核验

- 产品/发布范围当前已分配计数：P0=0、P1=0、P2=2（`NM-AUD-0001`、`AUDIT-07-CAND-001`）、P3=2（`AUDIT-09-CAND-001`、`AUDIT-12-CAND-001`）。未分配不代表已证明不存在。
- 另有 `AUDIT-14-CAND-001`：P3 文档优先级 finding，不并入产品 P0–P3 计数。
- 开放 finding 共 7 项：原 triaged 的 3 项（`SEG-B-PROBES-001/002` 为 Medium / High confidence、`NM-AUD-0001` 为 P2）加上述 4 项新 finding。两项 SEG-B 严重度仍用独立量表。
- `AUDIT-11-INC-001` 是单独的未决调查风险；`AUDIT11-REV-001` 是关闭的非产品 P3 observation，均不增加开放 finding 计数。

## R1–R4 次序意见

认可 [12_REMEDIATION_PLAN](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md>) 的 R1 → R2 → R3 → R4：

1. **R1** 先处理 AUDIT-11 当前远端可见性这一未知项，并分开处理 junction containment 和 restore 错误语义；只读调查、修复与任何历史补救分别授权。
2. **R2** 处理 `NM-AUD-0001` sidecar 生命周期。
3. **R3** 先做 P2 导出项，再处理 Reader 提示和发布输出路径；05/06/14-002 等需求未决项先裁语义。
4. **R4** 做文档和架构观察。建议把 14-001 的 V1 manifest 提前到 14-002 范围判断之前；14-003/14-004 不需缺陷修复 Task。

R1–R4 是建议次序，不等同 P0–P3 优先级，也不授权本 Task 实施修复。

## Release Gate 决定

**保持 BLOCKED；不宣告产品发布 PASS 或 CONDITIONAL。** 未修复 finding、Python pytest 的 16 个失败、Avalonia TestHost 未进入测试、具名 `NOT_RUN` 的 GUI/模型/API/安装流程，以及 `AUDIT-11-INC-001` 的远端未知状态足以支持 BLOCKED。见 [13_RELEASE_GATE](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md>)；535 pins 和历史治理门禁通过不能解除产品发布阻断。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。**
- **AC2：MET。** AUDIT-00–14 均有结果或具名限制；这不把 `FAIL`、`BLOCKED` 或 `NOT_RUN` 改成 PASS。
- **AC3：内容条件满足，可收口为 MET。** 台账、整改路线、正式报告和 BLOCKED Release Gate 齐全且分类一致。
- **AC4：当前仍需 DSH 集成后收口。** 535 pins 已通过只读复算，但本次 Review 尚未进入仓库 Canonical Evidence，最终门禁也未在 delivery head 执行。它们是可完成的集成项，不阻止本次接受。

建议 DSH：

1. 将本 reviewed head 的 Task 状态置为 `approved`；记录本次审查身份、`reviewed_head`、候选裁决、计数和“ZCode 不可用、Codex 回退”，更新当前 Review 指针。
2. 在集成提交中记录实际 `integration_commit` 与 `delivery_head`，将本次 Review 及必需 evidence pins 固定；验证 `canonical_evidence_status=complete`。
3. 在集成候选 head 执行 default governance、TaskPath governance、`verify_pins`、API inventory 四项门禁，记录每项实际 generated HEAD、EXIT、warnings 和结果，并固定输出。
4. 记录 `resource_closeout_status=complete` 的实际盘点与处置；现有标记为 `PRESERVE_REFERENCED` 的 task-env/agent-output 可保留，不要求删除。
5. 对滚动门禁，记录门禁生成 head 与 pinbackfill 后 delivery head 的对应关系，不声称门禁是在未运行的后续 head 上执行。若仅有此滚动 pin 边界，作为接受的 limitation 记录；不要因此无限递归 pin 门禁自身。
6. 四项 AC 和 closeout 记录完成后，再按 Task 生命周期更新为 `done`，并同步 `STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER` 及当前审计指针。产品 Release Gate 仍保持 BLOCKED。

## 没有执行的检查及边界

- 没有运行测试、probe、build、GUI、模型/API、安装或发布；没有重跑四项治理门禁。核对历史门禁时只读了存档日志和 JSON。
- 没有执行 ZCode Review；其 2026-11-14 headless 诊断无 session/response，不构成 Review。也没有访问远端或其他外部系统。
- 没有读取或重建私有漫画、模型、用户数据；没有清理、安装、发布、删除或改写 Git 历史。
- 已执行只读 Git 对象核验：Task 表共 535 行、535 个唯一 evidence ID，包含 512 条 `CANONICAL` 和 23 条 `SOURCE_PIN`；全部 `sha256_basis=BLOB`，path/commit/blob 可解析且可达，535/535 SHA-256 匹配，无重复 ID 或元数据异常。
- 14 条 worktree→BLOB 更正中，旧值与工作区字节 14/14 匹配，新值与 Task pin 的 Git blob 值 14/14 匹配；修正符合 `BLOB` 基准。
- `ed17a790` 与 `52b86d39` 两批各自的 default、TaskPath、pins、API 四项元数据均指向对应 generated HEAD 且 EXIT 0；这些是历史门禁，不是本次或最终 delivery-head 门禁。

**推荐下一步：** 由 DSH 按上述步骤集成并完成 AC4 closeout；之后优先释放一个范围冻结的 R1 只读 Task，核验 `AUDIT-11-INC-001` 的远端可见性，期间不做删除或历史改写。