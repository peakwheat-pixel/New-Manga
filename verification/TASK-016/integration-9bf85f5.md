# TASK-016 集成验证：`9bf85f5`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86` |
| reviewed head | `f5442615911cf60125fe8bde604c5237f482610b` |
| metadata head | `81532749586f0a30eb02b780b11fa6eb691dd244` |
| Review | `878ac161425b95f8c8513b0c664ca99780f299fa` |
| integration commit | `9bf85f5` |
| 环境 | Windows；固定 Python 3.12 环境；`QT_QPA_PLATFORM` 为空，未设置 offscreen |

## 复验结果

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `$env:PYTHONPATH='experiments/TASK-016'; …python.exe -m unittest experiments/TASK-016/test_protocol.py -v` | 0 | **5** | **0** | 协议测试全部通过 | 无 |
| 2 | `…python.exe experiments/TASK-016/run_experiment.py --manifest experiments/TASK-016/samples/manifest.json --output <temp>/probe.json` | 0 | N/A | N/A | **30 BLOCKED**；6 候选 × 5 样本 | 探测进程无测试项，N/A |
| 3 | `…python.exe experiments/TASK-016/run_experiment.py --manifest experiments/TASK-016/samples/manifest.json --output <temp>/run-models.json --run-models` | 0 | N/A | N/A | **30 BLOCKED**；`blocked_with_metrics=0`；离线开关 `1,1,1` | 探测进程无测试项，N/A |
| 4 | 预置 `HF_HUB_OFFLINE=0`、`TRANSFORMERS_OFFLINE=0`、`HF_DATASETS_OFFLINE=0` 后执行同一 `--run-models` 命令 | 0 | N/A | N/A | **30 BLOCKED**；`blocked_with_metrics=0`；离线开关仍为 `1,1,1` | 探测进程无测试项，N/A |

临时输出目录为 `C:\Users\49745\AppData\Local\Temp\task016-integration-4f262eedd2d44def8b5a6de09b96dc68`。实际输出 SHA-256：`probe.json=905a7cc37d892dde82d534834b9b961f48b6433f8a71fd2815c6d2343ee1f503`、`run-models.json=6d0d64d807d60904389d8420be8a9403d35766ccb0a1de1b0a867c909a56d84f`、反例输出同为 `6d0d64d807d60904389d8420be8a9403d35766ccb0a1de1b0a867c909a56d84f`。临时 JSON 的 `image_path` 使用主工作区绝对路径，因此与交付物中保留的来源 worktree 路径导致的固定 SHA 不同；状态、字段门控和计数均已独立核对。

## 验收结论

- [x] 协议层保留 `region_id`、Tile-local → page-global 坐标和稳定阅读顺序。
- [x] Provider 探测覆盖 6 个候选、30 条记录；缺依赖/权重/端点时全部 `BLOCKED`，没有伪造模型质量或性能指标。
- [x] `--run-models` 在正常与离线环境变量反例下均强制三项 HF 离线开关为 `1`；失败路径不进入未满足前置条件的模型构造器。
- [x] `detector-yolo` 保留为 `DOCUMENTATION_ONLY`，不表示本仓库已有实现；真实 OCR/检测质量与性能继续为 `BLOCKED`/`NOT_RUN`。

首次未设置 `PYTHONPATH` 的协议命令出现导入错误；按仓库 README 补设 `PYTHONPATH=experiments/TASK-016` 后复验为 **5 passed / 0 skipped**。未修改生产 `src/`、`tests/`、Schema/migration、依赖清单、AGENTS 或其他/冻结 Task；未 push。
