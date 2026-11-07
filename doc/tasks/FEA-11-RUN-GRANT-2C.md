---
id: FEA-11-RUN-GRANT-2C
title: 2C 长 Run 续期实现（Host-only 周期重铸 grant + 重发 AuthorizeSourceReadForRun；L-G1 降级）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；PREREQ `FEA-11-RUN-GRANT-2C-PREREQ-1` done（C-06 v1.3 + C-16 v1.6，2 pins，`7317837d5`）；权威 scope `2C-LONG-RUN-RENEWAL-scope-r1` + ZCode 裁决 `cbdf231a-…`（APPROVE 2 pins/方案 a）；旧别名 `FEA-11-2C-LONG-RUN-RENEWAL-1` 仅登记、不得并存；DSH D-1…D-10 见下
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RUN-GRANT-2C-PREREQ-1
base_commit: fdd170039
branch: null
worktree: null
integration_commit: 7c95bb3c4
delivery_head: 7c95bb3c4
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-RUN-GRANT-2C
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2C.md
  - doc/reviews/FEA-11-RUN-GRANT-2C-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2C-*.md
  - verification/FEA-11-RUN-GRANT-2C/**
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/RunGrantRenewalTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - tests/fea11/test_source_run_grant.py
out_of_scope:
  - C-06/C-16 契约字节（PREREQ 卡负责）；C-05/C-15/C-17/C-07/M2-C1
  - `src/**`（Core/Python）零 diff；Run wire/TTL≤300s/撤销/失联/错误闭集/能力
  - App/UI；自动重新授权；B2/folder/L-S4-1/L-R1/L-G16；真实用户数据；push
---

# FEA-11-RUN-GRANT-2C：2C 长 Run 续期实现（proposed 占位）

> **状态：`ready`；PREREQ（C-06 v1.3 + C-16 v1.6）已 done；按卡面 In/AC 实施（Host-only 续期）。**

## 目标（草案）

Run 由 Core 后台串行整跑，grant 在 dispatch 前一次性铸造（`SourceReadCoordinator.cs:586` `+300s`）→ 排队/长 Run 未开始或中途即失权（`PROVIDER_FAILED`/`DB_FAILED`）。实现 **Host-only 周期续期**：Run 非终态期间对同一冻结 `{command, scope}` 重铸 grant + 重发 `AuthorizeSourceReadForRun`（零 Core、零 Run wire、零新命令/能力/错误码）。

## 候选 Scope（待 PREREQ 后冻结；依据 scope review §3 + ZCode D-1…D-10）

- In：新 `RunGrantRenewal.cs`（interval=240s/maxRenewals=12/TimeProvider/HostOptions）+ `HostRuntime` 接线（`AuthorizeSliceAsync` 返回 `RunAuthorizationResult`，不得「发了就算成功」）+ `SourceReadCoordinator` 刷新/计数/停止条件（禁碰 `+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads`）+ dispatcher post-dispatch 钩子 + 单测 + `tests/fea11/test_source_run_grant.py` in-process fake clock 判别 + gated「同 scope 二次 mint+bind+可读」。
- Out：`src/**` 零 diff；Run wire/TTL/撤销/失联/错误闭集/能力；App/UI；自动重新授权；B2/folder/L-S4-1/L-R1/L-G16；真实用户数据；push。

## Acceptance Criteria（草案，PREREQ 后冻结）

- [x] **AC-2C-1 续期主 AC**：Run 非终态期间，同一冻结 `{command, scope}` 在 TTL 前被重铸并重发 `AuthorizeSourceReadForRun`；in-process fake clock 前推 300s+ 后页读/提交仍成功；判别性：删续期 → 回到 `PROVIDER_FAILED`/`DB_FAILED` RED。 <<MET>>
- [x] **AC-2C-2 不延长/不扩 scope/不改 command**：旧 grant `expires_at` 不变；每次新 grant id；scope/command 逐字节同值；判别性：复用旧 grant 或换 scope/command → RED。 <<MET>>
- [x] **AC-2C-3 撤销/漂移即停**：续期前重走 `Registry.Authorize`+facts；revoked/generation 漂移/根替换 → typed 停止、不发送、不自动重建 identity；判别性：绕过 Authorize → RED。 <<MET>>
- [x] **AC-2C-4 失败不放行/不自动重试成自动恢复**：续期失败 typed；不重试 reattest/不自动重新授权；整请求任一页不可授权 → 不发送部分映射。 <<MET>>
- [x] **AC-2C-5 预算/间隔**：`interval + 单轮 mint 时长 < 300s`；每轮单次发送（`_gate` 串行）；单轮超限 typed skip + 计数入 EV；不得并行绕 gate。 <<MET>>
- [x] **AC-2C-6 接线点/无 App 改动**：dispatcher post-dispatch 钩子；`HostCommandDispatcher.cs` 属 Host 内部零 wire；App 零 diff；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 既有值不变。 <<MET>>
- [x] **AC-2C-7 L-G1 只降级不关闭 + 不夸大**：STATUS/Handoff/EV 写「有续期 + 子限制」（单步 >300s/续期失败/L-G2/L-G9/L-R1/L-G16）；不宣称任意长 Run 可用/自动恢复/自动重新授权。 <<MET>>
- [x] **AC-2C-8 门禁**：pins 18/18（C06 v1.3/C16 v1.6 新值）；check（默认+`-TaskPath`）PASS；API；scope ⊆ allowed_paths、`src/**` 零 diff；全量 pytest/.NET 不降（起点重测）；跑后恢复 `verification/FEA-09`。 <<MET>>

## 依赖与下一步

- 依赖：`FEA-11-RUN-GRANT-2C-PREREQ-1`（done 后 DSH 冻结 release）。
- Release 后走实现 → 独立 Review → 集成门禁 → closeout → push。

## 交付记录（Owner 回填；不改 status）

- **交付完成（2026-11-07）**：`delivery_head=e5e9c4c52`；commit 链 `c40489b5d`（`RunGrantRenewal.cs` 新 + `HostRuntime`/`HostOptions`/`SourceReadCoordinator`（仅计数）/`HostCommandDispatcher`（result-carrying 预授权 + post-dispatch 钩子））→ `e5e9c4c52`（`RunGrantRenewalTests.cs` 13 例 + gated `Fea11RunGrantIpcTests` 同 scope 二轮 + `tests/fea11/test_source_run_grant.py` 3 例 fake clock）；随后同批 docs/evidence 提交（本卡面/Handoff/`verification/FEA-11-RUN-GRANT-2C/**`）。
- **AC 判定**：AC-2C-1…8 **全 MET**（逐项 `<<MET>>`；见 `verification/FEA-11-RUN-GRANT-2C/EV.md` §1）。
- **实跑门禁**：build **PASS 0/0**；Host 续期单测 **13/0/0**；回归 **32/0/7 skip**（gated 默认 skip）；gated 真 IPC **7/0/0**（同 scope 二轮 = 续期轮、new grant id、`bound_pages=1`、页可读）；定向 pytest **92 passed**；全量 pytest **3363/10**（起点 3360/10，+3 本卡）；全量 .NET **1674/0/96**（起点 1661/0/95 → +13 单测、+1 新 gated skip；Lead 给定基线 1660/0/95 亦不降）；pins **18/18**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope **PASS**（delivery ⊆ allowed_paths、`src/**` 零 diff、禁止面零 diff、卡 status 未改）；判别性 **7/7 RED_AS_EXPECTED**；跑后 `verification/FEA-09` CLEAN。
- **before/after**：in-process fake clock（真实装配）窗口后读 `ProviderInputError`/提交 `SOURCE_ACCESS_DENIED`+零业务写 → 续期轮（新 grant + 同一冻结 `{command, scope}`）后读/提交恢复且旧 grant 不延长；不同 scope/command 的「续期」typed 拒绝且零映射。gated 真 IPC `logs/renewal-ipc.json`（2 帧 register（run 面增量）+2 帧 authorize、wire 无路径、`reattest_frames=0`）。
- **L-G1 口径**：**只降级不关闭**——「有续期 + 子限制」（单步 >300s / 续期失败 / L-G2 / L-G9 / L-R1 残余 / L-G16 / 未 dispatch 的 pending Run 不在范围）；未宣称「L-G1 关闭 / 任意长 Run / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。
- **Review r1 返修（2026-11-07，`7c95bb3c4`）**：P1-01 补 Host 接线判别（HostRuntime 安装行 seam + 3 用例；**Probe-C 复现**：修复前全量 Host 277/0/65 全绿 → 修复后 281/2/65，新接线用例 RED；恢复 sha256 MATCH 并复绿）；P2-01 round budget 改为进入单轮前传入 mint 路径（on-demand 冷扫描 timeout=min(30s,剩余预算)，耗尽即停；超预算 → `SkippedBudget` typed skip + 计数、保留跟踪）；P3（预算 mint 计数、LedgerStatus 接线、EV/Handoff 填实、manifest 去 `__pycache__`/可到达 head、FROZEN-C16 由 Lead 处理）；判别性 **9/9**。
- **证据目录**：`verification/FEA-11-RUN-GRANT-2C/`（`EV.md`、`RESOURCE-MANIFEST.json`、`scope-validation.log`、`changed-files.txt`、`logs/**`（含 `probe-c.log`）、`tools/**`）。未 push、未建 worktree；`status` 未改（由 Lead 维护）。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/changed-files.txt | 03361fec6 | eb26ea60617a2e9b7a666fbf0b6b8de80711e57cf8e019f67394801c9e0c641b | CANONICAL |
| EV-02 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/EV.md | 03361fec6 | 585436cc4b934a6e26fe0c6a103284111092c3aee9db49bc26e73f1b7715ec87 | CANONICAL |
| EV-03 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/build.log | 03361fec6 | f3cb468dbe23391fa9cb74d17f390191a216a9278420bb62aff171e7c6d50b2a | CANONICAL |
| EV-04 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/discrimination.log | 03361fec6 | 9b4406f0aa022b9e01623c5debe18be9dda3aee811ab3c2c7cf37c56519a1fb2 | CANONICAL |
| EV-05 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/full-dotnet.log | 03361fec6 | dd7e46127d407a470947dd11bc7672c0747d10c03de269e9c3053ea338e8cc3b | CANONICAL |
| EV-06 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/full-pytest.log | 03361fec6 | 30c62ee5fcc193727d7f805cded4b42f8cdea6862574998a69cfb6168a61276d | CANONICAL |
| EV-07 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/gates.log | 03361fec6 | 07ac806f17772df249e36753bb4aa940b52c9f961f491ec4130d89f8fda40498 | CANONICAL |
| EV-08 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/host-ipc.log | 03361fec6 | cc4dcf0a64d08ff1cb265304012c9a1cfd0d7eac9b0d4f3de8c58085cdbe779e | CANONICAL |
| EV-09 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/host-unit.log | 03361fec6 | 5afd9b09181b3dee553f115f026d062ad36218ddd55b0e2b4a06cf05671e825a | CANONICAL |
| EV-10 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/ipc-fixture.txt | 03361fec6 | 20fc0a1153035eb0e73c29e9f562e2bf74af6ce7e029895014eb50a505dab83b | CANONICAL |
| EV-11 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/probe-c.log | 03361fec6 | 7d1b4b018556ec6dde9f245458db18274286c507bb3cf86c7d6625ce9273300b | CANONICAL |
| EV-12 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/regression-74.log | 03361fec6 | b855a67151dcf45ac07cdafcd6b86872ccffc6f9b7fb73eac32e5ea8cdbafb6d | CANONICAL |
| EV-13 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/regression.log | 03361fec6 | 30a3eb3c5d090d377280d68a0fa2acf6ce57cfc5f6f26424feea84bb65f590c4 | CANONICAL |
| EV-14 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/renewal-ipc.json | 03361fec6 | 0bde5be43ae78cd153eecf551dc4b77715c5853c3118c63cc2e982a5ace1d01e | CANONICAL |
| EV-15 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/logs/renewal-ipc.txt | 03361fec6 | 98d7ef5dfce10b25c90352bf60c675f77b1e7e02ca78051aa6308215277a0392 | CANONICAL |
| EV-16 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/RESOURCE-MANIFEST.json | 03361fec6 | 82312ddc54e69a0cd07685735e3e03b1bc8ae7fa19483e917d693925d096e386 | CANONICAL |
| EV-17 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/scope-validation.log | 03361fec6 | 58e56d4e48b8d1bf16372436a6ea7a25df9f3e3cb4eff3033f5a8d14b4c35f11 | CANONICAL |
| EV-18 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/tools/discrimination.py | 03361fec6 | e84d0f71cacba276cb44c875402db0202b338b7cf6ab1c1ae07d71650d8be845 | CANONICAL |
| EV-19 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/tools/gen_manifest.py | 03361fec6 | 6ddcf3070050f5bf759e869ff88c47eb0e98d55ad2368a6fcbf5a0102f6dd4e5 | CANONICAL |
| EV-20 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/tools/probe-c-apply.py | 03361fec6 | 0caceb6e7bd554818b62baff9ee005825e36cfa10232560d9234841f28809011 | CANONICAL |
| EV-21 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/tools/probe-c-restore.py | 03361fec6 | 31eefb243b269a08e3f59d124ae00c2014873f89928be708f82f1d5a3a19fb1e | CANONICAL |
| EV-22 | AC-2C-1..8 | verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py | 03361fec6 | 67e7f52c55a9926595147666257c923057fb059093e31bb3c969a0d6d2d761b2 | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；未提交任何被删/被移文件；工作区 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\`（fixtures/review-r1/review-r2/tools/lead-r2-gates）为测试夹具与审查备份，保留（PRESERVE_REFERENCED）；无残留进程 |

## Closeout Record（2026-11-07；Lead）

- **状态**：`done`；`delivery_head`/`integration_commit` = **`7c95bb3c4`**（r1 返修交付，含 P1-01 Host 接线判别 + P2-01 轮前预算 + P3 处置）；初版实现链 `c40489b5d`（引擎+接线）→ `e5e9c4c52`（测试）；证据提交 `03361fec6`；收尾交接 `3945e1f5c`。
- **AC 判定**：AC-2C-1…8 **全 MET**（r2 复核确认；AC-2C-1/AC-2C-6 附 **R2-01 P2 证据缺口** limitation，不改变 MET 语义判定）。
- **Review 链**：r1 `doc/reviews/FEA-11-RUN-GRANT-2C-r1.md` **changes_requested（P0=0/P1=1/P2=1/P3=5）** → 返修 `7c95bb3c4` → r2 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md` **approved（P0=0/P1=0/P2=1/P3=7）**；r2 reviewer = fresh subagent（session `a4410d0a…`，独立上下文、未参与实现/返修）。
- **Lead 集成门禁（2026-11-07 实跑，repo root）**：build **0 warning/0 error**；Host `--filter "FullyQualifiedName~HostWiring|FullyQualifiedName~RunGrantRenewal"` **19/0/0**；**Probe-C** `281 passed/2 failed/65 skipped`（2 failed 恰为 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` + `HostWiring_ManagedOnlyRun_StartsNoRenewal`）→ 恢复 sha256 `bae563e1…` MATCH、git blob `0098ff5f…` → 复跑 **19/0/0**；gated 真 IPC（`NEWMANGA_FEA11_IPC=1`）**7/0/0**；fake clock **3 passed**；全量 pytest **3363 passed/10 skipped EXIT=0**；全量 .NET **1680 passed/0 failed/96 skipped EXIT=0**；pins **18/18**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope **PASS**（changed=32 全 ALLOWED、`out_of_scope=[]`、`forbidden=[]`、`src/**` 零 diff、pins_ok/blob_ok）；跑后 `git checkout -- verification/FEA-09` 已恢复（工作树 clean）。
- **R2-01（P2）处置 = 登记 limitation + follow-up，不重开实现**：3 条 HostWiring 用例驱动 `HostRuntime` 生产方法（`RunAuthorizeWithResultAsync`/`RunDispatchedAsync`/`TickAsync`，renew=真实 `RenewRunGrantsAsync`），但**未穿过** `StartInternalAsync` 安装调用点、dispatcher 构造的 `runDispatched:` 参数、`AcceptRunAsync` 启动调用点；r2 附加删除这 3 处调用点后全量 Host 仍 283/0/65 全绿。**当前代码行为正确**（功能方法与安装行已被 Probe-C 判别），风险是「未来误删生产调用点不会被测试发现」；按 P2 非阻断 closeout，登记 **L-2C-01**（调用点级判别 follow-up，候选独立小卡）。**不得据此宣称接线已被完整判别**。
- **P3 处置**：R2-05（EV/Handoff 口径滞后 7/7→9/9、`typed 停止`→`typed skip`、`delivery_head`、STATUS 基线 1674→1680）本次 closeout 一次清理；R2-02（生产 `ProbeRunLivenessAsync` 无测试）、R2-03（预算事后守护窄窗口可吞 typed stop code）、R2-04（全 skip 折叠丢失 `SOURCE_GRANT_REVOKED` 等 code）、R2-06（预算窗口未计 probe/mint 超时）、R2-07（manifest 历史提交行 sha 用最终快照口径）、R2-08（测试 seam public/`Untrack` 死代码）**全部保留为 P3 非阻断 limitation**，不伪造已修。
- **契约/范围**：零契约字节改动（pins 18/18，C-06/C-16 工作树字节 == 冻结 pin）；`src/**` 零 diff；App/UI 零 diff；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 既有值不变；`PROTOCOL_MINOR=3` 不变。交付 32 文件 ⊆ `allowed_paths`。
- **limitations（保留，不得夸大）**：**L-G1 只降级不关闭**——「有续期 + 子限制」（单步 >300s / 续期失败 typed 停止不重试不 reattest 不自动重新授权 / L-G2 加密源 / L-G9 Core 重启 / L-R1 viewer 残余 / L-G16 >4096 成员 / 未 dispatch 的 pending Run 不在范围 / L-G8 成本放大）；**预算 skip ≠ 续期成功 ≠ Run 失败**；**L-2C-01**（调用点级判别，R2-01）；R2-02…R2-08。**不写**「任意长 Run 可用 / L-G1 关闭 / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；工作区 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\`（fixtures/review-r1/review-r2/tools/lead-r2-gates）为测试夹具与审查备份，**保留（PRESERVE_REFERENCED）**，未删除。
- **push**：随本轮 Lead closeout 统一 push（PRE/POST hash、AHEAD 记录见 `doc/handoffs/DSH-HANDOFF-2026-11-06.md` §18）。
