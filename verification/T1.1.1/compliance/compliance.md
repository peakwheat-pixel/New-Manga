# T1.1.1 合规证据（docTR fast_base）

抓取日期：2026-09-21（本机有网络环境；每个留档文件附 URL 与 SHA-256，
可复核）。本文件只汇总事实与来源，不构成法律意见。

## 1. 留档清单

| 文件 | 来源 URL | 大小 | SHA-256 |
|---|---|---:|---|
| `doctr-v1.1.0-LICENSE` | https://raw.githubusercontent.com/mindee/doctr/v1.1.0/LICENSE | 11,336 | `ef94534ac5ceb006211a9c6c1dcf54e357a9e864bbbeb50fb9f79e920a1e3973` |
| `doctr-v1.1.0-README.md` | https://raw.githubusercontent.com/mindee/doctr/v1.1.0/README.md | 16,928 | `b06c87c9aefd4db42b91682fa00ce0be34c0fc5f4541e0fa4977cb764f7d0a77` |
| `doctr-v1.1.0-docs-using_models.rst` | https://raw.githubusercontent.com/mindee/doctr/v1.1.0/docs/source/using_doctr/using_models.rst | 44,990 | `6b834063f845f17e35b7f7f5322dc254dab65484ed8708251deccb39e18060a5` |
| `doctr-v1.1.0-docs-datasets.rst` | https://raw.githubusercontent.com/mindee/doctr/v1.1.0/docs/source/modules/datasets.rst | 27,566 | `6dab40c0432a0557e27338553e57371185e12ce38b54a9d29a30c6fbee827e4a` |
| `doctr-v1.1.0-docs-sharing_models.rst` | https://raw.githubusercontent.com/mindee/doctr/v1.1.0/docs/source/using_doctr/sharing_models.rst | 6,229 | `6406ebf90e1498af772d09fa109758b0cd5347a98cc60c182969164e8e4fa1ab` |
| `pypi-python-doctr-1.1.0.json` | https://pypi.org/pypi/python-doctr/1.1.0/json | 36,093 | `63cbbf892f2659bdf57a574b355bde7acdde54140f16f105bee4255e1c936940` |

## 2. 逐项结论与证据

### 2.1 代码许可：Apache-2.0

- `doctr-v1.1.0-LICENSE`：完整 Apache License 2.0 文本，落款
  `Copyright 2022 Mindee`；
- `doctr-v1.1.0-README.md` §License（L394-396）：
  *"Distributed under the Apache 2.0 License."*；
- `pypi-python-doctr-1.1.0.json` `info.license` 为 Apache-2.0 全文，
  classifier 含 `License :: OSI Approved :: Apache Software License`；
- `requires_dist` 与本仓库 requirements 的选择一致：
  `torch<3.0.0,>=2.0.0`（本任务 pin 2.14.0 在此范围内）。

### 2.2 权重与再分发

- 权重文件 `fast_base-688a8b34.pt` 由 docTR 官方静态 CDN 分发
  （`doctr-static.mindee.com`，URL 见 `fetch_doctr_weights.py`），SHA-256
  `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace`
  与上游发布一致（评估与实现两侧独立校验，见 author-verification.md §1）；
- 上游**没有**对预训练权重单独发布许可文件；docTR 仓库以
  Apache-2.0 整体许可（§2.1），`using_models.rst` L109/L117 说明
  `pretrained=True` 从官方渠道加载对应权重，未附加其他条款；
- `sharing_models.rst`：社区模型共享机制经由 Hugging Face Hub；
  本任务权重不来自 HF Hub，而是上游官方 CDN，因此不受第三方
  Hub 仓库可能附加的条款影响。

### 2.3 训练/评估数据

- `using_models.rst` L58/L86/L142/L170：docTR 官方模型的 benchmark
  基于**公开数据集**，检测模型以 FUNSD、CORD 的训练与评估集评估；
- `datasets.rst`：docTR `doctr.datasets` 支持的数据集类清单
  （FUNSD、SROIE、CORD、SVHN、SynthText、COCOTEXT 等），均为公开
  学术/文档理解数据集；
- 本任务**不**训练、不微调、不再分发数据集，只消费官方权重文件做
  前向推理。

### 2.4 本项目再分发姿态

- 生产路径零下载：权重由用户/运维经
  `verification/T1.1.1/scripts/fetch_doctr_weights.py` 显式获取并做
  SHA-256 门控（作者验证记录 §1）；
- 依赖入 requirements.txt 的只有包级 `python-doctr==1.1.0`（含其
  PyPI 元数据中声明的许可）；权重文件不进入本仓库，不随代码分发。

## 3. 边界（如实声明）

1. 上游无单独的权重许可文本：以仓库 Apache-2.0 整体许可 +
   官方 CDN 无附加条款文件为证据基线。若未来上游发布独立的
   weights LICENSE，需重新核对；
2. 训练数据集的**原始**采集许可由上游数据集维护方各自声明
   （FUNSD 等公开数据集），本任务留档的是 docTR 对其使用的官方
   陈述，不替代对每个数据集条款的法务复核——仅在"再分发数据集"
   时才成为必要动作，本项目无此行为；
3. 商用/对外分发的最终合规裁决超出本技术任务的授权范围，
   由产品/法务流程负责。
