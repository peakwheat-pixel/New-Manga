# M2-SFX-ANNOTATE-R1（T1b 两阶段工具）

SFX 标注轮 R1：阶段一 AI 预标注 + 审核工作表导出；阶段二裁决回填 + 三集导出。
Task：`doc/tasks/M2-SFX-ANNOTATE-R1.md`；报告：`verification/M2-SFX-ANNOTATE-R1/stage1-report.md`
（阶段一）、`stage2-report.md`（阶段二）。

## 阶段二用法（stage2_finalize.py：AC3 回填 + AC4 三集导出 + AC5 合成并入）

```bash
# 1) 回填：judgments（consensus/divergence/arbiter）→ worksheet verdict+user_rationale 列
#    + judgments/user-residual.json（未判定残留清单，交用户）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step backfill

# 2) manifest：正判定样本 pseudo→complete（provenance.stage2 留 AI 判定链，human_review=false）；
#    delete 框排除留痕；correct 框 revision 链留痕；回放 5 页与其余保持 pseudo
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step manifest

# 3) 拆分：T1a assign_splits 组隔离（组不跨集 + BJ13/14/15 挑战单列 + seed=20261004 冻结）
#    + 合成 324 pinned train → final/manifest.{r1,train,val,test,challenge}.json + 指纹
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step split

# 4) YOLO seg 导出：train/val 经 TrainingSetBuilder（不可读 test/challenge），test/challenge
#    独立路径；dataset.yaml names 顺序逐字=SFX_CLASS_MAP（写后读回断言，双通道校验）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step yolo

# 5) 摘要：final/export-summary.json（数据树）+ verification/M2-SFX-ANNOTATE-R1/stage2-final-summary.json（Git 内）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step summary
```

五步可 `--step all` 依序连跑（判定输入齐备时秒级；R1 首轮 2026-10-04 实测全绿）。

## 阶段二关键口径

- 判定来源=AI 代审（编排裁定 2026-10-04）：`codex+agy-consensus`（consensus.json，397 单元，
  rationale 双方全文入列）+ `arbiter`（divergence 16 单元全量仲裁）；范围=conf>=0.5 共 413 单元；
  `human_review=false` 全量留痕，不谎称人工。残留 393 单元（conf<0.5 + ref 无 conf）→
  `judgments/user-residual.json` 交用户扩标。
- complete 语义=该样本 boxes 列表内全部为判定保留框（confirm/correct）；未判定框与 delete 框
  从正集 GT 剔除并在 `provenance.stage2.{unjudged_boxes,excluded_delete_boxes}` 全文留痕；
  correct 框坐标不动、`revision{needs_fix:true}` 留修正链。
- 回放 5 页（BJ06+J38/J41/J43/J51，合同 AC2 域内回放集）保持 pseudo 不入本轮训练集——即使其
  单元已获判定（BJ06 8 confirm 仅回填 worksheet 留痕）。
- 拆分：T1a `assign_splits` 原样复用（seed 冻结、组键=作品组、challenge 单列优先）；合成组
  `synthetic/annotate-r1` pinned train（沿 T1a cli.PINNED_GROUPS 先例），test 零合成（断言）。
- challenge/BJ 域本轮正集空集如实登记（BJ13 唯一判定=delete、BJ14/15 无判定、BJ06 属回放），
  不凑数；扩标补框后重跑 split+yolo 即自动单列。
- 生产 `SFX_CLASS_MAP`（src/infrastructure/providers/detection_sfx.py:137）只读 import，
  dataset.yaml names 写后读回断言与其逐字一致（T0 P3-6 硬约束）。


## 关键口径

- 三源：①chiqui7（DOMAIN-EXT L1 raw + 本轮新扫，sfx 类 conf@0.01）②ogkalu 43 region text 检出
  （T1a `import_ogkalu` 复用；模型无 panel 类，以实际类表为准）③BJ06 8 自证框 + l3 7 参照框。
- 跨源去重：页坐标 IoU≥0.5 合并（坐标取优先源 bj06-qual > l3-ref > chiqui7-l1 > chiqui7-scan，
  conf 取 max，sources 合并）。
- 页面选取：密度（页 sfx 合并候选数）降序，并列按 `sha256(seed:case_id)` 决胜；seed=20261004
  （沿 T1a `splits.SEED_DEFAULT`）。池小于承诺量时全选并登记缺口，不凑数。
- K 域（webtoon 690px 宽超长条）：690×1024 无缩放 tile 重叠 128（整页 letterbox 会把宽缩到
  172px 丢失细节）；`scan_mode` 字段留痕，跨域 conf 不可直接比较。
- 零检出入选页 = pseudo 空框负证据样本（T1a schema 允许），工作表呈现为「负证据页——请补画漏标」。
- 每框元信息（conf/sources/texts）挂 `provenance.boxes_meta`（与 boxes 索引对齐）——T1a
  `BoxAnnotation` 字段冻结，不扩 schema。

## 产物

数据本体：`training_data/sfx-v1/annotate-r1/`（gitignored）——`preannotate/manifest.json`、
`selection/selection.json`、`scan/density-scan.json`、`worksheet/worksheet.{json,md}`、`previews/`、
`judgments/{units,consensus,divergence,user-residual}.json + {codex,agy,arbiter}/`、
`synthetic/`（AC5 合成 324）、`final/`（AC4 三集 manifest + yolo 导出 + export-summary）。
Git 内摘要：`verification/M2-SFX-ANNOTATE-R1/stage1-manifest-summary.json`（含产物 sha256）、
`synthetic-summary.json`（AC5）、`stage2-final-summary.json`（阶段二，含产物 sha256）。

零 src 修改；生产推理序列经 `experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`
只读 import 复用。
