# M2-SFX-T5-TILE-KO 部署记录与性能双档呈报（tile-deploy-report）

- Task: [M2-SFX-T5-TILE-KO](../../doc/tasks/M2-SFX-T5-TILE-KO.md)（branch `agent/zcode/M2-SFX-T5-TILE-KO`，base `a3b0f537`）
- 生成: 2026-10-06，Owner=ZCode
- 权重: 生产 pin v2b `944e8114…`（本 Task 零权重变更）；chiqui7 `d87389af…` 为回滚 pin（AC3 进程内重指出证）

## 1. 部署形态呈报（AC2，用户终选=收口呈报项，不阻塞本 Task）

tile 冻结口径（1024/896/128/NMS 0.5）conf 0.5，KO 4 页（58/112/70/21 tiles/页），
协议=每页 warm-up 1 次不计 + 计测 1 次（`experiments/M2-SFX-T5-TILE-KO/perf_tile_dual.py`，
原始行 `raw/perf-run.log`，汇总 `raw/perf-summary.json`）：

| 页 | 尺寸 | tiles | CPU 生产 EP v2b | GPU DML v2b | GPU DML chiqui7 |
|---|---|---|---|---|---|
| pre-k08 | 690x51971 | 58 | 9.26s | 0.95s | 1.13s |
| pre-k09 | 690x100480 | 112 | 17.96s | 1.89s | 2.19s |
| pre-k01 | 690x62133 | 70 | 11.24s | 1.14s | 1.37s |
| pre-k02 | 600x18401 | 21 | 3.36s | 0.34s | 0.41s |
| **合计/均值** | — | 261 | 41.82s / 10.46s | 4.32s / 1.08s | 5.10s / 1.27s |

- CPU 档=生产部署形态（`_build_engine` 原样 `CPUExecutionProvider`，轻量栈裁决）；GPU 档=
  独立 task-env venv（`M2-SFX-T5-TILE-gpu`，onnxruntime-directml 1.24.4，
  `DmlExecutionProvider`，RTX 5070 Ti），生产引擎冻结 CPU EP，GPU session 仅替换
  engine tuple 内的 session、tile 序列=生产代码逐字（可比性口径）。
- ORT 运行期 warning 如实登记：DML 会话存在未分配到 preferred EP 的节点（shape 类 op
  被 ORT 显式留 CPU），见 `raw/perf-run.log`。
- 参照：T3/KO-TILE 校准轮 chiqui7 CPU tile 实测 8.9s/页（71.6s/522 tile-passes）；本轮
  CPU v2b 均值 10.46s/页同量级。directional 数据如实登记不作质量判定；部署形态终选
  （CPU 单档 / GPU 加速档）留用户裁决。

## 2. AC 证据总表

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 tile 分支 | **PASS** | `src/infrastructure/providers/detection_sfx.py`：tile 路由分支（`_routes_to_tile`：宽≤690 且 aspect≥8.0 走 tile，否则 letterbox 原路径逐字不变）；冻结口径常量 `SFX_TILE_HEIGHT=1024`/`SFX_TILE_OVERLAP=128`/`SFX_TILE_NMS_IOU=0.5`（KO-TILE 提案 §3 逐字，T3 评测矩阵锚定数字）；路由阈值常量+登记依据（KO 域观测宽 600/690、aspect 30.7-145.6，T3 raw page_size；普通页 ~1.4）；`NEWMANGA_SFX_TILE` on/off 开关+`NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W`/`_ROUTE_MIN_ASPECT`/`_HEIGHT`/`_OVERLAP`/`_NMS_IOU` 覆盖，空/非法值=命名变量的 fail-fast `ValueError`，先于权重解析与任何推理。commit `98338691` |
| AC2 性能双档 | **PASS** | §1 表；双档原始数据 `raw/perf-summary.json`（faces: cpu_v2b/gpu_v2b/gpu_chiqui7） |
| AC3 KO 域验收 | **PASS** | `raw/parity-{v2b,chiqui7}.json` + `raw/parity-summary.json` + `raw/parity-run.log`：**v2b 35/56（派生 GT）+48/135（非派生 npd GT）、chiqui7 56/56+41/135 全部逐位复现**（生产 tile 分支 conf 0.5；逐页 `bit_parity_vs_t3_raw=True` vs T3 raw eval JSON 写盘精度 xyxy 0.1/conf 4 位，matched 数字与 T3 矩阵逐位）；BJ 考卷 pre-bj17/pre-bj18 chiqui7 letterbox 重跑 preds 与 T3 raw 逐位一致（`sfx_route=letterbox`，零变化实证）。权重纪律：v2b=生产 pin 原样零重指；chiqui7=sha 先验断言（d87389af）→进程内重指→finally 恢复（tile_calib/eval_gate_t3 先例） |
| AC4 契约与测试 | **PASS** | `contracts/**` 零 diff（RegionCandidate 输出面不变）；单测先红（`raw/test-red-before-impl.log`：ImportError `SFX_TILE_HEIGHT` collection error）后绿（`raw/test-green-after-impl.log`：70/70）；全量回归 `raw/regression-run.log`：**1812 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=main 基线一致**（1812=基线 1780+本轮 32 个新 tile 用例）。commit `c9880955` |
| AC5 文档 | **PASS** | 本报告（部署记录）+Task 交付记录回填+Handoff；**T4 承接项 r1 P3-2 闭合**：tile 冻结参数运行期断言落地 `_assert_tile_caliber`（typed `ProviderInvalidOutput`，非 `assert` 语句、不可被 `-O` 剥除；校验面=非空+首锚点 0+相邻差=冻结步长或页底锚点+末锚点覆盖页底+锚点非退化；`_tile_ys` 每次调用断言，单测 5 面） |

## 3. 运维与回退注记

- 路由面：`sfx_route`（letterbox/tile）+ tile 参数进 detect options（审计可见）；普通页
  letterbox 唯一新增=该审计键，候选输出零变化（AC3 BJ 逐位实证）。
- 关闭开关：`NEWMANGA_SFX_TILE=off` 恢复 pre-T5 letterbox 行为（KO 页回到 0 sfx 响应的
  已知结构性事实）；单测钉住。
- 已知限制（如实登记）：①宽≠600/690 的 KO 形页按常量阈值参数化路由，未逐宽重校
  （KO-TILE §9 既有登记）；②KO 4 页相位依赖——若复测偏离 56/56（chiqui7 派生 GT 上界）
  先查 GT 相位与页图 sha；③GPU 档为呈报数据，生产引擎仍冻结 CPU EP，启用 GPU 属部署
  形态用户终选+后续 Task。
- 权重/GT 数据不入 Git：weights 与 npd-gt.json/R2 manifest 均在 gitignored 外部树
  （路径见 `verify_tile_parity.py` 头部）。
