# M2-DETECT-WEBTOON-DIAG 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-DETECT-WEBTOON-DIAG`；链：批次 release `8996ca55` → 续接交付 `2d6b7bf6`+`b311f52f`（r1 被审头）→ 返修 `1697bb15`+`a867ff49`（r2 被审头）
- Review 链：DSH r1 `changes_requested`（1×P1 R1=K19 无字页被误写进 tiling Gate、R2 计量层级混淆、R3 NMS 数据不可复算；报告 `doc/reviews/M2-DETECT-WEBTOON-DIAG-b311f52f-dsh-r1.md`）→ Owner 返修 R1-R11 全 closed（R3 选重跑：探针 schema v2，pre/post-NMS 全量框坐标落盘，**226/193 与四页分布精确复现**；「NMS 实测有效」落到数据=33 删框中 30 个中心在重叠带、删除 IoU mean 0.848、带内密度 3.12× 带外）→ DSH r2 **`approved`（可集成）**——r2 独立核对「pre_nms 226 行/post_nms 193 行/nms_removed 33 行由行区间结构精确成立」，R10 的 273ms 出处（M2-PROD-DETECT-2 发布探针 PK-L3-real-inference.warm_avg_ms=273）逐字段为真（报告 `doc/reviews/M2-DETECT-WEBTOON-DIAG-a867ff49-dsh-r2.md`）

## 诊断结论（正式）

**ogkalu 对 webtoon 长条漫 0 候选的根因=整页无 letterbox 各向异性重缩放致目标消失**（生产路径把 690×62133 直传 RTDetrImageProcessor size 640×640，垂直压缩 ~97×；决定性证据=同页同权重同阈值仅改输入分辨率：1024² 块级 0→193 合并前文本框）。修法排序：**A tiling+坐标回映（推荐主线，契约零变更、可行性已实测）** > B per-layout 路由 docTR（粒度语义成本未知，留基线）> C processor size 覆盖（排除）。

## 修复 Task 释放口径（DSH r2 定案，编排会话执行）

- 验收面=**5 张 webtoon_long_strip**（K01/K02/K04/K05/K08）；Gate=「生产 provider.detect region 数>0 且全链可用」（生产 region 层级计量，非合并前文本框）
- K19 单列 F4 口径项（无字页应空成功而非 failed/INVALID_INPUT）
- 参数配置化：块尺寸/重叠/NMS 阈值；qualification 带 ≥2 阈值点候选数曲线 + 690×690 原生尺度块对照
- 性能预算：K01 ≤25s / K02 ≤10s / K04 ≤15s（CPU）
- 授权修改面：`src/infrastructure/providers/detection_manga.py` + 检测参数配置通道（修复 Task release 时冻结）

## 运行时项

- 探针复跑：Owner 返修轮已重跑（19793→19811ms 精确复现），DSH r2 独立核对行区间结构成立；集成方不再重复
- git 层：porcelain 干净、diff --check EXIT=0（Owner 自检+DSH 静态核对一致）
- post-merge 三套件：本 Task 零 src/tests 改动，基线不变预期（merge 后复跑登记于 main close commit）
