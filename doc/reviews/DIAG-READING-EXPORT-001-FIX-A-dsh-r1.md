## 只读审查报告（DSH 非作者 Reviewer）

审查范围：`git diff 32ef1dd6..3f3bd7a9`（base=`32ef1dd6`，实现=`77a78b25`，Handoff=`3f3bd7a9`）。本会话未修改任何文件。
说明：本 worktree 的沙箱授权失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），**所有 shell 命令均不可用**，因此无法执行 `git diff/status` 或复跑 pytest/探针；下列核对基于工作区文件全文阅读、主仓 worktree 同名文件逐行比对、worktree reflog、以及 verification 日志交叉核算。

已正面核对通过的要点：
- 提交链与 reflog 一致：`32ef1dd6 → d793939d(claim) → 77a78b25(fix) → 3f3bd7a9(docs)`（`G:/CODEX/New Manga/.git/worktrees/DIAG-FIX-A-zcode/logs/HEAD`），Handoff 的 base/owner_head 口径正确。
- 4 处改动精确定位：base `:274/:289/:426/:442` → tip `:281/:296/:433/:449`（`and finished` / `and failures`）；其余 6 处 `:310/:346/:372/:391/:396/:415` 未动。与主仓（main@878bf2a5）同名文件全文逐行比对，**除文件头注释重写与这 4 处谓词外零差异**，未加 sleep/skip/重试，未放宽断言。
- 探针只读性成立：无 `monkeypatch`/`setattr`/mock；只用探针内子类（`TimestampedVM`/`BrokenVM`）覆盖 `_finish`，产物只落 `tempfile.TemporaryDirectory()`，无新依赖。
- 全仓口径诚实且可算：1321 = 1316+5，5 个 skip 为 2 docTR+1 numpy+2 torch；6 个 OpenSSL 用例的 skip 条件是 `shutil.which("openssl")`（`tests/network/test_connection_tester.py:24-25`、`test_transport_tls.py:22-23`），本运行未出现在 SKIPPED 摘要中，差值解释与 DIAG 基线 1310+11 自洽。
- 产品面零改动可信：`src/ui/viewmodels/export/viewmodel.py`（418 行）与主仓副本逐行相同；`requirements.txt` 与主仓副本相同。

decision=changes_requested

findings：

- **P2** — `tests/reading_export/test_viewmodels.py:346-349`（base `:339-342`）＋文件头注释 `:63-73`＋Handoff §1（`doc/handoffs/DIAG-READING-EXPORT-001-FIX-A-77a78b25.md:42-45`）
  - 触发条件：忙碌主线程／事件队列被占用（判别探针同款刺激）时，工作线程发出的 `changed` 由主线程 lambda 槽经 Qt **排队投递**；等待谓词只读普通属性 `vm.running`，可在 `changed` 投递前返回，而紧随其后的 `assert snapshots, "the changed signal must have fired"` 消费的正是该排队投递列表。同一 `running=False` 观察时刻，`snapshots` 可能仍为空 → 该断言失败。
  - 影响：FIX-A 声称"其余 6 处只读普通属性、**无排队竞态暴露面**"对 `:346` 不成立（`:372` 的"只读普通属性"表述也不准确——它同样消费 `snapshots`，只是缺少非空守卫，失败面表现为 `half_published([]) == []` 断言真空）。即：同一文件、同一根因的同类 flake 仍可命中，且该错误结论同时被写进文件头注释（会成为后续维护者的持久规则）。该形态不是历史形态（`running=False, finished=[]`），故 AC1 未被推翻，但交付完成度表述失真。
  - 建议：把 `:346` 谓词按交付自身规则改为 `not vm.running and snapshots`（或断言前补一次 `qapp.processEvents()`，DIAG 报告 §6 已给出该选项）；`:372` 至少更正理由表述。若决定保留现状，必须在文件注释与 Handoff 中如实改述为"已知残余暴露面"并登记后续，不能以"无暴露面"收口。

- **P3** — `verification/DIAG-READING-EXPORT-001-FIX-A/probe-terminal-wait-discrimination.py:154,167,218-232`
  - 触发条件：任何一次运行，含"新谓词全部超时"的坏运行。
  - 影响：阶段 B 的 `misses` 在谓词含 `state["arrived"]` 时数学上恒为 0（`misses` 只在 `not state["arrived"]` 时自增），故 Handoff §2 AC1 引用的"0/400 miss"不构成独立证据（真正载荷是 `completed: 400/400` 与延迟列）；verdict 未校验 `completed == iterations`，若 `completed=0` 仍会打印"B: clean"；`main()` 无条件 `return 0`，所以 Handoff/日志中的"EXIT=0"不是通过判据。
  - 建议：verdict B 增加 `completed == iterations` 条件，任一 verdict 为负时返回非 0；Handoff 改引 `completed` 作为 B 阶段通过依据。

- **P3** — 判别探针 `:78-86`（`pump_until` 逐字复制）与 `:152-154`（谓词复刻）；AC2 证据强度
  - 触发条件：探针与真实测试文件发生漂移（例如未来改动测试的 `pump_until` 或断言）时不被发现。
  - 影响："先红后绿 + 故障注入保持红"证明的是**同款谓词模式**的判别力，而非被修改测试函数本身；因 Task 禁止 monkeypatch 产品/测试文件，副本是合规做法，但结论强度应如实标注。
  - 建议：Handoff 明确写"证据基于逐字副本，非真实测试函数执行"，或在不违反禁改约束的前提下改为 import 真实 `pump_until`。

- **P3** — Handoff §3 表第 1 行（`doc/handoffs/...:65`）：定向 `15 passed` 无日志归档（`verification/DIAG-READING-EXPORT-001-FIX-A/` 仅 probe log 与 full-suite.log）
  - 影响：定向结果不可独立复核（全仓日志已覆盖同一文件，实际影响低）。
  - 建议：集成前补一份定向运行日志（命令／环境／passed,skipped／EXIT）。

- **P3** — `doc/STATUS.md:7,45` 仍记录 FIX-A `proposed / NOT_RELEASED`，而 Task 文件已记录 overnight 释放 + claim `d793939d`
  - 触发条件：集成核验时对状态源。
  - 影响：治理口径与 Task 文件不一致；且释放记录由 Owner 同一 ZCode 会话的"代行 Codex"写入，AC6 的真实 Codex 追认未完成（Handoff 已诚实披露）。`doc/STATUS.md` 不在 FIX-A 允许写集合内，故这是集成侧待办而非本次越权。
  - 建议：Integrator 在集成 commit 同步 STATUS 并标注"代行 Codex / 待追认"关系。

- **P3** — `tests/reading_export/test_viewmodels.py:449`（base `:442`）的改动实为惰性
  - 触发条件：`pages_provider` 返回空列表时，`startExport()` 在**主线程**同步调用 `_fail`（`src/ui/viewmodels/export/viewmodel.py:262-264`），根本没有工作线程与排队投递，谓词首次求值即为真。
  - 影响：4 处改动中实际覆盖竞态的只有 3 处（`:281/:296/:433`）；不影响正确性，但 Handoff 的"4 处"框架易被读成同为竞态点。
  - 建议：Handoff/注释注明该处属"消费信号列表即改"规则的一致性改动。

未覆盖风险：

1. **无法执行任何命令**（沙箱 ACL 失败），`git diff/status`、`git diff --check`、pytest、探针、`PATH` 检查全部未复跑；本报告全部结论来自静态阅读与交叉核算，不代表我已独立复现任何运行结果。
2. **文件级范围未用 git 核对**：主仓 worktree 为 main@878bf2a5（≠ base 32ef1dd6），我只能用主仓同名文件作代理。已全文比对 `tests/reading_export/test_viewmodels.py`、`src/ui/viewmodels/export/viewmodel.py`、`requirements.txt`（仅发现 FIX-A 声称的差异）；其余 `src/**`、Schema/Domain Contract、`requirements-dev.txt` 未逐一比对，不能完全排除越权改动（结合 reflog 仅 3 个 commit 与交付说明，风险低）。
3. **工作区是否有未提交改动无法检查**；reflog 末条为 `3f3bd7a9` 只说明最后提交，不等于工作区干净。
4. **U3 仍开放**：修复后 0 命中仅在合成忙碌刺激（2 ms/次 processEvents 忙等，旧谓词 324/400 命中）下成立；真实全仓事件负载是否为历史触发条件未被证明，Handoff §4 已如实披露，我未能增强证据。
5. 6 个 OpenSSL 用例"实跑通过"的解释依赖 Git Bash PATH 事实（`/mingw64/bin/openssl`），我只能核对 skip 机制与计数自洽，无法直接验证 PATH。

推荐下一步（基于当前仓库状态）：由 Owner ZCode 在 `agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics` 上补一个最小 commit——按上述 P2 扩展 `:346`（必要时 `:372`）的等待语义并更正文件头注释／Handoff §1 的"无暴露面"表述，随后把 `probe` verdict 的 `completed` 判据一并修正；交 DSH 复审该增量（只审增量 diff），再由代行 Codex 集成并在 `doc/STATUS.md` 同步状态与"待真 Codex 追认"标注。可直接转发指令：`在 DIAG-FIX-A 分支上：1) 将 tests/reading_export/test_viewmodels.py:346 的等待谓词改为 not vm.running and snapshots（并复核 :372 同类暴露面）；2) 更正文件头注释与 Handoff §1 中"其余 6 处无排队竞态暴露面"的表述；3) probe 的 verdict B 增加 completed==iterations 条件且判定为负时返回非 0；4) 保留全部既有证据，提交最小增量并 Handoff 注明 Δdiff。`
