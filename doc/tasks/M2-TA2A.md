---
id: M2-TA2A
title: JA Public Assets Bootstrap
kind: asset_infrastructure
status: in_progress
approval: user_authorized_2026-09-29
suggested_owner: ZCode
owner: Codex Desktop
reviewer: DeepSeek Harness
depends_on: [M2-TA1]
base_commit: eb41a352c03df84400d90a78c29d2dfbe28a76c9
branch: agent/codex/M2-TA2A-ja-public-assets
worktree: C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga
integration_commit: null
---

# M2-TA2A：JA Public Assets Bootstrap

## 来源与目标

来源：[M2-TA1](M2-TA1.md) 资产状态、[素材来源审计](../../verification/M2-TA1/asset-sources.md) 与用户 2026-09-29 对 JA 资产优先级的明确调整。目标是在不使用 Manga109 gated 图像、不从非官方镜像取数的前提下，把当前合法公开可取得的日语漫画/漫画风格页面和可配对标注真正落到本地，并形成可复验清单。`READY` 只表示该 Case 的预期文件存在且完整性验证通过，不表示应用 Pipeline 已验证。

## Acceptance Criteria

- [ ] AC1：逐项审计 JMangaBench_Mixed、Manga109 public annotations、COO、Manga109Dialog、Text Mask、Open Ground Truth 及本地已登记的 JA 来源；区分图像、annotation、transcription、mask、metadata、code-only，并分别记录来源、license、图像再分发状态、实际访问/下载入口和是否依赖 gated 图像。
- [ ] AC2：对无需额外授权且许可明确的来源执行实际下载；至少取得一组日语图像与其真实 source transcription/ground-truth 文件。若来源是日语翻译版开放 webcomic，须准确标为该类型，不得称为日本原创 Manga。
- [ ] AC3：只有 annotation 没有配对图像的 Manga109 相关数据保持 `PARTIAL`；JMangaBench、Text Mask 或其他依赖 Manga109 图像的可运行范围保持 `BLOCKED_BY_ASSET_ACCESS` / `PARTIAL`，不得标为 `READY`。
- [ ] AC4：每个实际落地来源记录 source、license、image redistribution status、local path、file count、byte size、SHA-256 或等效完整性信息、ground-truth 类型、可用于检查的 Pipeline，以及该 Pipeline 的真实执行状态。
- [ ] AC5：本地资产有确定性枚举与校验；重复运行不覆盖已有文件，不完整/损坏下载不发布为 READY；路径兼容 Windows。离线 verify 不应破坏已有资产。
- [ ] AC6：原始漫画/漫画图像与外部归档全部留在 Git 忽略路径；Git 不跟踪任何受版权限制图像。不得修改生产 Schema/migration/Pipeline/Provider、依赖锁、QML/UI 或用户作品数据。
- [ ] AC7：完成独立非作者 Review、Codex 集成检查和证据化 Handoff。OCR、Detection、Translation、Inpainting、Typesetting、Reading Order、SFX、Speaker、Webtoon slicing/reassembly 等应用级结果若未实际运行，保持 `NOT_RUN`。

## 允许修改范围

- `test_assets/comic_golden_suite/**`（manifest、README、测试专用工具及本地 ignore 规则）
- `tests/m2_test_assets/**`
- `doc/tasks/M2-TA2A.md`、`doc/handoffs/M2-TA2A-*.md`、`doc/reviews/M2-TA2A-*.md`
- `verification/M2-TA2A/**`
- Codex 仅回填 `doc/00_INDEX.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 中本任务状态和导航。

## 禁止范围

- 不申请或使用 Manga109/Manga109-s gated token/数据，不绕过登录、许可或官方访问控制，不使用第三方镜像。
- 不把 Manga109、商业 Webtoon 或其它不可再分发漫画原图、衍生页图或数据归档提交 Git。
- 不把 annotation license 推导为底层漫画图像许可；没有明确商业/再分发权链时不下载、不标 READY。
- 不扩充 L1 到 100–150；不改生产 Schema、migration、Pipeline、Provider、依赖锁、QML/UI 或正式 Library 数据。
- 不修复或重跑无关基线问题作为本 Task Gate；`tests/m2_acceptance` 的历史 `BASELINE_FAILURE` 和 `tests/core` 的 `BLOCKED_BY_ENV` 继续如实保留。

## 并行与依赖顺序

硬依赖：M2-TA1=`done`。以下只读来源审计和互不重叠的资产获取可并行；对共享 `cases.json`、source inventory、README 与状态文档的合并必须由 Integrator 串行完成：

1. 已完成只读源审计：Manga109 相关 benchmark/annotation 与独立开放日文素材分开查证。
2. 可并行轨 A：合法开放的日语页面、对应文本源文件下载和本地校验。
3. 可并行轨 B：CC BY 4.0 的 COO / Manga109Dialog annotation 子集下载；只标 `PARTIAL`，不配图不跑视觉评测。
4. 串行集成：核验所有路径/哈希/字节数，回填 manifest、README、inventory 与工具测试，完成 Review 和 Codex integration verification。
5. M2-TA2B 是独立 gated follow-up；没有官方合法归档时不执行。M2-TA3 的 L1 扩展须等本 Task 完成，且 TA2B 可用范围明确后再释放。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| Catalog/校验器 | `python -m pytest tests/m2_test_assets -q` | Windows / Python；跟随资产工具变更 | NOT_RUN | `verification/M2-TA2A/` |
| 新增 JA 素材 | `python test_assets/comic_golden_suite/tools/assets.py verify --language ja --level smoke` | 已下载的公开源 | NOT_RUN | `verification/M2-TA2A/` |
| 重复下载与网络失败 | 执行公开源下载两次；对离线/损坏输入执行 verify，不覆盖有效文件 | 临时或本地缓存 | NOT_RUN | `verification/M2-TA2A/` |
| Manga109 gated 不误报 | `list/missing/download --language ja` 无官方 archive | 不提供 gated 凭据 | NOT_RUN | `verification/M2-TA2A/` |
| Git/版权边界 | `git ls-files`、`git check-ignore --no-index -v`、`git diff --check` | 集成 HEAD | NOT_RUN | `verification/M2-TA2A/` |
| 应用 Pipeline | OCR/Detection/Translation/Inpainting/Typesetting 等 | 本 Task 不改生产链路 | NOT_RUN | 不作为本 Task 的 READY 含义 |

Known baseline: `tests/m2_acceptance` 之前已证明 `8 failed / 24 passed / 3 skipped` 为 `BASELINE_FAILURE`；`tests/core` 因缺 PySide6 为 `BLOCKED_BY_ENV`。本 Task 不修复它们。

## 交付与运行记录

- Handoff：待完成。
- Review：待完成，Reviewer 必须为非作者。
- Integration：待 Codex 审核固定 delivery head 后记录。
