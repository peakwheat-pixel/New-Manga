# M2-SFX-CORRECTION-EXPORTER（T5c）实现报告

- Author：ZCode（Owner 实现 agent）
- base_commit：`69321db7`（Task 合同登记）；claim @ release `1b765007`
- 分支/worktree：`agent/zcode/M2-SFX-CORRECTION-EXPORTER` @ `G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode`
- Reviewer：DeepSeek Harness（非作者）
- 环境：dev venv `T1.1.1-impl-py312`（Python 3.12.3，pytest 9.1.1）
- 纪律：零 src 修改；SQLite 只读；依赖零新增（sqlite3 stdlib + 既有 PIL + 复用 T1a sfx_data_infra）

## 1. 交付范围

`experiments/M2-SFX-CORRECTION-EXPORTER/**`（包 `sfx_correction_exporter` + tests + README）、
`verification/M2-SFX-CORRECTION-EXPORTER/**`（报告+摘要+红绿证据）、Task/Handoff 回填。
导出物落 `training_data/sfx-corrections/`（gitignored 外部树，Git 只进摘要）。

模块：`db.py`（只读 opener）、`scanner.py`（AC1）、`samples.py`（AC2）、
`eligibility.py`（AC3）、`export.py`（AC4+管道）、`fixture.py`（fixture 库）、
`cli.py`/`__main__.py`（AC5）。

## 2. AC 对照

| AC | 结论 | 证据 |
|---|---|---|
| AC1 事件识别 | PASS | `pytest tests/test_scanner.py`（17 测试全绿）；fixture 15 region 混合链逐条断言（基本纠错/被撤销/纯几何/纯文本/机器改标/二次改标取代/撤销再纠错/用户自建/几何编辑后 restore/纯顺序/非 sfx 向/软删除/BJ13 映射/纯 bbox/撤销后 restore 复活保守角例）；判据=契约 §5.4（改标 origin 恒 user、撤销=restored 溯源、review_state=UNREVIEWED、机器改标非事件） |
| AC2 样本构建 | PASS | `tests/test_samples.py`：T1a SampleRecord 逐条 validate()==[]；图引用=真实文件 sha256+尺寸；框=settled 几何+cls=sfx；complete/partial 落地；provenance 含 correction.chain 全链 trace（revision_no/origin/region_type 序列可回放） |
| AC3 资格判定 | PASS | `tests/test_eligibility.py`：许可继承（BJ13→commercial_use_permitted_attribution）/user_library_source 备案，全部 blocking=false（二次裁决全备案不阻断）；几何门 complete/partial 与辅助集路由；与 T1a 已册样本 exact+box-exact 去重（同图同框剔除、同图异框保留、空册/坏册四态登记）；阈值冻结于 `eligibility.CONSTANTS` |
| AC4 双形态导出 | PASS | `tests/test_export.py` + fixture 冒烟：manifest.json（正集 complete）+ manifest-auxiliary.json（partial 辅助集）均为 `sfx-data-infra/manifest@1` 容器（T1a atomicio 原子写）；YOLO seg labels（sfx id=2 归一化多边形）+ dataset.yaml names 逐字=SFX_CLASS_MAP；输出 `training_data/sfx-corrections/` |
| AC5 CLI/只读 | PASS | `--help` EXIT=0；`selfcheck` EXIT=0（6 checks：只读写拒/识别语义/schema 互操作/class_map 锚定/去重 sanity/manifest 往返）；只读铁律=URI `mode=ro`+`PRAGMA query_only=ON`（UPDATE/DELETE 均被拒，缺库 fail-closed 不静默创建） |
| AC6 互操作 | PASS | 导出 manifest 过 T1a `load_manifest`（逐样本 schema 校验）→ `TrainingSetBuilder` 消费（challenge 设计性隔离、组原子性断言、`allowed_splits` 含 test 时抛 `SplitAccessError`）；组继承：注册表组直接继承 split，challenge case 优先 |

## 3. 测试与红绿证据

- 用例数（r1 返修后实测）：**50**（test_scanner 17 / test_samples 7 / test_eligibility 9 /
  test_export 11 / test_cli 6，含 parametrize 无）。
  r1 交付时点分项误记为「test_scanner 12 / test_samples 5 / test_eligibility 8 /
  test_export 10 / test_cli 6 = 41」（自相矛盾于总数 46）；r1 实际分项 =
  **16/5/9/10/6 = 46**（DSH r1 P3-4 核正）；r1 返修新增 rgO 判别用例、rgO2 保守角例、
  rgO3 几何门判别、--yolo-scope 用例后为 17/7/9/11/6 = **50**。
- **红态**：实现落盘前 `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` →
  **5 文件 collection error，`ModuleNotFoundError: No module named 'sfx_correction_exporter'`**，
  pytest **EXIT=2**（evidence/red-run.txt 尾行；r1 报告此节曾误记 EXIT=1，P3-4 修正）。
- **绿态**：r1 返修后同命令 **50 passed, 0 failed**，EXIT=0（evidence/green-run.txt）；
  r1 交付时点为 46 passed。
- 中途修复（红→绿之间的实现缺陷，均由测试捕获）：fixture 重复插入 book/chapter
  （UNIQUE 约束）；`machine_type_changes_excluded` 误计 restored 类型回退；
  `__init__.py` REPO_ROOT 少上一层导致 cases.json 解析不到；`quality_note` 未写入 provenance。

## 4. 冒烟

1. **fixture 库全流程**（真实 SQLite 文件，生产 v1–v4 冻结 DDL；r1 返修后重生成）：
   扫描 14 region（15 - 1 软删除）/36 revisions → 12 事件（8 存活，其中 6 sfx 向；
   rgO2 角例事件 undone 不存活）→ 正集 2（complete）+ 辅助集 4（partial，
   **main/aux 计数与 r1 相比不变**，仅 polygon/label 内容随 bbox 语义修复变化）→
   split train=5 + challenge=1 → YOLO 2 labels（`--yolo-scope` 默认 main=仅正集；
   all=6）→ **EXIT=0**。摘要：
   `verification/M2-SFX-CORRECTION-EXPORTER/fixture-smoke-summary.json`。
2. **主仓库真库**（`C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db`，
   只读探测确认含 regions/region_revisions 表、regions=0——T5b 未集成，真库无改标事实）：
   **CORRECTIONS_EMPTY=expected，EXIT=0**，db_readonly=true。摘要：
   `verification/M2-SFX-CORRECTION-EXPORTER/real-db-smoke-summary.json`。
   T5b 集成后真库冒烟由集成方补跑（合同「依赖、风险与阻塞」节预告）。

## 5. 冻结语义登记（实现裁定，供 review 核对）

- 存活规则 (a)：其后存在 `origin=restored` 且 `region_type==type_before` 的 revision
  即撤销（无论 restored_from 指向）；(b)：链末笔类型必须等于 `type_after`。二者与
  fixture 矩阵逐条对应（rgB/rgF/rgG/rgI 是关键判别用例）。
- 角例（保守不采，DSH r1 P3-1）：撤销后经 restore 至已改标 revision 复活纠错态 →
  事件仍视为已撤销（restore 不是 retype，不产生事件）。此为**保守误杀，非契约 §5.4
  唯一读法**——按「用户 settled 终判」读法该纠错已复活，应计入；现按保守读法丢弃，
  已登记 `CONSTANTS["SURVIVAL_UNDONE_RULE"]` 并由 fixture rgO2 显式钉住期望
  （undone、不存活），语义重裁定留 T2。
- 几何确认门读法（DSH r1 P3-2）：restore 至改标 revision 读作用户背书该 revision
  几何（用户主动回退到该状态）；现实现不单独以 restore 背书触发 complete——
  `geometry_confidence` 判别用例（无先撤销/无用户几何编辑的 restore→改标笔链）
  钉住现读法=partial，背书读法会判 complete；已登记
  `CONSTANTS["GEOMETRY_CONFIRM_RULE"]` 读法段，语义重裁定留 T2。
- 乐观冲突（DSH r1 P4-3 登记）：`expected_revision` 拒绝笔不产生事件由**写入端
  保证**（契约 rev1.4 乐观锁拒绝发生在写路径，被拒请求不落 region_revisions 行），
  导出端不可观测——本导出器只读 revision 链，对拒绝笔无从也无需观测。
- provenance.type=asset_case 而非 derived（derived 的孤儿 split 语义会破坏组隔离）；
  注册表组继承取该组非 challenge split 众数；challenge case_id 优先于组继承。
- provenance 含 `geometry_from_revision_no`（DSH r1 P4-5）：settled 几何来源
  revision_no（链末笔），与 `correction.revision_no`（事件笔）区分。
- bbox 回退语义（DSH r1 P1-1）：settled 几何 polygon<4 点（空/三点）时按生产
  `BBox.as_tuple()=(x, y, width, height)`（entities.py:72-73）xywh 语义展开四角，
  复用 T1a `importers.bbox_to_polygon`；旧实现误把 xywh 当 xyxy 读已修正，
  rgN 期望重算 + rgO 判别用例（空/三点两形态）钉住。
- 去重层级 exact+box-exact（感知层级不启用，理由见 README）。

## 6. 遗留与风险

- **T5b 集成耦合**：识别规则按契约 §5.4 fixture 断言冻结；T5b 集成后真库若出现
  实际链形态与本规则的偏差（例如未来新增 origin 或 restore 语义变化），需回归
  fixture 矩阵——单测已把语义钉死，漂移会红。
- **无真库改标事实**：本 Task 无法用真实用户改标链验证（真库 0 region），fixture
  覆盖即合同预设路径；真库冒烟仅证明空结果安全路径。
- **cases.json 页映射是精确茎匹配**：用户库页命名若与 cases.json source_id 惯例
  不一致则落到 user_library_source 备案（不阻断，仅许可信息较弱）。
- YOLO 导出为单类（sfx）口径，与 T1a 单类 schema 同构；T1b 四类 GT 的 names 顺序
  约束已在 dataset.yaml 逐字锚定（其余三类本导出不产样本）。

## 7. 证据清单

| 证据 | 路径 |
|---|---|
| 红态日志 | verification/M2-SFX-CORRECTION-EXPORTER/evidence/red-run.txt |
| 绿态日志 | verification/M2-SFX-CORRECTION-EXPORTER/evidence/green-run.txt |
| selfcheck 输出 | verification/M2-SFX-CORRECTION-EXPORTER/evidence/selfcheck.txt |
| fixture 冒烟摘要 | verification/M2-SFX-CORRECTION-EXPORTER/fixture-smoke-summary.json |
| 真库冒烟摘要 | verification/M2-SFX-CORRECTION-EXPORTER/real-db-smoke-summary.json |
| fixture 源库/导出物 | 一条命令可复现：`fixture.build_fixture_db(...)`（冒烟产物在 training_data/，gitignored） |

## 8. DSH r1 返修记录（r1=changes_requested，本分支返修 commit 全量处置）

返修基线：r1 审对象=实现 9c7cf7bc + 文档 fae43e4d；返修 commit=本文件所在分支
tip（`r1(CORRECTION-EXPORTER):` 前缀）。findings 处置对照（R 编号按 r1 原文）：

| R | 处置 | 落点 |
|---|---|---|
| P1-1 bbox 回退语义错（xywh 当 xyxy 读） | **修复** | `samples._polygon_from_geometry` 改用 T1a `importers.bbox_to_polygon`（xywh）；`fixture.geom` 改 xywh 生产语义（参数/命名同步）；rgN 期望重算 [[6,8],[46,8],[46,36],[6,36]]；新增 rgO 判别用例（生产 bbox+空/三点 polygon，纯函数级、不进 fixture 矩阵→冒烟 main/aux 计数不变）；旧读法对新期望必红（已数值验证：rgN bbox=[6,8,40,28] 旧读法得 (6,8)-(40,28) 错误框） |
| P2-1 YOLO seg 树混入辅助集未登记 | **实现** | `--yolo-scope {main,all}`（默认 main=仅正集；all=显式混入辅助集）；`run_export(yolo_scope=)`+summary 登记 `export.yolo_scope`；CLI choices 校验；README「--yolo-scope」节登记；test_export 新增 all 用例并重写默认 scope 断言 |
| P3-1 存活判据 (a) 保守误杀 | **方案②：保持保守+显式钉住+登记** | fixture 新增 rgO2 角例（撤销后 restore 复活已改标 revision；期望=undone 不存活，test_scanner 用例显式钉住）；`CONSTANTS["SURVIVAL_UNDONE_RULE"]` 登记「保守误杀，非 §5.4 唯一读法」；报告 §5/README 同步 |
| P3-2 几何确认门读法未登记 | **登记现读法+补判别用例（推荐项）** | `CONSTANTS["GEOMETRY_CONFIRM_RULE"]` 读法段：「restore 至改标 revision=用户背书该 revision 几何」及理由；现实现不以 restore 背书触发 complete，`geometry_confidence` 判别用例（test_samples，构造 restore→改标笔链）钉住现读法=partial；语义重裁定留 T2 |
| P3-3 partial 映射理由未登记 | **登记** | README 阈值表下补「partial=类型人工确认+几何机器产出，不落 pseudo 的理由」 |
| P3-4 计数错误（41≠46 与红态 EXIT） | **修正** | Task 测试表 AC1/AC2/AC3/AC4 行、报告 §2 AC1 行、§3 用例行改实际分项（r1 时点 16/5/9/10/6=46；返修后 17/7/9/11/6=50）；红态 EXIT 1→2（报告 §3、Handoff 证据表，对齐 red-run.txt 尾行） |
| P3-5 Task status 与 AC 注记 | **修正** | Task frontmatter `status: ready→in_review`；AC 节加注记「Owner 自评，待 Reviewer 确认」 |
| P4-2 / P4-6 / P4-7 / P4-8 / P4-9 / P4-10 | **登记不修（按 r1 处置）** | r1 原文未随本返修 ask 提供，按 ask 指定处置逐号登记为「登记不修」；r2 时若需展开请 DSH 附原文编号对照 |
| P4-3 乐观冲突角例不可观测未登记 | **登记** | 报告 §5：「expected_revision 拒绝笔不产生事件由写入端保证，导出端不可观测」 |
| P4-4 fixture 几何越界（y1=50>48） | **改页内几何（择 DSH 给的第一选项）** | `fixture.geom` 全部调用点重设计为 64×48 页内（不止 DSH 点名的 rgA/G，含 x 方向 gB/gC1/gI2 越界一并消除）；受影响期望（rgA、reg-dup、rgN）同步重算；未新增 clamp 计数逻辑 |
| P4-5 provenance 缺 settled 几何来源 | **实现** | provenance 新增 `geometry_from_revision_no`（链末笔 revision_no），test_samples rgA 断言 |

返修重跑证据（本机 T1.1.1-impl-py312，返修分支 tip）：
- `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` → **50 passed, EXIT=0**（evidence/green-run.txt）。
- `python -m sfx_correction_exporter selfcheck` → **6/6 PASS, EXIT=0**（evidence/selfcheck.txt，rules 含新增两条 CONSTANTS）。
- fixture 冒烟重生成 → **EXIT=0**：14 region/36 rev→12 事件（8 存活/6 sfx 向）→
  main 2+aux 4（与 r1 相比**计数不变**，仅 polygon/label 内容变）→ train5+challenge1 →
  YOLO 2 labels（scope=main）。摘要已重写。
- 真库冒烟重跑 → **EXIT=0，CORRECTIONS_EMPTY=expected**（real-db-smoke-summary.json 重生成；
  同时验证新 `--yolo-scope` 参数默认路径无破坏）。
- 红态证据 red-run.txt 为 r1 交付前历史记录，未重跑（ModuleNotFoundError 红态不可复现于已实现状态），仅修正其在报告/Handoff 中被误记的 EXIT 值。
