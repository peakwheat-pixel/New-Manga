---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: dbeca3babfb8689da113b5ef263501bcdf6ece61
reviewed_head: fc7672338eebe357f273eec7d279b7e415a6db86
decision: changes_requested
---

# P20-ISOLATION-1 独立复审 R3

## 1. 结论

**decision = changes_requested。** `R-008` 的存活但无响应检测已由请求级 `core.ping` 超时驱动恢复；`with_channel` 释放锁并克隆 `Arc` 的改动消除了原来的锁等待死路，正常强杀路径也有子进程回收证据。仍不能批准：R-009 的完整关闭时限不覆盖强杀后的阻塞清理；R-010 桌面脚本把草稿写入了书架搜索框而非创建弹窗标题框，AC3 的关键 PASS 是误判；AC4 尚未完成；R-005 的 Task/evidence pins 仍与提交内容不一致。另有 R-012 失败退出码修复未覆盖实际行为断言。

复审基线为 `dbeca3babfb8689da113b5ef263501bcdf6ece61`，被审实现为 `baf4ec90ce0478eed266aebda25233f9fdcfeb3b`，当前 `HEAD` 为 `fc7672338eebe357f273eec7d279b7e415a6db86`。校验发现 `baf4ec90c..HEAD` 之间还包含 `ccee74d7c` 的 P09 Task/Plan/Status 变更；它不影响本次产品代码结论，但与“其后只有 STATUS 修剪”的提交描述不符。工作区原有用户改动未触碰；本次只新增本 Review 文件。

## 2. R-008 / R-009 逐项复核

### R-008：请求级心跳可检测活进程挂起并触发恢复——已修复

- `library_bridge.rs:2564-2565` 配置心跳间隔 1500 ms、ping 上限 2000 ms。`round_trip_timeout` 不只限制响应等待，还把事务锁等待计入期限（`1213-1244`, `1318-1336`）；若另一个业务请求卡在响应等待中，心跳也会在锁期限内失败。
- 心跳在 `Child::try_wait()` 确认进程仍活着后调用 `ping_timeout`（`2854-2879`）；ping 错误使 `needs_restart=true`，随后进入同一 `trigger_restart` 状态机（`2882-2885`）。`is_restarting` 的 compare-exchange（`2631-2637`）避免 EOF 回调、心跳和请求错误同时创建多个恢复线程。
- 重试上限为 3（`2619`），退避从 500 ms 起倍增（`2563`, `2671-2745`），30 s 稳定期后才补回预算（`2562`, `2831-2842`）；这些数值与 Task 声明相符。
- R2 日志包含真实存活的 `cmd /c pause` 子进程不回应 IPC 的测试，以及检测超时并发出 restarting/fatal 的测试；汇总为 8 个 `resilient_channel` 测试加 1 个 `stdio_channel_drop` 测试。测试使用测试专用 custom spawner；其中“recovered”状态断言本身不证明替代 `pause` 进程已能响应 ping。生产 spawner 另经 `spawn_with_startup_ping`（`1652-1703`, `2688-2705`）等待 Core 响应后才安装。故请求级超时触发恢复有代码和 Rust 子进程测试支持；真实桌面注入仍是强杀退出场景，没有实际挂起的 Python `core_service` 桌面证据。
- 1500 ms 间隔 + 2000 ms ping 限制符合声明的最坏检测时间 3.5 s；没有发现心跳被“进程仍活着”这一条件短路。

### R-009：释放 `inner` 锁和正常强杀回收——原死路已修，硬上界尚未完全成立

- `with_channel` 现在只在锁内克隆 `Option<Arc<StdioLibraryChannel>>`，随后释放 guard 再做 IPC（`2891-2925`）。Arc 保证旧 channel 在在途调用结束前不会被释放；不会出现释放后仍访问对象的 use-after-free。若请求已克隆旧 channel、同时恢复线程换入新 channel，该请求可能被旧 channel 的 shutdown 中断并返回 `CORE_UNAVAILABLE`，代码不自动重放该请求；这是可见的在途失败，不是悬空引用或重复创建恢复线程。
- `shutdown_and_kill` 先标记 down、排空 pending response 让在途 `recv()` 返回，再以 500 ms 限制关闭 HostSession、非阻塞尝试写 shutdown，并按给定时限等待/强杀子进程（`1740-1797`）。恢复线程用 1500 ms（`2662-2668`），`ResilientLibraryChannel::drop` 用 1500 ms（`2928-2937`），`StdioLibraryChannel::drop` 用 5 s（`1801-1804`）。R2 测试用真实 `cmd /c pause` 验证在途请求返回错误、关闭耗时 `<3 s`，并用 PID 查询确认进程不再运行（`4845-4957`）；提供的测试日志相符。
- 但 `wait_timeout_or_kill` 超时后忽略 `child.kill()` 的结果并调用无超时的 `child.wait()`（`1723-1737`）；随后 `shutdown_and_kill` 对 reader 执行无超时 `join()`（`1792-1796`）。因此参数只严格限制“强杀前等待”，不能单凭当前实现保证强杀失败/reader 未退出时整个关闭绝不无限等待。PID 测试也没有断言 `tasklist` 退出码成功。普通可终止进程确已在测试中回收；Task 的“杜绝无限等待”硬保证尚未覆盖这些清理分支，R-009 不宜标作无条件闭环。

## 3. R-010：脚本交互不完整；不是当前证据支持的产品写库缺陷

`run-r010-ac3-real-injection.ps1:109-115` 的 `FindFirstEdit` 在整个窗口后代中找第一个 Edit；调用点 `:215-222` 直接对整窗 `$win` 查找并写入，未限定到“新建作品”弹窗。桌面截图 `r010-20261018-0901/01-draft-preserved-during-crash.png` 和 `02-draft-preserved-after-recovery.png` 显示草稿文本在顶部书架搜索框，弹窗“作品标题”输入框为空；`03-draft-submitted-successfully.png` 仍显示空标题框及浏览器“请填写此字段”校验提示。

产品对话框输入有 `required`（`CreateTitleDialog.tsx:110-133`），提交处理先校验标题（`:42-59`）；只有该表单成功提交后，书架才调用 `activeClient.createBook`（`BookshelfPage.tsx:139-149`）。因此空标题的原生表单校验拦截了提交；这次运行没有证据表明请求到达 Rust/Python 或失败于写库。隔离根 `%TEMP%\p20r010-bfd642d9\library.db` 存在且 `books` 行数为 0，与未提交一致。**定性：脚本定位/交互不完整，不是已证实的产品缺陷。**

`trace.log` 总计 13 条 ASSERT：4 条启动前置检查 PASS，弹窗/草稿/恢复/提交这 9 条中 8 PASS、1 FAIL，故“8/9”计数本身成立；但 `title-input-element-found`、`draft-title-entered-successfully`、`draft-preserved-during-crash`、`draft-preserved-after-recovery` 这 4 条 PASS 实际都检查搜索框，不能作为 AC3 草稿证据。脚本捕获并返回失败（`script_fails=1`，脚本 `:306-307`），没有把最终 FAIL 隐去。现有证据不支持故意操纵指标，但文档把这批误指向的 PASS 当作真实草稿保全，构成证据夸大。

**AC3 阻断。** 前端组件测试仅证明合成生命周期事件期间 React 草稿可保留；真实注入确实杀了 sidecar，但没有在创建弹窗中输入草稿。应先把 UIA 搜索限定到弹窗标题输入控件，再复跑强杀、恢复、提交和隔离库查询；在此之前 Task 的 AC3 `[x]`（`doc/tasks/P20-ISOLATION-1.md:40`）与父 Task 对 AC6“实测通过并含草稿保全”的陈述（`doc/tasks/P20.md:39`）均超过现有证据。

## 4. Coordinator R-011 / R-012 / R-013 复核

- **R-011：文档修正成立，AC4 仍未完成。** Task 将 AC4 保持未勾选，且明确冷启动/四页交互复核待执行（`doc/tasks/P20-ISOLATION-1.md:41`）；这修复了 R2 指出的“未测却打勾”。没有找到当前 head 的冷启动耗时和四页可达原始证据。
- **R-012：计时修正成立，失败退出码修正不完整。** `run-r004-timeline.ps1:82-95` 在 UIA/进程查询完成后采样时间，现存 `r004-20261018-0838/trace.log` 记录 UIA 故障文案 +84 ms、重生 +655 ms、恢复文案 +935 ms；摘要的 93/655/940 ms 是后续取时点，截图则更晚，不能把它们互换。可是脚本 `A()` 在 `:25` 才增加 `scriptFails`，真实行为断言在 `:104-105` 仅调用 `T` 写日志，没有增加计数；如果前置检查通过但故障文案或重生缺失，末尾 `:111-112` 仍可能 exit 0。R-012 尚未完全闭环。当前这次 trace 两项行为断言均 PASS，故其观察结果仍可用。
- **R-013：修复成立。** `doc/tasks/P20.md:39` 已说明 fatal 态只提示检查日志、没有“重试连接”按钮，与 `AppShell` 当前实现一致。
- **R-004：修复成立。** 当前 timeline 脚本用独立故障文案正则并分别记录故障/恢复状态；`r004-20261018-0838` 的 UIA trace 和两张截图支持运行中强杀后出现故障提示、sidecar 重生和恢复提示。

## 5. 新发现问题

| ID | 级别 | 文件/行 | 触发与影响 | 建议 |
|---|---|---|---|---|
| R-015 | P1 | `doc/tasks/P20-ISOLATION-1.md:17-19,76-83`; `doc/handoffs/P20-ISOLATION-1-antigravity.md:5-6` | R-005 未真正闭环：Task `delivery_head` 仍为旧 `eb62dbc7f`，Handoff `delivery_head` 为 `796613ef4`，均未指向包含实现的 `baf4ec90c`；Task 第 18 行把 `review_status` 粘连进 `canonical_evidence_status`，第 19 行仍指向 R1；8 行表中 `EVID-P20-ISOL-UISCRIPT` commit 只有 9 位。SHA-256 与磁盘当前文件相符，但 5 行的 commit 树内容哈希不符（SRC、RUSTLOG、FELOG、UITRACE、REVIEW-R1）；R2 新测试日志与 R010 注入证据也未列入 Canonical Evidence。Task/Handoff 与证据无法共同定位当前交付。 | Coordinator 用实际包含所列字节的完整 40 位 commit 重建 pins，更新 Task/Handoff delivery head、最新 Review 指针及 canonical evidence；修复 front matter，并让 AC3/AC4 状态与实测一致。 |
| R-016 | P2 | `verification/P20-ISOLATION-1/run-r004-timeline.ps1:25,104-112` | R-012 的行为断言未走 `A()`，故 FAIL 不一定导致非零退出；自动 Gate 可在故障提示缺失或未重生时仍返回 0。 | 让两个行为断言也调用会计入 `scriptFails` 的断言函数，并保留现有 trace。 |

按仓库要求运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md`，结果为 **PASS（3 warnings）**。该检查器只验证 pin commit 中存在同路径，并将 SHA-256 与当前磁盘文件比较；它不比较 commit tree 中该路径的 blob 哈希，也不要求 40 位 commit。因此本次手工发现的 5 组 commit/blob 与 SHA 不匹配不会被该检查器拦截。其余警告为 STATUS/Plan 预算达到 80% 及 evidence_dir 存在未登记过程文件（含本次按用户指定写入的 R3 Review）；检查结果不替代本复审结论。

代码回归方面未发现冷启动路径、四页容器、打包配置、既有共享契约或依赖的修改。`events.ts` 新增生命周期事件，但原有六个领域事件常量未变；R2 心跳/重试参数与 Task 声明一致，未降低已有 NFR 阈值。父 Task 的 480 MB 内存门槛已在本复审基线中，属于既有用户裁决，不是本次实现的改动。当前 Task 只写“构建与 SHA-256 PASS”，Canonical Evidence 中没有对应当前 head 的 hash 原始文件；即便静态 diff 未改打包资源，不能替代 AC4 实测。

## 6. 阻断项 / 遗留项

- 阻断批准：R-010 的真实 AC3 草稿注入误测；AC4 的冷启动/四页/当前 bundle-resource hash 证据未齐；R-005 Task pins 与 owner delivery metadata 不自洽。
- R-009 已解决旧的 `inner` 锁占用和在途 `recv()` 阻塞；普通强杀路径有测试 PID 回收证据，但 `wait()`/reader `join()` 仍没有全路径硬时限，AC2 文案不应宣称“杜绝无限等待”已无条件证明。
- R-012 已修正计时点，现存 R004 桌面运行是 PASS；脚本失败码仍有缺口（R-016），不应作为 fail-closed 自动 Gate。
- R2 证据包自洽：Rust 日志为 `8 + 1 = 9` 个测试，两个 `.exit` 均为 0，meta 中命令/cwd/时间/结果与日志一致；前端日志为 1 个文件、3 个测试通过，`.exit=0` 且 meta 一致。日志中的 React `act` 与重复 key 警告不改变通过数量。R010 的退出为失败，且真实草稿目标误选；不发现隐藏失败或故意改写计数的证据。
- 本复审只核验现有日志、静态调用路径和已提交截图/数据库；未重新运行测试、冷启动、四页桌面验收、bundle-resource hash 或挂起 Python Core 的桌面注入。

## 7. AC1 / AC2 / AC3 / AC4 独立判断

| AC | 判断 | 证据支持 | 证据不足 / 限制 |
|---|---|---|---|
| AC1 用户可见故障提示 | **支持（运行中强杀场景）** | `r004-20261018-0838` UIA 文案 +84 ms；截图和 trace 区分故障/恢复提示。 | 未重新验证启动早期故障；R004 当前自动断言失败退出码仍有 R-016。 |
| AC2 心跳、自愈与降级 | **主要机制支持，关闭时限有保留项** | 1.5s heartbeat / 2.0s 请求级 ping 超时；活着但不回 IPC 的真实子进程测试触发恢复；重试上限测试到 fatal；桌面强杀后自动重生。 | 无实际 Python Core 挂起桌面注入；`wait()` 与 reader `join()` 不在明确时限内，故“杜绝无限等待”未充分证明。 |
| AC3 状态保全 | **不通过 / 证据无效** | React 组件测试证明生命周期事件不会卸载弹窗；真实运行确实杀了 sidecar。 | UIA 把文本写到搜索框，弹窗标题为空；恢复截图同样如此；提交被 required 校验拦截，隔离库 `books=0`。没有真实草稿保全/恢复/提交证据。 |
| AC4 不回归 | **未验证** | 静态 diff 未改四页结构、打包配置或既有阈值；Task 保持未勾选。 | 无当前 head 的冷启动、四页可达、`bundle==resource` 原始结果及内存复测。 |

**推荐下一步：** Antigravity 修正 UIA 弹窗定位并重跑 AC3；Coordinator 同步修复 Task delivery/evidence pins、把 AC3 恢复为未验证并补齐 AC4 当前 head 证据，同时修复 R004 的行为断言退出码。完成后由 Codex 对新 reviewed head 再审。
