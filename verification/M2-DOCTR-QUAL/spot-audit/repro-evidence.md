# M2-DOCTR-QUAL-C1 阶段一：R7 复现证据归档（AC4）

Task：[M2-DOCTR-QUAL-C1](../../../doc/tasks/M2-DOCTR-QUAL-C1.md) · 交付分支 `agent/zcode/M2-DOCTR-QUAL-C1`（delivery base=`0d4d07a9`）· 日期 2026-09-30。
本文件闭合 DSH r1 R7（committed 复现证据文件 + raw 日志归档）与 C4 报告 §7.4 的披露项。

## 1. C4 三个正式 results JSON（分母来源，零改动）

| 文件（`verification/M2-DOCTR-QUAL/qualification/`） | SHA-256 |
|---|---|
| `results-formal-manga_rt_detr_v2-cuda-seg05.json` | `745b0f93a43f7936de3ca6391113a13b87a237c5b678ac20bdb41d0b65537409` |
| `results-formal-manga_rt_detr_v2-cuda-seg05-padoffset.json` | `7e0aeb65335198c11570dd849f55bc659ddc65193d8057f865c1f06b79c83210` |
| `results-formal-manga_rt_detr_v2-cuda-seg05-conf03.json` | `0f529a85e848a40349c42bc96945bb5d72a5ac61f43586bbf032b1c14f4bcd01` |

本 Task 全程未写入上述文件（自检见 §6；专项 diff 为空）。
manifest SHA-256 = `4f16425a8ba72435…`（正式 JSON 内登记与本 Task 重跑实测一致）；权重 SHA-256 = `037930a861e67870…`（C4 pin）。

## 2. C4 集成期两次复跑 0 diff（引用既有集成记录）

来源：[integration-record-c4/integration.md](../qualification/integration-record-c4/integration.md)（原文不改写，此处仅摘引）：

- **集成方核验（merge 前）**：全量 seg05 正式口径 EXIT=0 `verdict all_pass=True`，与入库正式 JSON 逐字段比对 **summary 0 diff / per_region 0/511 diff**。
- **集成复跑（merge head `d5b1831d`）**：全量 seg05 正式口径（C4 隔离 venv，cuda）EXIT=0，`all_pass=True`（Recall 0.9618 / MeanCov 0.9965 / severe 0.0；bubble 丢弃 903）；逐字段比对 **summary 0 diff / per_region 0/511 diff（确定性复现）**。

## 3. 本 Task 导出重跑（AC1 全量导出，正式口径 + 新导出 flag）

- 命令（`reproduce_command` 字段同文）：

  ```
  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
    experiments/M2-DOCTR-QUAL/eval_detection_manga.py \
    --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
    --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" \
    --device cuda --conf-threshold 0.5 --previews 0 --task M2-DOCTR-QUAL-C1 \
    --out verification/M2-DOCTR-QUAL/spot-audit/data/frames-rerun.json \
    --export-frames verification/M2-DOCTR-QUAL/spot-audit/data/frames-export.json \
    --export-pairs verification/M2-DOCTR-QUAL/spot-audit/data/pairs-export.json
  ```

- **EXIT=0**；墙钟 2026-09-30T17:05:25+08:00 → 17:05:52+08:00（脚本内 elapsed=21.7 s）。
- raw stdout 全文（外部 gitignored 路径，12 行含 transformers 进度条与 numpy 警告）：
  `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/logs/export-rerun-stdout.txt`
- committed stdout 摘要（剥离加载条/警告后共 9 行）：

  ```
  candidate=ogkalu/comic-text-and-bubble-detector device=cuda conf=0.5 regions=511 elapsed=21.7s
  PRIMARY block_coverage: precision=0.8909 recall=0.9618 meanCov=0.9965 severe_miss_rate=0.0000
  diag block_strict:      precision=0.8525 recall=0.9204 meanIoU=0.7844
  diag raw_strict (text-box granularity, NOT judged): recall=0.9553
  bubble-class detections dropped (not a text box): 903
  verdict all_pass=True
  results -> verification\M2-DOCTR-QUAL\spot-audit\data\frames-rerun.json
  frames export -> verification\M2-DOCTR-QUAL\spot-audit\data\frames-export.json (143 rows)
  pairs export -> verification\M2-DOCTR-QUAL\spot-audit\data\pairs-export.json (882 rows)
  ```

- **与正式 JSON 同源性证明**：`frames-rerun.json` vs `results-formal-manga_rt_detr_v2-cuda-seg05.json` 逐字段 diff（排除运行元数据 `generated_at` / `elapsed_seconds` / `reproduce_command` / `task`）= **0 diff**；`summary`、`per_region`、`candidate`、`manifest_sha256` 全等。C 层分母（matched-pair coverage 分布）即来自本次导出：882 对中 `lt_0.5`=0、`[0.5,0.7)`=**2**、`≥0.7`=880。

## 4. 行为不变性证明（AC1 附加纪律）

`--limit 8` 冒烟两遍（同 venv/cuda/conf 0.5，`--previews 0`）：

| 运行 | 导出 flag | EXIT | stdout 行数 |
|---|---|---|---|
| smoke-noflag | 无 | 0 | 10 |
| smoke-flag | `--export-frames` + `--export-pairs` | 0 | 12（=10 + 2 行 export 行） |

两遍 out JSON 逐字段 diff（排除运行元数据）= **0 diff**；stdout 差异仅为尾部两行 export 路径行。即：**不带新 flag 时行为与输出与 C4 完全一致**。raw 日志（外部）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/tmp/smoke-noflag.stdout.txt`、`.../smoke-flag.stdout.txt`。

## 5. 抽样清单确定性自检（AC2）

`build_spot_audit_sample.py`（种子 `20260930`）三重验证，全部 EXIT=0：

1. **脚本内 `--self-check`**：同进程从磁盘重建 payload 两次，JSON 字节一致 → `pass: same-seed rebuild byte-identical`；
2. **同参数跨进程重跑**（覆盖写）：`spot-audit-sample.json` / `spot-audit-sample.csv` / `labeling-worksheet.csv` 三文件 SHA-256 与首跑逐一相同；
3. **异目录、无 self-check 重跑**（payload 为纯输入函数证明）：三文件 SHA-256 再次全部相同。

committed 产物 SHA-256：

```
deb3814e16f6a178dc9f363382975378231de461c17ea60c4c763df56b493bba  spot-audit-sample.json
b1ccd6026984c0e6d07b29982cd99456821c0f6e9457b09e8444bcd97beaa673  spot-audit-sample.csv
96b40e4a（阶段一空表版 hash；正式交付表终版 hash 见 c1-spot-audit-report.md §7：da93f4f9…）f7dcb98cf3782e1dc422f7e7691b800dcb7632668160e93641ebb4cf  labeling-worksheet.csv
```

运行日志（外部）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/logs/sample-run{1,2,3}-stdout.txt`、`sample-sha-run{1,2,3}.txt`。

## 6. 分母核对表（冻结协议 §7.2 vs 本次实测，三源交叉）

核对源：①rerun `per_region`（与正式 JSON 全等）②`frames-export.json` layer_denominators ③冻结预期常数——三源任一不一致脚本即 fail-closed 退出（实际全部一致，EXIT=0）。

| 层 | §7.2 预期（N3 更正口径） | 实测 | 判定 |
|---|---|---|---|
| A1 真未检出 | 6 框（K06 r36/r38/r48/r94、K07 r79、K09 r14，各 1 GT） | 6 框/6 region，region 列表逐一相同 | 一致 |
| A2 coverage 不达标 | 2 region（K07 r109：1 检出框；K08 r3：3 检出框） | 2 region / 4 检出框，region 一致 | 一致 |
| B1 有 GT region 的 FP | 78 框 / 49 region | 78 / 49 | 一致 |
| B2 无 GT region 的 FP | 30 框 / 23 region | 30 / 23 | 一致 |
| C 贴合匹配对 | 导出后实测（不足 20 全查） | **2 对**（882 对中 coverage∈[0.5,0.7)）→ **fallback 全查触发（协议内）** | 实测登记 |
| D 零检测校准 | 78 个 `n_det_block=0`（72 `n_gt=0` + 6 A1） | 78（72 + 6） | 一致 |

汇总守恒交叉验证：B1+B2=108 = `summary.block_coverage.fp`；未匹配 GT 35 = A1 6 + A2 GT 2 + FN-partial 27（23 个部分命中 region 的残差 GT 框——**冻结 6 层协议不含该层**，frames 导出中标记 `FN-partial` 留证，不入清单）。A2 的 4 个检出框按冻结分母定义同时计入 B1 的 78 框（框级重叠）；抽样清单在 B1-U11（K08 r3）命中此重叠并已在单元 note 中标注。

## 7. 交付物 SHA-256（本文件同目录）

| 文件 | 说明 |
|---|---|
| `spot-audit-sample.json` / `.csv` | 6 层抽样清单（50 单元，元数据+分层明细） |
| `labeling-worksheet.csv` | 判定工作表（verdict/rationale 列为空，用户专属） |
| `README.md` | 用户判定指引 |
| `data/frames-rerun.json` | 导出重跑结果 JSON（与正式 0 diff） |
| `data/frames-export.json` | 143 框级导出（B1/B2 FP + A1/A2 GT + FN-partial） |
| `data/pairs-export.json` | 882 匹配对导出（含 per-pair coverage） |

预览图 50 张落 gitignored 外部路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews/`（版权素材不入库，与 C4 同纪律）。
