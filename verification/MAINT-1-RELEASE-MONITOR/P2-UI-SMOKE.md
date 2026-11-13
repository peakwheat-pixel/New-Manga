# P2 · 可见 UI 冒烟（四页，双根隔离）——MAINT-1，2026-11-14

对象：`REL-GATE-1` 卡住的「GUI 冒烟 BLOCKED」与 `FEA-15-ACCEPT-1` 的「可见 UI NOT_RUN」。
本记录只提供证据，**不翻转任何节点状态、不改任何历史字节**。

## 1. 方法

`verification/MAINT-1-RELEASE-MONITOR/tools/p2-ui-smoke.ps1`：四个一级页面各起一个进程，
参数 `--page=<p> --data-root=<temp> --log-dir=<temp>/logs --theme-home=<temp> --sidecar-dir=<sidecar> --exit-after=12000`，
双根隔离（数据根 + 主题根），用 `PrintWindow(PW_RENDERFULLCONTENT)` 抓窗口像素。

被启动对象：`apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/win-x64/NewManga.App.exe`
（当前 HEAD 的 Release 构建）＋ `workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`。

### 本会话踩过的三个坑（写死，防回退）

1. **`Start-Process` 会无限阻塞**（走 ShellExecute）：三次尝试都卡在首页，进程实际已退出。
   改用 `[System.Diagnostics.Process]::Start(UseShellExecute=$false)`（与通过的 C# 用例一致）后正常。
2. **`Graphics.CopyFromScreen` 无交互桌面时阻塞**；改用 `PrintWindow`，实测 279 ms 完成。
3. **`Start-Job` 在本沙箱挂死**（命名管道受限）；不要用作业做超时看门狗。

## 2. 结果（`logs/p2-ui-smoke.log`、`tools/ui-smoke/p2-ui-smoke.json`）

| 页面 | 窗口出现 | 截图 | 退出码 | host.log |
|---|---|---:|---:|---:|
| bookshelf | True @1582 ms | 28,321 B `page-bookshelf.png` | 0 | 1,316 B |
| workbench | True @1570 ms | 32,555 B `page-workbench.png` | 0 | 1,316 B |
| reader | True @1535 ms | 34,730 B `page-reader.png` | 0 | 1,313 B |
| settings | True @1532 ms | 59,932 B `page-settings.png` | 0 | 1,315 B |

汇总：`pages_ok=True shots_ok=True host_logs_ok=True appdata_unchanged=True` → **`P2_SMOKE PASS`**（EXIT 0）。

## 3. 目视核验（DSH 逐图确认，非自动断言）

- `page-bookshelf.png`：标题 `New Manga`；页签「资料库 1 / 工位 2 / 控制台 3」；`资料库 0 / 0 作品`；
  搜索框「搜索作品（中文/拼音首字母）」；按钮 全部/收藏/已归档/导入文件/导入文件夹/新建作品/回收站；
  右栏「选择一本作品」空态；状态栏 `Host 启动中…`。
- `page-settings.png`：页签切到「控制台」；左栏 `控制台 · 设置中心 · 9 分区`，分区 01 任务与队列、02 Provider 与凭据、
  03 网络与代理、05 缓存与版本清理、06 备份与恢复、07 插件与 Hooks、08 诊断与日志、09 外观 标「已接入」，
  04 模型与设备 标「待接入」；顶栏 `主题工作室 / 浅色 / F1`；状态栏 `Host 就绪`。

两页判读：四页渲染的是**不同的真实界面**，非同一默认页；`04 模型与设备 = 待接入` 与 V1 清单中「模型 API 真实调用 NOT_RUN」一致，界面未假装已接入。

## 4. 真实 `%APPDATA%` 零写入

`%APPDATA%\com.newmanga.desktop` 文件数与字节数在整轮前后完全相同（`real_appdata.unchanged = true`）。四页运行全部落在 `%TEMP%\newmanga-p2-*` 下的隔离数据根与主题根。

## 5. 与 `REL-GATE-1` / `FEA-15-ACCEPT-1` 的关系

- `REL-GATE-1` AC2 的原理由「App 无隔离数据根入口」已被源码（`AppOptions.cs:97/216/343-351`，见 E-4）与本轮实测同时否证；
  该卡正文按红线 2 **不改一字**，其 BLOCKED 状态仍以卡面为准，解冻需 P3 独立 Review。
- `FEA-15-ACCEPT-1` 的「可见 UI NOT_RUN」在本轮获得了**可复核的替代证据**，但该节点的 `closed_with_limitations`
  状态不在本记录中翻转。

## 6. 限制（不得读作完整 GUI 验收）

1. 运行对象是 `bin/Release` 构建，**不是**单文件发布产物、**不是**安装包安装后的实例；clean install 仍未做。
2. 只覆盖四个一级页面的**首屏可达性**，不覆盖交互链路（点击、快捷键、拖拽、跨页导航）。
3. 未覆盖 C4 硬件类验收（双屏、DPI 矩阵、原生 IME、a11y、真机截图），这些仍为 `NOT_RUN`。
4. 截图是窗口像素（`PrintWindow`），不含合成器外效果（如 Mica 背板）；不等于真机视觉评审。
5. `bookshelf` 截图捕获于 `Host 启动中…`（约 1.5 s 时点），`settings` 为 `Host 就绪`；两页就绪时序不同，未做就绪等待后再抓。

## 7. 复现

```powershell
pwsh -NoProfile -File verification/MAINT-1-RELEASE-MONITOR/tools/p2-ui-smoke.ps1
```

前置：Release 构建存在；sidecar 副本存在（默认取 workspace 下 `HOST-CORECLIENT-1/sidecar-copy`）。
