# 全量测试 9 个失败的处置裁定（r42）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
范围：B 类环境假设测试、A 类检测运行环境、C1 类 P11 投影测试。  
依据：`verification/PDF-STREAM-FIX-1/full-suite-failure-classification.md`、P11 §4.2 / §4.5、指定源码与当前 `requirements.txt`。  
本裁定文件不改写源证据；本次授权仅写入此文件。

## 裁定摘要

| 项目 | 裁定 |
|---|---|
| B 类 4 个依赖机器状态的测试 | **选择 3.1 A：建立有界治理 Task 并纳入 Plan 后激活，修正测试，不改 `src/`。** 本文件本身不改变 Plan、Task 或 STATUS，也不授权在任务释放前实施。 |
| B 类覆盖方式 | 测试须显式覆盖运行时存在与不存在两侧。优先隔离环境探测、确定性模拟两种前提；单机真实环境探测只断言实际报告与实际能力一致。不得把期望值改成当前机器状态。 |
| A 类 transformers 失败 | **建立独立环境恢复 Task。** 当前检测链路在本机无法完成真实模型加载，属于已观察到的功能不可用/环境不符合项目依赖基线；尚不能据此判定加载正确环境后的产品行为。 |
| C1 两个 Pending/pause 测试 | **应更新测试以符合 P11 §4.5。** 它们不是应保持旧断言的历史证据；Git 历史保留旧行为来源。另立有界测试契约对齐 Task，不并入 B 类 Task。 |
| C2 旧 PySide6 viewmodel 测试 | 不释放旧栈修复 Task。其 continue 后未完成的结果不能归因到新架构；也不能作为共享 PipelineService 已无缺陷的证明。 |
| Plan / Task 权威状态 | Plan 当前无 READY 节点。新增工作须经 Plan 登记、依赖与范围冻结、STATUS 登记及正常 Task 释放；本裁定没有替代这些步骤。 |

## 一、证据与边界

失败分类报告记录 9 项失败：2 项模型检测真实测试、4 项可选运行时/设备状态断言、2 项 projection 按钮断言、1 项旧 Qt viewmodel 测试。报告记录本机有 `manga-ocr`、CUDA 可用，且 `transformers 4.48.3` 缺少权重要求的 `RTDetrV2ForObjectDetection`。本次只读核对了报告、P11、投影与检测加载源码，以及项目根目录 `requirements.txt`；该报告所引用的权重目录不在本次读取的仓库相对路径下，权重内容依据报告所引 config 记录，不声称本次重新读取了该外部文件。

`src/application/tasks/projection.py` 对 `PENDING` 返回仅含 `can_stop=True` 的投影；P11 §4.5 明确要求 Pending 拒绝 pause。两者一致，现有两个测试仍要求 pause 可用，属于测试与契约不一致。

`src/infrastructure/providers/detection_manga.py` 使用权重声明对应的 `RTDetrV2ForObjectDetection`。项目 `requirements.txt` 将 `transformers` 固定为 `5.17.0`（并列出 `torch==2.14.0`、`safetensors==0.8.0`）；本机报告中的 `4.48.3` 不仅低于模型类所需版本，也不符合项目固定依赖。报告记录的真实模型加载失败意味着**本机当前检测链路不可用**；失败发生在模型加载阶段，不能宣称检测质量/推理 AC 已通过，也不能仅凭这一环境失败断言正确依赖环境下的实现有缺陷。

## 二、B 类裁定：环境假设从测试中移除

建议 Task ID：`TEST-ENV-ASSUMPTIONS-1`。范围仅限以下四项测试与必要的测试 fixture：

- `test_production_stack_starts_without_heavy_runtimes`
- `test_real_environment_reports_optional_providers_as_not_ready`
- `test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented`
- `test_cpu_fallback_only_when_the_provider_declares_it`

不得修改 `src/**`、产品依赖声明、Provider 就绪规则或设备选择语义。

### 验收标准

1. 无 manga-ocr / 无可用 CUDA 的模拟场景下，断言 Provider 如实报告缺依赖、GPU 如实报告不可用；声明支持 CPU fallback 时选择 CPU 并记录 fallback provenance，不支持时保持拒绝行为。
2. manga-ocr 可用 / CUDA 可用的模拟场景下，断言 Provider 与 GPU 如实报告可用。测试不能因为当前宿主机安装了可选依赖而变红。
3. 所有受影响逻辑的两侧均由确定性测试覆盖，不能把关键分支只留给另一台“裸机”碰巧覆盖。可以通过 monkeypatch、注入探测器或等价测试 seam 构造能力状态；不要为此新增生产接口。
4. 如保留真实环境集成断言，只验证探测报告与当前探测事实一致。若该集成断言针对本机不可达路径而 skip，必须说明该 skip 只表示该环境无法触发该路径；两侧逻辑仍须由第 1、2 项的确定性测试实际执行。不得用 skip 代替分支覆盖。
5. 验证记录明确区分 pass、skip、失败；在有可选依赖的开发机与无可选依赖的环境均可运行，不要求本机伪装卸载依赖。

## 三、A 类裁定：检测链路运行环境恢复

建议单独建立环境 Task（例如 `M2-PROD-DETECT-ENV-1`），不得把它记作代码测试修复或产品验收通过。工作重点是找出当前执行环境为何与已固定依赖不一致，并在隔离、可复现的环境中恢复检测能力；不能为迁就旧运行时把 V2 模型类改成 V1 类，也不能只改测试断言。

### 验收标准建议

1. 记录执行环境、Python 版本、实际安装包版本及安装来源；环境满足项目声明的模型栈基线，至少核对 `requirements.txt` 中的 `transformers==5.17.0`、`torch==2.14.0`、`safetensors==0.8.0`，并解决与当前实际平台/锁定基线的兼容性。
2. 在不联网下载权重的前提下，确认实际本地权重目录及其 config 与受测代码使用同一模型快照；从该本地快照成功构造模型及 processor。
3. 在该隔离环境执行两个真实检测用例（候选检测与空白页零候选），逐项记录实际结果。若环境/权重无法满足，AC 标为 BLOCKED 或 NOT_RUN 并保留日志，不得报告检测链路可用。
4. 明确环境修复落点（隔离 venv、Task 环境或 CI 环境）及复现方式；不以升级全局 Python 环境作为默认操作。

有网络的兼容机器可以执行安装/重建，但“在有网络机器上升级并复跑”应纳入环境 Task 的 AC 和证据，不是无记录的运维口头动作。该 Task 不需要修改模型实现；若按项目锁定依赖仍无法加载权重或真实用例失败，再以新证据另行判断是否需要代码 Task。

### 修复前声明口径

应表述为：**“检测实现与权重预期使用 RT-DETR-v2；当前本机运行环境 transformers 版本不符合项目固定依赖，两个真实检测用例未通过，本机 manga 检测链路目前不可用，尚未验证正确环境下的真实推理结果。”**

不得将其简写为“9 个旧测试红”或“检测链路已可用”。也不应把当前加载前置条件失败称为已证明的检测算法缺陷。

## 四、C1 裁定：更新过期的投影测试

建议单独建立 `P11-PROJECTION-TEST-ALIGN-1`（或等价 Plan Task），仅修改两个与 P11 §4.5 冲突的 projection 测试及必要断言：

- `test_pending_run_all_waiting_and_pause_stop_enabled`
- `test_button_matrix_all_statuses`

验收至少包括：Pending 的 `can_pause=False`、`can_stop=True`；其余被测状态矩阵与 P11 §4.5 一致；无需改 `projection.py` 来迎合旧期望。TASK-013 的历史内容和提交保持历史事实，不因测试更新而改写。虽然 `tests/workbench/` 中也有旧 PySide6 测试，本项范围只涵盖对新架构仍适用的应用层 `build_projection` 测试。

## 五、未授权与下一步

本轮没有创建/修改 Task、Plan、STATUS、测试、源码、权重、依赖或既有 verification 文件；没有运行全量测试、安装依赖或执行 Git 写操作。以上 Task ID 是建议 ID，只有完成 Plan 登记、allowed paths / Owner / Reviewer / base / worktree 冻结并按协作协议释放后才可实施。

**推荐下一步：**由 Codex 在获准的治理变更中先登记并释放 `TEST-ENV-ASSUMPTIONS-1`，同时分别排期环境恢复与 P11 投影测试对齐；三项范围与证据相互独立，不应把环境阻塞或契约过期混记为 B 类完成。
