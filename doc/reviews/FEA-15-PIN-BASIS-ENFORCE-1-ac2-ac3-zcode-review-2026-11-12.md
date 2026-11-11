---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
reviewer: ZCode CLI `0.17.1`, session `sess_6b151e7e-8133-4b6a-ae6f-3c47296e5b7a`, turns `turn_f7833d05-4c82-435e-bf53-7107ffc59c82` and `turn_ade3c4aa-3c7f-426a-85ac-060dcf566544`
reviewer_kind: agent
author: Codex implementation agent; report transcribed from ZCode response
base_commit: bfae0b9bd6a9b85a9a546d2adda0b684783ddb24
reviewed_head: 5e216dc53102ff93db39124b97ab85d88f18643b
decision: approved
---

# Review：FEA-15-PIN-BASIS-ENFORCE-1 AC2/AC3

## 范围与依据

这是 AC2/AC3 的独立只读 Review，审查范围固定为 R0 `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24` 到实现分支 `codex/fea-15-pin-basis-enforce-1` HEAD `5e216dc53102ff93db39124b97ab85d88f18643b` 的 diff。实现文件仅 4 个，均在已释放范围内：

- `doc/templates/TASK.md`
- `tools/governance/check.ps1`
- `tools/governance/tests/test_architecture_assertions.py`
- `tools/governance/tests/test_canonical_evidence_basis.py`

ZCode 首轮结论为 **`APPROVED_WITH_LIMITATIONS`**，无 P0/P1 代码发现。审查者是全新 ZCode CLI 会话，未参与实现或返修；同一审查会话随后提交了 P3-6 事实复核 Addendum。审查期间未改文件、未提交、未 push。ZCode 无法直接执行实现 worktree 的 `git status`；Codex 在审查前后均核验该 worktree clean，验证日志也记录 clean 状态。

审查覆盖 Architecture 与 Verification：原始 Git blob 字节读取、旧六列表 r194 双通道兼容、新七列表严格 basis 校验、错误 fail-closed、模板说明、测试隔离以及范围纪律。Standards/Spec 未作为独立双轴报告。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | `tools/governance/check.ps1:732,742,748-751,757-761,771,778` | 新七列表的行列数、64 位 SHA、无效 BLOB commit，以及 basis 与仓库内外路径方向错误等分支缺少直接负例测试；实现当前逐项检查为 fail-closed，但后续重构可能弱化这些边界而不被专项测试发现。 | `test_canonical_evidence_basis.py` 已覆盖 AC3 明确列出的 basis、来源、缺失路径、PNG、EOL 和旧格式要求；未覆盖本 finding 列出的全部额外反例。 | 在 AC4/AC5 前或集成返修时补充测试。 | `deferred`；不阻塞本次 AC2/AC3 Review，待 Integrator/ZCode 处置 |
| R-002 | P3 | `tools/governance/check.ps1:54-83` | `Get-GitBlobSha256` 先同步读 stdout 到 EOF、再读 stderr，且 `WaitForExit` 无超时；若 stderr 管道缓冲被填满，理论上可能死锁；Git 当前错误输出很小，未观察到实际风险。 | 代码路径检查；无复现。 | 可并行读取 stderr 或增加超时。 | `informational` |
| R-003 | P3 | `tools/governance/check.ps1:61` | `Get-GitBlobSha256` 隐式引用脚本作用域 `$repoRoot`，与显式接收 `$RepoRoot` 的路径 helper 风格不一致；现有调用点在变量初始化后，当前功能正常。 | 代码路径检查；无复现。 | 后续重构时考虑显式传参。 | `informational` |
| R-004 | P3 | `tools/governance/check.ps1:771-782` | WORKTREE/EXTERNAL 的仓内外判断基于词法路径，不检查符号链接最终目标；符号链接可能让实际读取对象跨越声明的仓内外边界。 | 代码路径检查；无复现。 | 可仿照 Resource Manifest 检查拒绝符号链接。 | `informational` |
| R-005 | P3 | `tools/governance/check.ps1:766-776` | WORKTREE basis 不校验 `commit` 列；该列不参与 WORKTREE 哈希，但任意值可能使读者误以为已验证 commit。 | 代码路径检查；无复现。 | 可要求该列为空或使用明确占位。 | `informational` |
| R-006 | P3 | `tools/governance/check.ps1:723-729` | Canonical Evidence section 缺失或无行时，会同时出现 `EVIDENCE_BASIS_HEADER_INVALID` 与 evidence 必填错误；错误数增加且首条文案略有误导，但拒绝方向正确。 | 代码路径检查；无复现。 | 可只在发现表格内容时报告 header 错误。 | `informational` |
| R-007 | P3 | `verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md:42`（main `29f24d5`） | README 中实现提交 hash 少最后一位 `c`；40 位真实值为 `fd84360219fddf1e0b7611c1da1a088d5635593c`。 | `git rev-parse` 与 README 对照。 | 修正记录。 | `fixed`，main `06432c1fb94b7fe8a81c575a27076868a448a074` |

## P3-6 Reviewer Addendum：旧 PowerShell 重定向结论撤回

ZCode 同一 Review session 在 2026-11-12 复核并**撤回**首轮报告中的 P3-6。首轮声称旧表达式 `git cat-file blob ... > $tmp` 会把二进制 stdout 解码为字符串并重加 CRLF；这是 Windows PowerShell 5.1 / `pwsh <= 7.3` 的行为，不适用于本项目日志记录的 PowerShell `7.6.9`。Microsoft Learn 对 PowerShell 7.4+ 明确说明 native stdout 重定向到文件保留 byte stream，且不解释或格式化字节；`2>$null` 单独丢弃 stderr，不会合并 stdout/stderr。

来源：[Microsoft Learn — about_Redirection](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_Redirection)。

因此，“r194 在目标运行时损坏二进制 blob 哈希”“新实现修复了该错误”及“旧实现二进制 basis 语义发生变化”等首轮表述全部撤回。PowerShell 7.4+ 下，r194 的临时文件重定向和新 `BaseStream` 读取对同一 Git blob 的字节口径相同；新实现的差别是直接读取 blob、去掉临时文件 I/O/清理依赖，并减少对重定向版本行为的依赖。Reviewer 明确披露未在 7.6.9 上构造旧表达式的本地二进制对照；错误源于未经运行时核实将旧行为外推。撤回后仍为 1 项 P2 + 6 项有效 P3，结论仍为 `APPROVED_WITH_LIMITATIONS`。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| basis 专项（EOL 有差异） | `python -m pytest tools/governance/tests/test_canonical_evidence_basis.py -q` | implementation HEAD `5e216dc…`；Windows；`core.autocrlf=true` | 13 passed，2 subtests passed；`EXIT=0` | `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac2ac3-basis-focused-autocrlf-true.log` |
| basis 专项（EOL 相同） | 同上 | validation HEAD `a2a3401eb703c3ae7899375755c981eabbf47572`；Windows；`core.autocrlf=false` | 11 passed，2 skipped，2 subtests passed；`EXIT=0`；EOL 相同导致差异用例 skip | `ac2ac3-basis-focused-final.log` |
| Architecture checker fixtures | `python -m pytest tools/governance/tests/test_architecture_assertions.py -q` | validation HEAD `a2a3401…`；Windows；`core.autocrlf=false` | 31 passed，43 subtests passed；`EXIT=0` | `ac2ac3-architecture-tests.log` |
| 全治理测试 | `python -m pytest tools/governance/tests -q` | validation HEAD `a2a3401…`；Windows；`core.autocrlf=false` | 56 passed，2 skipped，3 failed，55 subtests passed；`EXIT=1` | `ac2ac3-full-pytest-final.log` |
| default / 当前 TaskPath / pins / API | `check.ps1`；`check.ps1 -TaskPath doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`；`verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | validation HEAD `a2a3401…`；Windows；`core.autocrlf=false` | default/TaskPath 各 `EXIT=0`（各 3 warnings）；pins `EXIT=1`（C04b/C17）；API `EXIT=0`，1/79/6=86 | `ac2ac3-candidate-gates.log` |
| 基线对照 | residual tests 与 `verify_pins.ps1`；main true checkout pins | 未变更 main HEAD `dd6372420a459cdc9a4c39377f663f1b5d0d8646` | false checkout 下同 3 个 residual failures、同 C04b/C17 mismatch；main `core.autocrlf=true` 为 18/18、`EXIT=0` | `ac2ac3-baseline-controls.log` |
| 源码叠加一致性 | 比较四个实现/测试文件 Git blob IDs | implementation `5e216dc…` / validation `a2a3401…` | 4/4 identical；`EXIT=0` | `ac2ac3-source-overlay-audit.log` |

全套测试的 3 个 `test_residual_runtime_identity.py` 失败与 false-checkout 的两个 pin mismatch，均在未变更基线同配置复现；属于已记录的 baseline limitation，不能写作 PASS。本实现没有修改 `clean_workspace.py`、历史 Task、18 个 frozen pins 或 `.gitattributes`。

## AC2/AC3 判定

- **AC2：PASS（限已释放范围）**。模板七列表默认 BLOB 说明清楚；checker 区分 legacy 六列与新七列；旧六列保留 r194 语义；新 basis 校验按声明来源执行并失败闭合。
- **AC3：PASS（限已释放范围）**。Task AC3 明确列出的旧格式、basis、三类来源、commit 路径、缺失路径、PNG exact bytes、CRLF/mixed-EOL 与兼容性断言均有专项覆盖。R-001 是超出 AC3 字面清单的补充负例建议。
- **AC4 / AC5：NOT_RUN、未释放**。跨 checkout 矩阵、集成后四个历史 TaskPath、集成门禁、Task 终裁与 `R-001` 最终处置均未完成。本 Review 不使 Task 进入 `done`、不批准集成，也不构成 AC5 终裁。

## 推荐下一步

保存本 Review 并记录精确 pin；由独立 ZCode adjudication session 处置 R-001 与非阻塞观察。若 AC2/AC3 被接受，下一步须先明确释放 AC4，再按卡片执行 Windows `core.autocrlf=true/false` 跨 checkout 对照；AC4 完成后另行进入 AC5 集成与最终 adjudication。
