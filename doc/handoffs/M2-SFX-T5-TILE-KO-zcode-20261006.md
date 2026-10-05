---
task_id: M2-SFX-T5-TILE-KO
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（非作者 Review）
base_commit: a3b0f537
delivery_head: 24ae2765（verify 收口；docs commit 随后）
status: delivered
---

# Handoff：M2-SFX-T5-TILE-KO — SFX KO 长条页 tile 化生产分支

## 交付结果

AC1-AC5 全 PASS。生产 `SfxDetectionProvider.detect` 新增 KO 长条页 tile 路由分支：
宽≤690 且 aspect≥8.0 走 tile_ov128 冻结口径（tile 高 1024/步长 896+末尾补页底锚点/
页级跨 tile NMS IoU 0.5 conf 降序稳定贪心，T3 评测实现逐字等价），普通页 letterbox
原路径零变化（仅加 `sfx_route` 审计键）；`NEWMANGA_SFX_TILE` on/off 开关 + 5 个
`NEWMANGA_SFX_TILE_*` 覆盖，非法值推理前 fail-fast；T4 承接项 r1 P3-2（tile 冻结参数
运行期断言）落地闭合。

变更路径（全部在 Task 允许面内）：

- `src/infrastructure/providers/detection_sfx.py`（唯一 src 文件：tile 常量段/
  `_TileConfig`/`_tile_config`/`_routes_to_tile`/`_tile_ys`/`_assert_tile_caliber`/
  `_tile_page_nms`/`detect` 路由/`_detect_tiles`）
- `tests/providers/test_detection_sfx.py`（+32 用例）
- `experiments/M2-SFX-T5-TILE-KO/verify_tile_parity.py`（AC3 等价性验证脚本）、
  `perf_tile_dual.py`（AC2 双档性能脚本）
- `verification/M2-SFX-T5-TILE-KO/**`（tile-deploy-report.md + raw/*）
- `doc/tasks/M2-SFX-T5-TILE-KO.md`（claim+交付记录回填）、本 Handoff

提交链（分支 `agent/zcode/M2-SFX-T5-TILE-KO`，base `a3b0f537`）：

1. `c11a2a9d` claim（ready→owner_claim，用户裁决 2026-10-05「三件都同意」授权）
2. `98338691` impl（AC1/AC5-P3-2：tile 分支+路由阈值+env 通道+运行期断言）
3. `c9880955` test（AC4：先红后绿 32 用例）
4. verify commit（AC2/AC3：parity/perf 脚本+raw 证据+deploy report）
5. docs commit（AC5：Task 交付记录+Handoff）

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 tile 分支+env fail-fast | `pytest tests/providers/test_detection_sfx.py`（32 新用例：路由边界/冻结常量/env 20 格 fail-fast/off 开关） | T1.1.1-impl-py312 venv @ impl `98338691` | PASS（70/70） | `verification/M2-SFX-T5-TILE-KO/raw/test-green-after-impl.log` |
| AC4 先红 | 同上命令（实现前） | 同上 @ test 文件先行 | 红（collection error ImportError SFX_TILE_HEIGHT） | `raw/test-red-before-impl.log` |
| AC3 v2b 逐位复现 | `M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe experiments/M2-SFX-T5-TILE-KO/verify_tile_parity.py` | 生产 pin 原样（944e8114），CPU 生产 EP @ impl+verify | **PASS：ko-tile 35/56 + ko-npd 48/135，逐页 bit_parity=True** | `raw/parity-v2b.json`、`raw/parity-run.log` |
| AC3 chiqui7 逐位复现 | 同上（chiqui7 sha d87389af 先验断言→进程内重指→finally 恢复） | 回滚权重 weights/yolo11s-seg.onnx | **PASS：ko-tile 56/56 + ko-npd 41/135，逐位** | `raw/parity-chiqui7.json` |
| AC3 BJ letterbox 零变化 | 同脚本 BJ 考卷段（pre-bj17/pre-bj18 chiqui7 letterbox 重跑 vs T3 raw） | 同上 | PASS：preds 与 T3 raw 逐位一致、sfx_route=letterbox | `raw/parity-summary.json` |
| AC2 性能双档 | `M2-SFX-T5-TILE-gpu/Scripts/python.exe experiments/M2-SFX-T5-TILE-KO/perf_tile_dual.py` | CPU=生产 EP v2b；GPU=onnxruntime-directml 1.24.4 DmlExecutionProvider（RTX 5070 Ti，独立 venv） | PASS：CPU 均值 10.46s/页（合计 41.82s）；GPU v2b 均值 1.08s/页；GPU chiqui7 均值 1.27s/页 | `raw/perf-summary.json`、`raw/perf-run.log`、`tile-deploy-report.md` §1 |
| AC4 全量回归 | `pytest tests -q`（产品 venv） | @ test `c9880955` | **PASS：1812 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=main 基线一致**（1812=基线 1780+32 新增） | `raw/regression-run.log` |
| contracts 零 diff | `git diff a3b0f537 -- contracts/ apps/` | @ branch tip | PASS（空 diff） | git |

未运行/限制（如实）：①GPU 档为呈报数据，生产引擎仍冻结 CPU EP（部署形态终选=用户
裁决）；②宽≠600/690 的 KO 形页按常量阈值参数化（KO-TILE §9 既有登记）；③测试
REAL-weights 面 3 例用 weights-v2b 真实权重跑（T4 先例），skip 计 1 与基线同款。

## 接收方式

- worktree：`G:/CODEX/New Manga.worktrees/M2-SFX-T5-TILE-KO-zcode`，branch
  `agent/zcode/M2-SFX-T5-TILE-KO`，base `a3b0f537`。
- 复现命令：见上表；数据路径（gitignored 外部树）与权重 sha 断言写死在
  `experiments/M2-SFX-T5-TILE-KO/verify_tile_parity.py` 头部。
- Reviewer（DSH 非作者）建议核查面：①`_tile_ys`/`_tile_page_nms` 与
  `experiments/M2-SFX-GATE-T3/eval_gate_t3.py`（只读蓝本）逐行等价性；②AC3 逐位
  断言的实际消费面（`production_preds` round 精度=T3 写盘精度 + match_gt 全精度
  复算 matched 数字）；③路由阈值登记依据与 fail-fast 覆盖格；④P3-2 断言面完整性。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-T5-TILE-KO r1 独立 Review（DSH 非作者，静态+证据复核）
- 推荐 Agent / Reviewer：DeepSeek Harness（Owner=ZCode 非作者隔离成立）
- 推荐原因与前置依赖：本 Task 已交付待审；依赖=本分支 delivery head；无新授权需求。
- Recovery point：`G:/CODEX/New Manga.worktrees/M2-SFX-T5-TILE-KO-zcode`，branch
  `agent/zcode/M2-SFX-T5-TILE-KO`，base `a3b0f537`，head=docs commit（见 Task
  frontmatter 回填）。
- 允许修改路径：`doc/reviews/M2-SFX-T5-TILE-KO-<head>-dsh-r1.md`（新建）。
- 禁止范围与新增授权条件：零 src/零 tests 修改；结论写 review 文件，status 变更与
  集成由 Codex 处置。
- 交付物：r1 review 报告（逐 AC 判定+证据抽查+P 级登记）。
- 验证命令、环境与完成 Gate：重跑 `raw` 证据命令任选（AC3 十分钟内）；Gate=逐 AC
  有判定、冲突点留证据。
- 可直接转发给 Agent 的指令：对 worktree
  `G:/CODEX/New Manga.worktrees/M2-SFX-T5-TILE-KO-zcode`（branch
  `agent/zcode/M2-SFX-T5-TILE-KO`，base `a3b0f537`）上 M2-SFX-T5-TILE-KO 交付做非作者
  r1 Review：逐 AC 核对 `verification/M2-SFX-T5-TILE-KO/tile-deploy-report.md` 证据表，
  抽查 `_tile_ys`/`_tile_page_nms`/路由 fail-fast 与 T3 蓝本
  `experiments/M2-SFX-GATE-T3/eval_gate_t3.py` 的等价性、AC3 逐位证据
  （`raw/parity-*.json`）与回归基线一致性（`raw/regression-run.log`，1812+1sk+1
  failed 既有登记），报告写 `doc/reviews/M2-SFX-T5-TILE-KO-<head>-dsh-r1.md`。

## 风险与遗留

- 部署形态终选（CPU 单档/GPU 加速档）为用户收口呈报项：CPU 形态均值 10.46s/页、
  GPU DML 1.08s/页（§1 表），数字如实不作判定；启用 GPU 需后续 Task（生产引擎冻结
  CPU EP=轻量栈裁决不动）。
- onnxruntime-directml DML 会话存在节点未分配 preferred EP 的 ORT warning（登记于
  deploy report §1）；若用户选 GPU 形态，建议届时评估 onnxruntime-gpu（CUDA EP）复测。
- 回退路径：`NEWMANGA_SFX_TILE=off`（行为回 pre-T5）与权重 pin 单值回滚（T4 AC4 语义）
  互相独立。
- 本 Task 全程未见 contracts/apps 需求，RegionCandidate 契约零变化成立；若未来 KO 域
  需要 mask/旋转框等新输出面，属新契约 Task。
