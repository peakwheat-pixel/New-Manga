# Rolling Checkpoint — 2026-10-16（断电恢复轮）

恢复轮次：R1–R6 FAST_RECOVERY。触发原因：宿主断电（用户 2026-10-16 08:35 告知）。
按持续运行语义，断电不视为停止；本文件是本轮及昨夜的稳定边界快照，供后续 session 接管。

## R1–R6 核验结果（全部以 live Git/FS 事实为准）

| 步骤 | 结果 |
|---|---|
| R1 Git/FS | repo=`G:/CODEX/New Manga`；branch=`main`；**HEAD=`4f019b6aa53b03da3a8deafd40837eef7f2e8888`**（与断电前一致，最后提交 2026-10-15 23:53:13 +0800）；工作区 1228 项（19 tracked dirty + 1209 untracked） |
| R2 治理/租约 | `coordinator-lease.py assert` = **`LEASE_VALID`**（dsh, epoch 5, ACTIVE, lease `264c2000541748298000f93fb25a52de`） |
| R3 权威指针 | `tools/governance/check.ps1` = **PASS**（1 预算 warning）；`doc/STATUS.md` 当前 Task=`ARCH-DOC-REBASELINE` |
| R4 EXTERNAL_CHANGE | **无**。无 `MERGE_HEAD`/`REBASE_HEAD`/`rebase-*` 残留；untracked 分布与断电前一致（`verification/P02` 1072 等）；P06 隔离根完好（5 个 exe 在，`core_service.exe` sha256=`ec8a03bd7bbd8b91…` 与证据一致）；G 盘剩 1412.6 GB |
| R5 日志设施 | `.orchestrator/{INFLIGHT.json, OPLOG.ndjson, BACKLOG.md, RUNTIME_DIRECTIVES.md}` 全部存在且内容完整 |
| R6 下一 READY | **无可自主释放节点**：唯一解阻点 P09 需用户选定首发输入格式（见"等待项"） |

`git fsck` 仅报**已登记**的 BL-1：`refs/codex/turn-diffs/checkpoints/2a21a8a6…/ba2cc422-…` 为 `badRefContent` +
`invalid sha1 pointer 0000000000000000000000000000000000000000`（**精确根因：该 ref 文件内容是全零 SHA1**，
非"指向不存在对象"）。其余为正常 dangling objects（gc 未运行）。

## 昨夜完成（2026-10-15 21:00 → 23:53，全部已集成 main）

| Task | 交付 head | 独立 Review | 集成 merge | 关键结论 |
|---|---|---|---|---|
| ARCH-DOC-REBASELINE（AC7/C3 closeout） | — | `dsh-review-r1` | `4227e8b5`（更早） | 8/8 证据 blob 层 sha256 复核一致；F-2 doc/02 取舍按 Merge Conflict 规则记录 |
| P11 长任务生命周期契约 | `c7922ae1` | `09797eab` approved_with_conditions | `ceca5721` | §4 状态机 + §4.5 非法转换清单 + §7.1 单一 scheduler；§8 实证 4 项实现缺口（P13 破坏性变更） |
| P10 凭据与配置通道契约 | `fa20602d` | `d4907acc` approved_with_conditions | `c46c0df0` | CredentialRef exchange + secret MUST NOT 边界 + Proxy 不得静默 Direct；15/15 AC id 真实、0 secret 形态值 |
| P06 GC 分发迁移安全补证 | `4ed493a3` | `ecfef603` approved_with_conditions | `d3342895` | 旧 runtime 真机构建（`ad75fadc`，5/5 exe hash 复核）；AC2 内核租约拒绝→kill 后首次扫描成功；AC3 两种旧 catalog fail-closed 且 catalog sha256 不变（零静默迁移） |

## 用户当轮指令（仍生效）

见 `.orchestrator/RUNTIME_DIRECTIVES.md`：
- **DIR-1**（已失效）：不打断在途 P06 → P06 已收口。
- **DIR-2**（生效中）：**后续 Task 的 Owner=codex，直到 codex 额度耗尽**。
  执行方式：`route-agent.py --prefer-agent codex`；若 codex 进入 `QUOTA_EXHAUSTED/AUTH_FAILED/UNAVAILABLE`，
  先 `set-agent-state` 更新 runtime，再按 router 自然 fallback（REBALANCE）。
  备注：codex 写入型派发当前须用 `-s danger-full-access`（BL-3），并保留"主仓零改动"自证要求。

## 等待项（唯一外部等待：BLOCKED_WAITING_EXTERNAL_DECISION）

四条件检验（P09）：
1. 关键路径 blocker — P09 是 P12/P13/P16/P17/P18/P19/P20 的共同前置；**成立**
2. 无其他 READY — P06 已 done；ARCH-DOC 挂起待消费者；其余全部依赖 P09/P13；**成立**
3. AI 无法自救 — 无法替用户选择产品首发格式；无法绕过 P09 释放下游；**成立**
4. 需用户独有裁决/资源 — 首发输入格式与最小目标是产品取舍；**成立**

**待裁决问题**：
- **Q1（P09 首发范围）**：仅图片/文件夹（最小闭环）／+PDF／+PDF+MOBI（D2 全组）／暂不释放。
- **Q2（技术债授权）**：是否授权处理 BL-1（清理 Codex 遗留全零 ref）与 BL-3（Codex Windows 沙箱：
  `[windows] sandbox="elevated"` 的 setup helper 刷新失败，修复需管理员注册或改用户级 `~/.codex/config.toml`）。

## 下一步（裁决后的动作序列）

1. Q1 得到答案 → 起草 `doc/tasks/P09.md`（冻结 base/allowlist/Gate），**owner 用 codex**（DIR-2），`guarded-write` → 提交 → 建 worktree → preflight（真实探测）→ 派发。
2. Q2 获授权 → BL-1：`git update-ref -d` 该全零 ref（先备份 refs 清单与 fsck 原始输出）；BL-3：按授权方式修复并回归 `-s workspace-write`。
3. 若 Q1 选择"暂不释放" → 继续处理 DAG 外必要技术债，不推进产品实现。
