# RELEASE-REPACK-3 报告：第三次重打包（含 UI 收尾）与全流程复验

- Task: `doc/tasks/RELEASE-REPACK-3.md`（team task-53）；Branch `task/RELEASE-REPACK-3`；
  Worktree `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3`
- Base / 构建 HEAD：**`dd2408869ce1d43f4d1dd0525ef1b13bb75bb38c`**（当前 HEAD）
- 隔离数据根：`task-envs/RELEASE-REPACK-3/data-root`（REPACK-2 completed-run 私有副本；真实 `%APPDATA%` 书库/凭据库未触碰）
- 未 push、未删旧包、未 gc/prune；旧包保留在 `task-envs/RELEASE-REPACK-2/out`。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 重打包 | **MET** | 新 base zip 103,326,248B / models zip **725,334,588B**；sidecar base `65d7b55a…`、models `8cfc9080…`（≠ REPACK-2 的 `091a201d…`/`c5531930…`）；安装后 VERSION 记录 `repo_head=dd2408869…`；**torch-free 断言通过**（models bundle 无 `_internal/torch`，含 onnxruntime） |
| AC2 全流程 | **MET（PDF 除外）** | 全新安装 **2.45s** → 启动→Host 就绪 **1.13s**；书架 8 页 → **UI 导入 1 文件**（8→9 页，DB pages=9）→ 阅读器 → **滚动翻页** → `reading_progress` 落库（13.55%、87.37s）→ **沉浸模式**（UIA ImmersiveButton，无边框全屏）→ **导出 ZIP**（7,070,562B，sha256 `d77ecf88…36f7`，3 张翻译页 + manifest）→ **打开导出目录**（Explorer，2.9s）。**PDF：NOT_IMPLEMENTED_IN_CURRENT_UI**——PDF-EXPORT-UI-1 仅「释放」（2591ef028），其 App UI 变更未合入 dd2408869；当前导出面板仍只有 ZIP（截图 `08-export-panel.png`），故 PDF 未验 |
| AC3 Mica/DPI 复核 | **给出结论** | OS：**Windows 11 26H2 build 26300.9711**（注册表 ProductName 仍写 "Windows 10 Pro"，CIM caption 为「Microsoft Windows 11 专业版」）→ 纠正 RELEASE-SMOKE-1 的 Win10 判断；**Mica actual=Mica**（app 诊断日志，requested=Mica,Blur,None；首帧 actual=None，约 60s 后稳定为 Mica；与 MICA-FIX-1 证据一致）；**4K@200% NOT_AVAILABLE**：本机主屏 2560×1440@96(100%)、副屏 **3840×2160@144(150%)**，4K 屏存在但未配置 200%；此前 MICA-FIX-1 的 DPI=192 来自 DPR2 仿真/192dpi RTB 证据，不是本机 200% 缩放 |
| AC4 残留/卸载 | **MET** | console 窗口 **0**；WM_CLOSE 优雅退出 **4.16s**；本安装的 app/core_service/host_bridge **0 残留**；卸载 exit=0、目录消失、数据根保留；注册表 NewManga 键 **0**；凭据管理器 2 条均为历史/他 Agent 残留（`p15-host-2-smoke`、`3819f991…`），**只上报未删** |
| AC5 门禁 | **MET** | 干净 worktree：`test.ps1` **TEST PASS 234/234**（CoreClient 61 + Host 55 + App 118；≥225）；pytest **3F/2772P/9S**（与既有基线 3F/2739P/9S 的失败集合一致、无新增）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 重打包

| 产物 | 大小 | sha256 |
|---|---|---|
| `NewManga-0.1.0-win-x64.zip` | 103,326,248B | 见 `package-hashes.json` |
| `NewManga-0.1.0-win-x64-models.zip` | **725,334,588B** | 见 `package-hashes.json` |
| REPACK-2 models zip（对照） | 724,989,976B | 见 `package-hashes.json` |

- 构建：`packaging/m2ac5/build_sidecar.ps1 -Force [-SkipWeights]`（base: 57.8s；models: 50.4s）；
  base bundle 195,375,520B / models bundle 868,862,035B；core_service 399,492B（两变体），
  sha256 base `65d7b55ad58f5d37709eb80fc25b22e7d5d04111f1f035162f7d48a98a3c422b`、
  models `8cfc9080cf24fd01ffbaeed92c31c76f5fb3bdcb36128de5011644edcaeb9340`。
- 安装后 `VERSION.json.sidecar_build.repo_head=dd2408869…`，`core_service_sha256=8cfc9080…`（新构建，未复用旧 exe）。
- **torch-free**：`sidecar-models/core-sidecar/_internal/torch` 不存在；`onnxruntime` 存在。
- 打包：`package.ps1`（base+models，78.1s）；publish 日志见 `out/publish-*.log`。

> **范围偏差（需 DSH 确认）**：首次 `package.ps1` 失败——`PublishTrimmed` 下
> `HostCredentialCoordinator.cs:210` 报 **error IL2026**（CREDENTIAL-PORT-1 证据用了反射
> `JsonSerializer.Serialize`）。为解发布阻塞，将该处改为 `Utf8JsonWriter(Indented=true)` 手写证据 JSON
> （不改变 Host 契约/语义；测试断言格式保持）。此修改在 `apps/desktop-avalonia/src/**`，
> 超出本卡 allowed_paths，需 DSH 裁决是否接受或改由 CREDENTIAL-PORT-1 补丁承接。

## 2. AC2 全流程（逐步骤）

| 步骤 | 结果 | 证据 |
|---|---|---|
| 全新安装 | 2,448.5ms；console=0；Host 就绪 1,133.0ms | `install-timed.log`、`smoke.json` |
| 书架 | BOOK-FIXTURE-1 日漫_JA 测试书（8 页） | `screens/01-bookshelf.png`、`04-bookshelf-loaded.png` |
| 导入（UI 全链路） | 工作台/书架「导入文件」→ 系统选择器 → 选中 ui-import-1/2.png → 目标书/章默认 fixture → 「开始导入」→ **已导入 1 个文件**；书页 8→9，DB `pages=9` | `screens/03-import-panel.png`、`screens/11-import-result.png` |
| 阅读器 | 第 1 章 webtoon 长滚动；工具栏 `Esc 退出 · F fit · H 隐藏 UI`、沉浸、导出 | `screens/05-reader.png` |
| 翻页/进度 | WM_MOUSEWHEEL 6 格滚动；`reading_progress`：progress_percent=13.55、scroll_offset_y=225.0、total_read_seconds=87.37 | `screens/06-reader-page.png`、`smoke.json` |
| 沉浸 Esc/H | UIA Invoke `ImmersiveButton`（标签「沉浸模式 (Esc/H/F)」）→ 无边框全屏、导航/状态栏隐藏 | `screens/07-immersive.png` |
| 导出 ZIP | 「导出」→「导出当前书（ZIP 图片包）」面板（3 页可导出）→「开始导出」→ **导出完成**：`…\exports\BOOK-FIXTURE-1 日漫_JA 测试书-第 1 章-20261027-160635.zip`（7,070,562B，sha256 `d77ecf888ddbfbb479129c3db35bf4ff65461651bbfefa330affd0ecd11136f7`，3 张翻译 JPG + manifest.json） | `screens/08-export-panel.png`、`09-export-progress.png`、Python zipfile 校验 |
| 打开导出目录 | 「打开导出目录」→ Explorer 打开 exports（2.9s） | `screens/10-export-folder.png` |
| PDF 导出 | **未验**：PDF-EXPORT-UI-1 仅释放未实现（当前面板无 PDF 选项；Core PDF composer 已合但 UI 未接） | `screens/08-export-panel.png` |

自动化说明：本机前台被用户 DSH 窗口占用，键盘输入无法送达 App；导入选择器通过
UIA `SelectionItemPattern.Select()` + `WM_COMMAND IDOK` 完成，其余用 UIA InvokePattern / WM_MOUSEWHEEL /
WM_CLOSE。键盘 Esc/H 与 IME 标注为「待用户前台确认」。

## 3. AC3 Mica/DPI 结论（纠正此前矛盾）

- **OS**：`build 26300.9711`，CIM caption「Microsoft Windows 11 专业版」→ **Windows 11**（注册表 `ProductName` 仍写 Windows 10 Pro 是已知历史遗留字段）。RELEASE-SMOKE-1 报 Win10 系依据该字段，**结论修正**。
- **Mica**：app 启动诊断日志（`%APPDATA%\com.newmanga.desktop\logs\window-material.log`）本次运行末行
  `material=Mica; requested=Mica,Blur,None; actual=Mica` → **actual=Mica 已验证**；首帧 `actual=None`、
  约 60s 后稳定为 Mica（与 MICA-FIX-1 的「actual=Mica + 标题栏随壁纸取色」一致）。DWM 属性 38 返回 0，
  属 Avalonia/DWM 上报差异，以 app 日志 + MICA-FIX-1 截图为证据。
- **DPI**：主屏 2560×1440 @96dpi = 100%；副屏 3840×2160 @144dpi = **150%**。4K 物理屏存在，
  但 **200%（192dpi）未配置 → 4K@200% NOT_AVAILABLE**。MICA-FIX-1 的 DPI=192 来自
  DISPLAY-PERF 的 DPR2 仿真 / 192dpi RTB 证据，不是本机显示器缩放。

## 4. AC4 稳定性

- console 窗口 0；WM_CLOSE **4,159.9ms**；本安装相关进程 **0 残留**（后来出现的 core/host 进程属
  另一 Agent app（pid 48580，使用我们的 sidecar-base 副本），非本安装）。
- 卸载：exit=0、安装目录不存在、数据根保留；注册表 `*NewManga*` **0**；
  凭据管理器 2 条（`NewManga/provider/p15-host-2-smoke/…`、`NewManga/provider/3819f991…/…`），
  均为历史/他 Agent 产生的残留，**按要求只上报、不删除**。

## 5. AC5 回归（干净 worktree）

- `apps/desktop-avalonia/scripts/test.ps1`（本 worktree，无主树未提交改动干扰）：
  `TEST PASS (Debug): 234/234 passed, 0 skipped`（CoreClient 61 / Host 55 / App 118），
  手动用 182.2s；日志 `dotnet-all.log`。
- `python -m pytest -q`：**3 failed / 2772 passed / 9 skipped**（263.17s），失败集合与既有基线
  （MICA-FIX-1 记录 3F/2739P/9S）一致，**无新增失败**；日志 `pytest.log`。
- `check.ps1 -TaskPath doc/tasks/RELEASE-REPACK-3.md`：PASS。

## 6. 遗留 / 建议

1. **PDF 导出 UI 未验**：PDF-EXPORT-UI-1（仅释放，2591ef028）需实现后重打/复验 UI PDF 选项。
2. **4K@200% 未验**：本机副屏 4K@150%；如需 200% 验收，应在 3840×2160@192dpi 环境复跑 DPI 与 Mica 取色。
3. **键盘 Esc/H 与 IME**：需用户前台人工确认（自动化会话无法取得前台焦点）。
4. **凭据历史残留 2 条**：建议 DSH 裁决清理（非本 Task 产生/未删）。
5. **范围偏差**：`HostCredentialCoordinator.cs` 的 trim 修复需 DSH 确认（详见 §1 注）。
6. 新包 `task-envs/RELEASE-REPACK-3/out` 已产出；旧包未动。
