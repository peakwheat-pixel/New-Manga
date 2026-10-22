# Antigravity Owner 修订任务：P02 Stage A r3

请从已接受的 P02 Owner conversation 继续，仅在你自己的 linked worktree 修改。当前固定起点如下：

- Owner worktree：`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- branch：`agent/antigravity/P02-real-webview-harness`
- start HEAD：`9b82e97b8aadc5b6b8710e03b5128a608697f56e`，tree=`7fe67d0fb9bfc95e579c0fbda539de85eb73e4f4`
- diff base：`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`；行为基线仍是 `241ff3b70b6fc0490ea238efd486cc707f849031`
- DSH r2 formal Review：`G:/CODEX/New Manga/doc/reviews/P02-9b82e97b-dsh-r2-review.md`，decision=`changes_requested`，P0/P1/P2/P3=`0/0/2/8`；Codex exact-commit preflight 补证见 `G:/CODEX/New Manga/verification/P02/r2-clean-commit-validation.md`。

## 保持冻结范围

P02 r1–r4 产品 AC、边界、Owner allowlist 和禁止路径保持冻结；不得重冻结、扩张或改产品取舍。仅可改 `apps/desktop/frontend/e2e/**`、`verification/P02/**`、`doc/handoffs/P02-*.md`，以及 `doc/tasks/P02.md` 的真实执行/交付证据记录。Task frontmatter、AC、base、scope hash、Plan/Status/Roadmap、共享契约/Schema/依赖、`frontend/src/**`、Tauri/Rust、Python Core、P03 均禁止改。不要触碰 Codex detached 验证 worktree或 root checkout。

## 必须修订的 DSH r2 open findings

正式报告逐项复核 F-01–F-12 与 G-01–G-07；下列内容全部处置，并在 Handoff/Task 记录真实 disposition，不能写成已闭合而无证据：

1. **F-05 (P2) + G-01 (P2)：证据 provenance 与错误闭合声明。** r2 的 `p02-harness-results.json` 指向 r1 HEAD/tree、`evidence_carrier` 指向自身，无法识别被测字节或交付。去掉自引用；清楚区分 source commit/tree、source-code file SHA-256 清单、test-run evidence 与 later delivery/review commit。禁止在同一提交中循环声称该提交自身是 delivery hash。真实文件哈希不得造作；Stage A 的 runtime AC1–AC6 继续 BLOCKED。准确修正 Handoff、RESUME、Task 中“已记录 delivery commit / artifact hash”的现状描述。Codex 会在新代码 commit 后从 clean detached exact head 重跑 Stage A probes/harness，并保存独立命令、结果和哈希证据；把该后续验证预期与当前已运行结果区分开。
2. **F-08 partial：** `live_bg_hex` 不得硬编码；从 fixture 中按语义 role 取对应背景。Alpha 函数声称仅到实际覆盖程度：要么准确标成 utility 自检覆盖、未用于当前不透明色值；要么加入有来源且明确底色的 synthetic alpha fixture 并证明评估路径使用它。不要声称真实 WebView/真实 token alpha 对比度通过。
3. **F-09 partial：** 全链路每次只运行一次 static-control probe；去掉 `env_identity_probe.py` 未使用的 `os` 导入。避免报告重复生成。
4. **G-02：** 人读环境报告须显示 `is_clean` / clean status 与必要的 porcelain 状态；若 runner 先写自身日志导致 dirty，修正执行顺序或如实把自产日志与源码 dirty 区分，不把旧 HEAD 描述为 tested bytes。
5. **G-03：** 将生成日志的行尾策略做成 Windows PowerShell 5.1 可复现的 LF；Handoff/Task/RESUME 中任何 `git diff --check EXIT=0` 断言都要指向实际命令+stdout/stderr+EXIT 证据，或改成等待 Codex Gate 的 future check。Codex 会独立复算 exact diff。
6. **G-04：** 实际运行记录必须与 Task 测试表命令一致。Codex 在 r2 clean checkout 确认 `run-webview.ps1 -ProbeOnly` 只运行环境与静态 probe、在 Stage A Harness 之前退出，且不会刷新 `p02-harness-results.json`。把 ProbeOnly 和完整 Stage A Harness 分别记录；精确说明每条命令覆盖哪些场景、对应哪个日志/EXIT。
7. **G-05：** 按 P02 AC6 role 明确阈值：普通文本 4.5:1；禁用文本/非文本 3.0:1。输出每对实际 foreground、background、alpha/composite base、角色及阈值。背景/描边不能作为前景与任意背景配对并冒称实际 contrast finding；无法确定真实配对时标 `NOT_VERIFIABLE`。不根据静态预检宣称实际 UI 失败。
8. **G-06：** 当前仅 6 位不透明 hex 实际进入模型；不要称 alpha blend 被实际 token 评估。按第2项修正声明/加入有来源的 synthetic 测例。AC6 仍 BLOCKED。
9. **G-07：** 每个 revision fixture 依据 `src/region/types.ts` 补齐 `RevisionSummary` 的 `created_at`、`region_type`、`sfx_policy`、`is_current`，并确认其他字段与 wire 完整一致。

## Codex 独立 Spec/Standards Review 补充项

- AC4 `retype` fixture 当前是 speech→narration，但真实 Workbench relabel UI `relabelMachine.ts` 只允许 speech↔sfx。按当前真实 UI 转移改 fixture 和预期结果，不要直接 IPC 绕开 AC 要求的真实交互。
- `PRE-01` 当前只检查 section 名称，Task 却写成验证 sections/enum/IPC；实现实际的 fixture shape、枚举、IPC/readback assertions，或准确收窄 PASS 名称/说明。核对书/章/页 wire keys（当前类型使用 `book_id`/`chapter_id`/`page_id`）及 Revision/restore 返回结构；不要用只含 `id` 的数据宣称符合导航投影。
- E2E TS protocol 对 foreground/background 均含 alpha 时要正确合成已知底色；底色不可确定则结果为 `NOT_VERIFIABLE`，不能丢掉背景 alpha 后算出假 PASS。不要新增依赖。

## 交付与执行边界

r2 DSH 报告的其他 closed findings继续保持；新增修订只限以上必要范围。提交新的 fixed code commit 并返回真实 commit/tree、干净状态、逐 path diff 和 Handoff。可运行不构建的 synthetic/static controls，并分别保存准确命令、PowerShell/Python/Node 头、stdout、stderr、EXIT；如果必须在提交后 clean worktree 重跑才能绑定 source hashes，可先提交代码再跑，并清楚将 source commit 与之后的 evidence commit 区分。`git diff --check` 不得先于最后一次文件改动运行。

禁止 Cargo/Tauri/sidecar build、前端全量 build、GUI/WebView/CDP、用户数据/真实漫画库访问、P07 释放。不得标记 P02 done 或把任何 runtime AC 改为 PASS。超出 allowlist、发现受保护文件漂移或环境指向真实用户数据时立即停止并汇报，不要清理或覆盖现场。
