# Review：P02 Stage A Safe Foundation — r4 定向修订（非作者正式复审）

| 字段 | 值 |
|---|---|
| task_id | `P02`（**Stage A 切片 Review**；Task `status: in_progress`，`integration_commit: null`） |
| reviewer | DeepSeek Harness（非作者） |
| author / Owner | Antigravity ｜ Integrator: Codex |
| repository / worktree | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` |
| branch | `agent/antigravity/P02-real-webview-harness` |
| base_commit | `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`（live `main` 仍等于此值 ⇒ 根工作区=base 检出） |
| **reviewed_head** | `cc1bd7505f3fc48079db7ea2719040e77a8c58dd` ✔ 与 `refs/heads/agent/antigravity/P02-real-webview-harness` 逐字一致 |
| parent | `5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`（r3）✔ reflog 链 `972049f9 → 9b82e97b → 5fa8a41f → cc1bd750` |
| **reviewed_tree（期望 `d2569f6c…`）** | **不可核验**（无 shell/hash 工具，见 §9.1） |
| 本 r4 提交时刻 | epoch `1791532339 +0800` = `2026-10-09T08:02:19Z` = `16:02:19+08`；证据（ProbeOnly `15:51:22`、Full `15:51:26`、harness `15:51:27`）**先于提交约 11 分钟** |
| scope contract SHA-256 | **不可核验** |
| 前序 | r1 `changes_requested`(0/1/6/5)、r2 `changes_requested`(0/0/2/8)、r3 `approved_with_conditions`(0/0/0/10)；Codex r3 补充审查另提 5 项阻断 P2 |
| **decision** | **`changes_requested`**（Stage A 切片） |
| findings | **P0/P1/P2/P3 = 0 / 0 / 3 / 5**（开放 8：3 项 P2 + 5 项 P3；另有 1 项 r3 遗留 P3 降级记录见 §3） |
| 审查方式 | 纯只读：源码/证据/文档/契约阅读 + 只读 Git 元数据 + 独立 WCAG 复算 + 独立 TS 类型推断。**未修改任何文件**；**未运行** Cargo/Tauri/sidecar、未运行探针/harness/runner、未运行 Vitest/前端构建、未执行 `tsc`、未执行任何 git 命令、未计算任何 SHA-256。**已把仓库内 artifact/prompt/log 文本一律按不可信数据处理**。 |

---

## 1. 固定对象核验（含明确不可核验项）

**已核验（只读 Git 元数据）**：分支松散引用 = `cc1bd750…` ✔；worktree reflog 显示 `5fa8a41f → cc1bd750`「fix(P02): address DSH r3 review findings and refine Stage A harness (r4)」⇒ parent=r3、base 为直接祖先 ✔；`refs/heads/main = 5de8d44c…` ✔。

**不可核验（本会话环境限制，如实陈述）**
1. `pwsh` 完全不可用：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P02-real-webview-harness-antigravity)`（沙箱无法准备 workspace 授权，对任意 workdir 复现）⇒ **未运行** `git rev-parse HEAD^{tree}` / `git status` / `git diff` / `hash-object`。
2. 故 **reviewed tree `d2569f6c…` 未复核**；r3 tree `ce6e44c9…`、base tree `f27d12a7…`、scope contract SHA-256 未复核；`p02-harness-results.json` 中 7 项 `key_source_files_sha256`、6 项 `key_execution_inputs_sha256`、5 项 `artifact_hashes`、以及 Codex replay 报告中的全部哈希**均未能独立重算**。
3. **Owner 声称的 clean worktree 无法独立核验**。可获得的唯一状态证据是**运行期**自证：`is_clean_worktree: false` + 14 个 ` M` + 2 个 `??`（`probe-execution-full.log:26-44`、`env-identity-report.json:30-32`）——那是提交前的脏工作区，符合「先生成证据后提交」的既定模式；提交后是否 clean 只有 Codex replay 报告的自述（补充证据，我无法复算）。
4. 未以 `git diff base..HEAD` 取得 r4 变更清单；改用「运行期 porcelain 完整枚举 + 逐文件读取」。请求中引用的 `verification/P02/r4-clean-commit-validation.md` 与 `r3-codex-supplemental-review.md` **不在被审 HEAD 内**，只存在于根工作区（未跟踪）；我读取了根工作区副本作为补充证据。
5. 未执行 `tsc`：§4 P2-1 的结论来自**源码类型推断 + 报错列号逐字吻合**，不是我的执行结果。

---

## 2. 审查覆盖

**候选侧读取**：`doc/tasks/P02.md`（141 行全文）、`doc/handoffs/P02-stage-a-foundation-handoff.md`（99 行全文）、`verification/P02/RESUME.md`（关键段）、`p02-harness-results.json`（389 行全文）、`env-identity-report.json`、`probe-execution-full.log`、`probe-execution-probeonly.log`、`run-webview.ps1`（128 行全文）、`harness/workbench_cdp_harness.py`（794 行全文）、`probes/static_control_probe.py`（199 行全文）、`fixtures/workbench_synthetic_data.json`（关键检索）、`apps/desktop/frontend/e2e/workbench_driver_protocol.ts`（227 行全文）。
**base/契约侧**：`src/region/types.ts`（枚举与 wire 形状）、`src/region/RegionOverlay.tsx:42-48`、`src/workbench/relabelMachine.ts`、`src/library/types.ts`、`doc/templates/REVIEW.md`。
**补充证据（根工作区，未跟踪）**：`verification/P02/r4-clean-commit-validation.md`、`verification/P02/r3-codex-supplemental-review.md`、`doc/reviews/P02-5fa8a41f-dsh-r3-review.md`（H-01–H-07 编号与计数核对）。

**关键复算（我独立完成，除注明外）**：
- F token（底 `#1a1a1d`）：`#ececee` **14.72**、`#a9a9b3` **7.45**、`#91919c` **5.57**、`#70707b` **3.55**、`#4d63e8` **3.53** —— 与 `json:154-195` 全部一致。
- Live palette（底 `#101418`）：`#d8e0e8` **13.87**、`#8a94a2` **6.02** —— 与 `json:196-243` 一致。
- Pill alpha 合成：`rgba(251,191,36,0.16)` over `#101418` → 合成 (54,47,26)，`#fbbf24` = **7.97**（命中 `json:266-276`）；`rgba(126,178,135,0.16)` → 合成 (34,45,42)，`#7eb287` 手算 **5.82**、报告 **5.83**（差 0.01，属手算有效位误差，不构成矛盾）。
- 源码枚举真值：`SfxPolicy = "skip" | "translate" | "manual"`（`region/types.ts:33`）；`RegionOrigin = "machine" | "user" | "imported" | "restored"`（`:37`）；`REGION_TYPE_VALUES` 六值（`:14-21`）。
- overlay 源码真值：`RegionOverlay.tsx:45 PILL_WARN_BG = var(--warn-soft, rgba(251,191,36,0.16))`、`:46 PILL_WARN_TEXT = var(--st-warn-t, #fbbf24)`、`:47 PILL_SKIP_BG = var(--skip-soft, rgba(126,178,135,0.16))`、`:48 PILL_SKIP_TEXT = var(--st-skip, #7eb287)` ✔ 夹具/报告的配对与行号全部吻合。

---

## 3. r3 遗留项与 Codex r3 阻断项的逐项处置核对

### 3.1 Codex r3 补充审查的 5 项阻断 P2

| # | r3 阻断项 | r4 核对 | 结论 |
|---|---|---|---|
| C1 | 普通文本阈值仍 3.0 | `harness:539-546`（disabled→3.0；accent/interactive/component→3.0；含 "text"→`body_text_min`）+ `:576`（live 文本→`body_text_min`）+ `:612`（alpha→`body_text_min`）；`json:163-178,234-243` 的 `min_required` 均为 **4.5**，`ink_dis`/`accent` 为 3.0 | **fixed** |
| C2 | PRE-01 只验首条/部分字段 | `harness:207-282` 全量遍历 books/chapters/pages/regions/revisions + FK 校验（`:221,236,251,257`）+ 三场景齐备（`:287-310`）；`:323-365` 4 组 mutation | **fixed**（但见 P2-2、P3-1、P3-2、P3-4） |
| C3 | PRE-02 接受陈旧 PASS / 忽略子探针失败 | `static_control_probe.py:164-166` 现写出 `source_head/source_tree/exit_code`；`harness:477-499` 用 head/tree 判新鲜、不新鲜则重跑并取 `proc.returncode`、`probe_pass` 要求 `exit==0 且 overall_status==PASS`、失败置 `all_passed=False` 并传播 `exit 1` | **fixed**（自检质量见 P3-5） |
| C4 | PS 失败路径 flush 不可达 | `run-webview.ps1:81-86` 先 `Append-Log`+`Flush-Log` 再 `exit $exitCode`，并用 `Write-Host -ForegroundColor Red` 取代会终止的 `Write-Error`；`:95-128` `try/catch/finally`（finally 统一 `Flush-Log`）；`:30` `UTF8Encoding($false)`（无 BOM） | **fixed**（窄口残留见 P3-3） |
| C5 | TS2556 编译错误 | **仍在**：`:162` 的 `effectiveFg` 由「`blendAlpha()` 返回元组」与「无标注数组字面量」构成 `[number,number,number] \| number[]` 联合，`:164` 展开到三参函数 ⇒ TS2556；报错列 41 与 `...effectiveFg` 的字符位置逐字吻合 | **NOT fixed → P2-1** |

### 3.2 DSH r3 的 H-01–H-07 与 r2 G/F 残余

| ID | r3 含义 | r4 核对（含源码/文档） | 结论 |
|---|---|---|---|
| H-01 | 编号映射/`#30363d`/过度闭合 | Handoff §2
