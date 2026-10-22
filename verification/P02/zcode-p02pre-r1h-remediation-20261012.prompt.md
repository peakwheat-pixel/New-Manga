# P02PRE-R1H Owner remediation — ZCode

你是当前 Task Owner（ZCode），不是 Reviewer 或 Integrator。请接续同一 R1H Task 的独立 Review findings。Codex 负责最终 pins、独立 Review/adjudication 与集成。

## 仓库、Task 与冻结输入

- 唯一项目仓库：`G:\CODEX\New Manga`。先读其 `AGENTS.md`、`doc/09_COLLABORATION.md`，以及下面冻结 Task/manifest/review/adjudication；这些主仓文件只读。
- 当前执行目录是你的独立 linked worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-zcode`。
- branch=`agent/zcode/P02PRE-R1H`；base/current input HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38`；base ancestor=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；tree=`a1a36dcb71d1d8718b21eb12ba2f778a95955f29`；派发前受控 status clean（exit=0，stderr=0，0 records）。不要 reset、clean、stash 或重写历史。
- Task `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H.md`：10277 bytes / SHA-256=`28BA063D8096C6027B61BBB49069C2EEE77AAF06AB67AF8DD565101FE81D79B6`。
- Frozen manifest `G:\CODEX\New Manga\verification\P02\p02pre-r1h-manifest-20261012.md`：4760 / `28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74`。
- 首轮非作者 Review `G:\CODEX\New Manga\verification\P02\codex-subagent-p02pre-r1h-static-review-20261012.md`：2308 / `4BB1D8B8C8FACD96C4C087774756A71D79F832F10AD75026ADA3800579EE6688`。
- Codex adjudication `G:\CODEX\New Manga\verification\P02\p02pre-r1h-review-adjudication-20261012.md`：1543 / `20EA61BC98F5826BF7FDF487E01B3F34CF6FBA609E9C3999C242100920268497`。
- Review input post-pins `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-review-input-pins-post-20261012.json`：2070 / `9AA0A6783B9466BD146DB04A65FC61287144C6ADA5B6747AE5958538251BCDB4`。

## 唯一允许的写入范围

只编辑并提交当前 worktree 中以下三个 candidate 文件：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

不得修改主仓中的 Task、manifest、Plan/STATUS/Index、任何 Review/adjudication/checkpoint、R1G 文件、其它文件或全局配置。只提交新 delivery commit；不要合并主线。若路径、branch、HEAD、base、输入 pin 任一不符，停止并报告。

## 必须逐项修复 Review findings

1. **R1H-001 / P1：冻结 Git status/index 基线。** 非-reparse skip 前，必须在任何 inventory/skip 前证明 main 与 scratch 的 refs、`.git/index`、及精确 status `--porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload` 与可核验的冻结基线一致。Task/manifest/R1G 证据若没有冻结的完整 status/index expected values，就必须保持 `STOP / UNPROVABLE`，禁止该非-reparse skip；不得编造值、把运行时即时采样伪称旧基线、修改 manifest 或放宽条件。两个仓库都检查完毕前不能在任一仓库进入可 skip inventory。
2. **R1H-002 / P2：保留 Git stage。** 每个 index entry 必须保留并核验 `mode`、`stage`、唯一性；仅唯一 stage=0 允许分类。stage 1/2/3、重复/冲突、未知 mode、格式异常都立即 fail-stop。
3. **R1H-003 / P2：证明 ordinary file。** 仅使用既有 manifest 已允许的 `Get-Item` metadata。必须以明确白名单证明普通文件；Device、目录、unknown provider/object/type/属性均 STOP。不得追加 target 解析、内容读取/hash、ACL、子项枚举或 getter。
4. **R1H-004 / P2：实际 AST 自检。** 修复被注释打断的 regex。self-check 应绑定真实 `Get-RepositoryRecord` AST skip branch、其 break 与外层 continue 顺序，静态拒绝 skip branch 内的内容读取/hash、ACL、枚举、target/path 解析读取和写入。添加 baseline mismatch、stage 1–3/重复、Device/unknown 类型的负例；断言能力不足就 fail-check，不得宣称超出覆盖面的保证。

## 操作限制与交付验收

- 允许阅读上述输入和当前三份 candidate source；可运行 `git diff --check`。不得运行 PowerShell parser/self-check、测试、preflight、capture、getter 或任何 OS/profile/registry/ACL 检查；不得 Build/Cargo 或执行 AC1–AC7；不得查询、安装、启用、启动 Windows Sandbox。
- 不读取、跟随、打开或哈希 `.tmp.driveupload` 或任何 tracked symlink target；Git status 时必须以独立 argv 传入 `:(exclude).tmp.driveupload`。
- 首先判断现存冻结 status/index baseline 是否完整可核验。无则如实写 `UNPROVABLE`，保留 fail-stop；不得为让 capture 通过而推断。
- 更新 Handoff：列出四个 finding 状态/代码位置；说明 frozen baseline 是否存在、证据来源；若不存在，明确 capture 禁止且 `STOP / UNPROVABLE`；parser/self-check/preflight/capture/Build/Cargo/AC 均 `NOT_RUN`；不得写任何 Gate PASS。
- 提交新的 delivery commit；交付 branch、base、HEAD、tree、精确三文件 diff、受控 clean status（排除 pathspec）、`git diff --check` 结果及三个文件的 bytes/SHA-256 pins。Owner 不自审；不做 Review 或集成。

## 当前 Gate（原样保留）

`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`。
