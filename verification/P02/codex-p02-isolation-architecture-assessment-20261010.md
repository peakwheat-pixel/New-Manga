# P02 隔离架构替代可行性：独立 Windows VM 候选

日期：2026-10-10；Owner/Integrator：Codex；Independent Reviewer：/root/orchestration_docs_review（待固定对象 Review）。
研究基线：G:/CODEX/New Manga，main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b；开始状态项=392。配置由本机会话轨迹确认：gpt-6.1-sol/high。
状态：STATIC_CANDIDATE / REVIEW_PENDING / NOT_RELEASED。本文是 P02 证据，不是第二规划源；排期/释放仍由 REBASELINE_PLAN 与 STATUS 管理。

## 1. 判断与适用范围

可以通过替换构建/验收运行环境，设计一条不需要本项目自建宿主 AppContainer profile 的路线，从而移除目前 private-registry 创建前证明的技术依赖。推荐候选为独立、可丢弃的 Windows VM worker，构建和真实 Tauri/WebView2 验收都放在 guest 内。

这是有条件的架构判断，尚未确认本机 VM 能力、可用镜像、许可、资源或驱动。原 registry absence 仍为 UNPROVABLE / BLOCKED。移除机制依赖需要正式替换相关 Gate，不能将原证明记为 PASS/N/A，也不能将一台 VM 的存在作为新 Gate PASS。

产品继续使用 AD-001 的 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy；不切换技术栈、数据库写入者或四个一级页面。当前阻塞属于验证基础设施，不是业务架构缺陷。

## 2. 仓库证据

| 证据 | 已确认事实 | 对候选的约束 |
|---|---|---|
| doc/tasks/P02.md，来源与目标、AC1–AC7 | 需要真实 Windows Tauri/WebView2；部分 IPC/Core mock 必须明确标注；普通浏览器不能代替 | VM 必须有可操作的 Windows GUI 与真实 WebView2；AC 继续逐项验收 |
| P02 Task，本机验证裁决与 AppContainer 范围 | 本机验证已取代 Sandbox；用户 B 保留创建前 absence 条件 | 本次提问不是采用 VM/Sandbox 或放宽 B 的决定 |
| apps/desktop/src-tauri/build.rs | 构建前检查 Core sidecar bundle；缺失时停止；不会自动运行 PyInstaller | 独立 worker 仍要按冻结步骤准备 sidecar；不能捏造“Rust 已自动构建 Python” |
| apps/desktop/src-tauri/tauri.conf.json | frontendDist 与 Core sidecar bundle 资源路径固定 | 输入归档、guest checkout 与生成路径必须符合实际配置 |
| apps/desktop/frontend/package.json | 构建为 tsc 与 vite build | 把工具及其子进程整体移入 guest；改 UI 技术栈不能自动约束工具写入 |
| verification/P02/run-webview.ps1 与 harness/workbench_cdp_harness.py | 现有 Stage A runner/报告器仍受 Hard Barrier；live CDP/行为驱动未启用，AC1–AC6 注册为 BLOCKED | 新环境不会自动补齐真实 GUI harness；代码与验收剩余工作仍需交付 |
| scoped source search | 在所查 apps/desktop 与 P02 的 ps1/rs/py/wsb 文件中，未找到自建 AppContainer API 的实现 | 当前候选主要替换隔离方案文档与未来 runner，不主张全仓库绝对不存在相关逻辑 |

## 3. 候选数据流和信任边界

1. Codex 冻结明确的源码/driver/fixture commit 与逐文件 hashes。不得把主仓或 Owner worktree 的未知未提交内容整体打包。Task 当前行为基线、scratch 构建 pin 与 live root 不同，执行前必须建立明确对应关系，不能随意以最新 HEAD 替代。
2. 受控宿主管理器将固定输入归档通过只读介质送入 guest；不用在线挂载的宿主主仓、用户目录或凭据。具体介质、字节 hash、工具和宿主新增写入路径均待后续 manifest 精确冻结与审查。
3. 每轮从固定 Windows/工具链基线创建独立运行盘；源码 checkout、npm/Cargo/Python/PyInstaller 输出、TEMP/cache 和 synthetic 数据都位于 guest 的运行盘。候选不在宿主创建 NewManga AppContainer profile，不依赖 GetAppContainerRegistryLocation 来证明宿主 storage 缺失。
4. guest 内构建真实 Tauri 应用并完成 GUI 场景；host/guest 两侧分别记录 VM 身份、guest OS、进程树、配置、输入/二进制 hashes、时序和视觉数据。未知进程或跨边界写入仍阻断。
5. 运行停止后，由受控证据导出步骤仅输出冻结 allowlist 中的 JSON/日志/截图及必要固定产物；限制大小/数量，拒绝绝对路径、路径穿越与 reparse，按 hash 校验；不执行 guest 返回的脚本，也不把构建产物直接覆盖主仓/Owner 工作区。
6. 将结果固定并审核后，按 exact VM/运行盘身份清理本轮对象；独立验证基线可重用、运行盘可回收和恢复记录完整。不能删除来源不明 VM、镜像或历史文件。

所有输入、运行盘、缓存和导出路径目前均为 UNFROZEN，不授权执行。Hypervisor/管理服务会有自己的宿主状态与磁盘操作，不能宣称宿主零写入；其精确管理范围和与 protected assets 的关系必须另行列明。如果新的验收依然要求逐一证明每个 OS 后台写入路径，VM 本身也不解决该要求。

## 4. 需要被正式替换的 Gate 与保留的保护目标

| 原机制或 Gate | 新候选应证明的事实 | 当前状态 |
|---|---|---|
| 自建宿主 LPAC profile / private-registry 创建前证明 | 本项目执行路线不创建该宿主 profile；所有构建/运行副作用在已验证的 VM 边界内；相关旧条件逐项保留原状态并登记替代依据 | 替代未采纳；原 UNPROVABLE / BLOCKED |
| 主进程及所有子进程的 AppContainer 身份 | 构建/runner/应用/WebView/sidecar 的 guest 归属和完整生命周期；无宿主执行旁路 | NOT_VERIFIED |
| 宿主仅 scratch leaf 可写 | host manager 精确输出/配置范围；guest 无宿主驱动器、目录或设备可写映射；保护资产前后 hashes 和配置证据一致 | NOT_VERIFIED |
| 本机 TEMP/cache 路径重定向 | guest 内精确 TEMP/cache/output manifest；host 不执行构建 hooks；预置缓存来源/版本/完整性固定 | NOT_VERIFIED |
| protected directory denial 与 scratch 正向 canary | 针对新边界设计无用户数据风险的拒绝访问/guest 正向写入 probe；证明无 host 可写通道，不能只以 hashes 未变化推断访问被拒绝 | NOT_VERIFIED |
| 恢复/清理 | 源码输入不变、证据导出完整、本轮运行盘回收和 exact 对象清理，可从 checkpoint 接续 | NOT_VERIFIED |

需要明示的新风险与取舍：guest 内写入许可范围扩大到冻结运行盘；新增 hypervisor 管理宿主状态；guest GUI 结果只适用于记录的 OS/WebView/渲染环境。这些变化不能由本次静态评估自行获准。

## 5. AC1–AC7 如何继续验收

| AC | 必要证据；VM 提供环境，不能替代证据 |
|---|---|
| AC1 | 固定源码/二进制 hashes、真实 Tauri 与嵌入式 WebView2 进程/窗口身份、工具版本、真实/模拟边界 |
| AC2 | GUI 桌面上实际鼠标/键盘操作与可见结果、焦点、截图 |
| AC3 | 在 guest 同一单调时钟下记录 resolve/list_regions、取消/迟到结果、300ms 判别；不得用 host 远程画面延迟计时 |
| AC4 | 默认 300ms 配置下分别验证 retype/undo/restore 的 write→read 次序；mock IPC/Core 不能宣称真实数据库持久化 |
| AC5 | 真实 Tab/Shift+Tab/Enter/Space/Escape 与焦点；远程控制输入路线必须验证，不直接把协议调用冒充按键 |
| AC6 | guest 中 computed foreground/background、实际合成背景、ratio 与 token_mapping；显卡/软件渲染/会话条件记录，不能扩大为所有 Windows 宿主渲染 PASS |
| AC7 | 逐场景 PASS/FAIL/BLOCKED/NOT_RUN、原始证据、退出码、mock 面和 finding；独立 Review 与 Codex 集成验证分开 |

## 6. 路线比较

| 候选 | 对当前依赖的效果 | 判断 |
|---|---|---|
| 独立可丢弃 Windows VM worker | 有条件移除本项目自建宿主 AppContainer 的依赖，保留真实 Tauri/WebView | 优先静态候选；需要新 Gate/环境范围与独立 OS 证据 |
| Windows Sandbox 改为外层执行环境 | 同样可能替代机制，但不是原 B 的自动满足；默认共享面/持久化导出另需处理 | 用户禁令仍有效，不查询/启用/启动；本轮不选择 |
| 单独验证 Tauri host / 拆分 UI 与 Python 打包 | 可减少 hook/toolchain 范围；仍有构建和 WebView 子进程的宿主副作用；需修改原范围且可能改变 AC1 对象 | 次级后续优化，不能单独解除现行 Gate |
| 改成普通浏览器、Linux/WSL/Docker GUI 或重写产品栈 | 不能自动满足固定 Windows Tauri/WebView AC，也不能自行解决宿主写入闭包 | 不作为本轮方案；PySide6/QML 仅 Legacy |

## 7. 一手来源、保证与限制

- Microsoft [Hyper-V features and terminology](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/features-terminology)：virtual disks/differencing disks 支持保留基线和把变化放在子盘；这不是对本机配置或 protected hashes 的验证。
- Microsoft [Share devices with Hyper-V Windows virtual machines](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/enhanced-session-mode)：Enhanced Session 的 clipboard、drive/device redirection 是需要明确禁用或限定的宿主通道。不能只看 VHDX 隔离而忽略共享面。
- Microsoft [Hyper-V Integration Services](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/integration-services)：管理、数据交换、文件/服务交互需要冻结；不建议盲目禁用所有必需服务，须逐项列明需要的通道。
- Microsoft [Windows Sandbox overview](https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-overview) 与 [configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)：fresh/disposable 与 kernel isolation 不意味着私有 registry absence；可写映射仍可影响宿主。仅静态参考，未执行 Sandbox 命令。

上述网页是查阅时的一手内容，不是 immutable API/runtime support contract，也不证明环境已经可用。本文推荐是依据这些能力与仓库 Task 作出的设计推论。

## 8. 交付边界与下一步

本轮只交付静态可行性评估：没有运行或修改 VM/OS/API/registry/profile/ACL，也没有构建、测试、GUI 或 AC；未修改产品代码/AD-001/共享契约。用户 B、本机验证裁决与 Sandbox 禁令仍有效；全部现行 Gate 保持 BLOCKED / NOT_RUN。

后续候选 P02 内部隔离架构替代切片为 NOT_RELEASED：若用户明确采用此替代运行环境及对应 Gate 变化，Codex 先冻结 scope delta、精确输入/输出/管理/导出/清理 manifest 与新 Gate，再作独立 Review 和非构建 OS preflight；任一条件未知则 BLOCKED。不得提前执行 VM setup 或产品构建。

推荐后续责任：Codex 负责隔离契约和新 Gate，Antigravity 负责另行释放的 runner 编程（独立任务分支，worktree 待 Codex 创建），DeepSeek Harness 负责非作者运行证据 Review，Codex 最终集成验收。当前没有安全已释放的下一执行 Task；无需下一步操作。
