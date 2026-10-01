# M2-SFX-DETECT-EVAL — 许可证据快照（license evidence）

- 目的：把本 Task 的许可核查从「报告文字结论」升级为**入库的可复核证据**（DSH r1 R4；格式先例=`verification/M2-DOCTR-QUAL/qualification/license-evidence.md`）。
- 抓取方法：HF API 原始 JSON `curl -sSL` 直取（代理 `127.0.0.1:7890`），未编辑；原始响应落 gitignored 外部路径 `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/license-evidence/*.json`（sha256 见下），关键内容摘录于本文件代码块/引文。Manga109-s 数据集卡为 gated（README raw 401），公共卡页条款经 WebFetch 摘录（转述/短引文标注）。
- 抓取时间：**2026-10-01T03:09:21Z**（`fetch-timestamp.txt`；Manga109-s 卡页条款同日抓取）。
- 抓取人：ZCode（Task Owner；非法律意见，许可判定限于「能否用于本内部评估与后续集成风险登记」）。

## 1. Kiuyha/Manga-Bubble-YOLO（NO-GO 候选）

- URL：`https://huggingface.co/Kiuyha/Manga-Bubble-YOLO`；API：`https://huggingface.co/api/models/Kiuyha/Manga-Bubble-YOLO`
- 快照：`api-kiuyha.json`，sha256 `bb78816254b7a489c6433b8158365aed4ef0046e7cefe1ecf95f13391ea73987`（1393 B）
- **HF license tag（API 实证）**：`tags` 含 `license:apache-2.0`；`cardData.license: "apache-2.0"`
- **revision（API 实证）**：`sha: fb646500455e8a8a3a807fd27b855c8e4fc63766`（与权重下载 pin 一致）；`lastModified: 2026-02-17T00:28:51.000Z`
- **ONNX 权重元数据（入库 `onnx-sfx-frames.json`，另一独立证据面）**：`license: "AGPL-3.0 License (https://ultralytics.com/license)"`、`names: "{0: 'text'}"`
- 冲突结论：HF 标签 apache-2.0 与 Ultralytics 权重元数据 AGPL-3.0 主张冲突（用户裁决项）；类别面单类无 SFX。

## 2. chiqui7/yolo11-manga-seg（EVAL 候选）

- URL：`https://huggingface.co/chiqui7/yolo11-manga-seg`；API：`https://huggingface.co/api/models/chiqui7/yolo11-manga-seg`
- 快照：`api-chiqui7.json`，sha256 `20c520b20a91f375a8087e6d92789be7e3e0b600dda65f8c501dd212384d0651`（691 B）
- **HF license tag（API 实证）**：`tags` 含 `license:mit`；`cardData.license: "mit"`
- **revision（API 实证）**：`sha: 7f5f5c0464f2eeb57282f16da760eb8828a8716a`（与权重下载 pin 一致）；`lastModified: 2026-09-17T16:55:28.000Z`
- **ONNX 权重元数据（入库）**：`license: "AGPL-3.0 License (https://ultralytics.com/license)"`、`names: "{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}"`
- 冲突结论：同上 AGPL 争议（用户裁决项）；类别面含独立 sfx 类（本 Task 唯一）。

## 3. cozy-creator/manga-sfx-detector（NO-GO 候选）

- URL：`https://huggingface.co/cozy-creator/manga-sfx-detector`；API：`https://huggingface.co/api/models/cozy-creator/manga-sfx-detector`
- 快照：`api-cozy.json`，sha256 `aa3d5a5355b09054ac4017613abde278c1bf2a6ee615c9e9a25d9c9015b0585e`（730 B）
- **无许可声明（API 实证）**：`tags` 中**无任何 `license:` 项**；`cardData.license: null`；`sha: 4c4d2a6980cc247542326699a60146233dad8eed`；`lastModified: 2025-03-07T08:20:02.000Z`
- 结论：「无许可 + 无独立权重 license statement」由 API 快照直接证实（默认保留所有权利），维持 NO-GO（T1.1.1 权重来源链口径）。

## 4. hal-utokyo/Manga109-s（Kiuyha 训练数据来源；传导核查）

- URL：`https://huggingface.co/datasets/hal-utokyo/Manga109-s`；API：`https://huggingface.co/api/datasets/hal-utokyo/Manga109-s`
- 快照：`api-manga109s-dataset.json`，sha256 `90b4fc48f73ee60c7060307301dd77213c178a3f04d26f23218af5d8908647d6`（2505 B）
- **API 实证**：`cardData.license: "other"`、`license_name: "manga109-s"`、`gated: "auto"`（申请制）；数据集卡发布 Manga109-s-v2026（"Starting from May 21, 2026"）
- 条款摘录（公共卡页，WebFetch 2026-10-01，短引文；完整条款以卡页为准）：
  - 许可行原文：**"License: manga109-s"**
  - 允许：**"Using results, or portions of results, obtained from machine learning experiments or image processing experiments, for commercial use."**（ML/图像处理实验结果——含预训练模型——可用于商用）
  - 禁止：**"Redistribution of the Manga109-s dataset to third parties is forbidden."**（数据集本体禁再分发）；数据集图像不得与结果打包出售、不得作为产品；发表页数上限（每卷 ≤20%）
  - 义务：发表结果（明确含预训练模型）**必须标注使用 Manga109-s 数据集**；署名 "courtesy of [Author's Name]" 并引用相关论文
- **传导结论**：权重（ML 结果）商用可用，条件=显著署名；数据集本体再分发禁止不约束权重文件。Kiuyha 权重的传导风险=「作者是否已履行署名义务不可证」→ 登记为集成前尽调项（非否决项）。本 Task 的 Kiuyha NO-GO 主因仍是**类别面（单类无 SFX）与 Ultralytics AGPL 争议**，与传导无关。

## 5. dmMaze/comic-text-detector（NO-GO 先例引用，未重抓）

沿用 T1.1.1 一手来源链（`doc/tasks/T1.1.1.md` L45-57）：上游 LICENSE GPL-3.0（GitHub raw）、manga-image-translator release 权重无独立 license statement。本 Task 未重新抓取（先例已入库，非本 Task 新事实）。
