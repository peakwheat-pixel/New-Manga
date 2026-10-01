# M2-SFX-DETECT-EVAL 释放证据（release @a9b054e8，2026-10-01）

## 授权

用户在 REBASELINE 第四轮盘点（governed @`a9b054e8`）的三个候选中裁决**「2. SFX 拟声词检测」**（2026-10-01）——产品方向裁决 + 既有自治/全权授权。

## 侦察事实

1. 产品面 SFX 策略门已存在（Legacy TASK-032/035 done：`region_type==sfx` + `SfxPolicy` + `decide_sfx_translation`）——缺口在检测/分类。
2. C1 裁定（c1-spot-audit-report.md §7 L116）：SFX 检测需另立任务、涉及伪 GT 重标注、超出检测器范畴；现状=检出不稳定（6 检出 FP + 4 零检出帧）。
3. 候选调研（WebSearch 2026-10-01）：dmMaze/comic-text-detector=GPL-3.0 双证（GitHub+HF 镜像）→ 沿用 T1.1.1 NO-GO；Kiuyha/Manga-Bubble-YOLO=HF ONNX、Manga109-s 域、许可待核查（首要候选）；ogkalu 无 SFX 类（现状基线）。
4. 域适配风险：Manga109-s（日漫印刷）→ KO webtoon（韩漫长条）；C4 教训=文档域权重在韩漫 FAIL。
5. GT 现状：KO GT 无 SFX 标注；正式重标注=集成前条件；评估走 directional 口径（agent 视觉预判+样本入库可复核，正式用户审核留集成前）。

## 代理裁决

评估域=KO 素材优先；许可门先行（NO-GO 即缩水交付分支）；现状抽检 ≥20 帧 directional；生产零改动（experiments/verification/Task/Handoff only）。
