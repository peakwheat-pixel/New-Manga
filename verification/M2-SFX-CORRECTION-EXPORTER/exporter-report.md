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
| AC1 事件识别 | PASS | `pytest tests/test_scanner.py`（12 测试全绿）；fixture 14 region 混合链逐条断言（基本纠错/被撤销/纯几何/纯文本/机器改标/二次改标取代/撤销再纠错/用户自建/几何编辑后 restore/纯顺序/非 sfx 向/软删除/BJ13 映射/纯 bbox）；判据=契约 §5.4（改标 origin 恒 user、撤销=restored 溯源、review_state=UNREVIEWED、机器改标非事件） |
| AC2 样本构建 | PASS | `tests/test_samples.py`：T1a SampleRecord 逐条 validate()==[]；图引用=真实文件 sha256+尺寸；框=settled 几何+cls=sfx；complete/partial 落地；provenance 含 correction.chain 全链 trace（revision_no/origin/region_type 序列可回放） |
| AC3 资格判定 | PASS | `tests/test_eligibility.py`：许可继承（BJ13→commercial_use_permitted_attribution）/user_library_source 备案，全部 blocking=false（二次裁决全备案不阻断）；几何门 complete/partial 与辅助集路由；与 T1a 已册样本 exact+box-exact 去重（同图同框剔除、同图异框保留、空册/坏册四态登记）；阈值冻结于 `eligibility.CONSTANTS` |
| AC4 双形态导出 | PASS | `tests/test_export.py` + fixture 冒烟：manifest.json（正集 complete）+ manifest-auxiliary.json（partial 辅助集）均为 `sfx-data-infra/manifest@1` 容器（T1a atomicio 原子写）；YOLO seg labels（sfx id=2 归一化多边形）+ dataset.yaml names 逐字=SFX_CLASS_MAP；输出 `training_data/sfx-corrections/` |
| AC5 CLI/只读 | PASS | `--help` EXIT=0；`selfcheck` EXIT=0（6 checks：只读写拒/识别语义/schema 互操作/class_map 锚定/去重 sanity/manifest 往返）；只读铁律=URI `mode=ro`+`PRAGMA query_only=ON`（UPDATE/DELETE 均被拒，缺库 fail-closed 不静默创建） |
| AC6 互操作 | PASS | 导出 manifest 过 T1a `load_manifest`（逐样本 schema 校验）→ `TrainingSetBuilder` 消费（challenge 设计性隔离、组原子性断言、`allowed_splits` 含 test 时抛 `SplitAccessError`）；组继承：注册表组直接继承 split，challenge case 优先 |

## 3. 测试与红绿证据

- 用例数：**46**（test_scanner 12 / test_samples 5 / test_eligibility 8 / test_export 10 / test_cli 6，含 parametrize 无）。
- **红态**：实现落盘前 `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` →
  **5 文件 collection error，`ModuleNotFoundError: No module named 'sfx_correction_exporter'`**，
  pytest EXIT=1（evidence/red-run.txt）。
- **绿态**：实现后同命令 **46 passed, 0 failed**，EXIT=0（evidence/green-run.txt）。
- 中途修复（红→绿之间的实现缺陷，均由测试捕获）：fixture 重复插入 book/chapter
  （UNIQUE 约束）；`machine_type_changes_excluded` 误计 restored 类型回退；
  `__init__.py` REPO_ROOT 少上一层导致 cases.json 解析不到；`quality_note` 未写入 provenance。

## 4. 冒烟

1. **fixture 库全流程**（真实 SQLite 文件，生产 v1–v4 冻结 DDL）：扫描 13 region
   （跳过 1 软删除）/32 revisions → 11 事件（8 存活，其中 6 sfx 向）→ 正集 2
   （complete）+ 辅助集 4（partial）→ split train=5 + challenge=1 → YOLO 6 labels →
   **EXIT=0**。摘要：`verification/M2-SFX-CORRECTION-EXPORTER/fixture-smoke-summary.json`。
2. **主仓库真库**（`C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db`，
   只读探测确认含 regions/region_revisions 表、regions=0——T5b 未集成，真库无改标事实）：
   **CORRECTIONS_EMPTY=expected，EXIT=0**，db_readonly=true。摘要：
   `verification/M2-SFX-CORRECTION-EXPORTER/real-db-smoke-summary.json`。
   T5b 集成后真库冒烟由集成方补跑（合同「依赖、风险与阻塞」节预告）。

## 5. 冻结语义登记（实现裁定，供 review 核对）

- 存活规则 (a)：其后存在 `origin=restored` 且 `region_type==type_before` 的 revision
  即撤销（无论 restored_from 指向）；(b)：链末笔类型必须等于 `type_after`。二者与
  fixture 矩阵逐条对应（rgB/rgF/rgG/rgI 是关键判别用例）。
- 角例（保守不采）：撤销后经 restore 至已改标 revision 复活纠错态 → 事件仍视为已
  撤销（restore 不是 retype，不产生事件）。
- provenance.type=asset_case 而非 derived（derived 的孤儿 split 语义会破坏组隔离）；
  注册表组继承取该组非 challenge split 众数；challenge case_id 优先于组继承。
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
