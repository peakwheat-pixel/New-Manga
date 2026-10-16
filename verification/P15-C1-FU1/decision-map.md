# P15-C1-FU1 决策映射与验证状态

- Task：`P15-C1-FU1`
- 基线：`82ce23bd50e4c53c3e546a392f4e984e7102a097`
- 变更范围：契约 §2、§5.2、§10、§11；没有产品代码、Schema、依赖变更。
- 测试纪律：设计类测试表保持全部 `NOT_RUN`。本交付没有新增可运行 handler；未运行产品、协议或安全测试，也未把静态撰写表述为测试通过。

## 裁决与来源映射

| 裁决/要求 | 契约条文 | 来源章节 | 交付处置 |
|---|---|---|---|
| A1：`provider_profile_id` 必需；目标固定为 Provider endpoint 经所选 Network Profile；缺省/非法 `INVALID_REQUEST` | §2、§5.2 | `ruling-P15-CORE-1-network-test.md` §1、§2(A1)；FU1 Task AC1 | 请求校验、唯一目标和不返回结果的错误路径已写明 |
| 禁止自选公网 URL、loopback、假目标；禁止 Proxy 冒充 TLS/HTTP 目标；禁止伪造阶段 | §5.2 | `ruling-P15-CORE-1-network-test.md` §2(B)；FU1 Task AC2 | 三项禁止规则写入契约正文 |
| 六阶段逐模式语义闭合；Proxy 来自 Network Profile/System 路由，其他阶段沿 Provider endpoint 路径 | §5.2 | D04 §41.1–41.4；P10 §6；P15 §5.1；ruling §1–2；FU1 Task AC3 | Direct/System/HTTP/HTTPS/SOCKS5 × 六阶段判定表及统一状态规则已写明 |
| 脱敏与错误投影不放宽 | §5.2、§9 | P10 §6、§8–9；P15 §1、§9；FU1 Task AC4 | 仅阶段安全字段；失败沿 §9 封闭投影；禁止敏感数据已写明 |
| minor 递增及兼容影响；G21/G22/G24 与 P10 冻结语义不变 | §2、§5.2、§10–11 | M2-C1 §3.2、§8；FU1 Task AC5 | rev 2.6→2.7；rev 2.5 不含此命令；2.6 草案缺参请求不兼容并会被拒绝；未声称其一般兼容 |

## 设计类测试表

| AC | 计划验证 | 前提 | 实际结果 | 原因 |
|---|---|---|---|---|
| AC1–AC5 | 按 Task 逐条核对契约条文及阶段判定 | 只读设计交付 | `NOT_RUN` | Task 要求设计类测试全部记为 `NOT_RUN`；无新增 runtime handler，不能将静态核对记为运行时测试 |
| AC5 | 核对 M2-C1 §3.2 版本递增与兼容影响 | 只读设计交付 | `NOT_RUN` | 未执行协议/runtime 测试；兼容影响仅作为契约声明 |

独立 Review：未自行发起；待非作者 Reviewer 复核。Handoff：`in_review`，不代表已被接受。
