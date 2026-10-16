# Rolling Checkpoint — 2026-10-16（r9，Coordinator=dsh epoch 6）

稳定边界快照，供新 session 接管。**事实以 live Git/FS 为准**；本文件不改变 DAG 或 Task 状态，
权威指针仍是 [STATUS](../../doc/STATUS.md) 与 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md)。
上一稳定边界见同目录 [checkpoint.md](checkpoint.md)（断电恢复轮，HEAD `4f019b6aa` / epoch 5，已过期）。

## 1. 当前 live 事实（须先核验，不得直接采信本文件）

| 项 | 值 |
|---|---|
| repo / branch | `G:/CODEX/New Manga` / `main` |
| HEAD（写入本文件时） | `ca53a5b08` |
| tracked dirty | **19（全部为用户既有改动，本次会话全程未变）** |
| Coordinator | **dsh epoch 6**，lease `9ce79020a36e4fab8970e8ae6de5fb10`（LEASE_VALID）；epoch 5 旧 lease 已 `STALE_COORDINATOR` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` → **PASS**（STATUS/PLAN 各 1 个 80% 预算 warning） |
| 权限/用户裁决 | **DIR-3（用户 17:10）**：只保留一个 Active Coordinator 会话 → 本会话以原子 CAS takeover 到 epoch 6 |

## 2. 本会话已完成并集成（含 Review 结论）

| Task | 状态 | 集成 | Review |
|---|---|---|---|
| [ENV-BUNDLE-1](../../doc/tasks/ENV-BUNDLE-1.md) | closed_with_limitations | `7b9cbbe6` | 由并行会话完成（`8250b420`）；bundle 重建对齐协议 2.3，AC4 严格口径转后续 |
| [UI-DESIGN-1](../../doc/tasks/UI-DESIGN-1.md) | **done** | `a24001f9` → `9e1221e1` | R1 `3f312c5dc` **approved**（I1 收敛：G6/G19 误判为缺口已撤销，新增 W30–W32；W=32/G=24） |
| [ENV-BUNDLE-1-FU1](../../doc/tasks/ENV-BUNDLE-1-FU1.md) | closed_with_limitations | `b474c09b` | R1 `a88242d5f` **approved**；AC2 六项由真实 frozen bundle 驱动 **6/6**；I1（启动死线脆弱）收敛；AC3 `REF_EXPIRED` 转 HOST-TTL-BOUNDARY-1 |
| [P12](../../doc/tasks/P12.md) | **done** | `465e3001` | R1 `78d782376` changes_requested → I1 `083610fb2` **收敛** → approved；四页 Shell + 书架页 + 导入 UI；173/173 前端测试、构建 exit 0 |

## 3. 在飞 / READY

| Task | Owner | 说明 |
|---|---|---|
| [HOST-TTL-BOUNDARY-1](../../doc/tasks/HOST-TTL-BOUNDARY-1.md) | codex | import 侧 `+299.0` 已验收（frozen 2.3 注册被接受）；**导出侧同类零裕量缺陷**（Reviewer 差分探针证明 1 ms 负偏差即 `REF_EXPIRED`）I1 返修中（`4662239b4` 已改 `+299.0`） |
| [EVENTS-FWD-1](../../doc/tasks/EVENTS-FWD-1.md) | antigravity | 解 G17：冻结并实现 host→WebView 事件转发面（P14 前置） |
| [EXPORT-REVEAL-1](../../doc/tasks/EXPORT-REVEAL-1.md) | **待派发** | 解 G20：按不透明 `export_id` 打开导出目录（**P17 最后一块前置**） |
| [ARCH-DOC-REBASELINE](../../doc/tasks/ARCH-DOC-REBASELINE.md) | — | ready/integrated；AC7 逐消费者裁决待做 |

## 4. 本会话新增登记（务必继承）

- **BL-13**（`.orchestrator/BACKLOG.md`）：生产 Host 启动也用 30 s ping（`main.rs:840/848`），失败经 `.expect` panic；
  产品期限/失败处理属**产品取舍**，待用户或 Codex 裁决。
- **HOST-TTL-BOUNDARY-1 的两处实例同源**：`build_import_grant`（`host_issuer.rs:152` ↔ `import_source_refs.py:153`）
  与 `build_export_grant`（`:301` ↔ `target_refs.py:127`）；两侧签名均以 `{:.6}`/`{:.6f}` 耦合，
  **改精度必须两侧同步**。探针：`.orchestrator` 同级 workspace `tmp/guarded/{ttl,export-ttl}-boundary-probe.{py,log}`。
- **ZCode 派发限制**（`.orchestrator/RUNTIME_DIRECTIVES.md`）：`--mode edit` headless 下**全部 shell 命令被拒**
  （含 `git add`/`powershell`），故需构建/测试/提交的 ZCode Task 必须把自检与提交指派给 Owner 之外的执行者。
- **环境限制**：无头 Windows 下 WebView2 取不到窗口句柄（`0x80070578`），**真实 GUI e2e runner 无法运行**；
  凡涉及前端"零回归"的结论目前只由单测支撑，**不得**表述为已 e2e 验证。
- **CRLF 噪音**：`core.autocrlf=true`，cargo/构建会重建约 27 个 tracked 文件的纯行尾差异；
  判定真实改动**必须用 `git diff`**，并在提交前逐项恢复。

## 5. 恢复流程（R1–R6）

1. `git rev-parse HEAD` / `git status --porcelain --untracked-files=no`（应为 19）；
2. `coordinator-lease.py assert`（若 epoch 已变，按 skill 用 `takeover --expected-epoch` 原子接管）；
3. `tools/governance/check.ps1` 应 PASS；核对 STATUS 当前 Task 与 PLAN READY 一致；
4. dirty ≠ 19 → 逐项归因，**不得** reset/覆盖/删除未归因改动；
5. 读 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`；
6. 从 §3 的在飞 Task 继续：先复核其 owner 交付（本会话对每个 Task 均执行"独立复跑 + 范围核验 + 证据 pin 复算"）。

## 6. 待用户裁决

- **P18 产品发布门槛**（JA/KO 达到何种程度才声明支持）——AI 不得代定。
