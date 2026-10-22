# Codex adjudication：P02 AppContainer 契约 r2 DSH Review

- 日期：2026-10-10（Asia/Shanghai）
- 审查报告：[`dsh-appcontainer-contract-r2-review.stdout.md`](dsh-appcontainer-contract-r2-review.stdout.md)，DSH decision=`NOT_VERIFIED`；内容等同 `CHANGES_REQUESTED`；findings=`P0=2, P1=5, P2=8, P3=7`，另有 C-00 exact-object binding limitation。
- Codex 仅对报告提出的对象绑定缺口复算：r2 SHA-256=`8D84DA22599FA074083DCADC73119BC259F4545EC2BB7B1090EBD44687DE6963`；P02 Task SHA-256=`4915CE24F6B540C98F5F54916F9A99951970A16733AF5CF8044FA36240D2F7A3`。复算与 DSH prompt 固定值一致。DSH 本身仍为 `NOT_VERIFIED`；Codex 复算不升级独立 Review。
- 修订对象：[`appcontainer-isolation-contract-r3.md`](appcontainer-isolation-contract-r3.md)，等待 DSH 对 r3 exact SHA 的新一轮独立 Review。
- 安全状态：profile 未创建，ACL/registry 未修改，OS preflight 未运行；Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`，build 与 AC1–AC7=`BLOCKED / NOT_RUN`。

| DSH finding | Codex disposition | r3 落点 / 未闭合条件 |
|---|---|---|
| C-00 | 接受 | 本表记录 Codex 自行复算；要求 r3 Reviewer 重新绑定 r3/Task SHA，不把本记录当作 Reviewer 核验。 |
| R2-01 | 部分接受 | r3 §2 要求三个独立只读“不存在”证据；禁止猜 registry 键。若公开 API/可验证只读 inventory 不能证明 private registry 不存在，则 `BLOCKED`，不创建 profile。 |
| R2-02 | 接受 | r3 §2 固定 moniker 字面值；同一 exact moniker 是唯一恢复对象，不生成后缀。 |
| R2-03 | 接受 | r3 §8 允许仅对同一 moniker 重试 `DeleteAppContainerProfile`，并要求删除后检查残留；禁止递归/通配删除。 |
| R2-04 | 接受 | r3 §2、§4、§7 分离 DACL 与 MIC；记录 token IL/mandatory policy 和对象 label；只允许 profile 树/已授权 scratch outputs 的必要 Low label。RO 输入标签不变，缺权即阻断。 |
| R2-05 | 接受 | r3 §2 固定当前 user/impersonation 调用上下文和返回值；身份/API 结果不符即阻断。 |
| R2-06 | 接受 | r3 §2、§7 固定 `TokenIsLessPrivilegedAppContainer` 等字段、启动 flags、OS build/architecture 与子进程环境回读。 |
| R2-07 | 接受 | r3 §6 增加 `TRANSFORMERS_CACHE`、`PIP_CACHE_DIR`、`TORCH_EXTENSIONS_DIR`、`XDG_DATA_HOME`、`UV_CACHE_DIR`、`PYTHONUSERBASE` 的封闭处理；出现未登记写入根即阻断。 |
| R2-08 | 接受 | r3 §2、§6 写明零 capability 下 registry/COM/network 需求是预期否决，禁止通过追加权限解决。 |
| R2-09 | 部分接受 | r3 §6 要求空 capability snapshot 和真实 OS 负向证据；无安全且有效的 network/registry/COM synthetic control 时 Build Gate 保持 `BLOCKED`。本轮不执行这些探针。 |
| R2-10 | 接受 | r3 §3、§5 禁止祖先 ACE；只测 `SeChangeNotifyPrivilege`，缺少无修改遍历条件即阻断。 |
| R2-11 | 收窄 | r3 §1、§4 将 host ACL/label 变更限制到精确 scratch 输出叶子及本轮 profile 树；12 个输入、祖先和系统对象零修改。逐对象安全描述符快照、精确还原和 `WRITE_DAC`/`WRITE_OWNER` 预检；不能证明恢复即阻断。 |
| R2-12 | 接受 | r3 §5 定义规范化/组件边界、兄弟路径边界、reparse/hardlink/ADS 核验与失败关闭。 |
| R2-13 | 接受 | r3 §4 将旧 WSB HostFolder TSV 标为历史，不作当前 clone 期望；clone HEAD/tree/clean/remotes/alternates/hardlinks 重新实测。 |
| R2-14 | 接受 | r3 §4 精确保留 Task:81 对两个 generated output 目录的 tracked-file hash/blob 与允许差异规则。 |
| R2-15 | 接受 | r3 §5 规定真实 LPAC impersonation token、`TOKEN_QUERY`、`MapGenericMask`、mapping/privilege/result 证据，并明确 `AccessCheck` 仅 DACL、不能证明可写；正向 control 需真实创建。 |
| R2-16 | 接受 | r3 §1、§4 保留 Task:79 alias 写入成功=`BLOCKED`；正向 canary 改用独立 `verification/P02/tmp/lpac-write-control/`。 |
| R2-17 | 接受 | r3 §8 不沿用旧 203 数字；区分 clean tracked/Git tree 与 dirty/untracked 原始字节 SHA，明确覆盖边界和 `UNKNOWN`，不把选样冒充全量。 |
| R2-18 | 接受 | r3 §7 选 Job completion port、具体通知类型、丢失阻断、resume 前 handle snapshot、无 breakaway 约束。 |
| R2-19 | 接受 | r3 §3 对 Windows loader/runtime 只读测量现存 `S-1-15-2-2` ACE；不改系统 ACL；缺 ACE 或依赖未闭合即阻断。 |
| R2-20 | 接受 | r3 §9 使用本地实际 Review 路径并明确引用仅为 API 设计依据、不代表本机核验。 |
| R2-21 | 接受 | r3 当前状态持续记录 hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`。 |
| R2-22 | 接受 | r3 §7 只读检查 WER/LocalDumps；任何潜在越界 dump、crash 或新 dump 均阻断并保留。 |

本 adjudication 不构成 r3 Review、OS preflight、测试、profile/ACL 准入或 Build Gate 通过凭证。R2 report 的对象绑定及内容结论保持原样存档。
