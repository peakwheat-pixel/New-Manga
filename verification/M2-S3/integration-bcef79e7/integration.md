# M2-S3 Codex 集成核验

- Task：`M2-S3` Tauri Asset Protocol Feasibility Probe
- Owner：ZCode；非作者 Reviewer：DeepSeek Harness；Integrator：Codex
- 固定 base：`90c3e45962733799d43e3aefacf4fea99f662a2c`
- Owner tip / reviewed follow-up：`bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`
- DSH Review 固定 head：`233d0901e1de817a8357be7047346de7d8c49f23`
- 集成 merge：`6799c73a75c16252602ac85f4454a5ac1b45b8d2`
- Merge parents：`a006acb93cf9eb4103ba6a95603368add0978ef4`（master）+ `bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`（ZCode）

## 范围与合并

ZCode 的 `90c3e459..bcef79e7` 变更为 27 个路径，全部在 M2-S3 允许的实验、研究、Task、Handoff、Review 和验证证据范围；`src/**`、`tests/**`、`packaging/**`、`src-tauri/**` 及 Contract 均未改动。`git diff --check 90c3e459 bcef79e7` exit 0。固定 base 到集成 merge 的整体比较为 34 路径：除 Owner 的 27 路径外，首父 master 已含 8 个释放/改派登记路径，其中 `doc/tasks/M2-S3.md` 与 Owner 范围重叠，另 7 个为治理与释放/改派证据。整体比较的禁止产品路径仍为零，`git diff --check 90c3e459 6799c73a` exit 0。

唯一 add/add 冲突为 `doc/tasks/M2-S3.md`。按“master 为基 + Owner 回填”保留 Owner 完成记录；合并结果 Task blob 与 Owner tip 的 Task blob 一致。Contract blob 在 Owner tip 为 `fc35913801297ee1876ea395f9c5041a16226f20`，集成后保持一致。

## Review 边界与增量核查

DeepSeek Harness 的非作者 Review 报告 `doc/reviews/M2-S3-233d0901.md` 决定 `approved`，绑定 `reviewed_head=233d0901`，0×P0/P1、5×P2 非阻断、5×P3 advisory。DSH headless 环境无法运行 shell，报告将范围命令与探针复跑标为 `BLOCKED` 并以交叉核验替代。Review 不覆盖后来的 `bcef79e7`；报告仍保留原固定 head 与原始 disposition。

Codex 逐项检查 `233d0901..bcef79e7` 的差异。代码差异仅在 `experiments/M2-S3/ui/index.html`：F-01 将 P-04 改成对页面可见 URL 的程序化记录与检查；F-04 将网络错误分类为失败，只有撤销后获得类型化重新解析结果才判定“未观察到缓存绕过”。报告、Task、环境表与泄漏扫描记录同步更正或细化。未发现阻断问题；上述结论仅覆盖该增量，不将 DSH 批准外推到新 head。

Review 报告由 DSH headless 会话产生。派发记录生成时记为未提交交付，Owner 后续 commit `bcef79e7` 已将该报告与派发记录纳入版本控制；没有独立冻结的原始文件摘要可供逐字节比对，因此本核验只确认集成所用提交内文件与报告内容，不声称完成外部原件 hash 对照。

## Codex 集成验证

本机 Windows 11、PowerShell 7.6.6、Python 3.14.6、Rust/Cargo 1.98.1、WebView2 Runtime 153.0.4234.48。验证产物均保存于本目录。

| 检查 | 结果 | 证据 |
|---|---|---|
| 生成合成 fixtures | exit 0 | `fixture-generation.log` |
| `cargo build --release --locked` | exit 0；有 2 条非致命 Rust warning（`unused_mut` 与未处理 `Builder.run` Result） | `cargo-build.log` |
| WebView2 探针独立运行 1、2 | 各 exit 0，16/16 PASS；场景状态序列相同 | `probe-run-1.log`、`probe-results-codex-1.json`、`probe-run-2.log`、`probe-results-codex-2.json` |
| symlink 补充运行 | exit 0，16/16 PASS；N-09 对映射到 scope 外的 symlink 目标返回 403 `REF_OUT_OF_SCOPE` | `probe-symlink.log`、`probe-results-symlink-codex.json` |

补充运行以合成 fixture 中的 `linkj` junction 换成指向 scope 外目标的 symlink；结果 ID 沿用矩阵中的 `N-09-junction-escape`，因此本次记录按 symlink 输入解释，不冒称为另一套结果 ID。源代码与探针代码未更改。fixture 生成前后 tracked icon SHA-256 均为 `5B34EE0227DE7D06738DE1888B480BA232A67FDA08BE1A64032CA91FBB693CF`。

## Findings disposition 与结论边界

- F-01..F-05：Owner 在 `bcef79e7` 按 DSH 指引完成修复/更正；Codex 检查增量并对最终探针复跑。DSH 报告本身不改写。
- F-06：拒绝码子集与 `REF_NOT_FOUND` 的显式清单仍为 advisory，延至实际触碰该错误码映射/Contract 的任务。
- F-07：Tauri 精确版本已补记；revision-change 场景与 300 s sliding TTL 仍 `NOT_RUN`，保留 advisory。
- F-08：Owner 将泄漏 verdict 限定为 host-side 路径/映射泄漏，并逐项分类两条攻击 URL 命中；不声称扫描结果 JSON 不含映射数据或 fixture stem。
- F-09：官方文档 URL/版本仍未补；Review 认定非阻断，作为 advisory 留档。
- F-10：本集成新增 symlink 专项复跑通过，补足本机 symlink 逃逸拒绝观察；探针结果 ID 为 `N-09-junction-escape-at-resolve`。报告中“Owner 原始运行未构造 symlink”的历史记录仍为真；不改写 Review/研究报告。

本任务只关闭研究探针 Gate。S1-B1=`PASS` 的适用边界仍为单宿主、Rust 模拟映射表、一次性 body、非打包运行。真流式在途窗口、revision fingerprint 绑定、300 s 滑动续期、S1-B3/B5/B6/B8、产品 pytest 与 IPC runtime 均未由本任务验证；其中 S1-B6 仍待 runtime 通道存在后测量。M2-C2 F-01..F-04 继续 deferred 至下一次实际修改 Contract 的 Task。大媒体 runtime 未释放。

## Git 历史保全状态

集成未改写提交历史。Owner 分支仍指向 `bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`，Owner worktree 保持干净；原 DeepSeek Harness worktree 保持在 `90c3e45962733799d43e3aefacf4fea99f662a2c` 且干净、授权已撤销；用户主工作区的预存 dirty 内容未触碰。
