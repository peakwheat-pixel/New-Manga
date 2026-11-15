# E-7 #2（fail-open）裁决 — Codex

- adjudicator: Codex（由 DSH 指派）
- date: 2026-11-16
- subject: 响应缺少 request_id 时应 fail-open 还是 fail-closed
- verdict: 条件化：生产路径改为 fail-closed；SendRawAsync 保留原始 wire 观察语义，不新增允许无 id 开关。
- reviewer_kind: agent
- reviewer_source: 本次独立 Codex 会话；未参与本次被核对修复的实现或返修
- base_commit: 2bcb58fa7f78e742b30d25555dd8811d5e20a9ec
- reviewed_head: 2bcb58fa7f78e742b30d25555dd8811d5e20a9ec
- branch / worktree: main / G:/CODEX/New Manga
- integration_authority: DSH；本文件交 DSH 以其名义集成
- scope: 契约裁决与最小方案；不批准现有实现、不关闭 E-7、不改变 Release Gate

## 1. 裁决规则

**生产请求只有收到与本次 request_id 精确相等的字符串 id，才可接受该帧为响应。** 缺键、JSON null、数字、布尔、对象、数组，以及不匹配的字符串，均不能证明归属；成功与错误响应采用同一规则。匹配使用 Ordinal，不做类型转换、大小写折叠或补填本次 id。

事件帧继续按事件规则跳过。缺少 id 的非事件帧可按 R002 的既有预算丢弃并继续寻找精确匹配帧；预算耗尽或等待超时后停止使用通道。这里的 fail-closed 指“不得把未配对帧返回给业务层”，不要求第一帧无 id 就立即抛错。

**SendRawAsync 是明确的例外边界：它返回所读原始帧的解析结果，不承诺请求/响应配对。** 保留其不自动生成/修补 id、不因 Core 业务错误而抛出 CoreOperationException 的现状。它仍必须持有传输租约，畸形 JSON 响应仍可导致解析异常。不得把 raw 的例外传播到 SendAsync 或 SendHostControlAsync。

不新增公共 allowMissingRequestId 布尔开关：raw 已是独立入口，生产入口无此选择。若未来需要可配对的 raw 工具，应另设明确的测试接口及范围，而非放宽生产默认值。

## 2. 自行复核的事实与证据

本次通过本地文件读取、rg、git 只读命令及 Python ast.parse 静态检查复核；未运行应用、构建或产品测试。开始时 git status --short 为空，HEAD 与委托一致，Git common directory 为 .git。以下行号均属于 reviewed_head。

| 事实 | 仓库证据 | 判断 |
|---|---|---|
| 两条生产发送路径都调用 ReadResponseForRequestAsync，并在整个交换与后续读取期间持传输租约 | [CoreServiceClient.cs](../../apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs)，L669–710、L2486–2506 | SendAsync 生成 req-{n}；SendHostControlAsync 实际生成 hostctl-{n}，两者都是非空字符串。委托摘要把后者也称为 req-{n}，仅前缀需更正。 |
| 生产配对判据将 RequestId=null 视为属于当前请求 | 同文件 L2418–2463 | fail-open 确实位于生产路径。 |
| EnsureResponseBelongsToRequest 同样放过 null，但已无生产调用 | 同文件 L2465–2477；对 apps/desktop-avalonia/src 和对应测试目录搜索调用点 | 它只有定义与 3 个测试调用；只改这个方法不能修生产行为。 |
| 缺键、非字符串、JSON null 都解析为 RequestId=null | [CoreProtocol.cs](../../apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs)，L52–89 | 不应只修“缺键”而遗漏错误类型。 |
| 已识别的事件帧在归属判据前被守卫排除 | CoreProtocol.cs L47–49；CoreServiceClient.cs L2433–2440 | 事件无 id 不能作为生产响应 fail-open 的理由。当前事件识别仍有局限，见残余风险。 |
| raw 独立取租约、直接解析首帧，不调用生产配对 helper | CoreServiceClient.cs L2380–2398 | 生产收紧不必改变 raw 的解析语义。 |
| SendRawAsync 的调用者只在测试中 | rg -n SendRawAsync apps src tests tools | CoreClient 调用为 CoreServiceIntegrationTests、BridgeResponseIdValidationTests 中的测试；另有独立 HostBridgeClient raw 钩子及测试。未找到生产调用者。 |
| Core 的响应构造包含 id 键，非法输入可以产生无可关联 id 的响应 | [core_service.py](../../src/bootstrap/core_service.py)，L1363–1373、L6870–6911、L6998–7004、L8282–8307、L8311–8365、L8368–8388 | 非法 JSON / 非对象请求明确返回 request_id:null；HostControl / 创建命令等对非字符串 id 也可返回 null。 |
| Core 事件有意不带 request_id，输出完整行有写锁 | core_service.py L1618–1641、L8412–8415 | 应区分 Event 和 Response。 |

静态补充：对 core_service.py 的 AST 中同时含 protocol 与 result/error 的响应信封字典逐一检查，共 **70 处，缺 request_id 键为 0**。id 表达式分布为：直接 request_id 52、字符串检查后否则 None 5、safe_request_id 10、固定 None 2、request.get('request_id') 1。此检查覆盖字典字面量，不能证明任意未来动态分支或已打包二进制的行为。

safe_request_id 的 settings/cleanup 投影会净化路径形状字符串（L769–788、L6915–6928）；生产自动生成的 req-{n} 不匹配该路径规则。不能把“Core 所有响应的 id 永远是字符串”当作事实，但也未发现正常生产请求必须接受无 id 响应的兼容需求。

相关任务已核对：[PIPE-EXCLUSIVE-TRANSPORT-1](../tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md) AC4 与 L123–129；[R002-RESYNC-1](../tasks/R002-RESYNC-1.md) 设计与 Closeout；[E7-1-UNIFY-LEASE-1](../tasks/E7-1-UNIFY-LEASE-1.md) Closeout。旧报告中的“_pipeGate 尚未统一”等描述保留为历史，不能覆盖本 head 的代码事实。

## 3. 理由：独占降低发生概率，不能替代配对证明

独占证明“现有调用方不会同时读写同一条管道”，并不证明“下一条 stdout 行就是本次响应”。因此风险不只剩“Core 返回了别人的响应”：

1. **本请求自己的响应丢失或改变 id。** payload 可能仍正确，但协议已违约。fail-open 会把违约伪装成正常成功，隐藏 Core bug 或不兼容演进；未知错误帧也可能被归给本请求。
2. **旧帧、重复帧、额外帧或未识别通知。** Core 的重复输出、意外协议行、此前未被正确收尾的读取，都可能留下帧。已修的取消 poison 与租约降低部分来源，不构成所有来源的排除证明。它们也不必属于另一个并发请求。
3. **绕过重同步。** 当前流若为“错 id → 无 id 非事件帧 → 正确 id”，R002 会在无 id 帧提前成功返回，真正响应留在流内。后续行为未必永久失步，但当前请求已得到未经验证的结果，R002 的配对目标被绕过。
4. **误导业务状态。** 可解析的无 id 对象可被上层当成成功数据或业务错误。即使部分 DTO 检查会拒绝形状，也不能依赖所有消费者都能识别错误归属；配对必须先于业务解析。

本次未复现这些异常输出，以上是由代码可达路径推导的风险，不声称正常 Core 已在生产中触发。

fail-closed 把无法证明的成功转为可诊断的传输失败，代价是异常 Core 的可用性降低。这一取舍符合 R002 已采用的“寻找匹配帧，无法配对则 poison”的规则。稳定协议不应把移除关联字段当作可静默兼容的演进。

## 4. 兼容性与契约解释

[Typed IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §3 的通用 envelope **仍标 PROPOSAL**，不能把整节冒称为全部已冻结。不过：

- §3 的 Response 表达为 request_id: OpaqueId，§3.1 定义非空字符串；§4 说明它用于单次请求/响应关联。
- 冻结的 §5.7 HostControlResponse 明确引用 Response；冻结的 §5.10 创建响应同样携带 request_id。
- §6.2（L1126）明确以 request_id 配对 Response，以 event_id 识别 Event。
- 现有 Task AC4 已要求默认 fail-closed，E7-1 又明确把 #2 留作契约决策；这不是从“已知限制”测试反推一个长期兼容承诺。

据此，本裁决明确本 head 的客户端接受策略：正常生产请求无 id 响应不属于合法兼容面。无需为本次收紧修改 Python wire 形状、Schema、依赖或协议版本；它拒绝的是当前生成请求不应收到的未配对响应。若另有受支持旧包确实对有效字符串 id 返回无 id 的最终响应，DSH 应以精确版本和 wire 证据单独裁决，不能通过通用 fail-open 暗中支持。

**Core 会不会真的输出“没 id”的帧？会，但必须区分：**

- 合法 Event 确实省略键，仍应跳过。
- 非法 JSON、非对象及某些无有效 id 的请求会收到 request_id:null 错误信封。这是 raw/负向诊断需要观察的输出。
- 本次未发现有效生产请求正常返回时省略键或将其置 null 的代码依据。L2459“the frozen core omits it on some frames”注释没有给出生产最终响应的实例，不能用事件或 raw 错误来证明它。

若把严格校验放进 CoreProtocol.Parse，可能破坏上述事件解析和 raw 错误观察；**本裁决不采用这种改法**。只收紧生产归属判据，raw 保持原样，现有 raw 负向测试无需因此改成生产异常断言。

## 5. 最小改动方案（供 DSH 冻结实现范围）

### 5.1 生产判据与现有重同步

改 CoreServiceClient.cs 的 BelongsToRequest 为：

~~~csharp
private static bool BelongsToRequest(CoreResponse response, string requestId) =>
    response.RequestId is { } actual
    && string.Equals(actual, requestId, StringComparison.Ordinal);
~~~

ReadResponseForRequestAsync 保留现有事件守卫、16 次额外读取预算、租约范围及 drain/poison 路径。null 和错误类型 id 将自然进入“不属于本次请求”的分支，而不是被返回。空字符串也无法匹配生产生成的非空 id。

EnsureResponseBelongsToRequest 若保留，应复用同一严格谓词：

~~~csharp
if (!BelongsToRequest(response, requestId))
{
    // throw SidecarException(SidecarErrorCode.MalformedResponse, ...)
}
~~~

调整错误消息以区分“缺失/非字符串”与“字符串不匹配”，不要无证据断言“必然是另一个命令的响应”。同步修正 L2459–2460 注释。另一可接受做法是删除这个无生产调用的 helper 并迁移对应测试；最小方案优先保留、共享谓词，避免扩大删除范围。

**不能只改 Ensure，也不能只改 Parse。** 不给 SendRawAsync 加允许无 id 开关，不改其直接解析逻辑，不为本切片增加新公开 API。

### 5.2 错误码与通道状态

复用现有 SidecarErrorCode，无需新增枚举或 Core 业务错误码：

| 场景 | 本方案要求 |
|---|---|
| 前帧无/非法 id，预算内找到精确匹配帧 | 返回匹配帧；不得返回前帧，不 poison。 |
| 额外读取预算耗尽 | poison + MalformedResponse，沿用现有重同步失败出口。 |
| 等待匹配帧时读取超时 | 传输层 poison + RequestTimeout，沿用现状。 |
| 等待期间调用方取消 | poison + 原 OperationCanceledException。 |
| Ensure 单独校验无/非法 id | MalformedResponse；它本身不持通道，不声称已 poison。 |
| poison 后再次调用 | 当前实现仍为 RequestTimeout + restart required；错误归因不精确，登记为残余。 |

因此，“只回一帧无 id，随后静默”的 Core 通常会等待到读取超时，得到 RequestTimeout，**不保证每次无 id 都立即得到 MalformedResponse**。这是最小复用方案的明确行为。如果 DSH 另选无 id 立即拒绝策略，必须同时 poison，不能仅抛错后继续复用可能仍有残留的会话；那是另一项接受策略，应重新冻结并测试。

预算维持“首帧 + 最多 16 次额外读取”的当前实际边界，不在本切片调整事件预算或计时器。

### 5.3 测试迁移与成本

必须同时迁移两处旧断言：

- [PipeResponsePairingValidationTests.cs](../../apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingValidationTests.cs) L52–65：MissingRequestId_CurrentlyFailsOpen_DocumentedLimitation 改为严格拒绝；保留匹配/不匹配测试。
- [R002ResyncTests.cs](../../apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/R002ResyncTests.cs) L97–116：ResponseWithoutRequestId_IsAcceptedWithoutDraining 改为“无 id 后继续读取，返回匹配帧”。

新增或参数化覆盖缺键、null、数字/布尔/对象/数组、空字符串；至少验证“坏帧 → 匹配”“错 id → 无 id → 匹配”“无匹配至预算耗尽并 poison”“事件混排”。原有错 id 重同步测试不能弱化。

另需在真正的 SendAsync 与 SendHostControlAsync 路径各有确定性假 sidecar/等价调用链测试，覆盖握手后注入坏帧与正常匹配帧，证明生产调用点使用严格 helper；仅测无生产调用的 Ensure 不足。raw 应验证 idless/非法请求错误仍可观察，测试用独立 client，不能假定 raw 后会话一定清洁。

成本评估：**生产源码改动小、测试迁移中等、数据迁移为零。** 主体只需改一个文件内的谓词、校验与注释；解析器、Core、共享 wire、Schema、依赖和 raw 签名均可保持。测试成本主要在两条真实生产调用链的夹具覆盖，而非一行谓词。现有测试全绿数字属于旧实现证据；本裁决未运行测试，不把任何新行为记为 PASS。

## 6. “已知限制”测试是否足够

**不足以作为长期保留 fail-open 或关闭 E-7 #2 的依据。** 它准确记录历史行为，但不证明行为符合契约；而且当前该测试只调用已无生产调用的 Ensure。R002 的第二条接受测试虽覆盖实际 helper，仍只是把现状固化，没有给出合法无 id 最终响应的兼容证据。

DSH 集成本裁决后，应在当前 Task/缺陷台账追加决定与实现任务指针，保留冻结历史 Review、日志、manifest 和 pin 原字节；不得把旧文件中的 fail-open 已知限制改写成“原本已合规”。新版测试与说明通过新提交记录策略变化。

在实现、独立上下文 Review、DSH 集成验证完成前，#2 保持开放；这份裁决完成只代表决策问题已回答。

## 7. 残余风险与关闭边界

1. **正确 id 不能证明 payload 正确或请求只执行一次。** Core 可回错数据却带对 id；计数器重用、重放等也非本判据能充分解决。契约明示 request_id 不是幂等键；写操作在响应失败前可能已提交，不能据 fail-closed 自动重试。
2. **事件识别仍按字符串包含关系。** 嵌套 payload 中出现 event_type/request_id、转义后的属性名、异常事件形状，都可能误分类。严格 id 只能减少误接受，不能替代结构化帧分类。
3. **Parse 仍宽松。** protocol/version、result/error 互斥、重复 JSON 属性等未被本方案完整校验；不可解析帧当前直接抛出且不保证 poison。本方案不宣称修复所有残留帧来源。
4. **预算及恢复限制。** 事件与坏帧共用 16 次额外读取；每次 ReadNextResponseLineAsync 重新设置 timeout，整次调用可超过一次 RequestTimeout；poison 后无自动恢复且错误码归因粗糙。
5. **租约仍依赖调用纪律。** internal 阻止程序集外直接 Exchange，但不强制同程序集调用者持租约；ReadNextResponseLineAsync 仍 public。未来绕过、重入与生命周期协调仍须分别审查，不能据本裁决宣布全局并发安全。
6. **raw 是显式未配对观察口。** 它只读首帧，未跳过事件，也未校验自带 id；异常输入或多帧输出可能污染后续读取。仅测试使用与独立 client 隔离降低影响，不构成生产配对保证。
7. **HostBridgeClient 的 id 漏洞仍独立存在。** ParseResponse L322–326 只在可解析为 Int32 的 Number 且不相等时拒绝；缺键、null、字符串、越界数字仍绕过。其协议字段是 id，不是 request_id，且是独立进程/管道。要关闭权威清单整项 #2，DSH 还须冻结并实现桥侧规则：有 expectedId 的生产响应必须是精确匹配的 Int32 id，否则 typed 拒绝并保证通道不会以未定义状态继续复用；raw 例外另行保留。不能仅修 core 后宣布整项关闭。
8. **二进制兼容面未实测。** 本裁决针对固定源码 head，没有对所有旧 sidecar 包做 wire 矩阵验证；不能把源码静态结论当作发布包验证。

Architecture 判断：条件化收紧保持协议解析、传输独占、生产关联与 raw 诊断的边界，适合本次问题。Verification 判断：代码和静态检查支持裁决；修复测试、包兼容测试与集成验证均为 NOT_RUN。

## 8. 推荐下一步与可转发指令

**下一接收者：DSH。** 先集成本裁决，按 MAINT-1-RELEASE-MONITOR 下的 E-7 #2 残余冻结后续实现 Task；建议 ID E7-2-FAILCLOSED-1（建议，尚未释放）。实现 Owner 建议 DSH；由另一个独立 Codex 会话或 DSH 任命的独立上下文 Reviewer 审查，本裁决会话不参与返修。

Recovery point：G:/CODEX/New Manga，main；base/head 均为 2bcb58fa7f78e742b30d25555dd8811d5e20a9ec。若集成本报告导致 head 前移，DSH 需重新固定实现基线；linked worktree 待 DSH 创建。

可直接转发：

> DSH：请集成 doc/reviews/E7-2-FAILOPEN-RULING-codex-2026-11-16.md，以其条件化 verdict 冻结建议 Task E7-2-FAILCLOSED-1。恢复点为 G:/CODEX/New Manga、main、base/head 2bcb58fa7f78e742b30d25555dd8811d5e20a9ec；集成后重新固定基线，worktree 待你创建。允许路径建议仅 CoreServiceClient.cs、对应 CoreClient 测试及本 Task/Handoff/verification 文档；若要同卡处理 HostBridgeClient.cs，先明确增加桥侧范围与清洁失败策略。禁止改 Python Core、CoreProtocol.Parse 的宽松 raw 语义、Schema、依赖和历史冻结证据；无需新增公共允许无 id 开关。交付严格生产配对、raw 保留、两处旧测试迁移、两条真实生产调用链判别证据及 Handoff。验证命令：dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --filter "FullyQualifiedName~PipeResponsePairingValidationTests|FullyQualifiedName~R002ResyncTests"，再跑同项目全量与 raw/生产调用链定向用例；按范围补 Host 回归。check.ps1、pins 与 inventory 门禁按 Task 执行。逐项记录环境、失败、skip 和 NOT_RUN；上下文独立 Review 与你的集成验证通过后才能关闭相应范围。未补桥侧严格 id 判据时，权威 E-7 #2 整项不得标已关闭。

本建议不释放实现任务，也不代替 DSH 的范围冻结、Appointment 或 Gate 判定。

## 9. 本次交付核验

- 只读治理检查：pwsh -NoProfile -File tools/governance/check.ps1，EXIT=0，PASS (3 warnings)。检查范围为当前 15 份文档；不代表语义裁决或实现验证通过。
- 产品构建、产品测试、sidecar 运行与旧包兼容矩阵：NOT_RUN。
- 本次仅新增本裁决文件；tracked diff 与 staged diff 均为空；未执行 git add/commit；HEAD 保持 reviewed_head。
