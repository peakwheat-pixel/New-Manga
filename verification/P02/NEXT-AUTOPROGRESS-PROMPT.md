# P02 自动续跑提示词

请从 `G:/CODEX/New Manga` 自动继续正式 P02，之后按权威路线推进依赖已满足且范围已冻结的任务；直到已授权工作完成或出现必须由用户决定的产品问题。默认简体中文。不得关机、push、发布或部署。

## 恢复入口

先读取根 `AGENTS.md`、Plan、Index、Status、协作协议、正式 P02 Task 和本恢复点；核对 live Git HEAD、主工作区、P02 worktrees/branches、Task 状态及 P01 manifest。以 Git/Plan/Status/Task/实际证据为事实；聊天只提供意图。P01 已完成，绝不重做。不要重复 P02 的 AC/路径范围冻结：scope r1–r4、release 与 post-FF Gate 已完成。

## 当前 P02 检查点

- Live root `main@4b54f304dc201d129d4ba1c62d0368252e6301b1`；live Task 仍 `ready / IDLE`、Owner=ZCode，因 CLI 配置失败未接单；本地候选 worktree `codex/P02-owner-amendment` 从此治理 checkpoint 派生，候选 Task/Plan/Status Owner=Antigravity，尚待 r6 固定 head Review 与集成，不是 live 生效事实。Reviewer=DeepSeek Harness、Integrator=Codex；P02基线=`241ff3b70b6fc0490ea238efd486cc707f849031`，AC/allowlist r2 和 Codex治理 r4保持；AC1–AC7/build/真实 WebView 仍 `NOT_RUN`。
- P01 原作者 root manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`，24 项必须逐项保护；当前复核为24/24且0 hash mismatch（04:10Z；`verification/P02/root-manifest-r6-recheck.txt`）。不得 stage、stash、覆盖或清理。
- ZCode headless r1 在模型启动前因缺少 Built-in Provider Config EXIT=1，证据=`verification/P02/zcode-dispatch-r1.*`。
- Antigravity r1 已于 `2026-10-09T03:39:09Z` 启动，但因发现任务禁止的源树写入而被Codex中断；没有conversation ID、final JSON或CLI exit，不能算Owner接单。完整事实见 [`antigravity-dispatch-r1.interruption.md`](antigravity-dispatch-r1.interruption.md)。
- 旧 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode` / `agent/zcode/P02-real-webview-harness` HEAD=`e1948466082b3cadbfde1da53b791319e359a10b` 已 `DRIFT_DETECTED`：保留24个 `apps/desktop/src-tauri/**` 行尾变化、`verification/P02/cargo-target/**` 和未验证的 `cdp_probe.py`；严禁复用、切分支、reset、stash、覆盖、删除或把它们并入交付。具体列表和差异判据见 interruption record。
- DSH r5 固定审查 `approved`（仅 Owner fallback 方案，1×P2+2×P3）；reviewed_head=`0b95c6a1024f89ae341c637c0d531611175acdc5`，session=`session-5f773271-e7f0-427f-982b-2d794d6e52d2`，EXIT=0且已挂载。完整报告/prompt/exit/mount 证据已复制至候选 amendment worktree 的 `verification/P02/`；stderr 原始字节保留在 Live root 未跟踪文件。实际 Owner 元数据需对新固定 head 做 r6 Review；候选 worktree=`G:/CODEX/New Manga.worktrees/P02-owner-amendment-codex`、branch=`codex/P02-owner-amendment`、base=`4b54f304dc201d129d4ba1c62d0368252e6301b1`。Owner worktree尚未创建或派发。

- 只读 Explorer 调查发现 Tauri build 通过 `build.rs` 直接生成源码树 permission/schema 文件，`CARGO_TARGET_DIR` 不能隔离；完整记录=`verification/P02/tauri-build-side-effects-investigation-r1.md`。新 worktree `core.autocrlf=false` 只是未验证的缓解候选，不代表构建已安全；所有 P02 产品 build/测试/WebView AC 继续 `NOT_RUN`。

## 下一步（按顺序，持续执行）

1. 在 `codex/P02-owner-amendment` worktree完成Plan/Status/Task/Resume/NEXT元数据候选与r5 evidence。新增 `owner-transfer-amendment-r6.md`，列出变更路径、当前完整 Task SHA-256、r2产品契约SHA、r4历史Task/validator/probe SHA以及r5有限批准；保持AC/allowlist/基线/依赖不变，Task仍 `ready / IDLE`。
2. 固定唯一候选commit并按其真实HEAD生成自包含的r6只读review prompt，继续已挂载的DSH session `session-5f773271-e7f0-427f-982b-2d794d6e52d2`审查实际Task/Plan/Status/恢复点与Task SHA。保存raw stdout/prompt/exit/mount事实；approved后由Codex做FF集成Gate，changes_requested则依finding修订新head并再审。不能用r5方案批准替代r6 metadata Review。
3. r6获批并通过Codex Gate后，从集成release HEAD创建全新 clean `agent/antigravity/P02-real-webview-harness` worktree；派发前确认Task-local Cargo/build输出及源码禁写路径不受影响。只有真实conversation ID、最终接单和start checkpoint齐备才设 `in_progress`；旧ZCode worktree现场绝不复用。
4. 真实Tauri/WebView2构建在新worktree中需先证明生成文件保持零 forbidden-path byte diff。`CARGO_TARGET_DIR`不能隔离build.rs源码写入；LF检出是未验证候选。若无法证明安全，停止该构建、证据化blocker并继续其他独立允许项；不把旧EXE/Chrome/Vite/JSDOM/mock冒充真实WebView。
5. Owner 在已批准范围内执行 AC1–AC7、Task-local synthetic evidence 与 Handoff；任何不能安全执行的 Gate 如实标为 `BLOCKED`/`NOT_RUN`，不扩大 Task、修改产品 UI或冒充真实 WebView证据。
6. 所有 AC/测试/skip 与受影响源Hash完整交接后，派给非作者 DSH 正式实现 Review；按 findings 修订并复审；Codex 固定head作集成 Gate，复核路径、基线、测试证据及保护清单后才可集成、标 `done`。随后从权威 Plan 自动推进下一项已满足依赖的 Task。每到状态边界更新 RESUME。

保持用户漫画数据、Lock、current/pinned Revision、人工编辑、密钥及其他 Agent 的未提交内容安全；不因 routine 分配询问用户。只有出现真正未决的产品取舍才一次性询问。不要继续或执行任何一次性关机授权。
