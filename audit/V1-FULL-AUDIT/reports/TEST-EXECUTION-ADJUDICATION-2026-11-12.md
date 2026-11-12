# 段 B 测试执行边界裁决

日期：2026-11-12（UTC 07:59；Asia/Shanghai 15:59）
审计基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
裁决时 HEAD：`8453559b1827795152e89b2d5ccf9136f8dc5936`
ZCode session：`sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`
ZCode turn：`turn_43c7abf5-aa04-419b-942d-c4f419c3da38`（CLI EXIT 0）

本文件记录只读范围与执行安全裁决，不是测试结果。ZCode 没有运行命令或测试、没有修改文件。当前 suite 证据与 AUDIT-01–14 逐项结论分开登记。

## ZCode 裁决

### smoke

| 层 | 段 B 处理 | 依据 |
|---|---|---|
| `core` | 适用 | 运行 Python Core 生产组装的插件沙箱检查。 |
| `wire` | 适用 | 启动真实 Python Core 子进程，检查 stdio JSON-lines 2.3；与 AD-002 保留的 Core/wire 协议一致。 |
| `packaged` | `NOT_RUN-legacy` | `tools/smoke/checks/packaged.py` 将 bundle 固定定位至 `apps/desktop/src-tauri/target/core-sidecar/...`，属于旧 Tauri 壳。当前 Avalonia 发布件无对应 smoke；该打包验收口径缺口保留，不扩写 `tools/smoke/**`。 |
| `frontend` | `NOT_RUN-legacy` | 指向旧 React 前端。 |

runner 中 smoke 命令应限定 `--only core,wire`。`packaged`、`frontend` 不能混入当前产品 smoke 结果。

### .NET

- 目标口径是 `apps/desktop-avalonia/NewManga.sln` 中全部 8 个测试 `.csproj`，但每个项目单独执行；不得用 solution 级单次 test 混合失败归因。
- 本次只读核验：8 个测试项目各自在仓库默认 `obj/project.assets.json` 均存在；外部 task-env 的 `artifacts/obj/NewManga.App.Tests/project.assets.json` 不存在。
- `dotnet msbuild` 的属性求值显示 `ArtifactsPath` 会将 `MSBuildProjectExtensionsPath`、`obj` 和 `bin` 全部移到外部目录。配合 `--no-restore` 会失去仓库现有 restore 状态；ZCode 判定 `--artifacts-path` 方案作废。禁止复制 `project.assets.json` 等 restore 派生文件到外部以伪造状态。
- 可执行命令模板（每个 `.csproj` 单独执行；将 `<project-name>` 换成唯一名）：

```powershell
dotnet test <csproj> --no-restore --results-directory "G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\dotnet\results" --logger "trx;LogFileName=<project-name>.trx" -v:minimal
```

- 设置 `DOTNET_CLI_TELEMETRY_OPTOUT=1`、`DOTNET_NOLOGO=1`。TRX 写到仓外；默认 `obj/bin` 写入仅接受被 `.gitignore` 覆盖的派生物，执行前后必须逐字节比较 `git status --porcelain`。仅当输出完全相同且 tracked 文件零变化才可继续下个项目；出现任何未忽略写入立即停止，不清理、不回滚，登记 `BLOCKED-UNTRACKED-RESIDUE` 并取新裁决。
- 每项只读检查项目 restore assets；缺失时登记 `BLOCKED-NO-RESTORE-STATE`，不 restore、不安装依赖、不改 csproj/props、不更换 SDK。测试失败照实记录 EXIT，不得绕过。
- headless `.NET` 测试不是 GUI 验收；真实 GUI 不可捕获时维持 `BLOCKED`。

## 当前分开登记的状态

- `AUDIT-01–14` 每项均为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`（具名阻断、未测试）；任何 suite EXIT 0 都不能改变逐项状态。
- suite 维度：`pytest` 为 Python Core 限定证据；`dotnet` 待执行；`probes` 待执行；`governance` 已有通过结果但需绑定最终审计 HEAD 复跑；`smoke-core,wire` 待执行；`frontend/rust/desktop/npm-audit/packaged` 为 `NOT_RUN-legacy`。Task 维持 `in_progress`，AC2/AC3 保持 `PARTIAL`。
- 运行顺序：probes → pytest → 8 个 `.NET` 项目逐项 → smoke `core,wire` → governance 复跑。每条 suite 记录 argv/cwd/start/elapsed/EXIT、结果文件和实际工作树前后状态；不把 suite 结果写成 AUDIT-NN PASS。
- 用户可后续提供 2026-10-24 原始审计指令，或正式裁决以阶段级口径取代逐项口径；在此之前不得自行代拟清单或解锁逐项状态。收到新输入后先停用本裁决通道并重新映射。

## 停止条件

除既有 Task/ZCode 范围外，以下情况立即停下：任何 suite 结果被归属为 AUDIT-NN 已完成/PASS；需要改产品/测试/构建配置/契约/Schema/依赖或执行 restore/install；测试触碰私有素材内容或输出真实路径；工作树前后 porcelain 不同；测试项目 restore assets 缺失；当前 Avalonia 发布件需要新定义 packaged 验收口径。
