# verification/TASK-043 — evidence index

交付 head `d8e9406`（分支 `agent/deepseek/TASK-043-import-fixes`）。环境：PowerShell + `TASK-012-py312`
（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1），`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`。
被测源码树与命令逐项写在对应文件内。

## 探针（可复跑；脚本首行都会打印实际加载的 src 树，避免串树）

| 文件 | 用途 |
|---|---|
| `probe_prereq.py` / `probe-prereq.txt` | 前置事实：`Format_BGR888` 存在且值 29、两个格式对同一缓冲的语义差别；0 页 PDF 是否可达（结论：pdfium 直接拒绝）；**修前**生产光栅器的三原色中心像素 |
| `pixel_probe.py` / `pixels-pre-fix.txt` / `pixels-post-fix.txt` | F-1 修前/修后像素对照。两棵树分别用 `PYTHONPATH` 选择，日志首行打印 `using tree` |
| `bgra_basis_probe.py` / `bgra-basis.txt` | BGRA→`Format_ARGB32` 字节序依据（不可达分支的正确性钉在字节上） |
| `bgra_basis_diag.py` / `bgra-basis-diag.txt` | 上述探针第一版读到"全黑"的原因：`bytesPerLine` 小于 `width*4` 会让 `QImage` 变成 `Format_Invalid`（null）；修正后 `pixel(0,0)=0xffff0000` |
| `pdf_builder_identity.py` / `pdf-builder-identity.txt` | 证明 `minimal_pdf` 抽出 `_assemble_pdf()` 后**字节恒等**（n=1,2,3,5,8 全等） |

## 判别力（修前必须失败）

| 文件 | 内容 |
|---|---|
| `pre-fix-tests-against-base-src.txt` | base `c5aa664` 的 `src` + 本次新测试，`-q -rs -rf`：**8 failed / 8 passed**，含逐条 node id 与树溯源（`infrastructure.importing = ...\task043-prefix\src\...`） |
| `pre-fix-import_formats.txt` | 同一判别的首次在时留证（改 `src` 之前跑的完整失败详情：红→蓝 `(0,0,255)`、蓝→红 `(255,0,0)`、裸 `ModuleNotFoundError` 逃逸等） |

修前**通过**的两项及其理由（不计入判别力，仅作守卫）：F-1 `[green]` 在 R↔B 互换下恒等；`test_zero_page_pdf_through_the_production_raster_fails_typed` 因生产 PDFium 本就 typed 拒绝。

## 回归

| 文件 | 内容 |
|---|---|
| `post-fix-targeted.txt` | `tests/import_formats tests/library` = **56 passed / 0 skipped** |
| `post-fix-targeted-with-providers.txt` | 上述 + `tests/providers` = **225 passed / 0 skipped**（16 + 40 + 169） |
| `full-suite-runs.log` | 全仓 **5 次连续 802 passed / 6 skipped，逐次 exit 0**；另附 run 6（`-rs` 单独使用）给出 6 条 skip 的逐条原因 |
| `skip-reasons.txt` | `tests/network` 单独复跑：91 passed / **6 skipped**，全部 `openssl unavailable` |
| `baseline-master-c5aa664.txt` | 独立基线（主仓库 master `c5aa664`）= **792 passed / 6 skipped** → 与交付树的差值恰为新增 10 例 |

## 说明

- pytest 的 `-r` 只接受**一组**字符：`-rs -rf` 中的第二个会覆盖第一个，故 runs 1–5 只有计数没有 skip 明细；run 6 单独用 `-rs` 补齐（已在 log 内注明）。
- 证据文件均在提交 `d8e9406` 内；本 README 与 Handoff 在随后的文档提交中。
