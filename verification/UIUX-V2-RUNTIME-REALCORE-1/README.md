# UIUX-V2-RUNTIME-REALCORE-1 证据目录

真实 Tauri 生产窗 + 真实 Python Core 的**脚本化**端到端验收证据。本目录由
`apps/desktop/frontend/e2e/uiux-v2/run.mjs` 生成（每条 run 一个 `run-iN/`），
不使用「截图 + 识图 + 坐标点击」的人工方式，也不依赖 jsdom。

## 复现

```powershell
# 1) 构建前端与验收用 exe（唯一差异：窗口 additionalBrowserArgs 打开 CDP 端口）
cd apps/desktop/frontend; npm run build
cd ../src-tauri
cargo tauri build --no-bundle --config tauri.acceptance.conf.json   # 验收构建
# 2) 跑 7 个场景
cd ../frontend
$env:UIUX_E2E_EXE = 'G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe'
node e2e/uiux-v2/run.mjs      # exit 0 = 全绿
```

脚本每轮自动分配新的 `run-iN`（绝不覆盖既有证据），把每个场景的断言结果写进
`run-iN/report.json`，截图由 CDP `Page.captureScreenshot` 产生，日志来自应用
`stderr`（含生产 IPC allowlist 公告）。

## 两版二进制（必须区分）

| 用途 | 构建方式 | SHA-256 | CDP 端口 |
|---|---|---|---|
| **验收构建**（本目录证据所用） | `cargo tauri build --no-bundle --config tauri.acceptance.conf.json` | `54F0957FC32DEA1855AE7C651A15E18DE86BB244A04284239345F774B5BA81D0` | 开（9345，仅本机回环） |
| **发布构建**（对外交付物） | `cargo tauri build --no-bundle` | `CF86888DA121C608B6A473E21666E3C335A874FB6A4CCE4374F6FB3C3FC43AAB` | 关 |

两版代码完全相同，**配置差异**只有 `tauri.acceptance.conf.json` 给窗口加的
`additionalBrowserArgs`（wry 会用它覆盖环境变量，这是 WebView2 打开 CDP 的唯一
可靠入口）。发布构建另做了一次冒烟：启动、v2 UI 渲染、`Core 在线`、无 9345 端口
（见 `release-smoke.png`）。`run-i18/report.json` 的 `exeSha256` 记录的就是当轮
被测二进制，可与本表对账。

## run 历史（含失败，不隐藏）

| run | 结果 | 说明 |
|---|---|---|
| `run-i2` | FAIL | 首轮：页面 `reload` 后 `app-root` 未出现（Tauri 页面 reload 会打断 IPC 桥），改为不 reload |
| `run-i4` | FAIL(2/7) | S3 鼠标点击无效（WebView2 忽略无 `buttons` 的 `mousePressed`） |
| `run-i5` | FAIL | S3 焦点还原断言假设错误（键盘路径下 opener 是 `<body>`，本就无元素可还原） |
| `run-i6` | FAIL | S3 鼠标路径改用「点击命令项」；S6 暴露真实写入被拒 |
| `run-i8` | FAIL(5/7) | S6 真实写入失败（P0 编码缺陷）、S7 被未关闭的对话框连带挡住 |
| `run-i9`..`run-i16` | 诊断轮（非验收） | 直接 IPC 探针证明写入路径本身可用；**`run-i14` 是 F-1 修复前的乱码铁证**（`雾港来信` → `闆炬腐鏉ヤ俊`，数据根保留在 workspace）；`run-i15` 复验环境变量钉死无效。原始产物在 workspace `task-envs/UIUX-V2-RUNTIME-REALCORE-1/` |
| `run-i17` | 诊断（修复后） | 六种中文 title 形态全部正确落库并读回 |
| **`run-i18`** | **PASS(7/7)** | 缺陷修复后全绿 |

每一次失败都被保留下来：它们是「工具化验收确实在检查真实行为」的证据，而不是被
清理掉的痕迹。中间轮的失败原因同时写进 Task 卡的发现表。

## 7 个场景（`run-i18/report.json` 逐条可查）

1. **S1 身份与单一 UI**：`data-view=app`、4 个 tab、DOM 中无 `AppShell`、Tauri IPC 桥存在、生产 allowlist 公告 66 条
2. **S2 书架真实数据**：空态来自真实 `library_list_books`，状态栏 `Core 在线`
3. **S3 命令面板**：`Ctrl+K` 与真实鼠标都能打开；焦点落输入框；`aria-activedescendant` 有效；Esc 关闭并把焦点还给唤起按钮
4. **S4 四页导航**：真实点击 4 个 tab，`aria-selected` 正确，全程只有一套 UI
5. **S5 设置页**：真实 `settings_get`（页脚「已同步」）、12 分节、切分节换内容
6. **S6 新建作品**：真实 Core 写入中文标题 → 书卡出现 → 计数 0→1 → 选中后详情与章节区真实空态
7. **S7 主题切换**：`data-theme` 变化 + **计算样式背景色** `rgb(27,27,27)` → `rgb(238,238,238)`

## 编码留痕（ZCode 复核 R-P2-1）

「`PYTHONIOENCODING` / `PYTHONUTF8` 对冻结的 PyInstaller sidecar 无效」这句话不留口说，实验在
`G:/CODEX/New Manga.workspace/task-envs/UIUX-V2-RUNTIME-REALCORE-1/encoding-probe/`：
同一个 `core_service.exe`、同一个含中文命令名的请求，四种环境组合各跑一次，原始响应在
`0N-*.response.txt`，汇总在 `summary.json`。结果：四种组合回显的乱码**完全一致**
（distinct = 1），即环境变量对该 bootloader 没有任何作用。修复不依赖这句结论——
纯 ASCII 的 `\uXXXX` 线上形式比钉住环境变量更强，但结论本身现在有据可查。
## 本轮抓到的产品缺陷（详见 Task 卡）

- **P0 中文内容经 IPC 落库乱码**：`library_bridge.rs` 请求序列化改为纯 ASCII
  （`\uXXXX`）后修复；修复前 `雾港来信` 落库为 `闆炬腐鏉ヤ俊`，多数中文标题直接失败。
- **P1 书架标题栏「搜索或执行命令」是死按钮**：运行时 `palette` 传 null，`onClick`
  静默无操作；已改走 `chrome.onOpenCommand`，并补 jsdom 守卫。
