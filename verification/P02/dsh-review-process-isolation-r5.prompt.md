# DSH exact-head design review: P02 process isolation r5

请作为非作者独立 Reviewer，在 detached、clean checkout 对 dispatch 中记录的精确 r5 candidate 进行只读正式 Review。

- Base / r4 approved design candidate: `fb0a7668d948ae68f15fd59aaffd6aedf6663c99`；r4 formal report=`verification/P02/dsh-review-process-isolation-r4.response.md`，decision=`APPROVED`（仅设计），P0/P1/P2/P3=`0/0/0/3`，N-01..N-03 待本轮修正。
- Candidate 必须是 exact-head 单 commit，parent=上述 base；请在报告记录 `git rev-parse HEAD`、tree、parent、cleanliness。dispatch 文件将记录最终 candidate SHA/tree。
- 只审查 base..candidate 的 commit 差异与正式 Review 证据；不得修改 checkout、Git/index、root 或其他 worktree。

重点核验 r4 formal report 的三个 findings 是否关闭：
1. **N-01**：build addendum 是否准确指出当前冻结的 r3 Smoke config 不含两个 Build-only Git roots；Build plan 是否去除过时的 `PROPOSED / REVIEW_PENDING`，准确记录 r3/r4 设计 Review 状态、三项 P3 收尾，以及 Smoke/Build/AC 与 Hard Build Barrier 原状态。
2. **N-02**：r3-start checkpoint 的文件级 scope allowance 是否明确涵盖 erratum 与 R3-01 MSVC/SDK 输入分类措辞修订；r5 extension 是否把授权限于本次三处文本和已列 verification artifacts。
3. **N-03**：P02 Codex-only boundary 对 scope delta 的章节指针，是否与实际标题逐字一致。

再检查 base..candidate 是否只修改既有 P02 Codex-only boundary 段及 `verification/P02/**` 里已冻结文件；r3 WSB XML bytes/hash 是否不变；有没有扩展 Owner allowlist、产品范围/代码/测试、Schema/IPC/依赖或修改 `STATUS`/`REBASELINE_PLAN`。检查新 P0/P1/P2/P3 问题与复数状态冲突。P02 AC1–AC7/AC1–AC6 文案差异已登记延期，不能把 AC7 隐去或声称验收。

严格区分 Design Review、Smoke admission、Build Gate、产品验收。不得提权、查询/更改/启用 Windows Feature、启动/连接 Sandbox、运行 `wsb`、Smoke、Build、产品 runner/Vitest/GUI/WebView。运行态无证据时保持 `UNKNOWN` / `NOT_RUN` / `BLOCKED`。Hard Build Barrier 必须继续有效。

请用简体中文返回 formal report，包含：base/candidate/tree/parent、checkout 洁净性、差异路径与 scope 核验、Decision=`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `BLOCKED`（只覆盖设计）、P0/P1/P2/P3 数量、N-01..N-03 disposition 与文件/行证据、新 findings、Windows Feature/Smoke admission/Smoke/Build Gate/build/AC1–AC7/Hard Build Barrier 的精确状态、已执行与未执行检查、限制和下一项安全 Gate。不得把未运行检查写成 PASS。
