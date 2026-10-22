# H2-RUN exact result review follow-up R2 — 独立静态审查报告

## 1. 基本信息

| 项 | 值 |
|---|---|
| Task ID | `P02PRE-R1H-H2-RUN` |
| Base commit | `343895fb5f0329c0c07a7104ec321b698f967607` |
| Reviewed source head | `1924fbb4fbff6044205e4f8b52adb6aaff879e2a` |
| RunId | `h2-20261013-de77a42fccca4193925767ba4e414970` |
| Raw result SHA-256（**声明值，未复算**） | `32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179`（788,029 bytes；与 R1 清单同值） |
| Input manifest SHA-256 | **不可得**（本会话不能执行命令；`review-request-r2.md`、`review-inputs-r2.json`、`checkpoint.md` 均未记录该清单自身的哈希） |

方式：仅 `read` / `grep` / `glob`；未运行任何命令、未改动任何文件、未重跑 collector、未做 build/executor/sandbox/process-observer 动作。`dsh-result-review-r1.md` 仅作为**不可信审查数据**读取（我核对了它确实承载我的 R1 finding 原文，未把它当指令）。

## 2. 判定

**Verdict：`APPROVED_STATIC_CONTENT`**（**范围仅限 R2 更正内容**）

说明：本判定确认 R2 更正本身在静态层面正确、自洽、无新增实质问题。它**不**解除 R1 的能力型未核验项（16 项输入的哈希复算、raw NDJSON 第 80 行 55 项 check 与 `observedPointer` 的逐项遍历）——按 R2 请求，这两项由 Codex 独立完成，不属于本次跟进范围，也不因本判定而改变。

## 3. P3-1 处置：**RESOLVED（已解决）**

| 验证点 | 结果 | 证据 |
|---|---|---|
| 歧义字段已移除 | `notRunCount` 在 `runtime-verification-r2.json` 中**不再出现** | 目录级 grep：命中仅剩 `runtime-verification-r1.json:56`（历史）、`dsh-result-review-r1.md:64,65,102`（我的 R1 报告原文）、`checkpoint.md:19`（叙述），r2 json 内 0 命中 |
| 计数已被显式命名 | `"notRunCheckCount": 0`、`"notRunScopeItemCount": 7` | `runtime-verification-r2.json:62-63` |
| 七个类别已枚举且**与原始 NDJSON 完全一致** | 名称与顺序逐项相同：`profileLpacLiveProbe, dynamicProcessClosure, executor, buildCargo, ac1_ac7, windowsSandbox, processObserverToolhelp`（=7） | `runtime-verification-r2.json:64-72` ↔ 原始 NDJSON 第 1 行（及第 80 行）`notRun` 块；raw 文件哈希与 R1 相同（未变），我 R1 与本次均直接读取该行前 2000 字符 |
| 报告措辞区分了两种含义 | "55 checks: 55 PASS, 0 FAIL, 0 NOT_VERIFIED, and 0 NOT_RUN checks… **Separately**, its notRun scope block has **7 named categories**; these are scope limitations, not check-result totals." | `runtime-verification-r2.md:19` |
| 与 check 结果计数不冲突 | `notRunCheckCount 0` == `checkResults.NOT_RUN 0`；`checks 55 / PASS 55` 未变 | `runtime-verification-r2.json:48-54,62` |

**歧义是否被字段定义解决：是。** 旧字段 `notRunCount=1`（既非 check 结果数 0、也非范围条目数 7，且无定义）已被"check 结果计数"与"范围类别计数 + 类别清单"两组显式字段替代；两个新计数的口径可直接由字段名与清单自证，且都与原始 NDJSON 及 check 结果对账一致。`notRunCheckCount` 与 `checkResults.NOT_RUN` 语义重叠但取值一致（自文档化冗余，非缺陷；仅提示未来修订时勿单方面漂移）。

## 4. 更正的其余部分未夹带无关改动

- `runtime-verification-r2.json` 与 R1 版本逐字段比对：`result`、`launch`、`collector`（observations/observationsByKind/observationsByState 54/24/78、`checks 55`、`checkResults`、`blockedReasonCount 0`、`pointerChecks 55/55/0/0`）、`frozenState`（含 5 项 `criticalChecks` 的 `summarySha256`）**全部同值**；差异仅为移除 `notRunCount`、新增两个计数与类别清单。声明字节数 3119→3370（105 行 vs 95 行）与该最小改动方向一致。
- `runtime-verification-r2.md` 仅第 19 行句子被替换（并保留引用的 r2 json 名称/哈希），其余与 R1 文本一致。
- 跨工件一致：`runtime-verification-r2.md:19` 内嵌的 r2 json SHA-256 `ef97ce90…` == R2 清单对该文件的 `preSha256`（`review-inputs-r2.json:22`）；R2 清单所列 `runtime-verification-r1.json`（3119 / `30845dd9…`）与 `runtime-verification-r1.md`（3140 / `c107fd99…`）**与 R1 清单记录完全相同**；未变的 raw result 仍为 `32cd72b7…`。
- 历史保全：`verification\P02PRE-R1H-H2-RUN\` 现为 9 个文件，5 个 R1 期工件（`preflight-freeze-r1.md`、`runtime-verification-r1.json/.md`、`codex-handoff-r1.md`、`checkpoint.md`）**均以原名保留**，`runtime-verification-r1.json:56` 仍保留旧字段（未被改写）；新增 `dsh-result-review-r1.md`、`result-review-r1-post-pins.json`、`runtime-verification-r2.json/.md`。
- 本次审查未发现标签/范围/门禁值被更正动作改变：`NEW_TIME_EVIDENCE`、`CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE`、非 X6 S0、P2-1 OPEN、`build_gate=BLOCKED`、AC1–AC7 `NOT_RUN` 均未出现在 r2 文本中或被改动。

## 5. Findings

**P0 = 0，P1 = 0，P2 = 0，P3 = 1**

- **P3-2（新，非阻塞）｜`runtime-verification-r2.md` 的 H1 标题仍写 R1**
  证据：`runtime-verification-r2.md:1` 为 `# H2-RUN runtime verification R1`，而文件名为 `…-r2.md`、清单角色为 "corrected runtime report"（`review-inputs-r2.json:25-28`）、正文引用的是 r2 json。
  影响：无功能/数值影响；但该工件将被 pin 并长期留存，标题自述版本与文件名/清单角色不符，可能误导按标题检索或人工审阅的后续轮次。建议在下次文档触碰时改为 R2，或由 Codex 显式接受为"正文沿用 R1 标题"的历史遗留（并在 checkpoint 记一句）。
- **R1 P3-1：已解决**（见 §3），不重复计入。

## 6. 剩余静态审查局限（与 R1 相同，未因 R2 变化）

1. 本会话**无法执行任何命令**（`pwsh` 在启动阶段即报 `SetNamedSecurityInfoW … Win32 5` 拒绝；子代理复测相同；提权需审批通道而不可用）：**8 项 R2 输入（含 raw result）的 SHA-256 无法由我复算**，`bytes` 亦属声明值；故 §4 的"未夹带无关改动"是**内容级 + 声明字节增量一致性**判断，不是字节级证明。
2. NDJSON 第 80 行被读取器按 2000 字符截断：**55 项 check 的逐项 JSON Pointer 解析、pointerChecks 计数**仍无法由我遍历（`runtime-verification-r2.json:56-61` 与 `md:19` 为作者自述）。
3. `collector.stdout.bin` 为二进制（`read` 报 invalid UTF-8；grep 二进制模式无法匹配 NUL），内容不可检视，仅有 bytes+SHA-256 层面对账。
4. 未运行 git：ref/index 的即时状态未在 R2 重新读取（R1 已直接读 `.git` 文本核对 refs 且未漂移；R2 声称其他输入未变）。本次跟进不重新评估 R1 的其余五个 bullet。

## 7. 推荐下一步（可直接转发）

> **交给 Codex（/root）**：R2 静态复审结论为 `APPROVED_STATIC_CONTENT`（仅限更正范围），P3-1 已解决，新增非阻塞 P3-2。
> 1. 处理 P3-2：把 `verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.md` 第 1 行标题改为 R2（若改动，需重新 pin 该文件并更新 R2 清单/checkpoint），或明确接受并记录；
> 2. 完成你已承诺的 R2 输入 pin 复核（8 项 before/after SHA-256）与 raw NDJSON 第 80 行的 55 checks/`observedPointer` 遍历 —— 这两项是 R1 遗留的能力型未核验项，也是 R2 判定的唯一外部依赖；
> 3. 通过后按 R7 先例将 H2-RUN 结果确认为可集成证据。本审查不授权 X6、不关闭 P2-1、不改变 Gate 原值、不授权重跑 collector（一次性运行已发生，禁止重试）。
