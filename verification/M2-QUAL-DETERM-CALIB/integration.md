# M2-QUAL-DETERM-CALIB 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-QUAL-DETERM-CALIB`；链：批次 release `8996ca55`（fork_commit，Task 授权基线 8e0de8d0）→ `e3b7c48d`(implement，r1 被审头) → `2400b57a`(handoff) → `8926f49c`(条件返修，r2 被审头)
- Review 链：DSH r1 `approved_with_conditions`（4×P2=Gate 定义完备性 R1 对齐置换/R2 空跑覆盖/R3 0 对场景/R4 余量语义 + 7×P3 + 3×P4；数字面全部独立复算通过；`doc/reviews/M2-QUAL-DETERM-CALIB-e3b7c48d-dsh-r1.md`）→ Owner 条件返修 R1-R14 全 closed（**复跑一致性：返修前后 calibration.json 逐值零差异**，连续两次重跑 sha256 字节级一致）→ DSH r2 **`approved`（可集成）** 0×新 P0/P1/P2（零数值漂移由 diff 结构证明：6 hunk 全为路径/字段/文本类；`doc/reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md`）

## 正式口径（F5 裁决落地）

确定性 Gate 双轨：**remote 采样翻译链=reading_order 对齐译文相似度（median≥0.95 且 min≥0.70，normalized 口径；0.05 绝对值余量；非空对 n≥1 覆盖前置；0 对 case NO_DATA 豁免不阻断）**；mock/deterministic 链=export 字节逐位（原口径保留）；判轨规则=translate provider 绑定 + runner `--determinism-track remote|mock` 显式记录、不一致 fail-closed。校准锚=K11 浮动对实测 [0.75,0.875]（5/13 normalized 浮动）+合成漂移对照。局限五条+增补登记（n=2、无自然 FAIL、词面口径固有误报方向、长度悬崖、Run1 层未测）。

## 集成运行时项

- r2 新增残留 3×P3+4×P4（脚本文档自相矛盾/恒零字段/判别示例词汇）不阻断——登记后续 hygiene
- post-merge 三套件：本 Task 零 src/tests 改动，基线不变预期（merge 后复跑登记于 close commit）
