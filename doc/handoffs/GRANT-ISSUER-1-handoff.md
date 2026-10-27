# GRANT-ISSUER-1 Handoff（Host grant 签发 + shell 动作）

- Task: `doc/tasks/GRANT-ISSUER-1.md`（team task-32）
- Branch: `task/GRANT-ISSUER-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1`
- Base: 卡面 `45efe7f00` 早于本卡；实际按 Lead 指定从 **`b993e68bb`** 开分支，交付前 rebase 到
  **`9f58b4c1d`**（NS-WIRE-B1 已合并，46/20）；三文件冲突取并集，test.ps1 165/165。
- Delivery head: `21fd47551`（rebase 到 ed85c4173 后的实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改 Python Core 语义、未扩展 host_bridge wire 版本、未改旧壳、未碰真实用户数据。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 grant 签发 | **MET** | host-control 会话 + `HostIssuer` 双 grant 签名 + 注册/执行链路；**import 成功样例**：8 页导入、8 grant registered；Export grant 注册成功、`StartExport` typed `EXPORT_INPUT_UNAVAILABLE`（translated 前置未解，未伪造） |
| AC2 shell 动作 | **MET** | `library_reveal_export_folder` + `plugins_open_directory`（data-root 白名单）；Explorer 真机截图；越权 typed 拒绝 |
| AC3 安全 | **MET** | 仅 Host 铸造 grant；import 源/export 目标校验；shell 白名单 + reparse 逐段拒绝；TileChannel/资源通道零改动 |
| AC4 parity/回归 | **MET（pytest 除外，主仓阻塞）** | `--check` PASS；51→55 IMPLEMENTED / 15→11 NOT_SUPPORTED；test.ps1 **166/166**；vitest 567/567；pytest 被 main ed85c4173 夹带的在途 Python 编辑阻塞（见 §4） |
| AC5 门禁 | **MET** | check.ps1 PASS；64-hex pin；本 Handoff + Record Decision §3 |

## 2. 代码改动（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/CoreServiceClient.cs` | `OpenHostSessionAsync`/`SendHostControlAsync`（HOST-ISSUER-1 信封、事件帧跳过、typed error） |
| `src/NewManga.CoreClient/Issuer/HostIssuer.cs`（新） | import/export grant 铸造：HMAC 签名（Core verifier 同字节）、路径/身份/reparse/扩展名校验、WIN32 文件身份、SHA-256、natural sort、六字段 export request 校验 |
| `src/NewManga.CoreClient/Commands/{HostCommandModel,HostCommandRegistry,HostCommandDispatcher}.cs` | `HostCommandChannel.HostLocal`；4 条 HostLocal IMPLEMENTED；local handler 注入 |
| `src/NewManga.Host/HostGrantCoordinator.cs`（新） | grant 注册/回滚、`ImportPages`、`StartExport`、ImportSummary 投影、evidence、shell 白名单动作 |
| `src/NewManga.Host/HostRuntime.cs` | 启动打开 host session；构造 `Commands`；`CreateChapterAsync`（minor 8，导入前置） |
| `tests/NewManga.Host.Tests/GrantIssuerTests.cs`（新） | 3 项集成测试（import 成功/grant；export grant+typed 失败+越权拒绝；shell 白名单）+ 1 项 real-shell 手动测试 |
| `tests/NewManga.CoreClient.Tests/...` | parity 50/16（并集）；B1 计数同步；channel 断言允许 HostLocal |

## 3. Record Decision（签发边界 / 白名单）

1. **签名字节冻结**：import 用 Core `_signed_fields/_sign` 的排序键压缩 JSON；export 用
   `grant\0session\0target\0format\0replace\0expires_at(%.6f)`。任何一端改格式都会 `REF_SIGNATURE_INVALID`，
   这由真实 Core 注册结果（registered=true）反向证明。
2. **Host 才是签发者**：grant id 随机、signing key 进程内随机且不落盘；Core 只验证/登记，
   WebView/UI 永远拿不到路径或签名材料。
3. **导出目标白名单**：`data_root/exports`（本 Task 采用）为唯一合法目标根；用户任意路径拒绝
   `EXPORT_PATH_UNAVAILABLE`。未来若接原生保存对话框，须先由 Host 记录目标目录再允许 reveal。
4. **shell 白名单**：plugins 固定 `data_root/plugins`；reveal 仅允许 data root 内且本会话 Host 签发过的
   导出目录；逐段拒绝 reparse。
5. **不扩展 wire**：未新增/修改 host_bridge wire 方法；host-control 信封是 Core 既有冻结面。

## 4. 遗留 / NOT_RUN

1. **Export 真跑 BLOCKED 于 translated 页**：需翻译/渲染链（RUN-OCR-DIAG-1 + 翻译 provider）产生产物后，
   StartExport 才能成功；本批未伪造。
2. `get_export_snapshot`/`cancel_export` 成功路径需真实导出记录（当前仅 typed 负例）。
3. `library_import_folder` 端到端未单独构造目录样例（复用同一 coordinator；目录签名/identity 逻辑在
   HostIssuer 中，import_file 成功样例反向验证签名正确性）。
4. reveal 的成功路径同样依赖真实导出记录，当前以 typed 负例 + 白名单校验为证。
5. 并发注意：本分支基于 `b993e68bb`；若 NS-WIRE-B1/S4-CMD-BATCH-1 先落地 registry，集成时以先落地者为准，
   本分支需 rebase（冲突点预计仅 registry/dispatcher 计数与列表）。
6. 需独立 Review（Owner 不得自审）。
