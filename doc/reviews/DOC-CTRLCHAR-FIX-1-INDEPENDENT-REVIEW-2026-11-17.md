---
task_id: DOC-CTRLCHAR-FIX-1
reviewer: reviewer-g3dc
reviewer_kind: subagent
reviewer_source: DSH 子 agent `reviewer-g3dc`（独立上下文，未参与该卡实现或返修；由父 agent `lead` 派发）
author: DSH
base_commit: 819298e99
reviewed_head: 89b36c3f2
review_time: "2026-11-17T12:57:00–13:13:18+08:00"
decision: ACCEPTED_WITH_FINDINGS
template_decision: approved
p0: 0
p1: 0
p2: 1
p3_observations: 4
---

# Review（独立复核）：DOC-CTRLCHAR-FIX-1

> **审查者来源**：`reviewer-g3dc`，DSH 子 agent，独立上下文，未参与本卡实现。
> **被审 head**：`89b36c3f2`（main）。修复提交为 `1ef6a2ebd`（37 字节），四件套证据提交 `3a0dea7b7`；`1ef6a2ebd` 之后被修的 5 张卡**未再变动**（`git diff --name-only 1ef6a2ebd 89b36c3f2 --` 五文件输出为空），故 `89b36c3f2` 上的被修字节与交付提交一致。
> **本复核不构成产品发布验收**。

## 1. 范围与依据

- 复核对象：`doc/tasks/DOC-CTRLCHAR-FIX-1.md`（status `in_review`，AC1–AC6 均 `<<MET>>`）、证据目录 `verification/DOC-CTRLCHAR-FIX-1/`、修复提交 `1ef6a2ebd` 与其父 `24c573d1b`。
- 依据：`AGENTS.md`、`doc/09_COLLABORATION.md`、本卡 AC/允许范围/禁止范围、用户 2026-11-15「全部授权」。
- 只读边界：未修改任何被审文件、卡片 frontmatter 或 `verification/**` 既有字节；本文件是唯一写入。扫描脚本只写到 `G:\CODEX\New Manga.workspace\tmp\review-g3dc\`。
- 工作区说明：复核期间 `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` 与 `doc/handoffs/NEXT-SESSION-STARTER.md` 有 Lead 的并发未提交改动；`doc/tasks` 控制字符扫描对**工作树**与 **HEAD tree** 各做一遍，两者均为 0。

## 2. B1：全量字节级复查（实测）

脚本：`G:\CODEX\New Manga.workspace\tmp\review-g3dc\review_scan.py`（Python 3）。规则：逐字节扫描 `doc/tasks/**/*.md`，**排除 LF(0x0A)** 与 **CRLF 中的 CR(0x0D+0x0A)**；其余 `0x00–0x1F` 与 `0x7F` 计为控制字符。

| 对象 | `.md` 文件数 | 控制字符命中 | 命中文件 |
|---|---|---|---|
| **HEAD `89b36c3f2`（git blob 原始字节）** | **667** | **0** | 0 |
| **工作树（含 Lead 并发未提交改动）** | **667** | **0** | 0 |
| 父提交 `24c573d1b`（修复前，对照） | 667 | **37** | **5** |

父提交的 37 处分类：**BEL 8 / BS 5 / TAB 12 / VT 6 / FF 1 / 孤立 CR 1 / ESC 4**——与卡面 AC1、Closeout、证据日志 `ctrlchar-scan-and-fix-2026-11-17.log:7-8` 的 7 类计数**完全一致**。

结论：**残留 0**，AC1/AC2/AC3 的「清零」成立；667 个 `.md` 的全量口径也成立。

## 3. B2：37/37 校验（父提交 → 修复提交）

对 5 个文件逐字节比对 `24c573d1b:<path>` 与 `1ef6a2ebd:<path>`：

| 文件 | 字节长度（前→后） | 差异字节数 | 是否全部「控制字符→ASCII 字母」 |
|---|---|---|---|
| `doc/tasks/AC-BLOCKED-CLOSE-1.md` | 5755 → 5755 | 3 | 是（VT→v、VT→v、BEL→a） |
| `doc/tasks/DOC-CTRLCHAR-FIX-2.md` | 6330 → 6330 | 1 | 是（VT→v） |
| `doc/tasks/FEA-07.md` | 85971 → 85971 | 2 | 是（**CR→r**、VT→v） |
| `doc/tasks/HUMAN-VS-AGENT-SPLIT-1.md` | 5605 → 5605 | 3 | 是（BS→b、VT→v、BEL→a） |
| `doc/tasks/SIDECAR-SCHEMA-STALE-1.md` | 34149 → 34149 | 28 | 是（BEL/BS/TAB/VT/FF/ESC → a/b/t/v/f/e） |
| **合计** | **长度全部不变** | **37** | **37/37，problems = NONE** |

- 程序化断言：每个差异位置的旧字节都 `∈ {0x00–0x1F, 0x7F}`；新字节都 `∈ [A-Za-z]`；5 个文件长度差均为 0。输出 `problems: NONE`。
- 行级 diff：`git diff --numstat 24c573d1b 1ef6a2ebd -- doc/tasks` 中五文件为 2/2、1/1、1/1、2/2、23/23，合计 **29 行增 / 29 行删（对称）**；第 6 个文件是 `GATE3-SETTINGS-SHORTCUT-1.md`（9/9，本卡之外的 GATE3 卡文档更新）。因此提交 `1ef6a2ebd` 的 `doc/tasks` 全量是 **38/38**，本卡修复范围（五文件）是 **29/29**——两者口径不同，均无「多余改动」。
- **没有额外字节改动**：除上述 37 个位置外，五文件逐字节相同；没有插入/删除整行（CR→r 使一行由 CR 分成两段并回一行，属预期）。

## 4. B3：逐处语义正确性（抽 14 处，含关键 CR 处）

| # | 文件:偏移 | 字节 | 修复后上下文（片段） | 判定 |
|---|---|---|---|---|
| 1 | `AC-BLOCKED-CLOSE-1.md:5025` | VT→`v` | `AC5（末条带 verified 注释…` | ✅ `verified` |
| 2 | `AC-BLOCKED-CLOSE-1.md:5564` | VT→`v` | `…PASS (3 warnings)｜verify_pins 18/18…` | ✅ `verify_pins` |
| 3 | `AC-BLOCKED-CLOSE-1.md:5584` | BEL→`a` | `…｜api_inventory 1/80/6=87…` | ✅ `api_inventory` |
| 4 | `DOC-CTRLCHAR-FIX-2.md:5940` | VT→`v` | `…git status 干净、verify_pins 18/18…` | ✅ `verify_pins` |
| 5 | **`FEA-07.md:52982`** | **CR→`r`** | `…**（reviewer-fea07b，全新…` | ✅ **正确**：删除会得到 `eviewer-fea07b`（仍错），还原 `r` 才是 `reviewer-fea07b` |
| 6 | `FEA-07.md:53057` | VT→`v` | `…报告 verification/FEA-07-AC5-…` | ✅ `verification` |
| 7 | `HUMAN-VS-AGENT-SPLIT-1.md:5155` | BS→`b` | `…**核心判断**：blocked ≠ 人才能…` | ✅ `blocked` |
| 8 | `SIDECAR-SCHEMA-STALE-1.md:9363` | BS→`b` | `改 package.ps1 / build_sidecar.ps1…` | ✅ `build_sidecar.ps1` |
| 9 | `SIDECAR-SCHEMA-STALE-1.md:9606` | BEL→`a` | `…｜apps/desktop-avalonia/…` | ✅ `apps/` |
| 10 | `SIDECAR-SCHEMA-STALE-1.md:9973` | BS→`b` | `…读 build-manifest.json 比对…` | ✅ `build-manifest.json` |
| 11 | `SIDECAR-SCHEMA-STALE-1.md:12848` | TAB→`t` | `…｜term_extract｜completed…` | ✅ `term_extract` |
| 12 | `SIDECAR-SCHEMA-STALE-1.md:16073` | ESC→`e` | `…core 响应里的 error.code**…` | ✅ `error.code` |
| 13 | `SIDECAR-SCHEMA-STALE-1.md:31620` | FF→`f` | `…新增 failure_boundary = "tran…` | ✅ `failure_boundary` |
| 14 | `SIDECAR-SCHEMA-STALE-1.md:33172` | TAB→`t` | `…分布差 30 ⇒ test.ps1 的额外环境…` | ✅ `test.ps1` |

全部 37 处上下文均已逐条打印核对，恢复后的 token 均为有意义的单词/路径/标识符；**未发现「控制字符被替换为空格、或还原成错误字母」的情况**。`FEA-07.md` 的孤立 CR 按「还原为 `r`」而非「删除」处理是**正确**的：该 CR 占据 `reviewer` 的首字母位（修复前字节序列为 `（` + `0x0D` + `eviewer-fea07b`），删除只会得到 `eviewer-fea07b`；AC3 与 Closeout 已如实登记该规则更正。

## 5. B4：门禁与四件套（实测）

命令与实测输出（2026-11-17，`89b36c3f2`，pwsh 7）：

```text
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/DOC-CTRLCHAR-FIX-1.md
→ Governance check: PASS (3 warnings)   EXIT=0
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md
→ Governance check: PASS (3 warnings)   EXIT=0
pwsh -NoProfile -File tools/governance/verify_pins.ps1
→ OK C01b…C17 / OK FEA01；PIN AUDIT: PASS (all 18)   EXIT=0
python tools/governance/audit_evidence_pins.py
→ rows=7120  FAIL=0  EXEMPTED=84  SUPERSEDED=0  WARN=273   EXIT=0
```

三条 warnings 均为既有全局提示（10 个非终态 Task、`doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md` 达预算 80%），与本卡改动无关。

**Canonical Evidence pin 逐条复算（sha256，BLOB 口径）**：

| evidence_id | 声明 sha256 | HEAD blob | 结论 |
|---|---|---|---|
| EV-G3SS-01 | `cfa29e0f…` | `cfa29e0f…` | ✅ |
| EV-G3SS-02 | `9302e219…` | `9302e219…` | ✅ |
| EV-G3SS-03 | `ed1c19c3…` | `ed1c19c3…` | ✅（工作树为 CRLF，EOL 对应物 `74b0830a…`；不违反 BLOB 口径） |
| EV-G3SS-04 | `f8d8afcd…` | `f8d8afcd…` | ✅ |
| EV-DC1-01 | `7d074bf3…` | `7d074bf3…` | ✅（工作树 CRLF） |
| EV-DC1-02 | `e8bef311…` | `e8bef311…` | ✅ |
| EV-DC1-03 | `c92e04b5…` | `c92e04b5…`（HEAD）且 `1f3bd0d84:verification/DOC-CTRLCHAR-FIX-1/fix-report.log` = 同值 | ✅（历史 SOURCE_PIN 仍成立） |

结论：AC5 的「`verify_pins` 18/18、四件套 PASS」成立；证据巡检当前 head **FAIL 0**（卡面 Closeout 记的 7117 行是 `1ef6a2ebd` 时点，现为 7120 行，属正常增量）。

## 6. B5：改写 5 张历史卡字节是否违反「不碰历史证据字节」

**判定：不违反，属于本卡获批的修复。**

依据：

1. **受保护对象的范围**：`AGENTS.md`（2026-10-25 用户裁决）与 `doc/09_COLLABORATION.md:9` 保护的是「历史署名、冻结 Review、日志、manifest 和 evidence pin」的原字节。本次改的是 5 张 **task 卡的正文/说明文字**，不是署名、冻结 Review、日志、manifest 或 evidence pin。
2. **授权与范围**：卡 `approval: 用户 2026-11-15「全部授权」`，`allowed_paths` 显式含 **`doc/tasks/**`**；项目也记录了「全部授权」的 standing mandate（`doc/handoffs/DSH-AUTORUN-PROMPT-RESIDUAL-CLOSEOUT.md:11`）。改动完全落在授权路径内。
3. **未破坏任何 pin**：
   - 在全部 tracked `doc/**` 与 `verification/**` 中检索 5 张卡的**修复前 sha256**，0 命中——没有任何报告/manifest 用旧字节给这 5 张卡做 pin；
   - 唯一对 `doc/tasks/FEA-07.md` 的 pin 是 `doc/tasks/FEA-07-RESIDUAL-3.md:129`（`EV-R4B-07`，commit `8e9420f41`，sha256 `c64b6a97…`）；实测 `8e9420f41:doc/tasks/FEA-07.md` 的 sha256 仍为 `c64b6a97427ef8c37b1f40569d5182d0476dd2742e8a945bc3a3cf5fea40b3eb`（83161 B）——**历史 pin 指向历史 commit 的 blob，不受当前工作树修复影响**。
4. **改动性质**：37/37 字节均为「控制字符 → ASCII 字母」，5 文件长度不变，无插入/删除内容（CR→r 的行合并是还原原意的必然结果），符合卡面「只修控制字符、不改文字内容」的禁止范围。
5. **注册情况**：AC1/AC3/AC4 与 Closeout 已登记 37 处、5 文件、7 类与规则更正；证据日志逐处列出 offset/前后字节/上下文。

**需要如实指出的现场事实（与派单描述不同）**：这 5 张卡的实际状态是 **3 张 `done`**（`AC-BLOCKED-CLOSE-1`、`FEA-07`、`HUMAN-VS-AGENT-SPLIT-1`）+ **2 张 `closed_with_limitations`**（`DOC-CTRLCHAR-FIX-2`、`SIDECAR-SCHEMA-STALE-1`），**没有 `in_progress` 卡**（派单写「2 张 done + 1 张 closed_with_limitations + 1 张 in_progress」）。这不改变「已关闭卡被改字节」的敏感性，但结论仍是：**授权范围内、无 pin 依赖、纯控制字符修复**，不属于违反硬约束。建议 Closeout 把这 5 个文件名与状态列出，便于审计（P3 建议，见 §8）。

## 7. 实测覆盖表

| # | 场景 / AC | 实际执行的命令或步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|---|
| B1 | AC2/AC3 残留 | `review_scan.py` 扫描 HEAD tree + 工作树 667 个 `.md` | `89b36c3f2` | **0 / 0** | 本文 §2 |
| B2 | AC4 37/37 | 逐字节比对父/修复提交 5 文件；`git diff --numstat` | `24c573d1b`→`1ef6a2ebd` | **37 差异、长度全不变、29/29 行** | 本文 §3 |
| B3 | AC1/AC3 语义 | 打印 37 处上下文，抽核 ≥14 处 | `1ef6a2ebd` | 全部为有意义 token；CR→r 正确 | 本文 §4 |
| B4 | AC5 门禁 | `check.ps1` × 2、`verify_pins.ps1`、`audit_evidence_pins.py` | `89b36c3f2` | PASS(3w) / PASS(3w) / 18-18 PASS / FAIL 0 | 本文 §5 |
| B5 | AC4 证据 pin | 7 条 declared sha256 vs HEAD blob/worktree/historical blob | `89b36c3f2` | 7/7 成立 | 本文 §5 |
| B6 | 历史 pin 安全性 | 检索五卡修复前 sha256；校验 FEA-07 的 `EV-R4B-07` | `8e9420f41` | 旧字节 0 处被 pin；历史 pin 仍匹配 | 本文 §6 |
| N1 | 声明审计（clean_workspace.py） | 未重跑（不在派单要求的三条命令内） | — | **NOT_RUN**（以 `four-piece-2026-11-17.log:21` 记录为参考） | — |
| N2 | 首轮 2026-11-16 修复（33 TAB/20 CR） | 只读 `fix-report.log` 追溯来源 | `819298e99` | 历史记录，不重跑 | 本文 §8 R-001 |

## 8. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | **P2** | `doc/tasks/DOC-CTRLCHAR-FIX-1.md:3`（标题）、`:28`（背景）、`:38`（§2 标题）、`:59-66`（§修复表） | 仍保留 **2026-11-16 首轮**的数字：33 TAB / 20 孤立 CR / 修复文件 37 个 / 44 insertions-44 deletions；与本卡实测的 **12 TAB / 1 CR / 5 文件 / 29-29** 及 AC1–AC4 直接矛盾。影响：卡面自相矛盾；若被后续引用，会误以为改了 37 张历史卡（实际 5 张）。 | 实测：父提交 37 处分类 `BEL 8/BS 5/TAB 12/VT 6/FF 1/CR 1/ESC 4`；五文件 29/29；`git diff --numstat 24c573d1b 1ef6a2ebd -- doc/tasks` 显示 5 个目标文件 + GATE3 卡。陈旧数字来源：`verification/DOC-CTRLCHAR-FIX-1/fix-report.log:6-16`（首轮 819298e99 的 33 TAB/20 CR/37 files/44-44） | 收口时把标题/背景/§2/§修复表改为本轮实测值；或明确标注「§修复 表为首轮 2026-11-16 记录，已被 AC1–AC4/Closeout 取代」 | open |
| O-001 | P3（计数） | `doc/tasks/DOC-CTRLCHAR-FIX-1.md:122` | Resource Manifest 写「**2 个证据文件**已逐行登记」，但 Canonical Evidence 表有 **3** 行（EV-DC1-01/02/03，含 SOURCE_PIN `fix-report.log`）。 | 读卡 `:112-116` 与 `:122` | 改为 3 个（或写「2 个本轮 + 1 个历史 SOURCE_PIN」） | 记录 |
| O-002 | P3（清单） | `doc/tasks/DOC-CTRLCHAR-FIX-1.md:18-22` | `allowed_paths` 未列 `doc/reviews/DOC-CTRLCHAR-FIX-1-*.md`，而本次 Review 报告写到 `doc/reviews/`。报告写入由 DSH 派单明确授权，不构成越界；但释放清单不完整（GATE3 卡已列 review 路径，本卡未列）。 | 读 frontmatter `:18-22`；对照 `GATE3-SETTINGS-SHORTCUT-1.md:24` | 将 review 文件 pattern 补入 `allowed_paths`（或按 §4.1 的 evidence_dir 口径登记为交付豁免） | 记录 |
| O-003 | P3（head 口径） | `doc/tasks/DOC-CTRLCHAR-FIX-1.md:129` | Closeout 写「被审 head `1ef6a2ebd`」，本次独立复核的 `reviewed_head` 是 **`89b36c3f2`**。`89b36c3f2` 只增加文档/证据（`apps/**` 无改动、五张被修卡未再变），被审字节等价；但字段应区分。 | `git diff --name-only 1ef6a2ebd 89b36c3f2`（6 个 doc/verification 文件）；五文件 diff 为空 | 收口时写 `delivery_head: 1ef6a2ebd`、`reviewed_head: 89b36c3f2`，或把 Closeout 的「被审 head」改为复核 head | 记录 |
| O-004 | P3（证据标注） | `verification/DOC-CTRLCHAR-FIX-1/ctrlchar-scan-and-fix-2026-11-17.log:65-71` | 日志标题写「`git diff --stat（doc/tasks）`」，实际只列 5 文件 29/29；提交 `1ef6a2ebd` 的 `doc/tasks` 全量是 **38/38**（另含 GATE3 卡 9/9）。scope 本身正确，但标注易误读。另：`git diff --check 24c573d1b 1ef6a2ebd` 返回 2，原因是 `SIDECAR-SCHEMA-STALE-1.md:183` 的**既有**行尾空格（父提交同字节，非本卡引入）。 | `git diff --stat 24c573d1b 1ef6a2ebd -- doc/tasks` = 38/38；`git diff --check` EXIT=2；父/修复两版该行长度均 216、行尾均 1 个空格 | 日志标注「五文件」；`--check` 的既有空格建议另行登记（本卡禁止格式化，不应顺手改） | 记录 |

**P0 = 0，P1 = 0，P2 = 1。**

## 9. Architecture / Verification 结论

- **Architecture**：改动只在 `doc/tasks/**` 的字节层，不碰产品代码、契约、依赖、schema 或 `doc/plan/**` pin 目标。未引入新语义：37/37 均为控制字符→字母，长度不变。**PASS**。
- **Verification**：残留 0（HEAD 与工作树各 667 文件）；37/37 全部符合「控制字符→ASCII 字母」且长度不变；语义抽样全部恢复为有效 token（含 FEA-07 的 CR→r）；`check.ps1` ×2 PASS、`verify_pins` 18/18、证据巡检 FAIL 0。**PASS（带 P2 记录）**。

## 10. 结论与复审

**decision = ACCEPTED_WITH_FINDINGS**（模板口径 `approved`：P0/P1 = 0）。

**能否从 `in_review` 翻为 `done`：可以。** 理由：AC1–AC5 的实质内容均经独立实测复现（37/37、0 残留、pin 18/18、FAIL 0），AC6 由本报告交付；历史卡字节改动在授权范围内且不破坏任何 pin；唯一 P2 是**卡面标题/背景/§修复表残留首轮旧数字**，不影响修复本身成立。

**建议**：在同一个收口提交里把 R-001 的四处陈旧数字改为本轮实测值（该卡 `allowed_paths` 覆盖自身，改动 4 处文本，无风险）；否则 `done` 卡会永久保留「37 files / 44/44 / 33 TAB」与 AC 的「5 files / 29/29 / 12 TAB」并存的矛盾。P2 本身**不阻塞**收口。

**本复核不构成产品发布验收。**

## 11. 未审到 / 限制

- 未重跑 `clean_workspace.py --audit-declarations`（声明审计）；以 `four-piece-2026-11-17.log:21` 的记录为参考，未独立复现。
- 未重跑 2026-11-16 首轮修复（`fix-report.log` 的 33 TAB/20 CR）；它只是历史 SOURCE_PIN，不用于本轮 AC 判定。
- 未审 `doc/tasks` 之外目录的控制字符（FIX-2 已判「不修」，不在本卡范围）。
