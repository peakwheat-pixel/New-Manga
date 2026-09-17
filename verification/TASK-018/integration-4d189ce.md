# TASK-018 集成验证：`4d189ce`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `dce95acbb57a3494cb0f9d8d2d42e27d164176bb` |
| start head | `9ee17189817ede5564866049e01139b9608f63a7` |
| reviewed head（delivery） | `6c33e7f237f63fd9b777335e72b84fe317cf866b` |
| 元数据 head | `ef6d1c382a5cee8b165217274a6c72db08716188` |
| Review | `doc/reviews/TASK-018-6c33e7f.md`（decision=`approved`，R-001～R-007） |
| implementation merge | `4d189ce`（merge commit，parents `461e639` + `ef6d1c3`） |
| integration commit | `4d189ce` |
| 环境 | Windows `10.0.26200`；固定 Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）；`PYTHONPATH=experiments/TASK-018`、`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM` |

## 复验结果

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m unittest experiments/TASK-018/test_mask_protocol.py -v` | 0 | **12** | **0** | `OK`，与交付一致 | 无（协议自检为纯 Python） |
| 2 | `…python.exe <副本>/experiments/TASK-018/run_experiment.py --repeat 3` | 0 | N/A | N/A | `{"MEASURED": 10, "BLOCKED": 20}`；MEASURED 记录 `protected_violations` 10/10 全为 `[]` | 进程执行无测试项，N/A |
| 3 | 交付 PNG 与样例 SHA-256 重算 | 0 | N/A | N/A | 10/10 `output_sha256` 与 `samples/manifest.json`、`manifest_sha256` 全部吻合 | N/A |
| 4 | `…python.exe -m pytest -q -p no:cacheprovider`（集成后全仓套件） | 0 | **530** | **6** | `530 passed, 6 skipped in ~23 s`；6 项 skip 逐条为 `openssl unavailable`（`tests/network/test_connection_tester.py`、`test_transport_tls.py`） | 环境缺 openssl，与本次变更无关 |

全仓套件在本次集成检查中共运行 7 次：**6 次为 `530 passed, 6 skipped`**，1 次为 `1 failed, 529 passed, 6 skipped`。该次失败未捕获到用例名（输出被过滤），其后连续 4 次重跑均通过。TASK-018 的集成只触及 `experiments/TASK-018/**`、`doc/**` 与 `verification/**`，不在 `pytest.ini` 的 `testpaths = tests` 收集范围内，因此该抖动**不是本次集成引入**，与 STATUS 已登记的 reading_export QML 低频 flaky 移交项性质一致；本文件既不把那次失败记为通过，也不归因于 TASK-018，仅如实登记观察结果。

复验在 `%TEMP%\task018-integration-20260917141520` 的整目录副本中执行：`run_experiment.py` 会把 `results/experiment.json` 写在实验根内，直接在仓库运行会改写该交付物，因此改用副本（该限制本身已登记为 Review R-003）。仓库内 `results/experiment.json` 保持交付时的字节：`ebb4a540e3eea7a98938a8fc7d9afab88e21a0cff2d21ecca0ef9ed663cb178a`；副本重跑输出为 `a0a509b738b80a77d752702e9db515fad0959a523bf89a87a776476e59e62b3e`，两者差异仅来自 `latency_ms` 与 `peak_rss_mb` 的时间/内存抖动。

确定性字段逐项比对（副本输出 vs 交付 JSON）**完全一致**：`routes` 块、`manifest_sha256`、`mask_sha256`、`output_sha256`、`sample_sha256`、`parameters`、`mask`（含 `raw_mask_area`/`final_mask_area`/`bbox`/`final_covers_raw`）；latency 复现差 ≤1 ms，`peak_rss_mb` 波动 ≤1 MB。

## 验收结论

- [x] 五条候选路线的实际可用范围已比较：`simple-fill` 与 `edge-bleed`（**非模型基线**，`learned_model=false`）实测可运行；`manga-lama`、`aot`、`brushnet-powerpaint`、`flux` 因缺 `torch`/`diffusers` 与权重全部 `BLOCKED`（20/30 条记录），且 `output_image`/`latency_ms` 为 `null`、残字与保护字段为 `NOT_RUN`、无 `output_sha256`/`mask_sha256`——**无伪造产物**。
- [x] 固定五类样例（白底/线稿/网点/渐变/结构穿越）连同目标框与保护框入库；`default_eligible` 仅两个基线为 `true`，四条学习型路线全为 `false`。
- [x] `--repeat 3` 实测：10 条 MEASURED，保护违规 10/10 全 0，峰值 RSS 45.45–57.70 MB、`vram_peak_mb=null`（CPU 路径）。
- [x] 白名单越界 0；未修改生产 `src/`、`tests/`、Schema、依赖清单、`AGENTS.md`、其他或冻结 Task；未扩展到 TASK-019；未 push。
- [ ] Mask **内部**结构损伤量化与学习型路线质量/性能：仍为 `NOT_RUN`/`BLOCKED`，**不得视为通过**。

## 未关闭项（Review deferred）

| ID | 级别 | 限制 | 解锁条件 |
|---|---|---|---|
| R-001 | P2 | harness 未按 `protected_boxes` 逐个断言（判据为 final Mask 外全部像素，严格更强） | 随 R-002 一并处理 |
| R-002 | P2 | 路线门控为静态常量，`runnable_here`/`blocked_reason` 不是环境探测结果 | 增加 `find_spec`/权重探测；结果须重跑取证 |
| R-003 | P3 | `--output-dir` 越出实验根即 `ValueError` 退出码 1 并留下部分产物 | 回退绝对路径或写盘前 fail fast |
| R-006 | P2 | `results/experiment.json` 的 `requirements` 键名仍带未核实的体积标注（如 `10GB+`） | 随 R-002 重跑时清理 |
| R-007 | P2（潜在、当前不可达） | 非 `simple-fill` 路线在 runnable 分支会回落到 `edge_bleed_fill` 并被写成 `MEASURED` | **必须先修**，再补 R-002 探测 |

R-001/R-004/R-005/R-006（报告部分）已在集成收口提交内以文档口径修正收口；R-002/R-003/R-007 与数据标签项保持 deferred，限制已写入 [实验日志](experiment-log.md) §7 与 [研究报告](../../doc/research/TASK-018.md) §9。
