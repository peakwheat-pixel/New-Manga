<!-- FEA-10 scope review r1 (Codex independent) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r1（Codex 独立）

- Reviewer：Codex 全新上下文；未参与建卡/实现；只读。
- reviewed_head：`ae1d2392673b385938b9af0bbec7d140bc0d79e9`。
- 结论：changes_requested，P0=0/P1=3/P2=5。
- DSH 处置：`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md` §Scope Review r1。

---

verdict: **changes_requested**
reviewed_head: `ae1d2392673b385938b9af0bbec7d140bc0d79e9`
身份/来源：Codex 全新上下文 `/root`，`reviewer_kind=agent`；辅助只读复核 `/root/protocol_scope`、`/root/governance_scope`。均未参与实现或返修。
仓库：`main`，工作区干净；C-08 实际 SHA-256 与 `453f993c…` 冻结 pin 一致。未修改文件、commit 或 push。

- **PREREQ-1 scope verdict：changes_requested**。单独承载协议注册合理；主要内容齐全，需补以下范围澄清。
- **FEA-10 scope verdict：changes_requested**。主线方向正确，写域与验收矩阵尚不足以冻结实施。
- **ADJ verdict：建卡顺序合理，释放条件需补全**；本轮不得据此直接编码。

**P0：无。**

**P1-1｜FEA-10 写域无法覆盖承诺的交付。**
[FEA-10.md:24](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:24>) 未授权 Python `tests/`，也漏掉新 Core 命令必经的 `src/bootstrap/core_service.py`；当前 `_RUN_COMMANDS`、dispatch 均在该文件。CoreClient 的 `CoreServiceClient.cs` 也未在写域内。
最小修复：补范围矩阵，按真实调用链列明 bootstrap、客户端方法及 Python 测试文件；将整目录 Host/ApplicationCore/App Services/.NET tests 收窄到所需文件。共享接口变化须由 DSH 明确授权。

**P1-2｜SC-R09 缺少可判 MET 的验收。**
[FEA-10.md:68](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:68>) 的“同键重放不新建”不足以证明提交成功、响应丢失后的 durable receipt。
最小修复：增加提交后丢 ACK、重启后同键找回、同键异 fingerprint 拒绝、相同 `request_id` 不同 key 为不同操作的断言；明确 SC-R09 仅覆盖冻结的三类带 key 操作，不擅自扩展新命令语义。

**P1-3｜提交安全范围超过 AC4 的实际检查项。**
[FEA-10.md:60](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:60>) 承诺 source lease、binding generation、manual/final、draft token/sequence 重验，但 AC4 只枚举 revision/Lock 等；“成功同事务”也未明确包含 Run receipt。
最小修复：逐项增加故障注入和零副作用断言，明确成功时 live/revision/Run receipt 同事务；区分 C-13 多 Region 编辑 apply 与 Pipeline step seam 的事务单位。

**P2-1｜PreparedRun 与 payload 验收仍不完整。**
[FEA-10.md:66](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:66>) 未明确验收 Prepare 零 DB 写/零执行、候选过期返回 `RUN_PREVIEW_EXPIRED`；实际 endpoint/model/body/blob 摘要比对也未落为断言。
最小修复：补上述 AC，区分 C-08 四元组 `preparedDigest` 与实际发送 payload digest，保留冻结算法。

**P2-2｜PREREQ-1 漏“不作 UI 分支依据”。**
[FEA-10-PREREQ-1.md:61](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:61>) 未覆盖 C-08 §3 的这项要求。
最小修复：负向对照增加“未注册码即便保留原 code，也不触发专属恢复/重试动作”。

**P2-3｜文档 rev 与 wire minor 的责任边界不清。**
[FEA-10-PREREQ-1.md:59](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:59>) 同时要求 rev 2.12、Core minor 不提升；两者并非同一概念。
最小修复：明确本卡登记新命令 wire 2.12；运行版本、dispatch 与兼容回归由哪张卡承接，并列文件落点。

**P2-4｜拆卡及既有实现复用缺少显式处置。**
C-08 冻结记录 §3 仍要求与 C-04b 共 Task、分提交/AC、≤5 提交；本次 ADJ 未解释替代安排。
最小修复：DSH 在 ADJ 留下拆分裁定；范围矩阵列明复用 `accept_retry_failed_targets`、`RegionStepWriter`、`SqliteTargetCatalog.commit_step`、`DraftProtectionService`，不得重建同类存储/调度器或混用两层 candidate。

**P2-5｜FEA-10 缺可执行验证矩阵。**
[FEA-10.md:81](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:81>) 仅声明等级和日志要求。
最小修复：补 AC→测试文件→计划命令→隔离数据根→预期断言→证据路径；区分现存回归与新增测试。

依赖核实：块②确为硬前置；已完成依赖与代码基础属实；retry 重新冻结上下文符合 SC-R08。无需因此新增 FEA-11/12/13/14 依赖，但 source 校验应消费既有能力，不扩展为重定位/同步实现。
首轮 Gate 合理；Owner/Reviewer/worktree 占位在 proposed 阶段合法，不能替代 ready 前的范围冻结。

**NOT_RUN**：测试、构建、治理检查器、全套 pins、真实 IPC/UI；本次仅静态审查及单独核对 C-08 hash。

推荐下一步（Agent：DSH，可直接转发）：“以本 reviewed_head 为基线，仅修订两卡及本次 ADJ，补齐以上写域、AC、验证矩阵与拆分裁定；保持 proposed，不写生产代码、不改冻结字节、不 push。运行治理检查并记录结果，再提交新固定 head，由未参与修订的上下文复审；worktree 待 DSH 创建。”