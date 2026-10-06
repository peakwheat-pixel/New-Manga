# M2-TEST-CATALOG-DRIFT-CLEAR-1 独立 Review 报告

- **Review 角色**：Antigravity（非作者独立 Reviewer，只读复核）
- **复核对象**：工作区未提交修改 [`tests/m2_test_assets/test_catalog.py`](file:///G:/CODEX/New%20Manga/tests/m2_test_assets/test_catalog.py#L30-L95)
- **关联任务**：[`doc/tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md)
- **基线 Commit**：`8bf57ba2`
- **总体判定（Verdict）**：**approve**

---

## 1. 逐项复核结论（a - d）

### a) `git diff tests/m2_test_assets/test_catalog.py` 改动核对
- **改动一致性**：
  1. 将原先过时的硬编码断言 `assert len(cases) == 97` 及 `assert len({case["case_id"] for case in cases}) == 97` 替换为无重复不变量 `assert len(cases) == len({case["case_id"] for case in cases})` 与冻结下界 `assert len(cases) >= 100`，并补充了完整的漂移历史注释。
  2. 扩展 `executed_cases` 集合，由原先的 5 个烟测案例（`{"BJ02", "BJ06", "K01", "K02", "K11"}`）并入了 M2-SFX-E2E-MATERIAL 的 3 个真实执行案例（`{"BJ13", "BJ14", "BJ15"}`）。
  3. 保留了针对所有非执行案例的严格 fail-closed 断言（所有 stage 必须为 `NOT_RUN`）。
  4. 新增 `expected_e2e_material` 真实留态字面快照，对 `BJ13/14/15` 的每个 stage 状态进行精确断言（特别是 BJ13 的 `sfx="PASS"` 及各阶段通过状态）。
- **风险评估**：
  - 仅修改了单测文件 [`tests/m2_test_assets/test_catalog.py`](file:///G:/CODEX/New%20Manga/tests/m2_test_assets/test_catalog.py) 中的单个测试函数 [`test_manifest_has_unique_cases_and_exact_taxonomy`](file:///G:/CODEX/New%20Manga/tests/m2_test_assets/test_catalog.py#L30)；
  - 核心契约、生产代码及 manifest 数据文件零改动；
  - 保持了 fail-closed 语义，新案例若未显式登记或未按预期全 `NOT_RUN` 仍会即时红灯；未引入任何新风险。

### b) 三次历史 Commit 追加真实性与 Append-Only 抽查
经对 [`test_assets/comic_golden_suite/manifests/cases.json`](file:///G:/CODEX/New%20Manga/test_assets/comic_golden_suite/manifests/cases.json) 进行 Git 提交历史溯源与数据完整性校验：
1. **Commit 链条确认**：
   - `40a8ceec` (`implement(M2-SFX-E2E-MATERIAL)`): `numstat` 显示 `+214 -0` 行，新增 `BJ13`、`BJ14`、`BJ15`，总数由 97 增至 100；
   - `9b9916af` (`material(ANNOTATE-R2)`): `numstat` 显示 `+750 -0` 行，新增 `BJ16` 至 `BJ25`，总数由 100 增至 110；
   - `579af8a5` (`material(ANNOTATE-R3)`): `numstat` 显示 `+900 -0` 行，新增 `BJ26` 至 `BJ37`，总数由 110 增至 122。
2. **Append-Only 前缀不变性验证**：
   - 经 Python 脚本比对每个 Commit 状态下的 `cases` 序列：
     `c_40a8[:97] == c_base`，`c_9b99[:100] == c_40a8`，`c_579a[:110] == c_9b99` 全部成立；
     旧案例内容与排序无任何删除或篡改，确为严格的 append-only 追加。
3. **留态出处复核**：
   - `40a8ceec` 提交记录中，`BJ13` 记录了 `sfx="PASS"`（SFX 翻译端到端闭环），`BJ14/15` 记录了除 sfx 与 speaker_attribution 外的全流程 PASS，出处确凿；
   - 其余新增案例（`BJ16` 至 `BJ37` 共 22 个）全部各 stage 均为 `NOT_RUN`。

### c) 测试执行验证
- **目标测试套件验证**：
  运行命令 `python -m pytest tests/m2_test_assets -q`：
  ```text
  ...............................................                          [100%]
  47 passed in 3.55s
  ```
  **47 个测试全部通过**（其中 [`test_catalog.py`](file:///G:/CODEX/New%20Manga/tests/m2_test_assets/test_catalog.py) 27 项测试全部绿色通过）。
- **全量测试回归表现**：
  查验 [`verification/M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/full-pytest-1.log`](file:///G:/CODEX/New%20Manga/verification/M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/full-pytest-1.log)：
  全量结果为 `1860 passed, 1 skipped, 2 failed`。原本长期报错的 `test_manifest_has_unique_cases_and_exact_taxonomy` 成为唯一转绿项（通过数由 1859 变为 1860，失败数由 3 降为 2，剩余两例归属于已知待处理的 `ui_shell` 环境项）。

### d) `>=100` 下界与字面快照例外集的口径合理性判断
1. **`>= 100` 下界口径**：
   - **合理性**：原先的 `== 97` 将动态增补的资产库锁死为固定快照，属于典型的测试坏味道（anti-pattern）。采用 `len == len(unique)`（守住 ID 唯一性不变量）+ `len >= 100`（守住 Milestone 2 核心基线容量下界）的组合，既允许后续授权任务继续合规追加资产，又防止资产集被静默削减。
   - **考量与对比**：若改为 `>= 122`，则每次合规入库资产（如后续 R4/R5）都需要被迫调整该数字；若保留 `>= 100`，则代表将其作为 M2 的“底线容量契约（Contractual Floor）”。目前口径在灵活性与保护性之间取得了良好平衡。
2. **字面快照例外集口径**：
   - **合理性**：对于已执行过端到端链路并留存状态的案例（`BJ02, BJ06, K01, K02, K11, BJ13, BJ14, BJ15`），通过在测试代码中保留显式字段快照（`expected_ta3a` + `expected_e2e_material`）进行强比对，能确保这些珍贵的真实执行留态不被意外篡改或回退；对于其余 114 个案例则继续执行一票否决的 `NOT_RUN` 检查，设计严密。

---

## 2. 分级发现（Findings）

- **P0 - P2**：无。
- **P3（Minor - 下界语义显式化建议）**：
  当前注释中提及了 `97 -> 100 -> 110 -> 122` 的演进史，但代码写的是 `assert len(cases) >= 100`。虽符合 M2 基线门槛，但未来其他维护者可能会疑惑为何下界停留于 100 而不是 122。建议后续可在注释中补充说明“100 为 M2 契约底线容量”。（不阻塞合并）
- **P4（Nit - 字典合并写法优化）**：
  行 92 中 `expected = expected_ta3a.get(case["case_id"]) or expected_e2e_material[case["case_id"]]` 利用 `or` 做了 fallback 查找。未来若留态案例增多，合并为一个映射字典常量（如 `EXPECTED_EXECUTED = {**expected_ta3a, **expected_e2e_material}`）会使可读性更佳。（不阻塞合并）

---

## 3. 总体判定与推荐下一步

- **Verdict**：**approve**（改动准确、事实确凿、回归绿色、无副作用）。
- **推荐下一步操作**：
  建议交由 **Codex Executor / Integrator** 执行以下操作：
  1. 将工作区改动提交至 `main` 分支（或按流程执行 commit，如 `fix(test-assets): resolve catalog drift via uniqueness invariant and executed snapshots (M2-TEST-CATALOG-DRIFT-CLEAR-1)`）；
  2. 更新任务文档 [`doc/tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/M2-TEST-CATALOG-DRIFT-CLEAR-1.md) 状态为 `done`；
  3. 更新 [`doc/STATUS.md`](file:///G:/CODEX/New%20Manga/doc/STATUS.md)，清除此长期存在的单测基线失败标记。
