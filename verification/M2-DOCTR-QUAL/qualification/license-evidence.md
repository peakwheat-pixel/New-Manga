# M2-DOCTR-QUAL-C4 — 许可证据快照（license evidence）

- 目的：把 C4 选型的许可核查从"Handoff/报告的文字结论"升级为**入库的可复核证据**（DSH r1 R6）。
- 抓取方法：公开 API 的原始 JSON 响应，`curl -sSL` 直取，未编辑；原始响应文件落 gitignored 外部路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/license-evidence-*.json`（sha256 见下），关键内容全文摘录于本文件代码块。
- 抓取时间：**2026-09-30T07:25:19Z**（选型核查与正式评测同日；原始选型核查亦为 2026-09-30）。
- 抓取人：ZCode（Task Owner，非法律意见；许可判定限于"能否用于本内部评估"）。

## 1. 采用候选：ogkalu/comic-text-and-bubble-detector（Apache-2.0）

来源 URL（两种口径均查）：

- 模型卡（页面标注）：`https://huggingface.co/ogkalu/comic-text-and-bubble-detector` — License 栏 **apache-2.0**
- API（结构化元数据）：`https://huggingface.co/api/models/ogkalu/comic-text-and-bubble-detector`

API 原始响应摘录（快照 sha256 `d1f86737c14ad271e819ee04beba346ccdcebc32a7e7626a43d12dc3e4b71428`，1050 B）：

```json
{"id":"ogkalu/comic-text-and-bubble-detector","private":false,
 "tags":["onnx","safetensors","rt_detr_v2","license:apache-2.0","region:us"],
 "modelId":"ogkalu/comic-text-and-bubble-detector","author":"ogkalu",
 "sha":"16e8a622f91fabc6b5b65c96d32d1183f8843546",
 "lastModified":"2026-05-15T04:38:36.000Z","gated":false,"disabled":false,
 "config":{"architectures":["RTDetrV2ForObjectDetection"],"model_type":"rt_detr_v2"},
 "cardData":{"license":"apache-2.0"},
 "siblings":[{".gitattributes"},{"README.md"},{"config.json"},
   {"detector-v4-s_int8.onnx"},{"detector.onnx"},{"detector_int8.onnx"},
   {"model.safetensors"},{"preprocessor_config.json"}],
 "createdAt":"2025-03-13T18:38:54.000Z",
 "safetensors":{"parameters":{"F32":42861209},"total":42861209},
 "usedStorage":469741850}
```

（摘录保留原字段值；`siblings` 数组简写为文件名列表，完整结构见原始快照。）

`?blobs=true` 变体（快照 sha256 `96f8c7e63ca73cbf4e22d1bbf8b22c144404f693c036c3fd54f399acfd7ec1d5`，2052 B）关键摘录——**服务端 LFS sha256 与本地实测 pin 交叉验证一致**：

```json
{"rfilename":"model.safetensors","blobId":"5bc8fe7532da222dea5c2be436810ff44d8a31a6",
 "size":171543900,
 "lfs":{"sha256":"037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d",
        "size":171543900,"pointerSize":134}},
{"rfilename":"detector.onnx","size":168481531,
 "lfs":{"sha256":"065744e91c0594ad8663aa8b870ce3fb27222942eded5a3cc388ce23421bd195",...}},
{"rfilename":"detector_int8.onnx","size":43838857,
 "lfs":{"sha256":"b5022ad46416b6fe4f88b0cc082cfd2ff5b1cfc624088c2f19879485493f5913",...}},
{"rfilename":"detector-v4-s_int8.onnx","size":11120765,
 "lfs":{"sha256":"5fe9e4f576e49d4e7e8b0e029d6d3cdc252abd4694113e1cae120e62c931ea79",...}},
{"rfilename":"config.json","blobId":"59bc8ad3e2d84dbbdf9258accf50c73131b467d8","size":2320},
{"rfilename":"preprocessor_config.json","blobId":"ea1fbb1edd242104e70301472d089735c68c5f21","size":470}
```

证据链结论：

1. **许可**：API `tags` 含 `license:apache-2.0` 且 `cardData.license = "apache-2.0"`，与模型卡页面标注一致 → 评估采用无许可障碍（Apache-2.0 商用友好，无 copyleft 义务）。
2. **版本 pin（R5）**：本评估所下载权重的 revision = **`16e8a622f91fabc6b5b65c96d32d1183f8843546`**（API `sha` 字段；`lastModified` 2026-05-15）。
3. **权重指纹（强化）**：服务端 LFS sha256 `037930a8...3df80d` 与本地 `sha256sum` 实测 pin **逐字符一致**（此前为"本地实测 + 字节数核对"，现升级为服务端官方元数据交叉验证）。
4. **参数量佐证（R11 相关）**：API `safetensors.parameters.F32 = 42,861,209`（≈42.9M），与模型卡口径一致；pinned `config.json` 证明 `RTDetrV2ForObjectDetection` / `model_type=rt_detr_v2` / backbone `rt_detr_resnet`。
5. **ONNX 变体存在性（R5）**：同一 revision 含 `detector.onnx`（168,481,531 B）、`detector_int8.onnx`（43.8 MB）、`detector-v4-s_int8.onnx`（11.1 MB）。**本评估不采用 ONNX 变体**：评估入口走 transformers `RTDetrV2ForObjectDetection` 检查点（与 docTR 基线的 torch 推理栈同构，避免引入 onnxruntime 这一额外推理栈变量）；`detector-v4-s_int8` 疑似更新的 v4 量化版本，但无 transformers config/checkpoint 配套、无法与 pinned `config.json` 核对结构，不在本评估范围内。

## 2. 备选候选（未采用）：dmMaze/comic-text-detector（GPL-3.0）

来源 URL：`https://api.github.com/repos/dmMaze/comic-text-detector`

API 原始响应关键摘录（快照 sha256 `58b009313e7e48f31bf65480437b1df210164c7a28f5f8d20dd6ee92b3a0b698`，6242 B）：

```json
{"license":{"key":"gpl-3.0","name":"GNU General Public License v3.0",
            "spdx_id":"GPL-3.0",
            "url":"https://api.github.com/licenses/gpl-3.0",
            "node_id":"MDc6TGljZW5zZTk="},
 "default_branch":"master","pushed_at":"2023-08-13T08:42:38Z", ...}
```

证据链结论：`license.spdx_id = GPL-3.0`（与仓库 LICENSE 文件一致）。GPL-3.0 对**本地不分发的内部评估**本身可用，但带 copyleft 传染义务；叠加权重获取依赖 manga-image-translator 第三方 release / Google Drive（无官方校验和直链）与 YOLOv5+DBNet 双模型适配成本，判定为"备选未采用"（ogkalu 已满足 AC1「至少一个候选完成全链」）。该判定为选型取舍记录，不是 GPL 合规意见。

## 3. 局限

- 快照为抓取时点证据（2026-09-30T07:25:19Z）；上游 repo/模型卡此后变更不在本证据覆盖内。引用本评估结论时应连同 revision `16e8a622...` 一起引用。
- 本文件是许可事实的工程归档，不构成法律意见；如未来将该模型用于生产分发，须按 Apache-2.0 条款（含 NOTICE/归属）另行做合规核查（报告 §7.3 集成 Task 范围）。
