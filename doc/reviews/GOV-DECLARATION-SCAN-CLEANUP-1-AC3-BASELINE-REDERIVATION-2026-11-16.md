# GOV-DECLARATION-SCAN-CLEANUP-1 · AC3 前置评估：154 条声明债务的 B1/B2/B3 重推（2026-11-16，R16）

- 作者：DSH（Lead），本轮以「评估」身份撰写；**未**改动 `GOV-DECLARATION-SCAN-CLEANUP-1` 卡面任何 AC 勾选与标记。
- 判据来源：`doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md` AC3 / AC6；分类口径：`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-RULING-ABC-2026-11-16.md` §Ruling B。
- 复现命令（在 `G:\CODEX\New Manga` 下）：

```powershell
python -B tools/governance/clean_workspace.py --audit-declarations --out "G:\CODEX\New Manga.workspace\tmp-dsh\decl-audit-2026-11-16c"
```

## 1. 依据实测的基线（不要再用 Ruling B 的 166 条旧数）

| 指标 | 2026-11-16 R15 记录 | **本轮实测（head `45af57007`）** | 说明 |
|---|---|---|---|
| errors | 154 | **154** | code 分布逐项一致 |
| warnings | 732 | **732** | — |
| declarations | 6729 | **6751** | +22：本轮 MAINT-1 新增三节（Canonical Evidence / Resource Manifest / Closeout Record）|
| protected_roots | 5585 | **5589** | +4：同上，且**零新增 error**（本轮曾因三格写成 `%TEMP%`/`*`/描述性 disposition 而多出 3 条，已修净，见 `doc/tasks/MAINT-1-RELEASE-MONITOR.md` 轮次 36） |

> 注：本报告自身入库后再实测为 **6755 declaration / 5593 protected root / 154 error / 732 warning**
> （报告里列举的 8 份资源清单路径被扫描器登记为保护声明，故 +4/+4，**error 不变**）—— 开工时应以
> 「开工当轮实测」为基线，本表用于说明来源与量级。

code 分布（154）：`TABLE_SCHEMA_INCOMPLETE` 53 / `DECL_RELATIVE_UNRESOLVED` 26 / `DECL_ENV` 16 / `DECL_GLOB` 16 /
`DECL_DESTINATION_UNRESOLVED` 11 / `TABLE_DELIMITER` 10 / `DECL_UNKNOWN_DISPOSITION` 8 / `DECL_TRAVERSAL` 7 /
`JSON_PARSE` 2 / `TABLE_ROW_ARITY` 1 / `DECL_BARE_NAME` 1 / `DECL_RELATIVE_AMBIGUOUS` 1 / `FILE_UNREADABLE` 1 /
`DECL_MISSING_SOURCE` 1。

## 2. 按 Ruling B 的「code → 桶」冻结映射重推（不重新发明分类）

| 桶 | 判据（冻结） | 本轮 code 组合 | 数量 |
|---|---|---|---:|
| **B1** 历史形态（解释层绑定，不改字节） | 旧形态产物，可绑定为非声明源 | 53 + 10 + 1 | **64** |
| **B2** 真实缺陷（先判活 pin，再决定修/登记） | 声明写错/失效 | 26 + 16 + 16 + 11 + 7 + 1 + 1 + 1 | **79** |
| **B3** 扫描器规则（出规则裁定） | 规则过严/过宽 | 8 + 2 + 1 | **11** |
| 合计 | — | — | **154** |

> Ruling B 原文的 64 / 86 / 16 是按 166 条算的；本表用**同一 code 映射**套到 154 条上得到 64 / 79 / 11，差额集中在
> `DECL_RELATIVE_UNRESOLVED`（27→26）、`DECL_ENV`（20→16）、`DECL_DESTINATION_UNRESOLVED`（12→11）、
> `DECL_RELATIVE_AMBIGUOUS`（2→1）、`DECL_UNKNOWN_DISPOSITION`（10→8）、`FILE_UNREADABLE`（4→1）。

## 3. B2 的硬约束实测：12 条被「活 pin」钉死 ⇒ 只登记、不修改

下列 8 个资源清单 JSON 内的 12 条 B2 错误，**每一份都被其终态卡的 `## Canonical Evidence` 以 sha256 + commit 钉住**
（实测：以 `git cat-file blob <commit>:<path>` 重算的 blob sha256 与卡面登记值一致）：

- `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json`（卡 `doc/tasks/FEA-07-RESIDUAL-2.md`，EV-R4A-12，`status: done`）
- `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json`（EV-R4B-10，`done`）
- `verification/FEA-11-AC4-GAPS-1/RESOURCE-MANIFEST.json`（EV-FEA11GAPS1-RESOURCE，`done`）
- `verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json`（EV-08，`done`）
- `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json`（EV-7，`done`）
- `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json`（EV-18，`done`）
- `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json`（EV-10，`done`）
- `verification/FEA-15-ACCEPT-1/resource-manifest.json`（SRC-26，`closed_with_limitations`）

**结论**：这 12 条**不能**用「改数据」的方式消除（改一个字节就使该卡证据 pin 失效）。要归零只剩两条路：
(a) 走 B1 式**解释层绑定**（把该 JSON 的声明源身份绑定为非声明/已保全，逐文件 + 行/origin + raw sha）；
(b) 等 pin 失效（需重开终态卡，代价远大于收益，不建议）。
⇒ **AC3 开工前必须先出一道书面裁定选定 (a)**，否则 AC3 的「`errors` 单调下降至 0」在字面上不可达。

## 4. 其余 67 条 B2：全部在 `doc/tasks/*.md` 的历史卡 Resource Manifest 表

- 分布：约 **46 张**历史卡（每张 1–3 条），全部位于卡内 `## Resource Manifest` 表或等价表；
- 典型形态：`source_path` 写 `..\New Manga.workspace\tmp`（TRAVERSAL + DESTINATION_UNRESOLVED 各 1）、
  写 `%TEMP%`/`$env:...`（ENV）、写 `verification/X/**`（GLOB）、写裸名或描述性文本（RELATIVE_UNRESOLVED / BARE_NAME）；
- **这些卡未被任何证据 pin 引用**（实测：无 Canonical Evidence 行指向 `doc/tasks/*.md`），故可修；
- 但**需要 scope 冻结**：修 = 改历史卡字节（约 46 张）⇒ 必须在 AC3 的 `allowed_paths` 里显式列出 `doc/tasks/*.md`，
  并写清「只改 Resource Manifest 的 source_path/disposition 单元，正文与其他表一律不动」。

## 5. B3 11 条：是规则问题，不是数据问题

- `DECL_UNKNOWN_DISPOSITION` 8：多为 `PRESERVE`（`DISPOSITION_RE` 只接受 `PRESERVE_[A-Z0-9_]+`）、
  `DELETE_SAFE（可重建）`（带括号说明）这类**裸/带修饰 disposition**；
- `JSON_PARSE` 2：两份不可解析 JSON（需定位后决定「修文件」还是「进 `non-declaration-json-exceptions.json`」，后者须 SHA-256 绑定）；
- `FILE_UNREADABLE` 1：单个不可读文件（需定位：权限 or 已删除）。
⇒ 逐 code 出一段规则裁定 + 最小代码改动，**不改任何历史字节**。

## 6. 建议的开工顺序与估时（供 DSH 决策，不是承诺）

1. **裁定先行**（0.5 轮）：出书面裁定，明确 ① 12 条活 pin B2 走解释层绑定；② B3 三个 code 的规则口径；
   ③ AC3 的 `allowed_paths` 扩到 `doc/tasks/*.md`（仅 Resource Manifest 单元）。落 `doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-*.md`。
2. **B3 批**（1 轮）：规则裁定 + 代码改动 + 每条规则的负例测试 ⇒ errors 154 → 143，`protected_roots` 不得下降。
3. **B1 批**（1–2 轮）：64 条逐 origin 绑定（含 12 条活 pin JSON）⇒ errors → 79。
4. **B2 批**（2–3 轮）：67 处逐单元修数据，按卡分批提交，每批后重跑 audit 记录单调下降 ⇒ errors → 0。
5. **AC6 集成复验**（1 轮）：固定 head + 上下文独立复核 + 前后两轮 JSON 回填。

**风险提示（三条）**：
- `protected_roots` 现在是 **5589**，AC3 写的是 `>= 5582`（R15 值）。修 GLOB/ENV 类声明时**很容易让 protected_roots 变小**
  （把 `verification/X/**` 改成 `verification/X`、把 `%TEMP%/*` 删除），必须在每批后比对，宁可用绝对路径保留保护面。
- 改 46 张历史卡会触发 `TASK_LEDGER`/声明审计的连锁变化，必须每批 `check.ps1` + audit 双跑。
- 本报告的 154 基线是 **head `45af57007`** 的值；若后续轮次再改 doc，基线会漂移 ⇒ 开工第一件事是重测并冻结新基线。

**结论（一句话）**：AC3 **值得做，但不能直接开工** —— 先出「活 pin B2 走解释层绑定 + B3 规则口径 + scope 扩到 doc/tasks」这一道裁定，
之后 4–6 轮可把 154 降到 0；否则第一轮就会卡在 12 条不可改的 pin 上。
