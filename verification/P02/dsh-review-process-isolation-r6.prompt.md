# DSH exact-head design review: P02 process isolation r6

请作为非作者独立 Reviewer，在 detached、clean checkout 对 dispatch 记录的精确 r6 candidate 做只读正式 Review。

- Base / r5 reviewed candidate=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0`；r5 formal response=`verification/P02/dsh-review-process-isolation-r5.response.md`，Decision=`APPROVED_WITH_CONDITIONS`（仅设计），P0/P1/P2/P3=`0/0/0/2`。
- Candidate 必须是 exact-head 单 commit、parent=base；请从 git 复核实际 candidate SHA/tree/parent、author checkout 干净性与 16-path 前置 base 差量。
- 本轮范围已冻结在 `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md` § r6。只审查 base..candidate 和 r5/r6 formal evidence；不得修改文件、Git/index、root 或其他 worktree。

重点判定 r5 Review 条件：
1. **N-04**：r5 extension 的 scope permission 是否明确覆盖 r3/r4 extension 中 r3-start 的原 :52 许可行的一行就地扩写，并限制不改其他既有文字；R6 extension 是否记录 exact repair scope。
2. **N-05**：scope delta 末尾字面 `` `n `` 是否已移除，文件是否以 LF 结束，git blob 是否无 `No newline at end of file`。
3. r5 Review formal response/dispatch/session/mount/exit/stderr、delivery/review checkpoints 是否完整入库、hash/path/session 等自洽；独立确认 R5 report 的 N-01..N-03 disposition。
4. base..candidate paths 是否全在已冻结的 P02 scope；r3 WSB XML/canonical bytes/hash、产品范围、Owner allowlist、Task/STATUS/Plan、Schema/IPC/依赖是否保持不变。

严格区分 Design Review、Smoke admission、Build Gate 与产品验收；不得提权、查询/更改/启用 Windows Feature、运行 `wsb`、启动 Sandbox、Smoke、Build、产品 runner/Vitest/GUI/WebView。无证据时状态保持 `UNKNOWN` / `NOT_RUN` / `BLOCKED` / `NOT_VERIFIED`。Hard Build Barrier 必须有效。

请用简体中文提交 formal report：base/candidate/tree/parent、cleanliness/diff/scope、Decision=`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `BLOCKED`（仅设计）、P0/P1/P2/P3、N-04/N-05 disposition、新 finding、R5 evidence 自洽、精确 Gate 状态、已执行/未执行检查、限制与下一项安全 Gate。不得把未运行检查写为 PASS。
