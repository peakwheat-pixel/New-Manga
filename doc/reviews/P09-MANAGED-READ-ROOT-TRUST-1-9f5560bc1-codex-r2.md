> **归档注（Lead 2026-10-21）**：本报告实际绑定 head = `9f5560bc1d169e803bb853c94b6c3d2619263f68`（提示词中的 `9f5560bc1c1b...` 为笔误，Codex 已在 findings 中更正）。条件“归档时使用实际 HEAD”已满足；Review 结论 `approved_with_conditions`，无代码层遗留 finding。
---
task: P09-MANAGED-READ-ROOT-TRUST-1-REVIEW-R2
reviewer: Codex
author: dsh-p09-root-trust
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
reviewed_head: 9f5560bc1d169e803bb853c94b6c3d2619263f68
implementation_head: 2a0ff8819
decision: approved_with_conditions
review_mode: read_only
---

## 1. 结论（R-001..R-005）

- **R-001：已修复。** `ManagedRootTrust._open_verified()` 在读取或摘要计算前检查已打开目标句柄，拒绝目录和 reparse point。新增的目录替换测试覆盖 `image_state=="invalid"`、URI 为空及各读取入口拒绝；AC3 记录为 base `FAILED` → current `PASSED`。
- **R-002：已修复。** 新测试覆盖 `_verified_managed_sha256`、`_read_verified_managed` 和经真实 `ExportService` 消费的惰性 provider。AC3 runner 解析实际 pytest 结果并检查退出码；缺失、失败或退出码不符都会导致判定失败。
- **R-003：已修复。** 8 份 suite 日志都有 shell、OS、Python、工作目录、命令头和 `EXIT`。
- **R-004：已修复。** ac1/ac3 的临时快照和 driver 使用 `G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`。
- **R-005：已修复。** `core_assembly` 统一使用 `_root_trust_for()`；`core_service` 收敛错误映射，并统一通过 `_managed_root_trust()` 获取信任对象。

实现和证据一致：Task 的 `delivery_head` 指向 `2a0ff8819dceff0849a2ea783ba202769e18078b`，证据提交为 `d305c584540f2979f149618de2d3947f4abcbf28`。

## 2. Findings

**代码层未发现 R-001..R-005 的遗留问题。**

有一项 Review 锚点差异：用户提供的完整 `reviewed_head` `9f5560bc1c1b57f8323e8ae0b81f7b565e39a475` 不存在于 Git 对象库；目标分支实际 HEAD 是 `9f5560bc1d169e803bb853c94b6c3d2619263f68`。本报告绑定实际 HEAD。条件是记录或归档本 Review 时也使用这个实际提交号。

## 3. AC3 8/8 判定表

提交的 `logs/ac3-discrimination.txt` 显示 base pytest exit=1、current exit=0，两边各观察到 14 条结果。8 个 site 测试均为 base `FAILED`、current `PASSED`；新增的 3 条 R-001/R-002 测试也都是 `FAILED` → `PASSED`。

| Site | 覆盖点 | base | current |
|---|---|---:|---:|
| 1 | `read_original_page` | FAILED | PASSED |
| 2 | `handle_resolve_page_resource` | FAILED | PASSED |
| 3 | `_checked_managed_path` / `_reader_sha256` | FAILED | PASSED |
| 4 | `_is_protected_export_target` | FAILED | PASSED |
| 5 | `image_state` | FAILED | PASSED |
| 6 | `_uri_within` / `image_url` | FAILED | PASSED |
| 7 | `_page_image` | FAILED | PASSED |
| 8 | `resolve_namespace_identity` | FAILED | PASSED |

补充判别项：句柄目录替换、导出 hash、惰性导出 provider 均为 base `FAILED` → current `PASSED`。因此记录中的 **8/8 有判别力**成立。

## 4. 残余风险

- AC5 的 9 条结果与基线一致；其中 `n002-race-probe.py` 在基线和当前都是 `INCONCLUSIVE`。Task 文档已明确说明这一项不代表 SAFE。因此 AC5 支持“未回归”的结论，不代表九项都独立证明安全。
- 设计文档已记录 QML `file://` 交接、Reader 预览发布器按名字重新打开文件的短暂窗口；硬链接叶子身份及配置根父目录可写时的整体 rename/recreate 风险也仍在记录范围内。
- AC2 的 core suite 为 564 passed、1 warning；日志还包含 QML null-property 诊断。基线日志也有同类诊断，suite exit 仍为 0。
- `git diff --check` 仅因证据文件 `ac5-delete-probes/PATH-ADAPTATION.diff` 中的空格行返回非零；没有指向实现或测试源码。

## 5. 运行证据

**本轮没有运行测试**，以遵守“不得修改任何文件”的限制。AC1/AC3/AC5 结论来自提交内现有日志，未由本轮重新执行。

只读核验结果：

- `git status --short`（目标 worktree，检查前后）：**exit 0，输出为空**。
- `git rev-parse HEAD`：**exit 0**，结果为 `9f5560bc1d169e803bb853c94b6c3d2619263f68`。
- `git cat-file -e 9f5560bc1c1b57f8323e8ae0b81f7b565e39a475`：**exit 1**，用户提供的完整 hash 无法解析。
- `git diff --stat b8a1e519703f13af73b320dded117004b4bb189a 9f5560bc1d169e803bb853c94b6c3d2619263f68`：**exit 0**，48 个文件；实现改动仅涉及 3 个指定源文件和 `tests/security` 测试文件，其余为 Task、handoff 与 verification。没有删除项，也没有契约、Schema、ACL 或依赖改动。
- Canonical Evidence 校验：**exit 0**，18/18 行对应的路径存在于 `d305c5845`，且 18/18 SHA-256 与当前 checkout 文件字节相符。仓库 `core.autocrlf=true`；部分 pin 按 CRLF 工作区字节计算，原始 LF blob 的哈希不同，符合协作协议 §4.1 的两种允许口径。
- 日志核验：8/8 suite 日志有执行头和 `EXIT=0`。core 564、storage 87、m2_resource_channel 106、library 63、reading_export 141、export 13、m2_acceptance 37，均与基线记录一致；security 从基线 29 增至 43。相对之前记录的 40，多出的 3 条正是 R-001/R-002 新增测试。
- `git diff --check ...`：**exit 1**，仅报告上述证据 `.diff` 文件中的空格行。
- ac1、ac3、ac5 和各测试套件：**NOT_RUN（本轮）**。

本轮未执行 Git 写命令、push、GC 或 prune，也未修改文件。主仓库已有的未跟踪内容未触碰。

**推荐下一步：**归档 Review 时使用实际 HEAD `9f5560bc1d169e803bb853c94b6c3d2619263f68`，再按协作协议完成 Task 的 Review 生命周期更新；本轮没有更新 Task 或 STATUS。