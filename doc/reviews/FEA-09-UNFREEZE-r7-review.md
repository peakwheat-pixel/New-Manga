**结论：`changes_requested`；P0=0 / P1=3 / P2=0。r7 尚未形成可冻结的完整契约语义。**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；未参与 FEA-09 实现、I001 裁决、r1–r6 起草或 r7 修订；未派子代理。
只读交付：未修改仓库、配置或用户数据，未创建报告文件，未 commit/push；本输出供 DSH 原字节归档。

仓库：`G:\CODEX\New Manga`；分支 `main`；common directory=`G:/CODEX/New Manga/.git`。
审查前后 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`（`reviewed_head`）。
r7 为未跟踪工作树文件，**不属于 reviewed_head 的提交字节**；6015 bytes。
r7 SHA-256：`c30634f7f0e9160290de870903ea7fe900f35eba322fd6c908e6a568d27d1c00`。

审查前后 `git status --porcelain=v1 --untracked-files=all` 相同：16 项既有 ` D`、10 项 `??`。
删除项均位于 `verification/FEA-09/native-registry/`，四组目录：
`37d836da52c94ad082d1bd01dcad9ea0`、`59949b7674c84c5297963275759606bf`、
`94737b1ab618406b9329c68637a2decc`、`d5e7ddf952c14c3b8e01ac92af56e6d4`。
每组为 registry、lock、corrupt、quarantine 文件各一项。
未跟踪项：impl-design；r3–r6 amendments/review；r7 amendments。
status 输出 SHA-256：`f685c368c7ff62c8953e7e48ed1e723b29f322a01eb4889c7b2bf5fb492ddad6`。

已核对指定 r3–r7 提案与 Reviews、impl-design、C-05/C-15/C-16/C-06/C-01b/C-14、M2-C1、冻结记录/矩阵、I001 裁决及当前权威指针。

| 必答项 | 判定 | 核验结果 |
|---|---|---|
| R6-001 | **OPEN** | C-16 §6 全部18码均覆盖，10码 PAGE、8码 REQUEST，无交集；另有 `INPUT_REVISION_CHANGED` 等既有码。分类本身可承载 V/R 分离，但闭集外错误面与 resume 边界仍未闭合，见 R7-001。 |
| R6-002 | **OPEN** | 表中明确列出的 code/category/retryable 均与 C-16 §6 原值逐字一致；过期/撤销的检查位置及结果仍不唯一，见 R7-002。 |
| R6-003 | **OPEN** | Auth-G 与 Secret-G 分离解决了“缓存无 token 却必须按 token 选 G”的原矛盾；但多匹配和 Host revoke 条款互相冲突，见 R7-003。 |
| R6-004及归档 | **CLOSED** | r5/r6 review 已存在且可读取；哈希与 r7 引用前缀相符，报告中的提案大小/指纹亦匹配。完整归档指纹见下。 |
| A/B与冻结流程 | **CLOSED（流程层）** | A→B、语义提交→三指纹/old-new blob→新上下文复核已提交字节→仅元数据重冻可执行；当前语义前置未满足，不得据此重冻或释放实现。 |

**R7-001 — P1：Reader 闭集外传播与恢复边界仍不确定。**
位置：`r7-amendments.md:11、18、35–36`；继承的 r6 §1；M2-C1 §6.3/§8。
“闭集外→REQUEST_LEVEL/internal”会覆盖既有非 internal 错误；例如 `REF_SIGNATURE_INVALID` 应整请求传播，但不能因此改写其既有错误面。第35行仅保证 code，未消除此冲突。
r7 将 resume 沿用 r6，而 r6 仍未确定：锚点自身可读是否包含该页；锚点后无可读页、前方有可读页如何处理。空章节也缺少必填 `initial_position.page_id` 的确定表示。
**最小修复**：REQUEST 为 PAGE 的补集并保留原 envelope；仅无既有映射时定义明确兜底。补齐上述恢复/空集结果，无需冻结 UI 实现。

**R7-002 — P1：过期/撤销仍有多个可观察结果，首命中无法唯一执行。**
位置：`r7:53–58、65–72`；C-16 §2/§6。
仅有一个已过期授权时，Auth-G 的 live 筛选先使其成为零匹配→`SOURCE_ACCESS_DENIED`；表却规定 grant 过期→`SOURCE_GRANT_EXPIRED`。
存在其他有效 Auth-G、但目标 Secret-G 已过期时，又可能零匹配→REQUIRED；第58行也将 grant 自身过期映射 REQUIRED。撤销同样可能先被 live 筛选吞成 DENIED/REQUIRED。
**最小修复**：明确候选识别、授权有效性校验与 live 筛选的先后；固定 grant expiry、secret_ref expiry、撤销各自检查位置及唯一结果，明确继承或修订 C-16 优先级。不能只声明“首个命中”。

**R7-003 — P1：Auth-G 多匹配与 Host 撤销责任自相矛盾。**
位置：`r7:48、69、73、80`。
错误表规定 Auth-G 多匹配→DENIED，定义却规定多个→允许；两个合法 source-read grant 共存时，缓存请求可成功也可失败。
第73行允许成功后撤销“上一”grant或等待TTL，第80行要求成功/失败/超时后 revoke；撤销对象和完成时限不唯一。
**最小修复**：统一为 Auth-G 存在性规则、Secret-G 唯一性规则，删除错误表中冲突条件；明确每请求 grant 的撤销对象、终止覆盖及 ACK/失败处置，消除“撤销或等TTL”二义性。
缓存条款已明确 capability→binding→Auth-G 后才能返回；按该定义不存在获准绕过授权的缓存路径，但当前冲突文本尚不能提供唯一验收判据。

归档核验：

| 文件 | bytes | SHA-256 |
|---|---:|---|
| r5-review | 9398 | `5cc70d2a9753e8ffecb3e40d00ba53bd6eda1985bb43a07762176266ba1a7657` |
| r6-review | 7821 | `8d47c2b53a67f0138521e6d20050e50f274e68b88db5feb004077032d7147b9b` |

r7 实际仅登记哈希前缀，未给 review 大小；上表补充实测值。r5/r6 报告记载的提案分别9876/6606 bytes，完整指纹均匹配；抽取指纹后至结束复测未变。Git 提交归档仍待 DSH。

实际核验：Git/文件读取/18码集合/指纹已执行；`check.ps1` EXIT 0、PASS（3 warnings）；`verify_pins.ps1` EXIT 0、17/17 PASS。
常规 shell 工具报 Windows error 740，改用 Node 只读文件 API及直接子进程，无提权。
pytest/.NET/build/真实 IPC/DPAPI/迁移实测/竞态/泄漏扫描：**NOT_RUN**。17 pins 不覆盖未提交 r7 或 M2-C1 amendment。

推荐下一步由 **DSH** 处置以上三项契约 P1；本 Reviewer 不参与返修。可直接转发：
> DSH：Task=FEA-09 契约修订；恢复点为上述仓库、main、reviewed_head。请原字节归档本报告，刷新并保留既有变更；仅在登记写域内按 R7-001…003修订提案、同步 impl-design及必要治理记录，不修改生产代码、Schema、依赖、UI、用户数据或历史证据，不 push。交付逐项 disposition、完整指纹及 check/pins结果，Appointment 新上下文只读复核。approved且P0/P1=0后，方按A→B推进提交字节复核与元数据重冻；本建议不释放 I001/I005 实现。