复核完成（只读；本会话 shell 因沙箱 `SetNamedSecurityInfoW` 失败不可用，git 证据改由 `.git/worktrees/.../logs/HEAD` reflog 直读，未修改任何文件，也未重跑测试）。

## Verdict
**approved_with_conditions**

处置层面 16 条中 15 条实质闭合、P4-2 部分闭合；新增 2×P3 + 4×P4，全部为文档数值/证据标注级，零功能与零契约影响，无需重跑。条件见文末（4 项，纯文本级 + experiments 一行清理）。

## 逐条闭合表

| 编号 | 判定 | 证据 |
|---|---|---|
| P1-1 | **闭合** | Task 文件 `doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md:25`（目标"可观察交付"段）、`:30`（AC2 修订口径+两行依据）、`:59`（依赖链注记 no-op+挂召回恢复 Task）三处均标注 2026-10-04 编排裁决 (a)；报告 `arbitration-report.md:13` §0 改为"DELIVERED（按…修订口径）"直述 |
| P1-2 | **闭合** | `raw/ko-scan/<K>.json` ×10 + `raw/ko-scan-run.log`：10/10 `bit_identical=true`，候选 13+0+180+93+113+62+247+60+119+147=**1034**，仅 K11 `sfx_count=1`/`sfx_x_primary_max_iou=0.1325`/`threshold_violation_ge_090=false`，日志无 STOP 行；与报告 §3.2（`:136`/表 `:138-149`）逐格一致 |
| P1-3 | **闭合（附 P3-1 数字瑕疵）** | 报告 `:110` 已改述"实现路径验证（代码级）"并登记"真实 0.90+ 形态至今 0 观测"；但同句样本面"22 个 sfx 候选"与 raw 不符（见新发现 P3-1） |
| P2-1 | **闭合** | 报告 `:117` 登记绿态前提 `sfx.policy=skip` + translate 残余未评估限定；实测背书可溯源：`verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json:1512-1582` 恰 8 条 `region_type=sfx`/`sfx_policy=translate` |
| P2-2 | **闭合** | 报告 §3.3 `:157-164` 6 对 conf 列表；BJ06 三对 sfx/primary conf（0.9156/0.5379、0.8170/0.6845、0.9131/0.6049）与 `raw/bj06-on-off-candidates.json:259/190`、`:351/29`、`:305/167` 吻合，BJ13 合成对 0.8636/0.8786/0.8173 与 `raw/arbitrate-pages.json:28/57/86` 吻合；`src/infrastructure/providers/detection_sfx.py:734-772` 仅 IoU 门、conf 门未实施。（§3.3 的 IoU 0.8864 与 §1.4/raw 的 0.8865 经手算确认为 1dp 框重算 vs 全精度差，非矛盾） |
| P2-3 | **闭合** | 报告 §1.3.1 `:41-48` 四点选型论证 + 副作用登记（计数+1/UI 双 region/OCR 双跑）+ 去重切片候选 |
| P2-4 | **闭合** | 报告 §1.3.2 `:54-55` margin 0.0135/0.0138 两口径 + 域内完全包含形（IoU=面积比，上界 1.0）登记 |
| P2-5 | **闭合** | 报告 `:71` 三框源口径读数差 0.0003-0.06、"第二位小数级论证不得跨口径引用"标注 |
| P3-1 | **闭合（附 P4-2 表述瑕疵）** | `raw/pytest-three-suites-r2.log` 系独立新跑（59 行含 header+EXIT，r1 版 `pytest-three-suites.log` 57 行无 EXIT；38.84s vs 39.03s），`627 passed, 1 skipped`；off 回退 11 次（KO 10 次 off + BJ06 off，`arbitrate-manifest.json:112`）真实复验。EXIT 落码位置表述有误（见新发现 P4-2） |
| P3-2 | **闭合** | 报告 §3.4；全 src 唯一功能性读取 `src/application/tasks/service.py:988`，`detection` 子树零消费（src 无 `get("detection")` 命中）；`handlers.py:285/308`、`service.py:649`、`schema.py:341`（step_runs DDL 首行，列在 :356）均实存 |
| P3-3 | **闭合（附 P3-2 归因错误）** | 6 失败名与 `raw/pytest-t111-py312.log`（`:11/:39/:311/:324`，`6 failed, 619 passed, 2 skipped` @ `:339`）一致；但逐名表第 1 项归因与日志矛盾（见新发现 P3-2） |
| P3-4 | **闭合** | 报告 §1.3.2 `:56` 分离带在参照框 ±0.03-0.05 不确定度内量化否决，并挂重审条件（0.85+ 或内含形出现） |
| P4-1 | **闭合** | src 仅存 `arbitrated_candidates`（`detection_sfx.py:737/745/757/762`）；全仓 `arbitratedRoute` 仅剩 Task/报告的历史引用（`:77`、报告 `:282`），src/tests 零残留 |
| P4-2 | **未闭合（部分）** | 双实例已闭合（`arbitrate_bj13.py:342` 与 `:383` 各自 composite）；但死形参未删净：`arbitrate_bj13.py:155` `def __init__(self, result, extra)` 体内（`:156-160`）不使用 `extra`，唯一调用 `:309` 传 `[]`，docstring `:152-153` 仍称 "merged with EXTRA synthetic candidates" |
| P4-3 | **闭合** | 报告 `:119`/`:188` 统一 15+1=16；`raw/red-phase-arbitration-tests.log:570` "14 failed, 1 passed, 23 deselected"（14+1+23=38=该文件用例数），7 组参数化见 `tests/providers/test_detection_sfx.py:808-818`，矩阵行见 `tests/core/test_sfx_assembly.py:160` |
| P4-4 | **闭合** | r2 脚本 `arbitrate_bj13.py:246` 零相交显式 `null`；r1 raw 未重生成已登记（报告 `:259` Known limitations 6），与 `raw/arbitrate-pages.json:449` 仍为 `0.0` 自洽 |

程序瑕疵登记：Task `:79` 与报告 `:287` 均已落账，未重复追责——符合裁决口径。

## 新发现

- **P3-1（数值不可溯源）**：报告 §0 `:13`、§2.2 `:110`、§9 `:272` 与 Handoff `:20` 引用的"BJ 4 页 **22 个 sfx 候选** × 25 primary"，与 raw 不符——`raw/arbitrate-run.log:2-5` 显示 sfx 候选 BJ13=1/BJ14=0/BJ15=0/BJ06=8，**合计 9**（primary 25 正确）。候选对实为 9×25=225 而非 550。结论"0 对 ≥0.90"本身不受影响（可独立核验：BJ13/14/15 `sfx_x_primary_max_iou=0.0`、BJ06 0.8865、KO 0.1325），但该数字是裁决 (a) 要求的"真实发生面登记"本体，须订正为 9（或删数只写 25 primary）。
- **P3-2（归因与原始日志矛盾）**：报告 §3.5 P3-3 表第 1 项把 `test_production_stack_starts_without_heavy_runtimes` 归因为"venv 装有 manga-ocr 等 heavy 依赖 → provider registry 状态非 missing_dependency"；`raw/pytest-t111-py312.log:25-30` 的 registry 断言全部通过，实际失败点是 `:31` `status["gpu"]["state"] == "unavailable"` 得 `'available'`——与第 5/6 项同属"该 venv 带 CUDA torch"一类。结论（与本 Task 零因果）不变，分类需改写。
- **P4-1（r1 项残留）**：见上表 P4-2——死形参 `extra` 与陈旧 docstring 仍在 `experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py:152-160`。
- **P4-2（证据标注不实）**：报告 §3.5 `:180`、`:185` 三处称"日志首行 `EXIT=0`"；实际 `raw/pytest-three-suites-r2.log:1` 是 `=== r2 rerun @4d8aaee0 ===`，`EXIT=0` 在 `:59`（末行）。
- **P4-3（证据-状态绑定弱）**：r2 三套件日志头记录 `@4d8aaee0`（reflog 显示 r2 收尾 commit 为 `e43cc5db`，两者相隔约 33 min），即日志记录的是 P4-1 重命名**之前**的 HEAD；加上"38 passed"（`:184`）无落盘日志，v2 树状态无法从证据自证。因 P4-1 是行为中性的局部变量重命名，风险≈0，建议只补一行状态标注而非重跑。
- **P4-4（数字粗糙）**：报告 §3.2 `:136` 与 Handoff `:71` 称 KO 长条"合计 ~700 tiles×2"，实际 `raw/ko-scan-run.log` tiles 合计 **605**；Handoff `:71` 称 KO 扫描"~4.5 分钟"，逐 case elapsed 合计约 **357s≈5.9 min**。

## 集成条件（全部为文本级，无功能返修、无重跑）
1. 将 5 处"22 个 sfx 候选"订正为 **9**（Task `:73`、报告 `:13/:110/:272`、Handoff `:20`）。
2. 改写报告 §3.5 P3-3 表第 1 项归因（CUDA torch → `gpu.state=available`，registry 断言实际通过）。
3. 报告 §3.5 的"日志首行 EXIT=0"改为"日志末行 EXIT=0"，并在 §7 证据物索引补注 r2 日志的 HEAD 标注（`@4d8aaee0`，重命名前）。
4. 删除 `arbitrate_bj13.py:155` 的 `extra` 形参与 `:152-153` 陈旧 docstring（或注明其为占位），完成 r1 P4-2 的收尾；顺带订正 tiles/耗时两个数量级描述。

上述 1-4 完成后 P4-2 转为闭合，本 Task 即可交集成方（Codex/编排代行）复跑三套件与 cargo/vitest 并集成。
