---
id: M2-TA1
title: Unified Japanese/Korean comic test asset foundation
kind: test_infrastructure
status: done
release_state: M2_TA1_USER_REQUEST_RELEASED
approval: approved_by_user_request_2026-09-29
suggested_owner: Codex
owner: Codex
reviewer: Codex (independent reviewer subagent)
integrator: Codex
depends_on: [M2-RG1]
base_commit: 40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be
branch: agent/codex/M2-TA1-comic-test-asset-foundation
worktree: C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga
integration_commit: 1ef8fe7e7e66044869f8c59646d28bfca7692bbe
---

# M2-TA1：日漫 / 韩漫统一测试素材基础设施

## 来源与目标

来源：用户 2026-09-29 提供的 `漫画测试素材包_日漫_韩漫.zip` 集成请求、D07 §98–101、`doc/fixtures/MANIFEST.md`、新架构目标 AD-001 与当前测试入口。

授权状态：用户于 2026-09-29 明确声明全部本地测试使用已授权，后续无需再次申请授权；按请求只下载固定 KO smoke 样本。此声明不改变第三方数据集的访问控制、来源限制或再分发属性。

现实基线：base=`40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be`；STATUS 中原无 Active Task，本次用户请求授权释放本 Task。附件有目录和元数据但无图像；当前没有 `test_assets/`，仓库已有的 `doc/fixtures/MANIFEST.md` 面向通用合成/容量 fixture，不能替代漫画语料 case catalog。

目标：在 `test_assets/comic_golden_suite/` 建立单一日漫/韩漫 case catalog、只用 Python 标准库的枚举/校验/显式下载工具、受保护原始素材的 Git 忽略边界和状态文档。该目录是测试数据基础设施；不装入正式应用，不创建第二个测试 runner，不修改生产 Pipeline/Schema/Provider/依赖。

## Acceptance Criteria

- [x] AC1：一个规范 JSON manifest 覆盖附件的 10 个 KO Webtoon、8 个 KO Pepper&Carrot 来源页、37 个 Manga109 选定作品；55 个 `case_id` 唯一，JA/KO 统一使用同一 schema，20 个 L0 smoke case 可枚举。
- [x] AC2：case 字段至少有 `case_id`、`language`、`source`、`source_type`、`layout_type`、`reading_direction`、`text_type`、`orientation`、`difficulty`、`tags`、`local_path`、`license_class`、`redistributable`、`expected_pipeline`、`ground_truth_available`、`levels`、`asset_status`；`levels` 是可多选的 level 字段；difficulty tags 精确覆盖用户列出的 16 项。
- [x] AC3：单一标准库 CLI 提供 `download`、`verify`、`list`、`missing` 和 `--language ja|ko`、`--level smoke|regression|full`。无副作用命令离线运行；KO 下载仅在明确请求时联网；Manga109 未取得 gated ZIP 时报告 `BLOCKED_BY_ASSET_ACCESS`，取得后可用 `--archive` 安全导入当前选择的标题。
- [x] AC4：脚本不自动安装依赖、不把 token 写入命令行；KO 下载校验 `Content-Length` 和文件格式后原子无覆盖写入；Manga109 只从用户提供的官方 ZIP 导入所选标题，拒绝危险路径并验证 CRC、数字 JPG 页名与 XML `page@index` 一一对应，不调用 `extractall`。第三方图像/归档全部由素材目录内 `.gitignore` 排除。
- [x] AC5：README/manifest 如实记录本地资产现状、授权需求、可再分发性与 L0/L1/L2 状态；L1 目前只有 55 个定义（目标 100–150），明确标为 `PARTIAL`；L2 不进入日常运行。
- [x] AC6：manifest JSON 可解析、ID 唯一、所有路径限定在套件目录内、Windows 相对路径可用；缺失数据不会被报告为已验证，工具能区分缺失与 gated。
- [x] AC7：新增测试只放新架构专用 `tests/m2_test_assets/`；相关工具检查、既有新架构回归和 Git 版权检查按测试计划执行并归档 EXIT/环境证据。新架构 acceptance 的 8 个既有失败在 base、Task 与集成提交上复现相同测试名，记 `BASELINE_FAILURE`。
- [x] AC8：Task、Handoff、Review、verification 和 STATUS/Plan/Index 导航完整；独立 Review=`approved`，Codex 集成后定向复验通过。

## 允许修改范围

- `test_assets/comic_golden_suite/**`
- `tests/m2_test_assets/**`
- `doc/tasks/M2-TA1.md`、`doc/handoffs/M2-TA1-*.md`、`doc/reviews/M2-TA1-*.md`
- `verification/M2-TA1/**`
- 由 Codex 负责的导航/状态元数据：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`

## 禁止范围

- `src/**`、`apps/**`、SQLite Schema/migration、Provider/IPC/production Pipeline、依赖清单/锁文件。
- Manga109、Webtoon、Zenodo 或其他受版权限制的漫画原图进入 Git。
- 运行附件中的安装器/脚本；默认执行整库下载；绕过 Manga109 审批；把许可不清的数据标成 `READY`。
- 把 Legacy PySide6/QML 测试当作新架构验收路径。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/2 manifest 与 ID | `python -m pytest tests/m2_test_assets -q` | Windows PowerShell 7.6.6 + `C:\Python314\python.exe` 3.14.6；集成 HEAD `1ef8fe7e` | PASS：10 passed | `verification/M2-TA1/post-integration.log` |
| AC3 CLI 枚举/缺失/校验 | `assets.py list|missing|verify --language ja|ko --level smoke`；官方归档 ZIP 导入使用合成安全测试包 | Windows PowerShell + Python 3.14 | KO `READY=10`；JA `MISSING_GATED_ASSET=10`；命令 exit 0；synthetic ZIP select/import/repeat PASS | `verification/M2-TA1/cli-verification.log`、`post-integration.log`、`pytest-m2-test-assets.log` |
| AC4/6 路径安全、重复下载保护、缺失态 | 定向 pytest；ZIP path traversal、页名/index 不匹配、非法 XML index 与截断 HTTP EOF 探针；`git check-ignore` | Windows + Python 3.14；HTTP 错误用 mock | PASS；10 项测试通过；重复下载跳过 80 个文件；原图匹配 ignore | `verification/M2-TA1/pytest-m2-test-assets.log`、`git-ignore-probe.log`、`post-integration.log` |
| 新架构回归 | `python -m pytest tests/m2_acceptance -q --tb=no` | Python 3.14；base main、Task delivery、集成 main | BASELINE_FAILURE：三处均 8 failed / 24 passed / 3 skipped，8 个测试名完全一致；非本 Task 回归 | `pytest-m2-acceptance-*.log`、`post-integration-acceptance.log` |
| Legacy `tests/core` 尝试 | `python -m pytest tests/core -q --tb=no` | 当前 Python 3.14，无 PySide6 | BLOCKED_BY_ENV：4 个 collection error（`ModuleNotFoundError: PySide6`），不作为新架构验收 | `verification/M2-TA1/pytest-core-environment.log` |
| 版权 Git 检查 | `git ls-files test_assets/comic_golden_suite` + Git ignore probe | 集成 HEAD `1ef8fe7e`；素材保持 ignored | PASS：仅 7 个清单/脚本/README/ignore/keep 路径被跟踪，跟踪图像/归档=0；KO/JA media path 命中 `.gitignore` | `verification/M2-TA1/post-integration.log` |
| 外部数据下载/导入 | `assets.py download --language ko --level smoke`；Manga109 gated 路径不取数据；对登记 URL 发送 HEAD | 用户声明授权本地测试；遵循来源非商业研究限制 | KO 10 case / 80 files / 884,913,245 bytes；重复执行 existing=80；M109 无获批 ZIP，真实导入 `NOT_RUN`，仅 synthetic ZIP PASS；AIHub 本次 HTTP 403 | `verification/M2-TA1/asset-sources.md`、`asset-url-head-check.log`、下载器日志 |
| 集成后 Smoke/Git 检查 | 定向 pytest、KO `verify`/repeat download、JA gated status、`git check-ignore`、`git ls-files`、`git diff --check` | Windows PowerShell 7.6.6 + Python 3.14.6；main integration=`1ef8fe7e` | PASS：10 passed、KO READY=10、重复执行 existing=80、JA gated=10、tracked media=0、diff check 0 | `verification/M2-TA1/post-integration.log` |

## 依赖、风险与阻塞

- 依赖 `M2-RG1`（done；仅作为当前新架构基线，不引入生产改动）。
- `Cleaned Webtoon Dataset` 数据卡限定非商业研究用途且明确原画版权属于各权利人；数据卡只将 CC BY-NC 适用于作者注释/metadata。用户于 2026-09-29 授权本地测试使用；素材仍禁止 Git 再分发。
- Manga109 是 gated dataset；当前环境没有 Hugging Face 凭据，保持 `MISSING_GATED_ASSET` / `BLOCKED_BY_ASSET_ACCESS`，不阻塞 manifest/tooling。
- JMangaBench 当前 builder 要求单独取得 Manga109-s；Text Mask 当前记录列出两份合计约 19.2 MB 文件，底层图像来自 Manga109 且再分发许可未确认；都不下载。
- KO smoke 10 个 case 的 8 个文件已下载到 worktree、本地合计 884,913,245 bytes；L0 pipeline 尚无应用集成入口，pipeline 执行记 `NOT_RUN`。
- L1 目标 100–150；附件有 55 个 case 定义。不得制造重复或虚构案例，当前标 `PARTIAL`。
- Text Mask 的 Zenodo 当前记录列出两份约 19.2 MB 文件；页面另有 8.6 GB 全版本统计，不能把后者当作当前下载体积。由于底层关联 Manga109 且当前记录未显示明确再分发许可，本 Task 不下载。

## 交付与运行记录

- Handoff：[M2-TA1-codex](../handoffs/M2-TA1-codex.md)，状态 `completed`。
- Review：[M2-TA1-codex](../reviews/M2-TA1-codex.md)，固定 base/head 的独立 Review=`approved`。
- 实际测试：素材工具 `10 passed`；新架构 acceptance 在 Task head 与 base `main` 同为 `8 failed / 24 passed / 3 skipped`（Python 3.14）；`tests/core` 因缺 `PySide6` collection error；详见 verification。
- 集成 checkpoint：merge=`1ef8fe7e7e66044869f8c59646d28bfca7692bbe`（first parent=`40ce1f91`，second parent=`b72f865b`）；post-integration 定向测试 10 passed，KO 10/10 READY，tracked media=0。main 中原有 dirty/untracked 文件按清单原样保留；Task branch/worktree 与忽略的本机 KO 数据仍保留用于恢复。
