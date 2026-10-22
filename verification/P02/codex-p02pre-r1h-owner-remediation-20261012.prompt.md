# P02PRE-R1H Owner implementation — Codex Executor subagent

你是 `P02PRE-R1H` 的 implementation Owner `/root/p02_r1h_codex_owner`，不是 Reviewer 或 Integrator。请在已建好的独立 linked worktree 接续首轮 Review findings。root `/root` 负责独立 Review 调度、adjudication、集成和后续验证。

## 冻结输入与工作目录

- 唯一项目仓库：`G:\CODEX\New Manga`。先读 `AGENTS.md`、`doc/09_COLLABORATION.md`，再读 Task、manifest、Review、adjudication；主仓所有文件只读。
- 你的唯一写入 worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`。
- branch=`agent/codex/P02PRE-R1H`；base/current HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38`；tree=`a1a36dcb71d1d8718b21eb12ba2f778a95955f29`；ancestor=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；controlled status clean（exit=0、stderr=0、0 records）。
- Task `doc/tasks/P02PRE-R1H.md`：11538 bytes / SHA-256=`95AC04FABD0EBFC1B97AF1B0C37F8B24AF62B7E8C1346057E0826AEA726E85CA`。
- Frozen manifest `verification/P02/p02pre-r1h-manifest-20261012.md`：4760 / `28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74`。
- 首轮 Review `verification/P02/codex-subagent-p02pre-r1h-static-review-20261012.md`：2308 / `4BB1D8B8C8FACD96C4C087774756A71D79F832F10AD75026ADA3800579EE6688`。
- Codex adjudication `verification/P02/p02pre-r1h-review-adjudication-20261012.md`：1543 / `20EA61BC98F5826BF7FDF487E01B3F34CF6FBA609E9C3999C242100920268497`。
- Review post-pins `verification/P02/codex-p02pre-r1h-review-input-pins-post-20261012.json`：2070 / `9AA0A6783B9466BD146DB04A65FC61287144C6ADA5B6747AE5958538251BCDB4`。
- 当前 candidate 输入 pins：`p02pre-r1h-capture.ps1` 85038 / `B236D70F235D14ACE16544CE361B8CC979100635C3EC738D32ED379EDA086C95`；`p02pre-r1h-selfcheck.ps1` 14375 / `3A3779FBE299815FE7176B55E02F13E32D707610BB25908F192AF28F4B29B972`；`p02pre-r1h-handoff-20261012.md` 13408 / `7F04106FD22655D238AC5A44AE34C6B93EE2C3E120C9E28AD139948734E9AD31`。
- ZCode CLI 因本机缺少 provider config 无法派发；Antigravity 两次 dispatch stalled/timeout 后均确认进程树停止、原 worktree clean。现由可用 Codex Executor subagent 接任；这不更改产品范围或 AC。

## 严格写入范围与交付

只可修改并提交以下三个现有 candidate 文件：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

不得修改主仓、Task、manifest、Plan/STATUS/Index、checkpoint、Review/adjudication、R1G 文件或其它路径。不得 reset、clean、stash、覆盖或删除任何内容。新 delivery 只提交到当前 branch。若 branch/base/HEAD、Task/manifest/review pins 或现有 candidate pins 不符，停止并报告。

## 必须修复四项独立 Review findings

1. **R1H-001 / P1：冻结 Git status/index 基线。** 运行任何 inventory/skip 前，必须同时确认 main 与 scratch 的 refs、`.git/index`、及完整 status `--porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload` 与可核验冻结值精确匹配。现有 Task/manifest/R1G 资料没有冻结的完整 status/index expected values；因此候选应保留 `STOP / UNPROVABLE`，非-reparse skip 不允许执行。不得编造 hash、把本次采样冒称冻结值、修改 manifest 或放宽要求。两个仓库基线检查完成前不得让任一仓库进入可 skip inventory。
2. **R1H-002 / P2：index stage。** Parser 必须保留每个 entry 的 mode 与 stage，并拒绝 stage 1/2/3、重复/冲突路径、未知 mode 与格式错误；只有唯一 stage=0 可继续分类。
3. **R1H-003 / P2：ordinary leaf。** 只能用现有已批准的 metadata 查询明确白名单证明普通文件。目录、Device、未知 provider/object/type/属性 fail-stop。不得增加 target 解析、内容读取/hash、ACL、枚举、getter 或 API。
4. **R1H-004 / P2：AST self-check。** 修复当前 comment 导致的 regex 误判；断言绑定实际 `Get-RepositoryRecord` 的 branch、break 与外层 continue 路径，证明 skip branch 不会执行内容 hash/读取、ACL、目录枚举、target/path resolution/read 或写入；补 baseline mismatch、stage 1–3/duplicate、Device/unknown object 反例。检查无法证明时 fail-check，不输出超范围安全保证。

## 执行限制与验收

- 可阅读精确 source 与 frozen inputs，允许运行 `git diff --check`。禁止运行 parser、自检、测试、preflight、capture、host getter、ACL/registry/profile 相关查询或 API；禁止 Build/Cargo、AC1–AC7 及 Windows Sandbox 查询、安装、启用或启动。
- `.tmp.driveupload` 和 tracked symlink target 严禁读取/跟随/打开/哈希。Git status 必须以独立 argv 传入 `:(exclude).tmp.driveupload`。
- Handoff 必须列四项 finding 及 disposition/code location；确认 status/index baseline 不存在时写 `STOP / UNPROVABLE` 且禁止 capture；parser/self-check/preflight/capture/Build/Cargo/AC=`NOT_RUN`；不宣称 Gate PASS。
- 提交新的 delivery commit。报告准确 branch/base/HEAD/tree、三文件 exact diff、controlled clean status、`git diff --check` 结果和三个文件的 bytes/SHA-256。Owner 不做 Review 或 integration。
- 当前治理 Gate 必须原样保留：`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`。
