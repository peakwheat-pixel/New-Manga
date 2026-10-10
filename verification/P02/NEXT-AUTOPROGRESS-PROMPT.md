# P02 自动续跑提示词

从`G:/CODEX/New Manga`持续推进权威项目路线图，默认简体中文。用户已授权安全且已释放的实现、检查、任务/worktree管理、提交与本地集成；持续到已授权工作完成或出现必须由用户决定的产品取舍。没有新授权不关机、不push、不发布、不部署、不执行破坏性用户数据操作。

**最新用户裁决（2026-10-10，优先于本提示内的旧 Sandbox 步骤）：**P02/P04 本机 Windows 验证按项目验收口径等同于 Windows Sandbox 验证，不查询、安装、启用或启动 Windows Sandbox Feature，不做 guest 验证。P02 Build Gate 仍因 hook/cache/子进程写入边界未闭合而 `BLOCKED`；不得把 WSB 免测写成 Build Gate/AC PASS。P04 已释放 `ready` 供测试代码实现，Cargo/Tauri 运行仍需 Codex 先通过 P02 本机 Build Gate 并提供 provenance-bound scratch sidecar。全产品干净 Windows 发布 Gate 与数据保护不变。详细事实以 [P02 Task](../../doc/tasks/P02.md)、[STATUS](../../doc/STATUS.md) 和 [当前 checkpoint](codex-checkpoint-local-validation-r1.md) 为准。

## 每次恢复先核对

读取根`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、本提示词与`verification/P02/RESUME.md`。检查Live root和相关worktree/branch的HEAD、tree、common-dir、staged/unstaged/untracked、Task/Plan/Status和Gate证据。下面hash只作历史锚点，绝不代替Live Git。

P01已`done`，绝不重做。P02真实/Mock边界、AC1–AC7、Owner allowlist和退出判据已由scope r1–r4冻结并释放，不重冻结。P02行为验证基线为`241ff3b70b6fc0490ea238efd486cc707f849031`；Owner转移治理已集成于历史release commit `3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff`，独立Review `bfc8790a` approved且0 findings，Codex Gate/fast-forward/post-FF Gate均已完成。恢复时核对Live main与`verification/P02/owner-transfer-post-ff-gate.md`，不要重跑C-2同步或Owner转移Review，除非Live Git出现新漂移。

## 保护现场与协作

- FF前root dirty=38；集成两份Recovery后预期剩余36项既有dirty/untracked。P01保护manifest应为24/24、0 mismatch。以恢复点的path/status/hash复核当前现场；不得stage、stash、覆盖、清理或解释成P02的其它Agent内容。
- 旧ZCode worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`固定在`e1948466082b3cadbfde1da53b791319e359a10b`，`DRIFT_DETECTED`；24个Tauri生成文件行尾差异、`verification/P02/cargo-target/**`与`cdp_probe.py`均保留，不复用。中断的旧Antigravity会话曾使用错误worktree，不续用、不迁移。
- Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。Qoder已退出，绝不分配。Owner无真实接单和start checkpoint前，Task保持`ready / IDLE`。
- 当前真实接单：Antigravity已`ACCEPT`，conversation=`054911c9-b133-4514-b471-143b80249fce`，CLI=`agy 1.3.2`，JSON `SUCCESS` / EXIT=0；start checkpoint=`agent/antigravity/P02-real-webview-harness@3c651f502d49de32f5b050cfefc1ea056354f663`、tree=`f8e32f9b64b0f0b1dbcfc14c74f2649c61629f7f`、clean。Task状态由Codex登记为`in_progress / ACTIVE`后，不重复接单握手；通过同一conversation续接正式实现任务。acceptance原始证据=`verification/P02/antigravity-owner-acceptance-r1.*`。
- 所有测试写明真实/Mock层、命令、环境、Hash、EXIT、逐项PASS/FAIL/BLOCKED/NOT_RUN与skip原因。Chrome/Vite/JSDOM/mock/旧EXE不能冒充真实Tauri/WebView2；P02发现产品缺口只登记finding，不自行修产品UI、样式或debounce。

## 下一条直接执行

1. 核对Live Task=`in_progress / ACTIVE`、Plan/Status/路线图计数一致、acceptance JSON 与 session migration 证据；确认owner branch/worktree clean并快进到当前main。P01不重做、P02 scope r1–r4不重冻结、Owner转移Gate不重跑。
2. 在同一 Antigravity conversation=`054911c9-b133-4514-b471-143b80249fce`发送[`formal implementation prompt`](antigravity-owner-implementation-r1.prompt.md)，从最新集成的main checkpoint开始。先完成允许范围内的只读环境盘点、构建输出目标存在性检查、synthetic fixture与只读probe；不得修改Task禁止路径。
3. 继续完成P02 AC1–AC7及证据，但Cargo/Tauri/sidecar build之前，Codex必须登记具体scratch worktree、隔离输出路径、synthetic/可信sidecar来源和准确命令，再交非作者Review批准。`verification/P02/build-preflight-lf-r1.md`仅为未运行构建的调查；不能据此在Owner worktree直接构建。
4. 禁止将Chrome/Vite/JSDOM/mock/旧EXE/fake timers冒称真实Tauri/WebView2/Core证据。产品缺口只记录finding；不改UI、token、debounce、键盘/焦点或性能，不读用户漫画库/生产数据。
5. Owner交付后由DeepSeek Harness对fixed head正式独立Review；Codex逐项复核allowlist、测试、恢复点与Integration Gate，再仅本地快进并做post-FF验证。全部AC未满足前不得标`done`。完成后立即从权威Plan选择依赖已满足、范围已冻结的下一Task并继续，除非遇到真实用户产品裁决或外部不可逆动作。

保存Task-local恢复点，记录实际commit、验证命令和结果、owner session、dirty路径和下一条精确指令。始终以Live Git和当前项目文档为事实，不依据本提示的旧状态推断完成。
