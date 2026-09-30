# M2-FIX-REGISTRY-READINESS-ENV 集成记录（2026-10-01，acting Codex）

## 结论

Task `done` @integration merge `52b07438`（branch `agent/zcode/M2-FIX-REGISTRY-ENV`，base `46f079e8`，分支 tip=集成修正 `75c72dfa`）。

## 交付链

`66ec6a6d`(claim+意图判定) → `3e4c3b44`(fix：环境条件化) → `32caab97`(handoff) → `59fe3467`(review-fix DSH r1 R-B1..B5) → `75c72dfa`(集成修正：DSH r2 P4-1/P4-2/P4-4，doc-only)。

## Review 轨迹

- DSH r1 [approved_with_conditions](../../doc/reviews/M2-MANGA-WEIGHTS-SOP-b0dd843c-dsh-r1.md)（同轮合并 review 的 Task B 节；2×P3：R-B1 修复前基线数字错、R-B2 skip 理由「被构建期断言接管」方向性不成立；3×P4）→ Owner review-fix `59fe3467`（R-B1..B5 全 closed；判别力探针固化为同文件参数化测试）→ DSH r2 [approved](../../doc/reviews/M2-MANGA-WEIGHTS-SOP-b0dd843c-dsh-r2.md)（P4 残留转集成）→ 集成修正 `75c72dfa`。

## 修复语义（终态）

`test_no_model_runtime_is_installed_in_this_environment`：ML runtime 在位（`find_spec("torch")`，与原断言同探针）→ `pytest.skip` 显式理由——TASK-019「环境无 ML」证据**作废**（INVALIDATED，T1.1.1 用户批准 requirements 推翻前提），**非被替代**；发布侧 ML 闭包完整性由 `core_sidecar.spec` `_assert_ml_closure` 构建期断言**独立**保证（方向相反）。无 ML 环境保留原断言逐字验证力+判别力探针（2 参数化用例，任何机器可复跑）。

## 集成方复跑门禁（2026-10-01，main @`52b07438`）

- 三套件 `pytest tests/providers tests/m2_acceptance tests/core -q -rs`：**403 passed + 1 skipped, 0 failed**（EXIT=0）；skip 理由全文逐字符合 R-B2 更正口径。
- 口径终结：**「历轮 +1 既有环境性失败（test_registry_readiness）」条目自此终结**；新基线=providers 291 passed + 1 skipped（env-conditioned）/ m2_acceptance 35 / core 77。
- git 层：`git diff --check 46f079e8..75c72dfa` EXIT=0；3 文件域；porcelain 干净。

Owner branch/worktree 保留于 `75c72dfa`。
