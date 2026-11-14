---
verdict: ACCEPT_WITH_LIMITATIONS
task: READER-PREF-PERSIST
review_round: r2
reviewer: review-reader-pref（独立上下文子 agent，未参与实现与本轮返修）
target_head: 98d42c6b6228137278531096d8082e3ed9b6f5e0
base: eebfedf6d
prev_review: doc/reviews/READER-PREF-PERSIST-review-r1.md（verdict REJECT，被审 head 57f149b）
review_date: 2026-11-15
mode: 只读复核（仓库内仅写本报告）；实验在 git archive 沙箱内完成
---

# READER-PREF-PERSIST 独立复核 r2

## 0. 审查者身份与来源

- 审查者：`review-reader-pref`，由 DSH 主会话派发的**独立上下文子 agent**；未参与实现，也未参与本轮 r1 返修。
- 被审 head：`98d42c6b6228137278531096d8082e3ed9b6f5e0`（`fix(reader-pref-persist): r1 复核 REJECT 返修`），基线 `eebfedf6d`。
- 工作区核对：复核开始时 `git status --short` **为空**（r1 的 P1-3 已消除）；r2 为单一提交，改动 8 个文件且全部落在 `allowed_paths`。
- 复核方式：读 diff/代码 + 在 `git archive 98d42c6b6` 解包的沙箱里跑定向与变异实验（5 个源文件 `git hash-object` 与 HEAD blob 逐一核对）+ 在**仓库干净树**跑全量 App.Tests。

## 1. 结论

**ACCEPT_WITH_LIMITATIONS**。r1 的 3 个 P1 全部真实修复且有判别力：View 回退基线后新增的 4 个接线测试 **4/4 变红**；把 P1-1 的快照写法回退后新测试 **变红（1.5 vs 1.7）**；切书目标书已由意图捕获固定（我实测写对旧书）。全量 App.Tests 我在仓库干净树亲自跑出 **946/0/11**（与声称一致）。没有残留 P1。

保留一项 P2 与若干 P3（不影响主路径，但建议在收口前处理或明确登记）：意图捕获了值与目标书，却**没有捕获 diff 基线**——若在 80ms 合并窗口内切书且新书快照恰好等于旧书意图，差分为空、旧书的这次修改会被静默丢弃（我实测 0 次写入）；另有异常路径的状态文案越界、无偏好书不清状态、View 覆盖只点到每个名字的第一个按钮（其中一个测试名与实际点击位置不符）、AC1–AC3 的"重开读回"半边未端到端验证但卡面已勾、证据日志仍是 r1 的 940 数字等问题。

## 2. r1 findings 逐项验证

| r1 finding | 处置声明 | 我的独立验证 | 判定 |
|---|---|---|---|
| **P1-1** 在途保存丢更新 | 改为只记录实际发送过的字段 | 沙箱把 `_appliedPreferences` 改回"await 后当前值"写法 → `ChangeMadeWhileASaveIsInFlight_IsStillPersisted` **红**（`Expected 1.7 / Actual 1.5`），其余 7 绿；当前写法下同一测试绿 | **已修且已固定** |
| **P1-2** AC4 证伪（View 无覆盖） | 新增 4 个 `[AvaloniaFact]`；双击改接 | 沙箱把 `ReaderPageView.cs` 换回基线 blob `94ef2163` → `ReaderPreferenceWiringTests` **4 failed / 0 passed（33 s）**；当前 View 下 4/4 绿 | **已修且已固定** |
| **P1-3** 工作区与 HEAD 不一致 | 单一提交 | 复核起始与结束时 `git status --short` 均为空；r2 提交含全部改动 | **已修** |
| **P2-1** 目标书在写时才读 | 意图里带 `BookId`，drain 只用捕获值 | 探针：80ms 窗口内切书后，写入的 `bookId` 是**旧书**（修复生效）；但同探针还暴露 diff 基线仍是"当前书"的（见 P2-1 残留） | **部分修（目标书已对，基线未捕获）** |
| **P2-2** 失败状态不随换书重置 | `ApplyReadingPreferencesAsync` 末尾清空 | 探针：切到**有**偏好的书 → 已清空（修复生效）；切到**无**已存偏好的书 → 旧"保存失败"文案残留（`Apply` 在 `preferences is null` 时早退，`:152-156`） | **部分修（P3-2）** |
| **P2-3** drain 无 try/catch 会卡死 | 捕获异常并置文案 | 探针：host 抛 `InvalidOperationException` 后状态显示失败，且**后续点击仍能继续保存**（写入计数 +1、值为 1.6）→ 不卡死；但异常路径在判断"书是否已切"**之前**打状态（见 P3-1） | **已修（残留 P3-1）** |
| **P2-4** AC6 断言 0 次写入也过 | `Assert.InRange(count, 1, 2)` | 代码核对：0 次写入必红；6 连点实测 1 次写入 | **已修** |
| **P3**（SettleAsync／卡面／证据 pick／flush／Load 重置） | 部分修 | `SettleAsync` 的续体等待只加在 View 测试；卡面已回填但 AC1–3 读回半边过度声称；`regression.log`/`four-pieces.log` 未随 r2 重新生成；flush 未做（已登记）；`_appliedPreferences` 在无偏好书时仍未重置 | **部分** |

## 3. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 单双页 | **PASS（写侧）** | 顶栏按钮（`ReaderPageView.cs:275`）与**页面双击**（`:180`，r2 新接）都走 persisting；VM 测试 + View 测试判别力实测有效。双击本身无测试；"重开读回"未端到端（E-2）。 |
| AC2 方向 | **PASS（写侧）** | 顶栏（`:276`）与浮动条（`:396`）均接；View 测试点第一个入口，浮动条入口由我的探针实测可保存。读回半边同上。 |
| AC3 缩放 | **PASS（写侧）** | 浮动条/底栏/键盘 7 处入口全接（`:393-395`、`:420-422`、`:712/717/722`）；无 `ZoomBy(`/`ResetZoom()` 残留。我的探针实测底栏放大/重置均保存。读回半边同上。 |
| AC4 判别测试 | **PASS** | 实验 B：View 回退基线 → 4/4 红。覆盖粒度仍有缺口（P3-3），但"控件路径"这一层已被固定。 |
| AC5 失败可见 | **PASS**（VM 侧） | 失败/异常均不改快照；两个 VM 测试判别有效。View 文案绑定（`PreferenceSaveStatusText`）仍无测试；两个边角状态场景未修（P3-1/P3-2）。 |
| AC6 不做过量写入 | **PASS** | `InRange(1,2)` 已能拒绝"0 写入"；我另测"同窗口两次修改 → 1 次写入、值=最新值 1.2"。测试本身未断言落库值（P3-5）。 |
| AC7 契约零变化 | **PASS** | `generate_api_inventory.py --check` exit 0、`1/80/6=87`；`Skip =` 源级 11→11；`check.ps1` PASS(3 warnings)；`verify_pins.ps1` PASS(18)；改动文件全在 `allowed_paths`。 |
| AC8 不回归 | **PASS（我亲自跑）** | 仓库干净树、无夹具：`946 passed / 0 failed / 11 skipped / 957 total`，耗时 4m40s，与声称一致（本卡前 940/0/11）。(trx 为临时产物，已随沙箱清理。) |

## 4. Findings

### P2-1（残留）意图没有捕获 diff 基线，跨书窗口仍可能静默丢一次修改
- 位置：`ReaderViewModel.cs:213-224`（`SavePreferenceIntentAsync` 用**当时的** `_appliedPreferences` 做 diff）、`:303`（意图捕获只含值与 `BookId`）。
- 证据：沙箱探针 `Probe_QueuedSwitch_StillWritesTheOldBookChange` —— b1 上 zoom 1.0→1.5 入队，80ms 窗口内切到 b2（b2 已存 zoom=1.5、其余字段相同）。结果 `targetBook == null`：**一次写入都没有**，b1 的修改被静默丢弃（期望写 b1、zoom 1.5）。
- 影响：比 r1 的"写错书"轻（不会污染别的书），但仍是"改了保存不下来"，且只在"80ms 内切书 + 新书快照恰好等于旧书意图"时触发，概率低。另一种情形（字段不等）只会多发几个无害字段。
- 建议（最小修复，3–5 行）：在 `QueuePreferenceSave()` 捕获时把 `_appliedPreferences` 一并放进 `PreferenceIntent`，diff 用它；更彻底的做法是在捕获时就构造好 `ReadingPreferencesPatch` 存进队列，drain 只负责发送。补一个"窗口内切书 + 旧书修改仍落库"的测试。

### P3-1 异常路径先写状态、后判断书是否已切
- 位置：`ReaderViewModel.cs:240-256`（`catch` 在 `Book?.BookId != intent.BookId` 守卫之前置 `PreferenceSaveFailedText`）。
- 证据：沙箱探针 `Probe_ExceptionOnLeftBook_DoesNotPolluteTheNewBook` —— 旧书的写抛异常后切到 b2，b2 的阅读器显示"阅读偏好保存失败…"（FAIL）。
- 建议：把书判断提到 catch 之前（或 catch 内再判断一次）；1 行改动。

### P3-2 切到"无已存偏好"的书不会清空旧失败文案
- 位置：`ReaderViewModel.cs:152-156`（`preferences is null` 直接 return，`:168-169` 的清空不执行）。
- 证据：沙箱探针 `Probe_NewBookWithoutPreferences_ClearsStaleStatus`（FAIL）。
- 建议：清空状态移到 `LoadAsync` 开头或 `Apply` 的 null 分支之前。

### P3-3 View 覆盖粒度：每个名字只点到第一个按钮，双击/键盘无测试；一个测试名与实际点击位置不符
- 位置：`ReaderPreferenceWiringTests.cs:55-61`（`FirstOrDefault`）；`ReaderPageView.cs` 中重名按钮：`放大页面`/`缩小页面`/`重置缩放` 各 2 个（`:393-395` 与 `:420-422`），`切换阅读方向` 2 个（`:276`、`:396`）。
- 证据：我的探针枚举按钮并断言 `InRail(重置缩放[0])` 为真 —— 即 `BottomBarFitPageButton_PersistsTheZoomReset` 实际点的是**浮动条**的"适合页面"，不是底栏；证据 README §7 也写成"底部适合页面"。我的探针另行点击底栏按钮确认其接线正确（行为无误，缺的只是测试粒度）。
- 影响：单个按钮被单独改坏时测试不会红；`DoubleTapped`（`:180`）与键盘 `+/-/0`（`:712/717/722`）在 View 层无测试。
- 建议：按控件定位（底栏容器/浮动条容器）各写一条，或至少断言同名按钮数量并各点一次；双击/键盘加 2 条。

### P3-4 AC1–AC3 的"重开读回"半边未端到端验证，但卡面已全部勾选
- 位置：`doc/tasks/READER-PREF-PERSIST.md:54-60`（AC 文本含"重开读回"）、`:84-91`（测试表）。
- 说明：真实 sidecar 早于 `SaveReadingPreferences` 命令（E-2），无法端到端；现有测试只断言"发出的 patch"。可行的补偿：让 `FakeHostController.SaveReadingPreferencesAsync` 把 patch 应用到自己的 `ReadingPreferences`，再新建 VM `LoadAsync` 断言读回（VM 级闭环）。或按 `CHAPTER-MANUAL-SORT` 惯例把该半边登记为 limitation/NOT_RUN。

### P3-5 AC6 测试未断言"落库的是最新值"
- 位置：`ReaderPreferencePersistenceTests.cs:132-146`。
- 说明：只断言 `count ∈ [1,2]` 与 `vm.Zoom == 1.6`，不断言 `LastSavedPreferences.Zoom == 1.6`；若实现改成"只发第一个意图"仍会绿。我用探针确认当前行为正确（2 次点击 → 1 次写入、值 1.2），建议把该断言补进测试。

### P3-6 全局单槽 pending：另一本书的新意图可以覆盖旧书待保存意图
- 位置：`ReaderViewModel.cs:303`（`_pendingPreferenceIntent = ...` 无条件覆盖）。
- 说明：在一个窗口内先在 A 改、切到 B 再改，A 的意图被覆盖、不会保存。概率极低（要求切书+第二次点击都在 80ms 内），但与 P2-1 同源；若按 P2-1 建议改成"捕获即构造 patch 并入队"，可顺带用每书列表消除。

### P3-7 证据日志未随 r2 重新生成
- 位置：`verification/READER-PREF-PERSIST/regression.log:1`（时间戳 `2026-11-15T00:12:33`、内容仍是 `940/0/11`）、`four-pieces.log` 同时刻；r2 提交时间 `00:32:33`。卡面 `:91` 仍把 AC8 的证据指向 `regression.log`。
- 说明：946/0/11 我已亲自复跑为真，但**被引用的工件**仍属 r1 提交，不能证明 r2 门禁；`README.md` 未写 r2 的 commit/全量结果。建议按 r2 head 重新生成两个日志并 pin commit。

### P3-8 其余遗留
- `ReaderPreferencePersistenceTests.SettleAsync`（`:34-41`）仍只等 host 调用、不等续体，状态类断言的亚微秒竞争窗口未消除（View 测试已加 100ms 等待）。
- `_appliedPreferences` 在切换到无偏好书时仍未重置（`LoadAsync` 不重置，`Apply` 早退），与 P2-1/P3-2 同源。
- 离开阅读器无显式 flush（作者已登记，我认可为限制）。
- `doc/TASK_LEDGER.md` 的 "non-terminal tracked / untracked (drafts)" 计数与已提交事实仍不一致（r1 遗留，未随 r2 修）。

## 5. 我亲自做的实验与结果

沙箱：`git archive 98d42c6b6` 解包到 `G:\CODEX\New Manga.workspace\review-reader-pref-r2\`，5 个关键文件 blob 逐一与 HEAD 对齐（VM `f5ee4ce4`、View `495826aa`、Fake `ddb95dcd`、持久化测试 `7c42f73f`、接线测试 `ae888941`）。

1. **基线定向**：`ReaderPreferencePersistenceTests` 8 + `ReaderPreferenceWiringTests` 4 + `ReaderReadingPreferencesTests` 7 + `ReaderVisibleControlsTests` 4 = **23 passed**（与声称一致）。
2. **实验 B（AC4）**：把 `ReaderPageView.cs` 换回基线 blob `94ef2163` → **4 failed / 0 passed**（33 s），失败含 `SideRailZoomButton_PersistsTheZoom:130` 等。→ AC4 现在是真的。
3. **实验 C（P1-1）**：把快照改回"await 后当前值" → `ChangeMadeWhileASaveIsInFlight_IsStillPersisted` **红**（1.5 vs 1.7），其余 7 绿。→ 该测试有判别力。
4. **探针 1（入口完整性）**：枚举真实按钮（每个名字 2 个）并分别点击底栏"放大页面"、"重置缩放"与浮动条"切换阅读方向" → 均产生保存且值正确（**PASS**）；同时证明 `BottomBarFitPageButton…` 实际点的是浮动条按钮（P3-3）。
5. **探针 2（P2-1 残留）**：80ms 内切书 + b2 快照等于 b1 意图 → **0 次写入**（FAIL，`Expected "b1" / Actual null`）。
6. **探针 3（异常越界）**：旧书写抛异常 → 新书显示失败文案（FAIL）。
7. **探针 4（无偏好书）**：切到 `ReadingPreferences = null` 的书 → 旧失败文案残留（FAIL）。
8. **探针 5（最新值）**：同一窗口两次点击 → **1 次写入、`LastSavedPreferences.Zoom = 1.2`（PASS）** → 回答"80ms 内改两次，落库的是最新值"：**是**。
9. **探针 6（不卡死）**：host 抛异常后再次点击 → 继续保存、值 1.6（**PASS**）→ P2-3 的"不卡死"成立。
10. **全量（仓库干净树）**：`946 / 0 / 11 / 957`，4m40s（我跑，非引用作者数字）。
11. **沙箱全量对照**：沙箱 `939 / 6 / 12` —— 沙箱只有跟踪文件，缺仓库中被 .gitignore 的 `apps/desktop-avalonia/build/sidecar/` 与 `src/NewManga.Theme/` 构建产物；同一提交在仓库树 946/0/11。**这是环境差异，不是回归**；我没有逐一命名沙箱那 6 个失败（沙箱已清理），故该对照只作环境说明，不作为判定依据。
12. **还原**：探针文件已删除；VM/View/Fake 与 HEAD blob 完全一致（`f5ee4ce4`/`495826aa`/`ddb95dcd`）；沙箱已删除；仓库 `git status --short` **为空**。
13. **门禁（仓库只读）**：inventory `1/80/6=87`（exit 0）、`check.ps1` PASS(3 warnings)、`verify_pins.ps1` 18/18、`Skip =` 11→11。

## 6. 我没有验证的面

- 真实 sidecar 端到端"重开读回"（E-2：sidecar 早于命令）；未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`。
- 真实 GUI 手动操作（只在 Avalonia headless 里点按钮）与真实 UI 线程/可见性（状态文案在自动隐藏底栏中的呈现）。
- 深色/无障碍下状态文本表现。
- `--shell=legacy` 的旧 `Views/ReaderPage`（hostless VM，属历史回退路径，不在本卡范围）。
- 极低概率的 P3-6（跨书覆盖待保存意图）只做了代码论证，没有写测试证实。

## 7. 对实现者两个问题的明确回答

1. **"意图捕获后，80ms 内改两次，最终落库的是最新值吗？"** —— **是**（探针 5：2 次点击 → 1 次写入、值 1.2）。但现有 AC6 测试没有断言落库值，属 P3-5。
2. **"切书后旧书意图仍写旧书，这是你认可的行为吗？"** —— **认可**。偏好是 per-book 语义；用户是在 A 书上做的修改，切走不应丢弃它，写回 A 才符合"所改即所存"。r1 的问题是"A 的 patch 记到 B"（污染的正是 B），现在目标书正确。**但**我要求它必须真的写出去——当前 diff 基线仍是"当前书"的快照，P2-1 的情形下会一次都不写，这一点必须修或明确登记。

## 8. 能否进入集成

**可以（ACCEPT_WITH_LIMITATIONS）**，无 P1。建议的最小收口集：

1. P2-1：捕获意图时一并固化 `_appliedPreferences`（或直接构造 patch 入队），+ 一条"窗口内切书旧书仍落库"的测试（3–5 行实现 + 1 条测试）；若 DSH 决定不修，须在卡面"风险/限制"明确登记。
2. P3-1/P3-2：各 1 行（把书判断提到 catch 前；清空状态提前）。
3. P3-7：按 `98d42c6b6` 重新生成 `regression.log`/`four-pieces.log` 并 pin commit。
4. P3-4：AC1–AC3 的"重开读回"半边按 E-2 登记 limitation（或补 VM 级 fake 闭环测试）。
5. P3-3/P3-5 可选加强（逐控件覆盖、断言落库最新值）。
