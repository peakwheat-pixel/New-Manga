# 裁决：GOV-DECLARATION-SCAN-CLEANUP-1 · AC3 的四个机制选择（Codex，2026-11-16）

- **裁决者**：Codex（`codex-cli 0.162.0`，模型 `gpt-6-luna`，reasoning `xhigh`），会话 `01a1e3fd-1afa-7303-9486-72469e6b3ef6`。
- **请求方**：DSH（Lead）。请求文原字节见仓外
  `G:/CODEX/New Manga.workspace/tmp-dsh/ac3-r1/ADJUDICATION-REQUEST.md`；
  裁决原字节：同目录 `codex-ruling.md`（9251 B）。
- **被审事实基线**：head `ac34da5a5`；`--audit-declarations` → `154 error / 732 warning / 6755 declaration / 5593 protected root`，
  逐条明细已按 Ruling B 的 code→桶冻结映射落成
  `verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-baseline-disposition-2026-11-16.md`（B1 64 / B2 79 / B3 11）。
- **裁决者自述的限制（如实保留，不修饰）**：其 Windows 命令进程启动被系统以 **错误 740** 拒绝，因此它
  **没有独立复核当前 HEAD、文件字节或仓外审计 JSON**，裁定基于请求文列明的基线。
  ⇒ DSH 采纳时不把本裁决当"独立字节复核"，字节复核由 DSH 自己的实测与后续独立 Review 承担。
- **采纳**：DSH 以 Lead / Integrator 名义**采纳**本裁决（`APPROVED_WITH_CONDITIONS`），并把它作为 AC3 的实施约束；
  下文的「条件」是 AC3 判完成的必要条件。采纳记录见本文末尾。

---

# 裁定：GOV-DECLARATION-SCAN-CLEANUP-1 AC3

verdict: **APPROVED_WITH_CONDITIONS**

**结论摘要：**Q1 采用逐表绑定；Q2 采用逐文件、逐诊断的原始内容绑定；Q3 采用封闭的精确别名表；Q4 采用 AC5 的追加式窄例外，并新增 AC7 约束 67 条未钉住的 B2 修复。以下条件是实施和验收的一部分，未满足前不得将 AC3 判为完成。

**核验边界：**我尝试读取仓库状态和所列文件，但当前 Windows 命令进程启动被系统以错误 740 拒绝。因此，以下按请求中列明的基线、分类结果和冻结裁决作出机制裁定；没有独立复核当前 HEAD、文件字节或仓外审计 JSON。

## Q1 — B1 的实现机制

**裁定：采用 HIE `template_bindings` 逐表绑定；不采用整文件绑定。**

绑定粒度须是一张具体表。每条绑定至少记录：

- `origin_file`：仓库相对路径；
- `raw_sha256`：覆盖该表原始字节的哈希，保留换行差异，不做规范化；
- `fence`、稳定表定位信息及精确 `row_count`；
- `parser_snapshot`：解析器版本或规则快照；
- `errors`：该表对应的有序错误码与 locator；
- `classification: B1`、`interpretation: historical_format_preserved`；
- 每条被裁决错误的 disposition、依据及活 pin 状态；
- 绑定的唯一作用范围：匹配该表，不得排除同一文件中的其他表或声明。

64 条错误须全部与绑定记录对应，不能只凭“约有 45 张历史卡”作批量豁免。表级哈希与精确 locator 任一不匹配时，绑定失效并重新报错。

**保护根判据：**绑定为非声明源不必然与 AC3 冲突，但不能假定这些表没有贡献任何保护根。当前计数为 5593，AC3 的书面下限为 5582；我不裁定可以利用这 11 个计数差额抵消保护根损失。验收须证明**基线保护根集合是最终集合的子集**，且最终计数至少为 5593；如表级绑定会移除根，必须证明并保留相同保护效果，否则不得绑定该表。

**反方风险：**若绑定意外覆盖同文件的有效声明，或只看总数而丢失特定保护根，会把保护退化藏在计数中。

## Q2 — B3 的 4 条解析错误

**裁定：选择 HIE `raw_non_declaration_bindings`，不修历史字节，也不另以宽泛的 JSON 例外清单绕过扫描。**

每条绑定至少包含：

```json
{
  "origin_file": "仓库相对路径",
  "raw_sha256": "完整文件原始字节的 SHA-256",
  "size_bytes": 0,
  "format": "markdown | json",
  "classification": "B3",
  "interpretation": "non_declaration_source",
  "expected_diagnostics": [
    { "code": "FILE_UNREADABLE | JSON_PARSE", "count": 1, "locators": ["精确位置"] }
  ],
  "nul_offsets": [],
  "parser_snapshot": "解析器/规则版本",
  "basis": "为何该文件不是声明源"
}
```

对含 NUL 的 Markdown，`nul_offsets` 必须是精确偏移列表；对两份 JSON，须显式记录空的 `nul_offsets` 和各自的 `JSON_PARSE` 诊断。路径、哈希、大小、诊断码或 locator 任一不匹配时，绑定不得生效。绑定只能解释列出的诊断，不能吞掉该文件的其他错误、警告或新发现的声明。

**反方风险：**整文件绑定可能遮盖同一文件中的真实声明。上述精确诊断范围和哈希失配即恢复报错，是采用整文件内容绑定的前提。

## Q3 — 8 条 `DECL_UNKNOWN_DISPOSITION`

**裁定：采用候选 (a) 的精确、封闭别名表；不为这 8 条首选行级 HIE 绑定，也不把 disposition 列降级为自由文本。**

别名仅在 Resource Manifest 的 disposition 字段中按原始 token 精确匹配：

| 原始 token | 规范 disposition |
|---|---|
| `PRESERVE` | `PRESERVE_UNKNOWN` |
| `READ_ONLY_REFERENCED` | `PRESERVE_REFERENCED` |
| `MODIFIED_IN_PLACE` | `PRESERVE_IN_REPO` |
| `RESTORED_IN_PLACE` | `PRESERVE_IN_REPO` |
| `NOT_CREATED_NO_SCRATCH` | `ALREADY_ABSENT` |

`DISPOSITION_RE` 保持封闭；只有列出的原始 token 可被映射。别名匹配须区分大小写并记录原始值与规范值，不能对大小写、空白、前后缀或近似拼写作通用归一化。`PRESERVE_UNKNOWN` 必须由扫描器的语义层明确实现为保全类 disposition，并按该行的可解析路径保留保护；不能仅因它匹配正则就算通过。若其语义实现无法证明具有保全效果，该映射不得启用。

这确实扩大了**五个精确 token**可接受的输入集合，但在此处**不构成放宽检查或绿洗**：原先 8 条因非法 token 未注册；规范化后须注册为有效 disposition，并保留相应保护。判断依据是逐条注册结果、保护根集合不缩小和未列 token 仍失败，而不是“错误数下降”本身。

**反方风险：**别名可能误赋予含糊 token 保护语义。`PRESERVE_UNKNOWN` 的保全语义及 `ALREADY_ABSENT` 的缺失含义必须由扫描器明确执行、逐条留痕；不得把无法确认的路径映射成 `ALREADY_ABSENT` 以消除诊断。

## Q4 — 67 条未钉住 B2 修复与 AC5

**裁定：选择候选 (a)，用 AC5 追加式窄例外授权修改，并新增 AC7。** 不接受把这些真实缺陷整体绑定为非声明源。12 条落在已钉住 manifest 的 B2 记录仍须只登记、不改字节。

AC5 已完成的历史核验范围和结果不得追溯改写。可在 AC5 后**追加**以下约束：

> **AC5 补充（仅适用于 AC3 本轮）**：既有 AC5 核验范围 `a6608dd4b..HEAD` 及其结果保持原样，不追溯修改。自本轮声明归属表冻结提交起，`doc/tasks/*` 的字节保护仅对 AC7 中精确列明的 Resource Manifest 单元开放；仅允许 AC7 `allowed_cells` 所列替换，同一文件其他字节不得变化。本补充不授权修改任何 `verification/**` 历史文件、任何 `RESOURCE-MANIFEST.json` 字节或 RRI-01…07。

`allowed_paths` 应是这 67 条对应文件的精确路径集合；它本身不够，必须同时有 `allowed_cells` 的 67 条逐单元清单。不得授权整个 `doc/tasks/*.md`、整张表或整行随意改动。

AC7 至少应机械验证：

1. 67 条逐条对应基线 B2 明细，含 `file`、`locator`、字段名、原始值、错误码、修复依据、活 pin 核验结果；每项唯一，不缺漏、不重复。
2. 修改前再次核验活 pin；67 条全部未被活 pin 引用。钉住的 12 条只登记，保留原诊断、原始值、文件哈希及 Canonical Evidence 引用，不改文件字节。
3. 每个允许修改的单元记录原文件哈希、单元 locator、旧值和新值。机械比较须证明变化只发生在列明单元；修复后的值须语义真实、可解析，不能用占位值或臆造路径消音。
4. 声明错误数按每个实施批次单调不增，最终为 0；被 pin 保留的 B2 诊断须以**可审计的保留状态或警告**继续显示原始错误码与 pin 依据。不得隐藏这些真实缺陷来宣称“零错误”。
5. 最终保护根集合包含基线集合，最终计数至少 5593。
6. `verification/**` 历史文件、所有 `RESOURCE-MANIFEST.json` 和 RRI-01…07 字节保持不变；AC5 补充例外之外不得有其他 `doc/tasks/*` 字节变化。

**反方风险：**追加例外容易被误读为全面撤销 AC5；如果只做路径白名单，允许文件中非目标内容一并变化。保留旧核验记录，并用单元级清单核验，是授权范围有效的条件。

## 不做清单

- 不按整文件、目录或通配符把资源声明排除出扫描。
- 不将 disposition 列降级成自由文本，不添加正则前缀、大小写归一化或模糊别名。
- 不用 HIE 绑定覆盖 B2 真实缺陷，特别是不以绑定代替 67 条修复。
- 不修改任何活 pin 钉住的 B2 源文件或 manifest；不修复含 NUL 的历史字节。
- 不用全局忽略 `FILE_UNREADABLE`、`JSON_PARSE` 或路径诊断的方式达成 `errors=0`。
- 不用新增保护根抵消旧保护根丢失，也不以 `protected_roots ≥ 5582` 作为允许基线集合缩小的理由。
- 不把 AC5 解释成全体历史任务卡都可改；不以路径白名单代替单元级 diff 审核。
- 不以占位符、`NOT_APPLICABLE` 或未经证实的 `ALREADY_ABSENT` 将真实缺陷改成无诊断状态。

## 验收时须机械证明

AC3 完成时，至少须有可复核的报告证明：

- 154 条基线错误与最终处置清单逐条一一对应，分类总数为 B1 64、B2 79、B3 11；
- 错误计数逐批次单调不增，最终 `errors = 0`；12 条活 pin B2 的原始错误码仍可见且有登记，不被伪称为已修复；
- `protected_roots ≥ 5593`，且基线保护根集合包含于最终集合；
- 64 条 B1 精确匹配表级绑定，4 条 B3 精确匹配内容绑定，8 条别名只接受上述 token，67 条 B2 修复只触及 AC7 列明单元；
- 任何文件哈希变化、locator 漂移、未列 token、额外声明或活 pin 变化都会使相应绑定/例外失效或使核验失败；
- AC5 保护范围内的文件字节和 RRI-01…07 全部不变。

**建议下一步：**由 DSH 将本裁定追加到该 Task，冻结逐条处置清单和 AC7 单元清单后，再按职责分配实施及上下文独立 Review。

---

## 采纳与执行记录（DSH，append-only）

- **采纳结论**：采纳 `APPROVED_WITH_CONDITIONS` 全文，逐条作为 AC3 实施约束。四项机制选择：
  Q1 逐表 `template_bindings`；Q2 逐文件 `raw_non_declaration_bindings`（带 `expected_diagnostics`）；
  Q3 封闭别名表（5 个精确 token）；Q4 AC5 追加式窄例外 + 新增 AC7（单元级清单）。
- **已实施（batch 1，2026-11-16）**：Q3 别名表 → `tools/governance/clean_workspace.py` 新增
  `DISPOSITION_ALIASES`（5 个 token，精确、区分大小写）与 `DISPOSITION_ALIAS_APPLIED` 警告（记录原始值与规范值）；
  测试 `tools/governance/tests/test_disposition_aliases.py`（9 项，含"未列 token 仍 fail-closed"与"大小写不折叠"负例）。
  **实测**：`errors 154 → 147`、`warnings 732 → 740`、`declarations 6755 → 6762`、`protected_roots 5593 → 5598`（不缩）。
  其中 `DECL_UNKNOWN_DISPOSITION 8 → 0`；同时暴露 1 条被 disposition 错误掩盖的真实缺陷
  （`doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` 的 source 是凭据描述文本而非路径）⇒ `DECL_RELATIVE_UNRESOLVED 26 → 27`，
  该条转入 B2 处置（**不是**用别名消音的）。
- **后续批次（按裁决条件执行，未完成前 AC3 不得判完成）**：
  Q2 4 条绑定 → Q1 64 条表级绑定（须证明保护根集合不缩）→ 12 条活 pin B2 + 3 条活 pin B3 的保留态（原始错误码以
  可审计的警告态继续显示）→ 67 条 B2 单元修复（AC7）→ AC6 集成复验 + 上下文独立 Review。
