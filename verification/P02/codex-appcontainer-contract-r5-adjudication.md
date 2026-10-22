# P02 AppContainer contract r5 Review findings 处置记录

- 日期：2026-10-10（Asia/Shanghai）
- Task：P02
- Adjudicator / Integrator：Codex
- 独立 Reviewer：DeepSeek Harness（非作者）
- 主仓基线：main@cddff58469b56e181019a8ddfeade80684bc7eb9
- r5 Review：CLI exit=0；session=session-0e3dba2a-8741-4271-bcbb-34f2afe9d48c；mount exit=0
- r5 Report SHA-256：95F7471F3D97F670A038159525203F72654C92EB867FC629516A74340B612C63
- Reviewed Task SHA-256：8CB3452994BA0DC5611BFF04E835F5B511903DB9CE817EE127EB4737876210F7
- Reviewed r5 Contract SHA-256：298C173DD2A434D87099B80996DF17F0FA2AB15B66662695CD3754953108E9BA
- Reviewed manifest r1 SHA-256：55E4ABD0822B81402C2023993D61C88BA747A96625C9FB2760DA6E2E43B99BD2

## Review 结论

DSH 内容结论为 CHANGES_REQUESTED，P0/P1/P2/P3=0/1/2/6，共 9 项 open；整体正式结论为 NOT_VERIFIED，object_binding=NOT_VERIFIED。DSH 未运行 shell、Git、Windows API 或任何 OS measurement。报告指出 r5 不能作为无歧义的 Phase A 执行契约，因此不准许开始预检。

Codex 逐条处置如下：

| Finding | 处置 | 修订位置 |
|---|---|---|
| R5C-01 P1：契约与 manifest 读取范围冲突，P1-02 出口不可达 | 接受 Reviewer 的第二种最小修正。明确拆为 Phase A 与 Phase B。Phase A 严格限现有 controller-only manifest；系统 DACL、profile/local-data、output-root 内容/安全描述符、Git/clone pins 均排除并保持 NOT_RUN。Phase B 必须另有逐路径、逐 API、逐字段清单及 Review/adjudication。Phase A 不解除 P1-01、P1-02 或 Build Barrier。 | r6 §1.2、§2、§3、§4、§8 |
| R5C-02 P2：Task 行号过期 | 接受。改用 P02 Task 中 Smoke 只读 alias 与 generated-file hash 规则的稳定语义锚点，不再引用移动行号。 | r6 §1、§4、§8 |
| R5C-03 P2：没有唯一标识只读清单 | 接受。r6 精确 pin manifest r2 的路径和 SHA-256；P02 Task 与 DSH prompt 也固定该对象。 | r6 §8；manifest r2；P02 Task |
| R5C-04 P3：表格缺少三条 leaf 行 | 接受。在 scratch 表中逐行列出 Smoke read-only alias、正向 canary、负向 DACL control 及独立写入/权限策略。 | r6 §4 |
| R5C-05 P3：状态 token 不一致 | 接受。统一为 private_registry_absence=UNPROVABLE / BLOCKED 和 OS isolation preflight=NOT_RUN。 | r6 header 与 §8 |
| R5C-06 P3：Triton 环境与 WER 前后采样缺失 | 接受。环境表登记 TRITON_CACHE_DIR；manifest r2 要求同范围 WER T0/T1 两次采样。 | r6 §6；manifest r2 |
| R5C-07 P3：Task 保留 r4 当前待审状态 | 接受。将旧 r4 段落标为历史；记录 r5 Review 已完成、r6 为当前候选。 | P02 Task continuation |
| R5C-08 P3：profile root / profile tree 术语残留 | 接受。统一到 profile directory、local-data directory、private registry storage；移除 profile root/tree 用词。 | r6 §2、§6、§8 |
| R5C-09 P3：授权文字与执行前置条件有字面张力 | 接受。授权句改为范围定义，并明确执行须等 r6 DSH Review 与 Codex adjudication。 | r6 header、§8、精确下一步 |

## 新候选与状态

- r5 保留为不可执行的历史候选，不覆盖或改写原报告。
- r6 Contract SHA-256：A7ED633CB00146DC60971BF35456D4B41E28229183BB0A1115A4E561A5A30C49。
- Phase A manifest r2 SHA-256：FD7C6AAB2888E235B3186FF7FC3AE5A8E9192BBCFC5A0D778B48C6B8AE4D7828。
- r6 与 manifest r2 仍是待审候选；本 Codex adjudication 接受 r5 findings 的修订方向，不等于新候选 Review 通过或对象绑定通过。
- 本轮未运行 Phase A/Phase B measurement，未调用任何 profile/private-registry API，未改 ACL/label/registry，未运行 probe/build/Sandbox。

## Gate

private_registry_absence=UNPROVABLE / BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；OS isolation preflight=NOT_RUN；hook/cache/child-process closure=BLOCKED / NOT_VERIFIED；Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；Hard Build Barrier=EFFECTIVE；AC1–AC7=BLOCKED / NOT_RUN。

