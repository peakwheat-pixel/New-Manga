# P02 AppContainer r4 Review 处置记录

## 对象与 Reviewer 结果

- 契约：`verification/P02/appcontainer-isolation-contract-r4.md`，SHA-256=`F025A2671FA16EB317C04C457C75BBD6A29D16A753FF146BCAD4AF244A591F49`。
- Task：`doc/tasks/P02.md`，SHA-256=`C7959EF931D7D937B885267D400553AADE1E9D40E3FA0A2B47CB18486D15138C`。
- Review prompt：`verification/P02/dsh-appcontainer-contract-r4-review.prompt.md`，SHA-256=`CD9ADC218F4406E0814C0A5D2EDE5BD339D94E5D53B34FCDBFAE5389C0AD6175`。
- DSH 报告：`verification/P02/dsh-appcontainer-contract-r4-review.stdout.md`，SHA-256=`B7A3537B5EB3FFFA8626EED0E0453AED7E41BE55BD592324E1355458095C6FA1`；session=`session-80152a96-0c1b-42e8-9d64-864aea78f03a`；CLI exit=`0`；挂载脚本 exit=`0`。
- Codex 当前重新计算的契约、Task 与 prompt 哈希均与派发固定值一致。DSH 无 shell，不能自行复算哈希，故其正式对象绑定仍为 `NOT_VERIFIED`；本记录不把该 Review 改写成 exact-object `APPROVED`。
- DSH 内容结论=`APPROVED_WITH_CONDITIONS`；正式结论=`NOT_VERIFIED`；P0/P1/P2/P3=`0/0/3/6`。本轮只接受内容层 Review 用于修订契约，不作为 OS preflight、profile 创建或 Build Gate 的通过凭证。

## Finding 处置

| Finding | 处置 | 必须落实的变更 |
|---|---|---|
| R4-01 | 接受 | §2 明示 private registry 创建前不存在性为 `UNPROVABLE / BLOCKED`；删除强制调用 `GetAppContainerRegistryLocation` 的步骤，任何后续 profile 创建继续禁止。 |
| R4-02 | 接受 | §8.4 的 exclusion 集以冻结 manifest 为唯一来源；profile/private registry 在不存在性证实前不得列为可忽略项；列出三条 canary/control 的精确 leaf。 |
| R4-03 | 接受 | 负向 DACL control 固定为 `verification/P02/tmp/lpac-write-deny-control/`，加入输出路径表并明确不授 Package SID ACE、不改 label/policy。 |
| R4-04 | 接受 | §8.1 改为绑定当前 r5 Review；说明 DSH 无哈希能力时须由 Codex 核验派发 pin 并显式接受内容级 Review，才可考虑纯只读 preflight。 |
| R4-05 | 接受 | §8.5 使用 `profile directory`、`local-data directory`、`private registry storage` 三个固定术语。 |
| R4-06 | 接受 | 区分禁止的写探针/MIC 探针与获准的只读测量；MIC control 不再依赖 profile 创建，但当前没有写探针授权。 |
| R4-07 | 接受 | §4 输出表加入 `verification/P02/tmp/`，并与三条 leaf 逐项对应。 |
| R4-08 | 接受 | §5 禁止范围明确约束 LPAC 主/子进程；controller 证据写入只限 Task allowlist 中的 `verification/P02/**`。 |
| R4-09 | 接受 | 若 P1-01 或 P1-02 在只读测量后仍不可解除，停留在 `BLOCKED` 并提交明确的用户裁决选项；不自行提权、改 ACL 或放行 Gate。 |

## 依据澄清

DSH §6.1 对 `KEY_READ` 句柄与 `RegCreateKeyEx` 的提醒应限定为**后续创建调用的权限判定**，不能描述为 `RegOpenKeyEx` 自身会创建 key 或产生写副作用。Microsoft 的 [`RegOpenKeyExW`](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw) 文档明确说明：目标 key 不存在时该 API 不会创建；同页也说明 `KEY_READ` 打开的 handle 后续可能用于 `RegCreateKeyEx`，若父 key 的安全描述符允许。r4/r5 流程禁止任何创建/写 registry 调用，因此该提醒不改变 blocker。真正未解决的是目标 private-registry key/view 未被权威文档定义，且 `GetAppContainerRegistryLocation` 文档没有说明 absent-state 行为；不能用猜测路径或调用该 API 解除 `private_registry_absence=UNPROVABLE / BLOCKED`。

## 不变 Gate 与下一步

`private_registry_absence=UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。本轮未执行任何 OS probe、profile/ACL/registry 操作、Sandbox、Cargo、构建或产品测试。

下一步：在新文件 `verification/P02/appcontainer-isolation-contract-r5.md` 实施上述文档修正，更新 P02 Task 与冻结 SHA，再派 DeepSeek Harness 做非作者只读 Review。Review 与 Codex adjudication 完成前不做 OS preflight；后续纯只读测量也不得解除 private registry blocker。
