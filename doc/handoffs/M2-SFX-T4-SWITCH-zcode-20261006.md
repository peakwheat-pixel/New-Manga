# Handoff: M2-SFX-T4-SWITCH — Owner 交付（ZCode → DSH Review → 编排集成）

- **Task**: [M2-SFX-T4-SWITCH](../tasks/M2-SFX-T4-SWITCH.md)（status=in_review，停写）
- **Owner**: ZCode（用户 2026-10-05 裁决「三件都同意」授权面）
- **Reviewer**: DeepSeek Harness（非作者；headless 静态可核部分为主，运行级由集成方补跑）
- **Integrator**: 编排会话代行 Codex
- **base**: `5166ba7f`（T3 收口）；**release**: `3d4f20f1`；**claim**: `d7e11e5d`
- **交付 commit 链**（claim 之后，逻辑分 commit）：
  - `5d5ab592` AC1 G7 翻译链深层补证 PASS（硬前置先行，先于任何 src 变更）
  - `5d835e44` AC2 pin 替换 944e8114+本地发布通道登记+随包构建+冻结探针 3/3
  - `d631f7ec` AC3 SHA 门反向验证 PASS+AC4 回退语义实测 PASS
  - AC5 commit（本 handoff 所在提交）：switch-report 回填+回归锚迁移+Task/Handoff

## 一句话结论

**生产 SFX 权重已从 chiqui7（d87389af）切换为自训 v2b（944e8114）**：G7 翻译链深层补证 PASS（切换硬前置闭合）、SHA 门反向验证与回退路径均实测通过、产品回归与 main 基线一致（1780+1sk+1 failed 既有登记）。

## 逐 AC 交付摘要

| AC | 判定 | 要点 |
|---|---|---|
| AC1 | PASS | BJ06 policy=translate 端到端双臂冒烟：v2b EXIT=0（14 region=5 sfx+9 speech，OCR/translate 14/14 落库，export OK）；chiqui7 对照 EXIT=0（17 region，speech 9/9 两臂一致）；**new_failure_count=0**；SHA 门先证 FIRED→重指→finally 恢复 |
| AC2 | PASS | pin 单值 944e8114；`SFX_HF_REPO="local-release:sfx-train-v2/v2b"`+`SFX_HF_REVISION`=best.pt 锚（登记性语义，注释含全链 sha）；build_sidecar EXIT=0+bundle 权重复算逐字；冻结探针 3/3（FV-1 conf 0.9047 directional）；contracts 零 diff；**NSIS 安装器层 NOT_RUN 如实登记**（授权面=随包机制） |
| AC3 | PASS | 外来 chiqui7 onnx 按新 pin→PROVIDER_FAILED 拒跑（先于 runtime import）；v2b 装载链 OK（imgsz=1024 metadata_parsed） |
| AC4 | PASS | pin 临时恢复 d87389af+chiqui7 权重在位→EXIT=0；chiqui7 文件全程只读；出证后恢复新 pin 终态 |
| AC5 | PASS | switch-report（含 G8 checklist 刷新：densho810 窗口 2026-11-02 在册未逾期+许可登记义务三项）+回归锚迁移+Task/Handoff 回填 |

## tests 修改声明（允许路径逐条声明，唯一文件）

`tests/providers/test_detection_sfx.py`：REAL_WEIGHTS → weights-v2b 副本；真实权重复现锚 chiqui7（conf 0.9313）→ v2b 锚 JSON（conf 0.9047，`extract_v2b_anchor.py` 同调用路径提取，与冻结探针跨环境一致）；新增锚-pin 一致性运行期断言；REAL_SKIP 文本更新。pin 断言本体（符号 import）零改动。

**回归**：pin 切换后首跑 3 个真实权重测试被 SHA 门 fail-closed 拒跑（预期连带，锚过时）→ 锚迁移后 `test_detection_sfx.py` 38/38，全量 **1780 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=main 基线一致**。

## 交付物索引

| 产物 | 路径 |
|---|---|
| 部署记录（主文档） | verification/M2-SFX-T4-SWITCH/switch-report.md |
| AC1 双臂冒烟 | verification/M2-SFX-T4-SWITCH/raw/g7-smoke-{v2b,chiqui7}*/ + g7-compare.json |
| AC2 随包/冻结 | raw/build-sidecar-v2b-console.log、raw/frozen-v2b-probe-{console.log,results.json}、experiments/M2-SFX-T4-SWITCH/frozen_v2b_probe.py |
| AC3/AC4 | raw/{ac3-pin-switch-verify-console.log,ac4-rollback-drill-console.log,pin-switch-verify.json,rollback-drill.json}、experiments/M2-SFX-T4-SWITCH/verify_pin_switch.py |
| 回归锚迁移 | experiments/M2-SFX-T4-SWITCH/{extract_v2b_anchor.py,v2b-k07-r123-anchor.json} |
| 部署权重 | `<task-envs>/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`（sha=944e8114；chiqui7 原件 weights/ 未动=回退在位） |

## Reviewer 建议核对点

1. **AC1 先行纪律**：`git log --author-date` 或提交顺序——5d5ab592（零 src）先于 5d835e44（src 变更）；`g7-compare.json` verdict 字段 new_failure_count=0。
2. **pin 段 diff 面**：`git diff 5166ba7f..HEAD -- src/` 应仅 `detection_sfx.py`；pin 常量+注释+来源字段段以外零改动；`contracts/**`、`apps/**` 零 diff。
3. **tests 声明面**：`git diff 5166ba7f..HEAD -- tests/` 应仅 `test_detection_sfx.py`（§tests 修改声明 4 项）。
4. **锚提取可信度**：`v2b-k07-r123-anchor.json` 的 weights_sha256=944e8114 与 pin 逐字；conf 0.9047 与冻结探针 FV-1 一致（两独立环境）。
5. **运行级补跑**（DSH 无 shell 时转集成方）：全量 pytest（T1.1.1-impl-py312 venv）；`extract_v2b_anchor.py` 重跑锚稳定（同帧同权重确定性）。

## 已知限制与 NOT_RUN（如实）

- NSIS 安装器构建未执行——理由按 AC2 允许口径对齐（DSH r1 P3-4）：授权面外的交付链环节（tauri/NSIS 打包属 M2-AC5/PROD-1 交付链），非技术不可行；bundle onedir+resource 随包链已实测——下一发布轮沿 PROD-1 cleanstart 复验。
- BJ06 sfx 检出 5（v2b）vs 8（chiqui7）=directional（单页无 GT，T3 G1 判定方向一致：v2b 更保守）。
- 冻结探针 FV-1 conf 0.9047 vs PROD-1 期望 0.9313=directional（期望值为 chiqui7 时代锚，不跨权重携带）。
- AC1 冒烟 venv=M2-TA3-B-ocr（先例同款；任务书 FINETUNE venv 用于 AC3/AC4）——偏差已登记 switch-report §1。
- **残留身份文本清单（DSH r1 P3-1/P3-2，越域登记交后续清理）**：requirements.txt:30-36、detection_sfx.py:24/:139-140/:286/:498、core_assembly.py:958、build_sidecar.ps1:115、run_qualification.py:481（detector 标签）——行为无影响，见 Task 偏差登记段。
- **AC1 断言面（DSH r1 P3-3）**：「新增故障=0」硬断言消费 attribution 集合差；failures=0+全 stage OK 为佐证未被脚本消费——DSH 独立逐字段复核结论方向正确；脚本强化留待下次重跑。
- 锚 JSON 仅 rgb24 面（DSH r1 P4-4）；FV-1 判据面窄于记录面（P4-6）；AC3/AC4 console 缺 shell 级退出码（P4-2）。

## 集成方后续（Task 合同外提示）

- 集成 merge 后：STATUS/PLAN 收口（T4 done、**T5-TILE-KO 解锁**）；G8 checklist 的 densho810 窗口（2026-11-02）沿登记。
- data-root 手工部署形态升级语义见 switch-report §7（旧 chiqui7 文件在新 pin 下 typed PROVIDER_FAILED=有意保护）。
