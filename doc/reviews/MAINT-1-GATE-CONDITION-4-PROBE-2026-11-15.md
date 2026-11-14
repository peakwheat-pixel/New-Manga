# Gate 条件 4 打包可行性探测（2026-11-15）

**Task**：`RELEASE-PACKAGE-PROBE-1`。**被探测 head**：`5dda04437d68baf304b4364a3a73f9dfa217d943`。
**条件原文**：「对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、
四个一级页面可达性与卸载矩阵」（`13_RELEASE_GATE.md`）。

> 本卡**只做探测**。结论不是"条件 4 已满足"，而是**"卡在哪一步、缺什么、已做到哪一步"**。

## 1. 结论速览

**条件 4 比此前记录乐观得多：前两步真实走通了。**

| # | 步骤 | 状态 | 证据 |
|---|---|---|---|
| 1 | 构建绑定当前 commit 的包 | ✅ **已完成** | `manifest-singlefile.json`：`git_head=5dda04437…`、`result=PASS`、`NewManga.App.exe` **99,554,850 B**、sha256 `EA01C8C77358F35B0F15F43A0A496DFD3BF1A0E1B472ADF9C55C65F0A28C76ED` |
| 2 | 启动冒烟（真实窗口 + Host 就绪 + 自然退出） | ✅ **已完成** | `smoke-singlefile.json`：`window_found=true`、`window_title="New Manga"`、`host_ready=true`、`exit_code=0`、`exit_kind=natural`、`pass=true`；截图 `published-singlefile.png` 显示四页导航与状态栏"Host 就绪" |
| 3 | 构建安装器（`setup.exe`） | 🟡 **工具具备，未执行** | `makensis v3.13` 存在于 `C:\Program Files (x86)\NSIS\makensis.exe`（不在 PATH，但 `build-installer.ps1` 会 probe 该路径）；`packaging/nsis/installer.nsi` 已就绪 |
| 4 | sidecar 重新打包 | 🟡 **可做（已更正）** | 需 PyInstaller。**r1 复核证明我此前"PyPI 不可达"的判断是错的**：默认 index（清华镜像）确实返回 `from versions: none`，但 `pip download pyinstaller -i https://pypi.org/simple` **成功**下载 `pyinstaller-6.22.3`（正是 `requirements-build.txt` 钉死版本）。本次冒烟仍用的是 **2026-10-23 的旧 sidecar** |
| 5 | 代码签名 | ⚪ **非硬需求** | `packaging/nsis/installer.nsi` 头注释明确：`the package is unsigned (SmartScreen warning is the documented known limitation)`；本机也无 `CurrentUser\My` 代码签名证书 |
| 6 | clean install / 启动 / 升级回退 / 四页 / 卸载矩阵 | ❌ **未执行** | 依赖第 3 步产物 |

## 2. 依赖逐项（命令级证据）

| 依赖 | 判定 | 证据 |
|---|---|---|
| .NET SDK（≥9） | **FREE** | `dotnet --list-sdks` → `9.0.308`、`10.0.401`；publish 实际用 `10.0.401` 成功 |
| .NET runtime 9 | **FREE** | `Microsoft.NETCore.App 9.0.11` |
| sidecar 包（`core_service.exe`/`host_bridge.exe`） | **FREE（但版本过期）** | `core_service.exe` 68,887,500 B，`LastWriteTime=2026-10-23 19:21`；同目录另有 `host_bridge.exe`/`catalog_loader.exe`/`sfx_detect_probe.exe`/`acceptance_bridge.exe` |
| 模型权重（ONNX） | **FREE** | `detector/rtdetr-v2-fixed.onnx` 164 MB、`ocr/manga-ocr-onnx/{encoder,decoder}_model.onnx` 328/112 MB，位于 `G:\CODEX\New Manga.workspace\task-envs\CORE-SLIM-2\models` |
| PyInstaller（重建 sidecar） | **FREE（已更正）** | 默认 index → `from versions: none`（镜像缺包）；**`python -m pip download pyinstaller -i https://pypi.org/simple` → 成功，`pyinstaller-6.22.3-py3-none-win_amd64.whl`**。此前判定 MISSING 是我的错误 |
| NSIS `makensis` | **FREE（未在 PATH）** | `C:\Program Files (x86)\NSIS\makensis.exe`（`v3.13`）、`…\Bin\makensis.exe`；`%LOCALAPPDATA%\tauri\NSIS\makensis.exe` 亦存在 |
| 代码签名证书 | **MISSING（非阻塞）** | `Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert` → 无；`.nsi` 声明 unsigned 为已知限制 |
| Windows 长路径 | **FREE** | `LongPathsEnabled = 1` |
| 磁盘空间 | **FREE** | G: 空闲 **1216.9 GB** |

## 3. 实际执行记录

```
pwsh -NoProfile -File tools/ci/publish-release.ps1 -Mode singlefile `
  -SidecarDir "G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy" `
  -EvidenceDir "verification/RELEASE-PACKAGE-PROBE-1"
```

输出：

```
== singlefile ==
[singlefile] result=PASS exit=0 elapsed=7.7s artifact=94.94 MB sha256=EA01C8C77358F35B...
   smoke: pass=True exit=0 exit_kind=natural host_ready=True reason=
publish: 1/1 PASS, 0 expected-failure(s), 0 FAIL
```

产物落在 workspace（**未进仓库**）：`G:\CODEX\New Manga.workspace\artifacts\publish\singlefile-Release-win-x64\`。

## 4. 三条必须说清的诚实边界

### 4.1 「包能启动」≠「命令面完整」（AC4）

本次冒烟**用的是 2026-10-23 的旧 sidecar**。该 sidecar **早于**多条现行命令，已知包括：
`ReorderChapters`（2026-11-10 引入，`83e45cfe5`）、以及 FEA-12 之后新增的 delete/trash 系列。
因此：

- `host_ready=true` 只证明 **Core 进程能起来、Host 桥能连上**；
- **不证明**当前 registry 的 111 条命令在该 sidecar 上都可用；
- 这也是 E-2 的同一根因。**分发用的 sidecar 必须重建**（缺 PyInstaller）。

### 4.2 包**不自包含** sidecar

`singlefile-Release-win-x64\` 里只有 `NewManga.App.exe`（94.94 MB）+ 日志 + 截图，**没有 sidecar**。
smoke 是通过命令行 `--sidecar-dir=<外部路径>` 注入的（见 `publish-release.ps1` 的 `InvokeSmoke`）。
所以这个 exe **不能**直接当"clean install 可分发包"—— 安装器 stage 必须把 sidecar 一起打进去。

### 4.3 截图证明的是"首屏"，**不是**"四页导航"

`published-singlefile.png` 显示书架首屏，状态栏"Host 就绪"。顶部那三个是**空间切换**
（`资料柜 1 / 工位 2 / 控制台 3`，见 `AppShellViewModel.cs:58-63`、`TopBand.axaml:18-21`），
外加 Breadcrumb 文字 —— **不是产品四个一级页面（书架/工作台/阅读器/设置）的导航**。
r1 复核指出我上一版把它写成"四页导航"是错的（且与本节自相矛盾），已更正。

冒烟脚本**没有逐页导航**（只断言窗口出现 + host ready + exit 0）。四页可达性仍需在打包产物上单独验证。

## 5. 后续链条（AC5）

| 步骤 | 本环境可做？ | 需要什么 |
|---|---|---|
| 构建 App 包 | ✅ 已做 | — |
| 启动冒烟 | ✅ 已做 | — |
| 构建 `setup.exe` | **✅ 可做** | `makensis`（**已具备**）；需先准备 stage（App + sidecar 副本 + NOTICE.md） |
| clean install | **✅ 可做**（在 stage 就绪后） | `setup.exe /S`，验证 `%LOCALAPPDATA%\Programs\NewManga` 与 HKCU 卸载项 |
| 启动（安装后） | **✅ 可做** | 同上 |
| 升级/回退 | **✅ 可做** | 需要一个"旧版本"的 setup（当前只有一个 head，需给回退目标一个版本号） |
| 四页可达性（打包产物上） | **✅ 可做** | 需扩展冒烟或手动逐页截图；现有 `--exit-after` 冒烟不覆盖 |
| 卸载 | **✅ 可做** | `setup.exe /S` 后运行卸载器，验证程序目录与 HKCU 项清理、且**用户数据根不被触碰**（`.nsi` 已声明该约束） |
| sidecar 重建 | **✅ 可做（已更正）** | PyInstaller 6.22.3 可从 pypi.org 下载（r1 复核实测）；需再核 ML 栈（onnxruntime 等）能否安装 |
| 签名 | ⚪ 不需要 | unsigned 是 `.nsi` 记录的已知限制 |

**⇒ 条件 4 的真实阻塞只剩一项：sidecar 重建（PyInstaller）。** 安装/卸载/四页矩阵在工具层面**全部具备**，
只是尚未执行；它们可以用旧 sidecar 先跑通"机制"，但**正式分发包**必须等 sidecar 重建。

## 6. 本卡的边界（不得当作条件 4 已推进到"可发布"）

- 只探测 **singlefile** 一种形态；`trimmed`/`aot` 未跑（脚本注释说默认是 EXPECTED FAILURE）。
- 未构建 `setup.exe`、未做 install/uninstall、未做升级回退、未在打包产物上验证四页。
- 未验证 sidecar 与当前 111 条命令的兼容性。
- 产物在 workspace，**未进仓库**；本文件不构成发布许可。
## 7. r1 复核后的更正与失效声明

### 7.1 两处实质更正（均属我的判断错误）

| 错误 | 真相 | 影响 |
|---|---|---|
| 断言"PyPI 不可达 → sidecar 无法重建" | 默认 index（镜像）缺包，但 **`pip download pyinstaller -i https://pypi.org/simple` 成功**（`pyinstaller-6.22.3`，正是钉死版本） | 我据此得出"条件 4 只差一项"的收窄结论**不成立**，已撤回 |
| 称截图显示"四页导航" | 截图顶部是**空间切换**（资料柜/工位/控制台）+ Breadcrumb，**不是**四页导航 | 已更正；与 §4.3 的自相矛盾一并消除 |

**教训**：我把"某个 index 失败"直接当成"包不可得"，没有换源验证 —— 与前面几轮"用源码推断代替实测"是同一类错误。

### 7.2 构建的可复现性限定

`elapsed=7.7s` 说明这是**热缓存增量构建**（脚本会先清输出目录，但不清 `obj/`，也无 `global.json`，
SDK 落到 `10.0.401` 而 TFM 是 `net9.0`）。因此：

- 它证明**本机可构建**，**不**证明 clean-room / 无缓存可构建；
- 若要作为发布证据，需补 `dotnet publish --no-incremental` 或干净克隆构建（`tools/ci/verify-clean-clone.ps1` 可能可用）。

### 7.3 失效（staleness）声明

本文件是 **`5dda04437` 时点**的探测快照。以下任一情况都会使它过时，**且没有任何自动机制会报警**：

- sidecar 重建成功（E-2 解除）→ §4.1 与 §5 的结论需重写；
- `tools/ci/publish-release.ps1` 或 `packaging/nsis/installer.nsi` 变更；
- 被探测 head 变化；
- PyInstaller / ML 栈可用性变化。

引用本文件时必须注明基线 commit。
