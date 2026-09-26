# M2-S1 — Task「验证计划」实际执行结果

对应 [M2-S1](../tasks/M2-S1.md) 的「验证计划」四行。全部命令与 exit code 见
[`raw/00-run-all.log`](raw/00-run-all.log) 与各探针日志。

| 场景 | 计划命令/步骤 | 环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 基线与范围 | `git rev-parse HEAD`、`--show-toplevel`、`--git-dir`、`--git-common-dir`、`git status --short`、`git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | C: 专属独立 clone | **PASS**：`HEAD=85a2aa7…`、branch 一致、`--git-common-dir=.git`、无 `commondir`/`alternates`（独立 clone）、开始时 status 干净、Contract blob=`4b503a17…`（与 base/origin/master 三方一致） | [`raw/00-recon.log`](raw/00-recon.log)、[`00-environment-and-recon.md`](00-environment-and-recon.md) |
| 候选容量/权限/生命周期 | 从 `verification/M2-S1/probes/` 运行隔离探针；每候选记录确切命令、环境、输入 hash、输出、exit code 与失败路径 | Windows 隔离临时数据（`%TEMP%\m2s1-lab`）；不接触用户库 | **PASS**：原交付 5 个探针 exit_code=0；60/60 场景 PASS（A 15、B 12、C 14、D 8、E 11） | [`raw/10..14-*.log`](raw/)、[`raw/probeA..E-result.json`](raw/)、[`raw/fixtures.json`](raw/fixtures.json) |
| **修订：R-001/R-002 边界实测** | `python verification/M2-S1/probes/probe_f_boundary.py --lab %TEMP%\m2s1-lab --out …probeF-result.json` | 新会话 lab（原会话 lab 被平台回收） | **PASS**：8/8 场景 PASS，exit_code=0；TOCTOU 窗口实测为**开**；引用正文无密钥可解；句柄绑定隔离对照可拦截本次替换 | [`raw/15-probe-F-boundary.log`](raw/15-probe-F-boundary.log)、[`raw/probeF-result.json`](raw/probeF-result.json)、[`raw/08-revision-code-diff.log`](raw/08-revision-code-diff.log) |
| **修订：fixture 可复现性** | `python verification/M2-S1/probes/make_fixtures.py --lab %TEMP%\m2s1-lab` | 同上 | **PASS**：10/10 SHA-256 与已提交 `raw/fixtures.json` 完全一致 | [`raw/16-revision-fixture-reproducibility.log`](raw/16-revision-fixture-reproducibility.log) |
| 交付范围 | `git diff --name-status <base>..<delivery>`、`git diff --check <base> <delivery>`；禁止路径检查 | 固定 Delivery head | **PASS**（见 Handoff「范围与 diff 证据」段与 `raw/20-delivery-scope.log`、`raw/21-revision-scope.log`）：仅授权路径；`git diff --check` 无输出；`src/**`、`tests/**`、`doc/contracts/**`、`doc/AD-001*`、治理导航、M2-C1 工件零改动 | [`raw/20-delivery-scope.log`](raw/20-delivery-scope.log)、[`raw/21-revision-scope.log`](raw/21-revision-scope.log)、Handoff |
| 产品 pytest、GUI、IPC runtime | 不在本研究 Task 运行或宣称通过 | 无产品实现 | **NOT_RUN（范围要求）**：未运行任何产品测试；未启动 GUI；未实现 IPC runtime | Handoff「实验附录」段 |

## 逐路线 exit code 与规模摘要

| 探针 | 命令 | exit code | 场景 | 结果 |
|---|---|---:|---:|---|
| A | `python verification/M2-S1/probes/probe_a_token.py --lab … --out …` | 0 | 15 | 15 PASS / 0 FAIL |
| B | `python verification/M2-S1/probes/probe_b_stream.py --lab … --out …` | 0 | 12 | 12 PASS / 0 FAIL |
| C | `python verification/M2-S1/probes/probe_c_section.py --lab … --out …` | 0 | 14 | 14 PASS / 0 FAIL |
| D | `python verification/M2-S1/probes/probe_d_base64.py --lab … --out …` | 0 | 8 | 8 PASS / 0 FAIL |
| E | `python verification/M2-S1/probes/probe_e_concurrency.py --lab … --out …` | 0 | 11 | 11 PASS / 0 FAIL |
| **F（修订）** | `python verification/M2-S1/probes/probe_f_boundary.py --lab … --out …` | 0 | 8 | 8 PASS / 0 FAIL |

**A–E 未在修订中重跑**：其日志、命令与 exit code 保持首次执行值；`run_all.ps1` 未改动。

关键容量结论（详见研究报告 §4）：
- 路线 A：控制通道 15,095 B 换取 85,310,202 B 带外交付；解析 0.33–0.47 ms；宿主峰值 26.2 MB。
  **权限结论限定为静态路径输入**；引用**不保密**（F-01），检查→打开竞态**未防护**（F-03..F-06）。
- 路线 B：60.77 MB 载荷 109.2 ms（530.9 MB/s；首字节 ~77 ms 为解释器启动，净传输约 32 ms）；宿主 WS 增量 0.96 MB；
  慢消费者背压 10.6×；截断/崩溃/超限均可判别；**不引入路径再解析竞态**。
- 路线 C：命名 section 可被同用户进程**匿名写**、随创建者消失；匿名 section + `DuplicateHandle`
  生命周期好但**同用户可复制**（实测成功）；映射 11.5 MB 使消费者 WS 增量 ≈11.0 MB。
- 路线 D（对照）：膨胀恒为 1.3333–1.3336；58 MB 载荷使接收端 WS +212.5 MB；naive 76 MB 路径 +265.6 MB
  （进程峰值 386.9 MB）。
- 并发（probeE）：A 8 消费者 81,032,259 B / 11.6 ms（页缓存热，非冷启）；B/C 受子进程启动成本主导。
- 边界（probeF，修订）：F-05 在“先检查大小、后打开”的顺序下实际读到 68,157,440 B（超过 64 MiB 限）；
  F-06 等大小换内容仅凭大小复检无法发现；F-07 打开后按句柄校验身份 → `FILE_IDENTITY_CHANGED`；
  F-08 合法资源仍读回正确 sha。

探针自身的两个缺陷（陈旧 report 读取、并发丢失更新）及修正记录见
`verification/M2-S1/02-evidence-manifest.md` §4；Review R-001/R-002 的修订见该文件 §6 与研究报告 §12。
