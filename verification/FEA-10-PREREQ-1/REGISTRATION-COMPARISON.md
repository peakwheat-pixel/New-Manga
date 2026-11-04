# C-08 块②登记对照（实施记录，非 Review）

| 冻结记录 §3 要求 | 本次落点/证据 |
|---|---|
| §5.5 两命令行 | M2-C1 §5.5 新增 PrepareRun 请求→PreparedRun、AcceptRun 请求→RunAccepted；既有六行保留 |
| 逐字段 wire 编码 | §5.5 PreparedRun 形状、四元组键/数组顺序/canonical JSON/digest 格式；Host 临时候选与 UI 安全摘要边界 |
| 3 码 category/retryable | §5.5 错误表；HostCommandRegistry + HostCommandDispatcher 投影；23 个 Host 测试 |
| §8 Proposed（未观察）3 行 | §8 新小节，明确登记不冒充运行观察 |
| 原 :1119 证据规则例外 | §8 C-08 局部例外：冻结规范 false/false/true，不推断其他码 |
| 原 :1122 taxonomy 例外 | §8 C-08 taxonomy 局部例外，保留既有观察与全局 PROPOSAL |
| allowedRunErrorCodes | 精确 ordinal FrozenSet；未注册→unknown、安全短消息、retryable=false、保留 code/requestId；无恢复/重试执行 |
| 负向对照 | 新码从注册集合移除后调用生产投影函数；再用正式注册集断言冻结值；未知/大小写近似码同样降级 |
| wire 2.12 登记 | §3.2 / 修订记录；运行 Core PROTOCOL_MINOR、DefaultMinor 和既有六命令 per-command minor 均未提升 |
| registry/dispatch 归属 | 本卡只新增错误 registry，不新增可执行 PrepareRun/AcceptRun 路由；Core dispatch/候选/接受运行逻辑归 FEA-10 |

`logs/registration-comparison.log` 机械比较 HEAD 的既有 §5.5 全部非空行在改后文件中原样保留，三新码在 HEAD 中不存在、改后存在。该检查不替代独立语义 Review。
