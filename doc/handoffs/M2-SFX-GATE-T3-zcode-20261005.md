---
task_id: M2-SFX-GATE-T3
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（Reviewer）
base_commit: 87ca8724
delivery_head: 2e95760a（AC4 评测执行；AC5 判定文档见本 Handoff 提交）
status: in_review
---

# Handoff：M2-SFX-GATE-T3 — SFX 正式评测门（G1-G8 判定+T4 材料终稿）

## 交付结果

Task 四层交付全链完成（AC1-AC6），分支 `agent/zcode/M2-SFX-GATE-T3`，base=`87ca8724`：

1. **AC1 Gate 定义冻结** @`907011a2`：[gate-definition.md](../verification/M2-SFX-GATE-T3/gate-definition.md) v1.0-frozen（G1-G8 合同级权威化，冻结时序经复核实证——评测执行后零修改）。
2. **AC2 R3-MISS 补画+AC3 KO 非派生考题** @`3c84f438`：BJ32-35 转正 15 框（ai-direct-annotation 首例，a13/b17/matched12→12 union+3 arbiter keep；BJ36/37 双 AI 终裁 0 框如实）+npd 非派生 GT 135 框（a128/b135/matched106→106 union+29 arbitrated kept，隔离纪律 task_brief_leak_check=PASS）+train-v4 重切 916 全量（9 断言落盘复算全 PASS，考卷 5 框逐位=R2 出厂）。
3. **AC4 正式评测执行** @`2e95760a`：三方（chiqui7 pin 原样零重指/v2a `27d162e9…`/v2b `944e8114…` 进程内重指）×四数据集（bj-exam 考卷 5 框/bj-ext 12 页 33 框/ko-tile 派生 56 框 tile_ov128/ko-npd 非派生 135 框），conf0.5 主+0.2 诊断，36 格（24 主+12 letterbox 对照）全部复算一致。
4. **AC5 判定+T4 终稿**（本提交）：[gate-t3-report.md](../verification/M2-SFX-GATE-T3/gate-t3-report.md)——G1-G8 逐门判定+前置数据+矩阵+复核+诚实边界+T4 终稿（切换候选建议/许可审计结算/tile 化方案/回退方案）。
5. **AC6 零 src**：`git diff --name-only 87ca8724..HEAD` 26 文件（HEAD=2e95760a 时点：doc/tasks 1+experiments 8+verification 17）+2 docs（AC5 轮：gate-t3-report.md+本 Handoff/Task 回填）全在 Task 允许路径，src/tests/doc/contracts/packaging/apps/doc/STATUS.md diff=0；生产 pin `d87389af…`（detection_sfx.py:110-112）base..HEAD 逐字一致；数据本体 gitignored（training_data/），Git 只进摘要+raw JSON。

**门判定结论（详据见报告 §4）**：

| 门 | 判定 |
|---|---|
| G3 先决 | PASS（9/9 断言，先决成立） |
| G1 BJ 门 | **v2a FAIL**（R 4/5 达线但 P 0.8<0.8333）/ **v2b PASS**（5/5 P=1.0） |
| G2 KO 门 | **v2a FAIL**（KO-B 0.2593<基线 0.3037）/ **v2b PASS**（0.3556≥0.3037；口径合规两候选均 PASS） |
| G4/G6 | directional 登记（覆盖矩阵含已知缺口原样入表/四层归因） |
| G5 生产序列契约 | 双候选 PASS 5/5（①SHA 门 PROVIDER_FAILED 引用 V2 当轮证据 export-smoke-v2.json sha_gate.fired=:38-43/:122-127，sha_gate.ok=:44-50/:128-134——T3 当轮未复跑，显式收编） |
| G7 端到端损害 | **PASS（条件性：T4 补证前置）**（冻结口径=T0/V2 冒烟方式=检测契约面，编排裁决 2026-10-05 确认；翻译链深层调用未以新权重执行——T4 部署前必须补跑 BJ06 型 policy=translate 端到端冒烟，未补证前不得把 G7 记为部署就绪） |
| G8 部署门 | **v2b 7/7 出证 PASS（license:other 审计本门执行=PASS 附登记义务，候选资格保持）**；v2a 已因 G1/G2 丧失资格（审计只登记） |

**候选资格：v2b（`944e8114…`）=唯一全硬门通过候选；切换与否=T4 用户裁决点。**

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 冻结 | `git log -- verification/M2-SFX-GATE-T3/gate-definition.md`（复核轮） | 2e95760a | PASS（仅 907011a2 一提交，评测后零修改） | gate-definition.md |
| AC2/AC3 数据 | `python experiments/M2-SFX-GATE-T3/verify_data_integrity.py` | AC5 轮实测 @本提交 | PASS（9/9，EXIT=0，复算后 json 与提交版逐位一致） | verification/M2-SFX-GATE-T3/data-integrity-asserts.json |
| AC4 矩阵复算 | `python experiments/M2-SFX-GATE-T3/recompute_eval_t3.py` | AC5 轮实测 @本提交 | PASS（ALL CELLS RECOMPUTED == eval-matrix.json，EXIT=0） | eval-matrix.json + raw/ 12 文件 |
| AC4 评测执行 | `python experiments/M2-SFX-GATE-T3/eval_gate_t3.py`（full） | 2e95760a | PASS（36 格落盘，EXIT=0） | raw/run-full.log |
| 权重 sha | python hashlib 三 onnx 盘上重算 | AC5 轮实测 | PASS（chiqui7=`d87389af…`=生产 pin 逐字/v2a=`27d162e9…`/v2b=`944e8114…`） | eval-matrix.json weights |
| 零 src | `git diff --name-only 87ca8724..HEAD` + 禁止路径过滤 | AC5 轮实测 | PASS（26 文件全在允许路径；src/tests/contracts/packaging/apps/STATUS=0） | 本 Handoff §交付结果 |
| 标注独立性 | 作者侧脚本重算（复核轮，IoU 分布/数值指纹/派生交叉核对；正式独立 Review=DSH r1 见 doc/reviews/） | 2e95760a | PASS（无泄漏信号；任务书无泄漏为作者自查字段，本项为产物级间接验证） | gate-t3-report.md §5 |
| NOT_RUN | PROVIDER_FAILED 反向验证（T3 当轮）、翻译链深层调用（新权重）、重训/消融 | — | NOT_RUN（前者引用 V2 证据收编，后者列 T4 补证） | gate-t3-report.md §4.5-1/§4.7/§6 |

## 接收方式

- 分支 `agent/zcode/M2-SFX-GATE-T3`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode`；base=`87ca8724`，AC4 head=`2e95760a`，AC5=本 docs 提交（review 从 base 或 2e95760a 均可，判定文档在 docs 提交）。
- Reviewer（DSH）建议检查点：①判定是否逐门符合 gate-definition v1.0 §4 判定规则（重点：G1 精度线 0.8333 的判据值口径、G2-B 相对不回退的基线取值、G7 执行边界的定性是否接受）；②G8-4 license 审计结论与登记义务是否认可；③非派生 GT=ai-consensus 的「模型质量载体」限制表述是否充分。
- 复现命令：`python experiments/M2-SFX-GATE-T3/verify_data_integrity.py`；`python experiments/M2-SFX-GATE-T3/recompute_eval_t3.py`（数据在 gitignored 外部树，须本机在位：train-v4/annotate-r4/R2 final/三权重 onnx）。

## 下一任务建议（必填）

- **Task ID / 标题**：M2-SFX-PROD-SWITCH-T4「SFX 生产切换（T4）：v2b pin 替换+KO tile 化+端到端补证」——**等待用户裁决**（切换与否+tile 化性能预算为用户裁决点；T4 Task 尚未在 REBASELINE_PLAN 释放，释放前不得实施）。
- **推荐 Agent / Reviewer**：Owner=ZCode（src pin 变更+tile 化实现）/ Reviewer=DeepSeek Harness（非作者）/ Integrator=Codex。
- **推荐原因与前置依赖**：T3 全硬门已出判定（v2b 唯一候选+审计结算+tile 化方案+回退方案终稿），T4 材料齐；依赖=用户对 §7.1 切换裁决+§7.3 性能预算裁决。
- **Recovery point**：主仓库 `G:/CODEX/New Manga`（T4 为新 Task，base=本 Task merge 进 main 后的 integration commit，**待 Codex 集成后确定**；worktree 待 Codex 创建）。
- **允许修改路径**：`src/infrastructure/providers/detection_sfx.py`（pin+来源字段+KO tile 分支）、对应 tests、packaging 权重通道——**均为 T4 授权范围，T3 未触碰**。
- **禁止范围与新增授权条件**：src 变更需 Codex 释放 T4 Task 明确范围；v2b 权重分发场景须先复核 Manga109-s/MangaSeg 授权边界（G8-4 登记义务①）。
- **交付物**：pin 单值替换+来源字段处置（HF or 本地通道登记）、KO tile 分支（G2 冻结口径实现+相位复测）、v2b BJ06 型端到端冒烟补证（policy=translate 全链）、回退验证、训练数据备案时点核查（densho810 窗口 2026-11-02）。
- **验证命令、环境与完成 Gate**：`python -c "import hashlib;…"` 权重 sha==新 pin；`pytest tests/ -k sfx`；tile 化后 KO 域复测（相位核对：chiqui7 参考矩阵 56/56 P0.8235 逐位）；端到端冒烟 EXIT=0；Gate=生产序列契约 5 断言+端到端补证全过。
- **可直接转发给 Agent 的指令**：等待用户裁决 v2b 切换与 tile 化预算；若裁决切换，以 T3 gate-t3-report.md §7 终稿为合同释放 T4 Task（Owner=ZCode，base=T3 integration commit），按 §7.3/§7.4 执行 pin 替换+tile 化+补证三项，全部 src 变更走 T4 授权，完成后交 DSH 独立 review。**裁决前无需下一步操作（不创建占位 Task）。**

## review-fix(GATE-T3 r1) 返修记录（2026-10-05，DSH r1 approved_with_conditions 条件闭合）

- **P1-1**：G7 改标「PASS（条件性：T4 补证前置）」（报告 §0/§4.7/§6-5/§7.4-①/§7.1+本 Handoff+Task 同步；条件=T4 部署前必须以新权重补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用），未补证前不得把 G7 记为部署就绪；候选资格结论不变，v2b 由 G1/G2/G5/G8 定资格）。编排裁决（2026-10-05）=接受「G7 冻结口径边界=检测契约面」，已登记 Task 正文返修记录。
- **P2-1**：AC3 51 单元仲裁终裁导出独立档案 `training_data/sfx-v1/gate-t3/npd-judgments/arbiter/batch-1.json`（51 单元 verdict/final_xyxy/rationale，与 AC2 同构）+`finalize_npd.py` 改为读取该档案并逐单元断言（对齐 `stage_r4_manifest.py:52/67-68` 模式）+`divergence.json` arbiter 指针修正为 `npd-judgments/arbiter/batch-1.json`。重跑验证：npd-gt.json 除 P4-4 措辞字段外逐位不变；`verify_data_integrity.py` 9/9 PASS 且 `data-integrity-asserts.json` 与提交版 git diff 为空；`recompute_eval_t3.py` ALL CELLS RECOMPUTED。
- **P2-2**：gate-definition.md §6 追加**不回溯**版本行 v1.1（challenge 成员随 vol05 组转正扩展为 pre-bj17/pre-bj18/pre-bj32 三页 8 框；**G1 判据集不变=原始 5 框**，S4 original_5box_bitwise_r2 断言保持）+§4.G3 措辞修正——§5.3 机制内追加式变更，已判定门定义与阈值零改动，**待 DSH 确认**。
- **P2-3**：报告 §5 改称「作者侧复核（workflow 内 phase 5，非本 Task 正式独立 Review）」；「preds 整数占比 12.8%」标注（过程观察，未舍入坐标未落盘，不可复算）；「独立脚本重算」→「作者侧脚本重算」。
- **P3-1/P3-3/P3-4/P3-5/P4-1/P4-2/P4-3/P4-4**：收编 sha 依据补注（§4.5-1）/credit 保守登记（§4.8-4+§7.2）/§8 证据索引补 `arb_previews_npd.py`（共 8 脚本）/「26 文件（HEAD=2e95760a 时点）+2 docs」改述/「逐位=R2 出厂」统一为「逐值（0.1 精度）等值」（比较逻辑零改动）/`prepare_dataset_v4.py:72` 开发期注释删除/行号引用统一（sha_gate.fired=:38-43/:122-127，sha_gate.ok=:44-50/:128-134）/coincidence_evidence 双向措辞——全部落地。

## 风险与遗留

1. **G5-① 证据边界**：PROVIDER_FAILED 反向验证=T3 当轮未复跑、引用 V2 当轮证据显式收编（export-smoke-v2.json sha_gate.fired=:38-43/:122-127，sha_gate.ok=:44-50/:128-134）——若 Reviewer 不接受收编口径，须补跑后 G5 才终判。
2. **G7 条件性 PASS**：翻译链深层调用未以新权重执行（冻结口径=T0/V2 冒烟方式=检测契约面）；T4 部署前必须补跑 BJ06 型 policy=translate 端到端（§7.4-①），未补证前不得把 G7 记为部署就绪。
3. **非派生 GT=AI 共识**：G2-B 绝对 recall 带 ai-consensus 标注质量层误差（与派生 GT 交集仅 40/135 差集粒度大）——相对不回退结论稳健，绝对值不外推。
4. **KO 域现状**：切换权重对 KO 零改善（letterbox 结构性全零）；KO 改善=T4 tile 化+性能预算裁决。
5. **回退**：pin 恢复 `d87389af…`+NSIS 通道不动即回退，无数据迁移、无破坏性操作。
6. train-v4/npd-gt/权重本体均在 gitignored 外部树（G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode、M2-SFX-ANNOTATE-R2-zcode、task-envs/M2-SFX-DETECT）——异机复核需先备齐数据路径。
