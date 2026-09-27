decision=changes_requested

## 0. 复核方式与工具限制（先说清证据边界）

- 本轮只读，未修改任何文件。
- 本会话 `pwsh` 不可用：沙箱初始化即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），escalation 又被 "no approval channel is available" 拒绝，因此**无法执行 `git diff` / `git status` / `git show`**。我改用「工作树文件内容 + `.git/worktrees/DIAG-FIX-C-zcode/logs/HEAD` reflog」交叉验证，并据此确认：
  - reflog 末条 `27dbedda → 46c7ff5a`（commit message: `R4 per DSH r3 -- tolerant away-time assertion, handoff r3 links, import order`），即 **HEAD = 46c7ff5a**，与派发方给定的 R4 被审固定点一致；
  - `verification/.../targeted-suite-r4.log`、`full-suite-r4.log` 时间戳（18:28:04Z / 18:29:43.857Z）**早于** R4 commit 时间（epoch 1790533784 = 2026-09-27T18:29:44Z），且字符串已存在于 worktree index，可判定两份 r4 日志属于 R4 变更集（非事后未提交产物）。
  - 因此"R4 相对 R3 只有断言/文档/import 顺序改动"这一说法，我只能以 commit message + 代码内 R3 标记 + 内容比对佐证，**不能独立 diff 验证**。

## 1. 判定项 1：`tests/core/test_bootstrap.py` 新断言 —— 通过（判别力与稳定性均成立）

- 落地内容正确：L694 取基线 `total_before_return`，L707-712 为容忍式断言
  `assert services.reading.progress.total_read_seconds - total_before_return < 1.0`，并附判别力注释（"a missing N-1 guard would add the full simulated 600 s absence"）。测试 L693 先把 `_last_settle` 人为拨回 `monotonic() - 600.0`。
- **判别力（正面确认，非仅"绿了就通过"）**：产品侧 `_open_reader_chapter` 的守卫（`src/bootstrap/app.py` L243-244，`if not reader._heartbeat.isActive(): reader._last_settle = time.monotonic()`）位于 L248-258 的章节查询与 L259 `reader.openChapter(...)` **之前**；而 `openChapter` 首行即 `settleReadingTime()`（`viewmodels/reader/viewmodel.py` L96），`settleReadingTime` 以 `elapsed = now - self._last_settle` 折叠墙钟并 `add_time`（L464-470），`add_time` 累计后经 `_touch/_persist` 落库（`application/reading/service.py` L234-241、L367-380），下次 `open()` 又从同一行还原（L140-156）。所以：**守卫缺失 → 折叠 ≈600 s → 重返后 `total_read_seconds` 增量 ≈600 ≫ 1.0 → 断言红**；守卫在位 → 重置后到 settle 之间只剩 3 次本地 SQLite 读（ms 级）→ 增量 ≪ 1.0。判别边界（600 vs 1.0）约 600×，且基线在 `navigate` 之前取，信号分发开销不计入。
- **稳定性**：残留量上界是 `L244` 重置到 `openChapter→settleReadingTime` 之间的 3 次 SQLite 查询耗时（注释写"sub-millisecond"略乐观，但 1.0 s 阈值留了 3 个数量级余量）；heartbeat 为 5 s 周期而测试 <1 s，不会叠加 tick。原严格相等对该残留非确定，改容忍式是正确的收口。
- 非阻塞观察（不建议本轮处理）：断言单边，只防"多计"不防"少计"；但累计语义已有 `tests/reading_export/test_reading.py:29-75`、`test_sqlite_reading_export.py:293-323` 等钉住，风险可接受。

## 2. 判定项 2：Handoff §3 引用与 §8 修订记录 —— 不通过（3 项文档事实错误，需 ZCode 收口）

技术结论（N-1/N-2/N-3 产品修复）我沿用 R3 的正面确认，本轮不改判。但**R4 这一轮的交付物主要就是这份 Handoff，而它对 R4 自身的记录不准确**：

- **H-1（P3，审计固定点悬空）**：frontmatter L7 写 `reviewed_head: 27dbedda（R3 handoff）→ R4 被审固定点见 §8`，但 §8（L123-134）**没有任何 commit hash/区间**；对比 §6 L104 给了 `de0bf175..e9f61f5b`、§7 L120 给了 `ee30172f..<R3 head>`。也就是说文档自己指了一个落空的指针——我是靠读 `.git` reflog 才知道 R4 = `46c7ff5a`。这恰好是本轮被点名复核的一节。
- **H-2（P4，标签与实物矛盾）**：§3 表 L65-66 两行标注"（……；R3 最终测试版重取）"，但同名红/绿日志**文件头写的是** `# FIX-C wiring assertion test (R4 final version)`，且 §8 T-1（L129）自称"以 R4 最终测试重取红/绿日志"。同一文档内 §3 与 §8 互相打脸，且标签落后一个轮次——这正是 R3 要求收口的"证据链接陈旧"同类缺陷在 R4 复发（指针文件名对、轮次标签错）。
- **H-3（P3，最终测试版本的证据未被引用）**：§3 L67-68 第 3/4 行最新指针只到 `-r3.log`（R3 用的是严格相等断言），而 **R4 最终测试版的证据是 `targeted-suite-r4.log` / `full-suite-r4.log`（210 passed / 1318 passed 5 skipped，EXIT=0），它们存在于变更集却在 Handoff 中零引用**；§2 AC4（L53-55）同样仍指 R1 日志；§8 L134 自称"R4 变更（git 实际）"却漏列这两个文件。按 Q-009 口径，被交付测试版本的 suite 证据必须在 Handoff 可溯源。

说明：R3 当时的要求（"§3 改指 `-r3.log`"）在字面上已满足（L67-68 已出现 R1/R3 双指针），H-2/H-3 是 R4 新产生/新暴露的，但因为同属"证据指针必须对应最终被交付的测试版本"这一条轴，我按同一把尺子判不通过。

## 3. 判定项 3：日志内容与 EXIT —— 通过

- `wiring-test-pre-wiring-red.log`：头 `R4 final version, PRE-wiring (base bootstrap)`；失败点 `tests\core\test_bootstrap.py:685`（`the heartbeat must stop`），**与当前测试文件 L685 逐字对应**（docstring、L669-672 的 N-5 注释、断言文本均一致），`1 failed`，`EXIT=1`。语义正确：pre-wiring 时 `closeReader` 从未被调用，先在心跳断言处红。
- `wiring-test-post-wiring-green.log`：`1 passed in 0.63s`，`EXIT=0`。
- `targeted-suite-r4.log`：`210 passed in 28.68s`，`EXIT=0`（与 §3 第 3 行口径一致）。
- `full-suite-r4.log`：`1318 passed, 5 skipped, 1 warning`，`EXIT=0`（0:01:08）；skip 明细 = 2×docTR + 1×numpy + 2×torch，与 §2 AC4 的 5 skip 口径吻合，无新增 skip、无放宽。
- 日志均为原始 pytest 输出忠实转录（含 QML `sourcePath`/`currentPage` TypeError 噪声，与 FIX-A/B 同口径），未见人为清洗或拼接迹象。

## 4. 其余两项收口 —— 通过

- **T-3（import 顺序）**：`src/bootstrap/app.py` L32-34 为 `import sys` / `import tempfile` / `import time`，`import time` 已在 `tempfile` 之后，字母序恢复。`tests/core/test_bootstrap.py` L12-19 亦为字母序（其 `import time` 属 R3 为 L693 引入，位置正确）。§7 L120 把"import time + import time 顺序"并列写在测试文件清单里表述含混，但属 R3 既有文字，不阻塞。
- **T-4（观察项处置）**：`app.py` L237-244 守卫注释已写明"stopped heartbeat marks the away state"与"in-session chapter switches (heartbeat active) 保持既有语义"；§8 T-4（L132）披露了"FIX-B 存储故障停跳也会重置基线、该段时长本已写不入库"的口径。判定为"accepted + 披露"成立。
  - 可选 nit（不阻塞）：L238-239 注释把停跳归因于"leave/quit endpoint"，而实际判据是 L243 的"任何非 active"，与 T-4 隐含口径略有出入，建议补半句"含 FIX-B 存储故障导致的停跳"。

## 5. 越权/范围核查

R4 未新增依赖、未改 QML/Schema/契约；`app.py` 内 N-1/N-2/N-3 守卫与 leave/quit 终结点均带 R3 标记、无 R4 新增产品逻辑，与 commit message 及"产品接线自 R3 零改动"自述一致（受 §0 限制，无法以 diff 独立验证，仅内容+记录佐证）。未发现越权或新产品缺陷。

## 6. 最小处置建议（纯文档，无需改产品/测试，无需重跑 suite）

1. §8 补记被审固定点：`27dbedda..46c7ff5a`（若本轮再提交，另记修复 commit，并保留 46c7ff5a 作为被审点）。
2. §3 第 1/2 行的"R3 最终测试版重取"改为"R4 最终测试版重取"（与日志头一致）。
3. §3 第 3/4 行、§2 AC4、§8 变更清单补上 `targeted-suite-r4.log` / `full-suite-r4.log`（R1/R3 日志作为历史保留）。

**推荐下一步**：ZCode 做一次 doc-only 收口提交后，请 DSH 再做一次纯文档定点复核（无需重跑测试）。可直接转发的指令：

> 任务：DIAG-READING-EXPORT-001-FIX-C R4 文档收口（doc-only）。
> 范围：仅 `doc/handoffs/DIAG-READING-EXPORT-001-FIX-C-de0bf175.md`。
> 要求：①§8 记录被审固定点 `27dbedda..46c7ff5a`（并注明本次收口 commit）；②§3 表第 1/2 行轮次标签由 R3 改 R4；③§3 第 3/4 行、§2 AC4、§8 变更清单补引 `targeted-suite-r4.log` / `full-suite-r4.log`；④不改产品代码、测试与任何日志文件，不重跑 suite。
> 交付：固定 commit + 更新后的 Handoff；随后交 DSH 非作者定点复核（仅文档）。

（本轮未发现需要 Codex 裁决的共享契约/AC 文本问题；F-1 的 AC1 文本裁决仍按计划留在集成层。）
