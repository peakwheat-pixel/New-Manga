---
task_id: T1.1.1
reviewer: Codex
author: ZCode
base_commit: 4a1ed6ca2778301da983f9f9159210a2fcca6985
reviewed_head: 2f116a2
decision: approved
---

# T1.1.1 R2 Non-author Review

审查对象为 `2f116a2` 的代码、测试和合规修订；其后续文档提交为
`4a631355316e959e9a9704f1ead2eaed39cbf7a3`，只追加 R2 作者验证记录和
Handoff。ZCode 未合并 master。本报告由 Codex 在独立 worktree 完成。

## 范围与提交裁决

`git diff 4a1ed6ca..2f116a2 --stat` 共 11 个文件，全部属于授权范围：

- `src/infrastructure/providers/detection_doctr.py`
- `requirements.txt`
- `tests/providers/test_detection_doctr.py`
- `verification/T1.1.1/scripts/fetch_doctr_weights.py`
- `verification/T1.1.1/compliance/**`

没有修改 `src/bootstrap/app.py`、ports、Schema、QML、Roadmap、STATUS 或
export 路径。R2 代码 diff 没有跨越 T1.1.1 边界。

## Architecture / Spec Review

- Fail-closed 顺序仍为权重存在性 → torch → 设备 → SHA-256 → docTR；缺权重
  不触碰重依赖，错误为 `PROVIDER_NOT_CONFIGURED`；哈希不符为 typed
  `PROVIDER_FAILED`。`fast_base(pretrained=False)` 与本地权重加载没有运行时
  下载或静默 fallback。
- 生产帧契约仍按 raw QImage `rgb32`/BGRA 或 `rgb24` 解码，ports docstring
  未被越权修改。
- `cluster_words_into_blocks` 现在实际使用水平 gap 常量，padding 后在生产
  `detect` 路径传入页尺寸并做页界 clip；merge 常量仍冻结为 `0.7 / 8.0 /
  8.0 / 6.0`。
- `requirements.txt` 固定 `python-doctr==1.1.0`、`torch==2.14.0`、
  `torchvision==0.29.0`。GPU 一次性环境使用 CUDA wheel，属于后续 T3.2.1
  打包决策，不改变本任务 CPU requirements pin。
- compliance 留档包含上游 LICENSE、README、官方模型/数据集/共享模型文档和
  PyPI 元数据；结论明确不替代法务裁决，且没有把未存在的独立权重许可证写成
  已存在。
- bootstrap 的现有生产 seam 仍是 `DoctrDetectionProvider` + 一个
  `region_creator`，没有新增 Region 第二写入路径；R2 未修改该装配边界。

## Findings

| ID | 级别 | 位置 | 结果 | 处理 |
|---|---|---|---|---|
| R2-B01 | BLOCKING（历史） | `detection_doctr.py:365-366` | `MERGE_HORIZONTAL_TOLERANCE_PX` 已实际参与 gap 判定；8.0/8.01 判别测试通过 | FIXED |
| R2-B02 | BLOCKING（历史） | `detection_doctr.py:383-390` | padding 后按 page size clip；detect 路径越界框测试通过 | FIXED |
| R2-B03 | BLOCKING（历史） | `requirements.txt:6-13` | docTR、torch、torchvision 已固定，CPU/GPU packaging 边界有明文说明 | FIXED |
| R2-B04 | BLOCKING（历史） | `verification/T1.1.1/compliance/` | 留档文件 SHA-256 全部与 `compliance.md` 清单一致，证据链和限制已写明 | FIXED |
| R2-B05 | BLOCKING（历史） | `fetch_doctr_weights.py:49-66` | env 精确文件路径 → `--dest` → `./models/detector`，与 bootstrap 数据根布局一致 | FIXED |
| R2-B06 | BLOCKING（历史） | `test_detection_doctr.py:80-124,170-188` | 水平/垂直阈值、padding、页界 clip 和 detect 路径均有判别测试 | FIXED |
| R2-I01 | IMPORTANT | `author-verification.md:256-265`; Handoff §2 | 作者记录的全量 pass/skip 拆分与本次同命令 fresh 结果不一致；总 collected 数和失败身份可解释，但证据数字需校正 | DEFER：以本报告 fresh 记录为准，集成记录中更正文档口径 |
| R2-I02 | IMPORTANT | Handoff §3; `tests/reading_export/test_viewmodels.py:275` | export `exportFinished` 信号竞态在 R2 基线环境仍复现；R2 diff 不含 export 文件，故不是 T1.1.1 回归 | DEFER：独立 export/reading reliability 修复窗口，建议归入 T3.1.1 前置维护；不阻塞本 detector review |

在本审查范围内，新的 BLOCKING 为 0；没有发现 source-file modification、
静默 fallback、坐标越界、持久化路径或生产 detector wiring 的新阻塞。

## Fresh Verification

以下均在 `G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`
执行；命令包含实际 Python 环境，退出码为本次运行结果。

| 场景 | 命令/环境 | 结果 |
|---|---|---|
| CPU 专项 | `T1.1.1-impl-py312`; 4 个 T1.1.1 provider/seam test 文件 | `46 passed in 11.03s`, EXIT 0 |
| GPU 专项 | `T1.1.1-gpu-py312`, `NEW_MANGA_DOCTR_DEVICE=cuda` | `46 passed in 15.79s`, EXIT 0 |
| 实现环境版本 | `python-doctr=1.1.0`, `torch=2.14.0`, `torchvision=0.29.0` | EXIT 0 |
| GPU 环境版本 | `python-doctr=1.1.0`, `torch=2.11.0+cu128`, `torchvision=0.26.0+cu128` | EXIT 0；GPU wheel 不属于 requirements pin |
| 实现环境全量 | `T1.1.1-impl-py312 -m pytest tests -q -p no:cacheprovider` | `1077 collected = 1069 passed + 6 skipped + 2 failed`, EXIT 1；失败仅为 registry readiness 环境断言和既有 export 竞态；6 skip 为 OpenSSL TLS cases |
| 基线环境全量 | `TASK-012-py312 -m pytest tests -q -rs -p no:cacheprovider` | `1053 collected = 1043 passed + 11 skipped + 1 failed`, EXIT 1；skip 为 2 docTR、6 OpenSSL、1 numpy、2 torch；唯一失败为同一 export 测试 |
| export 对照 | 实现环境定向运行 registry readiness + export 测试 | registry 为环境预期 FAIL、export FAIL；状态/历史已完成但 `exportFinished` 未收到 |
| 网络 skip 解释 | `T1.1.1-impl-py312 -m pytest tests/network -q -rs` | `91 passed + 6 skipped`, EXIT 0；6 skip 均为 openssl unavailable |
| Compile | `T1.1.1-impl-py312 -m compileall -q src tests` | EXIT 0 |
| Diff check | `git diff --check -- src tests verification/T1.1.1 requirements.txt` | EXIT 0 |
| 权重 pin | `fast_base-688a8b34.pt` | `65,814,772 B`; SHA-256 `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace`，与代码 pin 一致 |
| compliance hashes | 6 个留档文件逐个 `Get-FileHash` 对照 `compliance.md` | 全部一致，EXIT 0 |
| bootstrap seam | `test_detector_assembly.py` included in CPU/GPU focus | 真实 `assemble_services` 注入 detector；缺权重为 `PROVIDER_NOT_CONFIGURED`，不创建 Region；PASS |
| seam/source safety | 22 项 seam included in CPU/GPU focus | 22 项自动化检查 PASS；合成源文件/Managed Copy hash 保持不变 |

作者提交的真实漫画 169 页 CPU/GPU 结果 JSON 已核对文件 SHA：
CPU `660d7aed...690a6c`、GPU `df1f18a8...d97fa9`；该批跑未在本轮再次执行，
因此作为作者证据而非本报告 fresh run。R2 §1 的权重字节数更正已由本地文件
复测确认。

## Export 失败归属

作者记录的 `4a1ed6ca` base 对照与本次基线 venv fresh run 均指向
`tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history`。
R2 diff 的路径集合没有 `tests/reading_export/**` 或 export VM；失败时
`running=False`、完成状态和 history 已更新，只有 `exportFinished` 列表为空。
因此裁决为既有 export/Qt 信号投递竞态，进入独立修复窗口；不把它伪装成
T1.1.1 绿灯，也不把它升级为 T1.1.1 blocker。

## 结论与集成门

`2f116a2` **APPROVED FOR CODEX INTEGRATION WINDOW**。

批准只针对固定 base/head 的 R2 review，不等于已集成或已完成产品验证。当前
master 产品代码仍停留在 T1.1.2 集成状态；Codex 需按 Rebaseline Plan 单独执行
串行集成、集成后 fresh verification，并由 Codex 记录 integration commit。ZCode
不得自行合并。
