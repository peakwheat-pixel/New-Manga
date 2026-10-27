# RELEASE-REPACK-4 报告：最终发布包（含 PDF UI/工具/修复）与端到端验收

- Task: `doc/tasks/RELEASE-REPACK-4.md`（team task-55）
- Branch/Worktree: `task/RELEASE-REPACK-4` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4`
- 构建 HEAD：**`f1b89c5e5`**（含 Lead 构建修复 `4be1c3f4f` 与其后 ledger 提交；原卡 base `84dd38978` 编译失败，见 §0）
- 新包：`task-envs/RELEASE-REPACK-4/out/`；旧包对照 `task-envs/RELEASE-REPACK-3/out`（未动）
- 未 push、未 gc/prune；真实 `%APPDATA%` 书库/凭据库未触碰。

## 0. base 阻塞与修复（重要）

原卡/Lead 初始 base `84dd38978` **无法编译**：`MainWindow.axaml.cs(593): error CS1061: SettingsPage 未包含 ApplyLayout`（`152538e34` 引入调用但未提交方法）。已上报 Lead；Lead 提交 `4be1c3f4f` 回退未落地主题 API 后构建成功（`build-head-failure.log` 为修复前证据）。本任务最终基于 **`f1b89c5e5`** 出包。

## 1. AC1 重打包（MET）

| 产物 | 大小 | sha256 |
|---|---|---|
| base zip | **103,330,812B** | 见 `package-hashes.json` |
| models zip | **725,339,894B** | 见 `package-hashes.json` |
| 旧 REPACK-3 base/models | 103,326,248 / 725,334,588B | 见 `package-hashes.json` |

- sidecar：base `bd23e66f…0d99`、models `3909a4a2…f57dde5`（均 ≠ REPACK-3 的 `65d7b55a…`/`8cfc9080…`，未复用旧 exe）
- 安装后 `VERSION.json.repo_head=f1b89c5e5…`，`core_service_sha256=3909a4a2…`
- **torch-free PASS**：models bundle 无 `_internal/torch`，含 onnxruntime

## 2. AC2 全流程（MET，含 PDF）

| 步骤 | 结果 | 证据 |
|---|---|---|
| 全新安装 | **2,545.5ms**；console **0**；Host 就绪 **1,100.1ms** | `install-timed.log`、`smoke.json` |
| 书架 | BOOK-FIXTURE-1（9 页）Host 就绪 | `screens/01-bookshelf.png` |
| 导入（UI 全链路） | 导入文件→系统选择器→目标书/章→开始导入→**已导入 1 个文件**；**9→10 页**（DB pages=10） | `screens/02-import-panel.png`、`03-import-result.png` |
| 阅读器/滚动 | webtoon 10 页；WM_MOUSEWHEEL 滚动 | `screens/04-reader.png`、`05-reader-page.png` |
| 沉浸 | UIA ImmersiveButton → 沉浸全屏 | `screens/06-immersive.png` |
| **导出 PDF** | 面板选 **PDF（默认 searchable_dual_layer）**→导出完成：`…-170429.pdf` **20,728,075B**、sha256 `c0a97eb3…b210`、**3 页**、`%PDF-1.7`、ToUnicode 文本层存在 | `screens/07-export-panel-pdf.png`、`08-export-pdf-done.png` |
| 导出 ZIP | 重开面板（默认 ZIP）→导出完成：`…-170520.zip` **7,070,562B**、sha256 `72d81db9…945c`、3 JPG+manifest | `screens/09-export-zip-done.png` |
| 打开导出目录 | Explorer 打开 exports（2.9s） | `screens/10-export-folder.png` |

说明：导入选择器沿用上一次目录（`IMPORT-EXPORT-UI-1/import-src`，内含已导入过的旧 fixture）；为证明“真导入”，临时放入内容唯一的 `ui-import-4.png` 选中导入（9→10 页）后**已删除并还原该目录**；旧目录两次点击得到“跳过重复”也按实记录。PDF 与 ZIP 为同一次会话两次导出（PDF 先、ZIP 后），均含 3 页已翻译内容。

## 3. AC3 真机 5 项

| 项 | 结果 |
|---|---|
| Mica | **本次 actual=None**（`window-material.log` 全部 actual=None；transparency effects=1；DWM 属性 38=0）。**与 REPACK-3 同机 actual=Mica 不一致**，需 DSH 复核（HEAD 回退/环境波动）。历史日志 973 行中 actual=Mica 50 行 |
| 4K@200% DPI | **NOT_AVAILABLE**：主屏 2560×1440@96(100%)；Mi TV 3840×2160 物理连接但当前**不在桌面扩展**（Screen.AllScreens 仅 DISPLAY1）；REPACK-3 时段副屏为 3840×2160@144(150%)。未强制改系统缩放（交互式 Settings，且会影响共享桌面） |
| 工作集 | App **526.7MB**（阅读+导出后）、core_service 44.5MB、host_bridge 23.7MB |
| Esc/H 键盘（前台自动化） | 已用 AttachThreadInput+SwitchToThisWindow+SetForegroundWindow **取得真前台**（foreground_pid==app_pid），并发送真实 `keybd_event` Esc/H；**但 Esc/H 前后截图 sha256 相同、UI 无可观察变化** → PARTIAL，需用户真机确认；UIA 按钮路径（沉浸）正常 |
| IME | **N/A**（需人工确认，未自动化） |

## 4. AC4 稳定性（MET）

WM_CLOSE 退出 **4,267.9ms**；本安装相关进程 **0 残留**；卸载 exit=0、目录消失、数据根保留；注册表 `*NewManga*` **0**；凭据管理器 2 条历史/他 Agent 残留（`p15-host-2-smoke`、`3819f991…`），只上报未删。

## 5. AC5 门禁（MET）

- 干净 worktree `test.ps1`：**TEST PASS 232/232**（CoreClient 61 + Host 56 + App 115；Lead 修复后预期值）——`dotnet-all.log`
- pytest：**0 failed / 2773 passed / 10 skipped**（241.24s）——`pytest.log`
- `check.ps1 -TaskPath doc/tasks/RELEASE-REPACK-4.md`：PASS
- 64-hex pin（见任务卡 Canonical Evidence）；Handoff 已交付

## 6. 遗留 / 需裁决

1. **Mica 回归疑似**：REPACK-4（f1b89c5e5）本次 actual=None；REPACK-3（dd2408869）同机 actual=Mica。建议 DSH 复核是否与 `4be1c3f4f` 回退 UI 文件有关。
2. **4K@200%** 需在活跃 4K 桌面环境复验（本机当前 4K 物理屏未在桌面扩展）。
3. **Esc/H 键盘** 前台已取得但无可观察响应，需用户真机确认；按钮路径已验证。
4. **凭据历史残留 2 条**建议 DSH 裁决清理。
5. 数据根为 REPACK-3 私有副本（含翻译页）；导入选择器临时文件已删除还原。
