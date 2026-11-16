---
id: GOV-EVIDENCE-PIN-REPAIR-1-PLACEHOLDER-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: a5c635229
decision: APPROVED_WITH_CONDITIONS
---

# 带 class 的占位行与 superseded 卡证据 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-17
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r16\codex-placeholder-ruling.md`（1,524 B）
- **背景**：2 条证据行缺 evidence_id/path/sha256 但 class 写 `CANONICAL`；另有 15 条证据行落在 `status: superseded` 卡上。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS  
Q1: D — 缺少必填字段的 `CANONICAL` 行判为无效且不计作证据；现存行可按精确指纹登记为 warning，但卡片仍须有独立有效证据，否则 FAIL。  
Q2: A — `superseded` 卡继续不受门禁校验、由巡检标记 `NOT_ENFORCED`，并为 15 条逐条补登记；卡片状态转为受检状态时须恢复门禁校验。  
Q3:

1. `class` 不能代替 `evidence_id`、path 或 sha256。结构校验先于 class 判断；缺字段的行无效，不能满足证据要求。
2. 例外仅限已存在且逐行核实的历史行；登记须绑定 task、文件路径、行号、原行指纹及文件指纹，不得使用通配符或自动登记。行内容或文件变化后，登记失效。
3. warning 只记录该历史行，不使其成为证据，也不豁免卡片的证据要求。受检状态的卡片若没有其他完整有效证据，仍须 FAIL。
4. `superseded` 登记明确标为 `NOT_ENFORCED` 并注明状态与理由；状态改变后不得沿用该豁免。

风险与遗留:

- 提供的 `FEA-05-WIRE-1.md:126` 字面内容是全 `-` 行，单凭该内容无法确认 class 为 `CANONICAL`；若实际确为全占位行，应按既有规则处理，不能登记成带 class 的例外。
- 本环境创建只读 shell 进程失败（Windows error 740），因此未能直接读取指定文件。以上是基于你提供的实测事实作出的规则裁定；DSH 入库前应核实该行的实际内容与表头，再建立精确登记。
```

## DSH 采纳（Lead 名义）

- **Q1=D**：缺必填字段的 `CANONICAL` 行**判为无效、不计作证据**；本卡若没有其他完整证据则 FAIL。
  实现为：门禁在 Canonical Evidence 的**原始行**上检查（`Get-TableRows` 会丢弃首格为 `-` 的行），
  该行本身报 warning（写明「不计作证据；本卡另有 N 条完整行」）；若全卡没有完整行则报 error。
  实测：`FEA-05-WIRE-1` / `FEA-GOV-6` 各有完整证据行（本 Task 早前补登），故 PASS(4w)，其中一条 warning 即该无效行。
- **Q2=A**：`superseded` 卡继续不受门禁校验，巡检工具标 `NOT_ENFORCED`；这 15 条在巡检输出里逐条可见，不进入失败计数。
- **Q3 边界**：`class` 不能替代 id/path/sha256；结构校验先于 class；行内容或卡片状态变化后判定失效。

### 裁定者指出的现场校正（已采纳）

其只读复核指出：`FEA-05-WIRE-1.md:126` 的字面内容是**全 `-` 行**，DSH 题述的「带 class」不准确。
DSH 已复核：实际两行均为 `| - | - | - | `-` | `-` | CANONICAL |`（class 列存在 `CANONICAL`，但 id/path/sha 全为占位符），
与裁定者的描述一致，故按「缺必填字段」处理，而不是「整行占位符」。
