# P02 Owner 转移元数据 amendment r6

## 固定事实与批准边界

- Live main amendment base=`4b54f304dc201d129d4ba1c62d0368252e6301b1`；候选 branch=`codex/P02-owner-amendment`。
- DSH r5 对提案 head=`0b95c6a1024f89ae341c637c0d531611175acdc5` 作出 `approved`，但仅批准项目既有 fallback 下的 Owner 转移原则、新 Owner branch/worktree 方案及产品契约不变；它明确不替代本候选元数据的固定 head Review。报告=`owner-transfer-r5-review/report.md`、mount=`owner-transfer-r5-review/mount.md`，session=`session-5f773271-e7f0-427f-982b-2d794d6e52d2`。
- P02 行为基线仍=`241ff3b70b6fc0490ea238efd486cc707f849031`；唯一产品 AC/Owner allowlist 契约仍使用 r2 SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`。该 SHA 只绑定产品范围，不是当前整份 Task 文件。
- r4 Codex-only 路线校验治理审查历史上绑定的 Task SHA=`5879A9FFA92931BB49183D4BD03E0D12DAAD3BFE21862993D6666FE0194013AA`、validator SHA=`FDE0012DF2ED21ADF4147B9744D88C06235401A6FA8211E5272B2501A1152B5B`、mutation probe SHA=`D37A0B3479B2EEA2F0D65B858FE013C2D5437F25468AF376F849928A7CB3FD15`；这些仅绑定 r4 当时的固定对象，不扩展到本 Task amendment。
- 本候选 checkout 的 EOL 核对：validator worktree bytes SHA=`FDE0012DF2ED21ADF4147B9744D88C06235401A6FA8211E5272B2501A1152B5B`，其当前 Git `HEAD` blob SHA=`6E05032C4BC26859BFE7FD7E5C256E8784B73F2F06F55B66D8824B53E0878DFE`；mutation probe worktree bytes SHA=`1E3C6AF28A4F29904B1DF89146701CBCFDC6FC7F55C13883CB202358054777A9`、其 Git `HEAD` blob SHA=`D37A0B3479B2EEA2F0D65B858FE013C2D5437F25468AF376F849928A7CB3FD15`。历史 r4 值照原记录保留；本次 Task SHA明确同时报告 worktree 与 LF-normalized 内容，避免把 Windows CRLF checkout 与 Git blob 误当同一字节串。

## 本候选 Task 完整 SHA

在 Task 文本完成修订后，以当前 Windows checkout 的实际文件字节计算：

- `doc/tasks/P02.md` worktree-byte SHA-256（CRLF checkout）=`B928814A051EC6E1C256BCDEF33968A2AB3F9C17654B0F086AA8163E56CAE78A`
- 同一内容将 CRLF 规范化为 LF 后 SHA-256（Git clean-filter / committed blob 内容口径）=`DC19C27450BDF378DD6EA4D31ABBECDD4968412656F8C23E6059359E2B517EAF`

固定 head Review 应复算并分别核对这两个口径；Task 哈希在本文件中登记，避免在 Task 内自引用。若候选 Task 在提交前再有任何文字修改，必须重算以上值并更新本记录。

## 本次唯一治理变更

- P02 Owner / suggested Owner：`ZCode` → `Antigravity`。
- Owner branch=`agent/antigravity/P02-real-webview-harness`；目标 Owner worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`，须在 r6 Review 与 Codex 集成 Gate 通过后从最终 release HEAD 创建。
- Reviewer=`DeepSeek Harness`、Integrator=`Codex`、状态=`ready / IDLE`、base、depends_on、AC1–AC7、允许/禁止路径、数据保护、无 UI 修复和无依赖新增均保持。
- ZCode dispatch 在模型启动前因缺 Built-in Provider Config EXIT=1；旧 worktree Antigravity r1 因 Tauri 生成路径越界被 Codex 中断，两个尝试都没有真实 Owner acceptance。旧 ZCode 命名 worktree 中未提交内容不复用、不集成、不清理。

## 对 r5 findings 的处置

- F-01（P2）：Plan/Status/Task/RESUME/NEXT 的实际 Owner 元数据均包含在本 amendment 候选固定 head；本 head 尚需 DSH r6 独立审查，批准前不得集成或派发。
- F-02（P3）：明确 r2 product contract SHA 与 r4 historical Task/validator/probe hashes 的绑定语义，并在本记录外置登记完整 Task SHA-256（上节）。
- F-03（P3）：RESUME/NEXT 已更新到真实 main `4b54f304dc201d129d4ba1c62d0368252e6301b1`；恢复时仍须先读 Live Git，不凭静态指针推断 HEAD。

## 尚未通过的 Gate

本记录不声称 Owner 接单、Task `in_progress`、build/Test、真实 Tauri/WebView2 或 UI 证据通过。实际 Task/Plan/Status metadata Review=`PENDING`，Codex integration Gate=`PENDING`。Owner worktree 尚未创建。
