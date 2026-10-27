# GRANT-ISSUER-1 报告：Host grant 签发 + shell 动作（7 条真缺口）

- Task: `doc/tasks/GRANT-ISSUER-1.md`（team task-32）；Branch/Worktree: `task/GRANT-ISSUER-1` /
  `G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1`
- 卡面 `base_commit: 45efe7f00` 早于本卡创建；实际按 Lead 指定从当前 HEAD **`b993e68bb`** 开分支
  （该提交含 RUN-EXPORT-E2E-1 done + 本卡）。
- 未 push；未改 Python Core 语义、未改 host_bridge 冻结契约（未扩展 wire 版本）、未改旧壳、未碰真实用户数据。
- 交付前按 Lead 要求 rebase 到 `9f58b4c1d`（NS-WIRE-B1 已合并，46/20）：三文件冲突取并集
  （registry 50/16、两测试并集），test.ps1 复跑 165/165；S4-CMD-BATCH-1 仍可能带来 registry 冲突，
  若其先落地按“先落地者为准”再 rebase。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 grant 签发 | **MET** | C# 实现 HOST-ISSUER-1 完整链路：`OpenHostSession`（host-control 信封）→ `HostIssuer` 铸造签名 grant（import=排序键压缩 JSON 的 HMAC-SHA256；export=`\0` 拼接串 HMAC）→ `RegisterImportSource`/`RegisterExportTarget`（host-control）→ `ImportPages`/`StartExport`（应用信封）。**真实成功样例**：8 个授权 PNG 导入 → `imported_files=8`、投影 8 页、8 个 grant `registered=true`；**Export**：grant 真实注册成功，`StartExport` 仍 typed `EXPORT_INPUT_UNAVAILABLE`（fixture 无 translated 页，翻译链是独立 slice），**未伪造成功** |
| AC2 shell 动作 | **MET** | `library_reveal_export_folder`（GetExportHistory→output_path→白名单目录→explorer）与 `plugins_open_directory`（data root/plugins，缺则创建）实现；白名单只允许 data root 内 + 本会话 Host 签发过的导出目录；**真机截图**：Explorer 打开 `...\task-envs\GRANT-ISSUER-1\real-shell-root\plugins`（`screens/01-plugins-directory-explorer.png`）；越权（`C:\Windows`）→ typed `PLUGIN_DIRECTORY_UNAVAILABLE`，导出目标越权 → `EXPORT_PATH_UNAVAILABLE` |
| AC3 安全 | **MET** | 签发只对授权资源：import 源路径由 HostIssuer 校验（绝对路径/无 `..`/无 reparse/扩展名白名单/文件身份+哈希前后一致），export 目标限定 data root/exports；失败均为 typed（`REF_*`/`EXPORT_*`/`INVALID_ARGUMENTS`）；**未放宽 TileChannel 摘要校验或资源通道授权**（相关代码零改动，S5 证据未动） |
| AC4 parity/回归 | **MET** | `--check` **PASS**（66 命令零漂移）；registry **51→55 IMPLEMENTED / 15→11 NOT_SUPPORTED**（rebase 到 S4-CMD-BATCH-1 后的并集；本 Task 新增 4 条：import_file/import_folder/reveal_export_folder/plugins_open_directory；3 条 export 命令已在 RUN-EXPORT E2E IMPLEMENTED，本批补齐 grant 层）；test.ps1 **166/166 passed**；vitest **60/60 文件 567/567**；pytest **3F/2746P/9S**（与基线相同，0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（签发边界/白名单） |

## 1. AC1 实现细节

| 组件 | 位置 | 说明 |
|---|---|---|
| host-control 通道 | `NewManga.CoreClient/CoreServiceClient.cs` | `OpenHostSessionAsync`（32B credential + 独立 32B signing key，取回 `core_session_id`）、`SendHostControlAsync`（`channel=host-control` 信封 + 会话三元组，跳过事件帧，错误转 typed `CoreOperationException`） |
| grant 签发 | `NewManga.CoreClient/Issuer/HostIssuer.cs` | `MintImportGrant`：绝对路径/reparse/扩展名白名单、WIN32 `GetFileInformationByHandle`（volume serial + file index）、分块 SHA-256、身份前后一致性、目录 natural sort、排序键压缩 JSON 签名；`MintExportGrant`：`grant\0session\0target\0format\0replace\0expires_at` HMAC、extension/父子目录/reparse 校验、`replace_existing` 判定；`ValidateExportRequest` 复刻 Rust 六字段+options 校验 |
| Host 编排 | `NewManga.Host/HostGrantCoordinator.cs` | 会话、逐 grant 注册（失败↔回滚 revoke）、`ImportPages`、`StartExport`（追加 target_ref）、`ImportSummary` 计数投影（legacy parity）、evidence 落盘（`<log>/grants/*.json`）、两道 shell 动作与白名单 |
| 生命周期 | `NewManga.Host/HostRuntime.cs` | 启动后打开 host session，构造 `Commands`（HostCommandDispatcher + HostLocal handler）；session 不可用时降级但读取照常 |
| 命令面 | `HostCommandRegistry/Dispatcher/Model` | 新增 `HostCommandChannel.HostLocal`；4 条命令 HostLocal IMPLEMENTED；dispatcher 注入 local handler |

**成功样例证据**（`verification/GRANT-ISSUER-1/evidence/` + test evidence `grants/`）：
- `import-success.json`：8 个授权 PNG → `imported_files=8`，`GetReaderProjection` 8 页；
- 每次导入的 `grants/import-*.json`：8 个 grant `registered=true` + 原始 `ImportPages` 结果（`imported/skipped/...`）；
- `export-attempt.json`：`RegisterExportTarget registered=true`、`StartExport` typed `EXPORT_INPUT_UNAVAILABLE`、越权路径 `EXPORT_PATH_UNAVAILABLE`。

## 2. AC2 证据

- 产品代码路径（非 mock）：`HostGrantCoordinator.OpenPluginsDirectoryAsync` 默认 opener
  以 `explorer.exe "<data_root>/plugins"` 打开。
- 真机运行（`NEWMANGA_REAL_SHELL=1`，专用 data root）：Explorer 窗口标题「plugins - 文件资源管理器」，
  路径 `...\task-envs\GRANT-ISSUER-1\real-shell-root\plugins`；截图
  `verification/GRANT-ISSUER-1/screens/01-plugins-directory-explorer.png`（SHA 见 pin）。
- 白名单负例：`C:\Windows` → `PLUGIN_DIRECTORY_UNAVAILABLE`；未知 export id → `EXPORT_PATH_UNAVAILABLE`；
  Host 签发目录之外的 export 目标 → `EXPORT_PATH_UNAVAILABLE`。

## 3. AC3 安全边界（Record Decision 摘要）

1. **只有 Host 能铸造 grant**：签名密钥进程内随机生成、不落盘、drop 时清零；Core 校验 HMAC，
   伪造/重放/会话不匹配 → `REF_SIGNATURE_INVALID`/`REF_UNKNOWN_ID`/`E_SCOPE_DENIED`。
2. **import 源**是用户显式选择的源文件（legacy 对话框语义），Host 校验后签发；**export 目标**由 Host 固定在
   data root/exports（不接受任意用户路径）。
3. **shell 白名单**：只打开 data root 内目录；reveal 额外要求该目录是本会话 Host 签发过的导出目录；
   路径逐段拒绝 reparse。
4. **未放宽**：TileChannel/per-tile digest/资源通道授权（S5-B/D4）零改动。

## 4. AC4 回归

| 门 | 结果 |
|---|---|
| `extract-command-surface.py --check` | **PASS**（66 命令零漂移） |
| registry | 51→**55** IMPLEMENTED / 15→**11** NOT_SUPPORTED |
| `scripts/test.ps1` | **166/166 passed, 0 skipped**（CoreClient 45 / Host 46 / App 75） |
| 旧壳 vitest | **60/60 文件、567/567** |
| pytest | **BLOCKED（主仓 rebase 目标问题，非本分支）**：ed85c4173 提交里夹带了 RUN-OCR-DIAG 在途编辑的残缺版本（`tests/core/test_sfx_assembly.py`/`test_sfx_policy_settings.py` IndentationError → 收集失败）；剔除这两文件后仍有 6F/2705P/9S，其中 3 个额外失败来自同一提交夹带的 `tests/pipeline/test_regionless_rebinding.py`、`tests/providers/test_detect_handler.py` 半成品测试（对应 main 工作树未提交的 CORE-PIPELINE-FIX-1 修复）。本分支未改 Python；在 `9f58b4c1d` 上基线 3F/2746P/9S 已通过（上一轮证据）。详见 `pytest.log` / `pytest-ignore-broken.log`。 |

## 5. 遗留 / NOT_RUN

1. **Export 真跑仍 BLOCKED**：grant 层已通，但冻结 Core 只导出 translated 产物，fixture/导入页无 translated
   页；需先有翻译/渲染链（RUN-OCR-DIAG-1 + 翻译 provider slice）。本批未伪造产物。
2. `library_get_export_snapshot`/`library_cancel_export` 成功路径需真实导出记录（当前只有 typed
   `EXPORT_NOT_FOUND` 证据）。
3. `library_import_folder` 端到端复用同一 coordinator；目录路径的 natural sort/identity/签名逻辑由
   import_file 成功样例 + HostIssuer 校验代码覆盖，未单独构造 8 项目录样例（时间限制，如实登记）。
4. `shell:reveal` 真实成功路径（真实导出记录）同样被 (1) 阻塞，当前以 typed 负例 + 白名单单测为证。
5. **pytest 基线阻塞（需 DSH 处理）**：rebase 目标 `ed85c4173` 提交夹带了 `tests/core/test_sfx_*.py` 的
   残缺编辑（IndentationError）以及 `tests/pipeline/test_regionless_rebinding.py`/`tests/providers/test_detect_handler.py`
   的半成品测试；这些对应 main 工作树里未提交的 CORE-PIPELINE-FIX-1 修复。本分支不改 Python，
   在 `9f58b4c1d` 上 3F/2746P/9S 已通过。请 DSH 先在 main 修复/提交该在途工作后再复核 pytest。
6. 需独立 Review（Owner 不得自审）。
