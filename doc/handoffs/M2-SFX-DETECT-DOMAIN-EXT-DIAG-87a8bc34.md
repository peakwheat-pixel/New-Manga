---
task_id: M2-SFX-DETECT-DOMAIN-EXT-DIAG
author: ZCode（owner subagent）
recipient: Codex（integrator）；Reviewer=DeepSeek Harness（非作者）
base_commit: 497621df
delivery_head: 87a8bc34
rework_head: d849c967
status: rework_delivered_pending_recheck
---

# Handoff：M2-SFX-DETECT-DOMAIN-EXT-DIAG（BJ 域 SFX 检测缺口诊断与扩展方案评估）

## 交付结果

四条 AC 全部交付，只评估不实施，零 src 改动。主报告：`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md`。

| AC | 交付 | 落点 |
|---|---|---|
| AC1 证据汇总与根因分层 | 三假设全部 **DETERMINED**：(a) 域外=成立（主根因）；(b) 类别映射歧义=分层（SFX 像素被其他类捡走成立 / argmax 竞争可阈值救=否定）；(c) 预处理=不成立。E2E r1 R2 遗留「panel/text 归属未定」收敛（DSH r1 P1-1 更正后口径）：**BJ13=text**（与 ko 域同型）；**BJ14=bubble 主导＋text 并存**（bubble IoU 0.122/0.399）；panel 大框全页平凡覆盖（IoU 0.013–0.126）非独立根因 | 报告 §3 |
| AC2 五方案评估 | ①后分类器（只救 BJ13/14，BJ15 结构性无载体）②类敏感阈值（实验否决）③fine-tune（对症但前置重，沿 C4 §7.1 条件式形态）④路由（不推荐独立立项）⑤维持现状+产品侧缓解（短期首选）；每方案列改动面/成本/收益/风险/SfxPolicy 交互 | 报告 §4 |
| AC3 裁决建议 | 排序 ⑤＞③（条件式）＞①（条件性次优）＞④＞②（否决）；含「不实施」合法选项；移交用户三个具体裁决问题 | 报告 §5 |
| AC4 零 src 佐证实验 | 三层探针实验跑成：L1 整页 conf 九档扫描（BJ06 对照+BJ13/14/15，全类+4 类分数向量 dump）、L2 60% tile（1.67×）、L3 参照框 crop（等效 3.5–5.4×，=page_h/crop_h——DSH r1 P2-1 更正）+ raw pre-NMS 参照框查询 | `experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py` + `raw/*.json` |

**结构性新发现（本 Task 新增，超出三假设框架）**：生产 region 创建无跨 provider 重叠仲裁（`src/bootstrap/core_assembly.py` `_create_detected_region` L1013-1049 按候选独立建 region）——chiqui7 召回修复（方案①②③任一）后 ogkalu speech region 仍并存走对话链，**误路由乱译损害不消失**。重叠仲裁属 region 语义/共享契约面，须 Codex 范围裁决（DETECT-EVAL §4.4 条件 5 的具体化）。

### 提交清单（base=497621df）

| commit | 内容 |
|---|---|
| `303d7e14` | claim（Task frontmatter status→in_progress + owner_claim） |
| `87a8bc34` | 交付主体：实验脚本 1 + raw JSON 4 + 主报告 1（6 文件，14796 行） |
| `cc2109ac` | 文档收尾：本 Handoff 初版 + Task 回填 |
| `d849c967` | **DSH r1 返修主体**（报告 r2 + Task：P1-1/P2-1/P2-2/P2-3/P2-4/P3-1/P3-2/P4-1/P4-2/P4-3，含报告 §8 闭合对照表） |
| （收尾 docs commit） | 本 Handoff 返修（P1-1/P2-1/P3-3 同步 + 本清单补 hash）与 Task frontmatter `rework_head=d849c967` 对齐——即本文件当前所在 commit（tip，hash 见 `git log --oneline -1` 与 Owner 回报；commit 无法在其自身内容中记录自身 hash——DSH r1 P3-3 口径注记） |

### r1 返修记录（2026-10-03）

DSH r1 verdict=`changes_requested`（0×P0，1×P1+4×P2+3×P3+3×P4）：主根因判语、五方案评估、AC3 排序、结构性发现均被确认成立且未越权，**不需重跑实验**。11 条纯文字/数字返修全部闭合，逐条处置与落点=报告 §8「DSH r1 闭合对照」；本文件同步修正的复制句：AC1 行收敛口径（P1-1 限定 BJ13=text、BJ14=bubble 主导＋text 并存）、AC4 行 L3 等效倍数（P2-1 改 3.5–5.4×）、本提交清单（P3-3）。返修 commit 只触碰报告/Task/Handoff 三个文件，`experiments/**` 与 `raw/**` 零触碰。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4 实验可复现 | `"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py` | onnxruntime 1.30.0 CPU；weights `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（sha256 `d87389af…` 由 `_build_engine` pin 校验）；@87a8bc34 | PASS：engine OK imgsz=1024 (metadata_parsed)；L1 四页各 ~0.2s；BJ06 @0.01 sfx=9；L1/L2/L3 参照框 sfx_box=False ×7/×7/×7 | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/{l1-fullpage-conf-scan,l2-tiles-resolution-probe,l3-reference-crops,scan-manifest}.json` |
| AC4 零 src 改动 | `git diff --stat 497621df..87a8bc34 -- src tests doc/contracts packaging apps doc/STATUS.md` | @87a8bc34 | PASS（空输出） | git |
| AC1 判语数字溯源 | 报告 §2.2/§2.4 每个数字对应 raw JSON 字段（`by_rung`/`reference_verdicts`/`raw_pre_nms_candidates_in_reference`/`best_sfx_class_score_any_box`） | @87a8bc34 | PASS | raw JSON ×3 |
| AC2/AC3 静态评估 | 报告 §4/§5（directional，静态分析+既有证据推导） | @87a8bc34 | N/A（评估性交付） | 报告 |
| 禁改面零触碰 | 逐文件 add（无 `git add -A`）；SFX-E2E/KO-RERUN/TILING 既有产物只读引用 | @87a8bc34 | PASS | git log |
| DSH r1 返修闭合（11 条） | 对照报告 §8 闭合表逐条核对报告/Task/Handoff 三处一致性（复制句同步）；`git diff --stat 87a8bc34..<tip> -- experiments verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw` 应为空 | 返修链 `d849c967`+收尾 docs commit | PASS（纯文字/数字返修，零实验重跑） | 报告 §8 |

未运行项：方案②③④的训练/集成实验（本 Task 合同「只评估不实施」）；imgsz 变档（ONNX 输入形状固定 1024，物理不可变，已由 L3 覆盖判定需求）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-DETECT-DOMAIN-EXT-DIAG-zcode`，base=`497621df`，delivery_head=`87a8bc34`。
- 复现命令见报告 §7（单命令，输出全落本 Task 目录）；页面图像为 gitignored 跨 worktree 只读引用（路径记录在 raw JSON `page` 字段：BJ13-15 在 `M2-SFX-E2E-MATERIAL-zcode`、BJ06 在 `M2-TA2B-OPEN-ASSETS-zcode`）。
- Reviewer 检查建议：①抽查 raw JSON 与报告 §2 数字的一致性（尤其 `reference_verdicts[*].best_sfx_class_score_among_intersecting` 与 `raw_pre_nms_candidates_in_reference[*][0].scores.sfx`）；②核对 §3 三假设判语与数字的对应；③§4/§5 评估的 directional 口径是否越界（不得被读成实施 Gate）；④r1 返修改为 r2 后：复核报告 §8 闭合表 11 条的落点与报告/Task/Handoff 三处复制句一致性（P1-1 收敛口径、P2-1 倍数、P3-2 基线口径）。

## 下一任务建议（必填）

- Task ID / 标题：暂无既有 Task——裁决材料已齐，下一步是**用户/编排裁决**（报告 §5 三个具体问题），裁决前无实施 Task 可释放。
- 推荐 Agent / Reviewer：裁决=用户（许可/范围类）+ Codex（重叠仲裁契约面）；若裁决选择⑤，UI 切片 Task 由 Qoder 主责（React/Tauri）。
- 推荐原因与前置依赖：本 Task 为诊断+评估，合同明确「只评估不实施、实施另行释放」；三假设已 DETERMINED，方案排序已给出，继续实施的授权条件在用户裁决。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG`，base=`497621df`，head=`87a8bc34`（或含本 Handoff 的收尾 commit）。
- 允许修改路径：裁决后按选项分别立 Task（⑤=React/Tauri UI 面；③=训练资产+许可链；仲裁切片=契约面由 Codex 冻结范围）。
- 禁止范围与新增授权条件：实施 Task 释放前维持零 src 改动；AGPL 衍生权重问题（若走③）必须用户裁决在前。
- 交付物：裁决清单（报告 §5）；裁决后各 Task 按模板另立。
- 验证命令、环境与完成 Gate：Review 通过（DSH 非作者）+ Codex 集成验证后本 Task 流转 done；实施 Task 的 Gate 在其自身 Task 文件定义。
- 可直接转发给 Agent 的指令：**Reviewer（DeepSeek Harness）**：在 worktree `G:/CODEX/New Manga.worktrees/M2-SFX-DETECT-DOMAIN-EXT-DIAG-zcode` 分支 `agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG` head `87a8bc34`（或收尾 commit）上 review `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md`：对照 `raw/l1-fullpage-conf-scan.json` 等四份 raw 抽查 §2 数字、复核 §3 判语是否被证据支撑、§4/§5 是否保持 directional 与「只评估不实施」边界；产出 `doc/reviews/M2-SFX-DETECT-DOMAIN-EXT-DIAG-<head>-dsh-r1.md`。

## 风险与遗留

1. **误路由损害仍在生产语义下存在**（BJ 域形态）：诊断未改变任何生产行为；BJ13-15 素材页重现该损害的条件是再次跑 e2e（policy 无关）。
2. **重叠仲裁缺口**登记为结构发现：修复召回≠闭合损害，契约裁决不可跳过。
3. ③的 AGPL 衍生权重许可争议比原权重分发争议更尖锐（Ultralytics 对训练产物的主张），用户裁决前置；替代路线（非 Ultralytics 基座自训）会引入新模型选型 Task。
4. BJ06 域内正例身份为 chiqui7 自证（无独立 GT），域内/域外对比分母有残余不确定性（报告 limitation 6）。
5. 关联 Task：M2-SFX-E2E-MATERIAL（损害形态来源，r1 R1/R2 遗留由本 Task 收敛）、M2-SFX-DETECT-EVAL（§4.4 清单=本评估框架）、M2-DOCTR-QUAL-C4（fine-tune 条件式先例）、M2-TA3-B3-KO-FULLRUN（并行无文件交集）。

## 实验附录（实验任务）

- **数据来源与许可**：BJ13/14/15（densho810 官方免费，`cases.json` attribution 字段，M2-SFX-E2E-MATERIAL 已核定）；BJ06 同源；页面图像 gitignored，只读跨 worktree 引用，零复制零修改。
- **数据 Hash**：页面 sha256 见 `test_assets/comic_golden_suite/manifests/cases.json`（BJ13 `86eeb6c2…`、BJ14 `61dfeb2f…`、BJ15 `3af00541…`、BJ06 `b06c9d7d…`）。
- **模型/权重版本**：chiqui7/yolo11-manga-seg @ `7f5f5c0464f2eeb57282f16da760eb8828a8716a`，`yolo11s-seg.onnx` sha256 `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646`（运行时 pin 校验通过）。
- **Provider/Runtime**：onnxruntime 1.30.0 CPUExecutionProvider；numpy/PIL（M2-TA3-B-ocr venv）；生产同源推理序列复放（`_build_engine/_letterbox/_map_back/_nms` import 只读）。
- **硬件**：CPU（本机）；网络策略：零网络访问（权重本地 pin，HF 不触网）。
- **参数**：imgsz=1024（metadata_parsed）；NMS IoU 0.7 class-agnostic（eval 口径）；conf 档 0.01–0.50 九档；L2 tile 60% 四锚点；L3 crop 外扩 20%。
- **运行次数**：每配置单次（前向确定性）；L1 4 次推理 + raw 查询复用、L2 12 次、L3 7 次。
- **原始结果**：`raw/l1-fullpage-conf-scan.json`（含每框 4 类分数向量与 raw pre-NMS 参照框查询）、`raw/l2-tiles-resolution-probe.json`、`raw/l3-reference-crops.json`、`raw/scan-manifest.json`（参数与环境登记）。
- **质量判断办法**：通道响应量级对比（盲区 sfx 分数 0.0000–0.0855 vs 域内 0.72–0.9355，跨 2–3 个数量级）+ 分辨率恢复实验（L2/L3 均不恢复）+ raw pre-NMS 干净探针（NMS 丢弃不可归因）。
- **失败样例**：无运行失败；BJ14 ref1/ref2、BJ15 ref1 的 raw 查询为 0 候选是**结果**（连 conf≥0.01 候选都没有），非脚本故障。
- **限制**：见报告 §6（directional 口径、参照框近似性、单形态探针、CPU 单环境、BJ06 自证对照）。
- **建议**：若未来走③，L3 crop 裁片可直接转为训练/增强素材形态；重叠仲裁设计应以 BJ13 双框并存（sfx+speech 同位）为验收场景。
