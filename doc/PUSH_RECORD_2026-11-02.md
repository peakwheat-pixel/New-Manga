# Push 记录：干净源码快照新分支（2026-11-02）

## 1. 授权与边界

- 授权：用户 2026-11-02 直接指示 **push**；沿用 2026-10-26 / 2026-10-29 已确认口径：**只推材料已隔离的干净源码快照到 `origin` 的新分支**。
- 允许范围：仅将材料已隔离的干净源码快照作为 `origin` 的**新分支**普通推送。
- 明确禁止并已遵守：force push、推送 `main`、覆盖远端 `main`、设置上游 tracking、改写本地 `main` 历史、传播私有漫画/审计/验证材料、修改系统 ACL、删除/清理素材或 refs。

## 2. 推送对象

| 项 | 值 |
|---|---|
| 快照本地目录 | `G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261102` |
| 目标远端分支 | `clean-snapshot-20261102`（新建） |
| 推送 commit | `ac7d488e1944893f961b94eb3d774c899f618829` |
| commit 性质 | 单一 root commit，无父提交；独立仓库无 remote、无 alternates/shallow/grafts/replace |
| 源 commit | 本地 `main` HEAD `5c12ab269`（FEA-06-PREREQ-2 done） |
| tracked 文件 | 1413 |
| 内容体积 | 21,120,652 B（约 20.1 MB） |
| 图片文件 | 0（白名单路径内无 jpg/jpeg/png/webp/gif） |

## 3. 导出白名单与剔除

- 白名单：`apps/`、`src/`、`tests/`、`packaging/`、`test_assets/`、`pytest.ini`、`requirements.txt`、`requirements-dev.txt`、`.gitignore`、`.gitattributes`、`tools/p02`、`tools/smoke`。
- 与 2026-10-29 口径的差异（本次增补，均为公开非私有材料）：
  - 仓库根 `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`PRIVACY.md`、`README.md`——GPL-3.0 分发合规所需；
  - `doc/design/redesign-v1/40-fusion/tokens.json`——构建期 `Content` 复制（DesignSystem.Tests / ThemeEngine.Tests）与测试仓库根定位所需；该文件为冻结设计令牌，无私有材料。
- 剔除（禁区检查 PASS，均不存在于快照）：`verification/`、`doc/`（除上述单文件）、`docs/`、`audit/`、`wiki/`、`archive/`、`experiments/`、`.orchestrator/`、`.codex/`、`.dsh/`、`.agents/`、`.gemini/`、`.qoder/`、`.workbuddy/`、`.codewiki/`、`.tmp.driveupload/`、`AGENTS.md`、`GOAL.md`、`tools/governance`、`training_data/`、`weights/`。

## 4. 推送前验证（快照目录内独立执行）

| 项 | 结果 |
|---|---|
| `git ls-files` | 1413 |
| 禁区泄漏检查 | PASS（禁区路径 0；`doc/` 仅 `doc/design/redesign-v1/40-fusion/tokens.json`） |
| 图片检查 | 0 |
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug -warnaserror` | **exit 0**，0 警告 / 0 错误 |
| `NewManga.Appearance.Tests` | 21 passed / 0 failed / 0 skipped |
| `NewManga.Host.Tests` | 51 passed / 0 failed / 28 skipped |
| `NewManga.ThemeEngine.Tests` | 253 passed / 0 failed / 0 skipped |
| `NewManga.DesignSystem.Tests` | 86 passed / 0 failed / 0 skipped |
| `NewManga.ApplicationCore.Tests` | 31 passed / 0 failed / 0 skipped |
| `NewManga.App.Tests` | 452 passed / 0 failed / 7 skipped |
| `NewManga.CoreClient.Tests` | 114 passed / **11 failed** / 25 skipped |

**11 个失败的原因（已知快照口径限制，非代码回归）**：`CommandParityContractTests` / `CommandContractV11RTests` / `RegionWriteCommandTests` 依赖仓库根的 `AGENTS.md` 与 `verification/HOST-COMMAND-MIGRATION-1/parity/*.json` 等契约证据；本快照按口径剔除 `AGENTS.md` 与 `verification/`，因此这些证据型契约测试无法定位证据。完整仓库基线为 **1022/0/57**（本轮集成验证通过）。外部协作者做 UI 时以 `App.Tests` + 构建为准即可。

## 5. 实际推送

执行者：DeepSeek Harness（Lead / Integrator）。

```text
git -C "G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261102" push --no-follow-tags https://github.com/peakwheat-pixel/New-Manga.git HEAD:refs/heads/clean-snapshot-20261102
```

- 结果：`* [new branch] HEAD -> clean-snapshot-20261102`，**exit 0**。
- 远端回读 `git ls-remote --heads origin`：
  - `clean-snapshot-20261102` = `ac7d488e1944893f961b94eb3d774c899f618829`（新）
  - `clean-snapshot-20261029` = `22de8608622eaa6e8e56fbb9cad31b5ae7563c61`（未变）
  - `clean-snapshot-20261026` = `e8147c6c8a7edde4e5784999454acb5732a869fb`（未变）
  - `codex/clean-source-snapshot` = `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`（未变）
  - `main` = `b1c1f5a56840988e149c18375f6e414bf5c7fbda`（未变，未推送本地 main）
  - `public-release` = `4d6c3fead0a46ffecc624556595f1b23cfd20d6d`（未变）
- 未使用 force、未推送 `main`、未设置上游、未传播私有素材。

## 6. 外部协作者使用方式（给后续 Task/沟通引用）

1. `git clone https://github.com/peakwheat-pixel/New-Manga.git`（或 fork 后 clone）。
2. 基于 `clean-snapshot-20261102` 开个人分支：`git checkout -b ui/<name> origin/clean-snapshot-20261102`。
3. 只在个人分支/fork 工作；完成后提 PR 或回传 patch；**不得 push main**。
4. 交付物：固定 commit + 测试输出 + 截图 + Handoff。
5. 由未参与实现者独立 Review，DSH 集成。

## 7. 未改变的状态

- 本地 `main` 未推送（本地 `main` = `5c12ab269`；远端 `main` = `b1c1f5a5…` 保持旧状态，未公开历史材料）。
- 未设置 upstream tracking；`GIT-CLEAN-PUBLICATION-1` 的 AC4/AC5 状态不受影响（本记录描述快照分支口径，不等于该 Task 通过）。
