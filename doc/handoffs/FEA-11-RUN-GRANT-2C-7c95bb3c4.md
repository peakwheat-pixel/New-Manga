# FEA-11-RUN-GRANT-2C 交付/收尾交接（delivery_head `7c95bb3c4`；2026-11-07 closeout）

> 本文件是 **2C 长 Run 续期**的最终交接（r1 返修后交付）。初版交付记录见
> `doc/handoffs/FEA-11-RUN-GRANT-2C-e5e9c4c52.md`（历史字节保留）；两者不一致处以本文件 +
> `verification/FEA-11-RUN-GRANT-2C/EV.md` + r2 报告为准。

## 1. 状态

- Task：`doc/tasks/FEA-11-RUN-GRANT-2C.md` — **`done`**；`delivery_head` = `integration_commit` = **`7c95bb3c4`**；
  `canonical_evidence_status=complete`、`resource_closeout_status=complete`。
- 交付链：`c40489b5d`（`RunGrantRenewal.cs` 新 + HostRuntime/HostOptions/SourceReadCoordinator/HostCommandDispatcher 接线）
  → `e5e9c4c52`（测试）→ **`7c95bb3c4`（r1 返修：P1-01 Host 接线判别 + P2-01 轮前预算 + P3）**；证据提交 `03361fec6`。
- 独立 Review：r1 `doc/reviews/FEA-11-RUN-GRANT-2C-r1.md` **changes_requested（P0=0/P1=1/P2=1/P3=5）** →
  **r2 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md` approved（P0=0/P1=0/P2=1/P3=7）**（reviewer = fresh subagent
  session `a4410d0a…`，独立上下文）。
- 卡 `base_commit=fdd170039`；实现起点 `c5f1b416f`；证据目录 `verification/FEA-11-RUN-GRANT-2C/`（21 个 canonical 文件）。

## 2. 做了什么（能力边界）

Run **非终态**期间，Host 每 `240s` 对**同一冻结 `{command, scope}`** 重铸**新** grant（新 id、`expires_at=_clock()+300`）
并重发既有 `AuthorizeSourceReadForRun`；每轮重走 `Registry.Authorize` + 物理 facts，typed 拒绝/全 skip/撤销/漂移/终态/
轮次上限（12）/单轮预算（50s，进入 mint 路径前传入）→ typed 停止或 typed skip。零 Core、零 Run wire、零新命令/能力/错误码、
零 App/UI、`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 既有值不变。

## 3. 门禁（Lead 2026-11-07 实跑，repo root）

| 项 | 结果 |
|---|---|
| build | **0 warning / 0 error** |
| Host `--filter "HostWiring\|RunGrantRenewal"` | **19/0/0** |
| **Probe-C**（`probe-c-apply.py` → 全量 Host → restore） | **281 passed / 2 failed / 65 skipped**（2 failed = `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` + `HostWiring_ManagedOnlyRun_StartsNoRenewal`）→ 恢复 sha256 `bae563e1…` MATCH、git blob `0098ff5f…` → 复跑 **19/0/0** |
| gated 真 IPC（`NEWMANGA_FEA11_IPC=1`） | **7/0/0** |
| fake clock pytest | **3 passed / 27 deselected** |
| 全量 pytest | **3363 passed / 10 skipped EXIT=0** |
| 全量 .NET | **1680 passed / 0 failed / 96 skipped EXIT=0** |
| pins | **18/18**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`） |
| check（默认 + `-TaskPath`） | **PASS(3 warnings)** |
| API inventory | **EXIT=0** |
| scope | **PASS**：changed=32 全 ALLOWED、`out_of_scope=[]`、`forbidden=[]`、`src/**` 零 diff |
| 判别性 | **9/9 RED_AS_EXPECTED**（D1–D9） |
| 跑后恢复 | `git checkout -- verification/FEA-09` 已执行，工作树 clean |

## 4. L-G1 口径（只降级不关闭；保留子限制）

**「有续期 + 子限制」，L-G1 不关闭。** 保留：单步 >300s／续期失败（typed 停止、不重试、不 reattest、不自动重新授权）／
L-G2 加密源／L-G9 Core 重启／L-R1 viewer 残余／L-G16 >4096 成员／未 dispatch 的 pending Run 不在范围／L-G8 成本放大
（每 240s 重 mint）；**预算 skip ≠ 续期成功 ≠ Run 失败**。**不得**写「任意长 Run 可用 / L-G1 关闭 / Run 全面恢复 /
自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。

## 5. limitation / follow-up（如实保留）

- **L-2C-01（R2-01，P2）**：3 条 HostWiring 用例驱动 `HostRuntime` 生产方法，但未穿过 `StartInternalAsync` 安装调用点、
  dispatcher 的 `runDispatched:` 参数、`AcceptRunAsync` 启动调用点；r2 附加删除这 3 处后全量 Host 仍 283/0/65 全绿。
  **当前代码正确**（安装行与功能方法已被 Probe-C 判别），风险是未来误删调用点不会被测试发现；建议另立小卡补调用点级判别。
- R2-02（生产 `ProbeRunLivenessAsync` 无测试）、R2-03（预算事后守护窄窗口可吞 typed stop code）、R2-04（全 skip 折叠丢失
  `SOURCE_GRANT_REVOKED` 等 §6 code）、R2-06（预算窗口未计 probe/mint 超时）、R2-07（manifest 历史提交行 sha 用最终快照口径）、
  R2-08（测试 seam public / `Untrack` 死代码）— 均 P3 非阻断，保留。
- R2-05（EV/Handoff 口径滞后）已由 closeout 清理（本文件 + EV §8 为准）。

## 6. 资源

`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\`（fixtures / review-r1 / review-r2 / tools / lead-r2-gates）为测试夹具
与审查备份，**保留（PRESERVE_REFERENCED）**；仓内 0 删除/0 移动/0 归档。

## 7. 下一队列

L-R11 gate 统一（scope review r1 已出：recommended，建议 C-16 v1.7 1 pin UNFREEZE PREREQ + Core-only 实现）→
C-04b residual（文档卡）→ SCAN-RH（RH-1…RH-5）→ UI P3（`FEA-12-UI-RESIDUAL-1` 已 done，需确认是否仍有残余）；
B2 `roots_available` 延后（无消费者）。
