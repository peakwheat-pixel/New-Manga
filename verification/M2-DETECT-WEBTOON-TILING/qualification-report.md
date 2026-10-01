# M2-DETECT-WEBTOON-TILING：qualification 报告（AC3）

- Task: `M2-DETECT-WEBTOON-TILING`（owner: ZCode；reviewer: DeepSeek Harness 非作者）
- 分支 / worktree: `agent/zcode/M2-DETECT-WEBTOON-TILING` @ `G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode`
- 脚本: [qualify_tiling.py](../../experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py)；raw 数据: [qualification-results.json](qualification-results.json)
- 运行: 主 venv `T1.1.1-impl-py312`（torch 2.14.0+cpu / transformers 5.17.0 / numpy 2.5.3，CPU），生产构造 `MangaDetectionProvider(weights_dir, device)`，权重三文件 sha256 与生产 pin 全匹配（JSON `weights.all_pins_match=true`），tiling 参数=冻结默认（1024/128/0.5/4.0），conf 生产默认 0.5。
- 判定性质: qualification（AC3 冻结口径逐条执行）；零 `src/**`/`tests/**` 之外改动，tile 图块仅驻留内存。

## 1. Gate：5 张 webtoon_long_strip 生产 region 数 > 0 —— **PASS**

生产 `provider.detect`（conf 0.5、tiling 默认参数），region=生产合并后 `candidates` 层级：

| 页 | 尺寸 W×H | 块数 | region 数（Gate） | 合并前框数 | CPU 延迟 | 预算 | 判定 |
|---|---|---|---|---|---|---|---|
| K01 | 690×62133 | 70 | **180** | 193 | 20 104 ms | ≤25 s | PASS |
| K02 | 600×18401 | 21 | **93** | 97 | 5 968 ms | ≤10 s | PASS |
| K04 | 690×28156 | 32 | **113** | 117 | 9 271 ms | ≤15 s | PASS |
| K05 | 690×46000 | 52 | **62** | 64 | 14 277 ms | （无预算项，如实登记） | PASS |
| K08 | 690×51971 | 58 | **60** | 61 | 16 252 ms | （无预算项，如实登记） | PASS |

- 三张预算页全部在预算内；K05/K08 不在预算表，延迟数字如实登记（发布形态输入）。
- **K01 合并前框数=193，与 DIAG 块级实验逐值一致**（同一页同一参数独立复现）——生产 tiling 路径即 DIAG 实验的产品化。

## 2. 阈值点候选数曲线（conf 0.5 生产 vs 0.4）

| 页 | 0.5: 框 / region | 0.4: 框 / region | 0.4 conf_min |
|---|---|---|---|
| K01 | 193 / 180 | 214 / 191 | 0.4011 |
| K02 | 97 / 93 | 103 / 97 | 0.4047 |
| K04 | 117 / 113 | 120 / 115 | 0.4344 |
| K05 | 64 / 62 | 65 / 62 | 0.4476 |
| K08 | 61 / 60 | 65 / 62 | 0.4259 |

检出数对阈值敏感（DIAG §4 预警的"贴阈"形态），但生产 0.5 点各页 conf_max 0.9666–0.9725、分布健康；0.5→0.4 增幅 +5%~+11%（框级），无爆炸。conf 阈值生产默认 0.5 不变（纪律），0.4 仅为曲线数据。

## 3. 690×690 原生尺度对照组（K01，分辨率假设验证）

tile 690（=K01 原生宽，水平重采样 ≈0.93×≈1.0×）、overlap 128、conf 0.5：**111 块（≈70×1.6×）→ 198 框 / 177 region，31 887 ms**。与 1024² 的 193 框 / 180 region 同量级（+2.6%）——**分辨率假设成立**：检出恢复来自"消除整页 640×640 重缩放"而非特定 tile 尺寸的产物。

## 4. 对照组

- **K19**（1200×1660 `paged_webcomic` 无字页）：0 candidates、`tiling=off`——正确行为。F4（无字页被 handler 判 `step=failed/INVALID_INPUT` 应为空成功）口径缺陷**本 Task 不修**，登记为相邻发现（与 DIAG 定案一致）。
- **BJ02**（2946×4167 正常页）：region=5、`tiling=off`——与 DIAG 探针逐值一致（`matches_diag_probe=true`），普通页行为零变化。

## 5. 发现（MERGE 合并行为 + 粒度登记）

1. **MERGE_* 对 tiling 框的合并行为正常**（任务书风险提示项）：`cluster_words_into_blocks` 对 193→180（K01）、97→93、117→113、64→62、61→60——合并率 1.6%~7.2%，无 region=0、无爆炸，第二层 post-processing 问题不存在。
2. **粒度登记（非缺陷）**：ogkalu tiling 框多为"气泡文本块"级而非"词"级（合并率低），K01 生产 region=180 远细于 docTR 路径同页的 15（TA3-A smoke，生产合并后口径）。两 provider 输出粒度差异属实，但 Gate 口径（region>0、全链可用）不受影响；粒度对下游 OCR/翻译成本的影响留作产品观测，不在本 Task 裁定。
3. 逐块检出覆盖率：K01 70/70 块全部参与（DIAG 已证），本轮五页块数 21–70，全页 y 覆盖由重叠带保证。

## 6. 局限

- CPU 单环境（数字见 JSON `environment`），GPU 绝对耗时不同；
- 无 ground truth：本 qualification 证明"region 恢复 + 行为零变化 + 延迟量级"，不证明逐框精度；
- K05/K08 无 DIAG 探针前数据，本轮为首次实测（Gate 一次通过）。
