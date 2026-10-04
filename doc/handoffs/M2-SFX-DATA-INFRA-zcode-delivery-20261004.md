---
task_id: M2-SFX-DATA-INFRA
author: ZCode（subagent，Owner 实现）
recipient: Codex（Integrator，编排会话代行）
base_commit: 4c12e8af
delivery_head: ecb39e67ff8eba63bf0586beaa00291b76bc29fc
status: delivered（待 Review，Task status 保持 in_progress）
---

# Handoff：M2-SFX-DATA-INFRA（T1a，SFX 训练数据基础设施）

## 交付结果

**提交链**：claim `339f11a0` → red `037a44cf`（三组断言先行，19 failed+4 error 红留证）→
green `673c3c1f`（全实现）→ data `ecb39e67`（真实管线首跑+语义修正，=delivery_head）。

**变更路径**（25 文件，全部在允许范围内；`git diff 4c12e8af..HEAD` 禁改范围零触碰）：

- `experiments/M2-SFX-DATA-INFRA/sfx_data_infra/`：schema / splits / atomicio / hash / dedup / synth / importers / cli / `__main__`（零新依赖：stdlib+PIL+numpy）
- `experiments/M2-SFX-DATA-INFRA/tests/`：5 测试文件 29 tests（红绿纪律三组先行）
- `experiments/M2-SFX-DATA-INFRA/`：README.md（口径冻结+组键规则）、schema.json（JSON Schema 双落地）、manifest_summary.json（Git 只进此摘要）
- `verification/M2-SFX-DATA-INFRA/`：red-run.log / green-run.log / pipeline-run.log / data-infra-report.md
- `.gitignore`：加 `/training_data/`（数据本体出 Git）

**AC 逐项**（详细证据见 verification/M2-SFX-DATA-INFRA/data-infra-report.md）：

- AC1 schema 冻结：dataclass+JSON Schema 双落地+一致性测试；**GT 口径冻结=sfx 实例包络（含遮挡推断）**，4 条理由写入 README §口径冻结
- AC2 拆分器：组键规则（peppercarrot ja/kr 同 ep 同组防泄漏）；BJ13/14/15 单列 challenge；`group-hash-rank-v2` seed=20261004 冻结+fingerprint；派生 fixpoint 继承；TrainingSetBuilder 构造期丢弃 test/challenge+allowlist 拒绝（API 无取回通道）
- AC3：dhash+框精确哈希双去重（判重=同图+同框集合）；manifest 原子写（tmp+fsync+bak+replace+读回校验）+crash 注入测试通过
- AC4：合成 PoC 24 样本（≥20），arc/rotate/perspective 点与像素同一几何函数，**参数↔标注互算 max err 2.27e-13 px**；AI 整图未引入（pseudo 不入 GT 语义已冻结）
- AC5：7（l3 参照框，partial）+8（BJ06 自证框，partial，**source_sha256 对账一致**）+43（ogkalu，pseudo）=58 一键导入；ogkalu 11 空 detections 以空框 pseudo 负证据入册（43 全量）
- AC6：零 src；`--help`/`selfcheck` EXIT=0；数据本体落 gitignored `training_data/sfx-v1/`

**数据产出**：全集 82 样本/71 图/206 框；拆分 challenge 7/train 39/val 31/test 5（12 来源组，
fingerprint `a02fed3d…` 重放一致）；去重 0 误杀；训练构建器可读 70（train+val），泄漏检查=[]。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC2 派生同集合 | `python -m pytest tests/test_splits_derived_same_set.py -q` | py312 venv @ecb39e67 | PASS（9 tests） | green-run.log |
| AC3 中断恢复 | `python -m pytest tests/test_atomic_recovery.py -q`（含子进程 replace 前 `os._exit(1)` 注入） | py312 venv @ecb39e67 | PASS（4 tests） | green-run.log |
| AC4 GT 互算 | `python -m pytest tests/test_synth_gt_roundtrip.py -q`（前向像素⊆包络/逆变换 2.27e-13/遮挡不裁包络/渲染确定性） | py312 venv @ecb39e67 | PASS（6 tests） | green-run.log |
| AC1 schema | `pytest tests/test_schema.py -q` | py312 venv @ecb39e67 | PASS（6 tests） | green-run.log |
| AC5 导入 | `python -m sfx_data_infra pipeline`（导入 7+8+43，BJ06 sha256 对账） | py312 venv @ecb39e67 | PASS EXIT=0 | pipeline-run.log |
| AC6 CLI | `python -m sfx_data_infra --help`；`python -m sfx_data_infra selfcheck` | py312 venv @ecb39e67 | EXIT=0 ×2 | 报告 §验证记录 |
| 复现性 | 盘上 manifest 重放 `assign_splits` 比对 fingerprint | py312 venv @ecb39e67 | 一致（`a02fed3d…`） | 报告 §验证记录 |
| 泄漏检查 | `[s for s in builder.samples if s.split not in ('train','val')]` | py312 venv @ecb39e67 | `[]` | 报告 §验证记录 |
| gitignore | `git check-ignore training_data/sfx-v1/manifest.full.json` | @ecb39e67 | `.gitignore:13:/training_data/` | 报告 |
| 红色证据 | `pytest tests/ -q`（实现前） | py312 venv @037a44cf | 19 failed+4 error | red-run.log |

未运行：训练实际消费该 manifest 的端到端训练（属 T2/T3 范围）；合成样本的模型质量提升
归因（无模型训练发生，不得据本 Task 声明检测质量变化）。

## 接收方式

- 分支/工作树：`agent/zcode/M2-SFX-DATA-INFRA` @ `G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode`（HEAD=ecb39e67，工作树干净，数据本体在 gitignored 区不受影响）
- 复现：`cd experiments/M2-SFX-DATA-INFRA && "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/ -q`（29 passed）；`... -m sfx_data_infra selfcheck`（EXIT=0）；`... -m sfx_data_infra pipeline --data-root <任意外部目录> --summary-out <tmp>`（可复现到同 fingerprint，seed 冻结）
- 前置条件：ogkalu crop 图在 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/`（43/43 在盘已验证）；BJ 页图像在 E2E-MATERIAL/TA2B worktree（只读导入）；素材根可 env `SFX_DATA_ASSET_ROOTS` 覆盖
- Reviewer（DeepSeek Harness）建议重点：①口径冻结理由（README §口径冻结）②ogkalu 空框负证据入册口径 ③dedup 判重语义（同图+同框集）④val 组样本级不均的接受度

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-DATA-INFRA 的 Review（DeepSeek Harness，非作者）——本 Handoff 即评审输入；无新 Task 需创建
- 推荐 Agent / Reviewer：DeepSeek Harness（独立 Review）
- 推荐原因与前置依赖：合同指定 reviewer=DeepSeek Harness（非作者）；实现已齐，可直接进入 review→integration 流程
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-SFX-DATA-INFRA`，base `4c12e8af`，head `ecb39e67`；worktree 已存在（上列路径）
- 允许修改路径：Review 报告落 `verification/M2-SFX-DATA-INFRA/**`；不得直接改实现
- 禁止范围与新增授权条件：`src/**`、`tests/**`（仓库级）、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`test_assets/**`；对 schema 口径/组键/负样本语义的异议走 Review 意见→Codex 裁定→本 Task r2
- 交付物：Review 报告（PASS/FAIL+逐 AC 结论+意见清单）
- 验证命令、环境与完成 Gate：上表「验证证据」命令在 reviewer 机器复跑；Gate=29 tests passed+selfcheck EXIT=0+pipeline 可复现 fingerprint
- 可直接转发给 Agent 的指令：
  「你是 DeepSeek Harness（非作者 Reviewer）。对 M2-SFX-DATA-INFRA 做独立 Review：分支 agent/zcode/M2-SFX-DATA-INFRA @ ecb39e67（worktree G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode）。读 doc/tasks/M2-SFX-DATA-INFRA.md 合同 AC1-AC6、experiments/M2-SFX-DATA-INFRA/README.md（口径冻结/组键）、verification/M2-SFX-DATA-INFRA/data-infra-report.md 与三个 run log。复跑：pytest tests/ -q（预期 29 passed）、python -m sfx_data_infra selfcheck（预期 EXIT=0）。重点裁决：①GT=实例包络口径及理由 ②ogkalu 11 空框负证据以 pseudo 入册 ③dedup 同图+同框集判重 ④val 组样本级不均。报告写 verification/M2-SFX-DATA-INFRA/review-r1.md，引用文件与行号；禁改实现与共享契约。」

## 风险与遗留

1. val 仅 2 组但 31 样本（组数 12 下按组切片）：批量数据入册后缓解；需样本级均衡则要新决策
2. ogkalu 11/43 空框负证据入册口径待 review 确认（可一行开关过滤）
3. 合成域差距已量化登记（横排 AR 2.3–4.5 vs BJ13 真竖排 0.4–0.5；系统字体非毛笔体）：PoC 只声明管线正确性，不声明域覆盖；批量生产 Task 需竖排+艺术字体源+页级尺度+真实底图
4. 素材根默认硬编码本机 worktree 路径（env 可覆盖），跨机器需配置
5. 未跑：真实训练消费端到端（T2/T3）；模型质量归因不适用

## 实验附录（仅实验任务）

- 数据来源与许可：densho810（BJ06/13/14/15，已登记利用报告，窗口 2026-11-02 前）；ogkalu weights license 记录于样本 provenance.model_license；K01-K10=Vasyanator2（CC-BY-NC 类，noncommercial_research_source_restricted）；未再分发行外素材
- 数据 Hash：manifest.full.json `095a3c590c29f9c5617edaa57fd959459e3ee16dd515873d3cc367ad4380b56b`；manifest.train.json `17129854061a9ba83b17d04715d527dbb09bbbef62cbb031f4128e7f35acf399`；BJ06 页对账 `b06c9d7ddb0f…`（qual 记录一致）
- 模型/权重：未训练任何模型；ogkalu 检测框为既有资产导入（weights_sha256 见样本 provenance）
- Provider/Runtime：无远程调用；本机 py312 venv
- 参数：split seed=20261004，method group-hash-rank-v2（train 0.70/val 0.15/test 0.15 组级切片）；synth seed=20261004+样本偏移，24 组合（旋转 ±25°、arc ±35px、persp ≤48px、遮挡 1/3）
- 运行次数：pipeline 首跑+语义修正后重跑（最终口径以 ecb39e67 的 pipeline-run.log 为准）；split 重放一致性 1 次
- 原始结果：manifest_summary.json（Git 内）+training_data/sfx-v1/manifest.*.json（gitignored 外部树）
- 质量判断办法：GT 互算断言（像素⊆包络/逆变换 2.27e-13）/BJ13 对照量化/复现 fingerprint
- 失败样例：开发期发现并修复 4 处（forward 漏前段变换/anchor 点列自交/measure_anchor_box 四元组误用/dedup 同图误杀）——过程见 red→green diff
- 限制：合成样本非域内数据；本 Task 不产出模型或质量结论
- 建议：T1b（批量数据生产）从竖排渲染+真实底图合成切入；组数≥30 后复核 val 分布
