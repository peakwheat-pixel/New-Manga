## 审查身份与 `reviewed_head` / 工作树状态

Reviewer：Codex，全新独立上下文。`reviewed_head=f251270833f3ea775f6f577dbfa33e6c88073162`，与 `expected_head` 一致；branch=`main`。审查开始和结束时 `git status --porcelain` 均为空，工作树 clean。

核验命令摘要：`git status --porcelain`、`git rev-parse HEAD`、`git branch --show-current`、`git log/show`、`rg`、文件读取，以及只读 Python 对 `git cat-file` 对象的 BLOB 哈希复算。未写入仓库文件。

## 总结结论

**REJECT。** 候选裁决、计数、Release Gate 和当前 535 条 pins 的内容可核验；仍有当前状态摘要没有同步到最新门禁与第八轮 Review 的问题，阻止本轮接受交付。产品 Release Gate 应维持 `BLOCKED`。

## 发现：按严重度排序

### F1 — 当前执行点和 Review 摘要有漂移（阻断接受）

[当前执行点](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_PLAN.md:5>)仍把 `0de08632` 列为最新 gate batch、只记七轮 Review；但[恢复记录](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_RESUME.md:27>)记录了第八轮 `6b09ca1f` 的 `REJECT`，并在第 29–31 行记录 `46a8fe6e` 四项门禁及 535 条 pins 回填。[Task AC4](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:38>)和[状态摘要](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:4>)的 gate 列表也停在 `9b0be2cd`，没有列出已 pin 的 `46a8fe6e`。[最终报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md:3>)仍称第七轮 `CODEX-FINAL6` 为最新 Review；[Release Gate](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:15>)仍以七轮和 522 pins 描述 Review 状态。

**最小返修：**同步 `AUDIT_PLAN`、`AUDIT_STATUS`、Task 的 AC4/Rolling checkpoint、`FINAL_AUDIT_REPORT` 与 `13_RELEASE_GATE`：记录第八轮结果及修订状态、535 pins，并说明 `46a8fe6e` 是最新已记录的四项门禁。保留产品 Gate `BLOCKED`。历史固定快照无需改写，但应保持其历史定位清楚；[P7 集成记录](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md:3>)已标为早期快照。

另纠正派发说明中的时间锚点：仓库没有 `f25127083` 的四项门禁记录。`f25127083` 是 535 pins 回填提交；当前可查到的最新四项日志生成于 `46a8fe6e`，收录于 `f0fa06ef`。该批在当时的 Task 树为 522 pins；恢复记录也将“回填后运行门禁”列为下一步。因此 AC4 现在不能收口。最终门禁应在 DSH 集成后的 delivery head 上记录。

## 11 个候选的逐项裁决表

依据集中在[候选裁决台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:39>)、[详细问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:5>)及对应专项报告。

| ID | 结论 | 进入 P0–P3 计数 | severity / priority | 依据与建议后续 Task / 验证 |
|---|---|---:|---|---|
| `AUDIT-05-CAND-001` | INVESTIGATE | 否 | N/A | 合成 same-geometry 保留两个 SFX Region，但去重语义未确定。[专项报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:56>)；先裁定相同/近似区域、人工修改及 `skip`/`translate` 规则，再验证 Region 数和请求数。 |
| `AUDIT-06-CAND-001` | INVESTIGATE | 否 | N/A | 有步骤与重试上限，没有账单级预算；未调用付费 API，也无重复计费证据。先裁定费用控制要求，再用 fake provider 验证预算耗尽和重试边界。 |
| `AUDIT-06-CAND-002` | INVESTIGATE | 否 | N/A | Glossary 随请求发送，但需求是否要求输出强制匹配、真实模型是否违例均未知。先定合同语义，再验证冲突词条和漏匹配。 |
| `AUDIT-07-CAND-001` | finding | 是 | P2 | 定向测试 `127 passed / 3 failed`，涉及 ZIP `store`、JSON text override 和空 options 的 hook audit events。[专项证据](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md:62>)；另立修复 Task，补 options/hook 单测及真实导出回归。 |
| `AUDIT-07-CAND-002` | accepted limitation | 否 | N/A | `license_note` 只是备注；tracked fonts 为 0，FEA-14-FONT-1 说明默认不随包分发字体。没有未授权分发证据；之后若随包带字体，再核验授权。 |
| `AUDIT-09-CAND-001` | finding | 是 | P3 | 合成零页章节中界面仍显示选择，Retry 却提示先选择。[观察](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md:41>)；隔离 Host/UI fixture 覆盖选中、切换、零页及 Retry/返回，再修提示状态。 |
| `AUDIT-12-CAND-001` | finding | 是 | P3（交付工具） | `publish.ps1` 默认输出到仓库内目录，目录已存在时递归清理；脚本未运行、无误删证据。[报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md:17>)；另立 Task 将输出移到 workspace，并只在 disposable 目录验证清理边界。 |
| `AUDIT-14-CAND-001` | finding | **否** | P3 优先级，非产品 P0–P3 | README、AD-003 等有可核验漂移，缺少 V1 逐项承诺总账，完成率无法计算。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:26>)；另立文档 Task 建立有日期/版本的 manifest 并对齐相关文档。 |
| `AUDIT-14-CAND-002` | INVESTIGATE | 否 | N/A | V2 Studio 有 `NOT_WIRED` 面，但 V1 归属未知且 GUI 未验证；先完成权威 manifest 映射，再决定是否实施及做真实 UI 验收。 |
| `AUDIT-14-CAND-003` | close | 否 | N/A | 未证明缺旧图标会导致当前 release 失败，也未证明当前 workflow 使用旧 sidecar 路径；关闭“当前 release 会失败”断言。若清理旧辅助路径，先核实调用者。 |
| `AUDIT-14-CAND-004` | close | 否 | N/A | 多 shell 增加回归面是架构观察，没有具体运行故障证据；后续 UI 验证记录 shell × page × 操作矩阵即可。 |

## `AUDIT-11-INC-001` 裁决

维持 **INVESTIGATE**；不分配 severity，不计入 finding 或 P0–P3。

本地 reflog 与提交祖先关系支持“私有素材对象可能随历史 main push 进入当时公开仓库”的高置信推论。以下事实仍未知：**当前远端是否可见、可下载或可 fetch；远端缓存及对象状态；当时完整授权语境。** 不能写成已公开，也不能写成已消除。详见[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:60>)。

后续最小步骤是另立有明确授权范围的只读核验 Task，记录目标、时间和方法。该核验不应顺带删除对象、改写历史或实施补救；本次没有访问远端。

## Canonical Evidence、计数与证据边界

- 当前 Task 有 **535 条** pins：逐条验证 commit 类型、`commit:path` 存在及 BLOB SHA-256，结果 **535/535 匹配、无重复 ID、无非 BLOB basis**。14 条 AUDIT-03/04 更正均必要且正确：旧值对应 LF→CRLF 后的工作区字节，新值对应 raw Git BLOB，**14/14** 两端匹配。当前 pins 的复算结果可重复核验。
- 历史 398 条 JSON 记录的 398 个对象哈希均匹配，且 398 个 commit/path/hash 组合都包含在当前 535 条中。其记录的 `HEAD=a021083c` 对应 Git 树内 Task 实际只有 371 条；398 结果应按当时工作区快照理解，而不是声称该提交树已有 398 行。历史 398 结果有 389 个不同 evidence ID；后续重命名已消除当前重复。
- `52b86d39`、`ed17a790` 两个门禁批次各有 8 条 pins，日志与 JSON 的 generated HEAD 对应，四项结果均 `EXIT 0`。ZCode 额度复核的三条 pins 支持 `provider code 1310`、HTTP `429`、`EXIT 1`、无 session/response；它不是 Review。
- 最新已记录的四项门禁是生成于 `46a8fe6e` 的批次，不是 `f25127083`。这不改变产品 Gate，但意味着当前 AC4 仍须等 DSH 集成后的门禁记录。

## P0–P3 和 finding 总计核验

- 11 个候选：4 finding、4 INVESTIGATE、1 accepted limitation、2 close。
- 开放 finding 共 **7 项**：原有 3 项（`SEG-B-PROBES-001/002` 为 Medium / High confidence、未映射 P 级；`NM-AUD-0001` 为 P2）加 4 项候选 finding。
- 产品计数：**P0=0、P1=0、P2=2、P3=2**。`AUDIT-14-CAND-001` 是非产品文档 finding，P3 仅为优先级，不进入产品 P 级计数。
- `AUDIT-11-INC-001` 不计 finding；关闭的非产品观察 `AUDIT11-REV-001` 也不计开放 finding。P0/P1 为当前已分配数量，不表示已证明不存在。

## R1–R4 次序意见

维持 **R1 → R2 → R3 → R4**。

1. **R1**：先由独立且获授权的只读 Task 查清 `AUDIT-11-INC-001` 远端现状；再分别处理 junction containment 与 restore 失败语义，不能把调查与历史处置混在一起。
2. **R2**：修复 `NM-AUD-0001` sidecar 取消、Dispose、EOF 和 Host shutdown 生命周期。
3. **R3**：先处理导出 P2（`AUDIT-07-CAND-001`），再处理 Reader 提示和 publish 输出路径；05/06 及 14-002 先裁定需求。并补核心旅程、GUI、安装及质量/安全验证。
4. **R4**：保留长期文档和架构治理；把 `AUDIT-14-CAND-001` 的 V1 manifest 提前到 `AUDIT-14-CAND-002` 归属决定之前。

## Release Gate 决定

维持 **BLOCKED**，不宣告产品发布 PASS。未修复 findings、AUDIT-02 `BLOCKED`、AUDIT-01/03/08/11 `FAIL`、pytest 16 个失败、Avalonia TestHost 未进入测试用例，以及真实模型/API、完整 GUI、当前安装包和 clean Windows 安装等具名 `NOT_RUN`/`BLOCKED`，都支持此结论。`AUDIT-11-INC-001` 仍未知。[Release Gate](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:7>)。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。AC2：MET。** 当前专项结果保留 `FAIL`、`PARTIAL`、`BLOCKED` 和 `NOT_RUN`；没有把失败或未运行项写成 PASS。
- **AC3：当前不可收口。** F1 的当前状态摘要漂移必须修正，随后由新的固定 head Review 确认。
- **AC4：当前不可收口。** 535 pins 已验证，但最新四项门禁不是在 535-pin 的 `f25127083` 上运行；最终门禁、集成后当前 pin、资源 closeout 尚待完成。
- 当前 `integration_commit`、`delivery_head` 为空，`canonical_evidence_status` 与 `resource_closeout_status` 均为 `pending`。[Task 卡](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:11>)。
- 本轮结论为 `REJECT`；按[协作协议 §4](<G:/CODEX/New Manga/doc/09_COLLABORATION.md:69>)，建议 DSH 记录 `changes_requested`，修订 F1 后以新 head 重新进入 `in_review`。获接受后再转 `approved`，由 DSH 集成并填写 `integration_commit`、`delivery_head`；补齐当前证据 pins 和资源 manifest 的 closeout，再将两个状态设为 `complete`，于集成后的 delivery head 记录最终四项门禁。全部已释放 AC 通过后才可设 `done`。

## 没有执行的检查及边界

没有运行测试、治理 checker、构建、安装、发布或清理命令；没有运行四项最终门禁；没有访问远端，也没有读取或重建私有素材。所有门禁结论来自已有仓库日志和对象证据。本回复未写入 Review 文件，符合本次只读约束。

**推荐下一步：**由 DSH 仅同步 F1 所列当前状态，记录本次 `REJECT`，随后在新固定 head 上安排独立复审；产品 Gate 继续保持 `BLOCKED`。