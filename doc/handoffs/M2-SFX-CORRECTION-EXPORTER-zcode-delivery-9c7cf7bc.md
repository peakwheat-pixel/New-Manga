---
task_id: M2-SFX-CORRECTION-EXPORTER
author: ZCode
recipient: Codex（Integrator）；Review：DeepSeek Harness（非作者）
base_commit: 69321db7
delivery_head: 9c7cf7bc
status: delivered
---

# Handoff：M2-SFX-CORRECTION-EXPORTER（T5c 纠错样本导出器）

## 交付结果

提交链：`1b765007`（release @claim）→ `df0e05c4`（claim）→ **`9c7cf7bc`（实现 delivery_head）** → 文档 commit（本 Handoff+Task 回填+verification 证据，见分支最新）。

实现范围（全部在允许修改路径内；零 src/tests 既有/contracts/packaging/apps/STATUS 变更）：

- `experiments/M2-SFX-CORRECTION-EXPORTER/sfx_correction_exporter/`：
  - `scanner.py`（AC1）：只读扫描 revision 链识别类型纠错事件。判据=契约 rev 1.4 §5.4：事件=第 j≥2 笔 `origin=user` 且 snapshot.region_type≠前笔；存活规则 (a) 其后无 `origin=restored` 回退至 type_before（被撤销不入册）、(b) 链末笔类型==type_after（settled 终判）；machine/imported 类型变化排除计数；restored 类型回退是撤销动作不构成事件；软删除 region 跳过计数。
  - `samples.py`（AC2）：事件→T1a `SampleRecord`（`sfx-data-infra/sample@1`）；框=链末笔 settled 几何（polygon<4 点回退 bbox 四角+quality_note）；状态=complete/partial（几何门）；provenance.type=asset_case+`source=revision_chain_correction`+`correction.chain` 全链 trace（可溯源可回放）。
  - `eligibility.py`（AC3）：许可备案（cases.json 映射继承 / user_library_source，全部 blocking=false——二次裁决全备案不阻断）；几何确认门 `GEOMETRY_CONFIRM_RULE=v1`（complete⟺首笔 user 或存在用户几何编辑）；T1a `find_duplicates` exact+box-exact 去重（册内优先）；阈值冻结于 `CONSTANTS`。
  - `export.py`（AC4）：`manifest.json`（正集 complete）+`manifest-auxiliary.json`（partial 辅助集，不入正集可选入）+YOLO seg（sfx id=2 归一化多边形；dataset.yaml names 逐字=SFX_CLASS_MAP——T0 P3-6）+export-summary；拆分=challenge 单列→注册表组继承（非 challenge 众数）→T1a `assign_splits`（seed 20261004）。
  - `db.py`（AC5）：URI `mode=ro`+`PRAGMA query_only=ON`（镜像 `src/infrastructure/sqlite/connection.py:367-374`，零 src 自持）。
  - `cli.py`/`__main__.py`（AC5）：`--help`/`selfcheck`（6 checks）/`export`（缺库 fail-closed）。
  - `fixture.py`：14 region 混合 revision 链 fixture（生产 v1–v4 冻结 DDL 原样执行）。
- `tests/`：46 用例（TDD 先红后绿）。
- `README.md`：冻结语义+设计取舍登记。
- `verification/M2-SFX-CORRECTION-EXPORTER/`：报告、两份冒烟摘要、红绿/selfcheck 证据。
- 导出物：`training_data/sfx-corrections/`（fixture 冒烟产物，gitignored 外部树）。

**未做/超出范围**：真库改标事实冒烟（真库 0 region——T5b 未集成，按合同由集成方在 T5b 集成后补跑）；`training_data/sfx-v1` 注册表不在本机（registry 四态已处理并测试）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 识别（14 region 矩阵逐条） | `pytest experiments/M2-SFX-CORRECTION-EXPORTER/tests/ -q` | T1.1.1-impl-py312 @ 9c7cf7bc | PASS（红→绿） | evidence/red-run.txt（5×ModuleNotFoundError，EXIT=1）、evidence/green-run.txt（46 passed，EXIT=0） |
| AC2 样本构建 | 同上（test_samples.py 5 例） | 同上 | PASS | 同上 |
| AC3 资格判定 | 同上（test_eligibility.py 8 例） | 同上 | PASS | 同上 |
| AC4+AC6 导出与互操作 | 同上（test_export.py 10 例：T1a load_manifest+TrainingSetBuilder+SplitAccessError+组继承+指纹确定性） | 同上 | PASS | 同上 |
| AC5 CLI | `python -m sfx_correction_exporter --help` / `selfcheck` | 同上 | PASS（EXIT=0/0，selfcheck 6/6） | evidence/selfcheck.txt |
| AC5 只读铁律 | test_cli/test_scanner 内 UPDATE/DELETE 断言被拒 + PRAGMA query_only==1 | 同上 | PASS | green-run.txt |
| fixture 全流程冒烟 | `run_export(db=fixture 14-region 库, out=training_data/sfx-corrections)`：13 region/32 rev → 11 事件（8 存活/6 sfx 向）→ main 2+aux 4 → split train5+challenge1 | 同上 | EXIT=0 | fixture-smoke-summary.json |
| 真库空结果冒烟 | `python -m sfx_correction_exporter export --db "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db" --summary-out .../real-db-smoke-summary.json`（库含 regions 表、0 region） | 同上 | EXIT=0，CORRECTIONS_EMPTY=expected，db_readonly=true | real-db-smoke-summary.json |
| git 纪律 | `git diff --check`（暂存后） | 9c7cf7bc | EXIT=0 | — |

未运行项：真库非空链冒烟（真库无改标事实，BLOCKED-ON T5b 集成，非本 Task 缺陷）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-CORRECTION-EXPORTER` @ worktree `G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode`。
- 复现：dev venv `T1.1.1-impl-py312`；`cd experiments/M2-SFX-CORRECTION-EXPORTER && python -m sfx_correction_exporter selfcheck`；pytest 路径装配已由 `tests/conftest.py`+包 `__init__` 处理（T1a 包/repo root/src）。
- Review 核对建议：①scanner 存活规则 (a)/(b) 对照契约 §5.4 与 fixture 矩阵（rgB/rgF/rgG/rgI 为判别用例）；②`eligibility.CONSTANTS` 四条冻结阈值与合同 AC3 的「阈值冻结并登记」；③provenance.type=asset_case 取舍（derived 会破坏组隔离，README 已登记）；④dataset.yaml names 逐字锚定（T0 P3-6 硬约束）。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-CORRECTION-EXPORTER 的 DSH 独立 Review（非作者；核对冻结语义与 fixture 判别用例），随后 Codex 集成。
- Owner：DeepSeek Harness（Review）→ Codex（集成）。
- 指令要点：Review 输入=本 Handoff+`verification/M2-SFX-CORRECTION-EXPORTER/exporter-report.md`+`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev1.4 §5.4+`experiments/M2-SFX-CORRECTION-EXPORTER/`（tests/test_scanner.py 顶栏矩阵注释即语义规格）。集成注意：T5b 集成合并后补跑真库冒烟（`export --db <library.db>`，期待 CORRECTIONS_EMPTY 直到出现真实改标链）；本 Task 与 T5b 零写重叠，集成顺序无约束。
