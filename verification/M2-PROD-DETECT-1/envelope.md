# M2-PROD-DETECT-1 Envelope 实测（AC3 + AC5）

- Owner: ZCode（worktree `G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-1-zcode`）
- 日期：2026-09-30
- 机器：本机（win32，RTX 5070 Ti 存在但本轮全部 CPU 路径；`torch.cuda.is_available()=False` 为 CPU wheels）
- 生产 provider：`MangaDetectionProvider`（`src/infrastructure/providers/detection_manga.py`），完整生产路径（validate → frame pixels → processor → model → post_process → 三类过滤 → 冻结合并）
- 权重：本地快照 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（三文件 SHA-256 逐文件校验 OK，见下）
- venv：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（torch 2.14.0+cpu，transformers 5.17.0，safetensors 0.8.0，numpy 2.5.3）
- 素材：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json` 前 5 个 region（真实推理素材，与 C4 同源）

## AC3 CPU 兼容门（go/no-go）

| 项 | 实测 |
|---|---|
| torch × transformers | 2.14.0+cpu × 5.17.0（`transformers==5.17.0`、`safetensors==0.8.0` 新装，torch/doctr 未动） |
| 三文件 SHA-256 | `model.safetensors` `037930a8…` / `config.json` `b6d70793…` / `preprocessor_config.json` `7e9e2245…` 全 OK |
| `from_pretrained` 本地目录（`local_files_only=True`） | processor + model 加载 OK，770 张量，0.4s，params=42,733,137 |
| 单页真实推理（`K01_R001.png` 690x672，conf 0.5） | EXIT=0，2 个 text box（label=1，score 0.941/0.938）+ 2 个 bubble 类被丢弃 |
| 结论 | **PASS（EXIT=0）**——torch 2.14.0 CPU wheels × transformers 5.17.0 兼容，C4 的 cuda-only 缺口闭合 |

复现：`"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" "G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-1-work/ac3_cpu_gate.py"`（EXIT=0）。

## AC5 CPU envelope（n=5，稳态，预热 1 页不计入）

| case | 尺寸 | elapsed_ms | block candidates | bubble 丢弃 |
|---|---|---|---|---|
| K01 R1 | 690x672 | 319 | 2 | 2 |
| K01 R2 | 690x514 | 319 | 2 | 2 |
| K01 R3 | 690x672 | 310 | 2 | 2 |
| K01 R4 | 690x568 | 317 | 2 | 2 |
| K01 R5 | 690x528 | 313 | 1 | 1 |
| **合计** | — | **1578** | **9** | **9** |

- **CPU ms/页（detect 全链）平均 = 315.6 ms/页**（310–319，n=5，波动 <3%）
- 每 block candidate 口径 = 175.3 ms/候选（1578/9，仅供内部参考——C4 基线是每输入页一口径，不与此直接比）

### GPU 对照（引用基线，非本轮实测）

- C4 formal（`verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json`）：38.9s / 511 页 ≈ **76.1 ms/页**（cuda，conf 0.5）。
- **CPU/GPU ≈ 4.1×**（315.6 / 76.1）。RT-DETR-v2（42.9M params）CPU 延迟与预期一致地显著高于 GPU；性能优化不在本 Task 范围（Task 风险②如实记录）。detect 为逐页一次性成本，CPU 路径可用性已由本轮 EXIT=0 证明。

## Sidecar 体积（AC6 相关，实测见 checkpoint 记录）

- 构建前后 onedir 体积对比在 AC6 执行后回填于任务表与本文件末尾（transformers/torch 依赖懒加载、不进 PyInstaller 闭包，预期增量仅为新增 `detection_manga` 模块字节码，KB 级）。

## 已知边界

- n=5 页全部来自 K01 案例（manifest 前 5 region）；页尺寸相近（690px 宽），延迟对超大页（如长条 webtoon）的外推未测——后续 slice 如需 CPU 全量跑批再测。
- envelope 测的是 adapter 单页 `detect()`（含合并），不含 Region 写库等 handler 开销。
