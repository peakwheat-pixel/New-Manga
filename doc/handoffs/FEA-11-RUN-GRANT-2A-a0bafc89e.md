---
task_id: FEA-11-RUN-GRANT-2A
author: run-grant-2a-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 9ec4826d6
start_head: 1b6152112
delivery_head: a0bafc89ec74be08e3d6d721105639df01a140a7
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-RUN-GRANT-2A（Host Run source 版本通道；无 UNFREEZE）

- Task：`doc/tasks/FEA-11-RUN-GRANT-2A.md`（Owner=`run-grant-2a-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=9ec4826d6`；实现起点 `1b6152112`（工作树 clean，实测）；**`delivery_head=a0bafc89ec74be08e3d6d721105639df01a140a7`**
- 交付 commit：`aa0a5562b`（实现）、`a0bafc89e`（测试，**delivery_head**）；证据/卡/本 Handoff 为同批文档提交（未 push、未建 worktree）
- 环境：Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET（net9.0）；无新依赖、无 schema/migration/契约/wire 改动
- 依据：`doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（2A=READY-TO-FREEZE，零契约）+ 卡「DSH 裁决 S-1…S-6」+ `FEA-11-RUN-GRANT-1` 卡（L-G12①/L-G15 处置）

## 1. 交付结果（AC-G1…G8 全 MET；卡面已勾选）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC-G1 生产版本通道（P0） | **MET** | `SourceIdentityCache` 是 Run `scope.version` 的唯一来源；真实 IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember` 的 scan 目标 Version 全为生产占位 `"1"`，缓存值 `sv1`/`svf1`/`sv-img` 全部来自真实 `ScanSourceSync` 响应 → `bound_pages=1` → `resolve_page_resource` OK；判别性 B1/B6 |
| AC-G2 缓存新鲜度 | **MET** | 仅 `status=ok && changed=false` 可写入；`changed/encrypted/unsupported/missing/malformed` 一律 **invalidate**（fail-closed，不铸）；`MaxEntries=1024` / `MaxEntriesPerIdentity=4096` / `TTL=3600s`，`TryGet`/`Remember` 均裁剪；判别性 B2 |
| AC-G3 冷缓存策略 | **MET** | 每切片最多 8 个冷源、每源 1 次、30s 超时；失败/超时/预算耗尽 → warn + 跳过，**不阻断** managed-only Run；判别性 B3（冷缓存用占位版本 → managed Run 被阻断 RED）、B4（删除填充 → RED） |
| AC-G4 生产口径边界 | **MET** | image 单 entry + folder（逐成员）+ 归档首成员在**生产版本通道**下 resolve 成功；归档第 2 成员仍 typed `SOURCE_ACCESS_DENIED`（L-G12②/2B 未修）；未写「全场景可用」 |
| AC-G5 managed 零回归 | **MET** | RUN-GRANT-1 全部 best-effort 用例保留通过；新增冷缓存跳过/失败跳过用例；定向 pytest 50 passed、全量 pytest 3281/10 不降 |
| AC-G6 R3-02 收口 | **MET** | `AcceptRunAsyncDelegatesToTheAuthorizationSeam` 直接判别生产 `AcceptRunAsync` 的委托行；删除委托 → 落到「Core unavailable」→ RED（B5） |
| AC-G7 零漂移 | **MET** | scope `changed=5` 全 ALLOWED、zero-drift surfaces 全空、`protocol_minor=3`；pins 18/18；check（默认 + `-TaskPath`）PASS；API inventory EXIT=0 |
| AC-G8 门禁/不夸大 | **MET** | 全量 pytest 3281/10、全量 .NET 1559/0/90（基 1551/0/89）；EV 逐文件 sha256；本 Handoff limitations；未写 L-R1 修复 |

## 2. 验证证据（实跑；`delivery_head=a0bafc89e`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error** | — |
| 定向 Python（回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed** | `logs/feature.log` |
| Host 单测（AC-G2/G3/G6 + RUN-GRANT-1 回归） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 29 passed**（基线 21，+8） | `logs/host-unit.log` |
| 真实 IPC（AC-G1/G3/G4） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 4 passed**（基线 3，+1 生产版本通道；不设 env 时 4 skipped） | `logs/host-ipc.log` |
| 全量 Python（AC-G8） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped**（基线 3281/10，不降） | `logs/full-pytest.log` |
| 全量 .NET（AC-G8） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1559 / 0 / 90**（基线 1551/0/89：+8 单测、+1 opt-in IPC skip） | `logs/full-dotnet.log` |
| 治理（AC-G7） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-G7） | `python verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py` | **PASS（changed=5 全 ALLOWED；zero-drift 全空；minor=3）** | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-G1/G2/G3/G6） | `python verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py` | **6/6 破坏点 RED_AS_EXPECTED + 6/6 字节级 RESTORED + final rebuild EXIT=0** | `logs/discrimination.log` |

- **跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行 `git checkout -- verification/FEA-09`（`git status` 事后复查无 FEA-09 残留）。
- **共享工作树披露**：同一 `main` 工作树同期由 `FEA-11-RUN-GRANT-2B-PREREQ-1` 会话使用（C-16 v1.4 UNFREEZE，commit `d8dcfc07a`；本卡 commit 之后落地）。本卡 scope 校验**按本卡自有 commit 链**（`aa0a5562b`/`a0bafc89e`）计算，不包含该会话文件；本会话未修改/暂存/提交其任何文件。因此 `doc/plan/FEA-C16*` 在最终 HEAD 上并非零 diff，但**不属于本交付**（见 `scope-validation.log` 的 shared-worktree note）。
- 已知 flaky：全量 .NET 若在 `verification/` 正在写入时运行，`FluentResidual2VisualEvidenceTests` 会因 `git status --porcelain -- verification` 快照差异失败；本卡先落盘证据再跑全量，两次均未命中。

## 3. 已知 limitation（closeout 必须保留）

- **L-G15（本卡修复对象，历史登记保留）**：生产 Host `scope.version` 恒为 `"1"` → referenced Run dispatch 前 typed 拒绝；**本卡已修**（版本只来自 Core 权威扫描响应，禁止常量回退）。修复后仍需 2B 才能真正放开多成员容器。
- **L-G12②（2B，未修）**：多成员容器（zip/cbz/pdf）其余成员页仍 typed `SOURCE_ACCESS_DENIED`（Host 对容器仍只铸单 entry；Core 侧 1..N 语义属 `FEA-11-RUN-GRANT-2B-PREREQ-1` 的 C-16 v1.4 UNFREEZE 范围）。本卡真实 IPC 明确保留该 fail-closed 边界。
- **L-R1 未全修**：本卡只修「生产版本常量」这一条阻断；「referenced Run 全场景可用」**不成立**。可用边界 = image 单 entry 源 + folder 源（逐成员 entry 匹配）+ 归档首成员（生产版本通道下实证）。
- **L-G1**：单 grant ≤300s；窗口后提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑另卡。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）；扫描 `encrypted` 观测**不写缓存**（本卡 fail-closed 语义）。
- **L-G8（本卡延伸）**：冷缓存 on-demand 扫描使 Run 前置成本与源大小线性相关；单切片最坏 `8 源 × 30s` 显式预算（阻塞在 Run dispatch 前），未标定大库成本；周期扫描正常时缓存已暖，走不到该路径。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑；缓存是内存态，重启后需重新扫描填充（冷缓存路径已覆盖）。
- **L-G10**：L-R11（两读面 gate 差异）未碰。
- **L-G11**：binding 解析仍在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G13**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑。
- **L-G14**：`AcceptRunAsync` 仍需同进程先 `PrepareRunAsync`（缺失/过期 → `RUN_STALE_PREVIEW`）；本卡新增的 R3-02 测试即在此前提下判别委托行。
- **缓存语义显式选择**：`changed`/非 ok 观测对缓存的影响是 **invalidate**（不是"保留旧值"）——因为候选版本尚未被 Core 提交，保留旧版本存在版本行已退役时不匹配的风险；invalidate 后该源变 cold，按 AC-G3 跳过（不铸、不阻断 managed-only Run）。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `1b6152112`；**delivery_head=`a0bafc89ec74be08e3d6d721105639df01a140a7`**（未 push、未建 worktree）。
- 复现：
  1. `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` → 成功（0 warning/0 error）
  2. `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **50 passed**
  3. `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` → **29 passed**；`$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` → **4 passed**
  4. `pytest tests -q` → **3281 passed / 10 skipped**（跑后 `git checkout -- verification/FEA-09`）；`dotnet test NewManga.sln -c Release` → **1559 / 0 / 90**（跑后同样恢复）
  5. pins/check/API inventory/scope/discrimination 同 EV §2/§6。
- 接收者下一步：①独立上下文 Review（AC-G1 生产版本通道 IPC、AC-G2 缓存矩阵、AC-G3 冷缓存判别、AC-G6 R3-02 委托行、AC-G7 共享工作树披露）；②核对 `EV.md` 每文件 sha256；③Lead 集成验证与 closeout（本卡 `status` 未改）。

## 5. 下一任务建议

- **无释放**（本卡 Review/集成前不释放后续实现卡）。可并行/顺序候选：`FEA-11-RUN-GRANT-2B`（容器成员 entry 通道；其 C-16 v1.4 冻结前置 `FEA-11-RUN-GRANT-2B-PREREQ-1` 已由另一会话提交 `d8dcfc07a`，由 Lead 判定是否释放）、L-S1（registry resilience）、L-G1（长 Run 续期设计卡）。均由 Lead 决定。
- Reviewer：由 DSH 指派**独立上下文**（非本实现会话；fresh subagent 或未参与实现的 ZCode/Codex）。

## 7. Review r1 处置补充（DSH，2026-11-07）

- 独立 Review r1：`doc/reviews/FEA-11-RUN-GRANT-2A-r1.md`（approved；P0=0/P1=0/P2=2/P3=6；AC-G1…G8 MET；4 个破坏点独立 RED+RESTORED）。
- R2A-01 已修（Manifest `delivery_head` → `a0bafc89e…`；原 repo HEAD 保留 `repo_head_at_generation`）。
- R2A-02 以**文档边界**关闭：`>4096` 成员的 folder 源不缓存、每 Run 重扫且不铸造（fail-closed）→ **L-G16**；不宣称 folder 全量可用。
- R2A-03…R2A-08 登记接受/后续（详见 EV §7.1）；不改变实现/测试字节与 AC 判定。
- 保留：L-G12②（多成员容器）、L-R1 未全修、L-G1/L-G2/L-G8/L-G9/L-G10/L-G13/L-G14；本卡只修 L-G15（生产版本常量）。
