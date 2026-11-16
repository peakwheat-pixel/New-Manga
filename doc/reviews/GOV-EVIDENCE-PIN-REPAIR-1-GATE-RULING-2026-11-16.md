---
id: GOV-EVIDENCE-PIN-REPAIR-1-GATE-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: 65d97a077
decision: APPROVED_WITH_CONDITIONS
---

# 历史证据 pin 例外通道 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-16
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r4\codex-gate-supersede-ruling.md`（4,156 B）
- **要解决的问题**：`FEA-11-HOST-AUTH-2` 这类**终态卡**的历史证据行无法在不改字节的前提下变绿；
  是否允许 `check.ps1` 自动识别 `*-supersede` 行？

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS

Q1: **B**。不让 `check.ps1` 自动识别任意 `*-supersede` 行；采用逐行、受控的历史 pin allowlist，只把经过核准的旧行错误降为可见 warning。

Q2:

1. 冻结资格基线为当前 supersession 提交 `65d97a077406d2041fd2de08e8d11b740eb9681b` 的父提交 `8db997f94683c6c959c30ba672af6df5d1bbc977`。我核对了该提交中的 FEA-11 卡：EV-01/03/11/12/13 原行已存在，`-supersede` 行尚不存在。allowlist 只能引用该基线中已经存在、当时状态为终态的行；非终态卡和基线之后新增或改写的行不得豁免。
2. 每个例外精确登记卡路径、Task ID、Evidence ID、原行各字段及当时的错误类型，并记录理由、裁定引用和失效条件。禁止通配符、按类别整体豁免或仅凭 `status: done` 放行。只有当前错误仍与登记的历史错误一致时，才可降级；新出现的路径缺失、哈希错误等继续报错。
3. 若登记了替代行，它必须在表中位于原行之后、基线中不存在，且只能对应同一精确路径；替代行自身须按常规规则通过完整 commit 解析和 `commit:path` blob SHA-256 校验。禁止跨路径替代、重复链式 supersede 或多个有效替代项。commit 本身不必晚于原行引用的 commit；要求的是替代记录在基线后追加，且其引用的 blob 可验证。
4. Allowlist 只产生明确的 legacy warning，不静默通过；只豁免该行当时已登记的证据错误，不豁免 Resource Manifest、表格结构或其他门禁。卡被重新打开或状态变为非终态时，例外失效；完成可靠重 pin 后应移除例外。
5. Allowlist 的新增或修改须由 DSH 逐项裁定，并经独立上下文只读复核；每项不得只因属于同一错误类别就批量获准。

Q3:

- **最小改动**：在 [check.ps1](/G:/CODEX/New%20Manga/tools/governance/check.ps1:709) 的证据表解析处加载并校验版本化 allowlist；在逐行证据校验处，仅将与冻结指纹及登记错误类型完全匹配的失败降为带理由的 warning。替代行仍执行原有严格检查；Resource 校验不变。
- **必须新增测试**：正例至少包括“精确匹配的基线终态行降为 warning”和“原行有同路径、有效 blob 替代行时，旧行告警而替代行通过”。负例至少包括“基线后新增行不能豁免”和“原行任一字段或错误类型变化后仍失败”；另应覆盖跨路径、错误 blob、重复替代与非终态卡拒绝。
- **性能**：默认门禁只需多读一次 registry，并对当前所选 Task 做精确查找，预计不会明显拖慢全局检查。多卡验证应缓存或批量读取基线 blob；验收要求默认 `check.ps1` 仍低于 10 秒，并记录前后耗时。
- **445 条**：允许按类别批量巡检、归因，也允许对已证明相同根因的修复使用脚本；但每条都必须单独得出修复或例外结论，并以精确行指纹登记，禁止按 `SHA_MISMATCH`、缺摘要、路径缺失或 commit 不可解析类别整批豁免。哈希错须定位权威 blob；缺摘要须从可信原始证据重建；路径缺失须逐项核实迁移，不能跨路径 supersede；commit 不可解析须恢复对象或用可信证据重 pin。不可恢复的历史行才可逐条申请 warning 例外。

风险与遗留:

- [check.ps1](/G:/CODEX/New%20Manga/tools/governance/check.ps1:788) 对旧六列表中的每行独立校验，也检查 `SOURCE_PIN`；当前没有 supersession 分支。Resource 错误在另一段独立校验中产生（约 912–920 行），不受此裁定影响。
- 我用 `git cat-file blob` 复核了 EV-11/12/13-supersede：三条 SHA-256 均与引用的 commit blob 及工作树字节一致。此前错误的旧行仍须按受控规则处理。
- 按你提供的实测，FEA-11-HOST-AUTH-2 仍有 EV-01/03 两条 pin 错误和两条 Resource 错误；本裁定不等于该卡单卡门禁已通过。建议 DSH 先将本裁定入库，再逐项处理这四个遗留错误并为获准的历史 pin 例外建立精确登记。本轮只读，未修改文件或提交。
```

## DSH 采纳（Lead 名义）

**Q1 = B，不采用「check.ps1 自动识别 supersede」**。这一点直接否掉了我原本在巡检工具里做的
「同路径存在可验证 supersede 行 ⇒ 原行判 SUPERSEDED」的**门禁化**用法。处置：

1. 巡检工具（`tools/governance/audit_evidence_pins.py`）**只是诊断**，不进门禁；其 `SUPERSEDED` 判定保留但仅供分诊，
   门禁一律以**受控 allowlist**为准（工具输出里会与 `EXEMPTED` 区分，见下轮实现）。
2. 门禁侧按裁定 Q3 落地：`check.ps1` 加载**版本化 allowlist**（一行一指纹），只在「卡路径 + Task ID + Evidence ID +
   原行各字段 + 历史错误类型」**完全一致**时降级为带理由的 warning；替代行仍走原有严格校验；Resource 校验不变。
3. 资格基线冻结为 **`8db997f94683c6c959c30ba672af6df5d1bbc977`**（supersession 提交 `65d97a07…` 的父提交）；
   基线之后新增/改写的行不得豁免；非终态卡不得豁免。
4. 逐条裁定 + 独立上下文只读复核后才可登记；禁止通配、禁止按类别整批豁免、禁止靠 `status: done` 放行。

## 对 445 条的分诊（AC4 输入）

DSH 已用只读巡检对全部 445 行做机器分诊（`verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-triage-2026-11-16.{md,json}`）：

| 类别 | 含义 | 行数 | 卡数 |
|---|---|---:|---:|
| `T1_PATH_EXISTS_DIGEST_MISMATCH` | 路径存在、摘要与 blob/工作树/LF/CRLF 全不匹配 ⇒ 可用当前字节重建（append supersede） | 122 | 64 |
| `T2_PATH_EXISTS_NO_DIGEST` | 路径存在但 sha256 单元格无 64 位摘要 ⇒ 需从可信证据重建摘要 | 211 | 51 |
| `T3_PATH_GONE` | 路径已不存在 ⇒ 逐项核实迁移；不可恢复者才可逐条申请 warning 例外 | 109 | 10 |
| `T4_NEITHER` | 路径不存在且无摘要 ⇒ 同上且信息更少 | 3 | 3 |

裁定要求「每条都必须单独得出修复或例外结论，并以精确行指纹登记，禁止按类别整批豁免」⇒ 本表只用于归因与排期，
**不构成任何豁免**。

## 未采纳项

无（裁定否掉了我原先「工具自动识别 supersede 即视作通过」的设想，已按 B 方案改道）。
