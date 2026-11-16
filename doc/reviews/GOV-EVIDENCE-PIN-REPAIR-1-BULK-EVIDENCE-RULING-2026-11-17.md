---
id: GOV-EVIDENCE-PIN-REPAIR-1-BULK-EVIDENCE-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: 5f14f06b0
decision: APPROVED_WITH_CONDITIONS
---

# 大目录证据（EVIDENCE-MANIFEST）与 Resource Manifest 散文行 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-17
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r11\codex-bulk-evidence-ruling.md`（2,086 B）
- **背景**：`DISPLAY-PERF-DECISION-1`（research/done）的 `evidence_dir` 有 235+ 个文件，逐行登记不现实；
  其 Resource Manifest 的表头曾被批量脚本改坏（第 5 列写入路径）。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS
Q1: A（附自引用处理）：manifest 逐文件列出 `evidence_dir` 中除自身外的所有文件；manifest 本身以 `Canonical Evidence` 行登记并校验。
Q2: A：散文移出 `Resource Manifest`；若它代表具体资源，仍须用真实路径行逐项记录，避免丢失处置对象。
Q3:

1. 仅在获准的卡片类型中启用；manifest 固定为 `evidence_dir/EVIDENCE-MANIFEST.json`，拒绝目录外引用、绝对路径、`..`、glob 和链接。
2. 使用固定、严格的 JSON schema；校验 `task_id`、相对路径唯一性及 64 位 SHA-256。无效、重复、越界或缺少字段均失败。
3. 门禁自行递归枚举目录中的全部普通文件（包括隐藏和系统文件），逐个重算 SHA-256。manifest 条目必须与实际文件集合精确相符：新增文件、缺失文件、哈希不符或未登记文件均失败；不能只比较总数或总校验和。
4. `Canonical Evidence` 必须单独登记 manifest；门禁要将它的登记哈希与当前文件字节比对，不能只接受一个与当前文件脱节的历史 blob。既有证据行保持原字节；表格行与 manifest 重复覆盖时，哈希必须一致。
5. 卡片声明 `evidence_dir` 却缺目录、manifest 缺失或解析失败时均须失败关闭；不得以忽略规则、目录前缀或散文说明替代逐文件覆盖。

Q4: 是：仅允许 `kind: research`，以及 schema 明确支持的 `evidence-only`；其他类型继续逐项登记，不以标题或说明文字推断资格。
风险与遗留:
- 当前工作树递归盘点结果是 246 个普通文件、58 个目录，与题述 235 个不一致。
- 当前卡片的 `source_path` 两行是实际路径；`Resource Manifest` 第五列表头却是路径而非字段名。所读脚本仅在 `DELETE_SAFE` 分支检查来源路径存在性，对其他处置类型主要校验目标路径。因此，本次只读检查未能复现“散文 `source_path` 被解析器拒绝”的情况；DSH 应先对齐目标版本与失败现场，再按本裁定改门禁。
```

## DSH 采纳（Lead 名义）

- **Q1=A**：允许 `evidence_dir/EVIDENCE-MANIFEST.json` 逐文件列清单（含相对路径 + 64 位 SHA-256），manifest 本身必须被
  `## Canonical Evidence` 单独登记并与当前字节比对；门禁须**自行递归枚举**目录内全部普通文件（含隐藏/系统文件）重算 SHA-256，
  与 manifest 条目**精确集合相等**：新增、缺失、哈希不符、未登记均失败；不得只比总数或总校验和。
- **Q2=A**：Resource Manifest 只保留真实路径行；叙述性内容移出表格。
- **Q3 边界**：固定路径 `evidence_dir/EVIDENCE-MANIFEST.json`；拒绝目录外引用、绝对路径、`..`、glob、符号链接；固定严格 JSON schema
  （含 `task_id`、相对路径唯一性、64 位小写 SHA-256）；目录缺失 / manifest 缺失 / 解析失败一律失败关闭。
- **Q4**：仅允许 `kind: research`（以及 schema 明确支持的 evidence-only）；其他类型继续逐项登记。

### 裁定者指出的两处现场不符（如实保留）

1. 其递归盘点得到 **246 个普通文件 / 58 个目录**，与 DSH 题述的 235 不一致（DSH 记录的是 235，差 11，需复核计数口径）；
2. 其只读检查未能复现「散文 `source_path` 被解析器拒绝」；反倒是**第 5 列表头被写成路径**——这正是 DSH 批量脚本造成的损坏，
   DSH 已恢复表头；因此该卡剩余失败应归因于「表头/行形态」而非「散文 source」。

### 待实现的验收（下一轮）

- 门禁新增 manifest 机制（仅 research 卡）；单元测试覆盖：清单缺失、条目缺文件、文件多出、哈希不符、路径逃逸、重复路径、manifest 自身未登记；
- `DISPLAY-PERF-DECISION-1`：按其真实文件重算 manifest，并把叙述性内容移出 Resource Manifest 表。
