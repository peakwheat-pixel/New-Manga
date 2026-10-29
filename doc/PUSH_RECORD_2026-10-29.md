# Push 记录：干净源码快照新分支（2026-10-29）

## 1. 授权与边界

- 授权：用户 2026-10-29 在「为外部协作者共享代码做新界面」的上下文中指示 **push**；沿用 2026-10-26 已确认口径：**只推干净源码快照新分支**。
- 允许范围：仅将材料已隔离的干净源码快照作为 `origin` 的**新分支**普通推送。
- 明确禁止并已遵守：force push、推送 `main`、覆盖远端 `main`、设置上游 tracking、改写本地 `main` 历史、传播私有漫画/审计/验证材料、修改系统 ACL、删除/清理素材或 refs。

## 2. 推送对象

| 项 | 值 |
|---|---|
| 快照本地目录 | `G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261029` |
| 目标远端分支 | `clean-snapshot-20261029`（新建） |
| 推送 commit | `22de8608622eaa6e8e56fbb9cad31b5ae7563c61` |
| commit 性质 | 单一 root commit，无父提交；独立仓库无 remote、无 alternates/shallow/grafts/replace |
| 源 commit | 本地 `main` HEAD `7b5f4037420a3635a941b453bdb48eb42267916f` |
| tracked 文件 | 1035 |
| 内容体积 | 17,772,674 B（约 17.8 MB） |
| 图片文件 | 0（白名单路径内无 jpg/jpeg/png/webp/gif） |

## 3. 导出白名单与剔除

- 白名单：`apps/`、`src/`、`tests/`、`packaging/`、`test_assets/`、`pytest.ini`、`requirements.txt`、`requirements-dev.txt`、`.gitignore`、`.gitattributes`、`tools/p02`、`tools/smoke`。
- 与 2026-10-26 口径的差异：`tools/dev` 已不存在，本次不导出；其余一致。
- 剔除（禁区检查 PASS，均不存在于快照）：`verification/`、`doc/`、`docs/`、`audit/`、`wiki/`、`archive/`、`experiments/`、`.orchestrator/`、`.codex/`、`.dsh/`、`.gemini/`、`.qoder/`、`.workbuddy/`、`.codewiki/`、`.tmp.driveupload/`、`AGENTS.md`、`GOAL.md`、`tools/governance`。

## 4. 推送前验证（快照目录内独立执行）

| 项 | 结果 |
|---|---|
| `git ls-files` | 1035 |
| 禁区泄漏检查 | PASS（上述禁区路径全部不存在） |
| 图片检查 | 0 |
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug -warnaserror` | **exit 0**，0 警告 / 0 错误 |
| `NewManga.App.Tests` | **137 passed / 0 skipped / 0 failed** |
| `NewManga.Host.Tests` | 39 passed / 21 skipped / 0 failed（无 sidecar 时按显式 Skip） |
| `NewManga.CoreClient.Tests` | 35 passed / 22 skipped / **4 failed** |

**4 个失败的原因（已知快照口径限制，非代码回归）**：`CommandParityContractTests` 的 `RepoLocator` 要求仓库根同时存在 `apps/desktop-avalonia` 与 `AGENTS.md`，并从 `verification/HOST-COMMAND-MIGRATION-1/parity/*.json` 读取命令契约证据；本快照按口径剔除 `AGENTS.md` 与 `verification/`，因此这 4 个契约测试无法定位证据。完整仓库基线为 249/249（`RELEASE-REPACK-6` / CI 已验证）。外部协作者做 UI 时以 `App.Tests` + 构建为准即可。

## 5. 实际推送

执行者：DeepSeek Harness（Lead / Integrator）。

```text
git -C "G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261029" push --no-follow-tags https://github.com/peakwheat-pixel/New-Manga.git HEAD:refs/heads/clean-snapshot-20261029
```

- 结果：`* [new branch] HEAD -> clean-snapshot-20261029`，exit 0。
- 远端回读 `git ls-remote --heads origin`：
  - `clean-snapshot-20261029` = `22de8608622eaa6e8e56fbb9cad31b5ae7563c61`（新）
  - `clean-snapshot-20261026` = `e8147c6c8a7edde4e5784999454acb5732a869fb`（未变）
  - `codex/clean-source-snapshot` = `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（未变）
  - `main` = `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`（未变，未推送本地 main）
  - `public-release` = `4d6c3fead0a46ffecc624556595f1b23cfd20d6d`（未变）
- 未使用 force、未推送 `main`、未设置上游、未传播私有素材。

## 6. 外部协作者使用方式（给后续 Task/沟通引用）

1. `git clone https://github.com/peakwheat-pixel/New-Manga.git`（或 fork 后 clone）。
2. 基于 `clean-snapshot-20261029` 开个人分支：`git checkout -b ui/<name> origin/clean-snapshot-20261029`。
3. 只在个人分支/fork 工作；完成后提 PR 或回传 patch；**不得 push main**。
4. 交付物：固定 commit + 测试输出 + 截图 + Handoff（`doc/templates/HANDOFF.md` 格式，但该模板不在快照内，可随任务说明单独提供）。
5. 由未参与实现者独立 Review，DSH 集成。

## 7. 未改变的状态

- 本地 `main` 未推送；`GIT-CLEAN-PUBLICATION-1` 的 AC4/AC5 状态不受影响（本记录描述快照分支口径，不等于该 Task 通过）。
- 远端 `main` 仍为 `6a68fdeb9`（1788 files），保持未公开历史材料状态。
