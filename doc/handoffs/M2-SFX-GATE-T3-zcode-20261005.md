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
5. **AC6 零 src**：`git diff --name-only 87ca8724..HEAD` 26 文件全在 Task 允许路径（doc/tasks 1+experiments 8+verification 17+本 docs 提交），src/tests/doc/contracts/packaging/apps/doc/STATUS.md diff=0；生产 pin `d87389af…`（detection_sfx.py:110-112）base..HEAD 逐字一致；数据本体 gitignored（training_data/），Git 只进摘要+raw JSON。

**门判定结论（详据见报告 §4）**：

| 门 | 判定 |
|---|---|
| G3 先决 | PASS（9/9 断言，先决成立） |
| G1 BJ 门 | **v2a FAIL**（R 4/5 达线但 P 0.8<0.8333）/ **v2b PASS**（5/5 P=1.0） |
| G2 KO 门 | **v2a FAIL**（KO-B 0.2593<基线 0.3037）/ **v2b PASS**（0.3556≥0.3037；口径合规两候选均 PASS） |
| G4/G6 | directional 登记（覆盖矩阵含已知缺口原样入表/四层归因） |
| G5 生产序列契约 | 双候选 PASS 5/5（①SHA 门 PROVIDER_FAILED 引用 V2 当轮证据 export-smoke-v2.json:38-45/122-127——T3 当轮未复跑，显式收编） |
| G7 端到端损害 | 双候选 PASS（按冻结口径=T0/V2 冒烟方式；翻译链深层调用未以新权重执行=执行边界，列为 T4 部署前置补证） |
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
| 标注独立性 | 独立脚本重算（复核轮，IoU 分布/数值指纹/派生交叉核对） | 2e95760a | PASS（无泄漏信号；任务书无泄漏为作者自查字段，本项为产物级间接验证） | gate-t3-report.md §5 |
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

## 风险与遗留

1. **G5-① 证据边界**：PROVIDER_FAILED 反向验证=T3 当轮未复跑、引用 V2 当轮证据显式收编（export-smoke-v2.json:38-45/122-127）——若 Reviewer 不接受收编口径，须补跑后 G5 才终判。
2. **G7 执行边界**：翻译链深层调用未以新权重执行（冻结口径=T0/V2 冒烟方式）；T4 部署前补跑 BJ06 型端到端（§7.4-①）。
3. **非派生 GT=AI 共识**：G2-B 绝对 recall 带 ai-consensus 标注质量层误差（与派生 GT 交集仅 40/135 差集粒度大）——相对不回退结论稳健，绝对值不外推。
4. **KO 域现状**：切换权重对 KO 零改善（letterbox 结构性全零）；KO 改善=T4 tile 化+性能预算裁决。
5. **回退**：pin 恢复 `d87389af…`+NSIS 通道不动即回退，无数据迁移、无破坏性操作。
6. train-v4/npd-gt/权重本体均在 gitignored 外部树（G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode、M2-SFX-ANNOTATE-R2-zcode、task-envs/M2-SFX-DETECT）——异机复核需先备齐数据路径。
