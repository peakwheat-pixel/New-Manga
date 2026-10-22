# P02 Stage A r3 Codex 补充 Review 与复核记录

- 固定对象：base=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`，HEAD=`5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`，tree=`ce6e44c9b21cd6cfe9832aa89e71a72650f4e5f7`，scope SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`。
- Owner=Antigravity；独立 formal reviewer=DeepSeek Harness；Codex 是集成方。
- 正式 DSH r3 Review=`doc/reviews/P02-5fa8a41f-dsh-r3-review.md`，decision=`approved_with_conditions`（Stage A only），P0/P1/P2/P3=`0/0/0/10`；报告 SHA-256=`F248C34C215C00D4753D4681B253E4727787F7FB55B289B658FC29D4B8417039`。DSH 未能在其执行沙箱运行 shell/hash，故 tree/status/diff 无法由 DSH 独立复核。
- Codex 在固定 commit 上做 clean detached exact-head 复跑，见 [`r3-clean-commit-validation.md`](r3-clean-commit-validation.md)：Stage A runner EXIT=0，3 PRE PASS、6 runtime AC BLOCKED；`git diff --check` EXIT=0；没有产品 build、GUI、真实 WebView 或 Vitest。
- 本补充 Review 由 Codex Standards 和 Spec 两个独立本地 reviewer 只读完成；它们没有修改代码。综合 decision=`changes_requested`，不集成 r3。Reviewers 的 mutation probes 是只读内存试验，其原始脚本/逐条 stdout 未保存，因此在本文件记录为 Review 发现，不冒充 Task 正式测试证据；r4 必须留下回归自检。

## 阻断集成的 P2 findings

1. **文本阈值与 AC6 不一致** — `verification/P02/harness/workbench_cdp_harness.py:310,336`：普通 secondary/tertiary/muted text 仍按 `3.0`，仅 primary 才按 `4.5`。reviewer 的内存判别把 `ink_2` 降为 `#70707b`（contrast `3.55`），仍因 `3.0` 阈值被判 PASS。按冻结 Task，除 disabled text/non-text 外，普通文本必须 `4.5`。影响结果语义并违反 AC6。
2. **PRE-01 只验证各集合第一条及部分字段** — 同文件 `:214–239`。Spec reviewer 的内存 mutation：第二 region 改成非法枚举、缺另页 revision `created_at`、删除 undo/restore 场景，依然 PRE-01 PASS；第二 region 类型非法也不影响总体 verdict。r3 的“深度契约验证”声称超过实际覆盖。
3. **PRE-02 会消费陈旧/无来源 PASS，子探针失败可被忽略** — 同文件 `:267–295`。有旧报告时无 source/hash/freshness 校验；缺报告且静态子探针 EXIT=7 时，可静默跳过 PRE-02 并返回总体 True。`exit_code` 是由报告状态合成，不是实际 child EXIT。当前完整 runner 先运行 probe 的正常流程，不能证明独立直接调用/失败路径正确。
4. **PowerShell 失败路径日志 flush 不可达** — `verification/P02/run-webview.ps1:64–70`：`$ErrorActionPreference='Stop'` 时先执行 `Write-Error`，会在日志写盘和 `exit $exitCode` 前中止。PS 5.1 只读微探针由 reviewer 确认输出 `CAUGHT_BEFORE_FLUSH`。失败时可能留下旧成功日志并丢失真实子进程退出码。
5. **新增 TypeScript 文件有编译错误** — `apps/desktop/frontend/e2e/workbench_driver_protocol.ts:161–163`：alpha 混色两分支推断出的 `effectiveFg` 为 `number[]`，spread 到固定三参数函数触发 `TS2556`。现有前端 `tsconfig.json` 的 `include` 仅 `src`，常规 `build` 不会检查该 e2e 文件。最小修正为显式 RGB tuple 并把该文件纳入一个可运行类型检查。

## DSH P3 条件项与闭合口径

DSH 报告的 H-01–H-07 均为 P3，需在 P02 `done` 前关闭；其中 H-02/H-03 与上述 PRE-02/PRE-01 有部分重叠，并因 Codex 找到实际失败行为升为本补充 Review 的阻断项。

- H-01：正式 r2 finding ID 被 r3 文档重新赋义；`#30363d` 与真实来源 `#2a3038` 不符；“所有 findings 已闭合”过度声明。
- H-02：PRE-02 旧报告缺乏新鲜度/来源校验，退出码为推导值。
- H-03：PRE-01 枚举硬编码；fixture 中阈值/background-role 字段未被消费。
- H-04：alpha 颜色用 App 正文色配 pill 底，角色还命名为 region highlight；真实 pill 文本令牌应与 `RegionOverlay.tsx:45–48` 一一配对。
- H-05：speech→sfx 的 `sfx_policy=translate` 依赖全局配置，夹具未声明配置前提。
- H-06：Task/Handoff 保留“实现尚未开始 / Review 尚未运行”的早期文字，却未标历史。
- H-07：TS 类型键名与 JSON 机器输出不一致，并声明未实现的 timing/contrast/findings 字段。
- r2 G-03/G-04/G-05 仍有证据/ProbeOnly/文本阈值残余。r3 的 `-ProbeOnly` 与 Full Stage A 日志同路径覆盖；Task 对 ProbeOnly PASS 的引用并无独立日志。

**最终门禁结论**：DSH 的条件批准不能覆盖上述可复现的 P2 实现缺陷。P02 仍 `in_progress`，`integration_commit: null`；r3 不集成，Owner 应在现有 allowlist 提交 r4 后复审。AC1–AC6 继续 `BLOCKED`；hard build barrier 继续有效。
