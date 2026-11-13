# SEC-01：AUDIT-11-INC-001 远端可见性只读调查

**Task：** SEC-01-REMOTE-VISIBILITY-1
**执行者：** DSH（2026-11-14 用户指令：所有任务交 DSH，自动裁决/规划，全部授权，无需用户介入）
**执行时间：** 2026-11-13T17:37Z–17:38Z（UTC；本地 2026-11-14 01:37–01:38 +08:00）
**仓库：** G:\CODEX\New Manga，branch main，调查开始时 HEAD=`5b32adaefa4875d0a61b344797f7cf5789f49ff4`
**远端：** `https://github.com/peakwheat-pixel/New-Manga.git`

## 方法（全部只读）

1. `git ls-remote --heads origin`（`GIT_TERMINAL_PROMPT=0`，匿名，不交互）。
2. GitHub REST API 匿名 GET（`User-Agent: dsh-audit-sec01`）：
   - 仓库元数据 `GET /repos/peakwheat-pixel/New-Manga`
   - 提交可见性 `GET /repos/.../commits/{cc88d1ee9fdd27825869b4cdc0a1b68965b3d1fc}`、`GET /repos/.../commits/b1c1f5a5`
   - 路径存在性 `GET /repos/.../contents/.tmp.driveupload?ref={cc88d1ee|b1c1f5a5}`
3. 未下载、未输出任何素材文件内容；未执行 push、删除、历史改写、上传或远端补救；未读取私有素材内容。

## 结果

| 检查 | 状态 | 结果 |
|---|---|---|
| `git ls-remote --heads origin` | EXIT 0 | 匿名可访问；远端有 `main`（`9b068382…`）、`clean-snapshot-20261026/20261029/20261102`、`codex/clean-source-snapshot`、`public-release` |
| GitHub 仓库元数据 | HTTP 200 | 仓库对匿名访问公开可见 |
| commit `cc88d1ee9fdd27825869b4cdc0a1b68965b3d1fc`（2026-10-30 push 目标之一） | HTTP 200 | 公开可见；该 commit 变更列表仅 1 个文档文件 |
| commit `b1c1f5a5`（push 目标、当前 HEAD 祖先） | HTTP 200 | 公开可见 |
| `.tmp.driveupload` 在 `cc88d1ee` 树中 | HTTP 200 | 目录存在，可枚举文件（例：`183038`，blob `3ca9cf44…`，190 bytes；列表响应约 1.0MB） |
| `.tmp.driveupload` 在 `b1c1f5a5` 树中 | HTTP 200 | 目录存在，可枚举文件（同一文件 `183038`，blob `3ca9cf44…`） |
| `.tmp.driveupload` 在默认分支当前 tip | HTTP 404 | 不在默认分支 tip 的当前树 |

证据：`logs/git-ls-remote.log`、`logs/github-api-probe*.log`、`evidence/github-api-probe*.json`（仅 metadata/状态，无素材内容）。

## 结论

**AUDIT-11-INC-001 的远端可见性从“unknown”升级为“已确认可见（历史树可枚举）”。**

- 仓库对匿名访问公开；2026-10-30 推送目标 `cc88d1ee` 与 `b1c1f5a5` 均公开可见。
- `.tmp.driveupload` 在 `cc88d1ee` / `b1c1f5a5` 的历史树中存在且可通过公开 API 枚举文件与 blob SHA；这些对象的字节属于公开可 fetch 范围（本调查未 fetch、未下载）。
- 该目录不在默认分支当前 tip，但历史 tree/blobs 仍可通过公开仓库历史访问；GitHub 页面/API 提供 blob 链接。
- 本结论不声称“已下载/传播素材”，也不声称所有私有素材文件的字节均已核验；只确认历史树与对象元数据在公开远端可访问。

## 限制与边界

- 未下载或展示任何素材内容；未验证每个素材文件的字节级内容（仅目录/文件名/blob SHA/size metadata）。
- 未执行 `git fetch` 远端对象（会下载历史与素材字节）；未使用 GitHub 网页抓取。
- 未评估 GitHub 缓存/CDN 或派生 fork/clone；未执行任何补救。
- 远端可见性确认不等于已发生公开传播的完整取证（第三方 clone/fork/缓存未知）。

## 后续（不在本 Task 内）

- 需要一个独立、明确授权的处置 Task 决定是否修复远端暴露面（删除分支、force-push 改写历史、联系平台等均不可逆且有外部影响）；本 Task 不执行任何远端写操作。
- 在处置 Task 前保留现状与证据；不传播素材、不复制素材内容。
