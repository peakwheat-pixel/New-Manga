# SETTINGS-OPEN-B-1 独立 Review r3（M2/M3/m1/m2 复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`d263c8e74a825c6ec20782f39b70eb6a8390c80b`**（实际 HEAD；`f0a8aa0` 后仅 core-report hash 刷新，docs-only）
- 修复链：`b521ad27`（M3 非 GPU preference）→ `a5bdb30`（clean evidence，B-2 GUI smoke）→ `f0a8aa0`（evidence commit pin）→ `d263c8e74`（core-report hash）
- 代码交付头：`b521ad27`；Task `delivery_head` / `integration_commit` 均为 `b521ad27`；Task `canonical_evidence_status: pending`（待本轮 Review 后关闭，见 P2）
- 审查方式：读完整 diff；独立 probe M3/B1/m1；在无 B-2 WIP 的 clean 工作树/commit 上跑 clean 验收；检查 Task/Handoff/core-report/design/UI 与 evidence pins。

## 结论

**approved**（代码与 clean 验收可交付；以下 **P2** 不阻塞集成，但建议在 Task 关闭前修正，尤其 P2-1/P2-2）。

## 1. AC 状态

| AC | 状态 | 说明 |
|---|---|---|
| AC1 Core 写入校验 | PASS | 未在 r3 变更；60 个 settings tests 全绿 |
| AC2 模型/GPU 消费点 | PASS（M3 行为已修） | 仅 `requires_gpu=True` provider 应用偏好；非 GPU provider 保持 auto；B1 descriptor 来源仍成立 |
| AC3 任务/重试 | PASS | 未在 r3 变更；m1 guard 保持 |
| AC4 前端 | PASS | clean `npm` **41 files / 406 tests**、tsc 0；B-1 自身 39/387 未回退 |
| AC5 证据 | PASS（clean 数字） | clean acceptance **1253/3**、clean full **2585/3** 与用户声明一致；结构 pins `check.ps1` PASS |

## 2. Findings

### P2-1（文件一致性）— Handoff 测试表仍是旧计数，Task 运行记录也未同步

- `doc/handoffs/SETTINGS-OPEN-B-1-7d19164.md:26-27` 仍写 **1212 passed / 3 skipped**、**2544 passed / 3 failed**；同一 Handoff 的 §Review（`:51`）已写 clean **1253 / 2585**，自相矛盾。
- `doc/tasks/SETTINGS-OPEN-B-1.md:85` 的"Lead 独立验证"仍写 **1212 / 3**；同 Task 的测试表 `:69,:72` 已更新为 **1253 / 2585**。
- 影响：用户 r3 要求"Task 测试表/Handoff 计数统一为 clean 数字"，Task 表已统一但 Handoff/运行记录未统一；后续 Owner 读 Handoff 会得到旧口径。
- 建议：把 Handoff 测试表和 Task `:85` 改为 clean 数字，并明确旧 1212/2544 是 B-1 before 口径（或删除旧行）。

### P2-2（规格/文档同步）— M3 的 `requires_gpu` 限定未写入设计 §4.1/UI 说明，core-report 仍有旧观察

- M3 实现（`src/infrastructure/providers/handlers.py:974-980`）在 `not requires_gpu` 时把 `preferred_device` 置 `None`；这是新语义。
- 但 `doc/design/SETTINGS_SECTION_SCHEMAS.md:105` 仍写"Run 执行时由 handlers 的 heavy_runner 读取 Run 快照……cpu/gpu 显式时经 `DeviceManager.plan` 校验"，没有限定"仅 `requires_gpu=True` 的 provider"；UI 同款说明 `apps/desktop/frontend/src/settings/sections.ts:553-554` 也未提非 GPU provider 忽略偏好。
- `verification/SETTINGS-OPEN-B-1/core-report.md:251` 仍保留"远程 translate 选 gpu 会 DeviceUnavailable，需裁决"的旧观察；§8.5 已不再成立。`core-report.md:255` 与 `:261` 还出现两个 `## 9` 标题。
- 影响：实现与冻结的 §4.1 文字不一致；后续 Owner 可能重新引入 M3。非代码 blocker，但应在 Task 关闭前同步设计/UI 措辞（"偏好仅作用于声明 `requires_gpu=True` 的 provider；CPU-only/远程 provider 保持 auto"）。

### P2-3（证据 hash 口径）— canonical sha256 是工作区 CRLF 字节，不是 commit blob

- B-1 Task canonical 表中文本日志的 sha256 与**工作区文件**一致（例如 `core-pytest-clean-acceptance-raw.txt`：worktree `c2313387...`），但与 `git show a5bdb30:verification/.../core-pytest-clean-acceptance-raw.txt` 的 blob 哈希 `7ac4075e...` 不同；16/19 个 B-1 文本 evidence 项存在此差异（B-2 侧同样 8/14）。
- `check.ps1` 同时接受 worktree hash 与 blob hash（`check.ps1:365-375`），所以本地 PASS；但用 `git archive`/autocrlf=false 的 clean 快照复核时，按 Task 表 hash 会不匹配，削弱"clean 证据可复现"。
- 建议：统一约定（优先 pin Git blob hash；或为 evidence 目录加 `.gitattributes -text` 固化行尾）；至少在本 Task 记录该口径，避免再次出现 r2 式证据争议。

## 3. 独立验证的 r3 修复

### M3（非 GPU provider 忽略偏好）

- 代码：`handlers.py:974-980`，`if not requires_gpu: preferred_device = None`；M3 只在通过 descriptor（或 descriptor 缺失时实例属性）得到 `requires_gpu=False` 时生效。
- 独立 probe（真实 `ProviderRegistry`/`ProductionHandlers`/`ProviderRuntime`/`DeviceManager`，GPU 不可用、`device_preference=gpu`、`allow_cpu_fallback=true`）：
  ```text
  remote translate descriptor requires_gpu=False -> executed, preferred_device=None（不再 DeviceUnavailable）
  local OCR descriptor requires_gpu=False        -> executed, preferred_device=None
  gpu provider descriptor requires_gpu=True      -> 仍走偏好路径（allow=true 时回退执行；allow=false 时 DeviceUnavailable）
  ```
- 测试：`test_non_gpu_provider_ignores_the_device_preference` 断言 forwarded `preferred_device is None`、`requires_gpu is False`；OCR 端到端断言已改为 `None`。clean 测试全绿。
- 结论：**r2 M3 的代码边界已修**；不再因用户选 gpu 让远程 translation/vision OCR 失败。

### B1 / m1（复述确认，未回退）

- descriptor 来源、alias、真实 DeviceManager 回退/拒绝、OCR 端到端在 r3 clean 树仍通过；`_section` 非 Mapping guard 及 4 参数化测试仍通过。r2 的 B1/m1 结论继续有效。

## 4. 独立测试原始结果（HEAD `d263c8e74`，工作区仅 P04 未跟踪诊断文件）

| 命令 | 结果 | 证据 |
|---|---|---|
| `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | **1253 passed, 3 skipped, 1 warning in 48.03s，EXIT 0** | clean raw `core-pytest-clean-acceptance-raw.txt` 同计数 |
| `python -m pytest tests -q` | **3 failed, 2585 passed, 9 skipped, 2 warnings in 172.25s**；3 failed = 2 个 `test_detection_manga_real` 环境失败 + 1 个既有 `test_workbench_viewmodel` 基线失败 | `core-pytest-clean-full-raw.txt` 同计数 |
| `npm --prefix apps/desktop/frontend test` | **41 files / 406 tests passed，EXIT 0**（B-1 自身 39/387，B-2 加入 2 files/19 tests） | clean HEAD |
| `tsc --noEmit` | exit 0 | — |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (2 warnings)**：3 个非终态 Task、STATUS 80% 预算 | 本地 HEAD |
| clean archive `b521ad27` 计数 | 1253/2585（与上述一致） | Lead clean raw + 本次重跑 |

- 未跑：GUI 烟测（B-1 面板；本轮 B-2 GUI 已做，但 B-1 自身仍 NOT_RUN）、真实 GPU 端到端（无 GPU/torch）。二者均无 r3 代码改动影响。

## 5. 范围核对

- r3 修复范围：`b521ad27` 仅 `handlers.py` + `tests/providers/test_handlers_b1_settings.py`；`a5bdb30` 为证据/Task/Handoff/Plan/Status/B-2 GUI 文档；`f0a8aa0`/`d263c8e74` 仅 Task pins/core-report hash。无越界产品改动。
- `Task` canonical 19 行、`delivery_head=b521ad27`、`integration_commit=b521ad27`；`check.ps1` PASS；`review-b1-r3.md` 为本轮新增，应随 Review 回填 Task/Evidence。
- B-2 已登记独立 Task；本轮只做 B-1 r3，未把 B-2 产品代码作为 B-1 结论依据。

## 推荐下一步

1. 修正 P2-1（Handoff/Task 运行记录 clean 计数）、P2-2（设计 §4.1/UI 文案的 `requires_gpu` 限定、core-report 旧观察/重复 §9）。
2. 若接受 P2-3 的行尾/hash 口径，在 Task 记录并在下一轮证据重录时统一；不阻塞代码集成。
3. 之后可关闭 B-1；B-2 另按 [review-b2.md](../SETTINGS-OPEN-B-2/review-b2.md) 处理。
