# M2-TA3-B2-KO-RERUN 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-TA3-B2-KO-RERUN`；链：`87f61d8b`(含 PRIMARY 语义定稿) → `36971e97`(implement) → `0001d68c`(docs，r1 被审头) → `677cd227`+`0ba046b8`(文档返修，r2 不需要——r1=approved 有条件)
- Review：DSH r1 **approved（有条件）** 0×P0/P1——3×P2 全文档/口径级；DSH 独立复算全部数字成立（CER 6 行逐位/计量 140/140/K02 93/93/相似度 12×1.0+min 0.4615）；停跑方向保守成立（`doc/reviews/M2-TA3-B2-KO-RERUN-36971e97-dsh-r1.md`）

## 运行时核验（集成方，2026-10-02）

- git 门禁：porcelain 干净、`diff --check` EXIT=0、禁改面（src/tests/contracts/packaging/apps/首跑产物/thresholds/STATUS）diff 空
- key 扫描：`sk-[A-Za-z0-9]{20}` 全 diff **0 命中**
- 相似度离线复算：`ko_rerun_similarity.py --case K11` 重算成功——**数值零漂移**（gate FAIL/13 对/min 0.4615）；唯一 diff=`declared` 字段（集成方裸跑未传 `--determinism-track remote`→null，inferred=remote 一致；带参数复现则逐位——**顺带实证 R3 控件的 fail-closed 行为正确**）
- post-merge 三套件：见 close commit

## 集成结论与移交

- **ko 全链 Gate 仍 FAIL（如实）**：F1 解锁实证（K02 93 region 全链 export OK）+F2 解锁（ALLOC 证据）但 7 case 因成本红线停跑待裁决；K11 行为对照一致；K19 F4 维持
- **§7 七项裁决移交用户**（ko-rerun-report.md §7，R7 重构后）：①7 case 范围与预算（107–209 万 est token 上界）②K02 干净重跑（+113k）③相似度 Gate 合法重译口径（CALIB 局限 8 首次自然实测 min 0.4615）④SFX 端到端素材路线 ⑤**50 万红线口径追认**（编排指令数值无任务书背书，R1）⑥F1 关闭口径 ⑦F2 页级必要性
- 成本实际：≈347 成功请求 ≈20.4 万 est token（估计口径 R9 已标注）
