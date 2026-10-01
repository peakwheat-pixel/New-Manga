# M2-SFX-PROD-1 释放证据（release @2f37b63a，2026-10-01）

## 用户三裁决（逐字）
1. 要做（可行性认定通过）2. chiqui7 能用，不在乎（AGPL 争议裁决=接受 MIT 解释）3. 路线 A（独立 SFX 检测器 +41.2MB）。

## 关键侦察
- SfxPolicy 默认 SKIP（models.py:186）→ 误标 sfx=对白被跳过（严重）→ 阈值冻结 conf≥0.50（precision 优先）。
- RegionType.SFX 枚举在位（entities.py:25）+ decide_sfx_translation 门（TASK-035）→ 管线消费面齐备，缺口纯在检测。
- 评估基线：chiqui7 sfx 11/29@0.5（非自比 8/18）、ogkalu 硬盲区部分相交 6/7；推理口径=letterbox 左上贴图+BILINEAR+NMS 0.7 class-agnostic（偏离披露）→ 生产复刻该口径。
- 权重 yolo11s-seg.onnx 41,227,478B（external-evidence-inventory.json 有 sha256）；onnxruntime 1.30.0 CPU 已在评估 venv 验证。
- 契约面：RegionCandidate 无类型槽 → label 前缀 `sfx-<n>` 方案（契约零修订优先，不可行即停）。

## 代理裁决
独立并联 provider（不改两既有 provider）；onnxruntime==1.30.0 追加+进闭包；NEWMANGA_SFX_DETECTION=on 默认（用户裁决落地）；conf≥0.5 冻结可覆盖；权重随包 sha256 校验复制；SFX 候选不进 MERGE_* 对白合并。
