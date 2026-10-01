---
id: M2-OCR-PADDLE3X-1
title: "生产 ocr_local.py PaddleOCR 3.x 适配修复（bytes 静默忽略 + 3.x 输出形状 + 双 region 行为判定）"
kind: feature
status: done  # 集成收口：DSH r1 approved_with_conditions 条件全闭（integration.md），merge 进 main 由编排会话执行
approval: ta3b_phase1_finding_registered_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B]
base_commit: 69137837  # release 父 commit（TA3-B R18 惯例）；分支起点=release commit 19adf0e0，review diff 以 19adf0e0..tip 为界（DSH r1 R6 口径澄清）
delivery_head: 15ef29ab
branch: agent/zcode/M2-OCR-PADDLE3X-1
worktree: G:/CODEX/New Manga.worktrees/M2-OCR-PADDLE3X-1-zcode
handoff: doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md
evidence: verification/M2-OCR-PADDLE3X-1/
---

# M2-OCR-PADDLE3X-1：PaddleOCR 3.x 生产适配修复

## AC 状态（2026-10-01，ZCode 交付，待 DSH review）

| AC | 状态 | 证据 |
|---|---|---|
| AC1 诊断先行 | **done** | verdict=ALWAYS_EMPTY（stale-reuse 排除，wrong-text 风险不存在）；探针 `experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py`（隔离 venv 实测 EXIT=0），报告 `verification/M2-OCR-PADDLE3X-1/diagnosis.md` + `diagnosis.json`；结论已写入 module docstring |
| AC2 输入侧修复 | **done** | recognize 前 bytes→BGR ndarray（`np.frombuffer`+`cv2.imdecode`，不可解码→typed `ProviderInputError`）；默认构造 `enable_mkldnn=False`；`engine_factory` 注入路径与 lazy 探针顺序不变；commit `15ef29ab` |
| AC3 输出侧修复 | **done** | `_parse_paddle_output` 双形状（legacy 2.x 嵌套 + 3.x `rec_texts/rec_scores/rec_polys|rec_boxes`，dict 与 `.json` 对象两形态）；box 先 `.tolist()` 物化（N6 静默丢弃修复）；`rec_boxes` xyxy→4 点 polygon；缺失/短 scores 记 None 不发明；不可识别形状仍 typed `ProviderInvalidOutput`；`provider_id`/`provider_type`/错误码零变化 |
| AC4 测试 | **done** | 先红后绿：`tests/providers/test_ocr_local.py` 17 测试（修复前 10 failed 红：3.x 解析抛 ProviderInvalidOutput / engine 收到 bytes / 无 mkldnn kwarg；修复后全绿）；主 venv 全量 490→**507 passed + 1 skipped 0 failed**；真实引擎端到端隔离 venv 手动验证（零注入生产路径页面级 28 行全 polygon 非空 + crop 等价性矩阵 6/6），证据 `verification/M2-OCR-PADDLE3X-1/e2e-real-engine.md` |
| AC5 文档 | **done（登记替代）** | module docstring 已更新（观测 vs 机制、mkldnn 原因、版本口径）；D06 OCR 环节版本口径与两项引擎限制登记在 handoff（`doc/contracts/**` 与 D06 不在允许面，按任务书以 handoff 登记替代） |

交付限制（如实登记，详见 handoff）：PP-OCRv5 det 对孤立小 crop 常检不出框、默认构造全预处理页面级质量低于精简预处理（conf 0.41 vs 0.69）——均超本 Task 授权面（构造参数授权仅 `enable_mkldnn=False`），待 D06/阶段二质量 Task 决策；TA3-B2 runner wrapper 输入约定需在 merge 本修复后一行适配（`ocr(data)` 将收到 ndarray）。

## 缺陷（M2-TA3-B 阶段一实证，DSH r1 R6/R10 + r2 N6 确认）

`src/infrastructure/providers/ocr_local.py` 的 `PaddleKoreanOcrProvider` 面向 paddleocr 3.x 环境存在三件缺陷：

1. **输入契约**：`ocr_local.py:184` 附近 `engine.ocr(request.image_bytes)` 直传 bytes——paddleocr 3.x 对 bytes 输入**静默返回空结果且无异常**（观测事实，`verification/M2-TA3-B/ocr-smoke-paddleocr.json`）。用户从 Settings UI 选 PaddleOCR 时会静默产出空 OCR。
2. **输出形状**：`_parse_paddle_output`（`ocr_local.py:202-241`）只接受 legacy `[[box,(text,score)],…]` 嵌套，3.x 实际返回 `rec_texts/rec_scores/rec_polys` 结构 → adapter 抛 `ProviderInvalidOutput`（fail-closed，但功能不可用）。
3. **机制未判定（R10）**：bytes 路径空结果是"恒空"还是"错位复用上一次输入"未验证——后者是静默错误文本，严重度显著更高。诊断步骤：**连续 2 个不同 region 走 bytes 路径**对比输出。

已知修复形态参考（已端到端验证）：TA3-B R6 探针 `experiments/M2-TA3-B/paddle_e2e_probe.py` 的双侧 wrapper（bytes→ndarray `cv2.imdecode`、`enable_mkldnn=False`（paddle 3.3.1 Windows CPU PIR/oneDNN 必崩）、3.x→legacy 映射、**box 必须物化为 Python list（numpy 非 `collections.abc.Sequence`，`_polygon_of` 静默返回空）**）。本 Task 把等价适配落进生产 adapter（非 runner 侧绕行）。

## 交付（AC）

1. **AC1 诊断先行**：双 region bytes 行为判定探针（隔离 venv `task-envs/M2-TA3-B-ocr`，script 放 `experiments/M2-OCR-PADDLE3X-1/`），结论（always-empty vs stale-reuse）落盘并写入 docstring/Task；若 stale-reuse 成立，在报告中显著标注（历史上发生过错误文本输出的风险面）。
2. **AC2 输入侧修复**：生产 adapter 对 bytes 输入不再直传 3.x engine——engine 构造带 `enable_mkldnn=False`，recognize 前 bytes→ndarray（Windows CJK 安全解码），或等价方案；行为对 2.x 旧形状环境保持兼容（不假设用户环境版本）。
3. **AC3 输出侧修复**：`_parse_paddle_output` 支持 3.x `rec_texts/rec_scores/rec_polys|rec_boxes`（含 box 物化）；不可识别形状仍 typed `ProviderInvalidOutput`（fail-closed 语义不放宽）；polygon 非空断言进测试。
4. **AC4 测试**：先红后绿——无 paddle 环境下的 typed `PROVIDER_DEPENDENCY_MISSING` 测试（主 venv 可跑）；有 paddle 环境的真实引擎端到端测试（隔离 venv 手动验证，pytest 以 skipif 保存或作探针脚本双轨）；3.x 形状解析单测（伪造 3.x 输出结构，不需要真引擎）。
5. **AC5 文档**：D06 OCR 环节如涉及版本口径则登记（`doc/contracts/**` 不在允许面时以 Task/Handoff 登记替代）；module docstring 更新（观测 vs 机制结论、`enable_mkldnn=False` 原因）。

## 允许修改面

`src/infrastructure/providers/ocr_local.py`、`tests/providers/**`（ocr 相关）、`experiments/M2-OCR-PADDLE3X-1/**`、`verification/M2-OCR-PADDLE3X-1/**`、`doc/tasks/M2-OCR-PADDLE3X-1.md`、`doc/handoffs/M2-OCR-PADDLE3X-1-*.md`。

## 禁改面

`src/ports/**`（协议不变）、其他 provider、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`experiments/M2-TA3-B/**` 与 `experiments/M2-TA3-A/**`（只读参考）、`doc/STATUS.md`。

## 纪律

- fail-closed 四纪律不放宽；`provider_id`/`provider_type`/typed 错误码零变化（消费方零感知，除行为从"静默空/异常"变为"可用或 typed"）。
- 测试基线不回退（main 490+1skipped 0 failed）；真实 paddle 验证用隔离 venv（主 venv 无 paddle 依赖，不引入）。
- 与 M2-TA3-B2（并行进行中）无文件交集；runner 侧 wrapper 不受影响（`engine_factory` 注入路径保持）。
