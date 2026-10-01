静态复核完成（本轮同样遇到 `pwsh` 沙箱 `SetNamedSecurityInfoW failed (Win32 5): grantWrite`，全程只读：`read`/`grep`/`glob`，未执行任何命令，未读取 key 文件内容；结论均基于 worktree 实文件行号与 `review-fix.diff`）。

## Verdict

**changes_requested**

理由：r1 的 1×P1（R1）在**权威叙事面已按定案重写且正确**（`quality-report.md` §0/§4-F5/§5/§8/§9、runner export 注释与错误消息、`rerun-compare.json` note、handoff §7），R2–R15 逐条核对**均已闭合**；但**同一交付内的 Task AC 表 `doc/tasks/M2-TA3-B2.md:57` 未同步**，仍写着被定案否定的旧叙事（「K11 根因=remote endpoint 译文非逐位确定…渲染器忠实」）与旧计数（「独立复算 11/11」）。该行正是本轮要求重点核查的「Run2 译文进入 export」类表述，且它与本次被 Owner 改写过的 AC1/AC4 行同属一张 owner 回填表（`:51`），留白即为交付内自相矛盾。**修复成本为一行**，其余全部为 P3/P4 级。

---

## R1-R15 逐条复核表

| # | 结论 | 证据（worktree 实文件行号） |
|---|---|---|
| **R1** | **partial（P2）**：报告/runner/handoff 侧严格一致；Task AC3 行未改 | ✅ `quality-report.md:16`（AC3=「Run1 页面级渲染产物两次独立 run 逐位一致」）、`:144`（F5 重写）、`:151-163`（§5 机制前提+结论收窄+撤销 TA3-A 表述）、`:189`/`:199`（F5 移交裁决）；`run_qualification.py:537-544`（export=Run1 产物注释）、`:548-552`（`no translated render on disk (the page render happens during Run1…)`）；`rerun-compare.json:4`（region_id 重生成/按 reading_order 对齐 + export=Run1 渲染）；`doc/handoffs/…:74-83`（§7 R1）。全文已无「渲染器忠实」式论断（grep 命中仅剩历史段与撤销说明）。 ❌ **`doc/tasks/M2-TA3-B2.md:57`**：`BJ02 PASS（逐位一致）；K11 FAIL——根因=remote endpoint 译文非逐位确定（OCR 0/13 差异、译文 7/13 浮动，渲染器忠实）…独立复算 11/11 哈希一致` |
| **R2** | **closed** | `run_qualification.py:826-850`（按 case 合并写入、合并保留既有条目）；`rerun-compare.json:1-51` 3-case 与 summary **逐字段自洽**：BJ02 `region_count 5/5`、sha `5c74a4f0…` 双侧、size 8759037/8759037、rev `7f7626c0…`/`d7adba58…`、wall_s_second 158.09（对 `qual-BJ02.json:350-353,364`、`qual-BJ02.rerun.json:55,74-75,350-353,364`）；K11 13/13、`2c5dee05…`/`86ff9aa7…`、3064835/3064842、rev `17095606…`/`0c8ee003…`、wall_s 89.42/68.95（对 `qual-K11.json:52,692-694,707`、`qual-K11.rerun.json:52,692-694,707`）；K01 `region_count 0/0`、`export: {}`、`wall_s_second 2.43`（对 `qual-K01.rerun.json:52,77,89`）。K01 `match=false` 与 runner `:813` 的 `bool(sha_first) and …` 语义一致（空 sha → false），非手改 |
| **R3** | **closed** | `quality-report.md:140`（同页 sha256 实证 docTR 15/7 vs ogkalu 0、「适配器级机制尚无证据」、建议 A 前置可观测值）；`phase2-plan.md:24`（docTR→ogkalu+chiqui7 已同步）。残留旧表述仅在 handoff §1-6（`:43`，被 §7`:76` 声明覆盖） |
| **R4** | **closed** | `quality-report.md:47`、`:141` 改推断口径（尺寸边界 345.6/264.5/265.0 MiB + `importing.py` 无设置点 + 原始 Qt 日志未归档）；全 worktree grep 已无 `QImageIOHandler`/`exceeds the current allocation limit` 字面原文 |
| **R5** | **closed（P4 备注）** | `cer-summary.json:5`（denominator=13 中取 6，含 ko7/ja6 结构）、`:95-…`（`excluded[]` **13 行**：ja6+ko7，与 `cer-regions.csv:52-57,59-60,65-70` 的 13 条非自动行一一对应）、`:170-172`（alignment_method 补 UNALIGNED/empty-OCR）；`measure_cer.py:170-217,295-296,315`；`quality-report.md:82,91,108`（下偏统计量+短串重复+**示意**反事实）。反事实算术复核成立：自动 6 值 `0,0,0,0.1111,0.2727,0.3333` → median 0.0556 ✓；并入 ko 可计被剔 5 值（0.5/1.0/0.45/0.6897/1.0）→ 11 值 median=0.3333 ✓「≈0.33 量级」。K11:65069961（真 OCR 失败 hyp_cer=1.0）与 df871de5（1.0）在案 ✓；`quality-thresholds.md:76,197` 同步 ✓ |
| **R6** | **closed（P4 备注）** | 56 落 `quality-report.md:14`、`doc/tasks/M2-TA3-B2.md:55`、handoff 以 §7`:76` 声明替代旧数；per-case 合计 5+2+3+1+17+3+11+8+1+5=**56** ✓，48=56−8 ✓；K19 1200×1660（`qual-K19.json:23-24,41-42`）✓；SFX 9=8 BJ06+1 K11（`cer-summary.json:266`、`cer-regions.csv:70`）✓；§1.1a 十项构成 ✓（与 `qual-report.json` K01/K02/K04/K05/K08/K19+K07/K09/K10 + 复跑集合 1 一致）。备注：同行的「11/11」属 R7 未回填（见新问题 N1） |
| **R7** | **closed（逻辑正确；P4 建议）** | `verify_exports.py:50-92`：按 `qual-*.json` 逐个读 `export.pixel_path` → 实算 sha256/size → 与 summary 字段比对 → 记录 `pixel_relative_path`/`rerun`（`:67` 由 `rerun_suffix` 判定）；`:54` 排除 `qual-report*`；`:90` `all_match` 含 size；覆盖 `.rerun` ✓（`export-hash-recompute.json` 13 条=11 首跑+BJ02.rerun+K11.rerun，`all_match:true`）。与 manifest 交叉一致（BJ02/K11/K11.rerun 的 sha/size 三处互证） |
| **R8** | **closed** | `pixels-manifest.json`：`n_files:126` 与 `"path"` 实测 **126** 条 ✓，`total_bytes:87573189`（83.5 MiB，表述 84MiB 为进位）；组成=13 export + 113 crops（56 ja 主 + 26 K11 目录含 F6 前残留 + 5 BJ02.rerun + 26 K11.rerun）✓；出库理由修正 `quality-report.md:27` + `run_qualification.py:37-46` docstring（仓库外兄弟目录、与 .gitignore 无关）✓ |
| **R9** | **closed** | `quality-thresholds.md:168`（行内 superseded-pending）、`:171`（§5 节尾注）、`:204`（§7 第 10 行）；阈值数值 0.10/0.15/0.20/0.25 未动 ✓ |
| **R10** | **closed** | `quality-thresholds.md:64`（在 `### 2.2` 段内，Owner 标注「§2.2」正确）加 ep20=352/ep04=472 修正注 ✓；`phase2-plan.md:192` 回退「数万 token 量级」并登记越界 ✓ |
| **R11** | **closed** | `quality-report.md:21` 改 estimated（93–104 请求推导 + 「token 量无计量证据」+ usage 落盘登记为候选）✓；全文无 `<10 万` 残留 |
| **R12** | **closed** | `quality-report.md:17`（AC4 行并列挂 n<30 + SFX=0）、`:126`（§3.2）、`doc/tasks/M2-TA3-B2.md:58` ✓ |
| **R13** | **closed（含 P4 漏点）** | `run_qualification.py:109-131`（`scrub_secrets`+`dump_json`）；**唯一 JSON 序列化路径**成立——全文件仅 `:131` 一处 `json.dumps`，落盘点 `:766`/`:808`/`:841-850`/`:857` 全走 `dump_json` ✓；traceback（`:611`/`:744`）随 summary/report 落盘故被覆盖 ✓。`translate_probe.py:83-99`+`:322-325`（record 落盘前 scrub）✓；`quality-report.md:19` 加「READY=endpoint-only 不等于生产 MISSING_CREDENTIAL 语义」✓。**漏点**：stdout/stderr 未 scrub——`run_qualification.py:278`（`stage()` 把 extra 含 error 内容打到 stdout）、`translate_probe.py:317`（`record['error']` 原文打 stderr，而文件版本已 scrub），若操作者重定向日志（本仓已有 transcript 落盘先例）则回显路径重新打开；另 `verify_exports.py` 无 scrub（其只读 export 字段，无密风险，可接受） |
| **R14** | **closed（集成方定案）** | handoff §7`:150-152` 登记为 not-owner-scope ✓；按本轮前提 1（merge-base=521d0bdd、线性链、两口径 53 文件）无缺口。**回填动作仍在集成方**（`doc/tasks/M2-TA3-B2.md:6,13,51` 仍 `delivery_head: 3c8801b7`/`base_commit: 521d0bdd`） |
| **R15** | **closed** | `build_worksheets.py:22-24`（30 short requests→batches of 10; n=26→3 batches）；`measure_cer.py:1-2`（docstring 不再谎称产 n=30 工作表）、`:24-32`（指向 build_worksheets 并说明死代码已删）、`:44-47` 分层常量已删且 experiment 内无残留引用（`TINY_TAG_CASES` 等仅存于 build_worksheets 的实际使用点 `:45-58`）✓ |

**复核要求 6（F5/建议 A-B 的定位）**：✅ 已正确移交——`quality-report.md:163`（「作为 F5 裁决点移交 Codex/用户（§8/§9），本报告不代裁」）、`:189`、`:199`、`quality-thresholds.md:171`（「本文档不做单方改写」）、`doc/tasks/M2-TA3-B2.md:61`（A/B 与 F4/F5 交 Codex 裁决）。F5 候选方向（reading_order 译文相似度）均以「候选」措辞出现，未见 Owner 自裁口径。

---

## 回潮与新问题

**回潮：范围与禁改面**（要求 2）——**PASS**。`review-fix.diff` 15 文件全落允许面（`doc/tasks/M2-TA3-B2.md:37` 授权 `experiments/M2-TA3-B/**`、`verification/M2-TA3-B/**`、`doc/tasks/M2-TA3-B2.md`、`doc/handoffs/M2-TA3-B2-*.md`）；`src/**`、`tests/**`、`requirements.txt`、`packaging/**`、`apps/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`、`doc/STATUS.md` 零出现；`qual-*.json`、`qual-report.json`、`cer-regions.csv`、`translate-probe.json`、`svg-gt-manifest.json`、三份 worksheet 均不在 diff 中。handoff §1-6 未改（`:12` 仍写 53，`§7:76` 显式声明「以本节修正为准」），仅追加 §7 ✓。

**新问题（按严重度）**

- **N1｜P2｜Task AC 表未同步（= R1 partial / R7 未回填）**：`doc/tasks/M2-TA3-B2.md:57`。同一张表 `:55`（56/§1.1a）、`:58`（AC4 双缺口）已被本轮改写，唯 AC3 行保留被否定的根因叙事与「11/11」旧计数。
- **N2｜P3｜新加的 §1.1a 行号引用已失效**：`quality-report.md:58` 引 `run_qualification.py:725-726,795-796`；实际 case 级失败累加在 `:764-765`、复跑集合级在 `:851-852`（R13/R2 的插入把原行号各推后约 25/56 行）。
- **N3｜P4｜handoff 剩余回潮点未被 §7 覆盖声明兜住**：`handoff:39` 仍写像素出库理由是「`.gitignore` 在禁改面」（R8 已否定），而 §7`:76` 的替代声明只枚举了「F1/F5/数字表述」；§7 的 R8 条目（`:117-119`）也未提 handoff §2 的旧措辞。
- **N4｜P4｜新脚本未进复现命令**：handoff §2`:33-36` 的「哈希复算」链路缺 `python experiments/M2-TA3-B/verify_exports.py`，manifest/recompute 两产物无法按文档复现。
- **N5｜P4｜合并写入的两处健壮性/持久性缺口**：`run_qualification.py:830-838` 若既有 `rerun-compare.json` 仍是**旧数组格式**，`existing_compare.get(...)` 会抛 `AttributeError`（只捕获 `JSONDecodeError/OSError`）；且 `:843-847` 重写只输出 `task/updated_at_utc/cases`，会把 Owner 新增的 `note` 方法学登记（`rerun-compare.json:4`）以及重跑 case 的 `rev/size/verdict/relative_path` 手填字段丢弃。
- **N6｜P4｜反事实口径的工件内标注可再明确**：`cer-summary.json` 仅有字段名 `hypothetical_cer_if_scored` 与 denominator 文案；measure_cer docstring 的「多元素 GT 是拼接、只作上界不作测量」未落进工件，而 `quality-report.md:108` 有该限定。反事实算术本身正确（见 R5）。
- **N7｜P4｜stdout/stderr 未 scrub**：`run_qualification.py:278`、`translate_probe.py:317`（见 R13 漏点）。
- **N8｜P4｜phase2-plan 未加 superseded 交叉注**：`phase2-plan.md:17,182-183` 仍写「哈希一致、确定性复跑一致」（r1 R9 只点了 thresholds，故非欠账，属可顺手收敛）。
- **N9｜观察｜run 派生工件被改写（非篡改）**：`cer-summary.json`、`svg-alignment-trace.json` 出现在 diff 中——前者按 R5 要求**新增** `excluded[]`/denominator/alignment_method；后者**仅** 3 处 `alignment_method` 描述串变化，`trace[]` 证据数组逐条未动；`cer-regions.csv` 与所有 `qual-*.json` 未被触碰。「历史 run 产物 diff 中不得出现」的字面口径未完全满足，但改动方向与 R5 指令一致、无证据字段改写。

---

## NOT_VERIFIED（集成方运行时项）

1. **git 事实面**：tip=`7922a3fc` 的 `git status --porcelain` 干净、`git diff --check` EXIT=0、`git diff --name-only 69137837..81e5ad81`/`521d0bdd..HEAD` 各 53 文件、禁改面专项 diff 为空（本轮为 worktree 内容审查，未读 commit 对象）。
2. **R1 机制前提与本文复核的同一性**：BJ02/K11 export PNG 的 sha256 与 mtime 事实（前提 2）由集成方给定，我未实算；建议集成时把两个文件实算结果与 `pixels-manifest.json:15-19`、`export-hash-recompute.json` 三处并排留档。
3. **`verify_exports.py` 复跑**：`all_match=true`、13 条记录与 `n_files=126`/`total_bytes` 是否可复现（哈希无法静态重算；要求像素外部树存活）。
4. **R4 一级证据补齐**：复跑 K09 并把 importer 未截断 per-file `error/detail` 落盘（否则 F2 维持「推断」口径）。
5. **R11 计量**：请求数 93–104 的间接推导与 token 量（产物无 usage 字段，无法核对）。
6. **R14 回填**：`doc/tasks/M2-TA3-B2.md:6,13,51` 与 handoff base 元数据按定案（merge-base=521d0bdd、线性链、Task 文件两区间均变动）回填 delivery_head/base_commit。
7. **集成门禁**：`pytest tests/providers tests/m2_acceptance tests/core -q -rs` + 两 worktree diff 范围核对。
8. **用户侧**：三份工作表与 G2 50 行 GT 审核（非本 Task 关闭条件）；像素外部树在审核期保持存活。

---

## 推荐下一步（一句）

请 Owner 在允许面内做一次一次性文档回填：改 `doc/tasks/M2-TA3-B2.md:57`（AC3 行按 §5 定案重写并把 11/11 改为 13/13），顺手修 `quality-report.md:58` 行号（→`run_qualification.py:764-765,851-852`）与 handoff §2/§39 两处回潮措辞，然后交集成方按上述 NOT_VERIFIED 清单跑运行时项并入。
