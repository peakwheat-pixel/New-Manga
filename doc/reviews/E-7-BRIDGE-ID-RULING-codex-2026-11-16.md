# E-7 bridge 侧 id 校验裁决 — Codex

- adjudicator: Codex（由 DSH 指派）
- date: 2026-11-16
- subject: HostBridgeClient.ParseResponse 在 expectedId==null 与响应缺失/非数字 id 时的行为
- verdict: 洞 1 保留 raw 原始观察语义；洞 2 改为 fail-closed：生产响应必须携带精确匹配的 Int32 id，否则 MalformedResponse；bridge 立即拒绝并 poison，不新增重同步循环。
- reviewer_kind: agent
- reviewer_source: 本次独立 Codex 会话；未参与被审 head 的实现或返修
- base_commit: 8b4bc274858a15abea87395bb97e895286a7eb64
- reviewed_head: 8b4bc274858a15abea87395bb97e895286a7eb64
- branch / worktree / git_common_dir: main / G:/CODEX/New Manga / G:/CODEX/New Manga/.git
- integration_authority: DSH；本裁决交 DSH 以其名义集成
- scope: 契约解释、代码事实核对与最小实现建议；不是修复批准，不关闭 E-7，不改变 Release Gate

## 1. 分别裁决

### 洞 1：保留 expectedId == null 的现有行为

**保留。** 在生产源码中，不传 expectedId 的唯一调用点是 bridge 的 SendRawAsync（L266–272）；它是 evidence/negative 原始 wire 钩子，不承诺请求/响应配对。它仍须持有传输租约，仍解析 JSON、检查对象根并执行现有 result/error 处理。不得从 raw 请求推断、生成或补填期望 id，也不增加公共 allowMissingId 开关。

这与 [core 侧前次裁决](E7-2-FAILOPEN-RULING-codex-2026-11-16.md) 的入口边界一致。**一致的是“不做关联校验”，不是两种 raw API 的所有返回/异常行为相同。** core raw 返回 CoreResponse、不会因业务错误抛 CoreOperationException；bridge raw 当前会把 error 对象转为 BridgeException，只返回 result 的克隆。本裁决保留这种差异，不将 bridge raw 改成返回完整错误信封。

因此，raw 收到缺失、null、字符串或其它类型的顶层 id 时，不因 id 本身拒绝；若同帧包含 error，仍按现有规则抛 BridgeException。这里不承诺“任何帧都成功返回”，也不承诺 raw 调用后通道一定没有残留帧。诊断应使用独立 client，避免与生产命令共享受污染的会话。

### 洞 2：expectedId != null 时改为 fail-closed

**应改。** 接受生产响应的必要条件是：顶层 id 属性存在、ValueKind 为 Number、TryGetInt32 成功，且实际值与 expectedId 完全相等。缺键、null、字符串（包括数字字符串）、布尔、对象、数组，以及无法解析为 Int32 的数字（如分数或越界数），均抛 SidecarException，Code=SidecarErrorCode.MalformedResponse，Sidecar=SidecarSpec.HostBridgeName。

成功与业务错误信封采用相同关联规则：**先校验 id，再读取 error/result。** 未配对的 error 不能作为本请求的 BridgeException 交给上层。校验的是顶层关联 id；issue 的 result.id 和 resolve/revoke 的 params.id 是资源 grant 字符串，不能被本规则收紧成数字。

理由：

1. 传输独占只证明串行访问，不证明读到的帧属于本次请求。缺失/损坏的 id、重复帧、旧帧或额外输出仍可能被静默交给错误调用方。
2. 当前生产客户端总是生成 Int32 id；服务端正常分派会把请求的顶层 id 原样写回，成功和错误路径一致。未找到有效生产请求必须接受无 id 或字符串 id 响应的兼容依据。
3. 短路链把“没有证据证明属于本请求”当作“没有证据证明不属于本请求”，这是实际生产 fail-open；不能由 raw 例外推导合法性。
4. 第 3 条现有测试明确标成 known limitation，固定的是历史行为，不能作为长期兼容契约或关闭 AC4 的依据。

## 2. 自行复核的事实与依据

以下行号属于 reviewed_head。对表中五个关键源码/测试文件逐一比对 git show HEAD:path，工作区内容与 HEAD 在归一 CRLF 后一致。

| 事实 | 实际仓库依据 | 判断 |
|---|---|---|
| raw 不传 expectedId；生产 SendAsync 传 requestId | [HostBridgeClient.cs](../../apps/desktop-avalonia/src/NewManga.CoreClient/Bridge/HostBridgeClient.cs) L266–297 | 两种入口确实分开；NextRequestId 使用 Interlocked.Increment(ref int)。 |
| 仅可解析 Int32 且值不同才抛错 | 同文件 L319–333 | 不仅非数字被放过，Number 中 TryGetInt32 失败的值也被放过。 |
| id 校验先于业务 error/result | 同文件 L335–346 | 收紧后未配对错误优先成为 MalformedResponse；匹配的业务错误维持 BridgeException。 |
| 正常 wire 明示 int id；分派回显请求 id | [host_bridge.py](../../src/infrastructure/resource_channel/host_bridge.py) L11–14、L150–159 | _dispatch 中 response["id"] = request_id，涵盖成功、typed 错误、参数错误和未知方法返回。 |
| 非法 JSON 可以产生 id:null 错误；raw 请求可携带任意 id | 同文件 L151、L163–177 | 这解释 raw 的观察需求，不证明生产应接受无关联响应。非对象请求还可能令 request.get 失败；本裁决不修服务端输入处理。 |
| 正常循环每个请求发一行，shutdown 发一行后退出 | 同文件 L163–182 | 未见正常业务事件混流或额外事件 emitter。文件头另列 fatal event 形状，不能宣称 bridge 永无事件输出。 |
| 现有三条直接校验测试 | [BridgeResponseIdValidationTests.cs](../../apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Bridge/BridgeResponseIdValidationTests.cs) L18–53 | 第 3 条明确以 expectedId:1 接受无 id 帧，是洞 2，不是洞 1。 |
| raw 业务错误已被集成测试依赖 | [HostBridgeIntegrationTests.cs](../../apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/HostBridgeIntegrationTests.cs) L56–69 | 路径参数走私负例通过 raw 发送 id:99，期望 BridgeException/REF_MALFORMED，应保持。 |
| 当前 core 严格相等、有界重同步、超限 poison | [CoreServiceClient.cs](../../apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs) L2405、L2418–2455、L2476–2499、L2513–2529；另一路生产调用 L703 | BelongsToRequest 已改严格字符串 Ordinal 相等；首帧后最多额外读取 16 次，超限 poison + MalformedResponse。读取超时/取消由传输层 poison。 |
| bridge ParseResponse 抛错后目前不会 poison | HostBridgeClient.cs L292–294；[SidecarProcess.cs](../../apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs) L222–298、L448–461 | ExchangeAsync 返回后才解析；它不会自动捕获 parser 异常。现成 internal Poison 可复用，不需新公共 API。 |
| 原任务允许重同步或 poison，要求避免后续错位 | [PIPE-EXCLUSIVE-TRANSPORT-1](../tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md) AC4/AC5（L64–67）、限定清单 L123–129 | poison 是已有可选契约，不是新增产品能力。 |

[AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md) 的 Host/IPC 边界及 [ADR-0002](../design/ADR-0002_RESOURCE_CHANNEL_SECURITY_V2.md) 的 grant 安全语义继续适用。host_bridge.py 文件头残留 Tauri 描述是历史文字，不改变当前 Avalonia 调用链与产品架构。

[E7-2-FAILCLOSED-1](../tasks/E7-2-FAILCLOSED-1.md) L111 明确排除 bridge；其 L141/L180 把桥侧残余简写为“expectedId==null 时不校验”，**不足以定位真实生产洞**。DSH 集成时应在当前 Task/台账追加澄清：raw 是保留的例外，生产 expectedId 非空时缺失/非法 id 才是待修范围；本次不改历史字节。

另已核对 [E7-2-DYNAMIC-EVIDENCE-1](../tasks/E7-2-DYNAMIC-EVIDENCE-1.md) 的最新 Closeout：两条 core 生产调用链已有重同步成功路径动态证据，但 host-control 无 id 耗尽 poison 等组合仍有缺口。该记录不等于 bridge 已覆盖，也不能用“core 已有两轮复核”替代本次桥侧验证。

## 3. 最小改动方案

只需改 HostBridgeClient.cs 的两个位置；不改 Python Core、wire 形状、Schema、依赖、公开签名或 raw 调用点。

### 3.1 替换 L319–333 的条件链

下列方案把原 15 行替换为 21 行，包含注释、括号与空行；这是一份可审查的小范围方案，不声称是字符数最短写法。

~~~csharp
            // Production responses require the exact Int32 id; raw has no expected id.
            if (expectedId is { } wanted)
            {
                if (!root.TryGetProperty("id", out var actualId))
                {
                    throw new SidecarException(SidecarErrorCode.MalformedResponse, SidecarSpec.HostBridgeName,
                        $"{method}: response is missing id (expected Int32 {wanted})");
                }

                if (actualId.ValueKind != JsonValueKind.Number || !actualId.TryGetInt32(out var actual))
                {
                    throw new SidecarException(SidecarErrorCode.MalformedResponse, SidecarSpec.HostBridgeName,
                        $"{method}: response id is not an Int32 JSON number (expected {wanted}; kind {actualId.ValueKind})");
                }

                if (actual != wanted)
                {
                    throw new SidecarException(SidecarErrorCode.MalformedResponse, SidecarSpec.HostBridgeName,
                        $"{method}: response id {actual} does not match request {wanted}");
                }
            }
~~~

错误消息明确分三类：

| 场景 | 消息关键词 | 含义 |
|---|---|---|
| 缺属性 | response is missing id | 没有提供关联字段。 |
| 类型/数值表示非法 | response id is not an Int32 JSON number | 提供了字段，但不能用于本客户端的 Int32 关联。保留 expected 与 kind；不插入原始对象、整帧或资源路径。 |
| 合法 Int32 但值不同 | response id X does not match request Y | 已提供可比较 id，但不匹配；不武断宣称一定是“另一个命令的响应”。 |

三类一律使用 MalformedResponse，不新增业务错误码，不改成 REF_MALFORMED。数值转换范围以 Number + TryGetInt32 为准，不用字符串解析、浮点截断、强制转换或补填期望值。

### 3.2 在生产 SendAsync 的 L294 加清洁失败出口

保留 L292 的 using var lease 与 L293 的 ExchangeAsync，**仅用以下 9 行替换 L294 原 1 行**：

~~~csharp
        try
        {
            return ParseResponse(method, frame.ResponseLine, requestId);
        }
        catch (SidecarException ex) when (ex.Code == SidecarErrorCode.MalformedResponse)
        {
            _process.Poison();
            throw;
        }
~~~

该 catch 在租约释放前执行，因此排队中的下一请求不能在 poison 前写入。静态 parser 只负责判定并抛错，持有 process 的生产调用点负责禁用通道；不能只改 parser 就宣布会话安全。

这个出口同时覆盖该生产 parser 已有的 invalid JSON、非对象根和数字 id 错配 MalformedResponse；这些也无法证明流处于可复用状态。匹配 id 的正常 BridgeException 不进入此 catch，继续保留可用会话。raw 不套用这段新 catch，保持原始行为与既有租约。

启动握手的外层 StartAsync 已将 MalformedResponse 包装为 HandshakeFailed 并 Dispose（L119–139）；因此“生产非法 id 抛 MalformedResponse”指 parser/已启动命令层，**不要求更改现有启动错误分类**。启动负例应断言 HandshakeFailed，并检查其内层 MalformedResponse。

**源码规模：原 16 行替换为 30 行，净增 14 行；限一个文件、两个位置，不含测试。** 其中 parser 单独净增 6 行；只做这一半不能解决错误后继续复用管道的问题。

## 4. 三条既有测试的影响与迁移

| 现有测试 | 新规则下结果 | 应如何处理 |
|---|---|---|
| MismatchedNumericId_ThrowsMalformedResponse（L19–29） | 继续通过 | 保留错误码与实际/期望 id 断言；可加 does not match 消息分类断言。 |
| MatchingNumericId_IsAccepted（L32–39） | 继续通过 | 保留；宜再断言 result.ok 为 true。 |
| MissingId_CurrentlyFailsOpen_DocumentedLimitation（L46–53） | **必然被破坏：由成功返回变为 SidecarException** | 改名为 MissingId_ThrowsMalformedResponse，断言 Code=MalformedResponse、消息含 missing id 和期望 1；移除“仍接受”的历史限制断言与过时注释。不能删除测试、加 skip 或改成 expectedId:null 来掩盖生产变化。 |

指定类确实只有上述 3 条；同文件 L61 起另有 RawSendPipeExclusivityTests 的一条 core 并发 SidecarFact，它测 core raw 与生产命令独占，不因桥侧 parser 收紧而需要迁移。

实施时还须覆盖以下必要边界；这是 planned，不是本次已运行结果：

- 参数化 id 为缺键、null、字符串 "1"、布尔、对象、数组、分数、超出 Int32 范围；同时覆盖 result 与 error 信封，确保都先触发 MalformedResponse。
- expectedId:null 时的 raw 解析边界：无/非法 id 的合法 result 仍可观察；包含 error 的响应仍按现有语义成为 BridgeException。用单独测试证明洞 1 保留，不能拿它替换洞 2 的生产断言。
- 匹配 id 的业务错误继续抛原 BridgeException；随后正常命令仍能成功，证明没有错误地 poison 业务失败。
- 在真正的 HostBridgeClient.StartAsync → public PingAsync/IssueAsync 链上，先通过正确握手，再注入无/非法/错 id 的帧：当前调用立即 MalformedResponse；即使后面紧跟正确 id 帧也不重同步成功；下一调用在写请求之前因 poisoned/restart required 失败。检查 fake server 收到的请求数，不能仅匹配消息中的 poisoned 一词。
- 握手本身收到非法 id 时，验证外层 HandshakeFailed 与内层 MalformedResponse；保持 bridge 并发独占和正常 grant 生命周期回归。

当前 Poison 快速失败的 Code 是 RequestTimeout，消息含 restart required（SidecarProcess.cs L453–461），不是首个协议错误的 MalformedResponse。新测试须准确区分两次调用的码，不能只断言宽泛异常类型。可用无等待的双帧注入与请求计数同步，避免依赖固定 sleep。

既有 HostBridgeIntegrationTests 的 raw 路径走私负例不应被破坏。其余合法服务端响应因回显相同 id，预计保持；这个兼容结论来自源码，尚未用全部发布二进制实测。Bridge fake 不能直接假定 core fake 的 Python 启动参数可复用：当前 HostBridgeOptions 只暴露 ExecutablePath，没有 Arguments。DSH 应冻结能通过现有启动方式运行的测试夹具方案，不为测试扩大生产公共 API。

## 5. 与 core 对称性及恢复策略

**共享接受原则，分别选择恢复策略。** 数字 id 和字符串 id 都可以严格比较、也都能用于重同步；“数字”本身不是 bridge 不重同步的理由。区别在帧模型、已有实现及此切片范围。

| 方面 | core 当前实现 | 本次 bridge 裁决 |
|---|---|---|
| 接受生产响应 | 精确匹配字符串 request_id | 精确匹配 Int32 顶层 id |
| raw | 不做生产配对 | 同样不做生产配对，保留既有 bridge 错误语义 |
| 正常事件 | 需要跳过同流事件 | 正常服务循环未见事件混流，不新增事件跳过逻辑 |
| 缺失/非法/错配关联 | 现有有界读取寻找匹配帧，超限或读取超时后 poison | 首帧立即拒绝，租约内 poison；不尝试读取后帧 |
| 对外错误 | 重同步超限 MalformedResponse；读取超时 RequestTimeout | 首次协议拒绝 MalformedResponse；后续 poisoned 快速失败沿用现有码 |

core 的思路技术上可适配 bridge，但不应直接移植其 CoreProtocol.Parse/CoreResponse/事件分类 helper：它们的信封和字段不同。本次增加 bridge 重同步会增加预算、超时、事件识别与多帧测试范围，缺乏必须容忍正常额外帧的证据，故选择原 AC5 已允许的 poison 方案。

**不接受“只抛错、不 poison、随后继续复用”。** 流可能是“错/坏 id 帧 → 本次正确响应”；若释放租约后继续下一命令，会把残留正确响应读给下一次调用。无业务事件并不能排除重复输出或其它残帧。poison 后不再读写该会话，关闭并由生命周期层重建，才能把这一风险隔离。

host_bridge.py L14 文档列有无 id 的 fatal event（随后退出）；本次检查未在正常 serve_forever 找到对应发射分支。即便遇到这种帧，生产也不得当作合法响应或可跳过事件继续等待；本策略拒绝并 poison，实际先遇 EOF 时沿现有 ProcessExited 路径。未来若正式增加业务事件，必须另行冻结帧分类及恢复契约。

## 6. 残余风险与关闭边界

1. **正确 id 不证明 payload 正确，也不保证只执行一次。** 仍可能有带正确 id 的错数据、重放；int 计数器长期溢出后重用亦未解决。id 校验不是认证或幂等机制，失败时不得自动重发 issue/revoke 等命令。
2. **重启有业务代价。** poison 只设置标志，不自动关闭/重建进程；现有 _service 保存内存 grant。重建 bridge 会失去旧 grant，需要生命周期层失效旧句柄、按既有授权重新签发；不能把目录数据等同于可恢复全部内存 grant，也不能据此删除用户文件或数据库保护状态。
3. **poison 后错误归因粗糙。** 当前统一返回 RequestTimeout，消息仍称 timeout/cancellation，不能准确说明首次为协议 id 违约。保留初次异常和诊断；本次不扩大成错误码体系改造。
4. **信封与 DTO 校验仍不完整。** 重复 JSON 属性、result/error 互斥、错误对象形状、必要业务字段及 ReadString/ReadLong 的空串/0 回退不在本修复内。匹配 id 也不能替代 grant 身份、大小、摘要、containment 与授权生命周期校验。
5. **raw 保留未配对风险。** 它只读首帧，不保证跳过事件，不会因本次新规则 poison；恶意/异常输出可能留下帧。当前搜索 Avalonia 源码/测试/tools，实际 raw 调用在测试；公开 API 未来被误用于生产仍是风险，需守住入口用途。
6. **生命周期与传输边界仍独立。** Dispose/停止与在途调用的协调、程序集内绕过租约的可能性、无界 JSON 行、写阶段取消/阻塞均非本裁决覆盖面。不得据此宣布全通道安全。
7. **可用性与包兼容待验。** bridge 选择立即停止会放弃“坏帧之后仍有正确帧”的可恢复机会；这是保护响应归属的明确取舍。所有受支持旧包未做 wire 矩阵，若发现有效 Int32 请求正常返回无/非法 id，应先固定版本及 wire 证据交 DSH 裁决，不能暗中恢复 fail-open。
8. **测试证据仍待实施。** parser 单测不能证明生产调用点 poison 接线；core 剩余组合测试也不因此消失。未完成桥侧修复、真实调用链判别测试、上下文独立 Review 与 DSH 集成验证前，E-7 #2 整项继续开放。

Architecture 判断：raw 与生产关联规则分别落实在明确入口，桥侧以立即拒绝 + poison 达到与 core 相同的归属底线，符合现有 AC5 的恢复选项。Verification 判断：源码与测试断言支持上述静态结论；任何新行为的产品测试结果均为 NOT_RUN，不能据此批准未实现补丁。按协作协议 §4.4，DSH 冻结实施范围前须确认影响边界；实施核验若发现合法生产兼容反例，暂停集成并重新裁决。

## 7. 本次核验与写入边界

- 开始时 main/HEAD 与委托一致，git common directory=.git。git status --short 的 stdout 为空，但 stderr 报旧 .workspace fixture/host 目录 Permission denied，因此只确认已跟踪 diff 干净，不声称对不可读目录完成全面 untracked 核查。
- exec_command 启动器返回 Windows 740（需提升），未执行其命令；随后改用本地 Node 文件读取和 child_process.execFile 的结构化参数调用 git/rg/pwsh 完成只读检查，未提升权限。
- 治理检查：pwsh -NoProfile -File tools/governance/check.ps1，EXIT=0，Governance scope=15 current documents，PASS (3 warnings)。它不验证本裁决语义或未实现代码，不代替 DSH 授权；检查结果在交付时复核。
- 构建、dotnet/pytest、fake sidecar、变异测试、真实包兼容矩阵：NOT_RUN。为遵守本轮只读范围，不运行可能生成 build/fixture/日志文件的产品测试。
- 本次唯一允许新增的是本裁决文件。未修改生产源码、既有测试、Task/STATUS/PLAN、历史 Review/manifest/pin；未执行 git add/commit；最终核对见文末交付核验。

## 8. 推荐下一步与可转发指令

**下一接收者：DSH。** 先以 DSH 名义集成本裁决，再冻结建议 Task **E7-BRIDGE-ID-FAILCLOSED-1**（建议 ID，尚未释放）。推荐 Owner=DSH；Review 由 DSH 任命未参与实现/返修的独立上下文 Codex 或 ZCode。当前 MAINT-1 仍 in_progress，Release Gate 仍 BLOCKED；本报告不释放实现任务，也不更改现有卡状态。

- 启动条件/依赖：本裁决获 DSH 采纳，MAINT-1 下桥侧范围完成登记；core 的 E7-2-FAILCLOSED-1 已完成，但其剩余测试不能冒充桥侧证据。
- Recovery point：G:/CODEX/New Manga，main，base/head=8b4bc274858a15abea87395bb97e895286a7eb64；集成本报告后由 DSH 重新固定实现 head。独立 worktree 待 DSH 创建，不在本轮创建。
- Scope：允许 HostBridgeClient.cs、BridgeResponseIdValidationTests.cs、DSH 明确命名的 bridge fake/调用链测试、当前 Task/Handoff/verification。禁止顺带改 core 关联策略、Python 服务端、Schema/依赖、raw 行为及冻结历史证据；不需新增共享 wire/API。
- Deliverables：严格 id 判据、生产 MalformedResponse → 租约内 poison、旧测试迁移、raw/业务错误边界测试、真实 bridge 调用链判别证据、Handoff；失败/skip/NOT_RUN 必须如实记录。
- Verification：以下为计划命令，未在本轮执行；新 fake 类名须由 Task 固定并加入过滤器。完成上下文独立 Review、DSH 集成验证及当前门禁后，才可判定桥侧切片完成；整项 E-7 另按全部残余验收。

~~~powershell
dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --filter 'FullyQualifiedName~BridgeResponseIdValidationTests|FullyQualifiedName~HostBridgeIntegrationTests|FullyQualifiedName~BridgePipeExclusivityTests'
dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj
pwsh -NoProfile -File tools/governance/check.ps1
# DSH 创建 Task 后再执行其 -TaskPath 检查，及按 Task 固定的 pins/inventory 门禁。
~~~

可直接转发：

> DSH：请以你的名义集成 doc/reviews/E-7-BRIDGE-ID-RULING-codex-2026-11-16.md，按该裁决冻结建议 Task E7-BRIDGE-ID-FAILCLOSED-1（未释放）。恢复点 G:/CODEX/New Manga、main、base/head 8b4bc274858a15abea87395bb97e895286a7eb64；集成后重新固定 head，独立 worktree 待你创建。建议你承担 Owner，并另任独立上下文 Codex/ZCode Review。写域仅 HostBridgeClient.cs、上述 bridge 测试与明确命名的 fake/调用链测试、Task/Handoff/verification；不改 Python Core、Schema、依赖、core 策略、raw 语义或历史冻结证据。交付必须包含 expectedId 非空时缺失/非法/错配顶层 Int32 id 全部 MalformedResponse，生产调用在租约内 poison，禁止随后继续复用；保留 expectedId:null 的 raw 行为。迁移第 3 条旧 fail-open 单测，补成功/错误信封非法 id、raw 保留、匹配业务错误仍可复用、真实 StartAsync 后故障及后续零写入的判别证据。按本报告定向测试、CoreClient 全量、必要 Host 回归、check/-TaskPath/pins/inventory 验证并写 Handoff；未跑/失败/skip 明示。上下文独立 Review 与你的集成验证通过后再关闭桥侧切片，E-7 #2 整项须继续核对 core 其余组合测试，不能仅凭本裁决关闭。

## 9. 交付核验

- 写入后复查 HEAD=8b4bc274858a15abea87395bb97e895286a7eb64，未变化；git diff --name-only 与 git diff --cached --name-only 均为空。
- git status --short 唯一可见项为 ?? doc/reviews/E-7-BRIDGE-ID-RULING-codex-2026-11-16.md；仍有 62 行旧 fixture 目录不可读警告，不对这些目录作全面清洁声明。
- 最终治理检查 EXIT=0，PASS (3 warnings)：11 张非终态卡提示、STATUS 预算 80% 提示、PLAN 预算 80% 提示。没有新增门禁失败。
- 本报告 12 个本地 Markdown 引用均存在，3 段代码围栏成对闭合；建议源码两段的替换行数为 21 + 9，原行为 15 + 1，净增 14。
- 未执行 git add/commit；产品源码/测试未改，产品测试与修复验证维持 NOT_RUN。报告落盘不表示实现任务已获释放或缺陷已关闭。
