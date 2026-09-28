# Handoff — M2-AC3 Provider Fail-closed Acceptance

- Owner: ZCode（本会话亲自实现，用户授权 2026-09-28）
- Task: `doc/tasks/M2-AC3.md`（`ready / M2_AC3_PROVIDER_FAIL_CLOSED_RELEASED`；纯验收，产品代码零改动）
- Base / release: `319c5e4b` / `7e88de4b`
- Branch / worktree: `agent/zcode/M2-AC3-provider-fail-closed` / `G:/CODEX/New Manga.worktrees/M2-AC3-zcode`
- Head ledger: claim=`c754e714` → 实现=`b0112834` → evidence/handoff=交付 tip（Owner 分支 HEAD）= `a63d3372ebbd364da9fb5fb53af835559235bb6c`（「集成方补充」：DSH r1 条件 C2，tip hash 落地）
- Status: delivered（等 DeepSeek Harness 非作者 Review；Integrator=新会话代行 Codex，保持 Owner≠Integrator）

## 交付物

| 文件 | 说明 |
|---|---|
| `tests/m2_acceptance/test_provider_fail_closed.py` | 新增验收模块，8 场景覆盖 AC1–AC5（零配置/无 binding/悬空 binding、网络失败、部分失败、源文件零风险、重装配真相保持、修复后重试无残留） |
| `verification/M2-AC3/verification-results.md` | 主证据：两级 pytest 日志、场景→AC 判定表、范围核查、NOT_RUN 单列 |
| `verification/M2-AC3/raw/pytest-provider-fail-closed-v.log` | 新套件 `-v` 原始输出（8 passed, EXIT=0，头部含 shell/解释器/固定 HEAD） |
| `verification/M2-AC3/raw/pytest-m2-acceptance-regression.log` | 回归原始输出（23 passed = 既有 15 + 新增 8，EXIT=0） |
| `verification/M2-AC3/raw/git-diff-check.log` | `git diff --check 319c5e4b..b0112834` EXIT=0 实测 |
| `verification/M2-AC3/discrimination-mutations.md` | 判别力先红记录（M1 吞失败状态、M2 typed code 替换 generic，均红 + 还原零残留），含 Reviewer 独立复放命令 |
| `doc/tasks/M2-AC3.md` | AC 判定回填、测试矩阵 executed、状态推进 in_review / DELIVERED_FOR_REVIEW |

## AC 判定表（全部实测，细节见 Task 与 verification-results.md）

| AC | 判定 | 要点 |
|---|---|---|
| AC1 未配置 fail-closed | **PASS**（3 场景） | 零配置 detect 缺口 / 无 binding / 悬空 binding 三条 fail-closed 路径，typed code + 可区分 detail，零半成品（Region/candidate/revision/managed 文件四断言） |
| AC2 网络失败 + 既有成果保护 | **PASS**（1 场景） | typed `PROVIDER_TIMEOUT`；人工译文、translation lock、manual_edited、pinned revision、revision 计数、current 指针全部原样 |
| AC3 部分失败边界如实 | **PASS**（1 场景） | 双页 A 成功/B 失败 → `COMPLETED_WITH_FAILURES`，task 边界可查询，A 成果完整可用（+1 revision 且 current 在其上），B 零伪造成果、typed detail 按页可诊断 |
| AC4 源文件零风险 | **PASS**（1 场景） | 连续两个失败 run 后源 bytes/size/mtime_ns/目录不变，managed copy 逐字节等于源 |
| AC5 可恢复 | **PASS**（2 场景） | 重装配后 typed 失败状态持久可查询；binding 修复重试 `COMPLETED`、旧 run 不复活、revision `[1,2]` 连续无重复无悬空 |
| AC6 证据纪律 | **PASS** | 两级 pytest EXIT=0、diff-check EXIT=0、mutation 先红留痕、NOT_RUN 单列 |

## 验证命令（worktree 根目录，$py=TASK-012-py312）

1. `$py -m pytest tests/m2_acceptance/test_provider_fail_closed.py -v` → **8 passed**，EXIT=0
2. `$py -m pytest tests/m2_acceptance -q` → **23 passed**（M2-AC1 4 + M2-AC2 11 + 本模块 8，零回归），EXIT=0
3. `git diff --check 319c5e4b..b0112834` → EXIT=0（交付 tip 全区间由集成方以同一命令复跑为准）

环境：Windows 11 x64 · Git Bash · Python 3.12.3 · pytest 9.1.1；0 skipped；无环境性 skip。

## 实现过程中的语义发现（供 Reviewer 重点核对）

1. **AC1 的三条未配置路径落两个不同 typed 槽位**：无 binding 在 handler `_chain` 直接抛 `ProviderNotConfigured`（`no provider binding configured for step 'ocr'`）；binding 指向未注册 id 在 `registry.resolve` 抛 `ProviderUnavailable`（`no provider registered as '<id>'`，retryable → 有界重试 3 次后 re-raise）；真实权重缺失（docTR `_build_engine` 零依赖前置检查）回到 `ProviderNotConfigured`。三个 detail 互不相同，满足"能区分'未配置'与其他失败"。Task AC1 措辞已按实测覆盖两种 code。
2. **失败注入手法**：按装配 adapter-injection 先例（M2-AC1/M2-AC2），fixture provider 经 production `registry.register` 注册（`m2ac3-*` id，仅测试文件内定义），binding 走持久化 `pipeline_defaults` 通道——与真实 provider binding 同一条 production 路径，不走 test-mode bridge、不扩 IPC 面。
3. **typed code 传递链**：handler `_typed` 把 `ProviderError.error_code` 经 `StepExecutionError` 带过 seam，`_fail_step` 落到 `step_run.error_code`/`task.error_code`；generic `Exception` 会塌缩为 `STEP_FAILED`——mutation M2 证明套件对该塌缩敏感。
4. **AC4 场景的 payload 必须是真实可解码 PNG**（`synthetic_page_png`）：binding 存在时 `handle_ocr` 在 provider 调用前执行 production `region_crop`，非 PNG 字节会先触发 `INVALID_INPUT` 而非目标 typed 错误（开发期实测发现，已修正）。
5. **零配置 detect 场景加了 `NEWMANGA_DETECTOR_WEIGHTS` 环境守卫**（monkeypatch.delenv）：防止宿主环境变量把权重缺口移出场景。

## NOT_RUN / BLOCKED

- **Qt/WebView2 读面的错误呈现**：NOT_RUN——headless 验收装配不可达（与 M2-AC2 Qt provider 读面 NOT_RUN 同因），登记为后续 E2E slice 输入。Core 层"页/run 状态如实"已按持久状态断言 PASS。
- 其余无 FAIL / BLOCKED；验收全绿。

## 风险 / 遗留

- 无新增遗留。`tests/m2_acceptance/` 既有两套件行为未触碰（回归 23 passed 实证）。
- 判别力 mutation 为临时本地改动，已还原（`git status --porcelain src/` = 0），Reviewer 可按 `verification/M2-AC3/discrimination-mutations.md` 独立复放。

## 启动 / 复现方式

```bash
cd "G:/CODEX/New Manga.worktrees/M2-AC3-zcode"
git checkout agent/zcode/M2-AC3-provider-fail-closed   # tip = delivery head
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance/test_provider_fail_closed.py -v
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q
```

## 下一接收者

DeepSeek Harness（非作者 Review）。Review 输入：本 Handoff、Task AC 表、`verification/M2-AC3/**`、Owner 分支 tip。Review 通过后由 Integrator（新会话代行 Codex）集成：复跑验证命令、核对 allowed paths（`tests/m2_acceptance/` 新增文件、`doc/tasks/M2-AC3.md`、`verification/M2-AC3/**`、`doc/handoffs/M2-AC3-*.md`；禁改 `src/**`、`apps/**`、`doc/contracts/**`、既有验收套件行为）、merge 进 main、置 `done` 并回填 `delivery_head`/`integration_merge`。
