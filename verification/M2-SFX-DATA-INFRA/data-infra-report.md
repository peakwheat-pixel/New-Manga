# M2-SFX-DATA-INFRA 数据基础设施交付报告

- Task: M2-SFX-DATA-INFRA（T1a，status=ready @4c12e8af release）
- Owner: ZCode（subagent）；Reviewer: DeepSeek Harness（非作者）
- 分支/工作树: `agent/zcode/M2-SFX-DATA-INFRA` @ `G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode`
- 链: claim `339f11a0` → red `037a44cf` → green `673c3c1f` → data/docs（见 delivery_head）
- Python: `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（PIL 12.3.0 / numpy 2.5.3 / pytest 9.1.1，零新依赖）

## AC 对照

| AC | 结论 | 关键证据 |
|---|---|---|
| AC1 schema 冻结 | **完成** | `sfx_data_infra/schema.py` dataclass + `schema.json`（draft-07，由 `make_json_schema()` 生成，`test_schema_json_file_matches_generator` 断言双落地一致）；字段=图引用(path+sha256+w+h)/框(多边形+cls+text+occluded)/`annotation_status complete\|partial\|pseudo\|synthetic`/provenance(type=asset_case\|synthetic_render\|derived\|external_model)/group/split/created_at。**口径冻结：GT=sfx 实例包络（含遮挡推断），理由 4 条写入 README §口径冻结** |
| AC2 分组隔离拆分器 | **完成** | `splits.py`：组键规则（README §组键；peppercarrot ja/kr 同 ep 强制同组防泄漏）；BJ13/14/15 单列 challenge；`group-hash-rank-v2` 排序切片（seed=20261004 冻结+fingerprint `a02fed3d…`）；派生 fixpoint 继承父 split；`TrainingSetBuilder` 构造期丢弃 test/challenge 且 allowlist 含即抛 `SplitAccessError`（API 无取回通道）。真实数据重放 fingerprint 一致 |
| AC3 去重+原子写 | **完成** | dhash 自实现（PIL+numpy，64bit 横向梯度）+框级精确哈希（规范化坐标 0.1px+cls+text+图 sha）；判重语义=同图+同框集合（一页多实例合法，首版误杀已修）；manifest 原子写=tmp+fsync+os.replace+读回校验+残留 tmp 清理；子进程 `os.replace` 前注入 `os._exit(1)` 的 crash 测试通过 |
| AC4 合成渲染 PoC | **完成** | 24 样本（≥20），`annotation_status=synthetic`；arc→rotate→perspective+translate 点与像素走同一几何函数；GT 包络=forward(anchor 路径序 64 采样点)；**互算断言**：A 字形像素⊆包络（容差 2px）/B forward∘inverse 全点还原（max err 2.27e-13 px）/C 遮挡只作用图像层不改变 GT 包络；AI 整图生成未引入（schema 语义已冻结 pseudo 不入 GT） |
| AC5 存量导入器 | **完成** | `importers.py` 一键 7+8+43=58：l3 七参照框→`partial`（页图 BJ13/14/15 在 E2E-MATERIAL worktree）；BJ06 八自证框→`partial`（页图在 TA2B worktree，**导入时对账 qual 记录 source_sha256 `b06c9d7d…` 一致**）；ogkalu 43 region→`pseudo`（crop 图 43/43 在盘，原始 cls/conf/harvest 阈值入 provenance；其中 11 region detections 为空→空框 pseudo 负证据样本，schema 冻结允许且 43 全量入册） |
| AC6 零 src+CLI | **完成** | `git diff 4c12e8af..HEAD --stat` 零 src/tests/contracts/packaging/apps/STATUS/test_assets 变更；`python -m sfx_data_infra --help` EXIT=0；`selfcheck` EXIT=0（schema 往返/dhash/几何互算 5.7e-14/原子写恢复 4 项自检全 OK）；数据本体落 `training_data/sfx-v1/`（`.gitignore` 加 `/training_data/`，check-ignore 验证） |

## 数据产出（真实管线 `pipeline`，EXIT=0）

- 导入 58 样本 / 182 框 / 素材副本 47 文件；合成 24 样本（PNG 落 `training_data/sfx-v1/synthetic/`）
- 全集 82 样本 / 71 独立图 / 206 框；by_status: partial 15 / pseudo 43 / synthetic 24
- 拆分（12 来源组，seed 20261004）：challenge 7 / train 39 / val 31 / test 5；lock fingerprint `a02fed3da3a8aba11d6e718985633a81b341aca373e70e8dcf07a6a7a431da1e`
- 去重：0 重复（判重语义修正后无误杀；ogkalu 11 空框负证据样本非重复）
- 训练构建器：train 39 + val 31 = 70 可读；test 5 + challenge 7 构造期剔除，泄漏检查=[]
- manifest 落外部树：`manifest.full.json` sha256 `095a3c59…`（234KB）、`manifest.train.json` sha256 `17129854…`；Git 只进摘要 `experiments/M2-SFX-DATA-INFRA/manifest_summary.json`

## 红绿纪律（合同测试表三场景）

| 场景 | red commit `037a44cf` | green（`673c3c1f` 及后续） |
|---|---|---|
| AC2 派生同集合 | 8 tests FAILED（red-run.log） | 9 tests PASSED：组内不拆散/派生继承/挑战单列/seed 复现/builder 禁 test/组键规则 |
| AC3 中断恢复 | 4 tests FAILED | 4 tests PASSED：round-trip/损坏拒绝/crash 注入旧版完好+重跑完整/错误 kind 拒绝 |
| AC4 GT 互算 | 3 FAILED+4 ERROR | 6 tests PASSED：≥20 样本/前向字形像素⊆包络/逆变换全点还原/遮挡不裁包络/渲染逐像素确定/schema.json 一致 |

终态：`pytest tests/ -q` → **29 passed**（green-run.log；含后续修正的重跑，见验证记录）。

## BJ13 真图对照登记（合同风险项，不阻塞）

| 维度 | 合成 PoC（24 样本） | BJ13/14/15 真参照框（7 框） |
|---|---|---|
| 排版方向 | 横排 | **竖排细高** |
| 框纵横比 | 2.26–4.51（均值 3.55） | 0.40–0.50 |
| 实例尺寸 | 108–370 × 42–82 px | ~250–350 × ~550–840 px（页 2650×3810 级） |
| 字体 | meiryo/msgothic/YuGothR/malgun（系统字，无毛笔体/艺术字） | 手绘拟声词（笔画粗细/抖动/飞白） |
| 背景 | 浅噪底+遮挡贴片 8/24 | 真实页（网点/对话框/效果线交叠） |

结论：本 PoC 验证的是**几何↔GT 管线正确性**（互算精确），不声明域覆盖。批量生产 Task
需补：竖排文字渲染、毛笔体/艺术字字体源、页级尺度渲染、真实底图合成（inpaint 后页）。

## 验证记录（本会话实际执行）

- `pytest tests/ -q`：29 passed（`verification/M2-SFX-DATA-INFRA/green-run.log`）
- `python -m sfx_data_infra --help` EXIT=0；`python -m sfx_data_infra selfcheck` EXIT=0
- `python -m sfx_data_infra pipeline` EXIT=0（`pipeline-run.log`）
- `git check-ignore training_data/sfx-v1/manifest.full.json` → `.gitignore:13:/training_data/`
- 拆分重放：盘上 manifest 重跑 `assign_splits` fingerprint 与 lock 一致
- builder 泄漏检查：`[s for s in builder.samples if s.split not in ('train','val')]` = []

## 遗留与风险

1. **val 组仅 2 组但含 31 样本**（synthetic/poc 22+vasyanator2/641253 9）：切片按组数比例
   （12 组→8/2/2），样本级分布不均。批量数据入册后组数上升会自然缓解；若需样本级均衡
   需改分层策略（新决策，不擅动）。
2. **ogkalu 11/43 空框负证据样本**：schema 冻结允许 pseudo 空框；若 DeepSeek review 认为
   负样本不应入 manifest，可加 `provenance.negative` 过滤开关（一行），43 入册口径不变。
3. **域差距**见上表：合成样本不用于域内评估，只入 train/val 作辅助监督。
4. **素材根硬编码**本机 worktree 路径（`importers.DEFAULT_ASSET_ROOTS`），env
   `SFX_DATA_ASSET_ROOTS` 可覆盖；跨机器复现需先配素材根。
5. BJ06 对账依赖 qual-BJ06.json 内嵌 sha256；素材被替换时会 fail-fast（本次一致）。
