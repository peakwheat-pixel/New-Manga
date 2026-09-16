# TASK-016 实验验证记录

## 固定对象

- Worktree：`G:/CODEX/New Manga.worktrees/TASK-016-deepseek`
- Branch：`agent/deepseek/TASK-016-ocr-detection-experiment`
- Base：`f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`
- Owner：DeepSeek Harness
- Reviewer：Codex（非作者独立 Review，待交付）
- 日期：2026-09-16（Asia/Shanghai）

## 环境证据

| 项 | 实际值 |
|---|---|
| OS | Windows 11 `10.0.26200` |
| 架构 | AMD64 |
| Python | 3.12.3，`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe` |
| PySide6 | 6.11.2 |
| Qt platform override | `QT_QPA_PLATFORM=None` |
| GPU | NVIDIA GeForce RTX 5070 Ti，16303 MiB，driver 616.92 |
| GPU used at probe | 4094 MiB |
| Optional runtime | `manga_ocr`、Pillow、torch、transformers、paddleocr、paddle、onnxruntime、openai：均未发现 |
| API | endpoint/model 配置未发现；未发送网络请求 |

## 实际命令与结果

| 场景 | 命令 | 退出码 | passed | skipped | 结果/证据 |
|---|---|---:|---:|---:|---|
| 自制样本生成 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe experiments/TASK-016/generate_samples.py --output-dir experiments/TASK-016/samples` | 0 | N/A | N/A | PASS；5 个 PNG + manifest |
| 协议自检 | `PYTHONPATH=experiments/TASK-016 G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m unittest discover -s experiments/TASK-016 -p 'test_*.py' -v` | 0 | 4 | 0 | PASS；单 Region、Tile global、顺序、fallback |
| Provider 探测 | `PYTHONPATH=experiments/TASK-016 G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe experiments/TASK-016/run_experiment.py --manifest experiments/TASK-016/samples/manifest.json --output experiments/TASK-016/results/probe.json` | 0 | 0 | 0 | 15 条均 BLOCKED；见 probe.json |
| 显式模型运行探测 | 同上并追加 `--run-models`，输出 `experiments/TASK-016/results/model-run-blocked.json` | 0 | 0 | 0 | 15 条均 BLOCKED；未安装/下载/联网 |
| 生产仓库测试 | N/A | N/A | N/A | N/A | TASK-016 禁止修改/创建生产 tests；模型质量不能由仓库既有测试替代 |

Provider 探测的 15 条记录按 5 个样本 × 3 路线展开：

| 路线 | passed | skipped | blocked | 原因 |
|---|---:|---:|---:|---|
| `manga-ocr` | 0 | 0 | 5 | 缺少 `manga_ocr` |
| PaddleOCR Korean | 0 | 0 | 5 | 缺少 `paddleocr` 和/或 `paddle` |
| OpenAI-compatible Vision | 0 | 0 | 5 | 缺少 endpoint/model 配置 |

所有 Provider 质量字段均为 `NOT_RUN`，包括文本错误、坐标误差、阅读顺序误差、耗时、RSS、VRAM；模型权重 Hash 为 `NOT_AVAILABLE`。没有 Mock 输出，没有下载模型，没有读取 secret 值。

## 证据文件 Hash

| 文件 | SHA-256 |
|---|---|
| `experiments/TASK-016/samples/art_text.png` | `109704b18c4917cb068e38f9e9f213fe81389bd36f1cd6c6175c977b00ceaada` |
| `experiments/TASK-016/samples/jp_horizontal.png` | `fe18507633d389bbbad0dbbe163c192cedc7509a4ad0418b557e3fa9e68f1bfb` |
| `experiments/TASK-016/samples/jp_vertical.png` | `bda605e03b715fcbca25dd3492b6ca83d0e6d63bc49468da3e3933128d014f66` |
| `experiments/TASK-016/samples/ko_horizontal.png` | `8700cbb9e9bc13af23f70e19c52ae292147a67ce0ddb33939289f9bf62fb9c36` |
| `experiments/TASK-016/samples/long_tile.png` | `c560a0c2fca88503a72a99e775b3e25ada7b114918868379ac38247b6cc979d1` |
| `experiments/TASK-016/samples/manifest.json` | `5e988b9b65d85ef87d947cbd1a9f74b18af3e4c9fb676a5ae82022c8d5fe4cf3` |
| `experiments/TASK-016/results/probe.json` | `bd33d38fd62ce3e268c168eaa22f5bfe1b352839bbb4d26a60dbd820bde18ee4` |
| `experiments/TASK-016/results/model-run-blocked.json` | `7a8b0afd78a5bab6e714caf88d40864297416fd52340e2483980aeda6a61be0e` |

## 未完成项 / 阻塞

- 真实 OCR/检测质量：`BLOCKED/NOT_RUN`，隔离环境没有 Provider 依赖和模型权重。
- 真实延迟/RAM/VRAM：`BLOCKED/NOT_RUN`；GPU 可见但没有可运行权重。
- OpenAI-compatible Vision：`BLOCKED/NOT_RUN`；没有合法 endpoint/model 配置，未发送请求。
- 低质量、艺术字和长图的真实识别错误率：`NOT_RUN`；自制样本已生成，不能将协议自检结果表述为模型质量。
- 许可：代码仓库许可已由官方来源记录；实际权重下载后仍需记录权重 Hash 与随附许可，尤其是 Qwen 路线。

本记录只证明实验 harness 和样本/协议证据可复现，不代表产品 Provider 已选定、生产接口已实现或任何质量阈值已满足。
