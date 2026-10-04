# M2-SFX-ANNOTATE-R2 交付报告（AC1 素材补齐 + AC2-AC4 扩审/补审 + AC5 三集扩集重导出）

- Owner：ZCode（本工作区）；Task：[doc/tasks/M2-SFX-ANNOTATE-R2.md](../../doc/tasks/M2-SFX-ANNOTATE-R2.md)
- 基线：99eab8b6（R1 收口 main）；素材链 @9b9916af；三集重导出 @cb055135（本分支）
- 工具：`experiments/M2-SFX-ANNOTATE-R2/`（material_fetch_ko / material_bj_render / material_scan_density / material_finalize / build_r2_units / stage1_preannotate_bj_new / stage2_finalize_r2）
- 生成：2026-10-04；**本文档收尾轮（docs 轮）撰写**——全部统计数字由文档收尾轮从盘上产物
  内部复算（命令与输出见 §2 复算记录），不转抄交付轮消息文本。**措辞澄清（沿 R1 rev3 先例）**：
  「复算」均指同 workflow 内文档收尾 agent 的复算，属 Owner 自核、非独立第三方 Review；
  独立 Review 由 DeepSeek Harness（非作者）另行执行（status=in_review，待审）。
- 判定输入：`training_data/sfx-v1/annotate-r2/judgments/{units,consensus,divergence}.json +
  codex/agy/arbiter batch 文件`（codex+agy 双评审 + 第三方仲裁，由编排会话按用户全权授权组织；
  本 Task 代理只消费判定、不生产判定）。
- 数据树：`training_data/sfx-v1/annotate-r2/`（repo gitignored 外部树；R1 树在
  M2-SFX-ANNOTATE-R1 worktree 同理只读）。本报告内数据路径均相对 `training_data/sfx-v1/` 根。

## 0. 模式与边界（先读）

**GT 性质=ai-consensus，沿 R1 §0 口径不变**：本轮判定继续由编排组织的 codex+agy 双评审+分歧
仲裁产出（用户 2026-10-04 裁决「T1b 交给 codex 和 antigravity 同时进行审核」的既定模式），
**`human_review=false` 全量保真**，provenance 写 `provenance.stage2r2`（不覆盖 R1 的
`provenance.stage2` 判定链），**不谎称人工**。R1 的一致性上限警示（ai-consensus 不等于人工
正确率，DSH r1 C5）对 R2 新增 11 个 confirm 框同样适用：T3 Gate 归因时「标注质量」与「模型
质量」两层误差仍须分开，用户抽检/翻案通道仍是唯一升级为人工背书的路径。

**本轮判定范围（19 单元）**：`judgments/units.json` counts=`{bj_lowconf: 0, replay: 6, bj_new: 13}`。
AC2 BJ conf 0.2-0.5 扩审部分为**空集**（R1 残留 BJ 域 11 单元全部落在 ref_no_conf 7 +
conf_lt_0.2 4，无一落在 [0.2,0.5)，§4.1 复算）——本轮如实登记空集，未凑数。

**覆盖完备性**：consensus(18) ∪ divergence(1) = units(19)，uncovered=0（§4.2 复算）；
分歧 1 单元经 arbiter 裁决，残留=0。

## 1. 交付概览

| AC | 内容 | 状态 | 证据 |
|---|---|---|---|
| AC1 素材补齐 | KO+5 页落位（K13/K15/K18/K19/K24）；BJ+10 页下载渲染入池并新增 cases.json 登记（BJ16-BJ25）；`resolve_asset_roots()` 全量对账 BJ 25/25 可解析 | **PASS** | `test_assets/comic_golden_suite/manifests/cases.json`（110 条，+750/−0）；`selection/material-selection.json`；`scan/density-scan-material.json`（§3） |
| AC2 BJ 低置信扩审 | R1 残留 BJ 域 conf∈[0.2,0.5) 层双 AI 交叉审核 | **N/A（空集如实登记）** | `judgments/units.json` counts.bj_lowconf=0；R1 残留分层复算（§4.1） |
| AC3 回放 5 页补审 | BJ06+J38/J41/J43/J51 共 6 单元补审（R1 C4 偏差闭合：按判定如实处理） | **PASS（6 单元全 delete，回放页保持 pseudo 不入训练集）** | `judgments/consensus.json` R1-BJ06-B08 等 6 单元；`preannotate/manifest.r2.json` stage2r2 留痕（§4.3） |
| AC4 BJ 新页预标注+扩审 | BJ16-25 三源合并预标注 29 候选 → conf≥0.2 13 单元双 AI 审核 | **PASS** | `worksheet/worksheet-bj-new.json`（29 行）；`judgments/*`（§4） |
| AC5 三集扩集重导出 | R2 判定并入 + split/yolo/summary 重跑；BJ 正集 ≥1 页 + §8.1 对照回填 | **PASS WITH DEVIATION（challenge 仍空集，如实登记交编排裁决）** | `final/manifest.*.json` 五件；指纹 `564498e1…ccfa`（§5） |
| AC6 零 src | 零 src 修改；数据本体 gitignored；Git 只进摘要与 cases.json 新增 | **PASS（附遗留：2 个 AC4 工具脚本未跟踪，§8）** | `git status`（§2 复算记录） |

## 2. 执行记录

> DSH r1 P3-5：本目录曾存在 `stage-r2-final-summary.json.bak`（atomicio 有意恢复位），已随返修删除；现 summary 为注记更正后重跑产物（指纹与三集数字不变）。

### 2.1 交付轮命令（Owner，产物在盘 + `stage-r2-final-summary.json` generated_at=2026-10-04T13:17:15Z）

```text
python experiments/M2-SFX-ANNOTATE-R2/material_fetch_ko.py      # K11-K25 15 页直下（peppercarrot CC-BY-4.0）
python experiments/M2-SFX-ANNOTATE-R2/material_bj_render.py     # vol01/03/05 PDF → 54 候选页 PNG（DPI 150）
python experiments/M2-SFX-ANNOTATE-R2/material_scan_density.py  # chiqui7 密度扫描 54+15=69 页
python experiments/M2-SFX-ANNOTATE-R2/material_finalize.py      # top-10/top-5 选取 → cases.json BJ16-25 + material-selection.json
python experiments/M2-SFX-ANNOTATE-R2/build_r2_units.py         # R2 判定单元（回放 6+BJ 新页 conf≥0.2 13）
python experiments/M2-SFX-ANNOTATE-R2/stage1_preannotate_bj_new.py  # BJ16-25 三源合并预标注 → worksheet-bj-new
python experiments/M2-SFX-ANNOTATE-R2/stage2_finalize_r2.py --step manifest
python experiments/M2-SFX-ANNOTATE-R2/stage2_finalize_r2.py --step split
python experiments/M2-SFX-ANNOTATE-R2/stage2_finalize_r2.py --step yolo
python experiments/M2-SFX-ANNOTATE-R2/stage2_finalize_r2.py --step summary
```

`--step` 四步产物与摘要数字的对应关系已由下方 2.2 的盘上复算逐项核对（82/351/345/4/2/0、
指纹、names、labels 行数等全部以重读盘上文件为准，非读缓存）。

### 2.2 文档收尾轮复算记录（本轮实际执行，全部 PASS 除非另注）

```text
# AC1 cases.json 结构与既有条目保真
python json.load cases.json → 110 条合法（BJ 25 + KO 25 + 其他 60）
git diff --numstat 9b9916af~1 9b9916af -- cases.json → 750 insertions / 0 deletions
既有 100 条深度对比（git show 9b9916af~1 取旧版逐条 == 新版前 100 条）→ True；追加 BJ16-BJ25 → True

# AC1 落位文件 PIL/sha256 逐页复核
KO 5 页（material-selection.json ko_selected）→ pixel_size 逐页一致 + sha256 5/5 一致
BJ16-25 页图（cases.json page_sha256）→ PIL 尺寸 10/10 一致 + sha256 10/10 一致（2946×4167 @150 DPI）

# AC1 完整性命令
python test_assets/comic_golden_suite/tools/fetch_bj.py verify
  → BJ16-25 10/10 VERIFY_OK；BJ01-15 VERIFY_FAILED missing=预期（像素在 TA2B/E2E 跨根素材树）
resolve_asset_roots(extra=[R2 suite 根])（importers.py:71，R2 worktree 不在 DEFAULT_ASSET_ROOTS）
  → BJ 25/25 可解析（跨根：R2+DATA-INFRA+E2E-MATERIAL+TA2B）
R1 manifest 引用路径 K01-10 → 10/10 在盘且 sha256 与 manifest.image.sha256 一致
TA2B bj_download_manifest.json vol01/03/05 PDF sha256 → 3/3 MATCH（jasrac_volume=false）

# 判定统计复算（judgments/{codex,agy,arbiter}/batch-*.json + units/consensus/divergence）
codex 19 单元 → confirm 11 / correct 0 / delete 8
agy   19 单元 → confirm 12 / correct 0 / delete 7
consensus 18（confirm 11 / delete 7）；divergence 1；arbiter 1（delete）
consensus_ids ∪ divergence_ids == unit_ids → uncovered=0；arbiter id 集==divergence id 集
R1 残留 BJ 11 单元分层（R1 user-residual.json）→ ref_no_conf 7 + conf_lt_0.2 4；conf∈[0.2,0.5)=0

# AC5 manifest/split 复算
preannotate/manifest.r2.json → 82 样本（R1 底册 72 + BJ 新页 10）；stage2r2 actions
  {—:67, kept_pseudo_replay_page_delete_excluded:5, completed:5, kept_pseudo_no_judged_units_this_round:4, kept_pseudo_zero_box_negative_evidence:1}
R1 底册对比（R1 worktree preannotate/manifest.json 72 样本 450 框）→ 前 72 id 全对齐；
  除 5 个回放页外其余 67 条逐字节一致=0 差异（只读并入）；R1 worktree git status 干净
回放排除复算 → 5 页共 6 框移出框列表（1+1+1+2+1），action=kept_pseudo_replay_page_delete_excluded
final/manifest.{r2,train,val,test,challenge}.json → 351=27 real complete+324 synth；
  train 345/571（21 real+324 synth）、val 4/53、test 2/5、challenge 0/0
fingerprint → manifest.r2 lock.fingerprint 与四分集顶层 fingerprint 同值
  564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa
组隔离 → train 10 组 + val 2 + test 2 = 14 组，跨集违例=0；合成 0 入 val/test
BJ 正集 → densho810 组样本 5 页 11 框全部在 train（§5.2 逐页清单）

# AC5 YOLO 复算（重读盘上文件）
labels train 571 / val 53 / test 5 行 == manifest 框数；cls 全部=='2'（629 行 0 异常）；
  坐标 ∈[0,1] 0 越界；多边形点数<4 为 0；images/labels stem 失配 0；challenge 目录未导出
pyyaml 6.0.3 safe_load dataset.yaml → names {0:bubble,1:panel,2:sfx,3:text} 键序 0,1,2,3；
  challenge 键不写入（keys=names/path/train/val/test）

# AC5 T1a schema 全量校验
SampleRecord.from_dict+validate（experiments/M2-SFX-DATA-INFRA/sfx_data_infra/schema.py）
  → preannotate/manifest.r2 82 + final 五 manifest 351/345/4/2/0 + manifest-bj-new 10
  = 794 样本逐条，errors=0；boxes/boxes_meta 索引对齐 0 异常
```

## 3. AC1 素材结果

### 3.1 KO +5 页（peppercarrot 韩文版，CC-BY-4.0 直下）

- cases.json 既有登记 **K11-K25 共 15 条候选**（无新增登记），`material_fetch_ko.py`
  直接下载 sources 页页图：**15/15 全部落盘**（`training_data/sfx-v1/annotate-r2/ko-candidates/`
  15 个 PNG 在盘，本轮复算确认）。
- chiqui7 tile 扫描（全宽 1024 高 tile、重叠 128，R1 K 域同口径）排序后 **top-5 落位**素材根
  `test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/`：
  **ep04/E04P07+E04P08+E04P01 与 ep20/E20P06+E20P01（=K13/K18/K15/K24/K19，
  ep04×3+ep20×2 两集互补）**。密度排序：K13 E04P07(5)/K18 E04P08(3)/K24 E20P06(3)/
  K15 E04P01(2)/K19 E20P01(1)（K18/K24 同密度 3 由 sha256(seed:source_id) 升序决胜）。
- 落位验证（本轮复算）：5 页 PIL 尺寸与 `material-selection.json` pixel_size 逐页一致
  （1200×1660 / 1200×1165），sha256 5/5 一致。
- **K11-15 等其余 10 张候选未入本轮落位**，留 `ko-candidates/` 作扩标池（§3.4）。

### 3.2 BJ +10 页（densho810 官方免费卷，零新增网络下载）

- **PDF 复用**：M2-TA2B-OPEN-ASSETS worktree 已下载卷 **vol01/03/05**（`material_bj_render.py:15`
  PDF_ROOT 直指该 worktree）；本轮复算三卷 PDF sha256 与 `bj_download_manifest.json` files[]
  登记**逐卷 MATCH**（vol01 `a2ad133d…ca8b4`/209 页、vol03 `31c37c85…`/221 页、
  vol05 `62e8f0ab…`/243 页，jasrac_volume 均=false）。**JASRAC 卷 2/7/11 未触碰**。
- `fetch_bj.py render` 子命令只支持每卷 4 页固定采样（首/1/4/中/末，`sample_page_indices`
  不可指定页），故自写 **`material_bj_render.py`**：pypdfium2 同款 **DPI 150** 均匀采样渲染，
  **避开 BJ01-15 已用 source_id**（USED_PAGES 15 页，`material_bj_render.py:30-34`）→
  **54 张均匀候选页**（vol01 18 + vol03 18 + vol05 18，`bj-candidates/render-plan.json`
  在盘可复核，本轮复算三卷 pages 目录 18/18/18）。
- **chiqui7 整页 letterbox 扫描**：引擎只读复用 R1 `conf_scan_diag` 入口（内部复用生产
  `src/infrastructure/providers/detection_sfx` 序列，`material_scan_density.py:5-8`），权重
  `M2-SFX-DETECT/weights/yolo11s-seg.onnx`（scan 产物 weights 字段一致），运行环境
  M2-DOCTR-QUAL-C4-gpu-py312（onnxruntime）。候选池 69 页（54 BJ 整页 letterbox + 15 KO tile），
  证据落 `scan/density-scan-material.json`（本轮复算 pages=69 与池一致）。
- **密度排序 top-10**（去重 sfx 框数降序，sha256(seed:source_id)=20261004 决胜沿 R1 口径，
  `selection/material-selection.json` rule 字段）：**vol01_p0045(7) / vol05_p0167(5) /
  vol05_p0065(4) / vol05_p0116(3) / vol05_p0052(2) / vol03_p0059(2) / vol01_p0067(2) /
  vol03_p0047(2) / vol03_p0186(1) / vol05_p0077(1)**（其中密度 2 的四页、密度 1 的两页
  均由 sha256 决胜定序）→ 登记为 **cases.json BJ16-BJ25**。

### 3.3 BJ16-BJ25 登记口径（BJ13 字段同构 + `pixel_size`）

> DSH r1 P3-4：BJ16-25 比 BJ13 多一个 `pixel_size` 字段（渲染 DPI 元数据）；无 cases.json 专用 schema，消费方 fetch_bj.py verify 10/10 VERIFY_OK 实证容忍额外字段。

本轮复算逐条核对 BJ16 条目与 BJ13 字段：`text_type=sfx_dominant_unverified`、
`orientation=vertical`、`difficulty=unassessed`、`tags` 4 项同构
（fragmented_sfx/huge_text/vertical_text/complex_background）、`pipeline_status` 十段
**如实全 NOT_RUN**、`page_sha256` 逐页登记、`render_dpi=150`、`pixel_size=[2946,4167]`、
许可字段沿 densho810 报告义务语境（报告窗口至 2026-11-02，registration_note 留痕）。
cases.json 110 条 json.load 合法；**既有 100 条深度对比 byte-identical**（本轮复算
旧版 git show 逐条 == 新版前 100 条）；`git diff --numstat`=**750 insertions / 0 deletions**。
素材 commit=**9b9916af**（cases.json 新增 + material 四脚本；页图 gitignored 未入库）。

### 3.4 AC1 验证全绿汇总（全部为本轮复算执行）

| 检查 | 命令（§2.2） | 结果 |
|---|---|---|
| cases.json 110 条合法 | `python -c json.load` | PASS |
| 既有 100 条 byte-identical | `git show 9b9916af~1` 逐条对比 | PASS（追加 BJ16-BJ25，+750/−0） |
| BJ16-25 页图完整性 | `fetch_bj.py verify` | **10/10 VERIFY_OK**（BJ01-15 missing=预期，像素在 TA2B/E2E 跨根素材树） |
| BJ 25/25 可解析 | `resolve_asset_roots()`+R2 素材根 extra | PASS（R2 worktree 不在 importers.DEFAULT_ASSET_ROOTS，本轮对账即用 env/extra 方式验证；后续 AC2-AC5 对账同法） |
| KO 在册 15 页 | R1 manifest 引用路径 K01-10 10/10 在盘 sha 一致 + K13/15/18/19/24 cases.json 5/5 可解析 | PASS（以 `selection/material-selection.json` ko_selected 为准） |
| KO 5 页 PIL | pixel/sha256 逐页 | PASS 5/5 |
| BJ16-25 PIL | pixel/sha256/page_sha256 逐页 | PASS 10/10 |
| PDF 来源保真 | TA2B manifest sha256 三卷 | PASS 3/3 MATCH |
| 下载 fallback 纪律 | — | N/A（densho810 经既有 PDF 复用+peppercarrot 直下，无失败场景） |

**扩标池**：未入池 **44 张 BJ 候选**（54−10：vol01 16 + vol03 15 + vol05 13）+ **10 张 KO
候选**（15−5）留 `training_data/sfx-v1/annotate-r2/`（bj-candidates 渲染页 + ko-candidates/）
作扩标池；扫描/选取证据 `scan/density-scan-material.json` + `selection/material-selection.json`
同落该 gitignored 树（本轮复算 54−10=44、15−5=10 与在盘文件数一致）。

## 4. AC2/AC3/AC4 双审统计（共识/仲裁/残留）

### 4.1 AC2 BJ 低置信层=空集（如实登记，不凑数）

R1 残留 393 单元中 BJ 域 11 单元（本轮复算自 R1 `judgments/user-residual.json`）：
BJ01×1 / BJ06×1 / BJ09×1 / BJ11×1 / BJ13×2 / BJ14×3 / BJ15×2，分层 **ref_no_conf 7
（l3 参照框）+ conf_lt_0.2 4**，**conf∈[0.2,0.5) = 0**——与 `judgments/units.json`
notes.bj_lowconf 登记一致。AC2 无判定输入，未产生新正样本；该 11 单元仍在 R1
user-residual.json 交用户通道，不在本轮范围。

### 4.2 双审各自 verdict 分布（本轮复算：逐批重算 codex/agy/arbiter batch 文件）

| 评审 | 单元数 | confirm | correct | delete |
|---|---|---|---|---|
| codex | 19 | 11 | 0 | 8 |
| agy | 19 | 12 | 0 | 7 |

- **共识（reviewer=codex+agy-consensus）**：18 单元（同判 confirm 11 / 同判 delete 7；
  无 correct 对）；user_rationale 保留双方 rationale 全文（`judgments/consensus.json`）。
- **分歧**：1 单元（`R2-BJ17-B02`，codex=delete vs agy=confirm，`judgments/divergence.json`）。
- **仲裁（reviewer=arbiter）**：1 单元 = 分歧全量，终判 **delete**（`judgments/arbiter/batch-0.json`，
  仲裁 rationale 原文在案：闭合椭圆气泡内三行规整普通手写假名，无毛笔/艺术化特征，归气泡
  对白而非 SFX，采 codex 判）。
- **覆盖完备性**：consensus ∪ divergence = 19 单元，**uncovered=0**；arbiter id 集==
  divergence id 集；**留用户=0**。
- **最终 verdict 分布**：**confirm 11 / delete 8**（=19）。

### 4.3 AC3 回放 5 页补审（R1 C4 偏差按判定闭合）

回放 6 单元（R1-BJ06-B08 + J38/J41/J43/J51 共 5 页）本轮双审**全部判 delete**（共识 6/6）。
处置沿 R1 合同口径：回放页保持 pseudo 不入训练集，6 个 delete 框**从框列表排除**并在
`provenance.stage2r2` 留痕（action=kept_pseudo_replay_page_delete_excluded；本轮复算
5 页移出框数 1+1+1+2+1=6，R1 stage2 链原样保留）。R1 §8.1 的「回放偏差」至此以
**如实判定**方式闭合：回放页经补审确认为无可保留 SFX 正例（判定即证据），而非未审跳过。

### 4.4 AC4 BJ 新页判定（BJ16-25）

三源合并预标注 29 候选（`worksheet/worksheet-bj-new.json` 29 行，本轮复算按 case 分布
BJ16×7/BJ17×5/BJ18×4/BJ19×3/BJ20×2/BJ21×2/BJ22×2/BJ23×2/BJ24×1/BJ25×1）。取
**conf≥0.2 共 13 单元**入本轮判定（复算 ai_conf≥0.2=13 / <0.2=16）：BJ16×3/BJ17×3/
BJ18×3/BJ23×2/BJ24×1/BJ25×1。终判：**BJ16/17/18/23/24 的 11 框 confirm**（→ 页级样本
complete 入正集）、**BJ25 唯一单元 delete**（→ 零框负证据 pseudo）；**BJ19/20/21/22 全部
候选 conf<0.2 无判定单元保持 pseudo**（§4.2 复算 conf<0.2 by case：BJ19×3/BJ20×2/
BJ21×2/BJ22×2，与 summary 登记一致）。16 个 conf<0.2 候选留 worksheet-bj-new.json
作后续扩标输入（verdict 列回填不在本轮 ask 范围，判定留痕以 judgments/* 与
manifest.r2.json stage2r2 为准）。

## 5. AC5 三集与验证

### 5.1 判定并入（preannotate/manifest.r2.json，82 样本）

- **R1 底册 72 样本 450 框只读并入**（本轮实读 R1 worktree
  `annotate-r1/preannotate/manifest.json`=72 样本 450 框；R1 阶段一「806」为工作表单元数，
  与 manifest 框数不同构，按实读执行并登记于摘要）。前 72 条 id 全对齐；除 5 个回放页外
  其余 **67 条逐字节一致**（只读并入证明）；R1 worktree `git status` 干净（只读未动）。
- 回放 5 页的 **6 个 R2 delete 单元排除出框列表**+`provenance.stage2r2` 留痕，R1 stage2 链保留。
- **BJ16-25 新页 10 样本 29 框**并入（`preannotate/manifest-bj-new.json` 10 样本 29 框）。
- stage2r2 action 分布（本轮复算）：`—`67 / completed 5 / kept_pseudo_replay_page_delete_excluded 5 /
  kept_pseudo_no_judged_units_this_round 4（BJ19-22）/ kept_pseudo_zero_box_negative_evidence 1（BJ25）。
- **T1a schema 全量校验 0 错误**（本轮复算 SampleRecord.validate 逐样本 794 条+
  boxes/boxes_meta 索引对齐）。

### 5.2 三集数字（seed=20261004 冻结沿 R1，group-hash-rank-v2）

> **DSH r1 P2-2 补充登记**：真实样本 split 漂移是**组级成员迁移**而非仅计数——`vasyanator2/717481`（K09，25 框）train→val、`vasyanator2/651664`（K02，3 框）val→test；清单见 `final/export-summary.json` 的 `group_split_migration_vs_r1`。**R1↔R2 分集指标不可直比**：跨轮对比须固定切分或限定 R1∩R2 交集样本，否则只能作同口径重新基线、不得宣称改进。

| split | 样本 | 框 | 真实/合成 | 作品组 |
|---|---|---|---|---|
| train | 345 | 571 | **21 真实（含 BJ 正集 5 页 11 框）**+ 324 合成 | synthetic/annotate-r1（pinned）+ densho810/vol01·vol03·vol05 + vasyanator2×6 |
| val | 4 | 53 | 4 真实 | vasyanator2/701535 + 717481 |
| test | 2 | 5 | 2 真实 | vasyanator2/651664(K02 页 3 框) + 724815(K01 页 2 框) |
| challenge | 0 | 0 | — | **空集，如实登记（§5.4）** |

- **五 manifest 指纹一致**：`564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa`
  （manifest.r2 `lock.fingerprint` 与四分集顶层 `fingerprint` 同值；本轮复算）。
  R1 指纹为 `f9ea1c80…9271`（R2 重切后变更，见 r1_baseline_for_diff 登记）。
- **组隔离**：14 组（train 10+val 2+test 2）跨集违例=0；**合成 0 入 test**（val/test 亦 0 合成）。
- **BJ 正集=5 页 11 框（R1 时为 0），全部入 train**：pre-bj16×3 框（densho810/vol01）/
  pre-bj17×2、pre-bj18×3（vol05）/ pre-bj23×2、pre-bj24×1（vol03）——vol01 1 页+vol03 2 页+
  vol05 2 页；本轮复算 train densho810 组逐页框数与 kept_units 清单一致。
- **真实样本 split 相对 R1 漂移（如实登记）**：R1 real train 18/val 3/test 1 → R2 **21/4/2**。
  原因=真实组池 10→13 组（新增 densho810/vol01、vol03、vol05）后同算法（group-hash-rank-v2）
  同 seed 重切边界所致；组不跨集仍 0 违例。漂移已登记于摘要 `r1_baseline_for_diff`
  （R1 三集数字逐项在案：train 342/585、val 3/31、test 1/2、challenge 0/0）。

### 5.3 YOLO seg 导出与 names 硬约束校验

- `final/yolo/dataset.yaml` names 双通道校验**双 PASS**（本轮复算通道 2 + 交付轮通道 1）：
  - 通道 1=脚本写后读回断言（`stage2_finalize_r2.py:531`，R1 同款手写解析器；names 顺序
    逐字={0:bubble,1:panel,2:sfx,3:text} 且键序=sorted(SFX_CLASS_MAP)）；
  - 通道 2=**pyyaml 6.0.3 独立解析复核**（本轮复算 safe_load 全文件：names 字典与键序逐字
    相等；keys=names/path/train/val/test，challenge 键不写入）——两通道解析器实现独立。
- labels 硬校验（本轮复算，独立重读盘上文件）：**cls 恒『2』0 异常（629 行）、坐标∈[0,1]
  0 越界、多边形点数<4 为 0、行数=manifest 框数（train 571/val 53/test 5）、images/labels
  stem 失配 0**；challenge 空集未导出目录。
- 构建路径：train/val 经 **TrainingSetBuilder**（`stage2_finalize_r2.py:582`，
  allowed_splits=("train","val")，T1a 设计：builder 不可读 test/challenge），**test 2 图独立
  路径导出**（`stage2_finalize_r2.py:592`）；builder **excluded_negative=[]**（复算输出
  `[yolo] builder excluded_negative=[]`）。
- 产物：`training_data/sfx-v1/annotate-r2/final/{manifest.r2,manifest.train,manifest.val,
  manifest.test,manifest.challenge}.json + yolo/`（gitignored 数据树）；Git 只进
  `stage-r2-final-summary.json`（artifacts_sha256 逐件登记，含五 manifest+dataset.yaml+
  _export_stats.json）。

### 5.4 challenge 仍空集（AC5 验收判据允许分支：如实登记+交编排裁决）

- 本轮判定范围（units.json 19 单元）**不含 BJ13/14/15 任何单元**（本轮复算 case_id 分布
  证实：0 单元）；BJ13 唯一 conf≥0.5 判定仍为 R1 的 delete（R1 判定 BJ 域单元复算：
  BJ06 8 confirm+BJ13 1 delete），**未翻案**。
- AC2 BJ 低置信层 conf∈[0.2,0.5) 为空集（§4.1），无潜在翻案输入。
- 按 Task AC5 验收判据「challenge 非空（**或 BJ13 判定仍=delete 时如实登记并交编排裁决**）」
  走分支：`manifest.r2.json lock.challenge_note` 与 `manifest.challenge.json` note 均已
  登记（本轮复算两处原文在盘），**交编排/用户裁决**。BJ13/14/15 页级样本保持 pseudo
  留待扩标；挑战集正框补齐后重跑 split+yolo 即自动单列。

## 6. GT 性质（沿 R1 §0 口径）

本轮 GT=**ai-consensus**（human_review=false 保真）：5 个新 complete 样本
`provenance.stage2r2` 逐样本留痕 `mode=ai-review-backfill`、`human_review=false`、
判定链（consensus/arbiter rationales 全文在 judgments/consensus.json 与
arbiter/batch-0.json）。R1 22 个 complete 样本的 `provenance.stage2` 判定链未动。
**本 GT 不声称人工标注质量等级**；用户抽检/翻案通道（R1 user-residual.json）仍开放。

## 7. A′ 采纳输入条件复核表（对照 R1 stage2-report.md §8.1 五行，交编排/用户——T2 释放判定依据）

> **DSH r1 P2-3/P2-4 补充登记（T2/Gate 前必读）**：① **BJ 正样本 100% 在 train**——val/test 全为 KO 样本，BJ 域当前无任何 held-out 参照；BJ 域指标**禁止在 train 上做门判定**，G1 BJ 门在 challenge 补齐或另设 BJ 留出前不可达。② **框粒度口径=一检测框一框**（chiqui7 检测单元）；编排对照原页复核（2026-10-04）：`BJ17-B00/B01` 为**同字形列双框**（预览同形、坐标相邻 x 差 43px 纵列摇摆），按实例合并计 BJ17=1；`BJ18-B00/B01` 与 `BJ23-B00/B01` 为**独立实例**（页内两处、气泡与背景处理不同，原页裁切对照 `_p2_4_bj18_b00/b01.png` 留 previews/）。按实例口径 BJ 正集=**约 10 实例 11 框**；seg GT 两框坐标不相交、mask 无冲突，训练可直接消费。

对照 `verification/M2-SFX-ANNOTATE-R1/stage2-report.md:177`（§8.1）与
`verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md:61` 输入条件，R2 交付后状态
（全部数字本轮从盘上复算）：

| A′ 输入条件 | 承诺 | R1 时点 | **R2 现状（复算）** | 状态 |
|---|---|---|---|---|
| BJ 域真实页标注 | ≥25 页 | 15 页（素材仅 BJ01-15 在盘） | **在册 25/25**（BJ16-25 新增入池+落位；`resolve_asset_roots` 全量可解析 25/25）。页数口径**满足**。判定覆盖如实细分：17 页有预标注候选单元（R1 7 页+R2 10 页），8 页经判定（R1 BJ06/BJ13+R2 六新页），其余页为预标注零检出负证据或候选留池 | **满足（页数口径）** |
| KO 域真实页标注 | ≥15 页 | 10 页（K11-25 路径缺失） | **在册 15/15**（K01-10 按 R1 manifest 引用路径在盘 10/10 sha 一致 + K13/15/18/19/24 落位 5/5）。页数口径**满足**。判定覆盖仍 10 页（K01-10）；KO 新 5 页素材在册未标注（本轮判定范围不含 KO 新页，如实登记） | **满足（页数口径）** |
| BJ 域正集样本 | 主攻形态覆盖 | **0（最关键缺口）** | **5 页 11 框**（pre-bj16×3/pre-bj17×2/pre-bj18×3/pre-bj23×2/pre-bj24×1；densho810/vol01(1)+vol03(2)+vol05(2)，5 页全部入 train）。判定链 codex+agy 共识（R2-BJ17-B02 分歧经 arbiter 裁 delete 已排除），rationale 主体为竖排/斜排毛笔假名——**A′ 主攻毛笔竖排形态获首批真实正样本；量级仍小（11 框），如实登记** | **满足（首批，量级小）** |
| challenge 集（BJ13/14/15） | 有正样本可评 | 空集 | **仍空集**：本轮判定范围不含 BJ13/14/15 任何单元；BJ13 唯一 conf≥0.5 判定仍=R1 的 delete 未翻案；AC2 低置信层空集无翻案输入。按 AC5 验收判据允许分支：如实登记（lock.challenge_note+challenge.json note）+**交编排裁决** | **未满足（交编排裁决）** |
| 合成样本 | ≥200 | 324 | **324**（R1 渲染产物只读并入，pinned train，test 零合成本轮复算 in_test=0） | 满足 |

**对 T2 训练的含义（如实呈现，不粉饰）**：A′ 最关键缺口（BJ 正集=0）已闭合——现有训练集
含 BJ 毛笔竖排真实正样本 11 框，主攻形态不再零覆盖；但 (a) 正集量级小（5 页 11 框 vs
KO 域 22 complete 样本/342 框），BJ 域深度仍由 324 合成承担（横排系统字体/限定毛笔字体，
与真竖排毛笔形态覆盖度未经验证——R1 §8.1 警示继续适用）；(b) challenge（BJ13/14/15）仍
无可评正样本，G1 BJ 门若含 challenge 条款则仍不可达。**是否释放 T2 由编排/用户按上表裁决**；
如实登记不构成释放建议。

## 8. 已知边界与后续（诚实登记）

1. **challenge 空集交裁决**（§5.4）：BJ13 delete 未翻案、AC2 层空集——翻案只能来自用户
   抽检通道或新页正集；不凑数。
2. **AC2 空集**：R1 残留 BJ 域无一落在 conf 0.2-0.5（§4.1），本轮该 AC 无输入；11 个 R1
   残留 BJ 单元仍走 user-residual 用户通道。
3. **KO 新 5 页在册未标注**：本轮判定范围不含 KO 新页（判定 13 单元全部为 BJ 域+回放）；
   K11-15 素材与 10 张 KO 候选留扩标池。KO 域判定覆盖仍 10 页（K01-10）。
4. **BJ 域判定覆盖仍部分**：25 在册页中 8 页经判定；BJ19/20/21/22 全候选 conf<0.2 保持
   pseudo；16 个 conf<0.2 候选留 worksheet-bj-new.json（verdict 列回填不在本轮 ask 范围）。
5. **真实 split 漂移**（§5.2）：R1→R2 真实样本三集分布 18/3/1→21/4/2，组池 10→13 组同算法
   同 seed 重切所致；对比基线已登记 `r1_baseline_for_diff`。
6. **2 个 AC4 工具脚本未跟踪**：`experiments/M2-SFX-ANNOTATE-R2/build_r2_units.py` 与
   `stage1_preannotate_bj_new.py` 在本轮 docs 提交时点仍为 untracked（git status 复算）；
   9b9916af 只进了 material 四脚本、cb055135 只进了 stage2_finalize_r2.py。建议集成轮
   补录（属 experiments 树允许修改范围），避免 AC4 判定单元构建/预标注过程不可复现。
7. **数据树跨 worktree 依赖**：R2 判定输入的 previews 引用 R1 worktree 绝对路径
   （units.json notes 已登记）；BJ01-15 像素在 TA2B/E2E 素材树（fetch_bj verify 的 15 个
   missing=预期）。R2 worktree 不在 `importers.DEFAULT_ASSET_ROOTS`（importers.py:25），
   后续 AC2-AC5 对账需以 `SFX_DATA_ASSET_ROOTS` 环境变量或 `extra` 参指向 R2 suite 根
   （本轮对账即用该方式验证）。
8. **GT 性质上限**（§6）：ai-consensus 非人工背书；A′ 正集 11 框的 rationale 主体为毛笔
   竖排/斜排假名与艺术化字形，标注质量误差在 T3 Gate 归因时与模型质量分开。
9. **扩标池待用**：44 BJ + 10 KO 候选页与 16 个 BJ 低置信候选（§4.4）留
   `training_data/sfx-v1/annotate-r2/`，后续扩标轮无需重新下载/渲染/扫描。
