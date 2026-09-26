---
task_id: M2-S1
author: DeepSeek Harness
recipient: Codex
base_commit: 85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc
delivery_head: 4eaad684769a02035748b95186d478bbed926042
status: superseded_by_revision
---

# Handoff：M2-S1 — Large-Media Resource Channel Feasibility Spike

> **已被取代（2026-09-26，保留为审计记录）**：Codex 非作者初审
> [`doc/reviews/M2-S1-4eaad68.md`](../reviews/M2-S1-4eaad68.md)（`f709e39`）为 `decision=changes_requested`
> （R-001=P1 检查→打开竞态、R-002=P2 引用并非不透明）。当前有效交接为
> [`M2-S1-64c87d1.md`](M2-S1-64c87d1.md)，`reviewed_head=64c87d13faa3889c749096dedeacf5afbe8dda16`。
> 本文件正文未改动；其中「不透明引用」「越界/重解析逃逸已缓解」等表述**已由修订取代**，请以修订版为准。

## 交付结果

**结论（一句话）**：在 Windows 上用同一台机器、合成隔离 fixture 实测，大媒体（页图 / Webtoon tile）
跨进程是**可行**的；推荐以 **受限资源引用/能力 token + Core 侧解析 + 带外文件读取（路线 A）** 为主通道，
以 **流式/分块字节通道 + 显式长度/摘要 framing（路线 B）** 为第二通道；**普通 JSON/Base64 在测量上被证伪**；
**命名共享内存不具备能力语义**，`DuplicateHandle` **只受源进程 ACL 约束（同用户可复制，已实测）**。
任何选型进入产品 Contract/Runtime 前仍需本 Review、Codex 集成与用户对 7 项缺失阈值的决定。

**提交列表**

| # | commit | 说明 |
|---|---|---|
| 1 | `4eaad684769a02035748b95186d478bbed926042` | **delivery head**：研究报告 + `verification/M2-S1/**` 探针与原始证据 + Task AC 回填 |
| 2 | 本 Handoff 提交（doc-only，在其之上） | Handoff、checkpoint 更新、Task frontmatter 状态与 SHA 回填、scope log 追加 |

**变更路径（共 39 项；授权写集合内）**

- `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`（新增，研究报告）
- `doc/tasks/M2-S1.md`（修改，Owner 运行记录与 AC1–AC6 回填）
- `doc/handoffs/M2-S1-4eaad68.md`（本文件，新增）
- `verification/M2-S1/**`（新增）：`README.md`、`00-environment-and-recon.md`、
  `01-source-and-consumer-reality.md`、`02-evidence-manifest.md`、`03-checkpoint.md`、
  `04-verification-plan-results.md`、`probes/**`（6 探针 + lib + fixture 生成器 + runner）、
  `raw/**`（原始日志、结果 JSON、fixture hash、证据 hash、delivery scope log）

**未改动（零变化，已用 `git diff` 核验）**：`src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、
React/QML、Schema/migration、依赖与锁文件、`doc/contracts/**`、AD-001、`doc/REBASELINE_PLAN.md`、
`doc/STATUS.md`、`doc/00_INDEX.md`、`verification/M2-C1/**`、M2-C1 的 Handoff/Review。
未 `merge` `master`；未写 Review；未创建/覆写 Codex 的
`verification/M2-S1/release-85a2aa7.md` 与 `dispatch-85a2aa7.md`。

### AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| S1-AC1 来源与边界 | **PASS** | `00-environment-and-recon.md`、`01-source-and-consumer-reality.md`：base/branch/clone 形态/Contract blob 三方一致；AS-IS 生产者/消费者与四类资源生命周期逐项标注 `AS-IS/TO-BE/PROPOSAL/UNVERIFIED` |
| S1-AC2 候选与取舍 | **PASS** | 研究报告 §3：A/B/C1/C2/C3/D 六路线候选矩阵（权限边界、拷贝次数、序列化、关闭/撤销、失效与诊断），全部实机筛选 |
| S1-AC3 可复现容量证据 | **PASS** | 研究报告 §4；5 探针、**60/60 场景 PASS**、全部 exit code 0；小图/典型页/tile/超长页/超限拒绝齐备；受控上限 64 MiB 明确标注为探针配置 |
| S1-AC4 数据保护与生命周期 | **PASS**（含明确 `UNVERIFIED`） | 研究报告 §5：过期/撤销/只读/限域/取消/崩溃已实测；Core 重启、断线重取、缓存清理探针、Revision 绑定、源文件 OS 级 ACL 记 `NOT_RUN/UNVERIFIED` |
| S1-AC5 决策输出 | **PASS** | 研究报告 §6 威胁模型、§7 缺失阈值（`USER_DECISION_REQUIRED`）、§8 推荐 + 10 项 blocker 与解除条件 |
| S1-AC6 范围与交接 | **PASS** | `raw/20-delivery-scope.log`（`git diff --name-status`、`git diff --check`、禁止路径与 M2-C1 工件检查）、`02-evidence-manifest.md` §5 `NOT_RUN/BLOCKED` 清单、本 Handoff |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 固定点与基线 | `pwsh -NoProfile -File verification/M2-S1/probes/00_recon.ps1` | Windows 11 26200 / base `85a2aa7` | **PASS**（独立 clone、Contract blob `4b503a17…` 三方一致） | `raw/00-recon.log` |
| 路线 A 引用/token | `python verification/M2-S1/probes/probe_a_token.py --lab %TEMP%\m2s1-lab --out …probeA-result.json` | Python 3.14.6 / base `85a2aa7` | **PASS** exit 0，15/15 场景 | `raw/10-probe-A-capability-token.log`、`raw/probeA-result.json` |
| 路线 B 流式管道 | `python …/probe_b_stream.py --lab … --out …probeB-result.json` | 同上 | **PASS** exit 0，12/12 | `raw/11-…log`、`raw/probeB-result.json` |
| 路线 C 句柄/共享内存 | `python …/probe_c_section.py --lab … --out …probeC-result.json` | 同上（`cmd.exe` 创建 junction） | **PASS** exit 0，14/14 | `raw/12-…log`、`raw/probeC-result.json` |
| 路线 D Base64 对照 | `python …/probe_d_base64.py --lab … --out …probeD-result.json` | 同上 | **PASS** exit 0，8/8 | `raw/13-…log`、`raw/probeD-result.json` |
| 并发/容量 | `python …/probe_e_concurrency.py --lab … --out …probeE-result.json` | 32 逻辑处理器 | **PASS** exit 0，11/11 | `raw/14-…log`、`raw/probeE-result.json` |
| 全套连续复现 | `pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 \| Tee-Object …` ×2 | 同上 | **PASS** 两次 `all_zero = True` | `raw/00-run-all.log`、`raw/04-repeat-run-1.log` |
| 交付范围 | `git diff --name-status 85a2aa7..4eaad68`、`git diff --check 85a2aa7 4eaad68` | delivery head `4eaad68` | **PASS** `rc=0`；仅授权路径；禁止路径与 M2-C1 工件零改动 | `raw/20-delivery-scope.log` |
| 产品 pytest / GUI / IPC runtime | 未运行（Task 范围要求） | 无产品实现 | **NOT_RUN** | 本 Handoff |

**实测关键数字**（MEASURED，全部来自上述日志；详细表见研究报告 §4）

| 路线 | 关键测量 |
|---|---|
| A 引用/token | 控制通道 7,098 B（去）+ 7,997 B（回）= **15,095 B** ↔ 带外交付 **85,310,202 B**；Core 内解析 0.33–0.47 ms；宿主峰值工作集 26.2 MB；9 个稳定拒绝码（`MEDIA_TOO_LARGE`/`REF_EXPIRED`/`REF_REVOKED`/`REF_SIGNATURE_INVALID`/`REF_OUT_OF_SCOPE`/`REF_READ_ONLY`/`REF_SCOPE_DENIED`/`REF_REPARSE_POINT`/`REF_NOT_FOUND`） |
| B 流式 | 60.77 MB / 109.2 ms（530.9 MB/s；首字节 ~77 ms 为子进程解释器启动，净传输 ~32 ms）；宿主 WS 增量 0.96 MB；慢消费者背压 **10.6×**；截断（生产者 exit 0）、崩溃（exit 3）、超限（0 字节，生产者被关闭通道终止）均可判别 |
| C1 命名 section | 只“得知名字”的同用户进程可 `FILE_MAP_READ\|FILE_MAP_WRITE` 打开并改写载荷（观测到 `HOSTILE!`）；创建者退出后 `OpenFileMappingW` 失败；未知名字被拒 |
| C2 匿名 section + `DuplicateHandle` | 句柄复制进宿主后可映射并 sha 匹配 11,525,983 B，且**创建者退出后仍可读**；映射 11.5 MB 使宿主 WS +11.0 MB；同用户恶意复制 **成功**（记录为限制）；伪造句柄值 `DUPLICATE_HANDLE_FAILED`；相邻值/外来值 `SECTION_MAP_FAILED`；超限 0 分配 |
| C3 只读屏障 | `GENERIC_READ` 句柄 `WriteFile` → `ERROR_ACCESS_DENIED (5)`；只读映射写 → `TypeError` |
| D 对照 | 膨胀恒为 1.3333–1.3336；58 MB 载荷使接收端 WS +212.5 MB；单 JSON 文档内分块**不**使内存有界（+29.4 MB），按消息边界分块才有效（+2.8 MB）；超限受控拒绝 0 字节；naive 76 MB 路径 +265.6 MB（进程峰值 386.9 MB） |
| E 并发 | A：8 消费者 81,032,259 B / 11.6 ms（页缓存热，非冷启）；B：4 消费者 111.7 ms；C：8 进程读同一 11.5 MB section 160.9 ms（一份拷贝、8 个映射） |

**未跑项与原因**：Tauri/WebView 资产协议（无 Tauri runtime）；React 消费者与重连（Task 范围排除）；
真实 Core worker 取消与 Core 重启后的引用行为（无产品进程模型）；缓存清理探针；断线重取快照；
冷缓存吞吐（页缓存热）；打包/沙箱形态；模型权重通道；Revision 绑定撤销；产品 pytest/GUI/IPC runtime
（Task 范围要求不运行）。完整 `NOT_RUN/UNVERIFIED` 清单见 `02-evidence-manifest.md` §5 与研究报告 §9.1。

**探针自身缺陷（已修正，必须在 Review 时知情）**：①路线 C 曾误读上一轮遗留 report，用已退出进程的 PID
得出错误结论；②路线 A 并发场景曾用非原子的 `list[0] += size` 累加，8 线程时丢失两次更新且仍判 PASS。
两者均已修正，并在受阻处加了断言；修正后连续两次运行一致。详见 `02-evidence-manifest.md` §4。

## 接收方式

- 仓库：`C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`（C: 独立 clone；`--git-common-dir` = 本地 `.git`）
- branch：`agent/deepseek/M2-S1-resource-channel-spike`；base `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`；
  delivery head `4eaad684769a02035748b95186d478bbed926042`
- 复现：`pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log`
- 前置条件：Windows x64、`python` 在 PATH（3.14.6 已测）、PowerShell 7、`cmd.exe`（创建 junction）；
  lab 目录默认 `%TEMP%\m2s1-lab`（可随时删除，约 200 MB）
- 无新增依赖、无 Schema/Contract 变更、无网络访问
- Reviewer 建议先做的检查：①核对 `raw/00-run-all.log` 与 `raw/06-evidence-hashes.log` 的 hash 一致性；
  ②按 `02-evidence-manifest.md` §4 复算两个缺陷的修正效果；③确认 `raw/20-delivery-scope.log` 的
  `diff --check rc=0` 与禁止路径为空；④确认研究报告 §7/§8.2 的 `USER_DECISION_REQUIRED` 与
  `NOT_RUN/UNVERIFIED` 未被提升为 PASS

## 下一任务建议（必填）

1. **Task**：`M2-S1` 收尾切片 —— 非作者 Review + Codex 集成（**不是**新的实现 Task）。
   后续任何“大媒体命令 runtime 实现 Task”必须先满足：本 Review `APPROVED`、Codex 集成完成、
   且用户在研究报告 §7 的 7 项阈值上给出决定。在此之前该实现 Task 应保持 `BLOCKED / 等待用户裁决`。
2. **Agent**：Reviewer = **Codex**（非作者）。Owner 与 Reviewer 必须不同，DeepSeek Harness 不得审自己的交付。
3. **Recovery point**：仓库/工作区 `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`；
   branch `agent/deepseek/M2-S1-resource-channel-spike`；固定 `base_commit=85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`；
   `reviewed_head=4eaad684769a02035748b95186d478bbed926042`（Handoff 提交为其子提交，不改动被审内容）。
4. **Scope**：Reviewer 只写 `doc/reviews/M2-S1-4eaad68.md`（新建）。禁止修改 `src/**`、`tests/**`、
   依赖、Schema、`doc/contracts/**`、AD-001、治理导航、M2-C1 工件与 Owner 交付内容。
   集成由 Codex 在共享仓库执行；**不得**把治理提交 merge 进本 Owner 分支。
5. **Deliverables**：Review 报告（Architecture 轴 + Verification 轴，逐项 `PASS/FAIL/BLOCKED/NOT_RUN`，
   findings 带级别/文件/复现/影响）；通过后由 Codex 记录 `integration_commit` 并更新 Task/STATUS。
6. **Verification**：核对 `raw/00-run-all.log` 的 `all_zero = True` 与逐探针 exit 0；
   `git diff --check 85a2aa7 4eaad68` 必须 `rc=0`；`src/**`/`tests/**`/`doc/contracts/**`/M2-C1 零改动；
   `NOT_RUN`/`BLOCKED` 不得记为 PASS。完成 Gate：非作者 Review `APPROVED` + Codex 集成 +
   集成后验证，且用户阈值决定已登记。
7. **Forwardable instruction**（可直接转发）：

> Codex：请对 M2-S1 研究交付执行**非作者 Review**。工作区
> `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`，branch
> `agent/deepseek/M2-S1-resource-channel-spike`，固定 base
> `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`，reviewed_head
> `4eaad684769a02035748b95186d478bbed926042`。请阅读
> `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`、`verification/M2-S1/README.md`、
> `verification/M2-S1/02-evidence-manifest.md`、`raw/00-run-all.log` 与
> `raw/probeA..E-result.json`；复算 `raw/06-evidence-hashes.log`；确认
> `git diff --check 85a2aa7 4eaad68` 为 `rc=0`、无禁止路径改动、无 M2-C1 工件改动；
> 逐项判定 AC1–AC6 与 `NOT_RUN/UNVERIFIED` 是否诚实。报告只写到
> `doc/reviews/M2-S1-4eaad68.md`，不要修改 Owner 交付内容、不要改 `src/**`/`tests/**`/契约，
> 不要写实现 Task 的代码。Review 通过后由你记录集成与集成后证据；在此之前的任何大媒体
> runtime 实现 Task 应标 `BLOCKED / 等待用户裁决`，因为研究报告 §7 的 7 项产品阈值尚未由用户决定。

## 风险与遗留

- **未验证的关键路径**（不得据此批准产品实现）：Tauri/WebView 资产协议（S1-B1）、源文件边界 OS 级
  ACL/完整性级别（S1-B3）、Core 取消/重启语义（S1-B4/B5）、冷缓存吞吐（S1-B6）、真实页压缩率（S1-B7）、
  打包/沙箱形态（S1-B8）、模型权重通道（S1-B9）、Revision 绑定撤销（S1-B10）。
- **路线 A 的绝对路径暴露**：本原型的 Core 批复把文件绝对路径回给宿主。产品实现应改为 host/Core
  资产 URL，使前端看不到 OS 路径（研究报告 §6.3 第 2 条）。这是 PROPOSAL 改进项，**不是**已实现能力。
- **同用户威胁**：`DuplicateHandle` 与命名 section 在同用户同完整性对手面前都不构成机密性边界
  （均已实测）；不要把“改用句柄/共享内存”当作安全论证。低完整性/跨会话对手的拒绝为 `UNVERIFIED`。
- **测量限制**：所有吞吐数字都在页缓存热、Python↔Python 进程、不可压缩 fixture 条件下取得；
  不可外推到 Tauri/WebView、磁盘冷启或真实漫画页。
- **回退方式**：本交付只新增文档与 `verification/M2-S1/**`；如需回退，只需弃用该分支或 revert 这两个
  文档提交，产品代码与共享契约不受影响。
- **关联 Task**：M2-C1（依赖，`done`，Contract blob `4b503a17…`）；M2-R1（Qt 平台研究，其结论不可外推
  为跨进程资源通道能力）。

## 实验附录（仅实验任务）

- **数据来源与许可**：无外部数据。全部载荷由 `verification/M2-S1/probes/make_fixtures.py` 在
  `%TEMP%\m2s1-lab` 内以固定种子生成确定性 RGB 噪声 PNG（真实漫画页可能有版权与隐私约束，
  故完全未使用）。fixture 生成器随仓库提供，可逐字节复现。
- **数据 Hash**：见 `raw/fixtures.json`（每个 fixture 的 SHA-256、尺寸、PNG 字节、种子、zlib 级别）；
  证据文件 hash 见 `raw/06-evidence-hashes.log`；探针脚本 hash 见 `raw/01-probe-script-hashes.log`
  （已核对与当前脚本一致）。
- **模型/权重版本与 Hash**：**N/A —— 本 Task 未加载、未测量任何模型或权重**；权重通道为 `NOT_RUN`。
- **Provider/Runtime**：无网络、无外部 provider。Runtime = CPython 3.14.6 + Windows 内核对象
  （管道、section、句柄、文件映射）。未使用 Tauri/Rust/WebView/React。
- **硬件**：AMD64 Family 25 Model 97；32 逻辑处理器；物理内存 32.4 GB（运行时可用 9.06 GB，负载 72%）；
  C: 可用 442.76 GB；OS Windows NT 10.0.26200.0。
- **网络策略**：全部命令行参数显式传入；探针不含任何网络调用；未配置代理。
- **参数**：`M2S1_MAX_MEDIA_BYTES = 67108864`（探针配置，非产品阈值）；写块 1 MiB；读块
  64 KiB / 256 KiB / 1 MiB / 4 MiB；背压场景每 8 MiB 睡 150 ms；取消点 4 MiB；截断点 8 MiB；
  崩溃点 4 MiB；并发 1/2/4/8。
- **运行次数**：全套探针在本 Task 内运行 4 轮（含 2 轮修正后连跑），每轮 60 场景全 PASS 且 exit 0；
  其中 `probeD` 的 naive 无界对照每轮只运行一次。
- **原始结果**：`raw/00-run-all.log`、`raw/04-repeat-run-1.log`、`raw/10..14-*.log`、
  `raw/probeA..E-result.json`、`raw/05-final-digest.log`。
- **质量判断办法**：每个场景都断言 sha256 与 fixture 匹配、字节数与期望精确相等、受控拒绝返回
  稳定错误码、以及内存/耗时上界；不依赖“看起来成功”。判别性场景（伪造/相邻/外来句柄值、
  词法穿越、域内 junction、单文档 vs 消息边界分块、EOF 截断）都是**对照**测量，不是散文断言。
- **失败样例**：`raw/10-…log` A-05、`raw/11-…log` B-08/B-09/B-10/B-11、`raw/12-…log` C1-04/C1-05/C2-03/C2-04/C2-05/C2-06、
  `raw/13-…log` D-06 均为**预期的失败/拒绝路径**，全部 PASS（即“按预期被拒绝”）。
- **限制**：见上文「风险与遗留」与研究报告 §4.6。
- **建议**：在 Tauri 骨架可用后，先用同一 `probeA`/`probeB` 的最小版本替换其中的“宿主进程”，
  验证资产协议与 sidecar 字节通道（S1-B1）；在此之前不要释放任何大媒体命令。
