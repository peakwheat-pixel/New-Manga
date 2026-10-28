# SignPath 免费 OSS 签名：申请前置清单（中文操作指引）

> 配套：[SIGNPATH-APPLICATION.md](SIGNPATH-APPLICATION.md)（英文申请草案，提交前替换所有 `[方括号]` 占位符）。
> 本清单只列**你（仓库所有者）**必须亲自完成的动作；Agent 不代持账号、token、密钥，也不代提交申请。
> 事实依据：`verification/SIGNPATH-OSS-SIGNING-1/facts.json`（2026-10-28 只读核对）。

## 0. 一句话结论

免费签名可以申请，但**当前公开仓库还不满足审核前提**：默认分支 `main` 与 `clean-snapshot-20261026`
分支都**没有 LICENSE、没有 README、没有 CI**。补齐这三样（全部零成本）后再提交申请，通过率最高。

## P0 — 提交申请前必须完成（硬阻塞）

| # | 动作 | 为什么必须 | 完成判据 |
|---|---|---|---|
| P0-1 | 在**公开默认分支**根目录加入 `LICENSE`（GPL-3.0 全文）、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md` | GitHub 当前 `license=null`；SignPath 需要可验证的开源许可 | `https://raw.githubusercontent.com/peakwheat-pixel/New-Manga/main/LICENSE` 返回 200，GitHub 仓库页显示 GPL-3.0 |
| P0-2 | 在默认分支加入 `README.md`（可用本仓库根目录草案：项目简介、技术栈、构建/测试/发布步骤、许可、未签名说明） | 审核人需要看懂项目与构建方式；发布页也需要 | `…/main/README.md` 返回 200，内容含构建与发布命令 |
| P0-3 | 把**当前产品源码树**推到公开仓库默认分支（或明确的 release 分支并告知审核方） | 默认分支现在是旧 Python-only 树，无 `apps/`、无打包脚本，审核方无法复现构建 | `…/main/apps/desktop-avalonia/scripts/package.ps1` 存在；或申请中明确 `[RELEASE_BRANCH]` |
| P0-4 | 加入 `.github/workflows/build-release.yml`（本仓库草案）并**手动 Run 一次**（签名输入保持 false） | SignPath 要求构建在公开 CI 中完成、按产物提交签名请求 | Actions 页出现该 workflow，手动运行通过（构建/上传产物成功；签名步骤被 `sign=false` 跳过） |
| P0-5 | 复核公开内容不含私有素材/模型权重/密钥/历史敏感材料 | 公开仓库是申请与签名构建的基础；泄露不修复会直接导致拒绝 | `git ls-files` 无 `.onnx`/`.pfx`/`.env`/密钥；仓库体积与文件清单复核通过 |

> 注意 1：`clean-snapshot-20261026` 分支根目录也没有 LICENSE（`…/clean-snapshot-20261026/LICENSE` → 404），
> 因此**不能直接拿该分支当审核对象**；先补齐许可文件再推，或把许可文件补进该分支。
> 注意 2：公开 CI 构建需 `pip install -r requirements.txt -r requirements-dev.txt`（PyInstaller/pytest 在
> dev 依赖里），sidecar 用 `-PythonExe python -SkipWeights`（不公开模型权重）；workflow 草案已按此编写，
> 清单在其内部生成 base-only 版本，完整三产物清单仍由维护者本机发布流程生成。

## P1 — 申请与集成（你本人操作，约 30–60 分钟）

1. **注册 / 申请**：在 <https://signpath.io> 注册账号；进入 SignPath Foundation 申请表单
   （开源项目免费），把 [SIGNPATH-APPLICATION.md](SIGNPATH-APPLICATION.md) 第 1、2、3、9、10 节内容
   对应填入；替换全部 `[YOUR NAME]` / `[YOUR EMAIL]` / `[TIMEZONE]` / `[RELEASE_BRANCH]`。
2. **等待审核**：SignPath 审核开源资质（公开仓库、许可证、构建可复现）。**不保证通过**，通常需要补充材料。
3. **拿到凭据后**（审核通过才有）：SignPath 会给出 organization id、project slug、signing policy slug，
   并在 GitHub 安装 SignPath GitHub App；把这些值填入仓库 **Actions secrets**（不是提交进仓库）：
   `SIGNPATH_API_TOKEN`、`SIGNPATH_ORGANIZATION_ID`、`SIGNPATH_PROJECT_SLUG`、`SIGNPATH_SIGNING_POLICY_SLUG`。
4. **启用签名**：在 Actions 页手动 Run `build-release`，把 `sign` 输入设为 true（workflow 用输入而非
   `secrets` 判断是否执行签名步骤——GitHub Actions 的 `secrets` 不能用于 `if:`），或按需启用 tag 触发
   （workflow 里已注释，确认后再打开）。
5. 触发一次签名构建 → 签名 installer 作为 artifact 产出 → 创建 GitHub Release。

## P2 — 发布与验证（签名跑通后）

1. 创建 GitHub Release：`NewManga-0.1.0-setup.exe`（signed）+ `SHA256SUMS` + 发行说明
   （`apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`）。
2. 本机验证签名：`Get-AuthenticodeSignature .\NewManga-0.1.0-setup.exe` → `Status = Valid`，
   `SignerCertificate.Subject` 含 SignPath/证书主体，`TimeStamperCertificate` 存在。
3. 干净 Windows 机器复验：SmartScreen 不再拦截（或显示可信发布者）；安装/卸载与
   `%APPDATA%\com.newmanga.desktop` 数据根保留行为不变。
4. 更新 [V1-RELEASE-SIGNING-1](../tasks/V1-RELEASE-SIGNING-1.md) 与发行说明中的「未签名」表述。

## 安全边界（必须遵守）

- **不要把** SignPath token、私钥、证书文件写入仓库、日志、截图或 Handoff；只放 GitHub Actions secrets。
- 不要为了通过审核而把模型权重（725MB）或第三方版权素材推上公开仓库；模型走独立下载/发布附件。
- 申请材料中不要虚构用户数、下载量、公司主体；按事实填写。

## 时间与风险

- 前置整改（P0）：约 1–2 小时（主要是把干净源码与许可文件推到公开默认分支并跑通一次 CI）。
- 审核：数天到数周，取决于 SignPath 队列；可能有补充材料往返。
- 失败风险：项目太早/活动量低可能被拒（本仓库 star/fork 均为 0，公开 release 尚未发布）；若被拒，
  继续用现有 SHA-256 校验 + SmartScreen 指引发布，等下一个版本再申请。
