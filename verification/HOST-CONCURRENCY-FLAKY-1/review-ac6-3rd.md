# HOST-CONCURRENCY-FLAKY-1 AC6 三次独立复核

- 被审 head: `a4ceea811`（分支 `main`；`f1f9db9e4` 返修主体 + `a4ceea811` EV-19/20/21 pin 补登）
- 复核者: `reviewer-hcf3`（**独立上下文子 agent**，未复用前两轮的会话/推理；前两轮报告只用于读取「要求」，所有事实由本轮重新实测）
- 复核时间: 2026-11-16T10:14–10:26+08:00
- 前两轮: `review-ac6.md`（361 行，`277406eeb`，CHANGES_REQUESTED）/ `review-ac6-2nd.md`（278 行，`9ce819ae7`，CHANGES_REQUESTED）
- 复核方式: 只读（`git log/show/cat-file/rev-parse/grep`、原始字节扫描、读代码/证据日志/TRX/summary、只读 `check.ps1`）。
  **唯一执行动作** = 任务允许的 `dotnet test --filter "FullyQualifiedName~HostFileIdNormalizationTests"`（跑 2 次；只写 `%TEMP%` 与 bin/obj 忽略产物）。**未跑** `test.ps1` / 全量 `dotnet test`。
- 说明: 复核期间 `main` 又前进到 `89a106aba`（`4549ce71f`、`89a106aba` 两笔与本卡无关的 docs 提交，只动 `doc/STATUS.md` 一行、`doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 与新 Gate 映射文件）。本卡范围内文件未被触及：卡面 blob `31f41d128c…`、`ac1-ac3-diagnosis.md` blob `88835a5668…` 在 `a4ceea811` 与当前 HEAD 完全相同，故本报告结论对应 `a4ceea811` 内容。

## 结论

**ACCEPTED**

1. 二次复核的 12 条 must-fix 我用**文件实际内容**逐条核对（不看卡面自称），全部闭环：21 行证据 pin 的 `commit` 归属与 `sha256` 同时校验通过；AC 标记合规且 `check.ps1 -TaskPath` 在 `status: in_review`（门禁生效态）下 **PASS**；卡面旧自相矛盾只剩显式标注的历史引述；P1-3/P1-4 的正文与 `ac1-ac3-diagnosis.md` 都是**原文改写**而非仅在处置节追加声明；P2-1/2/3/4/5、P2-N1 落地。
2. 新增的 `HostFileIdNormalizationTests` **有真实回归价值**：它不是同义反复断言（在测试内部强制 `raw > 2^53`，所以 `normalize(raw) != raw`），实现回退时必然红；我独立复算作者红测的 `Expected 5348024557882020 / Actual 59391220086327972` 与 53 位 mask 算术完全一致；`%TEMP%` 新建文件实测 **12/12** 的 raw file id > 2^53（而 G: workspace 卷 0/6），证明前置条件在本机成立；该测试我实跑 2 次均 3/3 通过，全量运行的 TRX 里 3 条亦为 `Passed`（有真实耗时）。
3. 代码侧无新增产品行为改动：`DescribeContainer` 仅 `private → internal`（`InternalsVisibleTo` 已存在），`TileChannel`/`SourceAccessRegistry` 的改动逐行核对**只有注释**，`Fea11ScanIpcTests` 是 opt-in 测试 helper 口径修正。
4. 剩余问题全部为 **P2 级文档细节**（同提交注释导致的行号漂移、AC5 旧总计数字、一个计数误算、若干历史段落未标注作废），不改变 AC1–AC5 的实质结论，不构成 AC6 放行障碍。

因此可以把 AC6 的返修判定为「到位」；建议 DSH 在集成确认后把 AC6 置 `[x] <<MET>>`（并按本报告 P2 清单顺手清扫文档细节）。

## 二轮 findings 逐条处置判定

| Finding | 二轮要求 | 我的判定 | 依据 |
|---|---|---|---|
| P1-1 剩余 15 行 sha256 | 从 `PIN_PENDING` 改为 BLOB 实算值 | **已解决** | §A：21/21 行 `git cat-file -e`=0，卡面 sha256 == `git cat-file blob` 原始字节 SHA-256；pin commit 的 blob 与被审 head 的 blob 逐字节相同 |
| P1-2 卡面自相矛盾 | 消除正文「AC4 现在 MET」vs AC 行 PARTIAL | **已解决** | `AC4 现在 MET / AC1 MET / AC5 MET` 仅出现在**明确标注为历史更正**的位置（卡面 L464-465 更正块、L584 二轮结论引用、L594 返修动作描述）；AC 行与「AC 状态」节已统一为 AC1–AC5 全 `<<MET>>` |
| P1-N1 AC 标记/门禁 | AC1/AC4/AC5 的 `[x]`+`<<PARTIAL>>` 违规；AC6 缺标记 | **已解决** | §4.3 逐条判定（§D 表）：AC1/AC4/AC5 = `[x]`+`<<MET>>`；AC6 = `[ ]`+`<<PARTIAL: …>>`；`check.ps1 -TaskPath` 在 `in_review` 下 **PASS (3 warnings)**，无 §4.3 FAIL |
| P1-3 并行叙事 | 正文「xUnit 并行」段 + `ac1-ac3-diagnosis.md:103` 实际更改 | **已解决** | 卡面 L73-74 原文加删除线，L76-81 紧跟作废更正；diagnosis 原错误段落（旧 L102-104）被替换为更正块（现文件 L99 标题 + L104-121 更正块），并写明「那个归因是错的，已作废」；`AssemblyInfo.cs:1` 实测 = `DisableTestParallelization = true` |
| P1-4 绝对化表述 | 卡面两处下调 + handoff 一致 | **已解决** | 卡面 L383-393「影响面」与 L468-477「这个缺陷的真实影响（更正后的口径）」正文均已改写（「超过 2^53 必然失败/新建场景高概率触发/『唯一一个』无法核验」）；`doc/handoffs/GOAL-WRAPUP-R100.md:89-92、105` 同口径 |
| P2-1 控制字符 | 修复 TAB/VT 等词内替换 | **已解决**（有计数小误，见 P2-3） | 当前卡面 blob 控制字符（排除 CR/LF）= **0**；旧 blob（`9ce819ae7`）实测 18 处，全部为词内替换，已全部还原 |
| P2-2 front-matter/标题 | 不再是 proposed/null/「待定位」 | **已解决** | L3 标题无「待定位」；L6 `status: in_review`；L8 `owner: DSH`；L9 `reviewer:` 记录两轮+待派三轮 |
| P2-3 `AcquireLockFile` 最坏等待 ~10s | 注释写清总上界 | **已解决** | `SourceAccessRegistry.cs:346-352` 新增注释明确「mutex 5000ms + 文件锁 5000ms ≈ 10s，不得按 5s 宣称」；代码 `:368` `WaitOne(LockWaitMillis)` 与 `:388` 独立 deadline 印证 |
| P2-4 常量一致性测试 | 新增 pin 测试 | **已解决** | `HostFileIdNormalizationTests.cs` 3 个 fact：常量 pin、mask/幂等/边界、wire facts 必为 masked；我实跑 3/3 绿 |
| P2-5 `test.ps1` 覆写 workspace evidence 目录 | 登记副作用 | **已解决** | 卡面「附带发现」第 2 条（L485-490）完整登记 `evidence-rerun/test/` 被覆写、旧 `trx_sha256` 不可复验及处置建议 |
| P2-N1 opt-in helper 口径 | `Fea11ScanIpcTests.ReadFileIdentity` 套 `NormalizeFileId` | **已解决（静态）** | `Fea11ScanIpcTests.cs:1161` 已套 `SourceSecurity.NormalizeFileId(...)`；4 处消费点全是 fixture DB 写入，无 raw 断言（§C） |
| P2-N2 P0-1 无直接回归测试 | 补直接测试 | **已解决**（覆盖缺口见 P2-5） | §B：测试为真断言、回退必然红、样本前提实测成立、实跑绿、全量 TRX 3 条 Passed |

**代码侧（二次复核已放行的 P0-1 补修与 `TileChannel` 判定）**：本轮复核未发现反例。`SourceReadCoordinator.cs:414/:638` 两处均套 `SourceSecurity.NormalizeFileId`；`SourceSecurity.Identity` 本体仍 raw（与 registry 持久化语义一致）；`HostIssuer.cs:563/:596-597` 保持二轮已放行的归一化；`TileChannel` 的「同进程同源 raw 自比、`TileGrantView` 不含 identity、唯一生产调用点不传 `VolumeSerial/FileIndex`」逐条抽查成立。

## 逐项核查

### A. 21 行证据 pin 全量校验（逐行 cat-file + sha256）

方法：从卡面 Canonical Evidence 表（L142-164）解析 21 行；对每行把 **`git -C <repo> cat-file blob <commit>:<path>` 的输出用 `cmd` 二进制重定向**落到 `G:\CODEX\New Manga.workspace\...\review3-tmp\`，再对该文件算 SHA-256（遵守 `core.autocrlf=true`：**不使用工作区文件**）；同时 `git cat-file -e` 取退出码、`git rev-parse <commit>:<path>` 与 `git rev-parse a4ceea811:<path>` 比较 blob、`git log -1 --format=%h -- <path>` 判「实际引入当前内容的提交」。

| # | evidence | path（短） | pin commit | cat-file -e | sha256（`git cat-file blob` 实算，BLOB） | 判定 |
|---|---|---|---|---|---|---|
| 1 | EV-HCF-01 | `code-evidence.log` | 84b4a2456 | 0 | cd56c9115852142faf19637c4c516c03ce05ad12839782c5e76a7ef788e9d92c | ✅ |
| 2 | EV-HCF-02 | `ac2-repro.md` | fbf704a37 | 0 | 7544f69b96563434b1bf8e2f0699b9950f3c804104c54806536a414558302a4a | ✅ |
| 3 | EV-HCF-03 | `repro-1.log` | fbf704a37 | 0 | bd5b44748d1bf5a784256364ef6e672dcf4ce011bc0c5421ac174ae3a0c5d3d0 | ✅ |
| 4 | EV-HCF-04 | `repro-2.log` | fbf704a37 | 0 | 01244f82eb49c100d49583109d1e4f4eb46d5e1ccac9b8fd5c138ba0efd79c3a | ✅ |
| 5 | EV-HCF-05 | `after-fix.log` | e66323bf2 | 0 | 5ba3e18433712f24a9daadbc6fa59b3dd20648a833e3080c5e0b1ec6c5bb6985 | ✅ |
| 6 | EV-HCF-06 | `build.log` | e66323bf2 | 0 | 3e4ef652f53a34659a8b8483daacfabc4ee27a3994062b598b5252bc8965fbd7 | ✅ |
| 7 | EV-HCF-07 | `correction-skip-vs-pass.md` | ac434d911 | 0 | b48e9f14f6e4b1ebd1efeb78a6b8b7d242e073a730d83a5d2e4f8b8fdc3bd30f | ✅ |
| 8 | EV-HCF-08 | `solo-detail.log` | ac434d911 | 0 | ac844014e387e117e9e7be1e4ce128a33b4071a1f07d2a213060a34ac9ab812d | ✅ |
| 9 | EV-HCF-09 | `file-identity-diagnosis.md` | 062918039 | 0 | 2714127339039ae731a5ba2e77cb0fb99e850caad0bd214ed2da7fbd3de290b8 | ✅ |
| 10 | EV-HCF-10 | `st-ino-measured.md` | 4b1198443 | 0 | 2cf046745af297e946b84efd57d647c3a51908e95d8cd60ac9123c983c4070fb | ✅ |
| 11 | EV-HCF-11 | `probe_st_ino.py` | 4b1198443 | 0 | a62d26e87d7407396a5fca3f794cb0af37c757f421541135154b2b01ea471322 | ✅ |
| 12 | EV-HCF-12 | `st-ino-probe-output.log` | 4b1198443 | 0 | c67c81482ab2d8579b4872d048162656cba982f4a5c18a14b2c3b7d9b56511e5 | ✅ |
| 13 | EV-HCF-13 | `root-cause-proven.md` | c75740cb9 | 0 | 5175256b81ae9b28035df456da4b467df7882adf83ac8b96d1be309333d73b7f | ✅ |
| 14 | EV-HCF-14 | `after-identity-fix.log` | 277406eeb | 0 | 0fca42ce83293a012e44a3a4c1132850a0101e5d130f61243e1bed46cbd0b976 | ✅ |
| 15 | EV-HCF-15 | `build-r99.log` | 277406eeb | 0 | 81aa19763b9320b2696b6bf6ce7478beed46241e8988d84ceb54a1b882bfdbbf | ✅ |
| 16 | EV-HCF-16 | `review-ac6.md` | bbeb28dcb | 0 | ca480b624833edee8201ba76ed927f08b464dab4f908a3db65361f44e137fbee | ✅ |
| 17 | EV-HCF-17 | `after-p0-fix.log` | bbeb28dcb | 0 | c9ff683c687acb564a6a9d9fec10221a862a03741af3e689b17420f421ad695d | ✅ |
| 18 | EV-HCF-18 | `build-p0.log` | bbeb28dcb | 0 | 5a1e95234be694cb71a90e80efa57321672d506ec82996e60803220b32880cef | ✅ |
| 19 | EV-HCF-19 | `review-ac6-2nd.md` | f1f9db9e4 | 0 | 62b4e36e940d986d989e5d959c2757e2a19262cd6c352f070f6eadee6b0d2d11 | ✅ |
| 20 | EV-HCF-20 | `after-ac6-2nd-fix.log` | f1f9db9e4 | 0 | bf3d8ef02de3bcc2bca8dfa0bc94b45cae44663efbb66afe79c95a123fd9b713 | ✅ |
| 21 | EV-HCF-21 | `ac1-ac3-diagnosis.md` | f1f9db9e4 | 0 | a65415bab851acd6a52999badb41ca8f49c4f4b723a7c7dad1a6b8ce69915107 | ✅ |

**补充校验**：21/21 的 `git rev-parse <pin>:<path>` == `git rev-parse a4ceea811:<path>`（pin 的 blob 与被审 head 的 blob 逐字节相同）；`git log -1 --format=%h -- <path>` 对 20 个新增文件等于 pin commit，对 EV-21（`ac1-ac3-diagnosis.md` 被修改过）等于 `f1f9db9e4`（即实际引入当前内容的提交，原始引入为 `84b4a2456`）。`a4ceea811` 本身只给卡面加了 3 行（EV-19/20/21 登记，`git show --stat`: 1 file changed, 3 insertions）。

`review-ac6-2nd.md` 的字节一致性：workspace 原件（`G:\CODEX\New Manga.workspace\tasks\HOST-CONCURRENCY-FLAKY-1\review-ac6-2nd.md`，34584 字节）SHA-256 = `62b4e36e…0d2d11`，与仓库 `a4ceea811` 的 blob 实算值**完全相同**（即作者复制未变形；行数实测 278，与卡面记述一致）。`review-ac6.md` 同样为 `ca480b62…7fbee`（workspace 与 repo blob 一致）。

### B. 新回归测试的回归价值

**被测文件**：`apps/desktop-avalonia/tests/NewManga.Host.Tests/HostFileIdNormalizationTests.cs`（新增 132 行，3 个 `[Fact]`，`IDisposable` 清理 `%TEMP%/newmanga-file-id-*`）。

**(1) 是否真断言 `wire.file_id != raw.Id`（不是同义反复）**——**是**。关键断言在 `:114-123`：

- `var wireFileId = facts["file_id"]!.GetValue<ulong>();`
- `Assert.Equal(SourceSecurity.NormalizeFileId(rawId), wireFileId);`
- `Assert.Equal(CoreFileMask & rawId, wireFileId);`
- `Assert.NotEqual(rawId, wireFileId);` ← 专门的 anti-regression 断言

因为测试在 `:101` / `:111-112` 用 `Assert.True(rawId > CoreFileMask, …)` 强制样本满足 `raw > 2^53`，所以 `normalize(raw) != raw` 恒成立：`Equal(normalize(raw), wire)` 不是同义反复，`NotEqual(raw, wire)` 也不会被"巧合"满足。

**(2) 样本前提是否成立**——**成立**。测试在 `:95-107` 用 `%TEMP%` 下新建文件探测（最多 64 次），找不到 `raw > 2^53` 的样本**直接 `Assert.True(strong is not null, …)` FAIL**（不是 skip、不是弱断言）。我独立实测：`%TEMP%` = `C:\Users\49745\AppData\Local\Temp`，新建 12 个文件逐个 `fsutil file queryfileid` → **12/12 的 raw file id > 2^53**；同一手法在 G: workspace 卷新建 6 个文件 → **0/6** 超 2^53。这既证明前提在本机成立，也印证作者「探针必须建在 %TEMP% 而不是 workspace 卷」的取舍（放在 G: 会假绿）。

**(3) 回退是否必然变红**——**必然**（逻辑推演）：若把 `SourceReadCoordinator.cs:414` 的 `["file_id"] = SourceSecurity.NormalizeFileId(before.Id)` 回退为 `before.Id`，则 `wireFileId == rawId > 2^53`，于是：
- `Assert.Equal(normalize(rawId), wireFileId)` → Expected=`normalize(rawId)`、Actual=`rawId` ⇒ 红；
- `Assert.NotEqual(rawId, wireFileId)` → 红。
前提（raw > mask）由测试自身强制，不存在「样本不溢出仍然绿」的路径；若有人改 `NormalizeFileId` 常量，第 1 个 fact 也会红。

**(4) 作者红测数值可信度**——**自洽**。作者报告回退红测为 `Expected 5348024557882020 / Actual 59391220086327972`。我独立复算：`mask = (1<<53)-1 = 9007199254740991`，`59391220086327972 & mask = 5348024557882020`；`59391220086327972 > mask`。这正是上层两个断言在「expected=normalize、actual=raw」下的输出形态，说明红测确由该断言的实现回退产生。

**(5) 实跑结果**（我执行的两次 filter run，具体结果行）：

```
已通过 NewManga.Host.Tests.HostFileIdNormalizationTests.CoreFileIdMask_MatchesTheFrozenCoreIdentityContract [3 ms]
已通过 NewManga.Host.Tests.HostFileIdNormalizationTests.NormalizeFileId_MasksTo53Bits_AndIsIdempotent [< 1 ms]
已通过 NewManga.Host.Tests.HostFileIdNormalizationTests.DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex [7 ms]
测试总数: 3 / 通过数: 3 / 失败: 0
```

第二次运行结果相同（3/3），无 flaky 迹象。

**(6) 全量证据内的执行痕迹**（EV-HCF-20 `after-ac6-2nd-fix.log`，用其声明的 TRX 哈希现场复算，三份 TRX 与磁盘完全一致）：

- `results-host.trx`：408 条 = **364 `Passed` + 44 `NotExecuted`**；其中 `HostFileIdNormalizationTests` 3 条全部 `Passed`（耗时 0.0013s / 0.0034s / 0.0001s），两个曾经失败的 `GrantIssuerTests` 均 `Passed`（0.766s / 0.653s，真实执行）。
- 结果行：CoreClient `256/0/0`、Host `364/0/44`（408）、App `962/0/4`（966）⇒ `TEST PASS (Debug): 1582/1630 passed, 48 skipped`，日志尾行 `EXIT=0`；日志头含 `# command:`、`# head: 9ce819ae7…（工作区含本次未提交返修）`、`# at_utc:`（P2-N3 已落地）。

**(7) 局限（不阻塞，见 P2-5）**：该测试只 pin `DescribeContainer` 的单文件 container facts 路径（`SourceReadCoordinator.cs:414`）；批量 folder member entries 的第二个写入点（`:638`）没有直接测试，若有人只回退 `:638`，本测试仍绿。另：测试在「低文件 ID 复用卷」上会 **FAIL** 而不是假绿——这是作者有意设计（宁红勿假绿），属可移植性风险而非正确性缺陷。

### C. 新问题扫描

1. **`DescribeContainer` private → internal：只是可见性，无产品行为变化**。diff 仅方法签名与 6 行 `<remarks>`；`apps/desktop-avalonia/src/NewManga.Host/AssemblyInfo.cs:6` 已有 `[assembly: InternalsVisibleTo("NewManga.Host.Tests")]`；方法本体（`:380-418`）未改逻辑，归一化本身来自二轮前的 `bbeb28dcb`。
2. **其余源码改动逐行核对为注释/口径**：`TileChannel.cs` +20 行全是 `FileIdentity.Read` 的契约注释（raw index 不参与跨语言比较、未来若接 `BridgeGrant` 需归一化）；`SourceAccessRegistry.cs` +6 行是「最坏 ≈10s」注释；`SourceReadCoordinator.cs` +6/-1 是可见性 + remarks。无行为变化。
3. **`Fea11ScanIpcTests` helper（静态判断；opt-in 无法运行）**：`ReadFileIdentity` 现在返回 `SourceSecurity.NormalizeFileId(((ulong)info.IndexHigh << 32) | info.IndexLow)`（`:1161`）。全部 4 处消费点（`:58/:213/:563` 取 facts → `UpdateLocationRow` `:1021-1049` / `UpdateLocationGenerationRow` `:294-325`）只把 facts 写进 fixture DB 的 `source_locations.volume_serial/file_id/size_bytes`，供 Python 侧与生产 grant facts 比较；没有其它断言依赖旧 raw 值（`:642-652` 的 before/after 比较两侧都来自 DB，`:780-786` 的 registry 快照比较是 Host 内部 raw 自比）。因此该改动方向正确（与生产 masked grant facts 对齐），静态上未发现会破坏该 opt-in 测试其它断言的点。**但它无法在本轮实跑**：`apps/desktop-avalonia/scripts/test.ps1` 不设 `NEWMANGA_FEA11_IPC`（opt-in 开关在测试内，如 `Fea11HostAuthIpcTests.cs:357` 的 `Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1"` + `Skip=`），且任务只允许跑 B.3 的 filter 命令。
4. **卡面 vs 代码的行号漂移**（P2-1）：`AC4`/处置节引用的 `SourceReadCoordinator.cs:408/:632` 当前实际为 `:414/:638`（同一返修提交自己加的 6 行 remarks 造成 +6）；`TileChannel.cs:437` 当前实际为 `:457`（同一提交加的 20 行注释造成 +20）。`HostIssuer.cs:563/:596-597`、`SourceAccessRegistry.cs:31-32/:49`、`HostRuntime.cs:1044-1050` 核对无漂移或仅 ±2 行内。
5. **`f1f9db9e4` 改了三指针**（`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`），这三份文件不在本卡 `allowed_paths` 内；作为 DSH/Lead 的生命周期指针更新可以理解，但其中 `STATUS.md` 的「条件 3/4」新口径（5/5 页真截图、portable 包已验证启动）**不在本卡任何证据范围内**，本轮无法独立验证（列入「未能独立验证」）。另 `REBASELINE_PLAN.md:57` 把本卡作为 `SIDECAR-SCHEMA-STALE-1` 的下游节点登记，而卡面 front-matter 是 `depends_on: []`——两种「依赖」口径不同，需 DSH 在集成时统一（不影响 AC6 的技术结论）。
6. **卡面其它陈述抽查**：`HostErrorCodes.cs:27` 说 BUSY 归类为可重试（实际 `RetryableCodes` 在 `:15`，`:27` 是 `IsKnown` 列表）——历史处置节的行号小误，实质成立；`scanner.py:163/168`、`source_read_refs.py:1068/1080`、`identity.py:16/20`、`source_strict_read`/`handle_resolver` 的叙述与代码一致；`HostRuntime.cs:1044-1050` 的 Tile 调用确为 6 个位置参数、不传 `VolumeSerial/FileIndex`；`TileGrantView`（`TileChannel.cs:64-71`）确无 identity 字段。

### D. AC 标记与门禁实测

`doc/09_COLLABORATION.md` §4.3 的勾选一致性表：`[x]` 只允许 `MET`/`NOT_APPLICABLE`；`[ ]` 只允许 `PARTIAL`/`BLOCKED`；`PARTIAL`/`BLOCKED`/`NOT_APPLICABLE` 必须带非空原因；标记必须在行末且其后无内容。本卡 `governance_version: 3`，`status: in_review` ⇒ 门禁生效（`tools/governance/check.ps1:953` 分支；`:967-987` 校验）。

| AC | 行 | 勾选 | 行末标记 | §4.3 判定 |
|---|---|---|---|---|
| AC1 | L89 | `[x]` | `<<MET>>` | ✅ 合规 |
| AC2 | L90 | `[x]` | `<<MET>>` | ✅ 合规 |
| AC3 | L91 | `[x]` | `<<MET>>` | ✅ 合规 |
| AC4 | L92 | `[x]` | `<<MET>>` | ✅ 合规 |
| AC5 | L93 | `[x]` | `<<MET>>` | ✅ 合规 |
| AC6 | L94 | `[ ]` | `<<PARTIAL: …>>`（待三轮复核确认） | ✅ 合规（PARTIAL 原因非空；本轮即第三轮，DSH 确认后可改 `[x] <<MET>>`） |

实测（只读）：

```
$ pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/HOST-CONCURRENCY-FLAKY-1.md
Task: doc\tasks\HOST-CONCURRENCY-FLAKY-1.md
WARN: 存在 13 个非终态 Task …（r38）
WARN: doc/STATUS.md 已达到预算的 80%：2936 bytes / 27 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6969 bytes / 64 lines
Governance check: PASS (3 warnings)   EXIT=0
```

⇒ 门禁 **PASS**（二轮担心的「进入 in_review 即 4 条 FAIL」不再出现）。

**P2-1 控制字符（原始字节）**：对 `git cat-file blob HEAD:doc/tasks/HOST-CONCURRENCY-FLAKY-1.md` 的字节逐一扫描（排除 CR/LF）：U+0009=0、U+000B=0、U+0007=0、U+000C=0 —— **零残留**；`verification/HOST-CONCURRENCY-FLAKY-1/` 下全部证据文件同样 0 控制字符。对比旧 blob（`9ce819ae7`）实测 **18 处**：11×U+0009（`<TAB>est.ps1`）、2×U+000B（`<VT>erification`）、2×U+0007（`<BEL>pps/`、`<BEL>lpha.png`）、3×U+000C（`<FF>ile_id`×2、`<FF>acts.`），全部词内替换，均已按语义还原（词内残留扫描未发现 `est.ps1`/`erification` 之类的首字母缺失词）。**但卡面 L598 与提交信息写「17 处」，实际为 18 处（其列项相加也是 18）**（P2-3）。

**P2-2 front-matter/标题**：L1-24 实测 `title:` 已去掉「（待定位）」、`status: in_review`、`owner: DSH`、`reviewer:` 记录两轮复核与三轮待派，与正文一致。

**P1-2 自相矛盾**：全文检索 `AC4 现在 MET`、`AC1 MET /`、`AC5 MET` 等旧表述，命中仅在：(a) L464-465 的「本小节曾与 AC 行自相矛盾…原文写…现统一」更正块；(b) L584 二轮复核结论表的引用；(c) L594 返修动作描述。均属**明确标注的历史**，无未标注的现行矛盾。

**P1-3 并行叙事**：卡面 L73-74 原文已加 `~~删除线~~`，L76-81 紧随更正块（`AssemblyInfo.cs:1` 实测 = `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]`，文件仅此 1 行）；`ac1-ac3-diagnosis.md` 的原错误段落（旧 L102-104，二轮报告引用 `:103`）已被替换为更正块（现文件 L99 标题 + L104-121 更正块），并明确写「那个归因是错的，已作废」；「为什么偏偏是 Fea11…暴露」一节的单测试内 watcher 线程叙事保留且成立。**残留小疵**：更正块下方的 L123「这一条需要 AC2（受控复现）才能确认到代码级，本轮只记录关联性」是未清理的旧收尾句，与上方「根因已被后续实测确认」的更正块口径不一致（P2-4）。

**P1-4 绝对化表述**：卡面 L383-387 已改写为「当 NTFS file index 超过 2^53 时**必然**报…新建文件场景下**高概率**触发」，L389-393 更正块注明「原文『任何用户』『唯一一个』过强/无法核验」；L468-473 同口径改写；L475-477 更正块注明 handoff 已同步。`doc/handoffs/GOAL-WRAPUP-R100.md:89-92`「新建文件场景下高概率触发，但不是『任何情况』… 反例 alpha.png」、`:105`「『唯一一个』无法核验」——与卡面一致。

**P2-5 证据目录副作用**：卡面 L485-490 已登记 `task-envs/HOST-RESOURCE-SECURITY-1/evidence-rerun/test/` 被全量运行覆写（`results-*.trx`、`summary.json` 的 `at_utc` 被重写，旧 `trx_sha256` 不可复验）并给处置建议；本轮复核时该目录当前的 `summary.json`（`at_utc`=2026-11-16T02:07:04Z）与三份 TRX 的磁盘 SHA-256 仍与 EV-HCF-20 声明值一致（未被覆盖），但该副作用机制本身仍然存在，登记正确。

## 新发现（如有）

**P0：无。P1：无。**

均为 P2（文档/可达性细节，不阻塞 AC6）：

- **P2-1（行号漂移，二轮 P2-N4 未真正闭环）**：卡面 AC4 行内注释（L92）与处置节（L518、L539、L579）引用的 `SourceReadCoordinator.cs:408 / :632` 当前实际为 `:414 / :638`；`TileChannel.cs:437`（L92/L539/L580）当前实际为 `:457`。原因是**同一返修提交**新增的 remarks/注释把目标行往下推（+6/+20），作者按提交前位置填写。建议改引用为 `:414/:638`、`:457`，或改用「函数名 + 语句特征」而非纯行号。
- **P2-2（AC5 总数陈旧）**：L93 AC5 写「全量 `test.ps1` 在当前 HEAD 仍全绿 **1579/1627** passed」，但返修后同 head 的证据 EV-HCF-20 是 **1582/1630**（Host 364 = 361+3，`TEST PASS (Debug): 1582/1630 passed, 48 skipped`，EXIT=0）。实质结论（0 failed / 48 skipped / App 962/0/4 不退化 955/0/11）成立，只是数字未随新增 3 个测试更新；L520/L540 同旧数。建议改为「1579/1627（返修前）；返修后 1582/1630」。
- **P2-3（控制字符计数误算）**：L598 与提交信息称「17 处」，实测旧 blob 为 **18 处**（11 TAB + 2 VT + 2 BEL + 3 FF，与 L598 自己列出的项相加一致）；修复本身零残留。
- **P2-4（未被要求但仍是旧口径的残留叙述）**：L186「并行下对 SourceAccessRegistry 的访问密度上升」、L245「并行下身份快照与文件读取的时序问题」两处旧归因未加作废标注（后续 L276-284、L542-545 已推翻，但读者需跨节拼合）；`SourceAccessRegistry.cs:343` 注释仍写 "whenever the full fixture set runs in parallel"；`ac1-ac3-diagnosis.md:123` 的旧收尾句「这一条需要 AC2…本轮只记录关联性」未随更正块清理；卡面 H1（L26）「Host.Tests 的并发 flaky」与正文「不是偶发 flaky、确定性触发」口径不一致（任务名历史所致，建议注明）。
- **P2-5（新回归测试覆盖缺口）**：测试只 pin `DescribeContainer`（`:414`）；`SourceReadCoordinator.cs:638` 的 folder member entries 写入点无直接测试，仅回退 `:638` 不会被抓住。建议后续加一条针对 entries 路径的 pin（或把两处写法收敛到同一 helper 后测 helper）。
- **P2-6（返修提交动了卡外文件）**：`f1f9db9e4` 修改 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`（不在本卡 `allowed_paths`）；其中 `STATUS.md` 的「条件 3/4」新陈述（5/5 页真截图、portable 包已验证启动）不属于本卡证据范围，本报告无法背书。另外 `REBASELINE_PLAN.md:57` 的依赖列与卡面 `depends_on: []` 口径不一致。建议 DSH 在集成时确认这两点（不阻塞 AC6）。
- **P2-7（handoff 状态行陈旧）**：`doc/handoffs/GOAL-WRAPUP-R100.md:84` 仍写「新建，AC1–AC5 PARTIAL/MET…AC6 待重审」；P1-4 要求的绝对化表述已在该文件改对（L89-92/L105），此行属历史 handoff 的功能状态描述，建议下次 handoff 更新。
- **P3（可忽略）**：`HostErrorCodes.cs:27` 作为「BUSY 可重试」的引用不准确（`RetryableCodes` 在 `:15`）；`ac1-ac3-diagnosis.md` 有「保留保留结论」重复词。

## 未能独立验证的项

1. **P0-1 的端到端运行时行为未实跑**：覆盖 source-read 路径的 `Fea11*IpcTests` 是 `NEWMANGA_FEA11_IPC=1` opt-in（会起真实 Python Core、写 workspace），`test.ps1` 不设该变量，且本轮唯一允许的执行动作是 B.3 的 filter 命令。本轮的 P0-1 结论仍是**静态链路 + 单文件 wire facts 层**证据。
2. **未重跑 `test.ps1` / 全量 `dotnet test`**（硬性约束）。EV-HCF-20 的「全量绿」我做了：日志结果行/头尾/`EXIT=0`、`summary.json` 与三份 TRX 的磁盘 SHA-256 复算（当前仍一致）、TRX outcome 解析（Host 364 Passed + 44 NotExecuted、两个 GrantIssuerTests Passed）；但**没有**重放这次全量运行。
3. **`Fea11ScanIpcTests` helper 改动无法实跑验证**（opt-in、会起真实 Core）；只有 §C.3 的静态判断。
4. **作者的回退红测未由我独立复现**（复现需改仓库文件，违反只读约束）；我以「断言逻辑 + 样本前提实测 + 红测数值的 mask 算术复算」三条独立佐证其可信度。
5. **EV-HCF-20 的「运行树 == 提交树」只能间接推断**：日志自述 head `9ce819ae7` + 工作区含未提交返修；我以「日志/TRX 内容齐全（含 3 条新测试、Host 408）」「日志 at_utc 02:07:13Z 早于 `f1f9db9e4` 提交时间 10:08:13(+08) 约 60s」以及「在我本机 HEAD 树上实跑同 filter 3/3 绿」间接佐证，但没有 worktree 快照比对。
6. **`f1f9db9e4` 对三指针（PLAN/STATUS/LEDGER）的更新**、特别是 `STATUS.md` 的 Gate 条件 3/4 新口径，不在本卡证据范围，未核（见 P2-6）。
7. **复核期间 `main` 前进**（`a4ceea811 → 4549ce71f → 89a106aba`）：两笔为无关 docs 提交，本卡范围内 blob 未变；但本报告只对 `a4ceea811` 内容负责。

## 声明

本复核**未修改仓库 `G:\CODEX\New Manga` 下任何受版本控制文件**：未 commit、未 checkout、未 `git add`、未写仓库内文件；复核期间 `git status --porcelain` 始终为 0 行。
唯一执行动作是任务允许的 `dotnet test --filter "FullyQualifiedName~HostFileIdNormalizationTests"`（两次），其副作用只有 `%TEMP%/newmanga-file-id-*`（测试自身清理）与 `bin/obj` 构建产物（git 忽略）；未跑 `test.ps1`、未跑全量 `dotnet test`。
报告与所有临时校验文件写在 `G:\CODEX\New Manga.workspace\tasks\HOST-CONCURRENCY-FLAKY-1\`（`review-ac6-3rd.md`、`review3-tmp/`、`review3-test-run.log`），不在仓库内。
本报告独立于前两轮：行号、字节、哈希、TRX outcome、`%TEMP%` 测量与红测算术均由本轮重新实测/复算；对前两轮报告的引用仅用于读取复核要求。

FINAL: ACCEPTED — 二次复核的全部 12 条 must-fix 均经文件事实独立验证闭环（21/21 证据 pin 的 commit+sha256、§4.3 门禁在 in_review 下 PASS、新旧叙述与实际文本一致），新回归测试具备真实回退变红能力且实跑 3/3 绿、全量 TRX 可复算，仅余 P2 级文档细节（行号漂移/AC5 旧总计/计数误算）不构成放行障碍。
