---
task_id: RELEASE-PACKAGE-PROBE-1
reviewer: DSH 子 agent `review-gate4-probe`（root agent `lead` 派发；全新上下文；未参与实现与证据产出）
reviewer_kind: subagent
author: DSH（commit `7220a261d`，author peakwheat-pixel）
base_commit: 5dda04437
reviewed_head: 7220a261d8a1220ecfbf1b5f27c829273e36ae76
decision: changes_requested
---

# RELEASE-PACKAGE-PROBE-1 独立复核 r1

## 0. 审查者、来源、范围与只读约束

- **审查者**：DSH 子 agent `review-gate4-probe`（由 root agent `lead` 派发；独立上下文；未参与本卡的 publish、证据采集或文档撰写）。
- **被审 head**：`7220a261d8a1220ecfbf1b5f27c829273e36ae76`（`docs(gate4): 条件 4 打包探测……`，2026-11-15 02:59:20 +08）。基线 `5dda04437d68baf304b4364a3a73f9dfa217d943`。
- **被审对象**：`doc/tasks/RELEASE-PACKAGE-PROBE-1.md`；`doc/reviews/MAINT-1-GATE-CONDITION-4-PROBE-2026-11-15.md`（主交付）；`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §16；`verification/RELEASE-PACKAGE-PROBE-1/` 六个文件；同步改动 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`。
- **只读约束**：除本报告外未修改仓库任何文件；未重跑 publish（用户明确要求不覆盖产物）。复核前后 `git status --short` 为空（本报告落盘前）。为读截图细节，在 `%TEMP%` 生成过两张放大裁剪图（仓库外，不影响 `git status`）。
- **边界**：本 Review 只对上述 head 有效；任何新 commit 或新证据都会使其成为历史记录。本报告不构成对"条件 4 已满足"的承认。

## 1. 结论（verdict）

**REJECT / changes_requested。**

- **"包构建 + 启动冒烟真实通过"这一半我独立核实为真，应予保留**：产物、哈希、目录内容、`host_ready` 语义、退出路径都对得上（见 §4）。
- **但主交付的两个"总结论"至少一个为假、一个为误读**：
  1. **P1**："PyInstaller MISSING，因为 **PyPI 不可达**"不成立。本复核在同一台机器、同一 pip 配置下实测：默认 index（清华镜像）确实返回 `from versions: none`，但 **`https://pypi.org/simple` 在本地代理下成功下载 `pyinstaller-6.22.3`** —— 恰好等于 `packaging/m2ac5/requirements-build.txt` 的钉死版本。因此"真实阻塞只剩 sidecar 重建（PyInstaller 不可得）"这一收窄结论不成立（详见 R-001）。
  2. **P2**："截图显示四页导航"是把 **3 个 space tab + 1 个 breadcrumb** 误读成四页导航；截图里第 4 个"资料柜"无编号、是 Breadcrumb（R-002）。
- 这不影响"首次真实产出绑定 head 的包并启动成功"的事实价值，但**影响这张卡交付的唯一核心结论**（卡在哪一步 / 缺什么），故不批准，需 r2 修正后复审。

## 2. 逐 AC 判定

| AC | 判定 | 依据（复核动作与结果） |
|---|---|---|
| **AC1 依赖清单** | **不满足**（P1/P2） | 9 项里 7 项与我的实测一致（SDK 9.0.308/10.0.401、runtime 9.0.11、sidecar 2026-10-23、三份 ONNX、makensis v3.13 可执行、LongPaths=1、G 盘 1216.9 GB、无代码签名证书）。但：①**PyInstaller 的判定错误**（R-001，MISSING 的理由不成立）；②AC1 明文要求的"**打包脚本本身**"没有作为一行依赖列出并给命令级证据（R-003）；③sidecar 重建还需要 Python 3.12 基础解释器与钉死的 ML 栈（`requirements-build.txt`：torch 2.14.0 等），依赖清单未列，"给了 PyInstaller 即可"不完整（R-003）。 |
| **AC2 真实尝试** | **满足** | `publish-release.ps1` 确实运行：manifest `publish_exit_code=0`、`publish_elapsed_ms=7681`、`command` 完整；`build-singlefile.log` 有 8 个项目 restore + 8 条 `->` 输出；产物 `NewManga.App.exe` 99,554,850 B，我复算 sha256 = `EA01C8C7…76ED` **与 manifest 完全一致**；目录内只有 exe + build log + png（无 sidecar）。见 R-006 的限定（热缓存增量构建，非 clean-room）。 |
| **AC3 绑定当前 commit** | **满足** | `manifest-singlefile.json:git_head` = `5dda04437d68baf304b4364a3a73f9dfa217d943`，与 `git rev-parse 5dda04437` **逐字符相同**；`git diff --stat 5dda04437..HEAD` 只含 `doc/**` 与 `verification/**`，**无 `src/**`/`apps/**`/`tests/**`**，故被探测 head 的源码与当前 HEAD 源码等价。 |
| **AC4 sidecar 版本诚实性** | **基本满足（有限定）** | 记录了 2026-10-23 构建时间与 `ReorderChapters`／`83e45cfe5`（我核实：该 commit 存在，2026-11-10 15:03:39 +08，标题含 `LibraryService patch/reorder/create`；`ReorderChapters` 在全仓 33 处命中）。"包能启动 ≠ 命令面完整"写明。但"等"未枚举，"FEA-12 之后 delete/trash 系列"无逐条对照；我尝试在 `core_service.exe` 里按 ASCII 搜 `ReorderChapters`/`DeleteBook` 均得到 -1，但同一文件里 `core_service`、`_MEIPASS` 可命中，说明**Python 字节码在压缩的 PYZ 内，二进制 grep 不能作为"命令缺失"的证据**——文档的"早于哪些命令"目前只有 mtime vs commit date 这一条间接证据（R-008）。 |
| **AC5 后续链条** | **结构满足、结论不成立** | §5 覆盖了 build/冒烟/setup/install/启动/升级回退/四页/卸载/sidecar/签名十行，`makensis` 与 `.nsi` 的 `File /r ${STAGE_DIR}\*.*`（`packaging/nsis/installer.nsi:121`）我核实存在且 `build-installer.ps1` 确会 probe 并跑 `/VERSION`（`apps/desktop-avalonia/scripts/build-installer.ps1:63-127`）。但"**真实阻塞只剩一项：sidecar 重建（PyInstaller）**"建立在 R-001 的错误归因上，需重写。 |
| **AC6 不虚报** | **满足** | 未声称条件 4 满足或可发布（§1、§6、§16 末段都写了）；`git status --short` 为空；`git ls-files verification/RELEASE-PACKAGE-PROBE-1` 恰为 6 个文件（4 文本 + 1 log + 1 png），**无二进制 exe/zip**；workspace 产物未被提交。 |

## 3. Findings

| ID | 级别 | 位置 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-001** | **P1** | 探测文档 §2 "PyInstaller" 行、§5 末行与结论段；Gate §16 第 4 行；Task 卡 AC1/AC5 测试表 | 把"默认 index 一次失败"归因成"**PyPI 不可达**"，据此宣布"条件 4 的真实阻塞只剩 sidecar 重建（PyInstaller 不可得）"。**该归因无区分性测试支撑，且在复核时刻被直接证伪**：PyInstaller（且是钉死的 6.22.3）可从 PyPI 下载。影响：Lead 会误判 sidecar 无法重建，可能因此推迟/放弃 Gate 条件 4 的关键路径。 | `python -m pip download pyinstaller --no-deps --only-binary :all: -i https://pypi.org/simple --timeout 20` → `Collecting pyinstaller` / `Saved …pyinstaller-6.22.3-py3-none-win_amd64.whl` / `Successfully downloaded pyinstaller`；同一命令换成 `-i https://pypi.tuna.tsinghua.edu.cn/simple`（pip 全局配置的 index）→ `ERROR: Could not find a version … (from versions: none)`；`pip config list`：`global.index-url='https://pypi.tuna.tsinghua.edu.cn/simple'`、`global.proxy='http://127.0.0.1:7890'`；`Test-NetConnection pypi.org -Port 443` = True、代理端口 7890 = True；`packaging/m2ac5/requirements-build.txt`：`pyinstaller==6.22.3`（与下载到的版本相同）。 | 把该行改为"**NEED_ACQUIRE（索引配置问题）**"或"可用（需 `-i https://pypi.org/simple`）"，并给出两条命令的对照输出；重写 §5 结论：真实阻塞不是"PyInstaller 不可得"，而是"sidecar 重建尚未执行 + 安装/卸载/四页矩阵尚未执行"；同时登记"重建还需要 Python 3.12（本机 `py -0p` 有 3.12）与钉死 ML 栈"。若探测时刻确有网络异常，须写明"时刻性"并给出区分性测试，不得写成环境结论。 | open |
| **R-002** | **P2** | 探测文档 §1 第 2 行、Gate §16 第 2 行 | "截图显示**四页导航**"与证据不符：截图顶栏是 `资料柜 1 · 工位 2 · 控制台 3`（3 个 space tab，`AppShellViewModel.cs:58-63`）+ Breadcrumb 渲染的当前空间名"资料柜"（`TopBand.axaml:18-21`、`Breadcrumb.axaml`、`AppShellViewModel.cs:1396`），**没有第 4 个页面 tab**；产品意义上的四页（书架/工作台/阅读器/设置）并不在 v2 顶栏。叠加 §4.3 自己写"不证明四页可达"，形成文内自相矛盾。 | 截图放大：`资料柜 1 | 工位 2 | 控制台 3 | 资料柜`（第 4 个无编号）；源码三处交叉印证 3 个 `SpaceTabItem`；Breadcrumb 首项 = 当前空间 label。 | §1/§16 改为"截图显示 v2 顶栏三个 space tab（资料柜/工位/控制台）+ 状态栏『Host 就绪』，**不显示**四页导航"；把"四页可达性未验证"从 §4.3 提升到 §1 的同一句里，避免摘要层误读。 | open |
| **R-003** | **P2** | Task 卡 AC1；探测文档 §2 | AC1 明文要求覆盖"**打包脚本本身**"，§2 的 9 行里没有这一项；同时 sidecar 重建的完整前置（Python 3.12 + `requirements-build.txt` 的 torch/doctr/transformers 等）未列，导致"缺什么"的判断不完整。 | `doc/tasks/RELEASE-PACKAGE-PROBE-1.md:51-53` 的 AC1 原文；§2 表格 9 行逐行比对；`packaging/m2ac5/requirements-build.txt` 与 `README.md:13`（基础解释器 Python 3.12.3）。 | 补一行"打包脚本（`tools/ci/publish-release.ps1`、`apps/desktop-avalonia/scripts/build-installer.ps1`、`packaging/nsis/installer.nsi`）FREE"，并在 sidecar 行的"需要什么"里写明 Python 3.12 与 ML 栈。 | open |
| **R-004** | **P2** | `tools/ci/publish-release.ps1:343-346` + smoke 证据 | `Invoke-Smoke` 在 `finally` 里删除整个 `smoke-<mode>-<guid>` 临时根，**`host.log`（host_ready 的真实依据）与 `core_service.stderr.log` 不复存在**；smoke JSON 记录的 `data_root`/`log_dir`/`theme_home` 全是失效路径，只剩一个 `.preview-lifecycle.lock` 残留。任何后验者都无法复核 host.log 两行原文，只能信脚本布尔值。 | `Test-Path G:\CODEX\New Manga.workspace\artifacts\publish\smoke-singlefile-b6f2bd45` = True，但递归仅剩 `data\derived\.preview-lifecycle.lock`（368 B）。 | 冒烟后把 `host.log`/两个 stderr log（或其中 `core_service ready`/`host_bridge ready` 两行的原文与 hash）复制进 `EvidenceDir`；至少在 smoke JSON 里记录匹配到的行。 | open |
| **R-005** | **P2** | Task 卡 Canonical Evidence / Resource Manifest；全仓测试与治理脚本 | 6 个证据文件没有任何 canonical pin（表为空）、Resource Manifest "待填"，`verify_pins.ps1` 只校验冻结契约的 pin，`check.ps1` 的 Resource Manifest 规则只在引用 JSON 时生效 → **没有任何机制会发现证据被替换/漂移，也没有失效条件登记**。这正是"探测结论在什么情况下失效"无人负责的根因。 | `tools/governance/verify_pins.ps1:1-28`（只做 contract pin 比对）；`tools/governance/check.ps1:94-116`（manifest 引用必须是 `verification/**` 的单个 JSON，本卡未引用）；`git grep -l "publish-release\|manifest-singlefile" -- tests` 仅命中脚本自身。 | 见 §6：补 canonical pins（6 个文件的 sha256）+ 在探测文档加"失效条件与重测命令"小节 + 在 Gate §16 标注"仅对该 head/该机器状态有效"。 | open |
| **R-006** | **P3** | 探测文档 §3；manifest `publish_elapsed_ms` | 7.7 s 是**热缓存增量构建**：脚本先删输出目录（`publish-release.ps1:373`）再 `dotnet publish`（未 `clean`、未 `--no-incremental`），`bin/obj` 是温的；因此"构建 PASS"为真，但**不代表干净机器/干净 clone 可在 7.7 s 或可在同条件下构建**。另：仓库无 `global.json`（`Directory.Build.props` 定 `net9.0`），SDK 选择落到 **10.0.401** 而非项目基线 9.0.x，manifest 只记录结果不记录"为何是 10"。 | 脚本 373 行删目录；`build-singlefile.log` 只有 restore+8 条输出（不区分"重新编译"与"已是最新"）；`Get-ChildItem -Filter global.json` 为空；`dotnet --version` = 10.0.401；`apps/desktop-avalonia/Directory.Build.props`：`<TargetFramework>net9.0</TargetFramework>`。 | 在 §3 或 §6 写明"热缓存增量构建，非 clean-room；SDK 未 pin（10.0.401）"；若后续要作发布证据，建议 `git clean -xdf` 后重建一次或加 `--no-incremental`，并考虑 `global.json`。 | open |
| **R-007** | **P3** | `publish-release.ps1:442`（`git_head = Get-RepoHead`） | `git_head` 是**manifest 生成时**的 HEAD，不是"构建输入对应的 commit"，也不检测脏工作区。本次时间线（build 02:55:47–02:55:55、manifest 02:56:12、`7220a261d` 02:59:20）无提交插入，且当前 `git status` 干净，故本卡结论不受影响；但作为 Gate 证据，方法上应拒绝脏树。 | reflog 与 manifest `generated_at` 对照；`git status --short` 为空。 | 在 publish 开始时记录 `git rev-parse HEAD` + `git status --porcelain`，脏树直接失败或记 `caveat`。 | open |
| **R-008** | **P3** | 探测文档 §4.1 | "早于 `ReorderChapters`（`83e45cfe5`）**等**命令"中的"等"未枚举；`FEA-12` 的 delete/trash 系列只有名称没有 commit/命令对照。二进制取证不可用（PYZ 压缩），只剩 mtime 间接证据。 | 见 §2 AC4 行；`git log -1 83e45cfe5` 与 mtime 2026-10-23 19:21 对照；ASCII 搜索 `ReorderChapters`/`DeleteBook` = -1，但 `core_service`/`_MEIPASS` 可命中。 | 至少把"早于哪些命令"落到可核验的清单（例如现行 registry 中 2026-10-23 之后新增的命令名列表，注明来源）；明确"二进制不可 grep"这一取证局限。 | open |
| **R-009** | **P3** | 探测文档 §0 第 1 段；Gate §16 | 条件原文引用写作 `13_RELEASE_GATE.md`，**无路径**；实际文件在 `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:28`（原文一致，我逐字核对）。 | `Get-ChildItem doc -Recurse -Filter "*RELEASE_GATE*"` 无命中；`Select-String audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 命中原文。 | 补全路径。 | open |
| **R-010** | **P3** | `doc/TASK_LEDGER.md`（本次同步改动） | 计数是**提交前快照**：`task files 611 / tracked by git 610 / untracked (drafts) 1 / non-terminal tracked 6`；提交后实际是 611 个非 README 的 task md（612 含 README）**全部 tracked**、非终态 7 个全部 tracked、untracked 0。`check.ps1` 仍 PASS，说明计数漂移无人守。 | 逐文件统计 + `git ls-files doc/tasks` + `git status --porcelain -- doc/tasks`（空）。 | 提交后重算，或注明"计数为生成时刻快照"。 | open |
| **R-011** | **P3** | 探测文档 §4.2 | "包不自包含 sidecar"判断**正确**（我核实：输出目录只有 exe+log+png；`Invoke-Smoke` 用外部 `--sidecar-dir=$SidecarDir`，`SidecarDir` 来自参数/环境变量并被 `Resolve-Path`），但未写清安装器 stage 必须把 sidecar 放到**哪个相对路径**：`SidecarLocator` 只认 `<exe 目录>/core-sidecar` 或 `<exe 目录>/resources/core-sidecar`（`apps/desktop-avalonia/src/NewManga.CoreClient/SidecarLocator.cs:42-43`）。 | 输出目录列举；脚本 289 行与 496-505 行；`SidecarLocator.cs:15-57`。 | §4.2 补一句目标布局，避免后续 stage"打进去了但放错位置"。 | open |

## 4. 我实际核实了哪些事实

| # | 命令/动作 | 结论 |
|---|---|---|
| 1 | `git status --short`；`git log -1 --stat`；`git rev-parse 5dda04437` | 工作区干净；HEAD `7220a261d`，改动仅 12 个 docs/evidence 文件；基线 `5dda04437d68baf304b4364a3a73f9dfa217d943` |
| 2 | 读 `manifest-singlefile.json` / `smoke-singlefile.json` / `manifest-summary.json` / `build-singlefile.log` / `four-pieces.log` | `git_head=5dda04437…`、`elapsed=7681ms`、`result=PASS`、`warning_codes=[]`、smoke 全字段与文档一致；four-pieces：check.ps1 PASS(3 WARN)、verify_pins 18/18、publish 1/1 PASS |
| 3 | `Get-FileHash artifacts\…\NewManga.App.exe`；目录列举 | 99,554,850 B，sha256 = `EA01C8C77358F35B0F15F43A0A496DFD3BF1A0E1B472ADF9C55C65F0A28C76ED`，**与 manifest 完全一致**；同目录仅 `NewManga.App.exe`、`build-singlefile.log`、`published-singlefile.png`，**无 sidecar** |
| 4 | `git ls-files verification/RELEASE-PACKAGE-PROBE-1`；`git ls-files -s` | 恰 6 个文件（manifest/summary/smoke/build log/four-pieces log/png），**无二进制产物** |
| 5 | 读 `tools/ci/publish-release.ps1:176-191, 252-366, 368-490` | `Wait-HostReady` 只匹配 `host.log` 的 `core_service ready` 与 `host_bridge ready` 两行；`host_ready` 是 `pass` 的必要条件之一；publish 前删除输出目录；`git_head` 在 manifest 生成时取 HEAD；smoke 后删除临时根 |
| 6 | 读 `HostRuntime.cs:1191-1245`；`CoreServiceClient.cs:431-484`；`HostLog.cs:15-55` | `core_service ready` 在 `CoreServiceClient.StartAsync` 之后才写；而 `StartAsync` 内部要做 `core.ping` 并要求 `ping.Ready==true` 且 protocol major 匹配，失败即抛 `StartupTimeout`/`HandshakeFailed`。→ **`host_ready=true` 不是脚本自证，是"Core 进程起来且 wire ping 成功"的真实信号**（但仍不证明命令面完整，文档这点写得对） |
| 7 | `& "C:\Program Files (x86)\NSIS\makensis.exe" /VERSION` | 输出 `v3.13`，`exit=0`（**真的可执行**，不仅是文件存在）；`Bin\makensis.exe` 与 `%LOCALAPPDATA%\tauri\NSIS\makensis.exe` 也存在；`Get-Command makensis` 无 → 确实不在 PATH |
| 8 | 读 `installer.nsi`；`build-installer.ps1:63-127` | `.nsi:12` 明文 `the package is unsigned (SmartScreen warning is the documented known limitation)`；`:121 File /r "${STAGE_DIR}\*.*"`；`:161` 明确 uninstall 不碰 `%APPDATA%\com.newmanga.desktop`；`build-installer.ps1` 会 probe `ProgramFiles(x86)\NSIS` 并跑 `/VERSION` 校验 v3.x |
| 9 | `Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert` | 0 个证书 → 文档"无签名证书"正确 |
| 10 | 读 `git log -1 83e45cfe5`；`git grep ReorderChapters` | `83e45cfe5` 存在（2026-11-10，标题含 `LibraryService patch/reorder/create`）；`ReorderChapters` 全仓 33 处 → 文档引用的 commit 与命令真实 |
| 11 | sidecar 目录列举 + 二进制字符串扫描 | 5 个 exe 均 2026-10-23 19:21；`core_service.exe` 68,887,500 B；ASCII 搜 `ReorderChapters`/`DeleteBook`/`TrashBook`/`GetLibraryTree`/`OpenHostSession` 全为 -1，但 `core_service`/`_MEIPASS` 命中 → **Python 字节码在压缩 PYZ 内，不能用该结果证明命令缺失**（文档未做此错误断言，但证据链应说明） |
| 12 | 读截图（含放大裁剪） | 1416×939；顶栏 `资料柜 1 · 工位 2 · 控制台 3 · 资料柜`（第 4 个无编号）；正文"书架还是空的"；底部左/右均显示 `Host 就绪` → **3 tab + breadcrumb，不是四页导航** |
| 13 | 读 `AppShellViewModel.cs:58-63`、`TopBand.axaml:16-21`、`Breadcrumb.axaml`、`AppShellViewModel.cs:1383-1404` | `SpaceTabs` 恰好 3 个；TopBand = SpaceTabs ｜ Breadcrumb ｜ 右侧栏；Breadcrumb 首项 = 当前 space label → 截图第 4 个"资料柜"是 breadcrumb |
| 14 | 读 `Directory.Build.props`、`NewManga.App.csproj`、`global.json` 搜索 | TFM = `net9.0`；无 `global.json`；`dotnet --version` = 10.0.401；`dotnet --list-sdks` 9.0.308/10.0.401；runtime 9.0.11 |
| 15 | `pip config list`；`pip download pyinstaller` 两个 index；`Test-NetConnection`；`py -0p` | 默认 index = 清华镜像 + 代理 7890；**镜像 → `from versions: none`；`-i https://pypi.org/simple` → 成功下载 `pyinstaller-6.22.3`**（= 钉死版本）；pypi.org:443 与代理端口均可达；本机有 Python 3.12 |
| 16 | `Get-ItemProperty LongPathsEnabled`；`(Get-PSDrive G).Free`；ONNX 列举 | 1；1216.9 GB；三个 ONNX 164/112/328 MB 均在 `task-envs/CORE-SLIM-2/models` |
| 17 | `Select-String audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` | 第 28 行逐字包含卡面引用的条件 4 原文（文档未给路径，见 R-009） |
| 18 | `git grep publish-release/manifest-singlefile -- tests`；读 `verify_pins.ps1`、`check.ps1` | **没有任何测试或治理脚本固定本卡结论**；pin 校验只覆盖冻结契约；证据目录无 pin |

## 5. 我没有验证的面

- **没有重跑 publish**（按要求，避免覆盖产物）。因此"7.7 s"是否可复现、"同一源码重建是否得到同 sha256"、"clean tree/`--no-incremental` 下的耗时"均未验证。
- **没有构建 `setup.exe`**、没有做 install/启动/升级回退/四页/卸载矩阵，也没有验证 `.nsi` 的 stage 布局是否与 `SidecarLocator` 期望一致。
- **没有重建 sidecar**：只验证了"PyInstaller 可下载"，未验证 `build_sidecar.ps1` 能否在本机（Python 3.12 + 钉死 ML 栈 + 权重 hash 校验）跑通。
- **没有复跑三项目测试**：`four-pieces.log` 里的 App 950/0/11、Host 321/0/74、CoreClient 186/0/26 是摘录，本卡未改代码，我未重跑。
- **没有验证 111 条命令的实际计数**：只核对了仓库多处记录的 `HostCommandRegistry.All.Count == 111` 口径；`four-pieces.log` 里 `api inventory | 合计 87` 是另一张表（`generate_api_inventory.py`），两者不矛盾但易混。
- **没有验证探测时刻（2026-11-14 18:56Z）的 PyPI 可达性**；只能证明复核时刻（2026-11-15 03:00+08）可用。但 R-001 的要点是"归因缺乏区分性测试"，与时刻无关：文档只跑了一个默认 index，就把结果写成"PyPI 不可达"。
- **没有验证截图是否为该次 smoke 的实时捕获**：只能证明它与 smoke JSON 的路径/尺寸/时间一致，且 png 在 smoke 期间写入（02:56:02）。

## 6. 测试能否固定住？失效条件与 staleness 登记

**结论：没有任何测试/门禁固定这份探测结论。** 具体：

- `git grep -l "publish-release\|manifest-singlefile" -- tests` 只命中脚本自身；没有任何测试断言 `Invoke-Smoke`/`Wait-HostReady`/`--sidecar-dir` 的语义。
- `verify_pins.ps1` 只校验冻结契约文件的 SHA-256；`check.ps1` 只在 Task 卡引用 `verification/**` 的 JSON 时检查其存在/非符号链接。本卡 Resource Manifest 仍"待填"、Canonical Evidence 为空 → 6 个证据文件**没有 pin、没有存在性守卫**。
- `four-pieces.log` 是人工拼接的快照（check.ps1 / verify_pins / api inventory / 测试数 / publish），不是可重跑的单一门禁；其中的 publish 段只重述 manifest。

**这份结论在下列情况下失效，应作为 staleness 登记：**

1. **head 变化**：产物只绑定 `5dda04437`；Gate 条件 4 要求"当前固定产品 commit"，任何新产品 commit（哪怕只改 `apps/**`）都会让第 1–2 步的绑定失效。
2. **sidecar 重建成功**：§4.1 的"2026-10-23 旧 sidecar 早于 ReorderChapters"立即过期；`E-2` 的根因也随之改变。
3. **`tools/ci/publish-release.ps1` 改变**：`Wait-HostReady` 匹配串、smoke 参数（`--exit-after`/`--sidecar-dir`/`--variant`）、输出目录清理、`git_head` 采集时机中任一改动，都会让"7.7 s / host_ready / 目录内容"的证据含义变化。
4. **`packaging/nsis/installer.nsi` 或 `build-installer.ps1` 改变**：unsigned 声明、`File /r`、makensis probe 顺序一旦变化，§1 第 3 行与 §5 的"工具具备"就要重判。
5. **本机状态改变**：makensis 卸载/升级、Python 3.12 移除、pip index/proxy 配置变化、磁盘/长路径设置变化。
6. **`.nsi`/SidecarLocator 的 stage 布局约定改变**：R-011 的"打进去"位置会变。

**建议（按优先级）：**

- 在探测文档加一节 **"本结论的适用条件与重测命令"**：固定 head + 复核日期 + 上述 6 条触发条件 + 最小重测命令（`pwsh tools/ci/publish-release.ps1 -Mode singlefile -SidecarDir …`、`pip download pyinstaller -i https://pypi.org/simple --no-deps`、`& "…\makensis.exe" /VERSION`、`git rev-parse HEAD`）。
- 在 Task 卡 Canonical Evidence 表登记 6 个文件的 `sha256`（`CANONICAL`），并在 Resource Manifest 填 workspace 产物路径（`PRESERVE_REFERENCED`）。
- 在 Gate §16 标题/末段标注"**仅对 head `5dda04437` 与本机 2026-11-15 状态有效；sidecar 重建或 publish 脚本变更后必须重测**"。
- 若要自动化：最便宜的做法是在 `check.ps1` 增加一条"evidence 目录若有 manifest，则与 Task 卡 Canonical Evidence 的 sha256 比对"；不建议为这张一次性探测卡写测试。

## 7. 这次"包 + 冒烟通过"能否算条件 4 的真实推进？

**包与冒烟这一半：算真实推进，不是自证、不是文字游戏。**

- 产物是本次真实 `dotnet publish` 写出的（输出目录先被删除，产物哈希与 manifest 一致），不是复制旧包；
- `host_ready` 不是脚本自报：`host.log` 的两行由 App 在 `CoreServiceClient.StartAsync`（含 `core.ping` Ready + protocol 校验）与 `HostBridgeClient.StartAsync` 成功后写入；
- 窗口真实出现（截图 + `MainWindowHandle`）、`exit_kind=natural`、`exit_code=0`；
- 它证明了"**单文件自包含 exe 能在本机起来、能拉起 sidecar 并完成 wire 握手、能自然退出**"这条机制链，这是此前从未被验证过的。

**但"条件 4 的真实阻塞只剩一项（PyInstaller）"不成立，因此整张卡不能按现结论收口：**

- 缺的不是"PyInstaller 不可得"，而是：①用 Python 3.12 + 钉死 ML 栈**实际重建 sidecar**（PyInstaller 本身可从 pypi.org 取得）；②把 sidecar 以 `core-sidecar/` 或 `resources/core-sidecar/` 布局 stage 进安装器并构建 `setup.exe`；③跑 clean install / 启动 / 升级回退 / 四页（打包产物上的逐页导航）/ 卸载矩阵；④在结论里明确"四页"指产品四页而非 v2 三个 space tab。
- 因此条件 4 仍然是 **NOT MET / Gate BLOCKED**；本次只是把"包能构建、能启动"从"未知"变成"已知"，并把"真实阻塞"错误地收窄了——需要 r2 修正 R-001/R-002 后才能作为 Gate 证据引用。

## 8. 复核结束状态

- 除本报告外未修改仓库；`git status --short` 预期只有 `?? doc/reviews/RELEASE-PACKAGE-PROBE-1-review-r1.md`（本报告）——其它路径无改动。
- 未重跑 publish，未安装任何包（`pip download` 只写 `%TEMP%`）。
- 本 Review 只对 `7220a261d8a1220ecfbf1b5f27c829273e36ae76` 有效；r2 需针对新 head 与 R-001/R-002 的修订重开。
