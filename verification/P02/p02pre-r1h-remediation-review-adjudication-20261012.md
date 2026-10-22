# P02PRE-R1H remediation Review adjudication

日期：2026-10-12  
Integrator / Adjudicator：Codex /root

## 冻结 Review 与 verdict

- Owner：/root/p02_r1h_codex_owner
- 非作者 Reviewer：/root/p02_r1h_remediation_review，指定 gpt-6.1-sol/high
- 冻结 Task base：946938bd0696dfddd01f87d61fe6723c63ecdc86
- 候选 branch：agent/codex/P02PRE-R1H
- 候选 HEAD/tree：4a02811d6edf9ab423d299a36c51f103e62dd5f3 / 95eb4b2977bded814e667b392e46ce5f76015c9f
- Reviewer verdict：CHANGES_REQUESTED，P0/P1/P2/P3=0/0/2/0。
- 原 Review 报告：verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-20261012.md；7949 bytes / SHA-256 2BF89EE77D3552C3DC11008F1C3A98F5ED143D711949705303CD133A22AC6021。
- 原 Review dispatch pins：verification/P02/codex-p02pre-r1h-remediation-review-input-pins-20261012.json；66CCFB05CD3E05FF12D4C1D4C85469AA864E0A0C5CCAC2149E8AD554D9A09CA3。

Codex 接受两个 finding，均待修复；候选未集成，也未运行。R1H-005/006 属于前轮 AC2 AST self-check 覆盖范围。

## Finding dispositions

### R1H-005 — OPEN / ACTION_REQUIRED / P2

self-check 对 Get-LinkTypeEvidence 与 Set-RepositoryStop helper 内任何 InvokeMemberExpressionAst 均拒绝，但 candidate 实际包含纯内存的 [string]::IsNullOrEmpty 与 [Math]::Max。静态结构表明合法 candidate 输入也会触发 throw；这不是一次已运行测试失败。

要求 Owner 在允许的 self-check 文件范围内采用精确、可解释的接收者/方法/参数 AST 白名单，或等价的最小精确结构校验；继续拒绝其他动态/外部操作，并增加合法 helper 正例及外部调用注入负例。不得删除整个 helper 安全检查来放宽规则。

### R1H-006 — OPEN / ACTION_REQUIRED / P2

当前 AST 条件只在 skip block 与 continue block 中限制操作，并以 offset/调用数量判断整体顺序；它不能覆盖实际 component loop 的完整 skip 前后区域或 loop 结束至 continue 之间的调用。Reviewer 给出的 Get-Acl -LiteralPath $full 注入例可落在被检查区间外且仍通过现有断言。纯函数负例复制逻辑，不能证明实际候选控制流回归会被拒绝。

要求 Owner 将约束绑定到实际 candidate AST 的真实 component loop 与直接父 block，覆盖 skip 前状态/目标操作、skip 后至外层 continue 的所有语句和退出关系；用内存 AST/source mutation negative cases 检查加入 hash/ACL/枚举/target read、state 改写、删除/绕过 break 或 continue 时均拒绝。只允许解析或内存检查；不得执行 candidate/getter、访问文件/ACL、增加 API/path 或运行 host capture。

## 上轮 findings 处置

Reviewer 本轮静态确认：

- R1H-001=FIXED_BY_FAIL_STOP_STATIC：冻结 status/index 基线缺失时 fail-stop 为 UNPROVABLE，不能用 live 值替代；双仓动态等值仍未证明。
- R1H-002=FIXED_STATIC：保存并拒绝非零 stage 等异常；未运行验证。
- R1H-003=FIXED_STATIC：仅接受精确 FileInfo/属性白名单，未知设备/类型停止；未运行验证。
- R1H-004=OPEN：由 R1H-005 与 R1H-006 延续。

这些处置仅是静态 source review，不是 parser/self-check/运行 PASS，也不改变 Gate。

## Review pin 时序与补充核验

Review 报告记录当时原始 source/candidate pins=8/8 MATCH。Review dispatch 后，root 为刷新治理状态而修改了 main 中未跟踪的 Task 文件，造成原 Task pin=11538 / 95AC04FABD0EBFC1B97AF1B0C37F8B24AF62B7E8C1346057E0826AEA726E85CA 与当前 Task=13733 / 86FFDD51CE8033C7C836A032BCA7F9EAE07C45F7C2411E68F8049BAB9EFF185D 不同。root 的操作限于 reviewer metadata、delivery status、历史 section 标题和新增证据段；AC1–AC7 及实现条件未编辑。root 当前复算 8 项原 pins 得到 7/8，唯一不符为上述 Task；其它来源及三个 candidate 文件仍匹配。

Codex 不把原报告描述的 8/8 延伸为当前 Task snapshot 的匹配。已派发同一非作者 Reviewer 执行 source reconciliation addendum，复核 current Task AC1–AC7 与 R1H-005/006 是否仍对齐；当前 pins 和 prompt：
- verification/P02/codex-p02pre-r1h-review-followup-pin-reconciliation-20261012.json，4052 bytes / SHA-256 516C202248B2347BE790707AB71465B57BC26A3C8F056FE82BF25354441BB4E2。
- verification/P02/codex-p02pre-r1h-review-followup-pin-reconciliation-20261012.prompt.md，2446 bytes / SHA-256 DE35D93D5F5E5AE0AA38C213D87E36281FBE0062402B51DF9ED1F01EAACEC83E。
- 唯一 addendum 输出=verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-pin-addendum-20261012.md。

Addendum 是窄 source reconciliation，不修改 candidate，也不改变本次 CHANGES_REQUESTED verdict；Owner 修复须等它完成，避免候选在核验期间变化。Codex 对 Task 编辑原因与确切替换范围负责。

## Gate / 下一步

Build Gate=BLOCKED；Hard Build Barrier=EFFECTIVE；Build/Cargo=NOT_RUN；AC1–AC7=BLOCKED / NOT_RUN（未运行，不是失败）。private_registry_absence=UNPROVABLE；Technical Gate=NOT_SATISFIED；Owner Risk Acceptance=APPROVED；Gate Disposition=WAIVED_BY_OWNER；Build Authorization=AUTHORIZED_WITH_EXCEPTION；风险原文必须保持 technical condition unmet; user explicitly accepted residual risk。

下一步：完成 source-pin reconciliation；随后把 R1H-005/R1H-006 与上述验收要求交回原 Owner，在允许的三文件范围内做最小修复。Owner 仅可运行 git diff --check；下一版仍需由非作者 Reviewer 再审。任何 parser/self-check/preflight/capture、动态隔离、Build/Cargo 或 AC 运行都必须遵循 Task 依赖和后续安全门。

Review 实际限于静态代码与 source 对照；未运行 parser、自检、preflight、capture/getter、tests、Build/Cargo、AC1–AC7、OS 动态验证或 Sandbox。风险：self-check 仍不能证明实际 skip 控制流安全；Hard Build Barrier 必须保持。