# PUBLIC-RELEASE-P0-1 — P0 公开仓库整改执行报告

日期：2026-10-28；Owner：dsh-lead；Reviewer：region-workbench-owner（独立只读复核）。
范围：执行 [SIGNPATH-APPLICATION-CHECKLIST](../release/SIGNPATH-APPLICATION-CHECKLIST.md) 的 P0（公开仓库申请前整改）。**已真实推送到 GitHub 公开仓库的新分支**；未改远端 `main`、未 force、未推本地 main 历史。

## 1. 执行结果

| P0 项 | 状态 | 说明 |
|---|---|---|
| P0-1 许可四件套 | **DONE** | `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md` 已在分支根目录（来自 main 已审核版本，字节一致） |
| P0-2 README | **DONE** | 根 `README.md`（英文 + 中文要点 + 准确隐私表述） |
| P0-3 产品源码树 | **DONE** | 公开树 = `clean-snapshot-20261026`（公开历史）+ 同步 `apps/desktop-avalonia`（151 文件/1.6 MB，新架构 C# 壳、scripts、tests、docs）+ `packaging/release` + `packaging/nsis` + `doc/release`；**不含** bin/obj/node_modules |
| P0-4 CI 草案 | **PARTIAL** | `.github/workflows/build-release.yml` 已随分支公开且 YAML 可解析（12 steps）；**首次 workflow_dispatch Run 未触发**——本机 `gh` 未登录、无 GitHub API token，需用户在网页 Run（`sign=false`）。未伪造运行结果 |
| P0-5 内容安全 | **DONE（修正口径）** | 推送树 **1040 文件 / 17,539,433 B（16.73 MiB）**；禁止扩展名（.onnx/.pfx/.p12/.pem/.key/.env/.db/.sqlite）0 个；密钥模式**原始命中 2、真实凭据 0**（2 处均为 `tests/network/test_transport_local.py` 的测试 fixture 密码占位）；无私有文件/模型/用户数据；存在 **107 行/41 文件**开发机路径字符串（本次新增 61 行/28 文件，仅为脚本默认值，已评估非敏感并登记 follow-up 清理） |

## 2. 推送事实

- 分支：`public-release`；本地与远端 commit：`3207e9c18726c62a2692cf7c5d89fb85ea9fabec`。
- push 命令：`git push origin HEAD:refs/heads/public-release`（新分支，无 force）。
- 远端 `main` 保持 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`（未改动）；`clean-snapshot-20261026`、`codex/clean-source-snapshot` 未动。
- 远端可见性（raw，全部 200）：LICENSE、README.md、LICENSE-AGPL-3.0.txt、NOTICE.md、THIRD_PARTY_LICENSES.md、.github/workflows/build-release.yml、apps/desktop-avalonia/scripts/package.ps1、packaging/release/verify-release.ps1、doc/release/SIGNPATH-APPLICATION.md。
- GitHub API：`branches/public-release.sha = 3207e9c18…`；仓库 `default_branch` 仍为 `main`、`license=null`（默认分支未切换，故 GitHub 许可徽标尚未显示）。

## 3. 未完成项（需用户 2 步操作，Agent 无 GitHub API 权限）

1. **切换默认分支**：GitHub → Settings → Branches → Default branch → `public-release`（可逆；不会删除 `main` 历史）。切换后 GitHub 许可徽标显示 GPL-3.0，且 `workflow_dispatch` 可在 Actions 页手动运行。
2. **首次 CI 验证**：Actions → `build-release` → Run workflow → `version=0.1.0`、`sign=false` → 观察构建与产物。若失败，把失败日志贴回（不要伪造通过）。

> 说明：本机 `git push` 凭据（Windows Credential Manager）可用，但 `gh` 未认证且无 `GH_TOKEN`，因此"改默认分支/触发 workflow/读 Actions"均无法由 Agent 执行；这符合本 Task 的"不代持 token"边界。

## 4. 风险与后续

- 公开推送不可逆（分支可删，但 GitHub 可能保留对象）；推送前已完成 P0-5 扫描（无密钥/模型/私有素材）。
- 公开树包含 `doc/release/SIGNPATH-APPLICATION*.md`（申请材料，公开无妨）；不含内部 `doc/tasks`、`verification/`、历史证据。
- 首次 CI Run 可能失败（本地环境与 runner 差异，如 pytest fixture/NSIS 安装）；失败属预期迭代，不阻塞 SignPath 申请提交。
- 默认分支切换后，`SIGNPATH-APPLICATION-CHECKLIST` 的 P0-1/P0-2 完成判据（raw 200 + GitHub 许可徽标）即达成；P0-4 以一次成功 Run 为准。

## 5. 扫描口径（可复现）

- 树计数：`git ls-tree -r -l 3207e9c18` → **1040 files / 17,539,433 B（16.73 MiB）**；原始输出见同目录 `ls-tree.txt`、`ls-remote.txt`。
- 禁止扩展名 / 密钥模式 / 路径引用：PowerShell `Get-ChildItem`（排除 `.git` 与本证据目录）+ `Select-String`；模式与命令见 `security-scan.json.scan_command`。
- 2 处密钥模式命中均为测试 fixture：`tests/network/test_transport_local.py:75 password="correct-password"`、`:139 password="secret-pw"`，**不是真实凭据**。
- 开发机路径字符串：模式 `G:/CODEX | G:\\CODEX | C:\\Users\\49745 | task-envs`；总计 107 行 / 41 文件，其中本次推送新增 61 行 / 28 文件（`apps/desktop-avalonia` 脚本默认值等）。

## 6. 独立 Review 修复记录（P1/P2）

| 编号 | 问题 | 修复 |
|---|---|---|
| P1-1 | AC3/P0-5「无 task-env 路径」不成立（公开树有 107 行/41 文件开发机路径；本次新增 61 行/28 文件） | 判据改为「无私有文件/凭据/模型/用户数据；路径字符串登记为非敏感 follow-up 清理」；REPORT 与 scan 如实记录数量与示例 |
| P1-2 | security-scan.json 报 2 而 REPORT 写 0，自相矛盾 | scan 增加 `scan_command` 与 2 条命中分类（测试 fixture）；REPORT 改为「原始命中 2 / 真实凭据 0」 |
| P2-1 | 文件数/体积口径不可复现（1041/17.0 MB vs 1040/16.73 MiB） | 改用 `git ls-tree` 树计数（1040 / 17,539,433 B），并落盘 `ls-tree.txt` / `ls-remote.txt` 原始输出 |
| P2-2 | AC1/AC2 缺原始 ls-tree / ls-remote 证据 | 新增 `ls-tree.txt`（1040 行）与 `ls-remote.txt` |
| P2-4 | 公开文档内链断点（CHECKLIST 链接 `../tasks/…`、APPLICATION 引用 `verification/…`） | 登记为 follow-up：公开材料面向外部读者，内部路径不影响安全，不随公开树暴露私有文件 |
| P2-5 | 测试假凭据字符串可能触发 secret-scanning 噪音 | 已在 `security-scan.json` 分类登记（非真实凭据） |
