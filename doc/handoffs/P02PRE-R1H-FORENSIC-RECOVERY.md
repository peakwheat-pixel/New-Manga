# Forensic recovery Handoff

2026-10-13 / Codex /root；状态 approved / APPROVED_DIAGNOSTIC，尚未集成，不是 done。

base/reviewed HEAD=343895fb5f0329c0c07a7104ec321b698f967607；root G:/CODEX/New Manga，main；integration_commit=null（attempt6 固定 root HEAD/index，不提前变更）。纯证据输入由 Task Canonical Evidence 的精确 SHA-256 绑定。

完成：限定本机 2026-10-12 Codex sessions 的 23 文件定位；15 项未恢复原工具输出。r2 补有限范围措辞、逐文件方法、span offset/hash、原 locator/canonical 副本同一性；既有 12 项不可变 H1 原输入匹配、Review r2 五项输入前后匹配、源 span 复核通过。旧 v2、attempt1、A6 不改写，历史 H1 P2-1 OPEN。

独立 Review：DSH session-4bb6a005-5f18-4aac-a103-1449c329d9c7，r1 CHANGES_REQUESTED → r2 APPROVED_DIAGNOSTIC，均 exit0；结果见 verification/P02PRE-R1H-FORENSIC-RECOVERY/dsh-review-r2.md，Codex adjudication 同目录。DSH 无 shell hash 能力且部分 manifest 截断，Codex 已补核原字节/pins；只读范围偏差如实记录。

实际检查：Windows / Python 完成 hash/span/assert 检查；PS7.6.6 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md` exit0 / PASS（Plan 80% budget warning）。未执行产品测试、采集运行、executor、Build、AC；此切片无生产代码。

资源收口：所有 Task 原始输出、原 source sessions、被当前 Gate 引用的 root 均保留；删除/迁移/归档 0 文件/0 bytes。没有清理未知内容或他人 dirty/worktree。Task canonical_evidence_status/resource_closeout_status 均 complete；集成后才可 done。

下一 Task：P02PRE-R1H-H2-COLLECTOR；ZCode Owner、DeepSeek Harness Reviewer、Codex Integrator。worktree=G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR；branch=agent/zcode/P02PRE-R1H-H2-COLLECTOR；base/current head=343895fb5f0329c0c07a7104ec321b698f967607（派发时）。Task 冻结允许两份新 PS7 脚本、纯测试日志、自己 Task/Handoff；无共享接口/Schema/依赖更改。Source Review/Parser/pure selftest 后才释放单独 live-run。

可转发指令已固定在 G:/CODEX/New Manga.workspace/agent-output/zcode/P02PRE-R1H-H2-COLLECTOR/dispatch.prompt.md，并已调用本机 ZCode CLI；原始 stdout/stderr/exit 在同目录。请在该 worktree 按 doc/tasks/P02PRE-R1H-H2-COLLECTOR.md 实现 collector 与纯 selftest，只提交 allowlist，固定 delivery commit/Handoff，再交 DSH 独立源码 Review；禁止 live collector/executor/Build/AC、修改 root refs/index、旧证据或用户数据。新证据不得关闭历史 P2-1，也不能作 X6 S0。
