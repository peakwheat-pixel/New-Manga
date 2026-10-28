# Handoff — PUBLIC-RELEASE-P0-1

## 交付结果

- Task：[PUBLIC-RELEASE-P0-1](../tasks/PUBLIC-RELEASE-P0-1.md)（`in_review`，等待 Reviewer 复核修复后收口）
- Owner：dsh-lead；Reviewer：region-workbench-owner
- 结果：**已真实推送公开 release 分支** `public-release` = `3207e9c18726c62a2692cf7c5d89fb85ea9fabec`（未改远端 main、未 force、未推本地 main 历史）。
- 公开树：`clean-snapshot-20261026` + `apps/desktop-avalonia`（151 文件）+ `packaging/{release,nsis}` + `doc/release` + 根许可四件套 + `README.md` + `.github/workflows/build-release.yml`；1040 文件 / 17,539,433 B（16.73 MiB）。
- 证据：`verification/PUBLIC-RELEASE-P0-1/{push.json,remote-verify.json,security-scan.json,REPORT.md,ls-tree.txt,ls-remote.txt}`（main commit `53481a9d9`，6 项 64-hex pin）。

## 验证证据

- `ls-remote.txt` 原文：`public-release`=`3207e9c18…`；`main`=`6a68fdeb…`（未变）；另两分支未动。
- `ls-tree.txt`：推送 commit 的完整 1040 文件清单（原始 `git ls-tree -r -l`）。
- `security-scan.json`：禁止扩展名 0；密钥模式原始命中 2、均为 `tests/network/test_transport_local.py` 测试 fixture（真实凭据 0）；开发机路径字符串 107 行/41 文件（本次新增 61 行/28 文件，非敏感，登记 follow-up）。
- `remote-verify.json`：raw 9 文件 200；YAML 12 steps；如实记录 CI 未运行（gh 未认证）。
- `check.ps1 -TaskPath` PASS（2 warnings）。

## 接收方式

- 公开分支可直接访问：<https://github.com/peakwheat-pixel/New-Manga/tree/public-release>。
- 内部证据在 main 的 `verification/PUBLIC-RELEASE-P0-1/`；worktree 与 main 无共同祖先，**不要 merge 其快照历史**（证据已复制入 main）。

## 下一任务建议（必填）

1. **用户两步**（阻塞 CI 验证）：
   - GitHub → Settings → Branches → Default branch 改为 `public-release`（可逆）；
   - Actions → `build-release` → Run workflow（`version=0.1.0`、`sign=false`）；失败则把日志贴回，不伪造通过。
2. 两步完成后：由 DSH 复验并更新本卡（AC4 完成、收口），随后可提交 SignPath Foundation 申请（材料已就绪，替换占位符）。
3. 可选 follow-up：清理公开树中的开发机路径字符串（107 行/41 文件；本卡范围外，需单独 Task 冻结范围后处理）。

## 风险与遗留

- 公开推送不可逆（分支可删但对象可能保留）；已做 P0-5 扫描，无真实凭据/模型/私有文件。
- `gh` 未认证、无 `GH_TOKEN`：默认分支切换、workflow Run、Actions 日志读取均需用户完成。
- 首次 CI Run 可能因 runner 与本地差异失败（pytest fixture/NSIS 安装等），属预期迭代。
- 公开树含开发机路径字符串（非敏感）与测试假凭据 fixture，可能触发 secret-scanning 噪音，已在证据中登记。
- `public-release` 历史 = 公开快照 + 本次提交（2 commits），不含内部 main 历史。
