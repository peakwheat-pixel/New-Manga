# DSH exact-head design review: P02 process isolation r4

请作为非作者独立 Reviewer，在此 detached、clean checkout 对固定 r4 candidate 进行只读正式设计 Review。

- Base / r3 reviewed candidate: `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`；DSH r3 response=`verification/P02/dsh-review-process-isolation-r3.response.md`，decision=`APPROVED_WITH_CONDITIONS`，P0/P1/P2/P3=`0/0/2/4`。
- Candidate / r4 delivery: `fb0a7668d948ae68f15fd59aaffd6aedf6663c99`；期望 parent=base；tree=`61abeb088dce6536494c27611f298187961c35ae`。
- 只审查 base..candidate 的 commit 差异；禁止修改文件、Git/index、root checkout 或其他 worktree。按仓库 `AGENTS.md`、P02 Task、Plan/STATUS、scope delta 和 r3 formal findings 校验授权范围。

重点逐项判定 R3-01..R3-05 / C1–C5 是否已实质关闭：
1. R3-01：MSVC/VS BuildTools、Installer、Windows SDK 是否明确是 Smoke 与未来 Build 共用的只读 HostFolder mappings；两个 Git for Windows 根才是 Build-only；Build config 是否复用映射、不重复 HostFolder/SandboxFolder，同时保持独立配置/hash。
2. R3-02：r3-start checkpoint 是否保留准确的 14:34 snapshot，并并列给出 r3 delivery addendum 的真实 blob bytes/SHA；是否修正“未修改”时间口径；从固定 r3 commit 复算是否吻合。
3. R3-03：HostFolder manifest record schema 是否完全确定字段名/类型/枚举/null 语义、相对路径/Unicode/casefold 排序、metadata-only 与 selected SHA 行为、canonical JSON/UTF-8/hash 限制披露，且不把 un-hashed bytes 声称已验证。
4. R3-04：P02 boundary、proposal setup、proposal Smoke step、Build plan 是否使用完全一致的 `git clone --no-local --no-hardlinks --no-checkout --single-branch --branch main ...`、`git remote remove origin`、`core.autocrlf=true`、固定 `checkout --detach` 顺序。
5. R3-05：scope extension 是否冻结仅 P02 Codex-only boundary paragraph 与已列 `verification/P02/**` process-isolation artifacts；r3 delivery checkpoint 是否引用 scope、18 个精确 r3 diff paths、canonical XML bytes/hash 和 Review 结果。
6. R3-06 是 r3 Review 明确指出的既存 AC1–AC7 vs AC1–AC6 表述差异，需核实已明确延期至 P02 closeout，不能把 AC7 忽略或报告为已验收。

并独立复核 r2 F-01..F-10 disposition、scope/路径许可、clone 只可进入 fixed scratch、缓存/输入限制、checkpoint/hash 可复算、r3 DSH response/raw JSONL 留档边界，以及所有 prose/XML/plan/gate/checkpoint 是否一致。检查新增 P0/P1/P2/P3 问题；如有 finding，给精确文件:行、严重级别、影响与可验证的修复要求。

严格区分 Design Review、Smoke admission、Build Gate、产品验收。即使设计 Review 为 APPROVED，也只可允许后续本机非提权只读 preflight；它不授权查询需提权的 feature、不授权更改/启用 Windows Feature、不授权 `wsb start/connect/exec`、Sandbox/Smoke、产品 build/tests/runner/Vitest/GUI/WebView 或任何 AC PASS。若任何运行事实无证据，保持 `UNKNOWN` / `NOT_RUN` / `BLOCKED`。Hard Build Barrier 必须有效。

不得运行任何可写、提权、Windows Feature、Sandbox、产品 build/test/GUI 命令；静态/只读检查即可。r3 exact review 的原始 JSONL 含 thinking events，因此本轮也将 raw JSONL 留在 checkout 外，不要复制到 Git。

请用简体中文返回 formal report，字段必须包含：
- Base/candidate/tree/parent、checkout 洁净性、18-path scope 检查方式；
- Decision=`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `BLOCKED` 之一，说明它只覆盖设计；
- P0/P1/P2/P3 计数；逐条 R3-01..R3-06、C1..C5 disposition 与证据；逐条 F-01..F-10 状态；新 findings 文件行证据；
- WSB feature、Smoke admission/Smoke、Build Gate/build、P02 AC1–AC7、Hard Build Barrier 的精确状态；
- 已执行/未执行命令、限制、下一项可安全 Gate。
不得用 `PASS` 代替未运行证据。
