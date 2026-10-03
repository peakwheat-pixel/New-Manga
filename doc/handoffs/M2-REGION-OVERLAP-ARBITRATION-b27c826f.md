---
task_id: M2-REGION-OVERLAP-ARBITRATION
author: ZCode（Owner 实现 subagent）
recipient: Codex（Integrator，编排会话代行）；Reviewer=DeepSeek Harness（非作者）
base_commit: eb7cd15e
delivery_head: b27c826f
status: ready_for_review
---

# Handoff：M2-REGION-OVERLAP-ARBITRATION（region 创建跨 provider 重叠仲裁）

## 交付结果

- **分支/worktree**：`agent/zcode/M2-REGION-OVERLAP-ARBITRATION` @ `G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode`；base=`eb7cd15e`（release 2026-10-04，用户裁决③授权）、claim=`8c74d170`、实现主体（delivery_head）=`b27c826f`、文档/证据收尾=本 Handoff 所在 commit（终 tip 见 Task frontmatter 下方提交链）。
- **提交清单**：
  - `8c74d170` claim：Task frontmatter `status: ready→in_progress`、`base_commit` 回填、`owner_claim` 时间戳；
  - `b27c826f` 实现主体：`src/infrastructure/providers/detection_sfx.py`（仲裁）、`tests/providers/test_detection_sfx.py`（14 仲裁用例，先红后绿）、`tests/core/test_sfx_assembly.py`（分发矩阵 `sfx-arb-` 锚定行）；
  - 收尾 commit：experiments 脚本 + verification 证据 + 本 Handoff + Task 回填（逐文件 add，`git diff --check` EXIT=0）。
- **AC 对照**：
  - **AC1（DELIVERED，证据定案）**：层位=provider 拼接层（composite 拼接前）；度量=bbox IoU；规则=sfx 候选驱动的 directional 改标（`sfx-arb-<原label>`，复用 `startswith("sfx-")` 分发契约，core_assembly 零改动）；冻结阈值 0.90；依据=BJ06 域内最高 0.8862/0.8865 之上的保守域（详 [arbitration-report.md §1](../../verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md)）。
  - **AC2（DELIVERED）**：BJ13 真实 rerun 红态对位（manga-1/manga-3 = qual region#1/#3 乱译路径；现状 sfx 通道仅 T 恤印花且与全部 manga 候选零相交）；绿态=合成召回恢复口径 B（近重复双检出）relabels=3 全落 `RegionType.SFX`（生产分发函数逐候选判定）；口径 A（参照框）partial 0.5501 诊断不迁移；BJ14（sfx=0 + 重叠 0.123/0.4287 双层不可达）、BJ15（与全部 ogkalu 候选零相交，结构性无载体）如实登记，不伪造覆盖。
  - **AC3（DELIVERED）**：BJ06 仲裁 off/on 候选逐位一致（17=17，bit-identical=True）；rerun 与 qual-BJ06 基线 17 region（9 speech+8 sfx）对位、BJ13/14/15 计数 4/6/7 对位；三套件 627 passed + 1 skipped，0 failed，EXIT=0（基线 611+1sk + 16 新用例精确吻合）；cargo/vitest 零改动面。
  - **AC4（DELIVERED）**：`NEWMANGA_SFX_ARBITRATION`（on|off，默认 on）/ `NEWMANGA_SFX_ARBITRATION_IOU`（(0,1]，默认 0.90）空/非法值 fail-fast `ValueError` naming the variable（TILING 先例；detect 入口解析，非法时 primary 不运行——探针用例锚定）；不可达形态 typed 可诊断（`sfx_arbitration_partial_overlap` + 既有 `sfx_candidates`）。
  - **AC5（DELIVERED，未触发停等）**：`doc/contracts/**`、RegionInput wire、`region_creator` 签名、`_detected_region_type` 分发逻辑零改动；detect options 尾部新增 2-4 个审计键属 provenance 面（报告 Known limitations 7 注记）。
- **结构性定案（Review 必读）**：纯几何重叠信号在 BJ06 域内对照与 BJ13 误路由 case 间**反向不可分离**（域内 0.886 > 误路由 0.490-0.550）——「误路由 case 高、域内 case 低」的分离前提在既有 raw 上不成立；冻结 0.90 是证据支持的唯一零变化安全域，其语义为「双 provider 近重复双检出的类型仲裁」。**BJ13 误路由的自动化闭合不在本仲裁的现状可达域内**（双层不可达：sfx 召回缺失 + 重叠量低于保守域），闭合路径=sfx 召回恢复（域外根因，另行 Task）后按未来形态重校准（env 旋钮已预留）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC2 红态+不可达+绿态 | `"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py` | M2-TA3-B-ocr（torch 2.14.0+cpu/transformers 5.17.0/onnxruntime 1.30.0）；ogkalu 权重 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector`（model.safetensors sha256 与生产 pin 一致，provider 内三文件 pin 校验）；chiqui7 `.../M2-SFX-DETECT/weights/yolo11s-seg.onnx`（sha256 pin 校验）；@`b27c826f` | PASS：BJ13 primary=3 sfx=1（relables=None/partial=None=第一层不可达）；BJ14 6/0；BJ15 7/0；BJ06 9/8 partial=0.8865；BJ06 off/on identical=True；口径 A partial=0.5501；口径 B relabels=3 + region_type="sfx"×3 | `verification/M2-REGION-OVERLAP-ARBITRATION/raw/{arbitrate-run.log,arbitrate-pages.json,arbitrate-manifest.json,bj06-on-off-candidates.json}` |
| AC3 域内零变化 | 同上脚本（BJ06 off/on 双跑） | 同上 | PASS（17=17 逐位一致；qual 对位 17 region） | `raw/bj06-on-off-candidates.json` |
| AC3 套件基线 | `"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs` | T1.1.1-impl-py312（pytest/numpy/PIL/cv2/onnxruntime/torch(无CUDA)/PySide6 全齐）；@`b27c826f` 工作区 | **PASS：627 passed, 1 skipped, 0 failed, EXIT=0**（基线 611+1sk + 16 新用例） | `raw/pytest-three-suites.log` |
| AC3 全量（补充口径） | 同 venv `-m pytest tests -q -p no:cacheprovider -rs` | 同上 | 1731 passed, 1 skipped, **1 failed**（`m2_test_assets/test_catalog.py` 本地 gitignored 素材 manifest 计数 97 vs 100，纯本地素材状态，与本 Task 改动面零交集，不属三套件口径） | `raw/pytest-full-suite.log` |
| AC4 env typed 拒绝（先红后绿） | `python -m pytest tests/providers/test_detection_sfx.py -q -p no:cacheprovider -k arbitration`（实现前）→ 实现后同命令 | 系统 python 3.14（pytest 9.1.1） | 红：14 failed EXIT=1 → 绿：全过 | `raw/red-phase-arbitration-tests.log` |
| AC5 契约零变化 | `git diff --stat eb7cd15e..b27c826f`（仅 `detection_sfx.py` + 2 测试文件）；`git diff --check` EXIT=0 | @`b27c826f` | PASS | 本仓库 git |
| cargo/vitest | 未运行（声明零改动面：无 `src-tauri/**`、`apps/**`、前端 diff） | — | N/A（集成方复跑） | — |

环境注记：`T1.1.1-gpu-py312`（带 CUDA torch）跑同三套件为 6 failed/619 passed——全部是该 venv 依赖面与测试假设不匹配（GPU torch 存在使 `test_devices` GPU-unavailable 断言失败、onnxruntime 缺失使 real-weights 面失败），非本 Task 引入，留档 `raw/pytest-t111-py312.log` 供对照；判定以 `T1.1.1-impl-py312` EXIT=0 为准。

## 接收方式

- 分支 `agent/zcode/M2-REGION-OVERLAP-ARBITRATION`（worktree `G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode`），Review 起点=`b27c826f`（实现）+ 收尾 commit（证据/文档）。
- 复现：见 [arbitration-report.md §7](../../verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md)（两条命令：rerun 证据脚本 + 三套件；页面图像为 gitignored 只读引用，路径已记录于 raw JSON）。
- Review 建议重点：①§0/§1.4 的结构性定案（重叠反向不可分离 → 0.90 保守域 + 不可达登记）是否被确认为 AC2 的合规达成口径（替代条款：合成口径 + 如实登记）；②`detection_sfx.py` 仲裁段与降级路径的交互（降级 return 先于仲裁登记）；③options 审计键是否接受为非 wire 面。

## 下一任务建议（必填）

- Task ID / 标题：M2-REGION-OVERLAP-ARBITRATION 的 Review（现行 Task 内流转，不新建）
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者，沿 Task frontmatter 指定）
- 推荐原因与前置依赖：Task 合同要求 DSH review 确认 AC1 提案；本交付含一个必须由 Review 认定的口径问题（AC2 绿态为合成召回恢复口径 + 真实不可达登记）。
- Recovery point：本仓库、branch `agent/zcode/M2-REGION-OVERLAP-ARBITRATION`、worktree 如上、固定 base=`eb7cd15e`、实现 head=`b27c826f`。
- 允许修改路径：review 意见落 `verification/M2-REGION-OVERLAP-ARBITRATION/`（review 文档）与本 Task 文件交付记录；返修限于 Task 允许面（`detection_sfx.py`、`handlers.py`、`core_assembly.py`、对应 `tests/`、本 Task 目录）。
- 禁止范围与新增授权条件：Task 合同禁止范围不变（`doc/contracts/**`、`doc/STATUS.md`、packaging、apps、前端、他人 Task 产物、SFX OCR/重绘/权重更换）。
- 交付物：review verdict 文档（模板 doc/templates/REVIEW.md）。
- 验证命令、环境与完成 Gate：上表两条命令（rerun 脚本 + 三套件）；Gate=verdict 出具 + 集成方复跑三套件与 cargo/vitest。
- 可直接转发给 Agent 的指令：
  「对 `agent/zcode/M2-REGION-OVERLAP-ARBITRATION` @`b27c826f`（base `eb7cd15e`）出具 DSH review：读 `verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md` 与 `doc/handoffs/M2-REGION-OVERLAP-ARBITRATION-b27c826f.md`，重点复核结构性定案（域内 0.886 vs 误路由 0.550 反向不可分离 → 冻结 0.90 保守域 + BJ13 双层不可达登记）与 AC2 合成口径的合规性；复跑报告 §7 两条命令核对数字；非作者约束（不得审核自己实现的变更）。」

## 风险与遗留

1. **BJ13/14 现状不闭合（登记为不可达）**：本仲裁对当前生产权重下的 BJ13 误路由乱译损害**无直接缓解**——损害兜底仍是 M2-SFX-MISROUTE-UI-MITIGATION（人工改标）与 SfxPolicy 默认 SKIP 的既有面；误路由的自动化闭合需域外根因 Task（sfx 召回）先行。
2. **0.90 域的未来行为**：若召回恢复后出现真对白与 sfx 候选 IoU≥0.90 的形态，按设计改标进 SfxPolicy 门（SKIP 默认不渲染，人工可逆）；至今 0 观测（BJ06 最高 0.8865）。
3. **全量 pytest 的 1 个环境性失败**（素材计数）在本机长期存在，建议编排/集成方择机清理本地 `test_assets` 状态或该断言改为区间校验（另行小切片，非本 Task 范围）。
4. **UI-MITIGATION 接口注记**需 Codex 转写入 M2-SFX-MISROUTE-UI-MITIGATION Task（本 Task 未改他人 Task 产物）：仲裁只产出确定态改标，无 region 级「疑似」信号字段；「改标前疑似警示」的数据基础为空，属未来契约修订候选。
5. 回退方法：revert `b27c826f`（或运行时 `NEWMANGA_SFX_ARBITRATION=off` 即回到 pre-arbitration 行为，无需回退代码）。

## 实验附录

- 权重：ogkalu `ogkalu/comic-text-and-bubble-detector` @ `16e8a622`（model.safetensors sha256 前缀 `037930a8…` 与 `detection_manga.py` pin 一致，三文件 pin 由 provider 加载时强制）；chiqui7 `chiqui7/yolo11-manga-seg` @ `7f5f5c04`（sha256 `d87389af…` pin 强制）。
- Runtime：M2-TA3-B-ocr venv（torch 2.14.0+cpu、transformers 5.17.0、onnxruntime 1.30.0 CPU、PIL）；检测耗时 BJ13 ogkalu 9.4s、其余页 0.5-0.6s（BJ14/15/06 ogkalu 推理包含在 composite 计时内，差异源于日志流缓冲，详见 manifest `detect_elapsed_s`）。
- 网络：全程离线（无下载，weights 本地 pin 校验）。
- 参数：仲裁默认 `on`/0.90；NMS/letterbox/conf 沿生产 provider 冻结值（chiqui7 conf 0.5、NMS IoU 0.7、imgsz 1024 metadata_parsed）。
- 原始结果：`raw/arbitrate-pages.json`（四页全候选 + 参照框对位 + sfx×primary IoU）；`raw/arbitrate-manifest.json`（manifest + 合成口径 + 零变化判定）。
- 质量判断办法：AC2 红绿 = 真实 rerun 与 qual 基线对位（红）+ 生产分发函数对改标候选的 `RegionType` 判定（绿）；AC3 = off/on 全字段逐位对照 + qual 计数对位； limitations 见报告 §8。
- 失败样例：无（脚本单次通过，EXIT=0）。
