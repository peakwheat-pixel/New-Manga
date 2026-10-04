---
task_id: M2-SFX-CORRECTION-EXPORTER
author: ZCode
recipient: Codex（Integrator）；Review：DeepSeek Harness（非作者）
base_commit: 69321db7
delivery_head: 9c7cf7bc
status: delivered
r1_rework: 分支 tip（r1(CORRECTION-EXPORTER) commit；DSH r1 changes_requested 全量处置，见文末修订段）
---

# Handoff：M2-SFX-CORRECTION-EXPORTER（T5c 纠错样本导出器）

## 交付结果

提交链：`1b765007`（release @claim）→ `df0e05c4`（claim）→ **`9c7cf7bc`（实现 delivery_head）** → 文档 commit（本 Handoff+Task 回填+verification 证据，见分支最新）。

实现范围（全部在允许修改路径内；零 src/tests 既有/contracts/packaging/apps/STATUS 变更）：

- `experiments/M2-SFX-CORRECTION-EXPORTER/sfx_correction_exporter/`：
  - `scanner.py`（AC1）：只读扫描 revision 链识别类型纠错事件。判据=契约 rev 1.4 §5.4：事件=第 j≥2 笔 `origin=user` 且 snapshot.region_type≠前笔；存活规则 (a) 其后无 `origin=restored` 回退至 type_before（被撤销不入册；保守读法已登记 `SURVIVAL_UNDONE_RULE`）、(b) 链末笔类型==type_after（settled 终判）；machine/imported 类型变化排除计数；restored 类型回退是撤销动作不构成事件；软删除 region 跳过计数。
  - `samples.py`（AC2）：事件→T1a `SampleRecord`（`sfx-data-infra/sample@1`）；框=链末笔 settled 几何（polygon<4 点按**生产 xywh bbox** 回退四角+quality_note，r1 P1-1 修正）；状态=complete/partial（几何门）；provenance.type=asset_case+`source=revision_chain_correction`+`correction.chain` 全链 trace+`geometry_from_revision_no`（r1 P4-5，可溯源可回放）。
  - `eligibility.py`（AC3）：许可备案（cases.json 映射继承 / user_library_source，全部 blocking=false——二次裁决全备案不阻断）；几何确认门 `GEOMETRY_CONFIRM_RULE=v1`（complete⟺首笔 user 或存在用户几何编辑）；T1a `find_duplicates` exact+box-exact 去重（册内优先）；阈值冻结于 `CONSTANTS`。
  - `export.py`（AC4）：`manifest.json`（正集 complete）+`manifest-auxiliary.json`（partial 辅助集，不入正集可选入）+YOLO seg（sfx id=2 归一化多边形；dataset.yaml names 逐字=SFX_CLASS_MAP——T0 P3-6）+export-summary；拆分=challenge 单列→注册表组继承（非 challenge 众数）→T1a `assign_splits`（seed 20261004）。
  - `db.py`（AC5）：URI `mode=ro`+`PRAGMA query_only=ON`（镜像 `src/infrastructure/sqlite/connection.py:367-374`，零 src 自持）。
  - `cli.py`/`__main__.py`（AC5）：`--help`/`selfcheck`（6 checks）/`export`（缺库 fail-closed）。
  - `fixture.py`：15 region 混合 revision 链 fixture（生产 v1–v4 冻结 DDL 原样执行；几何全部页内且 bbox=生产 xywh 语义，r1 P4-4）。
- `tests/`：50 用例（r1 返修后；TDD 先红后绿）。
- `README.md`：冻结语义+设计取舍登记。
- `verification/M2-SFX-CORRECTION-EXPORTER/`：报告、两份冒烟摘要、红绿/selfcheck 证据。
- 导出物：`training_data/sfx-corrections/`（fixture 冒烟产物，gitignored 外部树）。

**未做/超出范围**：真库改标事实冒烟（真库 0 region——T5b 未集成，按合同由集成方在 T5b 集成后补跑）；`training_data/sfx-v1` 注册表不在本机（registry 四态已处理并测试）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 识别（15 region 矩阵逐条） | `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` | T1.1.1-impl-py312 @ 9c7cf7bc + r1 返修（分支 tip） | PASS（红→绿） | evidence/red-run.txt（5×ModuleNotFoundError，EXIT=2）、evidence/green-run.txt（r1 返修后 50 passed，EXIT=0） |
| AC2 样本构建 | 同上（test_samples.py 7 例，含 rgO bbox 语义判别） | 同上 | PASS | 同上 |
| AC3 资格判定 | 同上（test_eligibility.py 9 例） | 同上 | PASS | 同上 |
| AC4+AC6 导出与互操作 | 同上（test_export.py 11 例：T1a load_manifest+TrainingSetBuilder+SplitAccessError+组继承+指纹确定性+yolo-scope main/all） | 同上 | PASS | 同上 |
| AC5 CLI | `python -m sfx_correction_exporter --help` / `selfcheck` | 同上 | PASS（EXIT=0/0，selfcheck 6/6） | evidence/selfcheck.txt |
| AC5 只读铁律 | test_cli/test_scanner 内 UPDATE/DELETE 断言被拒 + PRAGMA query_only==1 | 同上 | PASS | green-run.txt |
| fixture 全流程冒烟 | `run_export(db=fixture 15-region 库, out=training_data/sfx-corrections)`：14 region/36 rev → 12 事件（8 存活/6 sfx 向）→ main 2+aux 4 → split train5+challenge1 → YOLO 2 labels（--yolo-scope 默认 main；all=6） | 同上 | EXIT=0 | fixture-smoke-summary.json |
| 真库空结果冒烟 | `python -m sfx_correction_exporter export --db "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db" --summary-out .../real-db-smoke-summary.json`（库含 regions 表、0 region） | 同上 | EXIT=0，CORRECTIONS_EMPTY=expected，db_readonly=true | real-db-smoke-summary.json |
| git 纪律 | `git diff --check`（暂存后） | r1 返修 commit | EXIT=0 | — |

未运行项：真库非空链冒烟（真库无改标事实，BLOCKED-ON T5b 集成，非本 Task 缺陷）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-CORRECTION-EXPORTER` @ worktree `G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode`。
- 复现：dev venv `T1.1.1-impl-py312`；`cd experiments/M2-SFX-CORRECTION-EXPORTER && python -m sfx_correction_exporter selfcheck`；pytest 路径装配已由 `tests/conftest.py`+包 `__init__` 处理（T1a 包/repo root/src）。
- Review 核对建议：①scanner 存活规则 (a)/(b) 对照契约 §5.4 与 fixture 矩阵（rgB/rgF/rgG/rgI 为判别用例；r1 返修后 rgO2 钉住保守误杀读法）；②`eligibility.CONSTANTS` 冻结阈值与合同 AC3 的「阈值冻结并登记」（r1 返修后含 SURVIVAL_UNDONE_RULE 与 GEOMETRY_CONFIRM_RULE 读法段）；③provenance.type=asset_case 取舍（derived 会破坏组隔离，README 已登记）；④dataset.yaml names 逐字锚定（T0 P3-6 硬约束）。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-CORRECTION-EXPORTER 的 DSH r2 Review（核对 r1 findings 全量处置），随后 Codex 集成。
- Owner：DeepSeek Harness（Review）→ Codex（集成）。
- 指令要点：r2 输入=本 Handoff（文末「DSH r1 修订段」R 编号→处置对照）+`verification/M2-SFX-CORRECTION-EXPORTER/exporter-report.md` §8 返修记录+返修分支 tip。集成注意：T5b 集成合并后补跑真库冒烟（`export --db <library.db>`，期待 CORRECTIONS_EMPTY 直到出现真实改标链）；本 Task 与 T5b 零写重叠，集成顺序无约束。

## DSH r1 修订段（r1=changes_requested → 本返修 commit 全量处置）

r1 审对象：实现 `9c7cf7bc` + 文档 `fae43e4d`。返修 commit：本文件所在分支 tip
（`r1(CORRECTION-EXPORTER):` 前缀；代码+测试+文档+证据同一 commit）。

findings_disposition（R 编号按 r1 原文；明细证据见 exporter-report.md §8 返修记录表）：

- **P1-1（必修，bbox 回退语义错）**：已修复。`samples._polygon_from_geometry` 改用
  T1a 现成 helper `sfx_data_infra.importers.bbox_to_polygon(x, y, w, h)`
  （importers.py:54-55）；`fixture.geom` 同步改生产 xywh 语义（参数/命名改为
  `(x, y, w, h)`）；rgN 期望值重算为 `[[6.0,8.0],[46.0,8.0],[46.0,36.0],[6.0,36.0]]`
  （bbox=[6,8,40,28] 按 x+w/y+h 推导；旧 xyxy 读法得 (6,8)-(40,28) 错误框，数值验证
  判别有效）；新增 rgO 判别用例（生产 bbox+空/三点 polygon 两形态，
  `test_polygon_from_geometry_xywh_discriminator`——纯函数级、不进 fixture 矩阵，
  冒烟 main/aux 计数因此不变）。
- **P2-1（YOLO seg 树混入辅助集未登记）**：已实现 `--yolo-scope {main,all}`，
  默认 `main`=仅正集（complete）入 YOLO seg 树；`all` 显式混入辅助集；
  `export.yolo_scope` 入 summary 登记；README「--yolo-scope」节登记；
  test_export 新增 all 用例+重写默认 scope 断言。
- **P3-1（存活判据 (a) 保守误杀）**：裁定=方案②保持保守。fixture 新增 rgO2 角例
  显式钉住期望（undone=True、survives=False）；`CONSTANTS["SURVIVAL_UNDONE_RULE"]`
  登记「保守误杀，非 §5.4 唯一读法」；报告 §5/README 同步；语义重裁定留 T2。
- **P3-2（几何确认门读法未登记）**：按推荐项=登记现读法+补判别用例。
  `CONSTANTS["GEOMETRY_CONFIRM_RULE"]` 明写「restore 至改标 revision=用户背书该
  revision 几何」及理由；`geometry_confidence` 判别用例钉住现读法=partial
  （背书读法会判 complete）；改判定语义留 T2。
- **P3-3（partial 映射理由未登记）**：README 阈值表下补 partial 判据构成与
  不落 pseudo 的理由（类型人工确认+几何机器产出，监督信号有效故保留辅助集）。
- **P3-4（计数错误）**：分项改实际值——r1 时点 **16/5/9/10/6=46**（原报告
  误记 12/5/8/10/6=41）；红态 EXIT 1→**2**（报告证据表与 Handoff 证据表对齐
  red-run.txt 尾行）；返修新增用例后总分项 **17/7/9/11/6=50**（Task/Handoff/
  报告全部同步）。
- **P3-5（Task 状态）**：frontmatter `status: ready→in_review`；AC 节加注记
  「Owner 自评，待 Reviewer 确认」。
- **P4-3**：报告 §5 登记「乐观冲突/expected_revision 拒绝笔不产生事件由写入端
  保证，导出端不可观测」。
- **P4-4（fixture 几何越界）**：择「改页内几何」——`fixture.geom` 全部调用点
  重设计为 64×48 页内（覆盖 DSH 点名的 rgA/G y 方向，并一并消除 x 方向
  gB/gC1/gI2 越界）；未新增 clamp 计数逻辑。
- **P4-5**：provenance 新增 `geometry_from_revision_no` 字段（链末笔）+测试断言。
- **P4-2 / P4-6 / P4-7 / P4-8 / P4-9 / P4-10**：按 r1 处置**登记不修**（r1 原文
  未随本返修 ask 提供，按编号登记处置结果；r2 若需逐条展开请附原文）。

返修重跑数字（本机 dev venv T1.1.1-impl-py312）：
- `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` → **50 passed，EXIT=0**
- `python -m sfx_correction_exporter selfcheck` → **6/6 PASS，EXIT=0**
- fixture 冒烟重生成 → **EXIT=0**：14 region/36 rev→12 事件（8 存活/6 sfx 向）→
  main 2+aux 4（**计数与 r1 交付相比不变**；polygon 与 YOLO label 内容随 bbox
  语义修复变化）→ train5+challenge1 → YOLO 2 labels（scope=main；all=6）
- 真库冒烟重跑 → **EXIT=0，CORRECTIONS_EMPTY=expected**
