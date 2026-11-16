---
id: GOV-EVIDENCE-PIN-REPAIR-1-EXCEPTION-HOOKS-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: 34f6b3eae
decision: APPROVED_WITH_CONDITIONS
---

# 例外通道剩余三类行的处置 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-16
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r9\codex-exception-hooks-ruling.md`（1,809 B）
- **裁定者自述限制（如实保留）**：本会话无法执行命令（Windows 740），未独立核对 `check.ps1`/登记表/卡片原文，
  裁定以 DSH 提供的实测事实为前提；要求 DSH 入库前自行复核。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS  
Q1: A：仅当完整行指纹与冻结基线登记项精确匹配，且 `commit` 原文逐字相同，才允许降级为 warning。  
Q2: A：登记有序摘要列表，并同时绑定 `sha256` 单元格的原始字节；只有列表中每个摘要都不匹配任何精确表示时才允许降级。  
Q3: 判为“行结构非法”并保持错误：全 `-` 空壳行没有证据字段，不应归类为证据缺失，也不得加入例外通道。  
Q4:

1. 按行登记例外；指纹绑定冻结基线、文件路径、行原文摘要及各单元格原文。散文 `commit` 必须逐字记录，摘要列表须绑定顺序及原始单元格字节。
2. 例外仅适用于冻结基线中已存在且字节未变的行；新行、改写行及仅复用相同 ID 或路径的行均不继承例外。
3. 钩子仅处理对应格式错误：散文钩子要求 `commit` 非十六进制且非 `-`；多摘要钩子要求登记列表与原始单元格精确对应，且列表中每项都不匹配任何精确表示。不得使用通配符、前缀匹配或全局忽略。
4. 每条例外须有 DSH 的逐条裁定及独立复核记录；warning 保留行路径、指纹、裁定依据和复核来源，不能静默跳过。
5. 保留格式错误检测与现有测试；新增测试覆盖未登记、字节变更、基线外新行、摘要列表次序或分隔符变化，以及列表中存在已匹配摘要的情形。

风险与遗留:
- 本会话无法完成文件复核：命令进程启动被 Windows `740` 错误拒绝。因此以上是以题述实测事实为前提的条件性裁定，不能声称已核对 `check.ps1`、登记表和卡片原文。
- 建议下一步由 DSH 在入库前复核上述文件与冻结行指纹，确认实现及登记表满足这些边界。
```

## DSH 采纳（Lead 名义）

- **Q1=A**：新增 `COMMIT_FORMAT` 钩子 —— 只有登记项**逐字记录**该散文 commit、且该行在冻结基线中逐字存在时才降级；
  已实现（`check.ps1` 的 `Get-EvidenceException` 分支 + schema 对该 error_type 放宽 commit 字段）。
- **Q2=A**：`sha256` 允许**有序列表**（1–8 个），只有列表中每个摘要都不匹配任何精确表示才降级；已实现 `SHA_MULTI`。
- **Q3**：整行 `-` 判「行结构非法」，**不进例外通道**；已实现（在证据行解析处提前拦截）。
- **Q4 边界**：逐行登记（指纹含 card/task_id/evidence_id/path/commit 原文/摘要列表/class/error_type）；
  只对冻结基线中已存在且字节未变的行生效；钩子只处理对应格式错误；warning 保留路径/指纹/理由；
  保留既有测试并新增负例（未登记、字节变更、基线外新行、摘要列表顺序变化、列表中已有摘要匹配）。

### 实测（DSH 补做，裁定者未能执行）

- 单元格解析统一剥离反引号后，`COMMIT_FORMAT` 条目才真正命中（此前 `` `(见提交)` `` ≠ `(见提交)`）；
- 登记表 97 条（PATH_MISSING 51 / SHA_MISMATCH 34 / COMMIT_FORMAT 12）；全局门禁 PASS(3w)；例外通道测试 10/10。

### 未采纳项

无。
