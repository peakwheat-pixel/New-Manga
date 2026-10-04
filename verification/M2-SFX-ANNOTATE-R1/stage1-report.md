# M2-SFX-ANNOTATE-R1 阶段一报告（AC1 预标注合并 + AC2 审核工作表）

- Owner：ZCode（本工作区）；Task：[doc/tasks/M2-SFX-ANNOTATE-R1.md](../../doc/tasks/M2-SFX-ANNOTATE-R1.md)
- 基线：release @1b765007；claim：fe62677e（stage-1）
- 状态：**AC1+AC2 完成 → WAITING_USER_LABELING 停点**（AC3-AC5 为阶段二，停点解除后实施）
- 生成：2026-10-04T07:08Z 前后（产物时间戳以文件为准）

## 1. 交付概览

| AC | 内容 | 状态 | 证据 |
|---|---|---|---|
| AC1 预标注 | 三源合并去重入 T1a schema，全标 pseudo | **PASS** | `training_data/sfx-v1/annotate-r1/preannotate/manifest.json`（72 样本 / 806 框，`SampleRecord.from_dict` 全量校验 0 错误） |
| AC2 页面选取 | 密度扫描+排序+seed 冻结+缺口登记 | **PASS**（含承诺缺口，见 §3） | `selection/selection.json`（seed=20261004） |
| AC2 审核工作表 | 每候选 20% 边距裁切预览 + 页级清单 JSON+md | **PASS** | `worksheet/worksheet.json` / `worksheet.md` / `previews/*.png`（808 张） |
| AC3-AC5 | 用户审核/三集产出/合成批量 | NOT_RUN / BLOCKED_ON_USER | 阶段二（停点解除后） |
| AC6 零 src | 零 src 修改；数据本体 gitignored；Git 只进摘要 | **PASS** | `git diff 1b765007..HEAD --stat`（见 §6） |

## 2. 执行记录（实际命令）

```text
# claim
git commit -m "claim(SFX-ANNOTATE-R1): owner claim stage-1 @1b765007"   # → fe62677e

# 密度扫描（onnxruntime CPU，119.4s）
"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step scan
# → 29 次整页推理 + 10 页 787 原生分辨率 tile（690x1024 重叠 128），EXIT=0

# 三源合并 + 页面选取 + manifest
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step assemble
# → 29 页级样本 + 43 ogkalu region 样本，EXIT=0

# 审核工作表（预览裁切 + 清单 + Git 内摘要）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step worksheet
# → 806 单元 / 808 预览 PNG，EXIT=0
```

工具链复用（零重造）：T1a `sfx_data_infra`（schema/importers/splits，含 `import_ogkalu`）、
DOMAIN-EXT `conf_scan_diag.run_inference`（生产推理序列只读 import，内部走
`src/infrastructure/providers/detection_sfx.py`——零 src 修改）。

## 3. 精确审核量（停点回报核心）

### 3.1 页面选取（seed=20261004 冻结，沿 T1a `splits.SEED_DEFAULT`）

| 域 | 承诺 | 选取 | 密度排序（合并 sfx 候选框数） |
|---|---|---|---|
| BJ（毛笔竖排） | ≥25 页 | **15 页全选**（池仅 15，缺口 10 页） | BJ06=9 > BJ13=3 > BJ14=3 > BJ15=2 > BJ01/09/11=1 > 其余 8 页=0 |
| KO（彩色艺术字） | ≥15 页 | **10 页全选**（池仅 10，缺口 5 页） | K03=231 > K10=81 > K09=74 > K08=68 > K07=66 > K06=32 > K01=21 > K02=19 > K04=11 > K05=10 |
| 域内回放 | ≥5 页 | **5 页**（BJ06 + J 系 top4） | J38=2、J43=2、J41=1、J51=1（密度并列由 sha256(seed:case_id) 决胜） |

入选页合计 **30 页**（BJ06 同时计 BJ 域与回放域）。

### 3.2 审核单元（每 AI 候选框 1 单元）

| 域 | 单元数 | 说明 |
|---|---|---|
| BJ 页级 | 20 | l1 九档 dump + 新扫 + BJ06 8 自证框 + l3 7 参照框，跨源 IoU≥0.5 合并 |
| KO 页级 | 613 | chiqui7 原生分辨率 tile 扫描（conf@0.01），K03 独占 231 |
| 域内回放（J 系） | 6 | chiqui7 整页扫描 |
| ogkalu region crop | 167 | 43 region 的 text 类检出框（源②，SFX 位置先验） |
| **合计** | **806** | — |

conf 分层（用户缩减决策数据，未擅自裁剪）：
`conf≥0.5`=413 · `0.2-0.5`=124 · `<0.2`=262 · 参照框无 conf=7。

### 3.3 预计用户审核时长（按 C1 实测速率）

依据：C1 先例 n=50 单元逐条人工审核 =「小时级人工抽检」（doc/tasks/M2-DOCTR-QUAL-C1.md:25）→ 1-2 分钟/单元。

- **全量 806 单元 ≈ 13.4-26.9 小时**（超出合同预估「1-2 小时级」一个量级——主因 chiqui7 对 KO 域彩色艺术字 conf@0.01 检出远超预期，613 框）
- 可选缩减路径（供用户裁定，阶段二入口按此调整）：
  - conf≥0.5 先审：413 单元 ≈ 6.9-13.8 小时
  - conf≥0.2 先审：537 单元 ≈ 9.0-17.9 小时
  - 仅 BJ+KO 页级（ogkalu 167 框后置）：639 单元 ≈ 10.7-21.3 小时
  - 本次框级裁切预览上下文小于 C1 region 单元，实际速率可能优于估算下限

### 3.4 MISSING 页清单（如实登记，不凑数）

- **BJ 域缺口 10 页**：cases.json BJ 组仅 15 case（BJ01-15），素材树（TA2B/E2E/DATA-INFRA 三根）无更多 BJ 页
- **KO 域缺口 5 页**：K11-K25 共 15 case 的 `local_path=韩漫_KO/02_public_ground_truth_peppercarrot/...` 在三个素材根均不存在（K01-K10 在盘，`base.png` 布局，与 T1a 解析器假定不同，已就地扩展解析）
- **J 系 manga109 37 页**（J01-J37）：磁盘无页；回放域另从 J38-J52（peppercarrot）补足
- **O 系 8 case**（O01-08，KO 域 peppercarrot）：全部缺失
- 合计 60 MISSING case，逐条登记于 `selection/selection.json` 的 `missing_pages`

## 4. 三源合并口径（AC1）

| 源 | 内容 | 坐标系 | 处理 |
|---|---|---|---|
| ① chiqui7 低 conf dump | DOMAIN-EXT L1 九档 raw（BJ06=9/BJ13=1/BJ14=0/BJ15=0 sfx 类@0.01）+ 本轮新扫（BJ 11 页 + K 10 页 + J 15 页） | 页坐标 | sfx 类框全保留；跨源 IoU≥0.5 合并（conf 取 max、sources 合并、坐标取优先源） |
| ② ogkalu text 类 | 43 region 的 text_bubble/text_free 检出 167 框（harvest 0.25） | region crop 坐标 | 复用 T1a `import_ogkalu`（pseudo）；注：ogkalu 模型无 panel 类（类表 0=bubble/1=text_bubble/2=text_free），合同"panel 类"以实际类表为准 |
| ③ 既有资产 | BJ06 8 自证框（qual run）+ l3 7 参照框（BJ13/14/15） | 页坐标 | bj06-qual 优先级最高；l3 参照框 conf=null 以 `ref` 标记 |

全部 72 样本 `annotation_status=pseudo`；`provenance.boxes_meta` 按索引携带每框 conf/sources/texts
（T1a `BoxAnnotation` 字段冻结，元信息挂样本级 provenance）。零检出入选页（BJ 8 页 + ogkalu 11
region）= pseudo 空框负证据样本（schema 允许），工作表中以「负证据页——请补画漏标」呈现。

## 5. 产物路径

数据本体（gitignored 外部树 `training_data/sfx-v1/annotate-r1/`）：

| 产物 | 路径 |
|---|---|
| 预标注 manifest（T1a schema，72 样本/806 框） | `preannotate/manifest.json` |
| 页面选取（seed 冻结 + 密度 + 缺口） | `selection/selection.json` |
| 密度扫描 raw（29 页扫描记录） | `scan/density-scan.json` |
| 审核工作表（机器可读） | `worksheet/worksheet.json` |
| 审核工作表（人类可读 md） | `worksheet/worksheet.md` |
| 裁切预览（20% 边距 + AI 框 + unit_id/conf/来源标注条） | `previews/*.png`（808 张） |

Git 内摘要：`verification/M2-SFX-ANNOTATE-R1/stage1-manifest-summary.json`
（含各产物 sha256；manifest `8f89d50d…`、worksheet.json `45dd5715…`、worksheet.md `76bb…`、selection 见文件）。

## 6. 纪律核对

- 零 src：`git diff 1b765007..HEAD --stat` 仅 `experiments/M2-SFX-ANNOTATE-R1/**`、`verification/M2-SFX-ANNOTATE-R1/**`、`doc/tasks/M2-SFX-ANNOTATE-R1.md`、`doc/handoffs/…`
- 禁改范围未触碰：tests/contracts/packaging/apps/STATUS/test_assets 既有 manifest 零变更
- 依赖零新增：scan 用既有 C4-gpu-py312 venv（onnxruntime 1.30.0 CPU），assemble/worksheet 用 dev venv（T1.1.1-impl-py312，PIL/numpy）
- `git diff --check` EXIT=0（提交前核）
- 数据本体全部在 `/training_data/`（gitignored），Git 只进摘要

## 7. 风险与遗留

1. **审核量超预估**（13.4-26.9h vs 合同预估 1-2h 级）：KO 域 conf@0.01 候选 613 框是主因。需用户在停点裁定审核范围（全量/conf≥0.5/conf≥0.2/域优先），阶段二入口按裁定调整。
2. **标注量承诺缺口**：BJ 15/25 页、KO 10/15 页——素材树无更多在盘页，缺口需素材扩充（用户动作），阶段二按现有池交付。
3. **K 页分辨率形态**：K 域为 690px 宽超长 webtoon 条，本次用 690×1024 无缩放 tile（整页 letterbox 会把宽缩到 172px 丢失细节）；与 BJ 页（2946×4167 letterbox 0.246）的推理形态不同，跨域 conf 不可直接比较——已记录于 `scan/density-scan.json` 的 `scan_mode` 字段。
4. **低 conf 噪声**：如 BJ01-B00（conf=0.06，页底 2631×128 超宽框）等长尾候选已如实保留（预标注宁多勿漏），预期用户大量 `delete` 裁决。
5. **ogkalu crop 依赖**：43 region crop 图在 `task-envs/M2-DOCTR-QUAL-work/regions/`（外部工作区），阶段二导出时依赖其在盘（import_ogkalu 已内置存在性校验）。

## 8. 停点声明

**WAITING_USER_LABELING**：阶段一（AC1+AC2）交付完成，等待用户裁定审核范围与逐条裁决（AC3）。
阶段二入口见 Handoff：[doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage1-20261004.md](../../doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage1-20261004.md)。
