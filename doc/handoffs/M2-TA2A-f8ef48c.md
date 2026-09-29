---
task_id: M2-TA2A
author: Codex Desktop
recipient: Codex Desktop
base_commit: eb41a352c03df84400d90a78c29d2dfbe28a76c9
delivery_head: f8ef48c4079e03e57a7ed0da1e9b79c05e90979c
status: complete
---

# Handoff：M2-TA2A

## 交付结果

M2-TA2A 已集成到 `main`，integration commit=`ef13a77bedf8bb06ee222113da186c7bfff09714`。

- 将统一 JA/KO 素材目录接入既有测试资产 catalog；L1 保持 65 个定义，没有为达到数字目标增加目录型 Case。
- 本地取得 Pepper&Carrot E04/E20 日语本地化页面 10 张 JPEG 与官方 SVG language-pack ZIP 2 个，合计 12 个媒体文件 / 40,284,868 bytes。原始作品为法国原创开放 webcomic 的日语本地化，不是日本原创 Manga；E20P06/P07 只有部分机器可读日文文字层。
- 取得 COO 37 XML + license、Manga109Dialog 37 XML + license。二者无配对 Manga109 图像，均为 `PARTIAL`。
- JA inventory 共 88 个文件 / 47,024,650 bytes；全部记录来源、许可、再分发状态、路径、字节数、SHA-256、Ground Truth 类型、Pipeline 适用性与执行状态。12 个媒体文件在主工作区已按 manifest SHA-256 迁入本地 ignored 目录。
- Manga109 图像为 0；Manga109、JMangaBench_Mixed、Text Mask 仍 gated。OpenMantra 未取得，原因是 CC BY-NC 4.0 的非商业使用范围尚不明确。
- KO Webtoon 10/10 继续为资产文件 `READY`；这不代表应用 Pipeline 成功。

## AC 与验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 来源类型、许可和图像边界 | 逐项核对上游实物类型与许可 | Windows 主工作区，集成收口 | PASS | `verification/M2-TA2A/source-audit.md` |
| AC2 公开日语页面与源文字 | 下载 10 页 JPEG、2 ZIP；检查所选 SVG 日文文本层 | 主工作区本地资产，逐文件 SHA-256 对照 manifest | PASS；文本层仅 E20P06/P07 部分可用，Open Ground Truth 仍 PARTIAL | `test_assets/comic_golden_suite/manifests/local_asset_inventory.json`、`verification/M2-TA2A/source-audit.md` |
| AC3 gated / annotation-only 状态 | JA regression verify | integration `ef13a77b` | PASS：37 `MISSING_GATED_ASSET`、10 READY | `verification/M2-TA2A/integration-checks.log` |
| AC4 文件元数据与完整性 | inventory verify：88 files / 47,024,650 bytes；74 XML 解析、2 ZIP 全成员 CRC；12 媒体从 source hash 迁入 | Windows 主工作区 | PASS | `test_assets/comic_golden_suite/manifests/local_asset_inventory.json`、`verification/M2-TA2A/integration-checks.log` |
| AC5 CLI 与重复下载 | `python -m pytest tests/m2_test_assets -q`；JA Smoke verify/list/missing/download | 主工作区 integration `ef13a77b` | PASS：23 passed；各 CLI EXIT 0；重复下载为 0 新文件 / 20 已存在 | `verification/M2-TA2A/integration-checks.log` |
| AC6 Git 边界 | tracked extension audit、annotation 内 jpg/png/zip ignore probes | 主工作区 integration `ef13a77b` | PASS：跟踪漫画媒体 0；本地原图/归档 ignored | `verification/M2-TA2A/integration-checks.log` |
| AC7 独立 Review 与 Pipeline 口径 | DeepSeek Harness R1/R2、Codex 集成回放 | R2 reviewed `f8ef48c4`；integration `ef13a77b` | PASS；R2 APPROVED；应用级 Pipeline NOT_RUN | [`Review`](../reviews/M2-TA2A-f8ef48c.md)、`verification/M2-TA2A/run-results.md` |
| 已知项目基线 | `tests/m2_acceptance` / `tests/core` | 本 Task 范围外 | 未重跑：`BASELINE_FAILURE`（8 failed / 24 passed / 3 skipped）；`BLOCKED_BY_ENV`（PySide6 collection errors） | `verification/M2-TA2A/run-results.md` |

OCR、Text Detection、Bubble Detection、Region、Reading Order、SFX、Speaker Attribution、Translation、Inpainting、Typesetting、重新渲染及 Webtoon 临时切片/重组的应用级验证均为 `NOT_RUN`。

## 接收方式

- 仓库：`G:/CODEX/New Manga`
- 分支：`main`
- 实现 branch/worktree：`agent/codex/M2-TA2A-ja-public-assets` / `C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga`，保留以供恢复。
- 集成点：`ef13a77bedf8bb06ee222113da186c7bfff09714`；代码交付 head=`f8ef48c4079e03e57a7ed0da1e9b79c05e90979c`。
- Smoke 复现：`python -m pytest tests/m2_test_assets -q`；`python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke`；`python test_assets/comic_golden_suite/tools/assets.py verify --language ko --level smoke`。
- JA 原始媒体需从本机 `test_assets/comic_golden_suite/日漫_JA/` 使用；它们被 Git 忽略，不在提交中。

## 下一任务建议

- **Task ID / 标题：** M2-TA2B — Manga109 Authorized Import（已登记 `proposed / BLOCKED_BY_ASSET_ACCESS`，未 release）。
- **推荐 Agent / Reviewer：** Owner=ZCode；Reviewer=DeepSeek Harness；Integrator=Codex Desktop。Owner 与 Reviewer 不同。
- **推荐原因与前置依赖：** 只在用户已通过官方渠道合法取得、且本机已有可核验的 Manga109-v2026 官方归档时释放 TA2B。不要请求凭据或尝试绕过访问控制。TA2A 已完成；M2-TA3 仍须等待 TA2B 可用范围明确。
- **Recovery point：** 仓库 `G:/CODEX/New Manga`，branch=`main`；最新已知资产集成=`ef13a77bedf8bb06ee222113da186c7bfff09714`。TA2B 尚无 branch/worktree；Codex 需在 access gate 满足后重新检查并登记当时的 HEAD/base、branch、worktree 和 allowed paths。
- **允许修改路径：** 释放时由 Codex 在 `doc/tasks/M2-TA2B.md` 冻结；建议仅测试素材 manifest、Manga109 本地 ignored image 目录、素材 loader/tool 专用测试、`verification/M2-TA2B/**`、Task/Handoff/Review 及必要状态导航。
- **禁止范围与新增授权条件：** 禁止非官方镜像、盗版站、绕过 gated access；禁止把 Manga109 原图或归档加入 Git。用户已授权本任务系列，无需重复索要用户授权；但必须实际存在官方合法本地归档，技术上无法取得时维持 `BLOCKED_BY_ASSET_ACCESS` 并停止导入。
- **交付物：** 80–120 个固定 Golden Pages 的实际图像、对应官方 annotations、源/许可与归档 checksum、逐 Case inventory、`READY` 证据、工具测试、独立 Review、Codex 集成记录与 Handoff。未取得的范围仍标 blocked，不计为 runnable。
- **验证命令、环境与 Gate：** 使用本项目 `tools/assets.py` 与 `tests/m2_test_assets`；验证官方归档、页面图像与 annotation 的配对、逐文件 checksum/size、Windows 路径、L0/L1 Case 枚举、`git ls-files` 中原图为 0、重复执行不覆盖。OCR 等应用级能力未运行则仍为 `NOT_RUN`。进入 `done` 前须 Reviewer≠Owner、测试与 Codex integration verification 通过。
- **可直接转发给 Agent 的指令：**

> 执行 New Manga 项目的 M2-TA2B — Manga109 Authorized Import。先检查 `G:/CODEX/New Manga` 当前 `HEAD`、工作区、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 与 `doc/tasks/M2-TA2B.md`。该 Task 当前是 `proposed / BLOCKED_BY_ASSET_ACCESS`，未 release；只有当本机已存在能够验证来源与版本的 Manga109-v2026 官方合法归档，Codex 完成新 Task release 并冻结 base/branch/worktree/allowed paths 后才可实施。若官方归档不在本机，保持 `BLOCKED_BY_ASSET_ACCESS`、记录检查结果并停止；不要索取 token/密码，不要访问非官方镜像或盗版站，也不要绕过授权。归档可用后，仅导入并筛选约 80–120 个代表页，不要把 21k+ 页面放进普通回归。原图和归档必须留在 Git ignored 本地目录；Git 不得跟踪任何 Manga109 图像。对每页记录官方来源、许可、图像再分发状态、相对路径、文件数/字节数、SHA-256、配对 annotation/ground-truth 类型和适用 Pipeline。验收要求：manifest 与 Case ID 可解析且唯一；真实文件与标注配对校验通过；L0/L1 只枚举实际可运行素材；缺失 gated 内容不算 runnable；重复运行不破坏数据；`python -m pytest tests/m2_test_assets -q` 及定向资产 verify 通过；git 媒体跟踪数为 0；应用 Pipeline 未实际运行则记 `NOT_RUN`。提交独立 Review 与 Handoff，由 Codex 集成并记录真实命令、结果和退出码。不要修改生产 Schema、migration、Pipeline、Provider、dependency lock 或 UI。

## 风险与遗留

- Manga109 官方图像仍不可用；JMangaBench_Mixed 与 Text Mask 不构成完整可运行图像资产。
- Open Ground Truth 为 PARTIAL，当前公开页面不是日本原创 Manga，且机器可读日文文字层不完整。
- KO `READY` 使用结构校验，不是 identity SHA-256 pinning。
- 无关基线不在本 Task 修复范围内；详情见 `verification/M2-TA2A/run-results.md`。
