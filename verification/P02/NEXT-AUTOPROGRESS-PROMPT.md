# P02 自动续跑提示词

从`G:/CODEX/New Manga`持续推进权威项目路线图，默认简体中文。用户已授权安全且已释放的实现、检查、任务/worktree管理、提交与本地集成；持续到已授权工作完成或出现必须由用户决定的产品取舍。没有新授权不关机、不push、不发布、不部署、不执行破坏性用户数据操作。

## 每次恢复先核对

读取根`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、本提示词与`verification/P02/RESUME.md`。检查Live root和相关worktree/branch的HEAD、tree、common-dir、staged/unstaged/untracked、Task/Plan/Status和Gate证据。下面hash只作历史锚点，绝不代替Live Git。

P01已`done`，绝不重做。P02真实/Mock边界、AC1–AC7、Owner allowlist和退出判据已由scope r1–r4冻结并释放，不重冻结。P02行为验证基线为`241ff3b70b6fc0490ea238efd486cc707f849031`；Owner转移治理已集成于历史release commit `3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff`，独立Review `bfc8790a` approved且0 findings，Codex Gate/fast-forward/post-FF Gate均已完成。恢复时核对Live main与`verification/P02/owner-transfer-post-ff-gate.md`，不要重跑C-2同步或Owner转移Review，除非Live Git出现新漂移。

## 保护现场与协作

- FF前root dirty=38；集成两份Recovery后预期剩余36项既有dirty/untracked。P01保护manifest应为24/24、0 mismatch。以恢复点的path/status/hash复核当前现场；不得stage、stash、覆盖、清理或解释成P02的其它Agent内容。
- 旧ZCode worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`固定在`e1948466082b3cadbfde1da53b791319e359a10b`，`DRIFT_DETECTED`；24个Tauri生成文件行尾差异、`verification/P02/cargo-target/**`与`cdp_probe.py`均保留，不复用。中断的旧Antigravity会话曾使用错误worktree，不续用、不迁移。
- Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。Qoder已退出，绝不分配。Owner无真实接单和start checkpoint前，Task保持`ready / IDLE`。
- 所有测试写明真实/Mock层、命令、环境、Hash、EXIT、逐项PASS/FAIL/BLOCKED/NOT_RUN与skip原因。Chrome/Vite/JSDOM/mock/旧EXE不能冒充真实Tauri/WebView2；P02发现产品缺口只登记finding，不自行修产品UI、样式或debounce。

## 下一条直接执行

1. 核实当前Live main、治理文档同步状态和Post-FF Gate。若Plan/Status/Index/Task导航/RESUME仍指向旧`4b54f304`快进前Owner状态，先更新并仅提交明确授权的治理文档，重跑`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`python -B -X utf8 verification/P02/route-validator-mutation-probe.py`、`git diff --check`、P01 manifest与root dirty map。
2. 从最新集成后的release `main` HEAD创建目标branch=`agent/antigravity/P02-real-webview-harness`、worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`。如目标已存在，先核验而不覆盖。创建后设置worktree-local `core.autocrlf=false`，记录branch/HEAD/tree/common-dir/status，必须clean。
3. 使用Antigravity dispatch Skill执行**只读**Owner acceptance/start-intent握手：自包含说明P02 Task、worktree、行为base、scope SHA、允许/禁止路径和构建副作用限制；要求明确接受/拒绝，若接受则给出实现start checkpoint与第一步，但禁止修改/暂存/提交。保存真实CLI JSON、stderr、exit及conversation ID，并在worktree确认无文件变化。
4. 无真实接受或checkpoint时保持`ready / IDLE`并按Skill记录dispatch失败；不得声称已派发/开工。真实接受后，Codex先把Plan/Status/Task更新至`in_progress`并集成该状态，再快进Owner分支到最新main HEAD；随后在同一Antigravity会话发送正式实现任务并持续跟踪。
5. Tauri `build.rs`会写源码树，当前还缺少受信sidecar输入；`verification/P02/build-preflight-lf-r1.md`只是未运行build的前置调查。Cargo/Tauri/sidecar build之前，由Codex登记具体scratch worktree、生成/合成sidecar来源和准确命令，再交非作者Review；不得在Owner worktree直接触发构建器写入禁止路径。此技术安全门不改变P02已冻结的AC或产品范围。
6. Owner按AC1–AC7交付真实Tauri/WebView2证据与Handoff；DeepSeek Harness对固定head正式独立Review，Codex逐项复核allowlist、测试、恢复点与Integration Gate，再仅本地快进并做post-FF验证。Task未满足全部已释放AC前不得标`done`。完成后立即从权威Plan选择依赖已满足、范围已冻结的下一Task并继续，除非遇到真实用户产品裁决或外部不可逆动作。

保存Task-local恢复点，记录实际commit、验证命令和结果、owner session、dirty路径和下一条精确指令。始终以Live Git和当前项目文档为事实，不依据本提示的旧状态推断完成。
