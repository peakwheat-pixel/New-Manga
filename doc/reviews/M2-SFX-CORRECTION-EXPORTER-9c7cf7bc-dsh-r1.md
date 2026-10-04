## Verdict

**changes_requested**

理由：AC1 识别语义（核心）经逐链推演与契约 §5.4 一致，fixture 矩阵与冒烟数字我全部独立复算通过；但 **P1-1（bbox 回退语义错）** 会在生产可达路径上静默产出错误 GT 框，且该错误已被 fixture/测试钉死为期望行为（不会红）。按协作协议 §6.8「P0/P1 未解决不能批准」，本轮不可批准。P1 修复面很小（1 行语义 + fixture/断言 + 冒烟摘要重跑），修完可直接复审。

---

## 审查范围与取证限制

- 覆审输入：Task 合同 AC1–AC6、`M2-C1` rev 1.4 §5.4、`experiments/M2-SFX-CORRECTION-EXPORTER/**`（scanner/samples/eligibility/export/fixture/cli/db + 46 用例）、`verification/M2-SFX-CORRECTION-EXPORTER/**`、Handoff、T1a 复用基底（schema/splits/dedup/atomicio/importers）、生产事实源（`entities.py`/`service.py`/`region_canvas.py`/`core_assembly.py`/`sqlite/schema.py`/`detection_sfx.py`）。
- **独立复算（PASS）**：fixture 14 链逐条推演 → 13 region（跳过 1 软删）/32 revisions/11 事件/8 存活/6 sfx 向/`machine_type_changes_excluded=1` → 正集 2（rgH/rgI）+辅助集 4（rgA/rgG/rgM/rgN）→ train 5 + challenge 1 → YOLO 6 labels，与 `fixture-smoke-summary.json` **逐项一致**；测试计数静态复算 = test_scanner 16 + test_samples 5 + test_eligibility 9 + test_export 10 + test_cli 6 = **46**（= green-run 46）；`dataset.yaml` names 逐字 = `SFX_CLASS_MAP`（`detection_sfx.py:137`，sfx id=2），label 首列实测 = 2；fixture 快照字段集与 `entities.snapshot_state()` 同构；origin/review_state/sfx_policy 字面量与生产 CHECK 约束一致（`sqlite/schema.py:248-267`）。
- **NOT_RUN（沙箱不可用，命令无法启动）**：`git log/status/diff`（delivery_head `9c7cf7bc`、提交链、零 src 变更、`diff --check`）、`pytest`、`selfcheck`、`--help` 的独立复跑。沙箱报 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，与 `doc/STATUS.md:102` 记载的 DSH 同类先例一致（残余项交集成方 git 关闭）。`green-run.txt`/`selfcheck.txt` 按原字节采信，并已用上述语义/计数复算交叉校验。

---

## 发现清单

### P1-1｜bbox 回退分支把生产 `bbox` 当 `xyxy` 读，静默产出错误 GT 框
- **位置**：`experiments/M2-SFX-CORRECTION-EXPORTER/sfx_correction_exporter/samples.py:92-97`（`_polygon_from_geometry` 的 bbox 分支）；被 `sfx_correction_exporter/fixture.py:93-97`（`geom(x0,y0,x1,y1)`）+ `tests/test_samples.py:103-115`（rgN 断言 `[[20,20],[50,20],[50,40],[20,40]]`）钉死为期望行为。
- **事实链**：生产唯一 bbox 生产者 `RegionGeometry.as_jsonable()` → `BBox.as_tuple()` = **`(x, y, width, height)`**（`src/domain/regions/entities.py:72-73,98-102`；`BBox.__post_init__` 要求 width/height>0；`BBox.covering` 同为 xywh `entities.py:75-84`；生产者 `region_canvas.py:99`、`core_assembly.py:1028`）。实现写 `x0, y0, x1, y1 = bbox`，把宽高当右/下角坐标。
- **触发可达**：settled 几何 `polygon` <4 点时走该分支——生产**允许 3 点 polygon**（`RegionGeometry.__post_init__` 仅要求 ≥3，`entities.py:94-96`；`normalized_to_page_geometry` 对 ≥3 点原样保留，`region_canvas.py:88`）与**空 polygon**（dataclass 默认 `()`、`from_jsonable` 容忍缺键 `entities.py:104-109`）。
- **影响**：错框静默入册。例：生产 bbox `(200,100,80,60)`（真实包络 `[200,100]-[280,160]`）→ 实现输出 `[[200,100],[80,100],[80,60],[200,60]]`（越界 + 自交）。用户自建 3 点多边形 region 经改标 → `geometry_confidence` 判 `complete` → **直接进正集**；`quality_note` 仍写「回退 bbox 四角包络」（不实）；T1a `validate()` 只校 ≥4 点，拦不住。
- **复现证据（入库产物）**：`training_data/sfx-corrections/labels/train/corr-pg1-rgN-r002.txt` = `2 0.312500 0.416667 0.781250 0.416667 0.781250 0.833333 0.312500 0.833333`（= `bbox=[20,20,50,40]` 按 xyxy 的结果；若按 xywh 应到 1.09375 越界），与 `tests/test_samples.py:114` 同一误读。
- **建议**：改用 T1a 现成 helper `sfx_data_infra.importers.bbox_to_polygon(x, y, w, h)`（`importers.py:54-55`，语义正是 xywh），或显式 `[[x,y],[x+w,y],[x+w,y+h],[x,y+h]]`；同步修正 `fixture.geom()` 的命名/语义与 rgN 期望值，并补一条「生产形态 bbox + 空/3 点 polygon」判别用例（如 `rgO`）。改后重跑 46 用例、重生成冒烟摘要（main/aux 计数不变，polygon 与 label 内容变）。

### P2-1｜YOLO seg 树把辅助集（partial）混入同一 `train` split，且未登记该决定
- **位置**：`export.py:236-237,250-252`（`write_yolo_export(out_dir, kept, …)`，`kept`=main+aux）、`README.md:29-35`、`fixture-smoke-summary.json`（`yolo_labels=6`）。
- **问题**：AC3 的「partial 不入正集、可选入辅助集」只在 manifest 双册实现；`dataset.yaml` 的 `train: images/train` 同时含 4 个 partial 样本，训练侧若走 AC4 宣称的「训练侧零适配」YOLO 直读路径，辅助集无法排除——「可选入」实为「默认入」，README 未登记。
- **建议**：三选一并落字：①`--yolo-scope {main,all}`（默认 main）；②辅助集写独立根（如 `aux/images/train`）；③显式登记「YOLO 树=全量，partial 过滤仅在 manifest 面生效」，并在 `dataset.yaml` 顶注一行。属训练口径取舍，建议连同 T1b 一起裁定。

### P3-1｜存活判据 (a) 是类型代理，误杀「撤销后 restore 回已改标 revision」的终态纠错，且无判别用例
- **位置**：`scanner.py:155-158`；登记于 `README.md:73-74`、`exporter-report.md:59-60`。
- **问题**：§5.4 的撤销 = `RestoreRegionRevision` 到改标前 revision；实现代理成「其后存在 `origin=restored` 且 `type==type_before`」。链 `m(speech)→u(sfx)@r2→restored(r1,speech)→restored(r2,sfx)` 的**终态就是纠正后的 sfx**，判据 (b) 已锁定终态 == `type_after`，此时 (a) 不再提供保护，只丢一个真阳性（且无别的事件补回）。属保守误杀（不产错 GT），但与自身 (b) 的「终态」口径不自洽，且该角例**仅存于散文**——`rgI` 是另一子形态（restore 目标类型 == `type_after`），T5b 集成后真库出现该形态不会红。
- **建议**：①把 (a) 收紧为「撤销未被后续 restore 至改标 revision 抵消」（按 `restored_from_revision_id` 解析目标 revision_no 后看终态）；或②保持保守但在 fixture 增 `rgO` 显式钉住期望，并在 CONSTANTS/报告写明「这是保守误杀，非 §5.4 唯一读法」。

### P3-2｜几何确认门问的是「链上曾有用户几何编辑」，settled 几何可能是机器几何却进正集
- **位置**：`samples.py:63-78`；入库证据 `training_data/sfx-corrections/manifest.json:89-174`（rgI：`annotation_status=complete`、`geometry_provenance=user_edited`，polygon `[250,10]-[300,50]` 即 r1 机器几何，用户 r3 的几何编辑已被 r4 restore 回退）。
- **问题**：AC3 门的意图是「导出所用几何是否经用户确认」，v1 规则问的是「链上是否存在用户几何编辑」。可辩护的读法（restore 至 r2 = 用户背书 r2 几何）**未在 `GEOMETRY_CONFIRM_RULE` 文本中登记**，当前表述看不出这层推理，等于把一个机器框送进正集且理由靠推断。
- **建议**：①在 CONSTANTS/README 明写「restore 至改标 revision = 用户背书该 revision 几何」及理由；或②改为按 settled 几何作者判定（回溯最后一笔改变几何的 revision 并沿 `restored_from_revision_id` 解析作者：`user`→complete、`machine`→partial）。两者都建议补一条判别用例。

### P3-3｜`partial` 与 T1a `ANNOTATION_STATUSES` 本体语义的映射理由未登记
- **位置**：`samples.py:63-78`、`export.py:236-237`；对照 `experiments/M2-SFX-DATA-INFRA/sfx_data_infra/schema.py:12,215-218`（`complete=人工精确; partial=人工核验但近似框; pseudo=模型产出未经人工确认`）。
- **问题**：本导出把「类型经人工确认 + 几何为机器产出」落 `partial`，与 `pseudo` 的解释空间相邻；选择可辩护，但报告/README 未给对齐 T1a 本体的一段理由，T1b/T2 侧会把 `partial` 读成「人工核验过框」。
- **建议**：README 阈值表下加 1–2 行：partial 判据 = 类型人工确认 + 几何机器产出，并显式声明不落 `pseudo` 的理由。

### P3-4｜Task/报告数字不自洽（分项计数与红态 EXIT）
- **位置**：`doc/tasks/M2-SFX-CORRECTION-EXPORTER.md:45,47`（「14 region 矩阵 **12 测试**」「AC3 PASS（**8 测试**）」）、`exporter-report.md:33`（「12 / 5 / 8 / 10 / 6」合计 **41 ≠ 46**）、`exporter-report.md:36` 与 Handoff `:37`（红态 `EXIT=1`）vs `evidence/red-run.txt:61`（`pytest EXIT=2`）。
- **依据**：实际 16/5/9/10/6 = 46（与 green-run 一致）。
- **建议**：按实际值回填分项与红态 EXIT；若「12」指 region 断言数，按协议 §6.12④ 在同一处给出总数与差值解释。

### P3-5｜Task 状态未推进到 `in_review`，AC 自评无注记
- **位置**：`doc/tasks/M2-SFX-CORRECTION-EXPORTER.md:5`（`status: ready`）、`:26-31`（AC 全 `[ ]`）、`:61`（Review：尚无）。
- **问题**：交付 head 已固定、测试与 Handoff 齐全，按协议 `09_COLLABORATION.md:65-71` 应为 `in_review`；AC 未勾选可接受，但缺「Owner 自评、待 Reviewer 确认」注记（沿 `M2-DOCTR-QUAL` r1 P3-6 的推荐写法）。
- **建议**：返修 commit 内改 `in_review` + AC 注记；`done` 与勾选由集成后收口。

### P4（不阻塞，建议随返修或集成落字）
| ID | 位置 | 内容 | 建议 |
|---|---|---|---|
| P4-1 | `evidence/red-run.txt` | 红态仅 collection error（5×ModuleNotFoundError），非断言级红；报告已披露 | 后续对 (a)/(b) 关键语义留一条反向探针 artefact（改坏规则→红） |
| P4-2 | `scanner.py:151` | `origin=imported` 排除分支无用例（rgE 仅覆盖 machine） | fixture 增一条 imported 类型变化 |
| P4-3 | `scanner.py`/报告 | 「乐观冲突/`expected_revision` 拒绝笔不产生事件」在读面**不可表示**（C4 零行写入，导出端只读已提交 revision） | 报告显式登记「该边界由写入端保证，导出端不可观测」，防误读为缺口 |
| P4-4 | `export.py:100-101`、`labels/train/corr-pg1-rgA-r002.txt` | fixture 几何越出页图（rgA/G/N `y1=50 > 48`）→ 归一化静默 clamp 到 1.0，label 与 manifest polygon 不一致 | fixture 改用页内几何，或 clamp 发生时登记 quality_note/计数 |
| P4-5 | `samples.py:120-121` | `provenance.correction.revision_no` 指事件笔，box 恒取链末笔 settled 几何；后续有几何变化时二者不对应 | 补 `geometry_from_revision_no` 字段（链 trace 已可解释） |
| P4-6 | `export.py:40-41` vs `sfx_data_infra/cli.py:296`、`manifest_summary.json:106` | 命名/摘要形状与 T1a 不一致（`manifest.full.json`+`manifest_summary.json` vs `manifest.json`/`manifest-auxiliary.json`+`export-summary.json`）；AC4/AC6「与 T1b 同构」在 T1b 交付前不可验证 | 登记待 T1b/T2 对齐，或提供 alias 落盘 |
| P4-7 | `fixture-smoke-summary.json:5` | `db` 路径 `verification/.../evidence/fixture-db/fixture-library.db` 不在交付树内；manifest `image.path` 同指该 ephemeral 目录 | 摘要内写可复现命令（`fixture.build_fixture_db(...)`）或注明临时性 |
| P4-8 | `eligibility.py:22-31`、`cli.py:15` | CONSTANTS 为纯文档常量（行为由 fixture 断言钉住，可接受）；`SEED_DEFAULT` 是 `splits.SEED_DEFAULT` 手抄副本 | 加一行注明；或延迟导入该常量 |
| P4-9 | `db.py:19` | URI 未做百分号编码（含 `?`/`#` 的库路径会破；含空格可用） | 与 `src/infrastructure/sqlite/connection.py:369` 逐字同构，非本 Task 新引入；可加注释 |
| P4-10 | `export.py:200-214` | 只跳过 region/页 软删除；软删除 book/chapter 的页仍导出 | 一句登记或补过滤 |

---

## 逐 AC 结论

| AC | 结论 | 依据 |
|---|---|---|
| AC1 事件识别 | **PASS**（附 P3-1/P4-2） | 「事件=第 j≥2 笔 `origin=user` 类型变化」与 §5.4 改标=新 revision/origin 恒 user 一致；`machine`/`imported` 排除并计数（rgE/计数=1）；`restored` 类型回退不构成事件（rgB/rgG）；软删跳过（rgL）；几何/文本/reading_order 天然非事件（rgC/D/J）；14 region 矩阵逐条断言 + `test_totals` 全量复算吻合；`review_state=UNREVIEWED` 断言在案。角例 (a) 保守误杀已登记但无用例（P3-1），`imported` 分支无用例（P4-2）。 |
| AC2 样本构建 | **PARTIAL** | 主路径正确：图引用=真实文件 sha256+尺寸、`cls="sfx"`、`correction.chain` 全链 trace、`SampleRecord.validate()==[]`、settled 几何与终态类型一致（rgA 断言 + 入库 manifest）。**但** `polygon<4` 回退分支按 xyxy 误读生产 xywh bbox → 错误框（P1-1）。 |
| AC3 资格判定 | **PASS**（附 P3-2/P3-3） | 许可继承（BJ13→`commercial_use_permitted_attribution`）/`user_library_source` 备案，全部 `blocking=false`（二次裁决全备案不阻断）；几何门 complete/partial → 正集/辅助集路由与冒烟一致；去重复用 T1a `find_duplicates`（exact+box-exact，册内优先，同图异框保留，空册/坏册四态登记）；四条阈值冻结于 `CONSTANTS` 且被断言。需补「settled 几何作者」与 T1a 状态本体的登记（P3-2/P3-3）。 |
| AC4 双形态导出 | **PASS**（附 P2-1/P4-6） | `manifest.json`（complete 正集）+`manifest-auxiliary.json`（partial 辅助集）均 `sfx-data-infra/manifest@1` 且过 T1a `load_manifest` 逐样本校验；YOLO seg 类别 id=2 + 多边形归一化 + `dataset.yaml` names 逐字 = `SFX_CLASS_MAP`（`bubble/panel/sfx/text`，T0 P3-6）；输出落 `training_data/sfx-corrections/`（gitignored，Git 仅进摘要）。YOLO 树含辅助集未登记（P2-1）。 |
| AC5 零 src / CLI / 只读 | **PASS**（NOT_RUN：未独立复跑） | `--help`/`selfcheck` EXIT=0（6/6 checks）见 `evidence/selfcheck.txt`；只读双层 = URI `mode=ro` + `PRAGMA query_only=ON`（与 `connection.py:367-374` 同构），UPDATE/DELETE 断言被拒（test_cli/test_scanner/selfcheck 三处）；缺库 `FileNotFoundError`→CLI EXIT=2 fail-closed；禁改路径无命中（**git 级未复算，NOT_RUN**）。 |
| AC6 与 T1b 产物互操作 | **PASS**（附 P4-6） | 导出物过 T1a `load_manifest`+`TrainingSetBuilder`：challenge 设计性隔离（train+val=5）、组原子性、`allowed_splits=("train","test")` 抛 `SplitAccessError`、注册表组继承（`inherited_groups`/`val=5`）、同 seed 指纹一致。本次在**无真实 T1a registry**条件下用 T1a 自身 `write_manifest` 造册做代理（格式保真），「与 T1b 同构」待 T1b 交付后验证（P4-6）。 |

---

## 推荐下一步

**Owner（ZCode，非本 Reviewer）在 `agent/zcode/M2-SFX-CORRECTION-EXPORTER` 分支做一次返修**：必修 P1-1（bbox→xywh 语义 + fixture/断言 + 冒烟摘要重跑），并择批闭合 P2-1/P3-1..P3-5；随后 DSH 于新 head 复审（P0/P1 未解决不得批准）。

可直接转发的指令：

> 在 worktree `G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode`（分支 `agent/zcode/M2-SFX-CORRECTION-EXPORTER`，交付 head `9c7cf7bc`）执行 DSH 非作者 Review 的返修：①**P1-1（必修）** `sfx_correction_exporter/samples.py:92-97` 的 bbox 回退改为生产语义 `(x, y, width, height)`——建议直接用 T1a `sfx_data_infra.importers.bbox_to_polygon(x, y, w, h)`；同步修 `fixture.py:93-97 geom()` 的语义/命名与 `tests/test_samples.py:103-115`（rgN）期望值，并新增「生产形态 bbox + 空/3 点 polygon」用例（如 `rgO`），重跑 `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q`（46 用例须全绿，含新用例数更新）与 `python -m sfx_correction_exporter selfcheck`，重生成 `fixture-smoke-summary.json` 与 `training_data/sfx-corrections/` 冒烟产物。②**P2-1**：裁定并落字 YOLO seg 树是否含辅助集（建议 `--yolo-scope main|all`，默认 main，或在 README/dataset.yaml 顶注显式登记）。③**P3-1/P3-2/P3-3**：在 CONSTANTS/README/报告登记 (a) 的保守误杀读法、settled 几何作者 vs 链上任一用户几何编辑的读法、partial 与 T1a 状态本体的映射理由；P3-1 建议补角例 fixture 用例。④**P3-4/P3-5**：修正 Task 与报告的分项测试计数（实际 16/5/9/10/6=46）与红态 EXIT（`red-run.txt` 为 2）；Task frontmatter 置 `in_review` 并把 AC 注记为 owner 自评。**禁止**：改 `src/**`、`tests/**`（仓库根）、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`；不得放宽 SQLite 只读铁律。完成后回填 Handoff r1 段与该 handoff 的 findings_disposition，交付新 head 供 DSH 复审。
>
> **集成方（代行 Codex）另需关闭 NOT_RUN 项**：`git diff --stat 69321db7..<rework head>` 范围审计（允许路径命中、`src/**`/`tests/**`/`doc/contracts/**`/`packaging/**`/`apps/**`/`doc/STATUS.md` 零命中）、`git diff --check` EXIT=0、以及返修后在集成 head 复跑 `pytest` 与 `--help`/`selfcheck` 的 EXIT 码留证；T5b 集成合并后补跑真库冒烟（`export --db <library.db>`，预期 `CORRECTIONS_EMPTY` 直至出现真实改标链）。
