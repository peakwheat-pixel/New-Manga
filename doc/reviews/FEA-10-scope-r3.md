<!-- FEA-10 scope review r3 (Codex independent) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r3（Codex 独立）

- Reviewer：Codex 全新上下文；未参与建卡/实现；只读。
- reviewed_head：`bb569c19d659f848edfffa7738027ac2074bda6e`。
- 结论：changes_requested，P0=0/P1=1/P2=2。
- DSH 处置：`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md` §Scope Review r3。

---

verdict：**changes_requested**；**P0=0 / P1=1 / P2=2**。两卡暂不宜进入 scope freeze/实施 Appointment。

reviewed_head：`bb569c19d659f848edfffa7738027ac2074bda6e`  
身份/来源：Codex 全新上下文 `/root`，用户指定独立 scope reviewer r3；`reviewer_kind=agent`。未参与建卡、实现或返修；全程只读，无文件修改、commit、push。

- **FEA-10-PREREQ-1 scope verdict：changes_requested**；文件用途/AC 映射及验证命令仍需补正。
- **FEA-10 scope verdict：changes_requested**；写域与验证矩阵仍有残留。

| r2 finding | r3 闭环判定 |
|---|---|
| P1-1 文件级写域 | **未闭环**：生产目录已收窄，但测试整目录授权仍在；PREREQ 缺文件→用途→AC 矩阵。 |
| P1-2 durable receipt | **闭环**：AC7 与验证矩阵已覆盖丢 ACK、重启 Core、重开同库、同键找回原 Run，以及 fingerprint/request_id 断言。 |
| P1-3 提交安全 | **安全范围已补齐**：AC5 明列十类逐项注入，并区分多 Region apply 与 Pipeline step seam；计数措辞另有 P2 歧义。 |
| P2-1 digest | **闭环**：四元组按冻结算法；仅要求 preview/send payload digest 同值，不要求两类摘要相等。 |
| P2-3 rev/wire | **闭环**：登记已批准 wire 2.12，区分文档 rev 与全局 `PROTOCOL_MINOR`，明确客户端 registry/Core dispatch 归属。 |
| P2-5 验证矩阵 | **部分闭环**：FEA-10 已补 solution、IPC 文件和环境门；PREREQ 命令及隔离/重启路径仍不精确。 |

**剩余 findings 与最小修复：**

- **P1-1｜写域仍不满足文件级冻结。** [FEA-10:63](<G:/CODEX/New Manga/doc/tasks/FEA-10.md:63>) 仍授权 ApplicationCore.Tests、App.Tests、`tests/fea10/`、`tests/pipeline/` 整目录；矩阵还保留 `Commands/*`。列明所需测试文件及用途/AC，并将误列的 Host.Tests/RunMonitorTests.cs 改为真实 ApplicationCore.Tests 落点。PREREQ 同样补文件→用途→AC 映射。`_RUN_COMMANDS`/dispatch、客户端及共享组合根边界已正确登记。
- **P2-1｜验证方案尚不能直接复跑。** [PREREQ:73](<G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:73>) 的第二个测试项目仅写简称，全量 `dotnet test` 未指定 solution；[FEA-10:128](<G:/CODEX/New Manga/doc/tasks/FEA-10.md:128>) 仍写未命名“重启脚本”，DataRoot 仅称临时/fixture。补完整命令、fixture/脚本文件、workspace 下隔离根规则、同库重开方式和日志出口。
- **P2-2｜AC5 将“不增加”扩大到全部 counts。** [FEA-10:114](<G:/CODEX/New Manga/doc/tasks/FEA-10.md:114>) 写“Run receipt/counts 不增加”，矩阵却写“完成数不增”。故障可以合法增加 failed 等计数；应限定为成功提交回执/完成计数不增加，允许权威失败或控制状态持久化，避免改变既有生命周期。

真实代码核对：现有 `commit_step_result` 通过 `persist` 回调在 seam 事务内持久化 Run，可复用。实际请求还经过 `ports/translation/protocol.py`、`translation_openai.py`、`openai_client.py`；文件级矩阵需明确这些构建/发送边界采用只读复用还是经 DSH 批准的窄范围扩写，不能将现有 `payload_hash` 默认视为 endpoint/model/body 全摘要。

依赖/越界：PREREQ-1 硬前置成立；FEA-10 不得先 ready。未误加 FEA-11/12/13/14；两卡仍 proposed，首轮不构成实施授权；符合 2026-10-31 上下文独立规则。  
diff 核验：`1ac21de73..bb569c19d` 仅两卡、ADJ、r2 报告归档，共 4 文件；无生产代码或冻结契约变更。  
实际验证：`main`、工作区干净；common directory=`G:/CODEX/New Manga/.git`；`check.ps1` **EXIT=0，PASS（3 warnings）**；`verify_pins.ps1` **EXIT=0，17/17 PASS**。  
**NOT_RUN**：pytest、.NET build/test、真实 IPC/UI、故障注入及重启行为测试；本轮不判实现 AC 为 MET。

推荐下一步（Agent：**DSH**，可直接转发）：“基于 reviewed_head，仅补正两卡及 ADJ：收窄测试写域、补用途/AC 映射、可复跑验证方案并澄清 AC5 计数；保持 proposed，不写生产代码、不改冻结字节、不 push。复跑 check/pins，提交固定 head 后交全新上下文复审；通过后先 Appointment PREREQ-1，FEA-10 等其 done。”