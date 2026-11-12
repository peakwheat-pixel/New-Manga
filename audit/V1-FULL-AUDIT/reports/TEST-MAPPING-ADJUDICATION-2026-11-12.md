# 段 B 测试映射裁决

日期：2026-11-12（UTC 07:45；Asia/Shanghai 15:45）
审计基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
裁决时 HEAD：`4534fed56da100e01bcef55197d97d448046f30d`
ZCode session：`sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`
ZCode turn：`turn_ef45a99a-6055-4dca-8822-88fd76189aa6`（CLI EXIT 0）

本文件记录测试范围映射裁决，不是测试结果或 Release Gate 结论。ZCode 本轮只读了任务卡、审计 runner、Avalonia 构建/测试配置、AD-002、段 B 基线报告、范围裁决和恢复点；未运行测试、未修改仓库文件。

## suite 映射

| suite | 段 B 处理 | 依据与限制 |
|---|---|---|
| `pytest` | 部分适用 | Python Core 是当前架构的保留权威；根 `tests/` 可作 Core 侧证据，但不覆盖 Avalonia。tests 是否混有 Legacy 专属断言未逐项分类，不能把整个结果记为当前产品全量 PASS。 |
| `frontend`、`rust`、`desktop` | 当前产品不适用 | runner 指向 `apps/desktop/frontend` 和 `apps/desktop/src-tauri`；AD-002 将 Tauri/React/Rust 标为旧壳，S5 后冻结为历史证据、不参与发布。登记为 `NOT_RUN-legacy`，或明确声明只审计 Legacy 历史证据。 |
| `governance` | 适用 | 与前端栈无关。段 B 既有 default、TaskPath、18 pins 和 API 清单门禁均 EXIT 0。 |
| `probes` | 适用 | 位于审计目录，可作审计工具自身探针证据。 |
| `smoke` | 部分适用 | `core` 适用，`wire` 与保留的 Core/wire 契约相符但仍需核 runner；`packaged` 目标未查明，核对 `tools/smoke/plugins` 后才能判定当前发布件适用性。 |
| `dependencies` | 部分适用 | `pip-check` 适用；`npm-audit` 面向 Legacy 前端，不作为当前产品依赖结论。 |
| Avalonia `.NET` | runner 缺项，建议补充 | 仅在允许的 `audit/V1-FULL-AUDIT/tests/audit_runner.py` 增加 `.NET` suite；不改产品、测试、csproj、props 或依赖。根 pytest 不能替代该测试面。 |

## .NET 执行边界（获准方案，尚未执行）

建议命令：

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-restore --artifacts-path "G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\dotnet\artifacts" --results-directory "G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\dotnet\results" --logger "trx;LogFileName=app-tests.trx" -v:minimal
```

- 不执行 restore、依赖/SDK/workload 安装；现存 `obj/project.assets.json` 是 `--no-restore` 的前提。若资产漂移导致失败，按实际 EXIT 记录，不为跑通而 restore。
- `--artifacts-path` 与 `--results-directory` 将正式产物写入仓外 task-env，但 MSBuild 仍可能在项目旁写 `obj/` 中间文件。执行前后都记录 `git status --porcelain`；出现未忽略残留立即停止。忽略的生成物也在报告中披露。
- 设置 `DOTNET_CLI_TELEMETRY_OPTOUT=1`。目标为 `net9.0`，环境 SDK 为 `10.0.401`；该差异如实记为环境限制。
- 当前 `NewManga.App.Tests` 使用 `Avalonia.Headless.XUnit`；headless 测试不等于真实 GUI 验收。真实 GUI 会话不可用时只能记 `BLOCKED`/`NOT_RUN`。

## AUDIT-01–14 清单缺口与停止条件

审计 DAG 目前只给出阶段级标签（架构/静态、导入/数据、OCR/SFX/翻译/图像、UI、性能/安全/交付、E2E/需求覆盖），没有 01–14 的逐项定义。执行方已对 `audit`、`doc`、`verification`、`archive` 下 Markdown/JSON/TXT/Python 文件搜索 `AUDIT-14|15项专项`；命中只有当前 `AUDIT_TASKS.md` 状态行和本 Task 状态行，未找到原始清单。该搜索不读取媒体内容。

因此不能从阶段标签推猜逐项验收要求。无法映射的项按 `BLOCKED-ARCH-MISMATCH` 记录；继续全量专项测试前需 ZCode 对“原始清单缺失”作进一步范围裁决。`frontend`/Rust/旧 npm suite 默认 `NOT_RUN-legacy`；真实 GUI 或旧库缺失按 Task 要求逐项记 `NOT_RUN`，不得以 headless/Mock 替代。

须停止并取得新裁决的情形：需要修改产品、测试、冻结契约、Schema、依赖或构建配置；出现不受忽略的构建残留；测试触及素材内容、输出真实用户路径或暴露新用户数据；基线/工作树条件变化；治理修复越出 Task allowed_paths；需要 push、远端操作、删除或 Git 历史处置；`packaged` smoke 目标不属于当前发布件且缺少当前打包验收口径；原始 01–14 清单缺失导致范围歧义。

## 下一步

先就原始 AUDIT-01–14 清单缺失向 ZCode 申请下一项只读裁决。裁决前，不运行 probes、pytest、`.NET` 或其他专项测试，不更改任何产品文件。此前既有 AUDIT-00 与治理门禁结果保持原状态，不外推为全审通过。
