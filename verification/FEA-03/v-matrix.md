# FEA-03 验收矩阵 V1–V25

状态口径：PASS 仅用于已执行且实际通过的步骤；PARTIAL 表示有局部 smoke/实现证据但未满足完整 V 场景；BLOCKED 表示环境无法执行；NOT_RUN 表示尚无该 V 的运行证据。测试源存在不等于测试执行通过。

| V | 场景 | 状态 | 实际证据 / 未完成部分 |
|---|---|---|---|
| V1 | 11 字段、序号 0→N | PARTIAL | Draft/Journaling 手工 smoke 验证 11 字段及 0→2；production pytest 未运行。 |
| V2 | 主窗/浮窗同 Session 同 DraftId | NOT_RUN | 实现按 Session/target 复用；该测试未执行。 |
| V3 | 五个强制 flush 点 | NOT_RUN | Core 与 C# 测试源覆盖五点；dotnet/pytest 测试未执行。 |
| V4 | flush 失败保留缓冲并 conflicted | NOT_RUN | 测试源已写；完整 pytest/dotnet 未执行。 |
| V5 | 两 Session 只读、转移 owner | PARTIAL | 组件 smoke 验证转移后的文本冲突；完整只读与 owner 生命周期测试未执行。 |
| V6 | 文本冲突双方 conflicted、禁止自动合并 | PARTIAL | SQLite 组件 smoke 通过；完整 pytest 未执行。 |
| V7 | 几何/样式按键合并 | NOT_RUN | 领域/BRIDGE 测试源已写；pytest/dotnet 未执行。 |
| V8 | 同 token replay 两次同 revisionIds | PARTIAL | SQLite component-level apply/replay 手工 smoke 返回同 revisionIds，revision count 未增加；production assembly suite 未运行。 |
| V9 | 过期 token 拒绝 | NOT_RUN | pytest 测试源已写；未执行。 |
| V10 | CRASH-A/B/C | PARTIAL | 真实子进程三阶段均通过、旧/新 journal 与 tmp 清理符合预期；单元级异常注入 pytest 未执行。 |
| V11 | 损坏 journal 丢弃且不阻塞 | NOT_RUN | pytest 测试源已写；未执行。 |
| V12 | candidate-only prepare、字段与 pointer | PARTIAL | SQLite 组件 smoke 验证 prepare 后 pointer 不变；完整 production assembly 未运行。 |
| V13 | translation artifact candidate | NOT_RUN | 未执行。 |
| V14 | 第三 Region stale 整体回滚 | PARTIAL | SQLite 组件 smoke 验证前两个 pointer/count 不变；独立连接“提交前不可见”未验证。 |
| V15 | 三锁×三域，两条 candidate/apply 路径 | NOT_RUN | 测试源已写；矩阵未执行。 |
| V16 | 六键白名单及错误含外键名 | NOT_RUN | 测试源已写；pytest 未执行。 |
| V17 | 改任一 protection 位后 LOCK_CHANGED | NOT_RUN | 测试源已写；pytest 未执行。 |
| V18 | 旧路径同文两次仍两 revision | NOT_RUN | 旧 service.py 未改；回归测试源未执行。 |
| V19 | 旧→新（刷新/不刷新）、新→旧组合 | NOT_RUN | 测试源/基线未执行；无法确认组合结果。 |
| V20 | 重启 receipt 命中/intent 兜底/current mismatch | PARTIAL | receipt 写失败后 intent 重启补 receipt 与 replay 通过；其他分支未全部执行。 |
| V21 | 不同内容、多序列、过期 replay | PARTIAL | 多 sequence receipt 文件 roundtrip 通过；不同内容和过期优先 pytest 未执行。 |
| V22 | OS 层 data-root 不可写 | NOT_RUN | 测试源已写；未执行真实 ACL/只读挂载验证。 |
| V23 | 双进程 .lock fail-closed、释放后可启动 | PASS（手工进程 smoke） | 第二进程退出 73，释放后返回 0；非 pytest。 |
| V24 | C# DraftBuffer 与 dotnet test | PARTIAL | 生产源和测试源 Roslyn 编译退出码 0；防抖 n=12 p50=405.3ms/p95=407.6ms；dotnet test restore 阶段阻塞，五触发测试未执行。 |
| V25 | 活跃登记、Session 清理、孤儿 discard、receipt 保留 | PARTIAL | edit-open active 登记手工验证；其余生命周期断言只在未执行 pytest 测试源中。 |

用户任务正文列 V1–V24；当前工作区 FEA-03 Task v6 冻结矩阵另含 V25。

> 复核处置（DSH）：V13 已补 	est_machine_result_candidate_prepare_keeps_pointer（machine-candidate 不写指针）；V19 旧→新/新→旧组合登记为 DSH 集成验证 deferral（见 Task 卡「契约 deferral 登记」），本卡不改旧路径，V18 覆盖旧路径行为不变。

