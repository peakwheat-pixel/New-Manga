# Handoff — PUBLIC-RELEASE-P0-1

## 交付结果

- Task：[PUBLIC-RELEASE-P0-1](../tasks/PUBLIC-RELEASE-P0-1.md)（`done`，集成 `cd58c50fe`）
- Owner：dsh-lead；Reviewer：region-workbench-owner（独立复核 PASS）
- 结果：**P0 全部完成**（含此前标记为 PARTIAL 的 AC4）：
  - 公开分支 `public-release` 推送并迭代至 `d3dd911c4`（初推 `3207e9c18`）；
  - GitHub 默认分支已切换为 `public-release`，GitHub license 徽标 = **GPL-3.0**；
  - 首次完整 CI run **`40689279237`** 全绿（13 个真实步骤 + 4 个 post 步骤全部 success，`sign=false`）；
  - 远端 `main` 始终未变（`6a68fdeb…`），未 force、未推本地 main 历史。
- 公开树：`clean-snapshot-20261026` + `apps/desktop-avalonia`（151 文件）+ `packaging/{release,nsis}` + `doc/release` + 根许可四件套 + `README.md` + `.github/workflows/build-release.yml`；1040 文件 / 16.73 MiB。

## 验证证据

- `verification/PUBLIC-RELEASE-P0-1/ci-run-success.json`：CI run 元数据与 17 个步骤结论。
- `verification/PUBLIC-RELEASE-P0-1/REPORT.md` §7：默认分支切换事实 + 6 次 run 迭代（5 次失败原因与修复、第 6 次全绿）。
- `ls-tree.txt` / `ls-remote.txt` / `push.json` / `security-scan.json` / `remote-verify.json`。
- `check.ps1 -TaskPath` PASS（2 warnings）。

## 接收方式

- 公开分支：<https://github.com/peakwheat-pixel/New-Manga/tree/public-release>（默认分支）。
- CI 历史：<https://github.com/peakwheat-pixel/New-Manga/actions>。
- 内部证据在 main 的 `verification/PUBLIC-RELEASE-P0-1/`；两个 worktree 保留，不导入快照历史。

## 下一任务建议（必填）

1. **用户动作**：现在可提交 SignPath Foundation 免费 OSS 签名申请 —— 材料已就绪：
   - 填写 `doc/release/SIGNPATH-APPLICATION.md`（替换 `[YOUR NAME]`/`[YOUR EMAIL]`/`[TIMEZONE]`/`[RELEASE_BRANCH]`=public-release）；
   - 申请前置已满足：公开默认分支有 LICENSE/README/产品树、CI 可跑、license=GPL-3.0；P0-4 的「公开构建可复现」已由 run `40689279237` 证明。
2. **可选 follow-up（非阻塞）**：清理公开树中 107 行开发机路径字符串（`apps/desktop-avalonia/scripts/*` 默认值）与公开文档内链；建独立 Task 冻结范围后处理。
3. 审核通过后：由 DSH 释放签名实施 Task（配置 4 个 Actions secrets → `sign=true` → 验证 Authenticode → 发布 signed installer），并收口 `V1-RELEASE-SIGNING-1`。

## 风险与遗留

- 公开 CI 产物体积大于维护者发布包（CI base zip 550 MB 含完整 release 栈 vs 发布包 103 MB trimmed）——已在 workflow 注释与申请材料中说明。
- `public-release` 历史 = 公开快照 + 6 个 CI 修复提交，不含内部 main 历史。
- 公开树含开发机路径字符串（非敏感）与测试假凭据 fixture（可能触发 secret-scanning 噪音，已登记）。
- 默认分支切换与 CI 操作使用本机 GCM 凭据经 GitHub API 完成；token 仅在内存使用，未落盘、未写入证据。

## 后续：SignPath 申请已提交（2026-10-29）

- 资格补齐：README **Code signing policy** 节 + **PRIVACY.md**（public-release `9501e33e8`）；GitHub Release **`v0.1.0`**（unsigned installer + SHA256SUMS，body 声明 SignPath Foundation 签名）。
- **申请已提交**：<https://signpath.org/apply>（用户授权，DSH 通过浏览器代填）；成功页 “Form submitted — Thank you, we'll be in touch soon.”；证据 `verification/PUBLIC-RELEASE-P0-1/{signpath-submission.json,screenshots/signpath-form-submitted.png}`。
- **2026-10-29 10:54 收到确认邮件**（oss-support@signpath.org，“Open Source Project Submitted”）：申请已收到，接下来几个工作日内回复后续步骤/补充问题；证据 `signpath-application-ack.json` + `screenshots/signpath-application-received-email.png`。状态：**等待审核**。
- 等待审核结果（可能要求补充材料）。通过后：安装 SignPath GitHub App → 创建 project/artifact configuration/signing policy → 配置 Actions secrets → `sign=true` 触发签名 → 验证 Authenticode → 收口 V1-RELEASE-SIGNING-1。
