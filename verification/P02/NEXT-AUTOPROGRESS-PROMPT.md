# P02 自动续跑提示词

请从 `G:/CODEX/New Manga` 自动继续正式 P02，之后按权威路线推进依赖已满足且范围已冻结的任务；直到已授权工作完成或出现必须由用户决定的产品问题。默认简体中文。不得关机、push、发布或部署。

## 恢复入口

先读取根 `AGENTS.md`、Plan、Index、Status、协作协议、正式 P02 Task 和本恢复点；核对 live Git HEAD、主工作区、P02 worktrees/branches、Task 状态及 P01 manifest。以 Git/Plan/Status/Task/实际证据为事实；聊天只提供意图。P01 已完成，绝不重做。不要重复 P02 的 AC/路径范围冻结：scope r1–r4、release 与 post-FF Gate 已完成。

## 当前 P02 检查点

- Live `main@a37f11baa287ba27eb9f5c2e75dce7472b88caa8`；P02 正式 Task 仍 `ready` / `IDLE`，当前正式元数据 Owner=ZCode、Reviewer=DeepSeek Harness、Integrator=Codex；所有产品 AC1–AC7/build/真实 WebView 仍 `NOT_RUN`。旧 RESUME/NEXT 曾落后于 a37 检查点；本恢复提交已校正。
- P01 原作者 root manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`，24 项必须逐项保护；检查点最后一次复核为24/24且0 hash mismatch。不得 stage、stash、覆盖或清理。
- ZCode headless r1 在模型启动前因缺少 Built-in Provider Config EXIT=1，证据=`verification/P02/zcode-dispatch-r1.*`。
- Antigravity r1 已于 `2026-10-09T03:39:09Z` 启动，但因发现任务禁止的源树写入而被Codex中断；没有conversation ID、final JSON或CLI exit，不能算Owner接单。完整事实见 [`antigravity-dispatch-r1.interruption.md`](antigravity-dispatch-r1.interruption.md)。
- 旧 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode` / `agent/zcode/P02-real-webview-harness` HEAD=`e1948466082b3cadbfde1da53b791319e359a10b` 已 `DRIFT_DETECTED`：保留24个 `apps/desktop/src-tauri/**` 行尾变化、`verification/P02/cargo-target/**` 和未验证的 `cdp_probe.py`；严禁复用、切分支、reset、stash、覆盖、删除或把它们并入交付。具体列表和差异判据见 interruption record。
- Codex 已在 `G:/CODEX/New Manga.worktrees/P02-fallback-scope-codex` 固定纯治理提案 commit=`0b95c6a1024f89ae341c637c0d531611175acdc5`，候选文件=`verification/P02/scope-owner-transfer-r5.md`，base=`a37f11baa287ba27eb9f5c2e75dce7472b88caa8`。真实 DSH 只读 review dispatch 正在 session `65872` 运行；到本检查点 stdout 仍为空、stderr 持续变化，无最终 JSON、退出码、session ID 或挂载证据。不能将 stderr 推理内容记作正式 Review。Owner 转移未批准/生效，Task 保持 `ready / IDLE`。不得重复向同一 reviewer worktree 派发。
- 只读 Explorer 调查发现 Tauri build 通过 `build.rs` 直接生成源码树 permission/schema 文件，`CARGO_TARGET_DIR` 不能隔离；完整记录=`verification/P02/tauri-build-side-effects-investigation-r1.md`。新 worktree `core.autocrlf=false` 只是未验证的缓解候选，不代表构建已安全；所有 P02 产品 build/测试/WebView AC 继续 `NOT_RUN`。

## 下一步（按顺序，持续执行）

1. 首先接续正在运行的 DSH review dispatch session `65872`，读取最终 stdout/stderr/exit，不重复派发。如果 DSH 将该提案判为 approved，则把批准报告限定解释为 Owner 故障转移原则；实际 Task/Plan/Status 元数据 amendment 仍需形成固定 head，由非作者 DSH 针对新固定内容复核后才集成。若 changes_requested，按正式 findings 在隔离 Codex scope worktree 修订、固定新 head 并重审。若 blocked，按 Skill 保存真实阻塞和状态，不伪称批准。
2. 只有实际 Owner metadata fixed-head Review 批准后，才把 Owner 改为 Antigravity、登记新 branch/worktree，重新计算 scope contract SHA，并同步 Plan/Status/Task/Resume/NEXT；保持 AC、allowed/forbidden paths、行为基线=`241ff3b70b6fc0490ea238efd486cc707f849031`、Reviewer=DeepSeek Harness、Integrator=Codex不变，Task 保持 `ready / IDLE` 直到真实接单和 start checkpoint。
3. 审批后由 Codex 串行集成纯治理修订；复跑 `verification/PROJECT-ROADMAP-20261008/verify_plan.py`、P02 route mutation probe、`git diff --check`、路径 allowlist、本地链接及 P01 manifest。保存完整日志/exit，更新恢复点。不得改写 root 的原作者或其他 Agent 未提交项。
4. 从新的 release HEAD 创建 Antigravity clean Owner worktree；按照 `antigravity-dispatch` Skill 重新真实派发 Task。只有真实 `conversation_id`/最终接单回应并写入 start checkpoint 后，才将 Task 设为 `in_progress`。旧 worktree隔离保留。
5. Owner 执行 AC1–AC7、Task-local synthetic evidence/Handoff；真实 Tauri/WebView2 不能由 Chrome/Vite/JSDOM/mock/fake timers冒充。Cargo构建在本机曾改写24个禁写的自动生成文件（内容忽略行尾后相同）；因此在新 worktree 派发前先用独立、无影响的预检确定如何使构建产物不改变任何禁止路径。若无法证明安全，记录精确 blocker 与证据，把相关 AC 标 `BLOCKED`，继续其他允许的只读证据；不得回滚或覆盖任何 Agent 内容。
6. 所有 AC/测试/skip 与受影响源Hash完整交接后，派给非作者 DSH 正式实现 Review；按 findings 修订并复审；Codex 固定head作集成 Gate，复核路径、基线、测试证据及保护清单后才可集成、标 `done`。随后从权威 Plan 自动推进下一项已满足依赖的 Task。每到状态边界更新 RESUME。

保持用户漫画数据、Lock、current/pinned Revision、人工编辑、密钥及其他 Agent 的未提交内容安全；不因 routine 分配询问用户。只有出现真正未决的产品取舍才一次性询问。不要继续或执行任何一次性关机授权。
