# Integration record：M2-DOCTR-QUAL-RUN（正式 qualification run）

- 集成方：Codex（代行，ZCode 编排会话，用户全权授权 2026-09-28/30）；集成日期 2026-09-30
- base=`5b3a477a`（release）→ claim `6384c807` → 契约适配 `f9894184` → 正式结果 `3b9cf180` → 交付 `eb01cd76` → DSH r1 处置 `4cc7def6`
- Review：DSH 非作者静态 **r1 APPROVED_WITH_MINOR_ISSUES**（"cleared for integration; FAIL verdict matches the frozen criteria item by item"；报告归档 [eb01cd76-dsh-r1](../../../../doc/reviews/M2-DOCTR-QUAL-RUN-eb01cd76-dsh-r1.md)）
- P1-1 集成裁定：**接受 f9894184 契约适配**（不 revert）——适配方向=用户裁决本身（Precision 降非 Gate），测量逻辑零改动，集成方实测 deterministic reproduction=True，三处披露
- 处置落字：P2-1 312→314（集成方从 per_region 重算：314 partial/102 fully matched）；P3-1 +9→+5（zero_detection_regions 重算 2+1+1+1）；P3-3 baseline-dir 显式化；P3-2 README 历史段标注
- 集成验证：集成方实测 deterministic reproduction True（manifest sha256 一致 + summary/per_region 逐字段）；merge=``e8c9c120a5bb3c71ab3f41c32b4985f7578aef61``；post-merge 抽验 results JSON 在 main 可读、Gate 数值一致
- **正式结论（Formal Result: FAIL）**：主判定层 block_coverage（生产 pad 6px）下 Recall **0.4776 < 0.92 FAIL**；Mean coverage 0.7531 ≥0.60 PASS；severe 0.0385 ≤0.05 PASS；Precision 0.1250=受污染观测下界（非 Gate）。附报：pad 抵消 Recall 0.2628（真实区间下界）、block_strict 0.4515、db_resnet50 对照 0.6085（+13.1pp 仍 -31.2pp）、raw_strict 0.1941
- **候选流程（报告 §7，供下一 Task 释放裁决）**：C1 GT 盲区人工校准（**First**，解锁 0.92 Gate 可测性，需用户/授权标注者）→ C2 FAST 阈值扫描（并行低成本探针，预期不改 verdict）→ C3 DBNet 换型（**Hold** 至 C1 报告，部分杠杆不闭 Gate）→ C4 manga 域检测器/微调（**C1 后裁决**，唯一可能逼近 0.92 的候选类）→ C5 合并层（最低优先）
