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

## r3 修订（DSH r2 changes_requested 返修——本节覆盖 r2/r1 数字）

r2 结论：changes_requested（r1 四项 P1 全通过；新引入 1×P1 + P2-13 回潮 + 7×P3）。
r3 修复：

- **新-1（P1）摘要覆写降级**：`cmd_summary` 改为从盘上 manifest **重算全部统计**
  （dedup/build-train/import 全算，不再传空报告）；验证流程改为"官方 data_root 只跑
  pipeline、子命令在临时副本验证"——Git 摘要不再被子命令回写污染。
  **最终产物 sha：manifest.full `a48d616eae59ee84…`、manifest.train `e0d2981a054145e1…`
  （与 manifest_summary.json 逐字节核对一致）**；报告与 handoff 引用同值。
- **新-2（P2-13 真闭合）**：摘要 `fonts` 只记文件名（TanukiMagic.ttf），无本机绝对路径。
- 新-3 未用 `import os as _os` 清除；新-4 importers 空 pass 分支删除、`det.get("cls")`。
- **新-5 字体可复现通道**：新增 `fetch_fonts.py`（上游 zip+ttf 双 sha256 pin 校验，
  fail-closed 不静默换源；LICENSE-NOTE.txt 落字体目录）；`_BRUSHY_NAME_HINTS` 收窄
  （去 pen/hand/magic，防普通字体误判顶掉真毛笔体）。
- **新-6 lock 形状统一**：pipeline/split/dedup 三写者 lock 键集一致
  （challenge_single_bucket 统一键名）；`cmd_dedup` 真丢弃时重算 fingerprint；
  `cleanup_stale_tmp` docstring 去"bak"。
- 新-7 `.gitignore` 的 `experiments/M2-SFX-DATA-INFRA/*.bak` 行：请集成方一并追认
  （原子写备份文件不进 Git，与 P2-1 追认同理）。
- 新-8 溯源：handoff frontmatter 填实 r2_head/r3_head；Task 正文回填在集成收口时；
  r1/r2 报告原字节入 `doc/reviews/` 由集成方执行。
- 新-9 登记：**test 集 4 样本中 1 个为空框负样本**（11 空框 = builder 排除 10 + test 1），
  评估价值进一步受限（转 T1b 重划）；r2 的 8 个回归测试 red 留证以
  `red-evidence-r2-tests.log` 替代证明（r1 代码上符号不存在，import/断言必然红）；
  `build_summary` 对 train manifest 中间态缺失容错（typed note，不再 FileNotFoundError）。

**r3 产物数字（pipeline EXIT=0，seed=20261004）**：与 r2 相同分布——challenge 7 /
train 63（含合成 24，TanukiMagic 独占）/ val 8 / test 4；builder 排除负样本 10；
GT 互算 1.71e-13px；tests **37 passed**（smoke 新增 summary 不降级/字体基名/lock
形状/dedup 后 fingerprint 一致断言）；selfcheck/help/pipeline EXIT=0；子命令在副本
data_root 全 EXIT=0（`subcommands-r3-run.log`）。

## r2 修订（DSH r1 changes_requested 返修后重跑——本节覆盖下方 r1 历史数字）

r1 结论：changes_requested（4 P1 / 12 P2 / 11 P3，无 P0）。r2 修复与重跑结果：

**P1 全修**：
- P1-1 感知去重死代码→框指纹改 `box_geometry_hash`（不含图 sha），跨图可达；
  新增跨图重压缩触发回归测试（`test_find_duplicates_perceptual_across_images`）
- P1-2 负样本无过滤进训练→`TrainingSetBuilder` 默认排除 `provenance.negative`
  （10 个 ogkalu 空框已排除；`exclude_negative=False` 为 T1b 显式决策通道）
- P1-3 合成全落 val→组级钉扎 `pinned={"synthetic/poc": "train"}`，24 合成全在 train
- P1-4 `occluded` 未落地→`BoxAnnotation(occluded=occlusion is not None)`，8 框 True

**P2/P3 处置**：summary KeyError 修复（P2-2）；dedup 回写透传 seed/lock（P2-3）；
force 真重划（P2-4）；fingerprint 以 dedup 后 kept 集计算（P2-5）；atomicio 主路径
缺失回退 .bak（P2-6）；README 分桶描述改排序切片（P2-7）；conf 留痕
`detection_conf_stats`（P2-9）；challenge 优先组原子性 README 明文登记（P2-10）；
test 集弱登记转 T1b（P2-11）；**AC4 毛笔字体接入 TanukiMagic（OFL）独占使用，
P2-12 闭合**；摘要去绝对路径（P2-13）；`.gitignore` 越界由 Codex 追认（P2-1）。
P3：测试计数/文件数/未用 import/loader close/孤儿 train 语义登记等已修或登记。

**r2 产物数字（`pipeline` EXIT=0，seed=20261004）**：
- 全集 82 样本 / 71 图 / 206 框；拆分：challenge 7 / **train 63（含合成 24）** / val 8 / test 4
- 训练构建器：train 57 + val 4 = 61 可读；**排除负样本 10**；状态分布 partial 8 / pseudo 29 / synthetic 24
- 合成 GT 互算 max err **1.71e-13 px**；字体 **TanukiMagic 独占**（`training_data/sfx-v1/fonts/`）
- lock fingerprint `de3787c6c34abb46…`（pinned 后新值）；manifest.full sha `2f8cdc1f…`、
  manifest.train sha `3e08c1be…`；tests **37 passed**（新增 8 回归）；selfcheck/help/
  pipeline/summary/dedup/split(force)/build-train 全 EXIT=0（`green-run-r2.log`/
  `subcommands-r2-run.log`）
- 新 fingerprint 与 pinned 语义写进 lock：`{seed, method, pinned_groups, fingerprint,
  frozen_at, challenge_case_ids}`

## r1 历史数字（被上节覆盖，留证）

### 数据产出（真实管线 `pipeline`，EXIT=0）

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

- `pytest tests/ -q`：29 passed，EXIT=0（`green-run.log`，终态复跑）
- `python -m sfx_data_infra --help` EXIT=0（`help-run.log`）；`python -m sfx_data_infra selfcheck` EXIT=0（`selfcheck-run.log`：schema 往返/枚举一致/dhash/框哈希/几何互算 5.7e-14/原子写恢复 全 OK）
- `python -m sfx_data_infra pipeline` EXIT=0（`pipeline-run.log`）
- `git check-ignore training_data/sfx-v1/manifest.full.json` → `.gitignore:13:/training_data/`
- 拆分重放：盘上 manifest 重跑 `assign_splits` fingerprint 与 lock 一致
- builder 泄漏检查：`[s for s in builder.samples if s.split not in ('train','val')]` = []

## 遗留与风险（r2 刷新）

1. **val 现为 8 样本/1-2 组**（r1 P1-3 修复后合成组移出 val）：批量数据入册后组数上升
   会自然缓解；若需样本级均衡需改分层策略（新决策，不擅动）。
2. **弱负样本使用策略**（r1 裁决②）：10 个空框负样本保留在 manifest（`negative=true`
   可追溯），builder 默认排除；是否作为训练弱负样本由 T1b 显式决策。
3. **域差距**：合成样本（毛笔体 TanukiMagic）现全部在 train 作辅助监督；域内评估不使用
   合成样本。合成分布与真实域差距仍需 T1b BJ13 真图对照目检登记。
4. **素材根硬编码**本机 worktree 路径（`importers.DEFAULT_ASSET_ROOTS`），env
   `SFX_DATA_ASSET_ROOTS` 可覆盖；跨机器复现需先配素材根（r1 P3 登记）。
5. BJ06 对账依赖 qual-BJ06.json 内嵌 sha256；素材被替换时会 fail-fast（本次一致）。
6. **test 集弱**（r1 P2-11）：4 个 ogkalu pseudo 无人工 GT，评估价值有限；人工可核验
   test 来源属 T1b。
