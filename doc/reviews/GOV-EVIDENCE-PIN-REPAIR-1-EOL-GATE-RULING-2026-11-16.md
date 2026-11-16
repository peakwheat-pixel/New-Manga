---
id: GOV-EVIDENCE-PIN-REPAIR-1-EOL-GATE-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: 94747c4ad
decision: APPROVED_WITH_CONDITIONS
---

# 门禁是否接受 blob 的行尾形态 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-16
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r6\codex-eol-gate-ruling.md`（3,711 B）
- **背景**：130 条历史 pin 记录的是 commit blob 的 CRLF 形态（签出时 `core.autocrlf=true` 的产物），
  门禁只比对「原始 blob」或「当前工作树」，两边都不等于 CRLF 形态 ⇒ 有效 pin 被判红。巡检工具已先按三种精确形态修正并验证。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS

Q1: A — 对六列历史行加入精确的行尾字节表示；这只处理 SHA-256 表示差异，不改变此前禁止自动 `SUPERSEDE` 的裁定。

Q2:

1. 有有效 `commit` 的六列行：保留现有的工作树原始字节匹配，并新增对 `commit:path` blob 原始、纯 LF、纯 CRLF 三种表示的精确 SHA-256 匹配。`commit` 必须可解析，且其中必须存在该路径。
2. 无 `commit` 时，只能对存在的工作树文件比较原始、纯 LF、纯 CRLF 三种精确字节表示。新行必须使用七列 `sha256_basis`；`BLOB`、`WORKTREE`、`EXTERNAL_SHA256` 继续只校验各自原始字节，不应用行尾变换。
3. 行尾变换须以字节操作完成，只替换 CRLF/LF；不得 trim、改编码、折叠空白或规范化其他字符。派生形式只对无 NUL、无裸 CR 的文本字节计算。混合行尾原文仅在 SHA 等于提交中的原 blob 时通过；其他混合变体必须报错。
4. 六列推断仅限冻结基线中已存在、字段未变且当时为终态卡的历史行；行级指纹之外的新行必须显式写 `sha256_basis`。工作树路径不存在时，只能尝试已解析提交中的 blob；无精确摘要匹配、提交不可解析或提交中无该路径，均报错，不自动降级为 warning。

Q3:

- **最小改动**：在 [check.ps1](</G:/CODEX/New Manga/tools/governance/check.ps1:916>) 的六列历史行校验中增加 blob 三种摘要计算，并将“工作树路径缺失即提前报错”调整为先尝试提交 blob。七列显式 basis 分支保持原始字节校验。用冻结基线行级指纹限制六列历史推断。
- **必须新增的测试**：正例至少覆盖“提交 blob 的 CRLF/LF 摘要通过”和“工作树路径已清理、提交 blob 精确摘要通过”；另覆盖无 commit 时工作树行尾表示。负例至少覆盖“内容字节改一位仍 FAIL”“非原 blob、非纯 LF/CRLF 的混合行尾仍 FAIL”；另覆盖提交及工作树都无法提供匹配时仍 FAIL，以及基线后新增六列行不能推断。现有巡检测试已有内容改单字节与混合行尾负例，但门禁本身仍需集成测试；另须保留 [test_canonical_evidence_basis.py](</G:/CODEX/New Manga/tools/governance/tests/test_canonical_evidence_basis.py:358>) 对显式 basis 精确字节语义的保护。
- **性能**：行尾哈希计算本身开销小；按 `commit:path` 缓存 blob，或批量读取，避免每行重复启动 Git。预计可维持低于 10 秒，但本轮只读核查不能证明实际耗时；实现后须记录同一门禁命令的前后耗时，并验收 `<10 s`。
- **剩余 310 条**：214 条缺 64 位摘要须从可信原始证据重建；53 条缺路径先检查提交中是否仍有 blob，不能恢复的逐条核实迁移或申请精确例外；31 条摘要不匹配须依据权威字节重钉或逐条处置；12 条提交不可解析须先恢复提交对象或以可信证据重钉。不得按类别批量降级。新规则只应消除经精确摘要证实的行尾表示误报。

风险与遗留:

- 已只读复核 `FEA-11-HOST-AUTH-2` 的 EV-01/EV-03：记录摘要分别等于 `f7016d3fb` 对应 blob 的 CRLF 形态；`HOST-CORECLIENT-1` 的 E1 构建日志在工作树缺失，但记录摘要等于 `c1efb938f...` blob 的 CRLF 形态。这印证了提交路径校验必须先于工作树缺失报错。
- 六列推断若不按冻结基线限制，后来新增的旧格式行也会获得隐式行尾推断资格。实现时须让新行强制使用七列格式。
- 推荐下一步：由 DSH 冻结上述边界，安排门禁实现、基线行资格规则、正反例测试及 `<10 s` 性能验收。
```

## DSH 采纳（Lead 名义）

**Q1 = A，采纳**：给六列历史行增加「精确行尾字节表示」校验。DSH 冻结的实现边界（逐条对齐裁定 Q2）：

1. **有可解析 commit 且该路径存在于该 commit** 时：接受 `commit:path` blob 的 ①原始 ②纯 LF ③纯 CRLF 三种**精确** SHA-256；
   现有工作树原始字节匹配保留。
2. **无 commit** 时：只对**存在**的工作树文件比较 ①原始 ②纯 LF ③纯 CRLF 三种精确形态。
3. 七列 `sha256_basis` 分支**不变**：`BLOB`/`WORKTREE`/`EXTERNAL_SHA256` 只校验各自原始字节，不做行尾变换；
   **新行必须使用七列**，行尾推断只服务历史行。
4. 行尾变换是**字节级**：只替换 CRLF/LF；不 trim、不改编码、不折叠空白；派生形态只对「无 NUL、无裸 CR」的文本字节计算；
   混合行尾原文只有在 SHA 等于提交中原 blob 时才通过，其它混合变体必须报错。
5. **资格限制**：六列推断只对「冻结基线 `8db997f9…` 中已存在、字段未变、当时卡片为终态」的行生效；基线之后新增的六列行不得推断。
6. **路径缺失的处理顺序**：先尝试已解析提交中的 blob；无 commit、提交不可解析、提交中无该路径、或三种形态都不匹配 ⇒ **报错**，
   不得自动降级为 warning。

### 待实现的验收（下一轮执行）

- 最小改动点：`check.ps1` 六列历史行校验分支（约 916 行附近）；blob 读字节用字节级方式（不经过 PowerShell 文本管道），按 `commit:path` 缓存。
- 必测：正例①“blob 的 CRLF/LF 形态摘要通过”②“工作树已清理、提交 blob 精确摘要通过”③“无 commit 时工作树行尾形态通过”；
  负例①“内容改 1 字节仍 FAIL”②“非原 blob、非纯 LF/CRLF 的混合行尾仍 FAIL”③“提交与工作树都无匹配仍 FAIL”④“基线后新增六列行不得推断”。
- 性能：同一门禁命令前后耗时对比，验收 < 10 s。
- 保留 `test_canonical_evidence_basis.py` 对显式 basis 精确字节语义的保护。

### 对剩余 310 条的裁定口径

无 64 位摘要 214 ⇒ 从可信原始证据重建；路径缺失 53 ⇒ 先查提交中是否仍有 blob，不可恢复者逐条核实迁移或申请精确例外；
摘要不匹配 31 ⇒ 依权威字节重钉或逐条处置；commit 不可解析 12 ⇒ 恢复对象或按可信证据重钉。**禁止按类别批量降级。**

### 未采纳项

无。裁定同时确认「不得因本次改动而让自动 supersede 复活」，与本项目既有 Q1=B 裁定一致。
