<!-- FEA-10 scope review r2 (Codex independent) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r2（Codex 独立）

- Reviewer：Codex 全新上下文；未参与建卡/实现；只读。
- reviewed_head：`1ac21de73a415e064e49a9ab8f9814277c2cdc6e`。
- 结论：changes_requested，P0=0/P1=3/P2=3。
- DSH 处置：`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md` §Scope Review r2。

---

verdict：**changes_requested**；**P0=0 / P1=3 / P2=3**。两卡尚不宜进入 scope freeze/Appointment。

reviewed_head：`1ac21de73a415e064e49a9ab8f9814277c2cdc6e`  
身份/来源：Codex 全新上下文 `/root`，`reviewer_kind=agent`；用户指定 scope reviewer r2；未参与建卡、实现或返修。全程只读，无文件修改、commit、push。

- **FEA-10-PREREQ-1 scope verdict：changes_requested**。需落实 wire 版本边界、投影写域及测试落点。
- **FEA-10 scope verdict：changes_requested**。写域与关键安全验收仍未闭环。

r1 findings 逐项复核：

| r1 项 | 闭环判定 | 剩余问题与最小修复 |
|---|---|---|
| **P1-1 写域** | **部分闭环，仍 P1** | [FEA-10:24](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:24>) 已补两个 bootstrap 文件、`CoreServiceClient.cs` 和部分 Python 测试；但 Host、App Services、ApplicationCore、.NET tests 等仍整目录授权，缺文件级范围矩阵。PREREQ 同样保留整目录。列明实际修改/新增文件、用途和 AC；保留共享组合根 DSH 单点边界。 |
| **P1-2 SC-R09** | **部分闭环，仍 P1** | [AC7:84](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:84>) 已覆盖丢 ACK、异 fingerprint、request_id 非键及三类操作；未明确关闭/重启 Core、重开同库后同键找回原 Run。AC6 的终态重读不能替代 receipt 重放；补入 AC7 与矩阵断言。 |
| **P1-3 提交安全** | **部分闭环，仍 P1** | [AC5:82](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:82>) 已补 Run receipt 同事务，但 lease、PageBinding generation、manual/final、draft token/sequence 仍只写在范围正文，未逐项进入故障注入验收。“区分事务单位”也未定义各单位。补逐项冲突→三处零变化/完成数不增/candidate 可恢复；明确编辑 apply 全部 Region 原子性与 Pipeline step seam 的单位。 |
| **P2-1 PreparedRun** | **部分闭环，仍 P2** | Prepare 零 DB 写/零执行、过期码已补；[范围:70](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:70>) 却写两种 digest“分别记录并断言一致”，AC3 又混比四元组与 payload。明确四元组按冻结算法校验；另比较预览 payload digest 与实际发送 payload digest，不要求两种不同输入的摘要相等。 |
| **P2-2 UI 分支** | **闭环** | PREREQ AC2/AC3 已禁止未注册码触发专属恢复/重试或作为 UI 分支依据，并保留原 code。 |
| **P2-3 rev / minor** | **部分闭环，仍 P2** | [PREREQ:76](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:76>) 区分了文档 rev 与运行版本，但未落实 C-08 冻结记录 §3 **已批准 wire minor 2.12** 的登记/兼容方案，反而要求另批。明确新命令 wire minor、客户端 registry、Core dispatch/响应及测试归属；保持既有 Run wire 兼容，不必等同提升全局 `PROTOCOL_MINOR`。 |
| **P2-4 拆分/复用** | **闭环** | ADJ 已记录拆分裁定；卡已列既有 service/store/writer/draft seam 复用要求；C-08 冻结字节未改。 |
| **P2-5 验证矩阵** | **部分闭环，仍 P2** | 已有矩阵，但 AC8 未给真实 IPC 精确测试文件/门径/命令；裸 `dotnet build/test` 未指定工作目录或 solution，仓库根无 solution。补完整命令、具体 fixture/DataRoot、测试文件、逐项断言和证据出口。 |

依赖与范围核验：

- PREREQ-1 确为 C-08 块②释放硬前置；两卡与 DAG 均禁止其 done 前将 FEA-10 置 ready/实施。
- 未误加 FEA-11/12/13/14；已完成依赖及现存 Run、candidate、draft 基础可复用。未发现须新增这些任务为前置的依据。
- 真实代码确认 `_RUN_COMMANDS`/dispatch、assembly、客户端 registry 与现有事务 seam 落点；当前 `commit_step_result` 已通过回调在 seam 事务内持久化 Run，可继续加深。
- 两卡仍 proposed，首轮明确不得写生产代码，未构成实施授权；2026-10-31 上下文独立规则符合。
- `git diff ae1d2392..1ac21de73`：仅两卡、ADJ、r1 报告归档及 `TASK_LEDGER` 计数，共 5 文件；无生产代码或冻结契约变更。

实际验证：`main`，HEAD 精确匹配，工作区干净；Git common directory 为 `G:/CODEX/New Manga/.git`。  
`check.ps1`：**EXIT=0，PASS，3 warnings**；`verify_pins.ps1`：**EXIT=0，17/17 PASS**，含 C-08。  
**NOT_RUN**：pytest、.NET build/test、真实 IPC/UI、故障注入与重启行为测试；本轮只审 scope，不判实现 AC 为 MET。

推荐下一步（Agent：**DSH**，可直接转发）：  
“以 reviewed_head 为基线，仅修订两卡及 ADJ，完成上述 3 项 P1、3 项 P2 的最小补正；保持 proposed，不写生产代码、不改冻结字节、不 push。复跑 check/pins，提交新固定 head，再 Appointment 未参与修订的全新上下文 scope r3；通过后先释放 PREREQ-1，FEA-10 等其 done。”