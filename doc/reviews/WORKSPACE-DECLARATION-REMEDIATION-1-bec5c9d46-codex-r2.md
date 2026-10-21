---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R2
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: bec5c9d462fcecabcd48fcc7771e6710c7167132
implementation_head: a431d7084896abe5a824d478925d1dabc45802ef
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–H）

**判定：`changes_requested`。** F-02、F-03、F-04、F-07、F-08 的主要行为或证据通过核对；F-01 与 F-05 仍有可能绕过保护的输入边界，F-06 的残余报告也没有完整保留或准确反映 r2 结果。

- **A — 部分修复：**带路径分隔符、空格/CJK 的真实路径会解析，嵌入路径的 prose 会 fatal；但无分隔符的多词或 CJK 裸相对路径会被 prose 启发式跳过，即使它对应仓库顶层真实条目。
- **B — 通过，测试有缺口：**解析器不再按 instrumentation 文件名豁免；67 条清单都有 `path`、`sha256`、`reason`，豁免时重算 SHA。错误 SHA 不豁免，`.stdout.json` 真声明和截断 JSON 均 fatal。不过，测试没有单独覆盖“`.stdout.json` 且截断在声明 token 前”的组合情形。
- **C — 通过：**path-like generalized destination、声明 identity 列但 schema 不完整的表均 fatal；无 identity 列叙述表 warning；malformed 行仍为 `TABLE_ROW_ARITY`。
- **D — 部分修复：**真实审计里的 3 个 GB18030 文件为 warning、3 个含 NUL/UTF-16 文件为 `FILE_UNREADABLE`，计数与报告一致；但短于 64 bytes 的高控制字符 payload 可借 GB18030+CJK 条件通过。
- **E — 部分通过：**测试日志包含 shell、解释器、命令和 exit；Task 有 29 个证据 pin，Handoff 声称 29，数值一致。`RESIDUAL.md` 有 76 行且 code/file/locator 无漏项，但其中 8 条 `message` 被截断；`TRIAGE.md` 有 7 条处置与 r2 错误结果冲突。
- **F — 计数核对通过，快照证明不足：**before/after 都是 1858 declarations / 1264 roots；after 为 76 errors / 236 warnings，分类与数量相符；76 条残余的 code/file/locator 均对应 audit JSON，8 条仅 message 不完整。protection delta 记录 dropped=0，且其旧解析器与 `f0f19596f` 中的解析器一致。但 before 侧没有命令和输入快照指纹，无法独立验证“同命令/同快照”。
- **G — 部分通过：**80+17 tests、双 replay、manifest 和 pin 均有可核对的成功记录；AC1、AC3、AC4、AC6、AC7 仍有以下 Findings 中的缺口。diff 范围只在 `allowed_paths` 内；未见历史 Task 修改或删除文件。
- **H — 残余处理建议见第 4 节。**所有残余当前都应保持 fail-closed；不要为降低错误数增加 parser 豁免。

核对到的 after 错误分类为：`TABLE_SCHEMA_INCOMPLETE` 44、`DECL_GENERALIZED` 6、`DECL_DESTINATION_GENERALIZED` 6、`DECL_RELATIVE_UNRESOLVED` 6、`DECL_ENV` 4、`FILE_UNREADABLE` 3、`DECL_UNKNOWN_DISPOSITION` 2、`JSON_PARSE` 2、`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1、`DECL_DESTINATION_UNRESOLVED` 1，总计 76。

## 2. Findings

### Standards

未发现违反仓库 `AGENTS.md` 的硬性规范，也未发现值得单列的 code smell。

### Spec

1. **[P1] F-01：带空格/CJK 的真实单组件路径可能被跳过。**  
   `is_path_like()` 对不含 `/`、`\`、盘符、环境变量等语法的裸值返回 false；随后 `is_descriptive_value()` 将任何含 CJK 的值或至少两个词的值判为 prose，并在解析前由 `add_declaration()` 跳过。可是 `resolve_declared_path()` 本身支持解析实际存在的仓库顶层条目。因而，若顶层条目名为 `资料 文件` 或 `中文目录`，同名 preserve 声明可能只产生 warning、不进入保护索引。当前正例使用带斜杠的绝对路径，没有覆盖这个边界。见 [clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:783>)、[解析顺序](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:982>)、[顶层相对路径解析](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:914>)。建议新增“已存在的顶层单组件空格/CJK 路径”反例，并令其被保护或 fatal。

2. **[P1] F-05：短二进制可绕过控制字符比例拒绝。**  
   控制字节比例只在 `len(raw) >= 64` 时检查。只读内存探测使用 24-byte payload：20 个 `0x01` 控制字节加上可解为 CJK 的 GB18030 字节。`read_text()` 接受它并只发出 `FILE_ENCODING_LEGACY` warning；解析结果为零声明、零错误。现有二进制测试覆盖 NUL 和“不含 CJK”的 GB18030 payload，没有覆盖短、高控制比例、含 CJK 的组合。见 [read_text 控制字节检查](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:305>) 和 [当前二进制测试](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py:260>)。

3. **[P2] F-06：8 条残余 message 没有完整保留。**  
   `build_reports.py` 将超过 240 字符的 message 截断；audit JSON 中有 8 条原始 message 超长，RESIDUAL 对应内容不完整。因此，“逐条含原始 message”的声明不成立。行数和 code/file/locator 对照通过，没有发现漏项或造项。见 [build_reports.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py:331>)。

4. **[P2] AC1/F-06：TRIAGE 仍写着 r1 的 warning 处置。**  
   `TRIAGE.md` 第 47、49、51、53、55、57 行将 6 条 generalized destination 描述为 `DECL_DESTINATION_GENERALIZED warning`，但 after audit 中这 6 条均为 fatal error。第 58 行把 `ENV-BUNDLE-1-FU1/resource-manifest.json` 的 `DECL_UNKNOWN_DISPOSITION` 写成“叙述行跳过”，但它仍是 fatal。生成器的 `decision_for()` 仍硬编码这些旧处置。见 [生成器](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py:75>) 和 [TRIAGE.md](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md:47>)。

5. **[P2] F/AC7：before 审计证据不能证明同命令、同快照。**  
   [audit-before.log](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.log:1>)只有审计摘要和错误输出；before 命令、cwd、shell 未记录，exit 2 另存在文件。after 日志则记录了完整命令和 exit。before/after JSON 的扫描文件数量一致，但没有仓库根路径或输入文件清单指纹；数量相同不能证明内容快照相同。因此，“同命令/同快照”目前是声明，不能从证据独立复核。

6. **[P3] Handoff 的治理检查 warning 数与日志不一致。**  
   Handoff 写 `check.ps1` 为 7 errors、3 warnings；锁定日志显示 7 errors、2 warnings。见 [Handoff](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/handoffs/WORKSPACE-DECLARATION-REMEDIATION-1-a431d70.md:68>) 和 [governance-check.log](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/governance-check.log>)。

**轴线汇总：**Standards 0 项；Spec 6 项（P1 2 项、P2 3 项、P3 1 项），最高为 F-01/F-05 的 fail-closed 缺口。

## 3. AC1–AC7 判定

| AC | 判定 | 核对结果 |
|---|---|---|
| AC1 | PARTIAL | 163 条分诊数量有记录，但至少 7 条 TRIAGE 处置与 r2 结果矛盾。 |
| AC2 | MET（有测试覆盖缺口） | parser 只认显式 path+sha256 豁免，67 条清单字段齐全且无重复路径；wrong-sha 和重命名声明测试存在。`.stdout.json` 与 token 前截断未组合成独立夹具。 |
| AC3 | PARTIAL | 空格/CJK 绝对路径与嵌入路径 prose 反例成立；现有顶层单组件空格/CJK 路径可被 prose 启发式跳过。 |
| AC4 | PARTIAL | 实际扫描里的 3 个 GB18030 文件和 3 个含 NUL/UTF-16 文件结果符合预期；短高控制比例 GB18030+CJK payload 仍会通过。 |
| AC5 | MET | generalized destination、identity schema 不完整和 malformed 行保持 fatal；没有 identity 列的叙述表为 warning。 |
| AC6 | PARTIAL | 76 行与 audit JSON 的 code/file/locator 一一对应；8 条原始 message 被截到 240 字符。 |
| AC7 | PARTIAL | 80+17 tests 和双 replay 的锁定日志结果符合声明；protection delta 为 0 dropped。before 审计快照/命令未充分固定；`run_evidence.py` 外层 exit 0 没有独立 stdout/exit 文件，现有 `environment.json` 的 `failures=[]` 与 runner 逻辑支持该结论，但属于间接证明。 |

另核对到 Task 中 29 个 Canonical Evidence pin 均指向 `a431d7084` 且文件 SHA 匹配；Handoff 也写明 29 条。manifest 有 27 项，27 项 SHA 全匹配：差出的两项是清单自身（不自包含）和清单目录外的 parser 文件。

## 4. 残余裁定建议

76 条全部维持 fatal，当前不建议安全降级。分类与行动建议如下：

| 残余 | 建议 |
|---|---|
| `TABLE_SCHEMA_INCOMPLETE` 44 | **另立 Task。**逐表确认它是 identity 表还是叙述表，再补全必要列或明确更正内容；在修复合并并重审前保持 fatal。 |
| `DECL_GENERALIZED` 6 + `DECL_ENV` 4 | **另立 Task/用户裁定。**前者需要收窄到具体路径；后者需要权威环境值才能展开。保持 fatal，不增加根级或变量豁免。 |
| `DECL_DESTINATION_GENERALIZED` 6 | **另立 Task。**收窄 destination 或取得明确策略裁定；保持 fatal。 |
| `FILE_UNREADABLE` 3 | **另立恢复 Task。**保留原始字节，查找权威来源或确认其为二进制工件；未经验证不原地改写，保持 fatal。 |
| `JSON_PARSE` 2 | **另立 Task。**恢复合法 JSON；只有独立确认不含声明后，才可为精确 path+sha 添加豁免。保持 fatal，不能按文件名放行。 |
| 其余 11 条：相对路径 unresolved 6、unknown disposition 2、relative ambiguous 1、`TABLE_ROW_ARITY` 1、destination unresolved 1 | **另立定向 Task。**由来源负责人确认真实意图后更正文档或路径。`TABLE_ROW_ARITY` 可在确认多出的单元格含义后修正文档行；其余不能由 parser 猜测为 prose。修复前均保持 fatal。 |

不要为降低错误数而放宽 parser。所有内容修复都应在独立授权范围内进行，再重跑审计。

## 5. 运行证据

**本轮只读执行：**

| 命令/检查 | exit | 结果 |
|---|---:|---|
| `git status --porcelain=v1 --untracked-files=all`（指定 worktree） | 0 | 无输出；最终 HEAD 为 `bec5c9d462fcecabcd48fcc7771e6710c7167132`。 |
| `git diff --name-status f0f19596f..bec5c9d462fcecabcd48fcc7771e6710c7167132` | 0 | 仅 Task、Handoff、`clean_workspace.py` 与指定 verification 目录；全部在 `allowed_paths` 内，无删除项。 |
| `git diff --check f0f19596f..bec5c9d462fcecabcd48fcc7771e6710c7167132` | 1 | `REMEDIATION.md` 末尾有多余空行；不影响行为。 |
| 只读 JSON 分类与计数核对 | 0 | before 163/54，after 76/236；declarations 1858、roots 1264。 |
| 只读 audit/RESIDUAL 对照 | 0 | 76 行，code/file/locator 无缺项；8 条 message 不完整。 |
| manifest 与 Task pin SHA 校验 | 0 | manifest 27/27、Task pin 29/29 均匹配。 |
| `git diff --exit-code f0f19596f 1dc8a89445207e47a28a330610a925fa8514bf3b -- tools/governance/clean_workspace.py` | 0 | protection delta 使用的旧解析器与 `f0f19596f` 版本一致。 |
| Python `-B` 内存 `BytesIO` 二进制边界探测 | 0 | 24 bytes、20 个控制字节且含 CJK；只产生 `FILE_ENCODING_LEGACY` warning，无错误。 |

**本轮 NOT_RUN：**未重跑 80/17 tests、真实仓库 audit、`run_evidence.py` 或 `check.ps1`；审查使用了提交中的日志和 JSON。提交证据记录的新测试 exit 0（17/17）、既有测试 exit 0（80/80）、双 replay 各 15/15 REJECT、0 删除、18/18 source，after audit exit 2。`environment.json` 记录 `failures=[]`。审查期间未执行 Git 写命令、真实删除、push、GC 或 prune。

推荐下一步：由 `workspace-hardening` 修复 F-01/F-05 两个 fail-closed 缺口，重生成准确的 TRIAGE/RESIDUAL 并补齐审计基线指纹，再提交新的证据 pin 供 Codex 复审。