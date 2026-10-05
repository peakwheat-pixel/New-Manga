# M2-SFX-T4-SWITCH · SFX 生产切换 V2B — Switch Report（部署记录）

- **Task**：[M2-SFX-T4-SWITCH](../../doc/tasks/M2-SFX-T4-SWITCH.md)（owner=ZCode；reviewer=DeepSeek Harness 非作者；integrator=编排会话代行 Codex）
- **授权**：用户 2026-10-05 裁决「三件都同意」（①切换 v2b ②KO tile 化立项 M2-SFX-T5-TILE-KO ③G7 补证=切换硬前置）
- **分支/base**：`agent/zcode/M2-SFX-T4-SWITCH`，base=5166ba7f，release=3d4f20f1，claim=d7e11e5d
- **执行顺序纪律**：AC1（G7 补证）先行且 PASS 后方动 src/权重通道——全程遵守，AC1 证据 commit（5d5ab592）先于 src 变更 commit（5d835e44）

## 0. 切换结果一览

| 项 | 切换前（现役） | 切换后（终态） |
|---|---|---|
| `SFX_WEIGHTS_SHA256` | `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646` | `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` |
| 权重身份 | chiqui7/yolo11-manga-seg @ 7f5f5c04（HF ONNX） | 本地发布通道 `local-release:sfx-train-v2/v2b`（M2-SFX-TRAIN-V2 训练产物，非 HF 发布物） |
| `SFX_HF_REPO` / `SFX_HF_REVISION` | `chiqui7/yolo11-manga-seg` / `7f5f5c04…71a`（HF 语义） | `local-release:sfx-train-v2/v2b` / `c22f0175…1c08`（best.pt 上游锚，登记性语义） |
| 部署文件 | `<task-envs>/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（**未动，保留为回退权重**） | `<task-envs>/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`（40,824,255 B） |
| 通道资源名 | `yolo11s-seg.onnx`（`SFX_WEIGHTS_FILENAME` 不变——装配解析链/bundle 布局零变化，身份由 pin+来源登记承载） | 同左（不变） |
| wire 契约 | — | **零变化**（`contracts/**` 零 diff；names `{0:bubble,1:panel,2:sfx,3:text}` 装载期断言在位） |

## 1. AC1 · G7 翻译链深层补证（硬前置）——PASS

T3 部署前补证项①（gate-t3-report §7）：以新权重补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用）。**未补证前不得把 G7 记为部署就绪**——本节即该补证，**G7 自此可记为部署就绪**。

执行方式：v2b 权重**进程内重指**（零 src，T3 `eval_gate_t3.py:505-520` / V2 `eval_v2.py:179` 先例），harness=E2E-MATERIAL 同款 `run_qualification.py`（M2-TA3-B2 phase2 交付，零改动 in-process 复用），先例=M2-SFX-E2E-MATERIAL BJ06 8/8。

- **SHA 门先证**：默认 pin（d87389af）下 v2b onnx 被 `_build_engine` 拒跑 `PROVIDER_FAILED`（console log 首行 `sha_gate_probe: FIRED error_code=PROVIDER_FAILED`）→ 重指窗口开启（944e8114）→ 跑完 finally 恢复（`pin_restored=True`）。
- **v2b 臂**（`--case BJ06 --sfx-policy translate --determinism-track remote --meter-translation`）：**EXIT=0**；run1 437s（对照臂）/356s（v2b 臂）；detect **14 region（5 sfx + 9 speech）**→ crops 14 → run2 COMPLETED（330.5s，无截断）→ OCR/translate **14/14 非空落库**（sfx 5/5）→ export OK（`d270ac3fc9211c8a…`）。检测→翻译链契约合法 fail-closed（0 候选=合法空输入语义未触发，链无 crash/无 defect attribution）。
- **chiqui7 对照臂**（同页同参同 harness，pin 原样）：**EXIT=0**；17 region（8 sfx + 9 speech，与 E2E-MATERIAL 先例 8/8+9/9 构成逐项一致）→ 17/17 落库 → export OK（`3090cb34e37083ad…`）。
- **新增故障=0**（硬断言）：`g7-compare.json` verdict `new_failure_count=0`、`both_pipeline_completed=true`、`fail_closed_chain_legal=true`；v2b 臂 attribution 空集。
- **框集差异=directional**：sfx 5（v2b）vs 8（chiqui7），speech 9/9 两臂逐项一致（主检测器 ogkalu 不受 SFX 权重切换影响，佐证链隔离正确）。差异方向与 T3 G1 判定一致（v2b 考卷 P1.0 零误检 vs chiqui7 P0.8333——更保守的检出）。单一页、无 SFX GT，E2E-MATERIAL directional 口径适用，本差异不作质量判定。
- 证据：`raw/g7-smoke-{v2b,chiqui7}-console.log`（V1 教训：全程 console 日志落盘，非脚本自产 JSON 单一来源）、`raw/g7-smoke-*/harness-meta.json`、`raw/g7-smoke-*/summaries/qual-{BJ06,report}.json`、`raw/g7-compare.json`。
- 偏差登记：冒烟 venv=`M2-TA3-B-ocr`（E2E-MATERIAL 先例同款，run_qualification 需 PySide6+manga_ocr+onnxruntime 全备）；任务指令所述 `M2-SFX-FINETUNE-gpu-py312` 缺 PySide6/manga_ocr 无法承载 run_qualification（该 venv 用于 AC3/AC4）。

## 2. AC2 · 权重通道与 pin 替换——PASS

- **pin 单值替换**：`SFX_WEIGHTS_SHA256` → `944e8114…`（detection_sfx.py pin 段，授权面内）。SHA 门语义零变化（`_build_engine` 校验链原样）。
- **来源字段处置=本地发布通道登记**（V2 §7.2.3 方案）：
  - `SFX_HF_REPO = "local-release:sfx-train-v2/v2b"`——登记性指向本地训练通道（M2-SFX-TRAIN-V2 B 版）；
  - `SFX_HF_REVISION = "c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08"`——直接上游 checkpoint（best.pt）锚；
  - 字段名保留（唯一消费点 `_build_engine` guidance 消息自动跟随，兼容面零破坏）；语义变更已在常量注释中声明。
- **部署记录 · 源链全链 sha256**（T3 §4.8-2 已验链，本轮 deployment 侧再录）：

  | 链段 | sha256 | 出处 |
  |---|---|---|
  | 基座 .pt（HF `anonimkaq4/manga-page-element-segmentation` snapshots/yolo11s_1024_b8，81,340,348 B，`license: other`） | `1f0fd609e7dc29c831255db67586ed5623f9bebae6a1e29fae197c1c6d7b77e0` | V2 报告 §2.2 盘上重算一致 |
  | 训练产物 best.pt（20,578,084 B） | `c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08` | train-v2b log TRAIN_RESULT_JSON + export-smoke-v2.json:104 |
  | 导出 best.onnx（40,824,255 B）= **现役 pin** | `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` | export-smoke-v2.json:119 + 本 Task 盘上两次独立复算（V2 权重树原件、部署副本）逐字一致 |
- **权重通道**（M2-SFX-PROD-1 随包机制，`core_assembly._resolve_detector_weights_path` 解析链：env override > data root > frozen in-bundle > default）：部署副本落 `<task-envs>/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`（**只读复制**，chiqui7 原文件 `weights/yolo11s-seg.onnx` 未动未覆盖=AC4 回退在位性）；权重本体 gitignored 不入库。
- **随包面实测（PROD-1 先例）**：`packaging/m2ac5/build_sidecar.ps1` lockstep（sha literal→944e8114；`-SfxWeightsSource` 默认→weights-v2b 目录；fail-closed 语义不变——stale literal 无法静默发布）。完整 PyInstaller 构建 **EXIT=0**（`raw/build-sidecar-v2b-console.log`）：manga 3 文件+sfx 权重 sha 校验随包；bundle 内 `models/detector/yolo11s-seg.onnx` 独立复算=944e8114 逐字。
- **冻结探针 3/3 PASS**（沿 PROD-1 `frozen-sfx-probe.py` 协议 1.1 形态，`experiments/M2-SFX-T4-SWITCH/frozen_v2b_probe.py` → `raw/frozen-v2b-probe-results.json`）：FV-1 v2b 冻结装载零 sha/PROVIDER_FAILED 线，K07_R123 锚帧 sfx-1 候选（conf 0.9047，**directional**——PROD-1 期望值 0.9313 为 chiqui7 时代数字，不跨权重携带）+ manga 候选并存；FV-2 SFX off=manga-only 面；FV-3 断权重=typed 降级 manga 存活。
- **tests 零改动**：`tests/providers/test_detection_sfx.py` pin 断言全用符号 import（`SFX_WEIGHTS_SHA256`），无 sha 字面量；grep 实证 src/packaging/tests 无 d87389af 活引用（残留 2 处=回退登记性注释，有意保留）。
- **NSIS 安装器层 NOT_RUN（如实登记）**：tauri/NSIS 安装包构建未执行——本 Task 授权面=随包机制（build_sidecar + tauri resource 声明零变化），安装器构建与 cleanstart 验证属 M2-AC5/M2-SFX-PROD-1 交付链；bundle onedir 形态+resource 随包链已实测（上述）。下一发布轮沿 PROD-1 cleanstart 先例对安装包复验即可。

## 3. AC3 · 新 pin SHA 门反向验证——PASS

（DSH r2 转承接项；T0/V2 `export_smoke_v2.py` 同款断言形态，独立进程 import 实测 = 生产 pin 本体）

- 外来权重（前现役 chiqui7 onnx，d87389af 文件）按生产 pin 944e8114 加载 → `_build_engine` **拒跑 `PROVIDER_FAILED`**（gate fired，先于任何 runtime import）。
- 新生产权重（weights-v2b 部署文件）全装载链 OK：sha 门 → onnxruntime session → names/imgsz metadata 断言（imgsz=1024，`metadata_parsed`）。
- 终态复核：AC4 drill 后 `git checkout` 恢复终态，AC3 复跑 PASS。
- 证据：`raw/ac3-pin-switch-verify-console.log`、`raw/pin-switch-verify.json`。venv=`M2-SFX-FINETUNE-gpu-py312`。

## 4. AC4 · 回退语义实测——PASS（非纸面）

回退方案（T3 §7.4 / V2 §7.2.6）：**pin 恢复 `d87389af…` + chiqui7 权重文件在位**。实测：

1. 工作区临时恢复 pin 单值 d87389af（git 未提交修改，不触碰提交历史）；
2. 独立进程 `_build_engine(chiqui7 weights/yolo11s-seg.onnx)` **EXIT=0**（imgsz=1024 `metadata_parsed`，names 断言过）——回退 pin 与在位 chiqui7 权重组合真实可用；
3. **chiqui7 权重文件全程只读**（未删除/未覆盖——切换部署采用独立 weights-v2b 目录，回退在位性由构造保证，非仅口头承诺）；
4. 出证后 `git checkout` 恢复新 pin 终态（AC3 复跑确认）。

证据：`raw/ac4-rollback-drill-console.log`、`raw/rollback-drill.json`。

## 5. G8 checklist 刷新（T3 §4.8 v2b 7/7 的部署时点核查）

- **densho810 报告义务窗口 2026-11-02 时点核查**：本 Task 执行时点 2026-10-05，**窗口未到**；履行登记=`74fa71e9`（T3 §4.8-7 引用）。**部署时点（即本切换）核查=义务在册、未逾期、履行路径不变**——2026-11-02 前达标义务沿既有登记继续有效，T5/后续发布 Task 不得遗忘该窗口。
- **许可登记义务三项**（T3 §4.8-4 v2b 审计结论「PASS 附登记义务」沿引，本切换不改变其触发状态——本地部署使用、未分发）：
  1. 若未来**分发/发布** v2b 衍生权重或公布数据集衍生图像 → 须先复核 Manga109-s/MangaSeg 授权边界（本结论不外推到分发场景）；
  2. MangaSeg 论文引用（b-base README :94-100）→ 备案项在册；
  3. credit 义务（b-base README :91「cite the MangaSeg paper」）→ 保守登记；当前本地未分发场景不触发，分发场景复核。
- 训练数据许可备案引用：own-manga=用户自有（2026-10-04 备案）、densho810（上述）、HF webtoon/P&C 沿 T0 §6 表。

## 6. 产品回归（src 变更后）

- **首跑（pin 替换后、tests 锚迁移前）**：4 failed / 1777 passed / 1 skipped——①`test_catalog`=既有 BASELINE_FAILURE 登记（与本 Task 无关）；②③`test_real_weights_reproduce_eval_payload[rgb24/rgb32]`+④`test_real_weights_blank_page_structurally_valid`=**pin 切换的预期连带**：三测试的 `REAL_WEIGHTS` 指向旧 chiqui7 权重文件（weights/yolo11s-seg.onnx，d87389af），新 pin 944e8114 下 SHA 门按设计拒跑（AC3 同型 PROVIDER_FAILED）——fail-closed 行为正确，锚定数据过时。
- **处置（tests 逐条声明，授权面内）**：`REAL_WEIGHTS` 改指 v2b 部署副本（weights-v2b，sha=pin 逐字）；真实权重复现锚从 chiqui7 eval payload（conf 0.9313，`onnx-sfx-frames.json`）迁移到 **v2b 锚 JSON**（conf 0.9047，`extract_v2b_anchor.py` 以与测试完全相同的 `SfxDetectionProvider.detect` 调用路径提取；与冻结探针 FV-1 conf 0.9047 跨环境一致）；锚 JSON 内含 `weights_sha256`==生产 pin 的**运行期断言**（pin 再动时锚自动失配报错，强制同步重提取）。
- **终跑（锚迁移后）**：`tests/providers/test_detection_sfx.py` 38/38 PASS；全量 **1780 passed + 1 skipped + 1 failed（仅 test_catalog 既有登记）**=与 main 基线完全一致（§8）。

## 7. 部署指引（已部署机器升级语义）

- **随包形态**（推荐，PROD-1 默认）：新包 build_sidecar 随包 v2b 权重自动就位（bundle 内 `models/detector/yolo11s-seg.onnx` 内容替换为 v2b，文件名不变）；零手工步骤。
- **data-root 手工部署形态**：`<data root>/models/detector/yolo11s-seg.onnx` 若仍为 chiqui7 旧文件，新 pin 下为 **typed `PROVIDER_FAILED`**（sha 门 fail-closed，AC3 实证）——**这是有意的供应链保护，不是回归**；处置=替换该文件为 v2b onnx（sha 944e8114）或删除让装配落到随包副本。
- **回退**：pin 单值恢复 d87389af + `weights/yolo11s-seg.onnx` 在位（AC4 实证 EXIT=0）。

## 8. 回归结果与基线对比

| 轮 | 结果 | venv | log |
|---|---|---|---|
| pin 替换后首跑 | 4 failed / 1777 passed / 1 skipped（3 新失败=锚过时，§6） | T1.1.1-impl-py312 | raw/pytest-regression-console.log（已被终跑覆盖，首跑数字见本轮 Task 交付记录） |
| 锚迁移后终跑 | **1780 passed + 1 skipped + 1 failed（test_catalog 既有 BASELINE_FAILURE）**=main 基线一致 | T1.1.1-impl-py312 | `raw/pytest-regression-console.log`（EXIT=1 仅因既有登记项） |

- tests 修改清单（Task 允许路径 `tests/**` 逐条声明，唯一修改文件=`tests/providers/test_detection_sfx.py`）：
  1. `REAL_WEIGHTS`：weights/ → **weights-v2b/**（v2b 部署副本，sha 944e8114=pin）；
  2. 真实权重复现锚：chiqui7 eval payload → **v2b 锚 JSON**（`experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json`，conf 0.9047 / box [200.5, 1131.4, 380.5, 1342.7]；`EVAL_PAYLOAD` 常量更名 `V2B_ANCHOR`）；
  3. 新增锚-pin 一致性运行期断言（`payload["weights_sha256"] == SFX_WEIGHTS_SHA256`，失配即指引重提取）；
  4. `REAL_SKIP` reason 与注释文本 chiqui7 → v2b 时代表述。
- pin 断言本体零改动（符号 import `SFX_WEIGHTS_SHA256` 原样，切 pin 自动跟随——首跑 36 passed 中已含）。

## 9. 风险与 NOT_RUN 清单

| # | 项 | 等级 | 说明 |
|---|---|---|---|
| 1 | NSIS 安装器层未构建 | NOT_RUN（授权面边界） | tauri/NSIS 打包属 M2-AC5/PROD-1 交付链；随包机制（build_sidecar+resource 声明）已实测。下一发布轮沿 PROD-1 cleanstart 复验 |
| 2 | 冻结探针 FV-1 sfx conf 0.9047 vs PROD-1 期望 0.9313 | directional | 期望值为 chiqui7 时代锚值，不跨权重携带；v2b 数字如实登记，不作质量判定（质量判定=T3 Gate 已冻结） |
| 3 | BJ06 sfx 检出 5（v2b）vs 8（chiqui7） | directional | 同 §AC1；speech 9/9 两臂一致；T3 G1 判定方向一致 |
| 4 | AC1 venv 偏差 | 登记 | 冒烟 venv=M2-TA3-B-ocr（先例同款全备）；指令所述 FINETUNE venv 缺 PySide6/manga_ocr，用于 AC3/AC4 |
| 5 | data-root 旧文件升级语义 | 部署指引 | 见 §7——sha 门 fail-closed 为有意保护 |
| 6 | densho810 义务窗口 | 在册 | 2026-11-02，未逾期，后续 Task 沿 §5 |

## 10. 证据索引

| 产物 | 路径 | commit |
|---|---|---|
| AC1 脚本 | `experiments/M2-SFX-T4-SWITCH/{run_g7_smoke,compare_g7_arms,verify_pin_switch}.py` | 5d5ab592 |
| AC1 冒烟产物 | `verification/M2-SFX-T4-SWITCH/raw/g7-smoke-*` + `g7-compare.json` | 5d5ab592 |
| AC2 src+packaging | `src/infrastructure/providers/detection_sfx.py`、`packaging/m2ac5/build_sidecar.ps1` | 5d835e44 |
| AC2 随包/冻结证据 | `raw/build-sidecar-v2b-console.log`、`raw/frozen-v2b-probe-{console.log,results.json}` | 5d835e44 |
| AC3/AC4 证据 | `raw/{ac3-pin-switch-verify-console.log,ac4-rollback-drill-console.log,pin-switch-verify.json,rollback-drill.json}` | d631f7ec |
| 回归锚迁移 | `experiments/M2-SFX-T4-SWITCH/{extract_v2b_anchor.py,v2b-k07-r123-anchor.json}` + `tests/providers/test_detection_sfx.py` | AC5 commit |
| 回归终跑 | `raw/pytest-regression-console.log`（1780+1sk+1 failed 既有登记） | AC5 commit |
| 部署权重副本 | `<task-envs>/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`（gitignored，sha=944e8114） | —（Git 外） |
| 回退权重（未动） | `<task-envs>/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（sha=d87389af） | —（Git 外） |
