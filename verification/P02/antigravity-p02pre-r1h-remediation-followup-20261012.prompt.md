# P02PRE-R1H Owner remediation — Antigravity follow-up

你是本轮 Task Owner（Antigravity），不是 Reviewer 或 Integrator。请修复同一 P02PRE-R1H 的首轮独立 Review findings。Codex 负责验收、独立 Review/adjudication 与集成。

## 冻结仓库、Task 与交付基线

- 项目根：`G:\CODEX\New Manga`。先读 `AGENTS.md`、`doc/09_COLLABORATION.md` 与以下冻结输入；这些主仓文件只读。
- 唯一可写 linked worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`。
- branch=`agent/antigravity/P02PRE-R1H`；base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；当前 HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38`；tree=`a1a36dcb71d1d8718b21eb12ba2f778a95955f29`；派发前 controlled status clean（exit=0、stderr=0、records=0；`:(exclude).tmp.driveupload` 为单独 argv）。不得 reset、clean、stash、覆盖或删除任何现有内容。
- Task：`doc/tasks/P02PRE-R1H.md`，10759 bytes / SHA-256=`8DE084E456DFAD6AB11ADA6E4EB26F57053C34E229B6CBA41F978698A530FCBE`。
- Frozen manifest：`verification/P02/p02pre-r1h-manifest-20261012.md`，4760 / `28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74`。
- 首轮 Review：`verification/P02/codex-subagent-p02pre-r1h-static-review-20261012.md`，2308 / `4BB1D8B8C8FACD96C4C087774756A71D79F832F10AD75026ADA3800579EE6688`。
- Codex adjudication：`verification/P02/p02pre-r1h-review-adjudication-20261012.md`，1543 / `20EA61BC98F5826BF7FDF487E01B3F34CF6FBA609E9C3999C242100920268497`。
- Review post-pins：`verification/P02/codex-p02pre-r1h-review-input-pins-post-20261012.json`，2070 / `9AA0A6783B9466BD146DB04A65FC61287144C6ADA5B6747AE5958538251BCDB4`。
- 先前 Antigravity dispatch session=`66982` 约 16 分钟无任何结果，由 Codex 中断；当时进程树已确认退出，原 worktree clean。ZCode CLI=`0.16.9` 随后因找不到 `zcode-builtin.json` Provider 配置 exit=1，未获得响应或修改代码。现在按项目故障转移再次由 Antigravity 接任；这是新的独立 dispatch。

## 唯一写入范围与交付

只编辑并提交以下三个 candidate 文件，不得改 Task、manifest、Plan/STATUS/Index、Review/adjudication、checkpoint、R1G 文件或其它路径：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

提交新的 delivery commit；报告 branch/base/HEAD/tree、精确三文件 diff、受控 clean status、`git diff --check` 与三个文件的 bytes/SHA-256。Owner 不自审、不集成。

## 必须修复的四项 findings

1. **R1H-001 / P1：冻结 Git status/index 基线。** 在任何 inventory/skip 前，须证明 main 和 scratch 的 refs、`.git/index` 和精确 status `--porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload` 与可核验冻结值相符。Task/manifest/R1G 没有完整 status/index expected values 时，保持 `STOP / UNPROVABLE`，禁止 non-reparse skip；不得猜值、把执行时现采值冒充冻结基线、修改 manifest 或放宽条件。两个仓库都完成检查前，不得让任何仓库进入可 skip inventory。
2. **R1H-002 / P2：保留 index stage。** 每个 entry 保留 mode/stage 并核验唯一性；仅唯一 stage=0 可参与分类。stage 1/2/3、重复/冲突、未知 mode 或格式异常立即 fail-stop。
3. **R1H-003 / P2：ordinary file 白名单。** 仅用既有允许的 `Get-Item` metadata 明确证明普通文件；Device、目录、unknown provider/object/type/属性均 STOP。不得新增 target 解析、内容 hash/读取、ACL、子项枚举或 getter。
4. **R1H-004 / P2：实际 AST 自检。** 消除被注释打断的 regex；断言需绑定真实 `Get-RepositoryRecord` AST branch、break 与外层 continue 顺序，并检测 skip branch 内无内容读取/hash、ACL、枚举、target/path 解析读取和写入。添加 baseline mismatch、stage 1–3/重复 entry、Device/unknown 类型负例；检查能力不足就 fail-check，不得虚报保证。

## 禁止操作与当前 Gate

- 只可阅读 Task/manifest/Review/adjudication 和当前三份 candidate source；可运行 `git diff --check`。禁止 parser/self-check、tests、preflight/capture/getters、OS/profile/registry/ACL checks、Build/Cargo、AC1–AC7 与任何 Windows Sandbox 查询/安装/启用/启动。
- 不读取、跟随、打开或哈希 `.tmp.driveupload` 和任何 tracked symlink target；Git status 的 `:(exclude).tmp.driveupload` 必须是独立 argv。
- Handoff 逐项列出四项 finding 的状态与代码位置；准确说明是否存在可核验 frozen status/index baseline，缺失时写 `STOP / UNPROVABLE` 且 capture 禁止；parser/self-check/preflight/capture/Build/Cargo/AC 均 `NOT_RUN`。不得宣称任何 Gate PASS。
- 保持 Gate 原值：`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`。
