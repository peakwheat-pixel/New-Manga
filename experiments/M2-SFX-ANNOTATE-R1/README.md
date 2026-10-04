# M2-SFX-ANNOTATE-R1（T1b 阶段一工具）

SFX 标注轮 R1 阶段一：AI 预标注 + 用户审核工作表导出。Task：`doc/tasks/M2-SFX-ANNOTATE-R1.md`；
报告：`verification/M2-SFX-ANNOTATE-R1/stage1-report.md`。

## 用法

```bash
# 1) 密度扫描（需 onnxruntime venv；BJ06/13/14/15 复用 DOMAIN-EXT L1 raw 不重扫）
"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step scan

# 2) 三源合并 + 页面选取（seed 冻结）+ T1a schema manifest（dev venv）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step assemble

# 3) 审核工作表（预览裁切 + JSON/md 清单 + Git 内摘要）
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step worksheet
```

三步可 `--step all` 连跑（scan 步仍需 onnxruntime venv；实测全量 119.4s + assemble/worksheet 秒级）。

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
`selection/selection.json`、`scan/density-scan.json`、`worksheet/worksheet.{json,md}`、`previews/`。
Git 内摘要：`verification/M2-SFX-ANNOTATE-R1/stage1-manifest-summary.json`（含产物 sha256）。

零 src 修改；生产推理序列经 `experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`
只读 import 复用。
