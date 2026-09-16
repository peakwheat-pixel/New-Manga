# TASK-016：OCR 与检测路线独立实验

本目录是独立实验，不是生产 Provider，也不改变任何 `src/`、`tests/`、Schema 或共享 Protocol。
实验默认只做环境/依赖探测和协议自检；只有显式传入 `--run-models`，并且本机已有模型权重或已授权的 OpenAI-compatible 端点时，才会发起真实推理。

## 可复现入口

在仓库根目录执行：

```powershell
$env:PYTHONPATH='experiments/TASK-016'
$env:PYTHONDONTWRITEBYTECODE='1'
python experiments/TASK-016/generate_samples.py --output-dir experiments/TASK-016/samples
python experiments/TASK-016/run_experiment.py --manifest experiments/TASK-016/samples/manifest.json --output experiments/TASK-016/results/probe.json
python -m unittest discover -s experiments/TASK-016 -p 'test_*.py' -v
```

`run_experiment.py` 默认不联网、不下载模型、不读取 secret 值。缺少 Provider 依赖、权重或端点时，每个样本都会输出 `BLOCKED`，并将识别错误、坐标/顺序、耗时、RAM、VRAM 留为 `NOT_RUN`。

## 样本

`generate_samples.py` 生成自制 PNG 与 manifest，覆盖：日文横排、日文竖排、韩文、艺术字/旋转文本和长图 Tile。manifest 同时保存人工标注的参考文本、参考区域、Tile 原点及样本 SHA-256；这些自制样本不代表真实漫画分布，也不授予任何产品质量阈值。

## 输出协议

Provider 输出统一成实验记录：`sample_id`、`region_id`、`text`、`polygon`、`reading_order`、`coordinate_space`、`latency_ms`、`ram_mb`、`vram_mb`。Tile 检测框必须先标记为 Tile-local，再加 Tile origin 映射到 page-global；单 Region OCR 的结果必须带回原始 `region_id`。协议自检属于实验 harness，不是生产接口契约。
