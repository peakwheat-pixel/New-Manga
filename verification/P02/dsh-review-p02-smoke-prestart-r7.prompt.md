角色：P02 的独立非作者 Reviewer（DeepSeek Harness）。这是 Codex 撰写的 Smoke admission / 隔离预检证据；你没有参与该实现。请只读审查，不能修改文件、不能启动 Windows Sandbox、不能访问或扫描宿主映射输入，也不能运行 Build、产品测试或 Smoke。

Task：P02 — R3 sequencing clarification 与 R2 recursive HostFolder manifests。
仓库/worktree：当前目录 `C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`，branch `codex/P02-process-isolation`。
Review base：`b3d36dd4db1a156e3db1057d40b32869880546cf`。
固定 Delivery HEAD：`ab3958e1270084d80f2edb228aebc6e463233602`。
固定 Delivery tree：`c2829a7f3186ad4c7efe9c872d6e0932c58a1b7b`。
作者：Codex。Reviewer：DeepSeek Harness。请确认 `git rev-parse` 结果与上述固定值匹配，并只以该 commit/tree 的版本作结论。Review 绑定 Task、Delivery HEAD、当前 P02 Task 的验收与 evidence；检查 `git diff base..delivery` 和下列文件。

主要文件：
- `doc/tasks/P02.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`
- `verification/P02/codex-checkpoint-p02-smoke-admission-r2.md`
- `verification/P02/codex-checkpoint-p02-smoke-admission-r3-sequencing.md`
- `verification/P02/codex-checkpoint-p02-smoke-prestart-r2-start.md`
- `verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md`
- `verification/P02/codex-smoke-prestart-manifest-r1.py`（已声明为无效历史尝试）
- `verification/P02/codex-smoke-prestart-manifest-r2.py`
- `verification/P02/smoke-prestart-manifests-r1/**` 与 `verification/P02/smoke-prestart-manifests-r2/**`

请着重独立判断：
1. R2 准入 item 5 的矛盾是否被最小澄清且只改变不可实现的时序：start 前确认交互式非提权 shell、UI backend readiness、0 个已运行环境和其余预检；唯一 `wsb start` 返回 session id 后、任何 guest command 前，绑定到唯一 Sandbox window 并保存截图；绑定失败时停止同一 session、记 `BLOCKED / NOT_VERIFIED` 且不重试。澄清不得扩大 Build、产品测试或第二次尝试授权。
2. R2 collector 是否正确固定 config bytes/hash 和 11 个映射；路径 containment、reparse/symlink 不跟随、目录遍历/文件哈希的 TOCTOU 与扫描期变化检测、大小写冲突、样本完整性、canonical JSON 与错误传播是否足够；指出真实的 race 或 false-pass 风险。
3. 按 commit 中的记录只读复核 R2 summary 与每个 records artifact 的 SHA-256、schema、canonical serialization、排序、计数及 `PASS` 声明是否相互一致；不得重新读取或 hash HostFolder 实际内容。区分 50,356 个小型根全量哈希、33 个工具链选样哈希和 138,947 个未算文件；确认文档没有夸大覆盖。
4. R1 脚本/partial evidence 是否清楚标为无效历史数据且不会被误当成 R2 或 Gate 通过证据。
5. Task、Plan、Status、Index 的状态是否一致，并保持 Smoke=`NOT_RUN`、完整 preflight=`BLOCKED / INCOMPLETE`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`。

返回格式：
- `decision: APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`
- 确认的 HEAD/tree；P0/P1/P2/P3 finding 数；每项 finding 的稳定 ID、严重级别、精确路径/行号、影响、最小修复。
- 指明哪些检查是静态审阅，哪些实际未执行；不要把未执行写成 PASS。
- 若无 findings，明确写 `findings: none`，并指出残留验证限制。只对这个确切 Delivery HEAD 作结论。