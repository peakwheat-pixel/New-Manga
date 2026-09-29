# M2-TA2C Integration Record（ZCode 代行 Codex 集成）

- 日期：2026-09-29（Asia/Shanghai）
- 集成方：ZCode（用户指示续接；代行 Codex Lead/Integrator，用户全权授权 2026-09-28）
- 实现作者：Codex Desktop；非作者 Reviewer：DeepSeek Harness（Owner≠Reviewer 保持）
- 本集成记录与治理收口（Task 置 done、STATUS/PLAN 回填、r2 报告归档、P3-8 转录出树）同属收口提交（`git log a4cd513d..HEAD` 首个治理 commit）。

## 1. 冻结与交付链

| 角色 | commit |
|---|---|
| fixed base | `d4d3977907bc64177ef85c61da4c95901f135fc6` |
| release | `ff2dee6c0dc0a20991dd2bfc3436b690d091e6e4` |
| claim | `391faae830e35ffec687863721d82cb0f1ac89bd` |
| r1 实现 / r1 handoff | `2e979701` / `2c12ba1e` |
| r1 返修 | `93f7b4b4` → `0676865b` → `c6c9c93c` → `66dc361d` |
| r2 handoff（reviewed_head）/ 终 tip | `8cb3a135c58d7a7a7b3d07fc5bba75c17aa6deb7` / `2e784327` |
| integration merge | `a4cd513d0f7ca6a50e1ae018629b3042612be3bb`（parents `406f2c76` + `2e784327`，`--no-ff`，无冲突，31 文件 / +5810 −107） |

## 2. Review 链

- r1（DSH，reviewed=`2c12ba1e`）：[`changes_requested`](../../doc/reviews/M2-TA2C-2c12ba1e-dsh-r1.md)——0×P0、0×P1、2×P2、7×P3。P2-1（KO 来源状态口径冲突）、P2-2（checksum_inventory 缺失/基准不统一）由 `93f7b4b4`+`0676865b` 修复；P3-2 建议被作者以红证（`pytest-assets-r2-initial-fail.log`）证实会改变既有 `PARTIAL` 失败模式后撤回，r2 判"以不采用关闭"。
- r2 首轮会话：`INVALID_REQUEST 422`、final 为空（`dsh-review-r2.err.log`），判无效，不作 verdict。
- **r2b（DSH 独立重派，session=`ca1ae6af-3e74-421c-a4ab-1ec58ec54927`）**：[`approved`](../../doc/reviews/M2-TA2C-8cb3a135-dsh-r2.md)——0×P0/P1/P2；r1 P2-1/P2-2 独立复核判定关闭；P3-1 关闭、P3-3/4/5/6/7 保留、新增 P3-8/P3-9/P3-10（均不阻塞）。报告由转录 final 字段提取原字节归档，SHA256=`d8fede0c9106fd9942babdd749d12c9e278cdd88badc805e91a4c95b32f473f4`。

## 3. 范围证明

`git diff --name-only d4d39779..2e784327` 全部 32 路径均在 Task 允许清单（`test_assets/comic_golden_suite/**`、`tests/m2_test_assets/**`、`doc/tasks|handoffs|reviews/M2-TA2C-*`、`verification/M2-TA2C/**`）与治理回填授权（`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`）内；`src/`、`apps/`、`doc/contracts/`、`packaging/`、`requirements*` 过滤零命中（与 r2b 独立结论一致）。返修对 `tools/assets.py` 净改动为零（r2b blob 比对 `2c12ba1e`==`8cb3a135`）。

## 4. 集成复跑（本机非沙箱；raw 日志同目录）

| 验证 | EXIT | 结果 | raw |
|---|---:|---|---|
| `git rev-parse HEAD` + `python --version` | 0 | 集成 head 绑定 | [i-integration-env.log](i-integration-env.log) |
| `python -m pytest tests/m2_test_assets -q` | 0 | **25 passed**（复现作者 r2 结果；DSH 沙箱因 `tmp_path` WinError 5 判 BLOCKED_BY_ENV 的项在此闭合） | [i-pytest-assets.log](i-pytest-assets.log) |
| CLI `list --level smoke` | 0 | READY=20 | [i-asset-cli.log](i-asset-cli.log) |
| CLI `verify --language ja --level smoke` | 0 | READY=10 | 同上 |
| CLI `verify --language ko --level smoke` | 0 | READY=10 | 同上 |
| CLI `verify --language ko --level regression --case-id K11 K12 K13` | 0 | READY=3 | 同上 |
| CLI `missing --level regression` | 0 | READY=23 / MISSING=8 / MISSING_GATED_ASSET=37 | 同上 |
| CLI `download --language ko --level regression --case-id K11 K12 K13` | 0 | downloaded=0 existing=6 failures=0（幂等） | 同上 |
| `git check-ignore -v` KO 新 4 文件 | 0 | 4/4 命中 `韩漫_KO/.gitignore:1:/*` | [i-git-boundary.log](i-git-boundary.log) |
| `git ls-files` test_assets 下媒体 | 0 | 0 个 tracked 媒体文件 | 同上 |
| `git diff --check d4d39779..a4cd513d` | 0 | 空输出（干净退出码复测，见该日志尾部） | 同上 |
| `python -m pytest tests/m2_acceptance -q --tb=no` | 1 | **8 failed / 24 passed / 3 skipped**；FAILED 集合与 [acceptance-r2.log](../acceptance-r2.log) 逐条 diff 为空（`FAILURE_SET_IDENTICAL`）——`BASELINE_FAILURE` 维持，非本 Task 引入 | [i-acceptance.log](i-acceptance.log) |

## 5. KO 新资产落地（ignored 本地）

从 Owner worktree `test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/` 非覆盖复制 4 文件到主工作区同路径；源/目标 SHA-256 与 `local_asset_inventory.json` 条目三重一致，合计 16,292,579 bytes：

| 文件 | 大小 | inventory SHA-256 |
|---|---:|---|
| `ep04_Stroke-of-genius_lang-pack.zip` | 14,428,439 | `cff6d3cfef4f…` |
| `kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg` | 659,359 | `4bd9b181ac6f…` |
| `kr_Pepper-and-Carrot_by-David-Revoy_E04P03.jpg` | 602,878 | `3116f5678a5b…` |
| `kr_Pepper-and-Carrot_by-David-Revoy_E04P07.jpg` | 601,903 | `a8d831e5512f…` |

## 6. Findings 处置（代行 Codex 裁决，用户可撤销）

- **P3-8（r1 会话转录入库）**：`verification/M2-TA2C/dsh-review-r1.jsonl`（362,273 bytes，含 Reviewer 思维链、97 处本机绝对路径与掩码 API key/request_id）与 0 字节 `dsh-review-r1.err.log` 已随收口提交**移出 Git 树**；内容可经 `git show 93f7b4b4:verification/M2-TA2C/dsh-review-r1.jsonl` 取证（历史不改写）。**立规：DSH 会话转录（JSONL/err.log）一律不入库；入库仅为 final 报告 md 原字节 + SHA256。** worktree 中 untracked 的 `dsh-review-r2*.{jsonl,err.log}`、`checkpoint-handoff-zcode.md` 已随 `2e784327` 入树者为历史既遂；`.dsh-review-tmp/` 删除曾被策略拒绝，保留原样披露（r2b 报告亦证实无权限）。
- **P3-9（raw log 空白规范化）**：`66dc361d` 将已提交 raw log `pytest-assets-r2-initial-fail.log:96` 的尾随空格规范化（`:96: `→`:96:`；仅空白、未删证据），在此登记为既往既遂披露；两个 blob 版本并存于历史，不构成证据改写。
- **P3-4/P3-5**：STATUS/PLAN 时点措辞已由本次终态回填消解（Task `done`、integration 回填）。
- **P3-6（`source_url` 仅前缀断言、`O01–O08`/`K11–K13` 目录命名不一致）与 P3-10（`checksum_inventory` 无运行时消费、断言覆盖缺口）**：不阻塞集成，留 planning 候选，不在本 Task 扩范围。

## 7. 终态

- Task `M2-TA2C` → `done`；Owner branch/worktree 保留于 `2e784327`。
- 集成后实际覆盖：L0 20/20 READY（JA 10 + KO 10）、L1/L2 68 定义中 23 READY / 8 MISSING / 37 MISSING_GATED_ASSET；inventory 92 文件 / 63,317,229 bytes；应用级 Pipeline 检查全部 `NOT_RUN`（真实状态，不计可运行）。
- 未运行项：`tests/core`（PySide6 环境缺失，历史障碍，非本 Task 范围）；DSH r2b 沙箱内 pytest 全量（BLOCKED_BY_ENV，已由本机复跑闭合）。
