# P02PRE-R1H round-two Review adjudication

日期：2026-10-12（Asia/Shanghai）  
Integrator / Adjudicator：Codex `/root`

## 冻结 Review 与证据

- Owner：`/root/p02_r1h_codex_owner`；Reviewer：`/root/p02_r1h_remediation_review`，非作者，指定 `gpt-6.1-sol/high`；Integrator=`/root`。
- frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；branch=`agent/codex/P02PRE-R1H`；reviewed HEAD=`92c90a9ba20f7a1b4ab090837f99c191745524f6`；tree=`c70bd6c756b5d6931d07a483c958131cd2934a04`；Owner worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`。
- Review input pins=`verification/P02/codex-p02pre-r1h-remediation2-review-input-pins-20261012.json`，3866 bytes / SHA-256=`1AF1D4815B0902B3149056BFA27842FB6EBA6C318709F3A66DFB7F5B0ACC0FB9`。Reviewer 报告 pre-review source/candidate=`11/11 MATCH`；Codex 在审后重新计算同一 8 source + 3 candidate pins，也得到 `11/11 MATCH`。
- Reviewer report=`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation2-20261012.md`，8812 bytes / SHA-256=`55A55133EF04FBED607F0754C9F5D75A25371BFF0EBCFF8E469CE40E68D08894`。
- Verdict=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/1/0`。Review 仅作静态结论，不代表 parser/self-check 执行、集成、P02PRE、Gate、Build 或 AC PASS。

## Root adjudication

Codex 接受 Review 的唯一 P2 finding：

### R1H-006 — OPEN / ACTION_REQUIRED / P2

Review 指出 self-check 在 `verification/P02/p02pre-r1h-selfcheck.ps1:292–304` 校验真实 candidate loop 与 component `pathLoop`，但没有检查外层 candidate loop 内、pathLoop 之前的 prefix。对应 capture 位置为 `verification/P02/p02pre-r1h-capture.ps1:509–510`，在 `$linkSkipped = $false` 与组件循环之间。此处插入 `Get-Acl -LiteralPath $full` 或 `[IO.File]::ReadAllText($full)` 不会改变已检查的 pathLoop AST、pathLoop/continue 邻接关系或唯一 `Get-FileHash` 数量；当前 negative mutation fixtures 也未覆盖该 prefix。因此候选的目标 ACL/内容访问回归可能绕过 self-check，违反 AC2 和 frozen Review prompt 的 prefix 覆盖要求。

要求 Owner 将真实 `$candidateLoop.Body` 从 candidate 处理入口到 component `pathLoop` 之前的 prefix 纳入精确 AST 约束；保留现有合法路径处理、staging 排除和初始化操作的最小 allowlist；拒绝新增 hash/ACL/枚举/target read 及未许可的成员调用/嵌套块。为 prefix 增加能成功施加且由 contract 拒绝的内存 source mutation 负例，覆盖 ACL、内容读取以及适用的 hash/枚举操作。不得执行这些 fixture 中的伪代码。优先仅改 `selfcheck.ps1`，若需更改 Handoff 只限原有授权文件。

该 finding 是静态可达性分析，并非已运行的测试失败。当前 capture 在冻结 status/index 基线缺失处 fail-stop，故不会以此 Review finding 推导已发生 OS 访问。

## 其他 Finding disposition

- R1H-001=`FIXED_BY_FAIL_STOP_STATIC`：冻结 main/scratch status/index 基线缺失时 fail-stop 为 `UNPROVABLE`，不得将 live 值替代冻结值；未证明双仓等值。
- R1H-002=`FIXED_STATIC`：stage 保留并拒绝异常阶段/记录；没有运行验证。
- R1H-003=`FIXED_STATIC`：普通文件 leaf 与属性采用精确白名单；没有运行验证。
- R1H-004=`OPEN / ACTION_REQUIRED`：真实 AST/control-flow self-check 覆盖仍由 R1H-006 prefix gap 阻塞。
- R1H-005=`FIXED_STATIC`：精确允许纯内存 `IsNullOrEmpty`/`Math.Max` 调用形态并拒绝外部调用；未执行 self-check。

## 验证与边界

- Reviewer 实际审查 frozen base→HEAD 全量三条 candidate 路径；独立记录的 static Review 命令和读取清单见其报告。未运行 parser、自检、preflight、capture、getter/API、tests、Build/Cargo、AC1–AC7、OS dynamic 或 Windows Sandbox。
- Codex post-review 用 PS7 对 pins JSON 枚举的 11 项文件复核字节数与 SHA-256，11/11 匹配；Review report pin 匹配。
- 本 adjudication 不集成交付、不通过 AC2 或 AC3，不释放 R1H parser/self-check/preflight/capture，不解除 Build Barrier。

## Gate 与下一步

Gate 原值保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。Windows Sandbox 不查询、安装、启用或启动。

下一步：将 R1H-006 prefix gap 与新增 negative case 的冻结修改范围交原 Owner `/root/p02_r1h_codex_owner`。Owner 仅能写三条既有 candidate paths，且只能运行 `git diff --check`；交付新 HEAD 后先由 Codex 验收，再交非作者 Reviewer 重审完整 frozen Task base→新 HEAD。其余依赖、Build Gate、AC 继续 blocked。
