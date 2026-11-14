# INSTALLER-MATRIX-1 证据（条件 4：安装/卸载矩阵）

卡面：`doc/tasks/INSTALLER-MATRIX-1.md`。基线 `fe7da5d92`。

## 1. 结果速览

| AC | 结果 |
|---|---|
| AC1 stage | ✅ **848.15 MB / 1037 files**（`app/NewManga.App.exe` 94.9 MB + `app/core-sidecar` 753 MB + 许可/NOTICE 齐全） |
| AC2 `VERSION.json` 真实 | ✅ 写入**实测**值（见 §2），未沿用模板旧值 |
| AC3 `setup.exe` | ✅ `NewManga-0.1.1-setup.exe` **621.9 MB**，sha256 `3e6dcb1f6d8d03c268e6a75c6d6afc6ab52cfe0e91c70a54e1e15f37b796650a`；`makensis v3.13`；`install_size_kb=868509` |
| AC4 clean install | ✅ `/S` exit 0；程序目录 `%LOCALAPPDATA%\Programs\NewManga`（848 MB）；HKCU 卸载项 `New Manga` / `0.1.1`；Start Menu `New Manga.lnk` + `卸载 New Manga.lnk` |
| AC5 安装后启动 | ✅ exit 0；`host.log`：`core_service ready (1 wire frames)`、`host_bridge ready (1 wire frames)`、`credential port ready`、`self-check status=Passed code=- detail=core_protocol=2.3 required_minor=3`、capabilities **17 条** |
| AC6 卸载 | ✅ `/S` exit 0；程序目录删除；HKCU 项移除；Start Menu 移除；**用户数据根 532 files / 967,726,273 B 逐字节未变** |
| AC7 四页可达性 | ❌ **NOT_RUN**（未在打包产物上逐页导航/截图；§4 说明原因） |

## 2. `VERSION.json` 的实测值（AC2）

| 字段 | 值 | 来源 |
|---|---|---|
| `app_build.exe_sha256` | `ea01c8c77358f35b0f15f43a0a496dfd3bf1a0e1b472adf9c55c65f0a28c76ed` | 对 stage 里的 exe 实测，与 publish manifest 一致 |
| `app_build.exe_bytes` | `99554850` | 同上 |
| `app_build.repo_head` | `fe7da5d9261e999de714519e393a4b9c28ba3fa6` | `git rev-parse HEAD` |
| `sidecar_build.core_service_sha256` | `6050881163753d32eca2fb1c0c824d9de7852bf62fb808926f5b6fc74a6b52ee` | 对 stage 里 sidecar 实测 |
| `sidecar_build.core_service_bytes` | `400098` | 同上 |
| `sidecar_build.core_service_built_at_utc` | `2026-11-14T19:16:55.3503345Z` | 文件 `LastWriteTimeUtc` |
| `sidecar_build.repo_head` | `6ad457c62ac1264fc8fa82267b06b90cb78f8b50` | sidecar 构建时的 head（`SIDECAR-REBUILD-1`） |
| `sidecar_build.known_limitation` | sfx 权重缺失 → `PROVIDER_NOT_CONFIGURED` | 实测 stderr |

## 3. ★ 我的一次真实副作用（必须登记，不淡化）

**第一次启动（AC5 的第一版）污染了真实用户数据根。**

- 我以为设 `NEWMANGA_DATA_ROOT` 环境变量就能隔离，**没有**传 `--data-root`
  （`AppOptions.cs:216` 才认这个参数）⇒ App 用了默认数据根
  `%APPDATA%\com.newmanga.desktop`，sidecar 在该根下 `re-bound preview namespace`、
  执行了 `applied 14 migration(s)` 并写入 `derived`/`logs`/`library.db`。
- **实测后果**：该目录从 **524 files / 210,443,772 B** 变为 **705 files / 879,396,924 B**
  （+181 文件、+约 669 MB；`library.db` 被重写为 729,088 B）。
- **影响评估**：新增的主要是 `derived`（170 文件 / 95.8 MB，**可再生预览产物**）与
  `logs`（177 文件 / 8.3 MB）；`library.db` 被 sidecar 正常迁移到 v14 —— 该 sidecar 每次可写启动都会做
  "first writable start backup"，因此有备份可回退。**未观测到用户可见数据丢失**，但**数据根被写是事实**。
- **修正**：第二次启动改为 `--data-root=<隔离目录>`，实测
  `before=967726273 B / after=967726273 B`（未变），且隔离根内 `applied 14 migrations` 正常发生。
- **教训**：`NEWMANGA_DATA_ROOT` 是给 **core_service** 的环境变量；**App 只认 `--data-root`**。
  任何"启动真实产物"的测试都必须**显式传 `--data-root`**，不能只设环境变量。

## 4. 另一处新发现（未修，登记为 E-8）

安装后启动的 `startup.log` 出现**成批 XAML 绑定错误**（6 条以上），全部指向 V2 Studio 页：

```
[Binding] An error occurred binding 'IsEnabled' to 'IsEnabled' at 'IsEnabled':
  'Could not find a matching property accessor for 'IsEnabled' on 'NewManga.App.ViewModels.V2.Studio.StudioPageViewModel'.'
[Binding] An error occurred binding 'Text' to 'ActiveTabLabel' at 'ActiveTabLabel':
  'Could not find a matching property accessor for 'ActiveTabLabel' on 'NewManga.App.ViewModels.V2.Studio.StudioPageViewModel'.'
```

**性质**：VM 缺属性、XAML 却绑定它 ⇒ 这些控件在运行时**不会**反映 IsEnabled/文案状态（静默失效）。
headless 测试**抓不到**（它们不读 `startup.log` 的绑定诊断）。
**已登记为 `E-8`**，本卡未修（属 V2 Studio 面，不属于条件 4 的范围）。

## 5. AC7 为什么标 NOT_RUN

条件 4 要求"四个一级页面可达性"。本卡**只**证明了：
- 窗口能起（`--exit-after` 自然退出 0）；
- Host 完全就绪（`core_service ready` + `host_bridge ready` + `self-check Passed`）。

**没有**在打包产物上逐页导航与截图。headless 侧有 `FluentPages_RenderHeadlessPngEvidence` 的四帧证据，
但**那不是**打包产物上的验证，不能替代。按纪律标 **NOT_RUN**，未用 headless 结果冒充。

## 6. 边界（不得越过的结论）

- sidecar 仍是 **2026-10-23 构建后重建**的版本，且 **SFX 权重缺失**（`yolo11s-seg.onnx` 全工作区不存在）
  ⇒ 正式分发包仍不完整。
- 安装器 **unsigned**（`.nsi` 记录的已知限制），SmartScreen 会警告。
- **升级/回退矩阵未做**（需要一个旧版本 setup 作回退目标）。
- 本卡产物（stage 848 MB、setup 621.9 MB）全部在 workspace，**未提交进仓库**。
