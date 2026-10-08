## r2 有界复核结论（只读；我本轮零写入、零测试、零commit、零诊断）

**总判**：C2/C3/C4=fixed；C1=部分fixed/部分unverified。0×P0/P1。**Task 仍 BLOCKED，不 done、不集成**。

**C1 — 部分 fixed / 部分 unverified**
fixed(有限)：`rev-parse 7556cb2d` 与 `cfb5d2ee→7556cb2d` 的 name-only 已落盘，39 条全在 `doc/**`、`verification/**`，与"只差治理/日志"自洽。
unverified：**没有** `cfb5d2ee→41d77f98`(reviewed_head) 的落盘 diff；binding log:42 的路径表不含 `verification/M2-RC2/run_e2e.py`，而 08fa1048 恰好动了它；line 52 的 AST 等价结论无命令回显/HEAD/EXIT 绑定 → 新发现 N1。

**C2 — fixed**
`frozen` 15 条与 `apps/desktop/src-tauri/src/main.rs:53-77` 逐项同名同序（我静态核对通过）；负向覆盖 version/capability/status/error 共 8 项；16=6+2+8 与 `raw/check-snapshots-r2.log` 一致，EXIT=0（父侧）。残留 N3（见下）。

**C3 — fixed**
`run_e2e.py:27-30` 已含 `--output-dir` 与 fresh `%TEMP%/m2rc2-lab-*`，`:506 mkdtemp(prefix="m2rc2-lab-")` 与文档串相符。UNKNOWN 处置**接受**：`run_app:382-390` 超时分支 kill 后仅返回 returncode、无时间戳，`:607-611` 日志头只有 `exit=code`，"瞬间退出 vs 240s 被杀"确不可事后重建；当前也未把它当 timeout PASS。

**C4 — fixed**：glob 无 `_pytmp*` 残留，scratch 已删。

**新发现**：N1(P2) 上述 C1 证据绑定缺口——审计者无法从落盘判断 41d77f98 与构建 head 的内容关系；N2(P3) binding log 标签 `R1_REPORT_UTF8_GIT_BLOB_SHA256` 实为文件字节 SHA-256，非 git 对象 id(SHA-1)，易误读；N3(P3) 契约 §5 表行序≠wire 序，顺序权威仍是 main.rs 冻结面，oracle 属人工转录，建议注明顺序来源；N4(P3) Handoff AC3 行仍写 `raw/check-snapshots.log：12用例`，未指向新 16 项证据；N5(P4) r1 的 F-17(:20)/F-07(:130) 为悬空引用、无定义，作者"编号载体不完整"描述准确、原文未改符合历史不改写。另：26 场景经我静态核数成立（21 条 gate json=20PASS+1FAIL，:623-624 早退致 5 项未注册），"21/21"确为 r1 原文错误。

**不可核验（明示）**：pwsh 沙箱 `grantWrite` 失败、升级无审批通道 → 我零执行；所有 diff/rev-parse/SHA/AST/EXIT 均为父侧断言；我只能核 `.git` 明文（ref/reflog 链 7556cb2d→a23a5333→08fa1048→41d77f98）与文件内容。

**不能采用 r1 批准作为新 head 批准**：r1 的 `approve_with_conditions` 只对 7556cb2d 有效；以 41d77f98 收口须先补 N1 落盘，再做新的非作者 re-review。

**下一步**：Codex 先补 `git diff --name-only cfb5d2ee 41d77f98` 与 AST 命令/EXIT 落盘，再释放只读 `M2-PACKAGED-AC1-DLL-DIAG`（Owner=DSH、Reviewer=Codex）；AC4 未修期间不得合并或 done。