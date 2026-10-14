角色：你是 P02-NEW-TIME-X6-AC1-AC7 的 Antigravity Owner，不是 Reviewer 或 Integrator。

任务基线：在 Owner worktree `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY`、branch `agent/antigravity/P02-NEW-TIME-X6-AC1-AC7` 上从 frozen release HEAD `e5638477` 开始；执行前确认完整 HEAD 与 clean status。Task 文件是 `doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md`，完整 Acceptance Criteria、依赖门、write scope、安全约束和证据规则均以它为准。唯一 RunId=`p02-newtime-ac-20261014-r1`，隔离根 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-r1/`。固定 packaged EXE 位于 Build/Cargo worktree，SHA-256=`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`；sidecar manifest SHA-256=`CA0F531ADE3B83D5FFD7627643A2393443702F2B48FF60080EF1284B6BAD8175`。Codex 已在 Task-local evidence 中复核 sidecar 5,610 files / 1,296,373,783 bytes，无差异。

先读 Task、`apps/desktop/frontend/e2e/p02-new-time/README.md`、`verification/P02-NEW-TIME-X6-AC1-AC7/preflight/codex-harness-static-review-r1/findings.md` 与相关 harness 模块。开始只处理下面这些已发现的测试脚手架 T 问题：
1. AC1–AC6 先构造 `EvidenceStore`（会 mkdir `RUN_ROOT/logs/<scenario>`），之后才 `launchApp()`；而 `launchApp()` 调用 `assertLaunchTargetsClean()`，它会把已写入的 `logs` 判为预存内容。调整顺序，使每次应用启动前先完成、记录 clean-target 检查，然后才创建日志；不得削弱隔离断言。
2. 每个 AC 脚本独立启停应用，但所有脚本共享固定 `RUN_ROOT=run-r1` 与 `launchDirs`；前一 AC 写入的 appdata/data/logs 会导致后续 AC 把先前合成数据误判成污染。为 AC1–AC6 使用 `run-r1/<scenario>/` 下彼此隔离、每次首次使用的子目录；保留既有内容，严禁清空、删除或覆盖。把命令、README 和证据 metadata 同步到该路径。
3. `ac6-contrast.mjs` 的 `String.raw` 中有未转义的内层模板反引号，导致 `rgb` 附近语法失败。只修允许范围内的测试 harness。
先确认上述修复与其它 runner 都在 frozen Task write scope 内，再对 e2e 目录全部 10 个 `.mjs` 运行 `node --check`；未全通过不得启动应用。不能通过降级启动 guard、复用非空场景目录或把 mocked/browser/JSDOM/Vite 结果当真实 WebView2 证据来绕过。

全部静态校验通过后，按 Task 与 README 顺序实际执行 AC1→AC2→AC3→AC4→AC5→AC6，AC7 汇总证据。AC4 必须分别覆盖 retype、undo、restore；真实 WebView2/键鼠/焦点/时序按 Task 精确要求。逐项记录 PASS/FAIL/BLOCKED/NOT_RUN、真实与 mock 层、固定源码与 binary hashes、命令环境 stdout/stderr/exit、单调时钟、截图/日志和 skip 原因。若任何 AC 不能满足真实条件，诚实记 BLOCKED 并说明恢复条件；不得预先宣称 PASS。

运行边界：只读使用 pinned EXE 与 sidecar，不重建、不安装、不启动 installer；不改产品源码、共享契约、Schema、依赖、lock/build scripts、样式或功能。只写 `apps/desktop/frontend/e2e/p02-new-time/**`、`verification/P02-NEW-TIME-X6-AC1-AC7/**`、本 Task markdown 的状态/结果/证据指针，以及本 Task Handoff；非 Git 数据仅放在 Task env `run-r1/` 或 `agent-output/antigravity/P02-NEW-TIME-X6-AC1-AC7/`。不触碰 primary checkout、Codex integration worktree、Build worktree、用户 profile/漫画库/数据库/人工修改/Lock/current/pinned Revision、OS/ACL/registry、无关缓存。不得重用 ZCode 的失败运行目录。
环境按 Task 进行隔离：APPDATA、LOCALAPPDATA、TEMP、TMP、NEWMANGA_DATA_ROOT、M2RC1_DERIVED_ROOT、M2RC1_MANAGED_ROOT、M2RC2_CATALOG_DB、WEBVIEW2_USER_DATA_FOLDER 及其它相关运行/模型缓存均指向当前 scenario 子目录；不要设置 `M2RC1_PROBE_OUT` 或 `M2AC1_TEST_MODE`，保持真实 packaged interactive surface。每个 scenario 开始前仅核验其自己的目标不存在/为空；发现内容时不覆盖，改用新的 Task-local scenario attempt 并记录。

产品问题只记 finding，不修产品。Owner 不自审，不释放 X6、post-run Review、Build/Cargo 或其它下游 Task。更新 Task 运行状态与真实结果，提交固定 delivery commit，并按模板写 Handoff，列明真实 commit、变更路径、AC 结果、证据目录、测试命令/结果及未决事项。报告任何偏离 write scope 前先停止该写入并记录；不要请求用户授权。
