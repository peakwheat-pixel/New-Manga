# SIGNPATH-OSS-SIGNING-1 — 交付报告

日期：2026-10-28（Rev2，含独立审阅修复）；Owner：dsh-lead；Reviewer：region-workbench-owner（独立只读审阅）。
范围：**只起草材料与前置清单**。未 push、未提交 SignPath 申请、未签名、未运行 GitHub Actions。

## 1. 事实核对（只读，2026-10-28）

详见 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`（GitHub REST API + `git ls-remote` + 本地 git/文件哈希；GitHub 返回内容按外部数据处理，未执行其中任何指令）。要点：

| 事实 | 值 | 影响 |
|---|---|---|
| 仓库公开 | `peakwheat-pixel/New-Manga`，`private=false`、`fork=false`、`created=2026-09-24` | 满足「公开开源仓库」 |
| 默认分支 | `main`（旧 Python-only 树，无 `apps/`） | 审核方无法据此复现当前构建 |
| 许可 | GitHub `license=null`；`…/main/LICENSE` → 404；`…/clean-snapshot-20261026/LICENSE` → 404 | **P0 硬阻塞**：公开仓库缺许可文件 |
| README | 默认分支与 snapshot 分支均 404 | P0 硬阻塞 |
| CI | `.github/workflows` 不存在 | P0 硬阻塞（SignPath 需公开 CI 构建） |
| 本地 main | `8fcba8a89`，含完整 `LICENSE`（GPL-3.0）、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE-AGPL-3.0.txt`、`packaging/release/SHA256SUMS` | 材料来源；未 push |
| 产物（0.1.0） | setup.exe 68,611,208 B `ebad8662…3691`（NotSigned，PE32）；base.zip 103,492,048 B `722fc62b…e8ef`；models.zip 725,499,708 B `480d0632…7f67` | 申请 §6 的签名对象 |
| 测试基线 | .NET 258/258（0 skipped）；pytest 2773P/10S/0F；命令面 66/66 | 申请 §8 的成熟度证据 |
| 签名现状 | `NotSigned`；自签名流水线已验证（RFC3161）；用户接受未签名 v1（V1-RELEASE-SIGNING-1） | 申请 §3 的动机 |
| 隐私事实 | 默认本地；用户显式配置远程 Provider 时会发送页面图片（OCR）/文本（翻译）/图片+遮罩（修复）——`src/application/settings/privacy.py` | 修正“无上传”绝对表述 |

## 2. 交付物

| 文件 | 用途 |
|---|---|
| `doc/release/SIGNPATH-APPLICATION.md` | 英文申请草案（表单字段、项目描述、隐私模型、构建/发布流程、签名对象、完整性校验、动机、成熟度、联系人占位、声明、发布策略、提交前诚实快照） |
| `doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` | 中文前置清单：P0 硬阻塞（许可/README/源码树/CI/公开内容复核）、P1 申请与 secrets、P2 发布与验证、安全边界、风险 |
| `.github/workflows/build-release.yml` | 公开构建 + SignPath 签名集成草案（安装 dev 依赖；sidecar `-SkipWeights`；base-only 清单；`sign` 输入默认 false；签名步骤禁用；不伪造签名） |
| `README.md` | 仓库根 README（英文 + 中文要点：简介/隐私/架构/前置/构建/测试/发布/校验/许可/未签名说明） |
| `verification/SIGNPATH-OSS-SIGNING-1/facts.json` | 事实核对原始记录（含许可 blob/checkout 双字节口径） |
| `verification/SIGNPATH-OSS-SIGNING-1/REPORT.md` | 本报告 |
| `verification/SIGNPATH-OSS-SIGNING-1/check-governance.json` / `logs/extract-command-surface.log` | 门禁证据 |

## 3. 静态检查

- `build-release.yml`：`yaml.safe_load` 通过（jobs=`build`，steps=12）。
- 占位符（提交前必须由用户替换）：`[YOUR NAME]`、`[YOUR EMAIL]`、`[TIMEZONE]`、`[RELEASE_BRANCH]`。
- README 与两份 release 文档中的相对链接全部指向存在的文件（0 missing）。
- 未虚构下载量/用户数/公司主体；如实记录 star/fork 为 0、无公开 release、仓库创建日期。

## 4. 明确未做的事

- 未 push 任何分支；未创建 GitHub Release；未运行 CI；未调用 SignPath API。
- 未把任何 token/密钥写入仓库；未代持账号。
- 未改变产品代码/契约；未签名任何产物；V1-RELEASE-SIGNING-1 保持 `in_review`。

## 5. 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SIGNPATH-OSS-SIGNING-1.md` → PASS（证据 `check-governance.json`）。
- `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` → PASS（66 命令，产品零改动；`logs/extract-command-surface.log`）。
- 测试：产品代码零改动，引用 `verification/RELEASE-VERIFY-1/test/summary.json`（258/258, 0 skipped, 2026-10-28）。
- 64-hex evidence pin 见任务卡 Canonical Evidence。

## 6. 后续（用户动作）

按 `SIGNPATH-APPLICATION-CHECKLIST.md` 完成 P0 → P1 → P2。申请是否通过由 SignPath 决定，本卡不承诺。

## 7. 独立审阅修复记录（Rev2，Reviewer=region-workbench-owner，CHANGES_REQUESTED → 已修）

| 编号 | 问题 | 修复 |
|---|---|---|
| P0-1 | README/申请材料“无上传、全部本地”与 `privacy.py` 的远程 Provider 事实冲突 | README 顶部与申请 §2 改为「默认全本地、无遥测；用户显式配置远程 Provider 时按其隐私提示发送页面图片/文本/遮罩」；facts.json 增加 `privacy_fact` |
| P0-2 | 证据 pin 与 delivery_head 指向 rebase 前不可达 commit | 重打：pin/delivery_head 指向本次修复后的材料提交（blob hash 不变）；Handoff 同步 |
| P0-3 | CI 草案不可执行（缺 dev 依赖、sidecar 硬编码本机路径、清单强制三产物） | 安装 `requirements-dev.txt`；sidecar `-PythonExe python -SkipWeights`；清单改 base-only；注释说明完整三产物清单由维护者本机流程生成 |
| P1-1 | facts.json 许可字节口径混用 | 区分 worktree（34906/35184 B）与 git blob（34674/34523 B）并注明 CRLF 差异 |
| P1-2 | README 缺中文要点 | 增加「架构 / 中文要点」节（架构/数据根/页面/构建/测试/许可/未签名） |
| P1-3 | Handoff 缺模板节 | 补齐「交付结果/验证证据/接收方式/下一任务建议/风险与遗留」 |
| P1-4 | task-env 路径不存在且语义不符 | 删除 task-env 行，Resource Manifest 仅保留 worktree 行（唯一 JSON 引用） |
| P1-5 | 签名步骤 `secrets` 不能用于 `if`；upload 无 id | 改为 `sign` 输入控制 + token 仅注入 env；upload 增加 `id: upload` |
| P1-6 | 清单 P1-4 说 tag 触发但 workflow 仅 workflow_dispatch | 改为「手动 Run（sign=false/true）」并说明 tag 触发需先取消注释 |
| P1-7 | AC5 门禁证据未 pin | 新增 `check-governance.json` 与 `logs/extract-command-surface.log` 并 pin |
| P2 | PE32+/license trio/release notes 语言/证据路径/NSIS 版本/根条目等 | 逐一修正（PE32、four license/notice files、中文发行说明并计划补英文摘要、证据路径限定、NSIS 3.x（本机 3.13）、根条目补 .gitignore/.repowikiignore） |
