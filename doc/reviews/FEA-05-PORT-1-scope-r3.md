---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: d647805a0
reviewed_head: e77e1baf5
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 6 }
---

# FEA-05-PORT-1 范围复核 r3（独立上下文，未参与本卡）

| 字段 | 值 |
|---|---|
| base_commit | `d647805a08eb5f8456270566ac991436edb1c391`（范围 v2 被审 head） |
| reviewed_head | `e77e1baf5de0513dc359946e7e681a7372847357`（`docs(fea-05-port-1): 范围 v3…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-PORT-1.md`（110 行，status=proposed）；同提交另收编 r2 报告 |
| reviewer | `fea05-wire-scope-reviewer`（Draft 线 FEA-05-WIRE-1 范围 r1–r7 与实现 impl-r1–r3 同一席位；**本卡未参与者**） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | r2 的 P1×2 是否关闭、P2 逐条 disposition、AC1–AC7 可验收性、写域（尤其 C-07/UNFREEZE 两冻结物）、新问题 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 6（共 7）** |

> **一句话理由**：r2 的两条 P1 **均已关闭**（AC1 ③ 数字改为 47→54 / 54→61 并补齐成员表/变更类别；AC2/W-2/P3 统一为「7 端口方法 ↔ 6 wire 命令」，W-2 给了 XOR）✓；写域两冻结物齐全 ✓。**但 P2 表新冻结的 nullability 与 `NullHostController` 默认自相矛盾**：`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync` 的返回类型写成**非可空** `Task<DraftLease>`/`Task<Draft>`/`Task<RegionCandidate>`，而同一格的 Null 默认明确返回 **null**（`Task.FromResult<DraftLease?>(null)`、Patch/Prepare→null）。本项目 `Nullable=enable` + `TreatWarningsAsErrors=true`（`Directory.Build.props:7/10`），按卡实现会触发 CS8619 类警告并**编译失败**；且与既有「可空返回用 `Task<T?>`」约定不符（`IHostController.cs:147/161/186/191`）→ **P1-01**。另有 6 条 P2（`备注` 节再次出现 literal `\n`、AC6 措辞、冻结矩阵、`All` 语义、DTO 外形、AC1 ② pin 措辞）。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `e77e1baf5…` / 空（clean） |
| `git diff --stat d647805a0..e77e1baf5` | 2 files：卡（+24/−10 改写）、r2 报告（+123） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态 Task；STATUS 3154/34（80%）；PLAN 3751/51（80%） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0**（渲染 `IHostController 47` / 合计 `54`，与 AC1 ③ 的基线一致） |
| 关键源码核对 | `Directory.Build.props:7`（`Nullable=enable`）、`:10`（`TreatWarningsAsErrors=true`）；`NewManga.App.csproj:25`（仅 `PublishTrimmed=true` 时关）；`IHostController.cs:147/161/186/191`（可空返回用 `Task<T?>` 的既有约定） |

---

## 1. r2 逐项 disposition

| r2 ID | 级别 | 状态 | 证据 / 缺口 |
|---|---|---|---|
| **r2-P1-01** C-07 数字错 | P1 | **CLOSED** | AC1 ③（`:67`）已改「现网 IHostController **47**、合计 **54** → 加 7 方法后 **54**、合计 **61**；成员表 +7、变更类别 11→18、生成日期/HEAD 刷新」，与实测（脚本渲染 47/54）一致 ✓ |
| **r2-P1-02** 6 vs 7 方法矛盾 | P1 | **CLOSED** | AC2（`:68`）改 **7 方法**并注明 C082 拆 `GetDraftAsync`/`ListDraftsAsync` 共发 `drafts_status`；W-2（`:85`）名单 7 个 + XOR；P3（`:60`）/AC3（`:69`）保持「6 条 wire 模型/注册」并区分 ✓ |
| r2-P2-1 契约 5 站点/DraftsCommandNames 归属 | P2 | **CLOSED（措辞小瑕）** | P1（`:58`）已列 5 处：①头部状态/版本 ②清册加 `DraftsCommandNames` ③不变式并集 ④§8 验证表 `:457` ⑤变更记录 ✓；仅「§命令清册」这一称谓与契约实际节名（§1.1 `:62-63`/§4 `:344-346`）不完全对应 |
| r2-P2-2 registry `All`/XOR | P2 | **PARTIAL** | XOR 已写入 P3（`:60`）✓、两方法共用 `drafts_status` 已由 W-2 说明 ✓；`All` 仍只写「`All`/域枚举/`CoreBindings`/`AddDomain` 同步」，未澄清是既有 `HostCommandRegistry.All` 字典还是新聚合属性 |
| r2-P2-3 Studio 写域矛盾 | P2 | **CLOSED** | `allowed_paths`（`:21-38`）已删除 Studio 路径 ✓，与禁止范围「不接 UI 交互」不再冲突 |
| r2-P2-4 STATUS 指针 | P2 | **CLOSED（改由 DSH 收口）** | 卡新增「备注」（`:108`）承接「STATUS/PLAN/LEDGER 指针：本卡完成后由 DSH 同步」✓；**STATUS 实际文本仍为旧行**（`:7` 重复句、`:10`「待建卡」），需 DSH 收口时兑现（另见下方 P2-1 结构损坏） |
| r2-P2-5 AC6 措辞 | P2 | **OPEN** | AC6（`:72`）仍为「不退化（基线 931/0/60）」，测试要求（`:96`）亦同；未改成「0 failed；总数 ≥931，新增测试不计退化」 |
| r2-P2-6 冻结矩阵 | P2 | **OPEN** | 卡与「备注」均未提 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（`:25`/`:71` C-07 `FROZEN` 行）是否随 re-freeze 更新；写域仍无该文件 |
| r2-P2-7 literal `\n` 结构损坏 | P2 | **PARTIAL（复发）** | 前置（`:49-52`）已恢复真实换行 ✓；但新增「备注」**又**以一行字面量写 `## 备注（收口时 DSH 处理）\n\n- …\n- …\n\n## Closeout Record`（`:108`，全文 5 处 literal `\n`）——`## 备注` 与 `## Closeout Record` 两个标题被吞进同一行，结构再次损坏 |
| r2-P2-8 `DraftPatch` 同名 | P2 | **CLOSED** | 已改名 `DraftPatchRequest`（`:59` 两处签名 + DTO 列表 + 显式理由「避免与 `NewManga.ApplicationCore/DraftBuffer.cs:21` 的 `DraftPatch` 同名」）✓ |
| r2-P2-9 Null 风格/DTO 外形 | P2 | **PARTIAL（并引出 P1-01）** | 「不抛异常，遵守 never throws」已改 ✓；但 null 默认与**非可空**签名冲突（见 P1-01）；`DraftLease` 三字段（wire `draft/canEdit/token`，`core_service.py:3015-3018`）、`DraftPatchRequest` 字段、`DiscardDraftAsync` 丢弃 `{discarded}` 仍未列 |
| r2-P2-10 P5 措辞/AC1 ② | P2 | **PARTIAL** | P5（`:62`）已改「手工更新 `FEA-C07_API_INVENTORY.md`（脚本只 print，不生成）→ `--check` EXIT 0」✓；AC1 ②（`:67`）仍写「两份冻结物的…新 pin 值」——Region 契约无 pin，pin 值仅 C-07 有 |

---

## 2. 关键核查

### 2.1 P1-01：签名与 Null 默认的 nullability 冲突（新）

- 卡 P2（`:59`）冻结的三处返回类型为**非可空**：`Task<DraftLease> OpenDraftAsync(...)`、`Task<Draft> PatchDraftAsync(...)`、`Task<RegionCandidate> PrepareCandidateAsync(...)`。
- 同一格随后要求 `NullHostController` **逐方法安全默认（不抛异常）**：`Open→Task.FromResult<DraftLease?>(null)`、`Patch/Prepare→null`。
- 项目设置：`apps/desktop-avalonia/Directory.Build.props:7` `<Nullable>enable</Nullable>`、`:10` `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`（`NewManga.App.csproj:25` 只在 `PublishTrimmed=true` 时才关闭）；现有约定也是「可能返回 null 的方法用 `Task<T?>`」（`IHostController.cs:147` `Task<ChapterSummary?>`、`:161`、`:186`、`:191`）。
- 结论：按卡直写 `Task.FromResult<DraftLease?>(null)` 返回给 `Task<DraftLease>` 会产生 CS8619（嵌套 nullability 不匹配）类警告 → **TreatWarningsAsErrors 下编译失败**；要么实现者被迫改冻结签名（越权），要么写 `null!`/假对象绕过（与「null 语义」矛盾）。AC2「7 方法 + Null 默认」因此**不可机械验收**。
- 建议二选一：**(a)** 三个返回类型改 `Task<DraftLease?>`/`Task<Draft?>`/`Task<RegionCandidate?>`（与既有可空约定一致，Null 返回 null 自然成立）；**(b)** 保持非可空，但 Null 返回**非 null 默认对象**（需定义默认值语义，成本更高）。推荐 (a)，并在 AC2/W-2 同步。

### 2.2 写域（C-07 / UNFREEZE 两冻结物）

- `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` ✓（`:23`）、`doc/plan/FEA-C07_API_INVENTORY.md` ✓（`:24`）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md` ✓（`:25`）、`doc/reviews/CONTRACT-UNFREEZE-*.md` ✓（`:26`）、端口三实现 ✓、`NewManga.CoreClient/**` ✓（`DraftCommands.cs`）、两个测试工程 ✓、`verification/FEA-05-PORT-1/**` ✓、指针 ✓、`doc/reviews/FEA-05-PORT-1-*.md` ✓。
- 仍缺：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（P2-3，是否更新待 DSH 决定）。
- `FEA-05_DRAFT_WIRE_CONTRACT.md` 与总契约 §8.2：**备注（`:108`）已明确由 DSH 收口升级**，不属本卡写域，可接受 ✓。

### 2.3 AC 可验收性

| AC | 判定 | 说明 |
|---|---|---|
| AC1 契约 UNFREEZE（两冻结物） | **可验收** ✓ | 数字正确（47→54、54→61）；两冻结物、UNFREEZE 记录、独立复核、`verify_pins` 15/15 均在卡/写域内；仅 AC1 ② pin 措辞待正（P2-6） |
| AC2 端口面 | **不可验收（P1-01）** | 7 方法已统一；但 Null 默认与签名 nullability 矛盾，按卡直写会编译失败 |
| AC3 registry | **可验收** ✓ | 6 wire 条、`V11RAdditiveCommandNames`=17、XOR、parity 派生断言均可行 |
| AC4 契约测试 | **可验收** ✓ | `:109`（17）+`:110-114`（Region 子集）+`DraftsCommandNames ⊆ additive` 成立；`CommandContractV11Tests` 不受影响（6 条已声明且注册后 IsImplemented=真） |
| AC5 端口清单 | **可验收** ✓ | 人工更新 C-07 + `--check` EXIT 0；写域已含该文件 |
| AC6 回归 | **可验收（措辞待补）** | 命令可跑；「不退化（基线 931/0/60）」未说明总数变化（P2-2） |
| AC7 证据 | **可验收** ✓ | `verification/FEA-05-PORT-1/**` 在写域 |

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P1-01** | P1 | 卡 `:59`（P2 签名 + Null 默认）、`:68`（AC2）；`Directory.Build.props:7/10`；`IHostController.cs:147/161/186/191` | **nullability 自相矛盾**：`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync` 返回非可空 `Task<DraftLease>`/`Task<Draft>`/`Task<RegionCandidate>`，但 Null 默认返回 null；`Nullable=enable` + `TreatWarningsAsErrors=true` 下按卡实现会 CS8619 → 编译失败；改签名则超出冻结范围 | 三处返回类型改 **可空**（`Task<DraftLease?>`/`Task<Draft?>`/`Task<RegionCandidate?>`），或 Null 改返回非 null 默认对象；同步 AC2/W-2 与「null 语义」注释 |
| P2-1 | P2 | 卡 `:108`（备注） | 备注节仍以字面量 `\n` 写在一行（全文 5 处），`## 备注` 与 `## Closeout Record` 标题被吞；r2-P2-7 复发 | 用真实换行重排「备注」节与 `## Closeout Record` 标题；提交前 grep `\\n` 自检 |
| P2-2 | P2 | 卡 `:72`（AC6）、`:96` | AC6 仍「不退化（基线 931/0/60）」，未说明新增测试使总数上升 | 改「0 failed；总数 ≥931（新增测试不计退化）」 |
| P2-3 | P2 | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:25`/`:71`；卡 `:63`（P6） | re-freeze 是否更新冻结矩阵未定，写域也没有该文件 | DSH 明确「不更新（只改 FROZEN-C07 记录）」或加入写域 |
| P2-4 | P2 | 卡 `:60`（P3） | `All` 语义仍含糊（既有 `HostCommandRegistry.All` 字典 vs 新聚合属性）；`AddDomain`/`CoreBindings` 仅列名未给映射要点 | P3 写明 `All`=既有 registry 字典；`CoreBindings` 6 条 `drafts_*`→`drafts_*`、minor 3 |
| P2-5 | P2 | 卡 `:59`；`core_service.py:3015-3018`；`FEA-05_DRAFT_WIRE_CONTRACT.md:26-31` | DTO 外形未列：`DraftLease` 三字段（draft/canEdit/token）、`DraftPatchRequest` 字段、`DiscardDraftAsync` 丢弃 `{discarded}` 的理由 | 按 wire §2/to_json 列出字段；C083 可改 `Task<bool>` 或注明丢弃理由 |
| P2-6 | P2 | 卡 `:67`（AC1 ②） | 「两份冻结物的…新 pin 值」——Region 契约无 pin，仅 C-07 有 | 改为「新 pin 值（仅 C-07；Region 契约以状态行+变更记录体现）」 |

---

## 4. 处置建议

1. **P1-01 先修**（唯一阻塞）：把三个 null 默认方法的返回类型改可空（推荐），或把 Null 默认改成非 null 对象；同步 AC2/W-2/「null 语义」。
2. **P2-1（备注 literal `\n`）建议本轮修**：这是 r2-P2-7 的复发，说明生成流程仍会写出字面量转义；建议提交前对卡跑一次 `\\n`/`\\r` 自检。
3. 其余 P2：AC6 措辞（2）、冻结矩阵（3）、`All`/`CoreBindings` 细节（4）、DTO 外形（5）、AC1 ② pin 措辞（6）。
4. 改卡后派 **r4** 复核；P0/P1=0 后 DSH 置 `ready` 并派实现。

## 5. 边界声明

本报告只审范围冻结（Task 卡文本及其引用的契约/代码/测试/治理事实），**不构成实现验收**，也不构成 UNFREEZE 或契约修订批准。本席位未参与 FEA-05-PORT-1 的起草/实现/返修；未修改被审文件、未 commit/push；行号基于 `e77e1baf5` 实测。
