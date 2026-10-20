# ZCode 独立 Review：DETECT-MEMORY-GUARD-1

- **Reviewer**: ZCode（非作者）
- **日期**: 2026-10-20
- **审查对象**: 分支 `agent/dsh/DETECT-MEMORY-GUARD-1`，base `2c569457c`，HEAD `fbd8fc496`（实现提交 `dd9d61c43`，stage2 证据 `fbd8fc496`；stage1 证据在 base 内）
- **方法与限制**: 本 Review 环境无 Bash 权限客户端，未执行 `git diff` / `pytest`。审查基于当前工作区（分支即 HEAD `fbd8fc496`）直接读取 `src/bootstrap/core_service.py`、`tests/core/test_core_detect.py` 全文与两份 stage 证据；diff 边界与测试结果均未独立复核（见「明确未核实」）。行号引用以 HEAD 工作区为准。

## 结论

**APPROVE_WITH_COMMENTS**

行为本身合格：判据真实消费宿主可用物理内存、失败回退安全、错误消息满足 AC4、测试对判据 (2) 的存在性有判别力，且证据文档把「正常机器上永不触发」主动放在显著位置而非粉饰。**本 Task 值得存在**（论证见逐项判定最后一行），不建议以 limitation 收口。

但收口前有一个应修项（P1）：判据 (2) 缺少与 `DETECT-TILING-1` 轮 P1-1 同构的「拒绝必须发生在 `convert()` 之前」顺序护栏——当前代码顺序正确，但测试无法防止重构把它挪到分配之后而全绿。

## 逐项判定

| 项 | 判定 | 依据 |
|---|---|---|
| 3.1 组合是否真满足「检查可用物理内存」，还是形式化读数 | **满足，非形式化** | `core_service.py:1499-1516`：`_available_physical_bytes()` 的返回值直接参与准入决策（`needed_bytes > budget_bytes` 则拒绝），错误消息携带实测数值（AC4）。这不是「读了不用」 |
| 3.1 0.25 系数理由是否站得住 | **站得住** | stage2 §二三条理由成立。补充量化：拒绝线为 `avail < 16N`（N=像素数），而 `convert` 真实峰值需求约 3N–7N（见 P2-1），0.25 系数给峰值留了 >2x 余量，同时吸收了 4 B/px 估算的口径误差。系数已常量化（`_DETECT_MEMORY_SAFETY_RATIO`）且有 `"25%" in message` 断言锚定，变更会强制过测试。stage1 §四曾说「此值我不能自己定」，stage2 以 AC2「实施时给出理由」路径补足——自洽，可接受 |
| 3.1 判据 (2) 是否可能放宽判据 (1) | **不可能** | 两判据是顺序执行的独立 raise（(1) 在 `:1470`，(2) 在 `:1496`），逻辑上是拒绝集合的并集（OR）。(2) 不在 (1) 的任何条件分支内，不存在「过了内存检查就绕过像素上限」的路径。(1) 用解码头尺寸（`Image.open` 惰性读头），与探测结果零耦合 |
| 3.2 `_DETECT_BYTES_PER_PIXEL = 4` 是否正确 | **方向正确（保守），但「worst-case」注释口径过强（P2-1）** | 对最终 RGB 缓冲（3N）：高估 33%，保守 ✅。误拒窗口精确量化：拒绝当 `4N > 0.25A` 即 `A < 16N`；按同一预算口径「3 B/px 本可处理」当 `A > 12N`。故误拒仅发生在 `12N < A < 16N`（2000×2000 页即可用内存 48–64 MiB 之间）——只在本来就在悬崖边的机器上出现，且消息给出数值与可操作建议，属正确的保守方向 |
| 3.3 `None` 回退是否安全 | **安全，论证成立** | 代码顺序上判据 (1)（`:1470`）先于判据 (2)（`:1496`）执行完毕才可能走到回退分支；32 MiB 文件上限（`:1438`）与格式白名单（`:1457`）同样独立于探测。probe 自身 `win32` 守卫 + 全异常吞掉（`:329-360`），`None` 是唯一失败形态，不可能抛出。非 Windows 永远 `None` → 永远只有固定上限，stage1 §五已按 AD-001 记录为范围而非缺陷 |
| 3.4 测试 1 的 4 M px 是否真低于像素上限 | **是** | `2000×2000 = 4,000,000 < 11,184,810`（`MAX_DETECT_PIXELS` = 32 MiB // 3），且测试内有显式前置断言 `assert 2000 * 2000 < MAX_DETECT_PIXELS`（`test_core_detect.py:787`）——即使未来上限被调低，测试会先在这个自检上失败而不是静默改测判据 (1)。做得对 |
| 3.4 删掉判据 (2) 测试会不会失败 | **会（测试 1）** | 页面合法（4 M px、小文件、PNG）→ 删除后走到 `convert`，尺寸匹配，FakeDetectionProvider 返回空结果 → `res["error"] is None` → `assert res["result"] is None` 红。测试 2/3 删除后仍绿（它们是对照组/回退路径测试），判别力集中在测试 1，组合恰当 |
| 3.4 「测试全绿但功能不存在」的可能 | **有一条真实路径（P2-2）** | 三个测试全部 monkeypatch 探测函数，与宿主解耦（这本身是对的——否则 CI 机器内存波动会引入 flaky）。但因此「真实 probe 永远失败返回 `None`」（如 ctypes 结构在某环境错位）时，判据 (2) 静默不存在而 39 个测试仍全绿。当前唯一反证是 stage1 手测三次读数 8.7 GB——它是「probe 真的能拿到数」的唯一实证 |
| 3.5 「monkeypatch 模拟而非真实吃光内存」是否偷懒 | **不是，理由成立** | 判据逻辑（给定 avail=8 MiB 时决策正确）与 API 真实性（给定机器时返回真值）是两个正交命题：前者由测试覆盖，后者由 stage1 实测覆盖，拼起来是完整的。真实吃光物理内存会危及本机其它进程；且 Windows 下「可用物理内存」与「进程可分配」受 commit limit 制约（见 P2-5 备注），用 Job Object 限制进程 commit 测的其实是另一个语义。monkeypatch 是本 Task 正确的验证选择 |
| 3.5 Task 是否值得存在（永不触发 ≠ 死代码？） | **值得，是规则完备性** | 理由四条：① `SEC-FMT-005` 第①项是明文要求，`DETECT-TILING-1` 已全文映射出零命中——缺失是事实，不是本 Task 发明的工作；② 「正常机器不触发」是防御性判据的本质属性（除零保护在除数非零时同样不触发），其目标场景（容器、内存压力、低配机——本产品 NSIS 包 438 MiB + 模型数百 MB，低配机不是幻想）真实存在；③ 实现质量非敷衍：真实 API、确定性判据、可区分错误消息、probe 失败安全回退、测试有判别力；④ 证据把「永不触发」量化写进 stage1 §二标题级位置——这是反 checkbox 的姿态。限定：其价值上限就是兜底，收口文档不得宣传为「OOM 防护完成态」；`SEC-FMT-005` 的「分块处理」已被 `DETECT-TILING-1` 的 PNG 单 zlib 流论证在本 face 排除，故「固定上限 + 可用内存检查 + 清晰警告」三项就是本 face 的完整合理形态 |

## 发现的问题（按严重度）

### P0（阻断）

无。

### P1（应修）

**P1-1 判据 (2) 缺少「拒绝发生在 `convert()` 之前」的顺序护栏。**
`test_detect_memory_backstop_rejects_when_host_is_short`（`test_core_detect.py:765`）断言了错误码、消息内容与 `seen_request is None`，但**没有**断言拒绝先于 `convert()`。若有人在重构中把判据 (2) 挪到 `image.convert("RGB")`（`core_service.py:1518`）之后，全部断言仍绿，而该判据的全部意义——在页级缓冲分配**之前**拒绝——已静默失效（OOM 风险在 convert 内兑现，且消息中 "may claim at most" 变成事后陈述）。这与 `DETECT-TILING-1` 轮 P1-1（`test_core_detect.py:547-597`，spy `Image.Image.convert` 断言 `conversions == []`）完全同构，且手法已在同一文件内，复用成本约三行。修法：在测试 1 中复用 `spy_convert` 模式，断言拒绝路径上 `conversions == []`。

### P2（建议）

**P2-1 `_DETECT_BYTES_PER_PIXEL = 4` 的「Worst-case」注释口径过强。**
`core_service.py:317-319` 注释称 4 = worst-case bytes per decoded pixel。这对**最终 RGB 缓冲**成立，但对**转换峰值**不成立：RGBA 源 PNG 的 `convert("RGB")` 期间源缓冲（4N）与目标缓冲（3N）并存，峰值约 7N；同 mode 源的 copy 峰值约 6N。故 4 B/px 对峰值是低估而非保守。行为上被 0.25 系数吸收（拒绝线 16N vs 峰值需求 7N，仍有 >2x 余量），不构成实际风险；但注释与 stage2 §二第 1 条「页缓冲是瞬态副本」的理由表述应把口径限定为「destination buffer」，并注明转换峰值约 6–7 B/px 由安全系数覆盖，避免后人把「worst-case」当成峰值保证。

**P2-2 真实 probe 路径零自动化覆盖。**
三个新测试全部 patch 探测函数，「probe 永远返回 `None`」（功能静默退化回 `DETECT-TILING-1` 完成态）不会让任何测试变红。stage1 手测是目前唯一实证。建议加一个不 patch 的最小存在性测试：`sys.platform == "win32"` 时断言 `_available_physical_bytes()` 返回正 int（非 Windows 跳过）——一条断言即可让「checkbox 虚勾」这条路进测试网。

**P2-3 测试 3 断言强度偏弱。**
`test_detect_memory_probe_failure_falls_back_to_pixel_cap`（`test_core_detect.py:840`）对超限分支只断言 `res["error"] is not None`，未断言 `code == E_INVALID_REQUEST`，也未像测试 1 那样校验消息属于像素上限那条文本——当前无法区分「被像素上限拒」与「被其它任何校验拒」。

**P2-4 stage2 §一「没有时间依赖」措辞过强。**
判据**函数**对输入确定 ✅，但端到端结果并非时不变：可用内存读数本身是时间函数（stage1 实测三次波动 7.4 MB），同一页在 avail 于 16N 附近波动时可能一次放行一次拒绝。语义上这是「当前快照」判据的固有属性，建议措辞改为「判据函数对（页尺寸, 读数）确定」。

**P2-5 消息单位口径为 MiB 标 "MB"。**
`core_service.py:1503-1505` 除以 `1024*1024` 却显示 "MB"（实为 MiB）；stage2 §四样例「8.0 MB」同口径。面向用户的可读消息、判据本身按字节精确比较，无实质影响，仅记录。

## 明确未核实的内容

- **未执行 `git diff 2c569457c..fbd8fc496`**（本 Review 环境无 Bash 权限）。变更边界以任务书所述四文件 + 工作区实读交叉验证为准，不排除 diff 中存在未列出的其它改动。
- **未运行测试**。「全文件 39 个通过」采信 stage2 §六声明；按文件内测试函数清点（16 个非参数化 + 15 + 5 个参数化 + 3 个新增 = 39）数目吻合。
- **未读 Task 文件原文**（`AC1–AC4` 文本来自任务书转述与 stage 文档引用）。
- **未独立复测 stage1 的 API 读数**（8.7 GB / 波动 7.4 MB），采信其记录。
- **未在非 Windows 平台验证** `sys.platform != "win32"` 分支（标记 `pragma: no cover`）。
