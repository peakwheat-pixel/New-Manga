# AUDIT-05/06：SFX 与 AI 翻译专项阶段报告

**Codex adjudication（2026-11-13，独立上下文）：** 本报告中的 `REVIEW_PENDING` 候选已由 Codex 最终独立 Review 裁决（首轮 `reviewed_head=d92859c9ac8a4d3122d6cabfe4d44af980574104`，复审 `226eb048006ffa804ebefd9f98e51bbc13793f31`；结论 REJECT 属交付文档返修，不改变产品 Gate）。现行状态以 `reports/11_ISSUES.md` 与 `AUDIT_ISSUES.md` 为准；本报告原观察与限制保持原字节语义。 本报告中的 `AUDIT-05-CAND-001`、`AUDIT-06-CAND-001/002` 均被裁为 **INVESTIGATE**。

**结论：AUDIT-05 `PARTIAL`；AUDIT-06 `PARTIAL`。** 已核对当前生产 Core 的契约、provider、pipeline 与人工修改保护路径，并执行纯合成的定向测试。此报告不代表全审 PASS；阶段快照中的“待独立复核/候选裁决”已由 Codex 四轮 Review 完成（见 CODEX-* 报告与 11_ISSUES.md）。

- 产品基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
- 本轮测试生成 HEAD：`d96529ebff6cf752ad64a676d05ec622da09e565`
- 产品源码/原有测试与产品基线的路径差异：`src/`、`apps/desktop-avalonia/`、`tests/` 均为空；本轮新增测试仅在 `audit/V1-FULL-AUDIT/tests/`。
- 独立复核（阶段快照）：原计划 ZCode fresh context；2026-11-13 已由 Codex 三轮 Review 裁决（见 CODEX-* 报告）；作者未自审。

## 范围与方法

依据原始审计清单 AUDIT-05/06、`doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md` §4/§7.2、SFX 策略/语义/重叠仲裁 Task，以及当前 `src/` 与 `tests/`。没有读取真实漫画图像、数据库或权重，没有调用付费 API、没有启动 UI。

| 测试批次 | 覆盖 | 结果 |
|---|---|---|
| `audit05-06-targeted-20261113` | 独立 SFX 合成检查；检测、SFX 策略端到端 Mock、Region 重类型/重检测、单 Region 翻译、pipeline 状态/恢复、响应映射与重试 | 247 passed，3 deselected，EXIT 0；明确排除名称含 `real_weights` 的测试。生成时点 `2026-11-12T18:43:21.132531+00:00`，HEAD=`d96529e`。 |
| `audit06-context-20261113` | 生产 SQLite 上下文冻结隔离、provider 请求形状、生产 handler seam、Mock transport、响应协议与重试 | 84 passed，EXIT 0。生成时点 `2026-11-12T18:43:21.132829+00:00`，HEAD=`d96529e`。 |

完整命令、解释器、cwd、生成 HEAD、UTC 和 EXIT 分别见两批 log 与同名 JSON。测试运行器将应用数据、临时目录隔离在 workspace task-env；无 product source/test 文件被改写。

## AUDIT-05：SFX 拟声词

| 检查面 | 观察与结论 | 状态/边界 |
|---|---|---|
| SFX/对白分类 | `sfx-` 与仲裁产生的 `sfx-arb-` 标签映射到 `RegionType.SFX`；其他主检测标签映射为 `speech`。合成测试覆盖标签映射与阈值内/外仲裁；不证明模型识别准确率。 | `PARTIAL` |
| 韩漫长条页/大型艺术字 | 当前 SFX 检测器对符合宽度/长宽比条件的长页走 tiled inference；测试只验证合成几何路由、切片合并边界。没有加载真实权重，也没有评估大型艺术字召回/识别。 | 运行时准确率 `NOT_RUN` |
| 斜体、旋转、变形、重叠 | 检测后处理按 bbox 输出轴对齐框；模型输出中的 mask 系数不构成旋转/变形文字的独立人工参考。SFX/主检测器几何仲裁冻结为 bbox IoU `0.90`；已知校准数据没有真实 `0.90+` 候选对。合成测试不能替代标注数据。 | 真实准确率 `NOT_RUN` |
| 跳过/翻译/manual | 缺省 `sfx.policy=skip`；`skip` 与 `manual` 在自动翻译门均为 `skip_policy`；`translate` 进入正常 pipeline。配置只影响新建 Region；用户重类型会按当前全局策略重取 SFX policy。契约规定 manual SFX 的最终确认与显式单 Region 操作，但真实 UI 确认流程未运行。 | Core/Mock `PASS`；UI `NOT_RUN` |
| 区域类型修改、Revision、人工保护 | 定向测试覆盖用户重类型 Revision、Lock/乐观并发保护、人工译文保护，以及 redetect 竞态时保留已存在的人工作业。 | 所选测试 `PASS` |
| 分类缓存与重检测 | 没有独立的模型输出缓存；已落库的 live Regions 是后续 pipeline 的复用依据。`handle_detect` 遇到 live Regions 时复用而不调用 detector，因此避免重复 Region，也不会因模型/配置更新而自动刷新已有分类。现有 SFX policy Task 说明设置仅作用于新建 Region。 | 数据复用与保护 `PASS`；自动重新分类未实现/未验证 |
| SFX detector 错误路由 | typed SFX provider 错误会附带 `sfx_provider_status=degraded: ...` 并保留主检测候选；若主标签为 `manga-*`，其 Region 类型仍是 `speech`，因此该降级下 SFX 不会进入 SFX policy 门。非 typed 编程错误传播。未实测真实权重损坏/运行时故障和人工恢复界面。 | 合成故障路由 `PASS`；恢复闭环 `PARTIAL` |
| 重叠与重复 Region | 对同一几何的合成 primary `manga-1` 与 SFX `sfx-1`，仲裁把 primary 重标 `sfx-arb-manga-1`，但仍追加原 SFX 候选；两个相同 polygon 均映射为 SFX。Region handler 对每个候选分别创建 Region；若用户将策略设为 `translate`，每个 Region 进入各自的单 Region 翻译 step。该副作用在 `M2-REGION-OVERLAP-ARBITRATION` 已列作已知取舍/去重候选（阶段快照）；2026-11-13 已由 Codex 裁为 INVESTIGATE（见 11_ISSUES.md）。 | 候选 `AUDIT-05-CAND-001`：INVESTIGATE |
| 单 Region 重翻/多阶段状态 | `RETRANSLATE_REGION`、SFX policy gate、pause/continue/stop 与 crash recovery 的合成测试覆盖了 Core 状态/调度路径。暂停/停止按 Step 安全边界处理，不替代真实 UI 操作体验。 | 所选测试 `PASS` |

机器检测输出只用于检查 pipeline 路由，不作为 SFX/对白准确率的独立正确答案。没有人工 GT 的项目准确率结论。

## AUDIT-06：AI 翻译引擎

| 检查面 | 观察与结论 | 状态/边界 |
|---|---|---|
| API 配置/模型请求 | production adapter 从冻结 provider binding 取 endpoint、model 与 credential reference，credential 在请求时解析；OpenAI-compatible client 使用统一 transport/network profile。配置、payload freeze 和 Mock transport 测试通过；本轮没有真实 endpoint/API 请求。 | 静态/Mock `PASS`；live API `NOT_RUN` |
| Prompt、SFX 语义与上下文 | System prompt 要求严格 JSON/RegionID 映射，并对 `region_type=sfx` 写明文化等效、简洁和强度规则。请求携带 `page_id`、目标语言、Region 类型、glossary 和上下文页文本；production SQLite catalog 冻结同一 chapter 的最近邻页及前后位置。provider payload 不含显式 `book_id`/`chapter_id` 或标题字段。 | payload/上下文合成检查 `PASS`；翻译效果 `NOT_RUN` |
| Glossary 优先级 | glossary 作为 source→target 字典进入 request body；当前 system prompt 没有可执行的锁定/优先级约束，production response path 也未调用 `glossary_hits` 校验术语是否应用。是否满足产品所需的词条优先级需 ZCode 对原始需求和现有语义裁决。 | 候选 `AUDIT-06-CAND-002`，待裁决 |
| 批量/单 Region 请求与映射 | 生产 handler 每个 translation step 构造一个 `RegionInput`，输出必须且只能映射回当前 Region；unknown/missing/duplicate/malformed 响应类型化失败，不写入 current。用户批量选择会通过多个 Region step 执行，不是一个多 Region API request。 | Core/Mock `PASS` |
| 重试与重复调用 | per-provider retry 最多 3 attempts，默认线性等待 1s/2s；只有允许的 typed error 重试，并校验 payload hash 保持相同；fallback 只按显式配置链运行。HTTP 头只有 `Content-Type` 与可选 Authorization，没有 provider 级 idempotency key。超时/响应丢失后服务端是否已完成、是否计费无法由离线代码证明。 | 本地规则/Mock `PASS`；远端语义 `NOT_RUN` |
| 超时、取消/恢复 | network profile 默认 timeout 为 30s，配置允许正值；pipeline 在 Step 边界检查 pause/stop，transport 调用不接收取消 token。因此 in-flight 请求需等响应或 transport timeout 才回到调度器；跨进程强制终止和上游取消未验证。continue/restart 区分在合成 pipeline 测试覆盖。 | 合成状态机 `PASS`；in-flight stop `NOT_RUN` |
| 并发与费用控制 | 单个 `PipelineService` scheduler 串行执行，默认并行页/Step 上限均为 1；每 Run 有 1000 个 StepRun 的资源上限。每个 Region step 可含最多 3 次同 provider 尝试，显式 fallback 可增加 provider 次数；代码没有美元/账单级 per-run spend cap。未执行付费 API，实际价格、服务端重复扣费和远端并发行为未验证。 | 候选 `AUDIT-06-CAND-001`，待裁决 |
| 人工修改与 Revision 历史 | write path 携带 Step 输入 revision；Lock/人工保护或 revision 冲突会阻止直接覆盖并走 Candidate/compare-and-write 机制。SFX/type retype 和 revision 相关选定测试通过。 | 所选测试 `PASS` |

## 待独立裁决的候选项

以下是证据支持的候选观察，不是本审计作者签发的最终缺陷定级或修复授权：

1. **`AUDIT-05-CAND-001`：同位 primary/SFX 双 Region。** 合成结果精确复现两候选相同 polygon、均为 SFX；handler 分别落 Region。`skip` 默认减轻自动 API 请求，`translate` 策略仍会分别请求/渲染。SFX 仲裁 Task 已记录此副作用与去重候选。
2. **`AUDIT-06-CAND-001`：无账单级 spend cap / provider idempotency key。** 单 Run 有步骤数上限且 per-provider retry 有上限，但没有货币预算；网络层的 ambiguous timeout replay 是否造成双重计费未知。
3. **`AUDIT-06-CAND-002`：glossary 优先级未由生产校验强制。** request 会附 glossary；未对实际翻译输出强制术语匹配。是否违背原始需求属阶段快照；已由 Codex 裁为 INVESTIGATE（见 11_ISSUES.md）。

## 未测与限制

- 真实 SFX 权重、真实韩漫/旋转/变形/重叠字体图像及人工标注 GT：`NOT_RUN`。
- 真实 GUI 内的人工确认/改标、SFX error recovery 交互：`NOT_RUN`；headless/core 测试不替代 GUI。
- 真实付费 translation API、provider 实际账单/idempotency/cancellation 语义：`NOT_RUN`；未发现可用于本轮的明确费用预算，因此没有网络调用。
- 超过默认请求规模的账单、跨多个 Core 进程的并发边界：`NOT_RUN`。
- 本报告不改变产品源码、原有测试、契约、Schema 或依赖；候选修复需另行释放实现 Task。

## 证据

- 定向回归 log/JSON：`logs/audit05-06-targeted-20261113.log`、`evidence/audit05-06-targeted-20261113.json`。
- 上下文/翻译 log/JSON：`logs/audit06-context-20261113.log`、`evidence/audit06-context-20261113.json`。
- 独立审计用例：`tests/test_audit05_sfx_regression.py`、`tests/test_audit06_context_observations.py`。
- 本报告生成时审计 HEAD=`d96529ebff6cf752ad64a676d05ec622da09e565`；后续证据、Task pins 与门禁按 Task Canonical Evidence 表更新。
