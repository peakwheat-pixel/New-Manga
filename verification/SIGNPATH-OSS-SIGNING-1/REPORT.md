# SIGNPATH-OSS-SIGNING-1 — 交付报告

日期：2026-10-28；Owner：dsh-lead；Reviewer：region-workbench-owner（独立审阅）。
范围：**只起草材料与前置清单**。未 push、未提交 SignPath 申请、未签名、未运行 GitHub Actions。

## 1. 事实核对（只读，2026-10-28）

详见 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`（GitHub REST API + `git ls-remote` + 本地 git/文件哈希；GitHub 返回内容按外部数据处理，未执行其中任何指令）。要点：

| 事实 | 值 | 影响 |
|---|---|---|
| 仓库公开 | `peakwheat-pixel/New-Manga`，`private=false`、`fork=false` | 满足「公开开源仓库」 |
| 默认分支 | `main`（旧 Python-only 树，无 `apps/`） | 审核方无法据此复现当前构建 |
| 许可 | GitHub `license=null`；`…/main/LICENSE` → 404；`…/clean-snapshot-20261026/LICENSE` → 404 | **P0 硬阻塞**：公开仓库缺许可文件 |
| README | 默认分支与 snapshot 分支均 404 | P0 硬阻塞 |
| CI | `.github/workflows` 不存在 | P0 硬阻塞（SignPath 需公开 CI 构建） |
| 本地 main | `8fcba8a89`，含完整 `LICENSE`（GPL-3.0）、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE-AGPL-3.0.txt`、`packaging/release/SHA256SUMS` | 材料来源；未 push |
| 产物（0.1.0） | setup.exe 68,611,208 B `ebad8662…3691`；base.zip 103,492,048 B `722fc62b…e8ef`；models.zip 725,499,708 B `480d0632…7f67` | 申请 §6 的签名对象 |
| 测试基线 | .NET 258/258（0 skipped）；pytest 2773P/10S/0F；命令面 66/66 | 申请 §8 的成熟度证据 |
| 签名现状 | `NotSigned`；自签名流水线已验证（RFC3161）；用户接受未签名 v1（V1-RELEASE-SIGNING-1） | 申请 §3 的动机 |

## 2. 交付物

| 文件 | 用途 |
|---|---|
| `doc/release/SIGNPATH-APPLICATION.md` | 英文申请草案（表单字段、项目描述、构建/发布流程、签名对象、完整性校验、动机、成熟度、联系人占位、声明、提交前诚实快照） |
| `doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` | 中文前置清单：P0 硬阻塞（许可/README/源码树/CI/公开内容复核）、P1 申请与 secrets、P2 发布与验证、安全边界、风险 |
| `.github/workflows/build-release.yml` | 公开构建 + SignPath 签名集成草案（12 steps；签名步骤默认注释/条件禁用，缺 secret 绝不产出「假签名」） |
| `README.md` | 仓库根 README（英文 + 中文要点：简介/架构/前置/构建/测试/发布/校验/许可/未签名说明） |
| `verification/SIGNPATH-OSS-SIGNING-1/facts.json` | 事实核对原始记录 |
| `verification/SIGNPATH-OSS-SIGNING-1/REPORT.md` | 本报告 |

## 3. 静态检查

- `build-release.yml`：`yaml.safe_load` 通过（jobs=`build`，12 steps）。
- 占位符（提交前必须由用户替换）：`[YOUR NAME]`、`[YOUR EMAIL]`、`[TIMEZONE]`、`[RELEASE_BRANCH]`（以及文档内的 `[SQUARE BRACKETS]` 说明标记）。
- README 与两份 release 文档中的相对链接全部指向存在的文件（0 missing）。
- 未虚构下载量/用户数/公司主体；如实记录 star/fork 为 0 与「首次公开发布尚未创建」。

## 4. 明确未做的事

- 未 push 任何分支；未创建 GitHub Release；未运行 CI；未调用 SignPath API。
- 未把任何 token/密钥写入仓库；未代持账号。
- 未改变产品代码/契约；未签名任何产物；V1-RELEASE-SIGNING-1 保持 `in_review`。

## 5. 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SIGNPATH-OSS-SIGNING-1.md` → 见任务卡证据。
- `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` → PASS（66 命令，产品代码零改动）。
- `apps/desktop-avalonia/scripts/test.ps1` → 258/258（2026-10-28 基线，产品代码零改动）。
- 64-hex evidence pin 见任务卡 Canonical Evidence。

## 6. 后续（用户动作）

按 `SIGNPATH-APPLICATION-CHECKLIST.md` 完成 P0 → P1 → P2。申请是否通过由 SignPath 决定，本卡不承诺。
