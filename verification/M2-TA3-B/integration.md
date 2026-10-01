# M2-TA3-B 阶段一集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-TA3-B`；diff 基点 `53fdfcc6`（branch_base，Task frontmatter R18 注记）
- 交付链：`53811c36`(claim) → `b057ec69`(implement, delivery_head) → `2beca0bb`(AC 回填+handoff) → `cad45622`(DSH r1 返修 R1-R18)
- Review 链：DSH r1 `changes_requested`（0×P0/P1，7×P2 + 11×P3/P4，报告 `doc/reviews/M2-TA3-B-dsh-r1.md`，sha256 `1f3ba2f3…35d4`）→ Owner 返修 `cad45622`（R1-R18 全 closed，R9 重跑选样零变化）→ DSH r2 **approved**（0×P0/P1/P2，1×P3=N1 + 5×P4=N2..N6，报告 `doc/reviews/M2-TA3-B-dsh-r2.md`，sha256 `94a6c66a…3327`）

## 运行时复跑（r2 NOT_VERIFIED 清单，2026-10-01 全部闭合）

| # | 项 | 结果 |
|---|---|---|
| 1 | git 层：porcelain 空 / `diff --check 53fdfcc6..cad45622` EXIT=0 / 禁改面（src/packaging/apps/M2-TA3-A/requirements.txt）diff 空 / 权重后缀 grep 空 / 拓扑 5 commit 完整 / 交付 10 文件+返修 8 文件与 review artifact 一致 | 全 PASS |
| 2 | `select_cases.py` 复跑：EXIT=0、`verification_failures: []`、counts 20/10/10/superset=true；与交付 JSON 忽略时间戳逐字节一致（R9「selection 零变化」实证） | PASS |
| 3 | 20 case `page_sha256` 独立实算（文件字节 sha256 vs manifest） | 20/20 ALL_MATCH |
| 4 | 两条 `ocr_smoke.py` 复跑（隔离 venv M2-TA3-B-ocr）：manga-ocr EXIT=0、paddleocr EXIT=0、均 `status=OK`；与交付 JSON 唯一差异=started_at_utc/weights_load_s/wall_s/first_inference_s 四个计时字段（OCR 实质输出逐字段一致）；`pip freeze`+`python -V` 归档 `verification/M2-TA3-B/env-manifest.txt` | PASS |
| 5 | R6 最小端到端（r1 清单 5 / r2 NOT_VERIFIED 6）：生产 adapter `PaddleKoreanOcrProvider(engine_factory=wrapper)` + 1 真实 region（E04P02 检测框 [62,8,161,50] PNG 裁剪）→ 识别 `당근아?` conf 0.998、n_lines=1、**polygon 非空**；探针脚本 `experiments/M2-TA3-B/paddle_e2e_probe.py`、结果 `verification/M2-TA3-B/paddle-e2e-probe.json`。双侧适配（bytes→ndarray + 3.x rec_texts/rec_scores/rec_polys→legacy 嵌套）实证可行；r2 N6 的「box 必须物化为 Python list（numpy 非 Sequence，`_polygon_of` 会静默丢弃）」确认为必要并已在 wrapper 落实 | PASS |
| 6 | 权重存在性：paddlex 缓存（PP-OCRv5_server_det / korean_PP-OCRv5_mobile_rec）探针运行实证「Model files already exist」；HF 424MB 权重冒烟复跑实证 | PASS |

未复算项（如实登记）：r1 的 pip 安装 166s 计时与 HF 424MB 体积数字未独立重测（复跑行为证据覆盖其可用性）。

## DSH r2 新问题处置

- **N3（delivery_head 双口径）**：本次集成修正 commit 将 Task frontmatter `delivery_head` 更新为 `cad45622…`；handoff 文件名保持 `M2-TA3-B-b057ec69.md`（交付实体锚点，返修记录为该文件追加节——文件名与内容的偏离已由本记录盖戳）。
- **N1（ko G1 present-but-unaligned 未贯通）/ N4（R4/R5 文档残留：`core_assembly.py:763-772` 行号错引应为 `:484-498`、裸 UPDATE 缺 commit、`credential_ref` 裸名、`SAKURA_DEFAULT_BASE_URL` 归属句为假）/ N6（取消截断后估时未回看、选项表凭证口径）**：按 r2 建议**并入阶段二首个 Task 执行清单**一并落地（阶段二尚 BLOCKED_ON_USER，见下）；不阻塞阶段一集成。
- **N2（handoff/Task 旧口径交叉引用）/ N5（engine_factory 注入机制未点名 re-register）**：同上并入阶段二；阶段二 plan §2.2/§3 已是新口径，以 plan 为准。

## 阶段二状态

**BLOCKED_ON_USER**（不随本次集成解除）：翻译 endpoint 二选一——(a) 用户提供 OpenAI-compatible `base_url`+`model`+API key（key 经 vault 或 runner env 注入，按返修后 §3(a) 序列）；(b) 授权 Sakura GB 级模型本地部署（llama-server 127.0.0.1:8080）。用户裁决后按 `verification/M2-TA3-B/phase2-plan.md` 执行，第 0 步=本记录第 5 项探针的复跑。

## 归档清单（本次集成 commit）

- `doc/reviews/M2-TA3-B-dsh-r1.md` / `dsh-r2.md`（原字节 import）
- `verification/M2-TA3-B/integration.md`（本文件）
- `verification/M2-TA3-B/paddle-e2e-probe.json` / `env-manifest.txt`
- `experiments/M2-TA3-B/paddle_e2e_probe.py`（探针脚本 in-repo，DOC-FIX-STALE N-6 先例）
- `doc/tasks/M2-TA3-B.md`（frontmatter delivery_head 更新）
