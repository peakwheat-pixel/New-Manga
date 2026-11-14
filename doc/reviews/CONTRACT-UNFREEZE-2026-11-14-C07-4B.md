# CONTRACT UNFREEZE：C-07 API Inventory（v1.10，2026-11-14）

- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（冻结记录 [`doc/plan/FEA-CONTRACT-FROZEN-C07.md`](../plan/FEA-CONTRACT-FROZEN-C07.md)）
- 关联卡：`FEA-06-RESIDUAL-4B`（实现卡，[卡面](../tasks/FEA-06-RESIDUAL-4B.md)）
- 授权：用户 2026-11-14 指令（撤销 Q7 `OUT`，走 C-07 additive UNFREEZE）→ [RO-1 重开裁决](MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md) §3 R2/R3 → [4A 预授权载体 v1.9](CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md) 写死的落地判据（成员表 #80 / 统计 80-87 / pin v1.10）
- 同型先例：[CONTRACT-UNFREEZE-2026-11-10-AI1](CONTRACT-UNFREEZE-2026-11-10-AI1.md)（实现落地翻转统计）、[CONTRACT-UNFREEZE-2026-11-14-C07-RO1](CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md)（预授权）

## 1. 变更范围（统计翻转 + 成员表纯 append）

| 项 | 旧（v1.9 冻结） | 新（v1.10 UNFREEZE） |
|---|---|---|
| 文件 sha256（pin） | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` | `498882eb17507b89db463eb7cc8eb4522af80783a92ba21f80a5229c6d66984f` |
| 统计行 | `IReaderProgressSink 1 / IHostController 79 / IRunController 6`，合计 `86`（另有 4 非方法成员） | `IHostController 80`、合计 `87`（4 非方法成员不变） |
| 正式成员表 | 79 方法 + 4 非方法成员 = 脚本 stdout 逐行一致 | **80 方法 + 4 非方法成员 = 脚本 stdout 逐行一致**（`ALL_MATCH: True`）；新增行 `| 80 | \`ListPageRegionTextsAsync\` | \`Task<RegionPageTextProjection?>\` |`，**旧 1–79 行逐字节未动、零重编号** |
| 变更类别 | 79 个中 36 基线 + 43 FEA 新增 | **80 个中 36 基线 + 44 FEA 新增**（+RO-1 1 个） |
| 「RO-1 计划追加」节 | 1 条预授权、尚未落地 | **已落地 1/1**（保留作历史口径，同「S5 计划追加」做法） |
| 状态行 / 生成日期行 | v1.9 链 | 追加 v1.10 注记与 v1.10 重跑记录 |
| 代码 | `IHostController` 79 方法（端口不存在） | 80 方法：`ListPageRegionTextsAsync` 落地于 `IHostController` + `HostController` + `NewManga.Host/HostRuntime.cs` + `NullHostController` + 测试 `FakeHostController` |
| 旧成员 / 旧签名 | — | **零改动**（无删除、无改名、无参数变更；纯 additive append） |
| 其他冻结契约 | — | **零改动**（C-01b…C-17、FEA-01 字节不变，其余 17 pins 不变） |

**差异指纹（可独立复现）**：`git diff --numstat doc/plan/FEA-C07_API_INVENTORY.md` = **+13 / −12**，全部为：① 正式成员表 +1 行（#80）；② 统计表 2 行（`80` / `87`）；③ 变更类别 1 行（79→80、43→44）；④ 状态行、生成日期行行内追加；⑤ 「RO-1 计划追加」节标题/导语/落地口径改写；⑥ §关系 1 条 bullet 更新。**无任何既有成员行被改写**。

## 2. 为什么必须 UNFREEZE（且为什么与代码同批）

1. **接口已变，统计必须跟上**：`tools/generate_api_inventory.py` 的计数**由源码 interface 块解析**（`generate_api_inventory.py:105-119`，源 `IHostController.cs`）。`FEA-06-RESIDUAL-4B` 第二刀（`fd4008ce3`）把端口加进接口后，脚本 stdout 立刻变成 `1/80/6 = 87`，而文档仍写 `79/86` ⇒ `--check` **EXIT=1**（`FAIL: IHostController: rendered 80 not in doc`）。
2. **`--check` 长期红违反治理门禁**：MAINT-1 AC2 要求四项治理门禁保持 EXIT 0；把红留到「最后一刀」会使 main 上的红线跨越两个 commit。故统计翻转必须**与接口变更同批原子完成**（本次在同一 commit 内补齐）。
3. **预授权判据就是本次落地内容**：v1.9 载体 §3 已写死「落地判据三件套」——成员表 #80、统计 80/87、pin v1.10。本次逐条兑现，未扩面。
4. **成员表取纯 append 而非「按逻辑位置插入」**：端口成员**追加在 `IHostController` 接口末尾**，使解析出的成员序号正好是预授权的 **#80**；若插在 `LoadPageRegionsAsync` 之后（逻辑相邻），该行会变成 #35 并把 35–79 全部重编号 ⇒ 与预授权的 #80 冲突，且让冻结契约产生 45 行无意义 churn。

## 3. 落地判据（v1.9 写死，本次逐条兑现）

| # | 判据 | 兑现 |
|---|---|---|
| 1 | `IHostController` 含 `Task<RegionPageTextProjection?> ListPageRegionTextsAsync(string pageId, IReadOnlyList<string>? regionIds = null, CancellationToken)` | ✅ 接口末尾（`IHostController.cs`）；无 `expected_revision` 参数 |
| 2 | 生产三处 + Null/Fake 实现，未就绪/失败一律 `null` | ✅ `HostController`（委派 runtime，`IsUiFacingFailure` → `null`）、`NewManga.Host/HostRuntime.cs`（`_readerIoGate` + `NotReady()`）、`NullHostController`、测试 `FakeHostController` |
| 3 | 重跑脚本、并入正式成员表 **#80**、统计 **80/87**、`--check` EXIT 0 | ✅ 实测 `1/80/6 = 87`，`OK: rendered counts match FEA-C07 doc` |
| 4 | 成员表逐行 = stdout（不只看计数） | ✅ 三接口逐行 `ALL_MATCH: True`（`IHostController` 84 行 = 80 方法 + 4 非方法成员） |
| 5 | pin 重算为 v1.10，v1.9 原值保留 | ✅ `498882eb…`（v1.9 `91e51ab7…` 在 §1「前一 pin（v1.9，保留原值）」行） |
| 6 | 独立字节级复核 + 重冻 | ⏳ **§6 `pending`**（本次未派发，作者不得自评） |

## 4. 不变量与门禁（本次 UNFREEZE 实测）

1. 旧 79 个 `IHostController` 方法 + `IReaderProgressSink` 1 + `IRunController` 6 的签名与返回类型**零改动**；4 个非方法成员（`Snapshot` / `Changed` / `StartRequests` / `ExportDirectorySuggestion`）零改动。
2. 正式成员表 = `python tools/generate_api_inventory.py` stdout **逐行一致**（`IReaderProgressSink 1`、`IHostController 84 行`、`IRunController 6`，`ALL_MATCH: True`）。
3. `python tools/generate_api_inventory.py --check` → **EXIT 0**，`OK: rendered counts match FEA-C07 doc`，实测 `1/80/6 = 87`。
4. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → **PASS (all 18)**，C07 = 新 pin `498882eb…`，其余 17 pins 逐项不变。
5. `pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md`）→ **PASS**。
6. 代码面：`dotnet build apps/desktop-avalonia/NewManga.sln` 0 error / 0 warning；新增端口测试 8/8 绿；App.Tests 897/0/11、Host.Tests 321/0/74、CoreClient.Tests 176/0/24。
7. **中间态登记**：4B 第二刀 `fd4008ce3` 提交时 `--check` 曾红（stdout 80/87 vs doc 79/86）；本 commit 原子补齐，红窗仅存在于该历史 commit，现网已绿。

## 5. 独立复核（必需）

- 按 C-07 冻结语义，本次 UNFREEZE 须由**未参与本卡写作与实现**的独立上下文 reviewer 复核（2026-10-31 裁决：独立性以上下文独立为准）。
- 复核面：§1 变更范围与差异指纹、成员表**逐行**= stdout（不是只看计数）、pin 三口径（工作树 / blob / 冻结记录声明）、「RO-1 计划追加」节落地标记与统计口径自洽、冻结记录 §1/§1B/§2/§3/§5 自洽、四项门禁与 `dotnet` 结果实测复跑。
- 结论（`approved` / `changes_requested`）**由复核者追写**到 §6 并同步冻结记录 §1B；**实现者不得代写 approved**。

## 6. 复核记录

**状态：`approved` —— 本 UNFREEZE 已生效并重冻（2026-11-14）。** 本载体与 `FEA-06-RESIDUAL-4B` 的实现同出自 DSH 派出的实施 Agent，故本 UNFREEZE 由**未参与实现的独立上下文**复核。

| 轮次 | 审查者身份与来源 | 被审 head | 结论 | P0/P1/P2/P3 | 门禁 |
|---|---|---|---|---|---|
| r1 | 独立上下文子 agent（`cc9fa3c4…`；未参与实现、未参与 4A 的 r1–r4；只读） | `5c84dc22f` | **`approved`** | 0 / 0 / 0 / 6 | 四门禁 EXIT=0；pin 三口径 `498882eb…`；成员表 `ALL_MATCH`（1 + 80 + 4 + 6，合计 87）；`tests/**` 零改动 |

- **纯 append 已被独立验证**：旧 79 方法行逐行 0 变更，唯一插入点即 #80，无隐式重编号；`numstat +13/−12` 与 §1 指纹 ①–⑥ 精确吻合。「声明置于接口末尾」被判定为**正当决定、不记 P2**（C# 接口成员顺序无语义；v1.9 预授权写死 #80；按逻辑位插入会重编号 45 行）。
- **中间态红窗已被精确界定**：经 blob 复算，`--check` 变红**恰好只有 `fd4008ce3` 一个 commit**（其父 GREEN 79/86 → 该 commit RED → `ba6136d0` 起 GREEN 80/87）；三处登记口径一致，既未把历史红说成当时正常，也未反向掩盖。
- **P3 六条**（登记、不阻断）：4A README 的 4B 前置数值未同步；gates 日志的构建/测试证据偏弱（1.32s 增量构建、warning 计数未捕获）；接口末尾可读性折衷；README 裁决主体称谓；`.gitattributes` 缺 `doc/plan/*.md eol=lf`（既有债）；载体 §1「行内追加」措辞实为行内改写。
- 结论：**满足「重新独立复核后重冻」条件**；pin 无需重算（`498882eb…` 仍为当前文件 SHA-256）。

## 7. 不构成什么

- 不构成「查看对照」UI 已完成（面板/交互属 4B 第三刀，AC3–AC5 未验收）；
- 不构成 `FEA-06` AC3 的状态变更（仍为 **PARTIAL**，直到 4B 集成验证通过并经 DSH 裁决）；
- 不构成对 `FEA-06-RESIDUAL-4B` 其余 AC 的通过声明；
- 不构成远端 push 授权；
- 不构成 FEA-15 正式验收。
