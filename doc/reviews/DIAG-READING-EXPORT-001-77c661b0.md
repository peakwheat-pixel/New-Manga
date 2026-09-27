---
task_id: DIAG-READING-EXPORT-001
reviewer: Codex（暂代行 Lead/Integrator，非作者）
author: DeepSeek Harness
base_commit: 83de13dfe0521125715c2e26da75b96a63103938
reviewed_head: 77c661b0e32c8f6f5a9a2e4006a267624f622e2e
delivery_head: 8b36e98e8ce11bb54be5d6dfe8921cf64390aa4e
decision: approved
---

# Review：DIAG-READING-EXPORT-001（reading_export 间歇失败诊断）

Reviewer 非 DeepSeek Harness（诊断作者），符合非作者要求。Review 固定
`base=83de13df` → `reviewed_head=77c661b0`（Owner 分支 tip，含 Handoff；
诊断交付 head 为 `8b36e98e`）。本次为只读诊断的**范围/证据 Review**；按
Integrator 指示不重跑 15 次矩阵，全部核验以对象级（`git show`/`git diff`）
逐字节读取与交叉核对完成。

## 范围与依据

- 依据：[Task](../tasks/DIAG-READING-EXPORT-001.md)（`kind: diagnostic`、固定 15-run 矩阵、≤2 个隔离探针、允许/禁止范围）、[09 协作协议 §6](../09_COLLABORATION.md)（含 Q-009 证据纪律）、[诊断报告](../research/DIAG-READING-EXPORT-001.md)、[Handoff](../handoffs/DIAG-READING-EXPORT-001-8b36e98e.md)。
- diff：`83de13df..77c661b0` 共 24 路径（23 增 1 改），提交链 `83de13df → 064ff980（claim）→ 8b36e98e（交付）→ 77c661b0（Handoff）`。
- 未审到的部分：未复核 Owner 本机 `TASK-012-py312` venv 之外的环境声明；未重跑矩阵与探针（Integrator 指示，成本/收益核验后认为对象级交叉核对已足够）。

## Architecture（executed）

只读诊断，零产品改动：`git diff --name-status 83de13df..77c661b0` 全部为
`doc/tasks|research|handoffs` 与 `verification/DIAG-READING-EXPORT-001/**`；
`src/**`、`tests/**`、`packaging/**`、`requirements*`、`doc/contracts/**`
零命中。两个探针脚本仅 `sys.path` 指向仓库 `src/` 并以公开 API/探针内子类
驱动真实 `ExportViewModel`/`ReaderViewModel`+生产装配适配器；无
monkeypatch、无仓库内写入（tempfile lab）、无新依赖。架构结论（症状 A=
排队投递 vs 轮询标志位竞态；症状 B=读者心跳生命周期泄漏）与源码事实相符，
方向依赖未被改变。**PASS。**

## Verification（executed）

| # | 场景 | 核验方式 | 结果 | 证据 |
|---|---|---|---|---|
| V1 | 15 条矩阵记录 ↔ run-01..15.log | 逐条比对命令/次数/环境头/结果/EXIT/起止 UTC | PASS | 15/15 命令与 Task 固定矩阵逐字一致；1+3+5+3+3=15 次用满；全 EXIT=0；`run-01.log` 尾部 `1310 passed, 11 skipped` + `EXIT=0` |
| V2 | run-01 的 11 个 skip 逐项披露 | 读 `run-01.log:389-399` | PASS | docTR×2（`test_detect_seam_t111.py:15`、`test_detection_doctr_real.py:11`）、openssl unavailable×6（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`）、numpy×1（`test_detection_doctr.py:173`）、torch×2（`:206/:236`）——与报告 §1 清单逐条一致，均未计为通过 |
| V3 | 结论口径 | 读报告 §0/§2/§8 与 Task 交付记录 | PASS | 全文维持 `NOT_REPRODUCED`，无"已修复"表述；§0 明示"NOT_REPRODUCED 不等于已修复" |
| V4 | 源码行号与时序 | `git show 83de13df:…` 抽取引用行 | PASS | export `viewmodel.py:291/344`（两处 `threading.Thread`）、`:379-394`（`_finish`：写状态→`changed`→`exportFinished`→清 `running`→`changed`）、tests `:34-48/:163/:274-275`、reader `viewmodel.py:42/69-72/104-105/110-112/441-451`、`test_bootstrap.py:604-611`（`enterReader` 生产装配）全部准确（`pump_until` def 行 33 vs 报告 34 的 ±1 属取段口径，不构成错误） |
| V5 | `_finish` 顺序未回归（0275290 vs base） | `git diff 0275290 83de13df -- src/ui/viewmodels/export/viewmodel.py` | PASS | diff 为空——两版本该文件逐字节相同，"非发布顺序回归"反证成立 |
| V6 | 探针无编辑/monkeypatch 产品或测试文件 | 通读两脚本全文 | PASS | 探针 1 仅子类化打时间戳（`super()._finish()` 后记录）；`pump_until` 为文件内逐字拷贝；探针 2 仅公开 API+`sys.excepthook` 进程内捕获；两探针均 tempfile 写入 |
| V7 | 探针结果 ↔ 报告描述 | 读两份探针日志 | PASS | 探针 1：隔离 0/400 miss、忙碌主线程 26/200 miss、26/26 一次 `processEvents` 到达、slot 全 main 线程、first-miss 字符串与报告引用一致；探针 2：同步调用即 `ProgrammingError`、真实心跳跨周期捕获 1 次未处理异常，栈帧 `viewmodel.py:450 → service.py:241/377/380 → reading_export.py:84 → connection.py:292` 与报告引用逐帧一致，且 `heartbeat still active = True` |
| V8 | 越权路径 | `git diff --name-status` + 禁改路径 grep | PASS | 24 路径全在允许清单；禁改路径零命中；无 D/R（未删除/改写既有证据） |
| V9 | 卫生 | `git diff --check 83de13df..77c661b0` | PASS | exit 0 |
| V10 | claim 纪律 | `git diff ceab572b:… 064ff980:…` | PASS | claim 相对释放版 Task 仅 `status: ready→in_progress` 一行；治理释放 commit `ceab572b` 未入 Owner 分支 |

证据纪律（Q-009）：15 份 run 日志均带命令头、解释器绝对路径、Env ID、
CWD、起止 UTC 与 `EXIT=`，逐次入库；skip 逐条给原因；`matrix.tsv` 另以
注释行登记 2 个探针（`outside the fixed matrix`），探针计数未混入矩阵
15 次。满足。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `doc/research/DIAG-READING-EXPORT-001.md` §4.1 末句 | 探针 1 仅证明**合成**忙碌主线程（`processEvents` 内 2 ms 忙等）放大窗口（26/200），未证明真实全仓事件负载是历史失败的触发/放大条件；但 §4.1 写成"而全仓……正是放大条件"，与 §5 U3（真实触发条件仍未决）自相矛盾，读者可能把候选机制误读为已证实结论 | 报告 §4.1 与 §5 U3 对照；探针 1 日志无任何全仓场景命中数据 | 降低措辞为"候选放大条件"，保留 U3 未决 | **fixed at integration**（集成层修正该句并在集成核验记录登记；不回写 Owner 历史，报告其余机制/数据不动） |
| R-002 | P3 | `verification/DIAG-READING-EXPORT-001/probe-export-signal-window.log` | 探针 1 的 r1/r2 中间修订日志被同文件名重跑覆盖，未保留原始 artefact；属探针开发过程迭代，非矩阵证据，且报告 §0 已如实披露三次修订史与覆盖原因（r1 判定无效原因、r2 仅隔离阶段） | 报告 §0；日志头 `(rev 3, two phases)` | accepted——矩阵 15 次证据完整不受影响；后续诊断建议探针迭代留版本化文件名 | accepted（无需返修） |

P0/P1：无。除 R-001/R-002 外，在记录范围内未发现问题。

## 未决项处置（Integrator 裁决记录）

- **U1**（历史那次是哪个用例留下活心跳）：维持**未决**。收口需第三个探针（teardown 后枚举存活 `ReaderViewModel`），超出本 Task ≤2 探针上限，不授权；其自然收口路径是 FIX-B 落地后的测试 teardown 关闭读者。
- **U2**（是否必然 SQLite 读者用例）：维持**未决**，归属 FIX-B 验证范围。
- **U3**（症状 A 真实触发条件）：维持**未决**；R-001 修正后报告措辞与 U3 一致。FIX-A 的验证 Gate 应包含"忙碌主线程下终态投递与标志位可观察顺序"的判别探针。
- **U4**（两症状独立）：采信报告处置（独立缺陷），作为 FIX-A/FIX-B 拆分为两个独立 Task 的依据。

## 结论与复审

**decision=approved**：固定 `83de13df..77c661b0` 可交 Codex 集成。理由：
范围零越权、证据链可交叉核对、结论口径诚实（NOT_REPRODUCED + 机制定位 +
≤2 探针）；唯一 P2 为报告措辞精度，不影响诊断事实与数据，按 R-001 处置
在集成层修正。

剩余风险（集成后仍成立）：① 该 flaky 未修复，高负载全仓运行仍可复现，
`NOT_REPRODUCED` 不是"已解决"；② U1–U3 未收口；③ run-01 的 11 个环境
skip（6 OpenSSL/2 docTR/1 numpy/2 torch）意味着全仓"全绿"口径需按环境
缺依赖打折。集成后的任何测试由 Codex 在集成核验记录另行登记；本 Review
不重跑诊断矩阵。
