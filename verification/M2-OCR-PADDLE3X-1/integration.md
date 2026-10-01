# M2-OCR-PADDLE3X-1 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-OCR-PADDLE3X-1`；链：release `19adf0e0`（base_commit=`69137837`=release 父，R18 惯例）→ `1885619b`(AC1 诊断) → `15ef29ab`(implement, delivery_head) → `67e974a1`(docs/tip)
- Review：DSH r1 **`approved_with_conditions`**（0×P0/P1；1×P2=R1 红态证据 + 5×P3 + 3×P4；报告 `doc/reviews/M2-OCR-PADDLE3X-1-15ef29ab-dsh-r1.md` 原字节入库，sha256 `b997a240…7046`）

## DSH 闭合清单执行（2026-10-01，全部闭合）

| # | 项 | 结果 |
|---|---|---|
| 1 | git 事实：merge-base=`19adf0e0`（线性 4 commit）；`diff --name-only 19adf0e0..67e974a1`=12 文件恰为允许面；禁改面（src/ports、src/bootstrap、doc/contracts、packaging、apps、TA3-A/B experiments、doc/STATUS.md）diff 空；`git diff --check` EXIT=0。R6=口径澄清（base_commit=release 父 vs diff base=release 起点，frontmatter 已加注记） | PASS |
| 2 | **R1（P2）红/绿 pytest 复跑留痕**：红态（`1885619b` src + `15ef29ab` tests）= **9 failed, 8 passed**（log `task-envs/M2-OCR-PADDLE3X-1/raw/red-state-pytest.log`）；绿态三套件 = **507 passed + 1 skipped, 0 failed**（`raw/green-state-suite.log`，venv `T1.1.1-impl-py312`）。**账目差异如实登记**：Owner/DSH 声称红态 10 failed/7 passed，实跑 9/8——差异=`test_missing_opencv_runtime_fails_typed`（环境防御测试，非红绿判别性测试，红绿两态均 PASS）；判别性主张（新测试修前失败）对全部 9 个判别测试成立，声称的 10/7 数字无法复现，定性为交付报告数字登记不准确（P4 级），不影响 AC4 实质 | PASS（附差异登记） |
| 3 | 真实引擎复核（隔离 venv M2-TA3-B-ocr）：`diagnose_bytes_path.py` 复跑 `probe_verdict=ALWAYS_EMPTY` EXIT=0（引擎拒绝日志原话直接可见于 stderr）；`paddle_fixed_e2e_probe.py` 复跑 `status=OK`、`page_level_n_lines=28`、polygon 全非空、mean conf 0.4086——与交付版**逐位一致**；孤立 crop `n_lines=0` 观测项同样复现（det 不确定性，与 handoff 风险②一致）。R7 注记：隔离 venv opencv-python 5.0.0 与 opencv-contrib-python 4.10.0.84 并存已知，`cv2.imdecode/imencode/IMREAD_COLOR` 跨版本稳定，接受 | PASS |
| 4 | R2/R3 集成修正 commit：R2=src docstring 注入契约句（注入 engine 收 BGR ndarray，非 bytes）+ tests docstring 更正（TA3-B2 wrapper 需一行适配）；R3=`texts/scores` 显式 `is None` 判空（消除 ndarray truth-value ambiguous 窗口）+ `_box_at` 异常集合补 `KeyError`；新增 2 条回归测试（ndarray texts/scores、dict 形 polys 缺键），ocr_local 测试 17→**19 passed** | PASS |
| 5 | R4：diagnosis.md 补 stale-reuse 结构性排除论据 + 复跑 stderr 指针 + 构造口径注记；探针构造注释同步为「pre-fix production default」。R5：性能对照（mkldnn off）与 2.x 兼容实测登记为 D06/后续测量项（见下方台账） | PASS |
| 6 | R9：DSH 报告按仓库惯例落 `doc/reviews/M2-OCR-PADDLE3X-1-15ef29ab-dsh-r1.md`（原字节 + sha256 登记）；handoff 中 `verification/` 路径建议由本记录取代 | PASS |

## 遗留台账（后续 Task / D06 登记项，非阻塞）

1. **TA3-B2 联动（handoff 风险①）**：本修复 merge 后，注入 engine 收到 ndarray——TA3-B2 runner 的 wrapper（`experiments/M2-TA3-B/run_qualification.py` 内）需一行 ndarray 直通适配；**在 TA3-B2 集成修正 commit 中落地**（其 run 在旧 adapter 语义下执行仍有效）。
2. mkldnn=False 的 CPU 性能对照（未测）；paddleocr 2.x 真环境兼容组合实测（enable_mkldnn kwarg/ndarray 输入/legacy 解析）。
3. PP-OCRv5 det 孤立小 crop 零框不确定性 + 默认构造全预处理质量（conf 0.41）vs 精简预处理（0.69）——engine 质量/配置决策，归 D06/阶段二质量台账。
4. cv2 测试间接依赖（R8，python-doctr 传递）——dev 依赖注记候选。
5. 零检测页（无文字图）`recognize` 不抛错验证（DSH NOT_VERIFIED 4）——轻量，随下次涉及 ocr_local 的改动顺带覆盖。

## 集成 commit 清单

- `doc/reviews/M2-OCR-PADDLE3X-1-15ef29ab-dsh-r1.md`（原字节 import）
- `src/infrastructure/providers/ocr_local.py`（R2 契约句 + R3 两处收紧）
- `tests/providers/test_ocr_local.py`（R2 docstring + 2 条 R3 回归测试）
- `experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py`（R4 构造注释）
- `verification/M2-OCR-PADDLE3X-1/diagnosis.md`（R4 论据）
- `doc/tasks/M2-OCR-PADDLE3X-1.md`（R6 frontmatter 注记 + status done 回填）
- `verification/M2-OCR-PADDLE3X-1/integration.md`（本文件）
