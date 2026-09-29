---
id: M2-TA2B
title: Manga109 Authorized Import
kind: dataset_import
status: proposed
approval: pending_official_manga109_access
suggested_owner: ZCode
owner: null
reviewer: DeepSeek Harness
depends_on: [M2-TA1]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# M2-TA2B：Manga109 Authorized Import

## 状态与启动门

`BLOCKED_BY_ASSET_ACCESS`，本 Task 已登记但**未 release、不得在未满足门槛时开工**。启动条件是本机存在用户依法取得的 Manga109-v2026 官方归档，且归档来源/版本可核验；不要求用户把 gated 凭据交给 Agent。

## 目标

正式满足启动门后，使用项目已有 Manga109 安全 importer 向 `test_assets/comic_golden_suite/日漫_JA/` 导入选定官方图像，从既有代表作品池固定约 80–120 个 Golden Pages。覆盖 normal/dense/tiny、vertical/horizontal/rotated/curved、fragmented SFX、overlap、complex background、low contrast、narration、multi-speaker、unusual balloon、action 和 screentone。`READY` 只表示图像、标注和完整性检查通过。

## 禁止项与前置条件

- 不绕过 gated access；不使用非官方镜像或盗版站。
- 不把 Manga109 原图或归档提交 Git；仅在本地 ignored assets 保存。
- 不因 annotation public/CC BY 推导原图许可；不把全部 21k+ 页面加入普通回归。
- 真实授权归档取得前只维护本 Task 和范围计划；实际下载/导入、Golden Page 确认和执行态必须保持 `BLOCKED_BY_ASSET_ACCESS` / `NOT_RUN`。
- Task 必须由 Codex 在授权条件满足后重新登记 base、branch、worktree 和 allowed paths，再转为 `ready`。
