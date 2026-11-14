---
task: TRANS-BINDING-BRIDGE
task_id: TRANS-BINDING-BRIDGE
reviewer: independent sub-agent (r3, read-only, not involved in r1/r2/implementation)
reviewer_agent: agent-5（由 lead 派发；独立上下文）
reviewer_kind: subagent
verdict: approved
decision: approved
date: 2026-11-14
reviewed_head: 3db81c4f0
base_commit: 65425a24f
scope: read-only
---

# Review：TRANS-BINDING-BRIDGE（L1-T-A）r3 窄复核

> **结论：`approved`。r2 的 R2-001 已真实关闭，无 P0/P1/P2 阻断项。T-A 可以以 `closed_with_limitations` 收口**；残余限制沿用 README §5/§6.2（另见 §5）。只发现 2 项 **P3 证据文本**问题（§4），非阻断。

## 0. 审查者、范围与方法

- **身份**：`agent-5`，lead 派发的独立上下文子 agent；只读；**未参与** `TRANS-BINDING-BRIDGE` 的实现/返修，**未参与 r1/r2**。仓库内唯一新增文件是本报告。
- **固定点**：`reviewed_head=3db81c4f0`（父 `65425a24f`），只核 R2-001 修复面，不重做 r1/r2 的全量审查。复核时工作树 HEAD 即 `3db81c4f0`，`git status --porcelain` 只有既有的未跟踪 `doc/reviews/TRANS-BINDING-BRIDGE-r2.md`，源码/测试无未提交差异。
- **方法**：逐行读 diff、调用链与测试；真实 `assemble_production_core` + `CoreServiceServer` 实跑；临时逐项删除 `_write_with_rollback` 的捕获成员做敏感性实验（同一 Python 进程内 `try/finally` 还原文件），每次还原后核 SHA-256；不 commit / 不 push / 不 checkout。
- **还原核验**：实验前工作树 `src/bootstrap/settings_commands.py` SHA-256 = `DDA99263F66D68C0E1405469DB4B8BF4026098B010E7B90C1672C56DD4D5E351`；全部实验后仍为该值；按 LF 归一化后 = `95bc7ed655b56a66887fd314d6d38118bebfe91272d53cc7b7b8388cc11a8925`，与 `3db81c4f0:src/bootstrap/settings_commands.py` 的 blob 内容一致。
- **视角声明**：Architecture = executed（异常族/持久化/分层）；Verification = executed（实际运行、逐项红/绿）；Standards/Spec 未单独使用（模板允许可选）。

## 1. 逐项结论

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | 改动是否正确 | **PASS** | 捕获元组含 `sqlite3.Error`（[settings_commands.py:1054-1061](../../src/bootstrap/settings_commands.py#L1054-L1061)）；`import sqlite3` 在第 10 行；无裸 `Exception`；docstring 的「镜像唯一持久化是 SQLite」与调用链一致 |
| 2 | 新测试构造是否成立（重点） | **PASS** | `commit_then_fail` 先无条件调用 `original(self, **kwargs)` 再抛 `sqlite3.OperationalError`（[test:466-476](../../tests/core/test_trans_binding_bridge.py#L466-L476)）；删掉 `sqlite3.Error` 后该测试**必红**（1 failed / 17 passed，断在镜像回读 `new != old`，[test:489](../../tests/core/test_trans_binding_bridge.py#L489)） |
| 3 | `BindingValidationError` 冗余成员说法 | **PASS** | 运行期 MRO = `BindingValidationError → SettingsError → ValueError → Exception → BaseException → object`；`issubclass(..., ValueError) is True`；删除该成员后 **18 passed / 0 red**，与矩阵一致（但测试 docstring 的敏感性表述有误，见 R3-002） |
| 4 | §6.3 回退敏感性矩阵可复算 | **PASS** | 6 个成员逐项实删复算，红/绿与表格**6/6 一致**（§2.4）；每次还原 SHA-256 一致，最终 `git status` 干净 |
| 5 | 实测 | **PASS** | 定向 **119 passed**（18 bridge + 101 P15）；`check.ps1` 默认 + TaskPath 均 PASS(3 warnings)；`verify_pins` 18/18；`generate_api_inventory --check` `1/80/6=87`；全部 EXIT=0 |
| 6 | 零越界 | **PASS** | `git diff 65425a24f 3db81c4f0 --name-status` 仅 5 个文件：源码、测试、`verification/TRANS-BINDING-BRIDGE/{README,logs×2}`；`apps/**` **0** 改动；父提交确为 `65425a24f` |

## 2. 证据细节

### 2.1 改动正确性

`_write_with_rollback` 的捕获元组现为 `(BindingValidationError, KeyError, OSError, TypeError, ValueError, sqlite3.Error)`（[settings_commands.py:1054-1061](../../src/bootstrap/settings_commands.py#L1054-L1061)），失败路径仍是「先 best-effort `rollback()`，再抛 typed `_fail("unavailable", phase, action, "SETTINGS_UNAVAILABLE")`」。唯一的 `except Exception` 在 [1062-1065](../../src/bootstrap/settings_commands.py#L1062-L1065)，只包住 **rollback 自身**（既有的、有注释的 best-effort），不是 write 的捕获面；`AttributeError`/`NameError`/`RuntimeError` 仍会响亮逃出。**未退化成裸 `Exception`。**

docstring 的选型理由**成立**：

- 镜像的写方法只调 `PipelineDefaultsService` seam（[provider_runtime_mirror.py:119-147](../../src/application/settings/provider_runtime_mirror.py#L119-L147)），模块 docstring 明说「只经 seam、无第二持久化实现」（[23-26](../../src/application/settings/provider_runtime_mirror.py#L23-L26)）。
- seam 的 `save_settings_section` / `save_provider_binding` / `clear_provider_binding` 最终走 [`pipeline_defaults.py:105-120`](../../src/application/settings/pipeline_defaults.py#L105-L120) 的 `self._save(...)`；生产装配注入的 `_save` 是 [`core_assembly.py:1826`](../../src/bootstrap/core_assembly.py#L1826) 的 `lambda **kwargs: SqliteSnapshotProvider(conn, **kwargs)`。
- `SqliteSnapshotProvider.set_defaults` 写的就是 `pipeline_defaults` 单行（[sqlite/pipeline.py:1766-1786](../../src/infrastructure/sqlite/pipeline.py#L1766-L1786)），SQLite 提交/IO/锁失败以 `sqlite3.Error` 族逃出。
- `sqlite3.OperationalError` 的 MRO 实测为 `OperationalError → DatabaseError → sqlite3.Error → Exception → BaseException → object`，**不是** `OSError` 子类；因此修复前它确实会跳过回滚。「与 `OSError` 同类」在 docstring 中是**语义分类**（存储不可写），不是继承关系声明，措辞可接受。

### 2.2 新测试 `test_sqlite_write_failure_rolls_the_mirror_back` 的构造（本复核重点）

**它是否真的先落盘再抛错？——是。** 三条独立证据：

1. **注入点成立**：生产 `_save` 每次都 `SqliteSnapshotProvider(conn, **kwargs)`；其 `__init__` 在参数非 `None` 时调用 `self.set_defaults(...)`（[sqlite/pipeline.py:1751-1757](../../src/infrastructure/sqlite/pipeline.py#L1751-L1757)）。测试在**类**上 `monkeypatch.setattr(..., "set_defaults", commit_then_fail)`（[test:476](../../tests/core/test_trans_binding_bridge.py#L476)），每次实例化的属性查找都会命中补丁；`set_defaults` 本身是 keyword-only（[1766-1772](../../src/infrastructure/sqlite/pipeline.py#L1766-L1772)），与 `commit_then_fail(self, **kwargs)` 签名吻合。
2. **调用顺序**：`calls["count"] += 1` → **无条件** `original(self, **kwargs)` → `if calls["count"] == 1: raise sqlite3.OperationalError(...)`（[test:466-474](../../tests/core/test_trans_binding_bridge.py#L466-L474)）。`original` 是补丁前的原函数，且 `with self._conn` 在 `set_defaults` 内提交；抛错发生在**提交之后**。
3. **反向对照实测**：把 `sqlite3.Error` 从捕获元组删掉后，测试在 [test:489](../../tests/core/test_trans_binding_bridge.py#L489) 红，失败值正是 `https://new.example.test/v1 != https://old.example.test/v1`——“镜像新值”被真实读到，证明写入确实已落盘；若写入没发生，镜像应仍是 old，该断言反而会假通过。

**「镜像回到调用前值」在该构造下是否必然能区分「回滚了」与「从未写过」？——是，但区分力来自“构造 + 断言”的组合，不是断言单独成立。** 第一次调用无条件写新值并提交；只有回滚（第二次调用，`count == 2` 不再抛）才能把它写回 old。上面的反向对照已经把「未捕获 ⇒ 不回滚 ⇒ 镜像保持 new」实测出来，所以 old 只能由回滚产生。反之，若像作者自述的第一版那样在写之前抛错，镜像前后同值，该断言就会在删掉捕获成员时仍然通过——当前版本明确避免了这一点（注释 [467-470](../../tests/core/test_trans_binding_bridge.py#L467-L470) 也写明）。

**删掉 `sqlite3.Error` 会不会红？——会。** 实测 `1 failed, 17 passed`，唯一失败为 `test_sqlite_write_failure_rolls_the_mirror_back`，断在镜像回读（line 489），消息 `sqlite failure escaped the rollback whitelist`。

**一个必须写清的细节**：在该反向对照中，`response["error"]["code"] == "SETTINGS_UNAVAILABLE"` 仍然通过。原因是 P15 dispatch 外层 catch-all 会把逃出的异常统一映射为该码（README §6.3 已登记）。因此**错误码不是判别信号，镜像状态才是**；这条测试的判别断言正是镜像回读，设计正确。

### 2.3 `BindingValidationError` 冗余成员

运行期实测：

```
MRO: ['BindingValidationError', 'SettingsError', 'ValueError', 'Exception', 'BaseException', 'object']
issubclass(BindingValidationError, ValueError): True
issubclass(BindingValidationError, SettingsError): True
```

类定义见 [errors.py:6,22](../../src/application/settings/errors.py#L6-L22)。从捕获元组单独删除 `BindingValidationError` 后实跑 **18 passed / 0 failed**，与 §6.3 的 0 红一致，故「已被 `ValueError` 覆盖、删掉行为不变、保留仅表达意图」的**结论成立**。

但见 **R3-002**：新增 seam 测试的 docstring（[test:536-539](../../tests/core/test_trans_binding_bridge.py#L536-L539)）与 README §6.3 的解释句把自己说成对「删除该成员」敏感，实测并非如此——该用例只有在**同时**删除 `BindingValidationError` 与 `ValueError` 时才红。

### 2.4 §6.3 回退敏感性矩阵复算

方法：每次只从捕获元组删一个成员（字节级替换），只跑 `tests/core/test_trans_binding_bridge.py`（18 个用例），跑完立即在 `finally` 中还原原字节。实测结果：

| 回退的成员 | 实测结果 | 变红的用例 | 与 §6.3 表一致？ |
|---|---|---|---|
| `KeyError` | **1 failed / 17 passed** | `test_store_update_failure_rolls_the_mirror_back`（line 381） | ✅ |
| `OSError` | **3 failed / 15 passed** | `test_store_create_failure_rolls_the_mirror_back`、`test_store_delete_failure_restores_the_mirror`、`test_store_binding_failure_rolls_the_mirror_back` | ✅ |
| `TypeError` | **1 failed / 17 passed** | `test_store_type_error_rolls_the_mirror_back`（line 531） | ✅ |
| `ValueError` | **1 failed / 17 passed** | `test_store_format_error_rolls_the_mirror_back`（line 512） | ✅（但解释句有误，见 R3-002） |
| `sqlite3.Error` | **1 failed / 17 passed** | `test_sqlite_write_failure_rolls_the_mirror_back`（line 489） | ✅ |
| `BindingValidationError` | **0 failed / 18 passed** | — | ✅ |

补充对照（为核对 R3-002）：同时删除 `ValueError + BindingValidationError` → **2 failed**，新增 `test_seam_validation_error_after_write_rolls_back_the_mirror`（line 567）变红。即矩阵表格本身**可复算、6/6 准确**；不准确的是 §6.3 表格后的解释文字与测试 docstring（P3）。

还原核验：全部实验结束后 `src/bootstrap/settings_commands.py` SHA-256 仍为 `DDA99263...`；LF 归一化后与提交 blob `95bc7ed6...` 一致；`git status --porcelain` 仍只有既有的未跟踪 r2 报告。**未提交任何临时改动。**

## 3. 实测记录

环境：Windows，`C:\Python314\python.exe`（Python 3.14），仓库根 `G:\CODEX\New Manga`，HEAD `3db81c4f0`。

| 场景 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 定向 pytest | `C:\Python314\python.exe -m pytest -q tests/core/test_trans_binding_bridge.py tests/core/test_p15_core_settings.py` | **119 passed in 13.55s**（collect-only：18 + 101 = 119） | 0 |
| 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` | 0 |
| 治理 TaskPath | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-BINDING-BRIDGE.md` | `Governance check: PASS (3 warnings)` | 0 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | 0 |
| inventory | `C:\Python314\python.exe tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`；`1/80/6=87` | 0 |
| 全量 pytest | 未重跑 | **NOT_RUN**（窄复核边界；提交内 `logs/pytest-full.log` 声称 3562 passed/10 skipped，本报告不为其背书） | — |

3 个 warning 均为既有治理提示（7 个非终态 Task；STATUS/REBASELINE 达到预算 80%），与本提交无关。

## 4. Findings（P3，非阻断）

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-001 | P3（文档/证据文本） | [README.md:94](../../verification/TRANS-BINDING-BRIDGE/README.md#L94) | §6.2 仍写「`_write_with_rollback` 现捕获 `(BindingValidationError, KeyError, OSError, TypeError, ValueError)` —— 这正好是…」，漏掉 `sqlite3.Error`，与同节下方表格第 101 行及代码 1054-1061 冲突；会让读者误以为修复未落盘 | 逐行比对：代码 6 成员 vs 该句 5 成员；同节表格已列 `sqlite3.Error` | 改为 6 成员元组，并把「正好是实际会抛的族」改成「已覆盖的族」 | open（非阻断） |
| R3-002 | P3（文档/证据文本） | [README.md:137](../../verification/TRANS-BINDING-BRIDGE/README.md#L137)；[test:536-539](../../tests/core/test_trans_binding_bridge.py#L536-L539) | 两处都声称删除**单个**成员即可让 seam 回滚用例变红，与实测不符：删 `BindingValidationError` → 0 red；删 `ValueError` → 仅 format 用例 1 red、seam 仍绿；只有**两者同删**才 2 red。当前文字还错误地说该路径「由 ValueError 分支接住」（实际先由元组首成员 `BindingValidationError` 接住，二者互为冗余） | §2.4 三组实测 | 把解释改为「BVE 与 ValueError 互冗余；该用例只在两者都缺席时红」，并修正 docstring 的“goes RED”表述 | open（非阻断） |

两项均只影响证据文本的可读性/准确性，不影响运行行为、不改变测试红绿矩阵，不构成收口阻断。

## 5. 残余限制（`closed_with_limitations` 口径）

R2-001 的修复消除了「SQLite 异常跳过回滚」这一具体缺口，但**不消除**以下已登记窗口（README §5/§6.2）：

1. **回滚本身失败**：若回滚调用也抛错（例如同一 SQLite 已不可写），[settings_commands.py:1062-1065](../../src/bootstrap/settings_commands.py#L1062-L1065) 会吞掉回滚异常并仍抛 typed 失败，留下「镜像新值 / JSON 旧值」；无跨库事务可用。这是 R2-001 的固有余量，不是回归。
2. **进程在两次写之间被强杀**：镜像已提交、JSON 未写，无崩溃恢复标记。
3. **外部并发改写 JSON**：store 是读-改-原子写，外部写者造成丢失更新（既有风险）。
4. **book/chapter scope 绑定不驱动执行**：扁平槽只接受 global（R-6 裁决）；T-C 展示面需带「scoped 绑定当前不驱动执行」的约束（R2-003 deferred）。
5. **网络 profile 镜像不在本卡**（README §5.1）；`Rendering` 无 pipeline step。
6. **未验证真实 Host↔Core 端到端**（README §5.4）。
7. 本 r3 **未重跑全量 pytest**（§3），只对定向面与四门禁负责。

## 6. 明确回答

1. **R2-001 是否已真实关闭？——是。** 捕获元组含 `sqlite3.Error`（代码 1054-1061），选型理由与真实持久化链一致，未退化为裸 `Exception`；新测试**先提交新值再抛 `sqlite3.OperationalError`**，删除 `sqlite3.Error` 后必红（1 failed，镜像回读 new != old），证明它能区分「回滚」与「从未写过」；错误码因 dispatch catch-all 不是判别信号、镜像状态才是，测试的判别断言选对了。定向 119 passed、四门禁全绿、零越界，均与提交自述一致。
2. **T-A 能否以 `closed_with_limitations` 收口？——可以。** P0/P1/P2 阻断项 = 0；仅 2 项 P3 证据文本（R3-001/R3-002）建议在收口前顺手更正或登记接受。收口时应保留 §5 的限制（尤其“回滚本身失败”与 scoped 绑定不驱动执行），并由 DSH 完成 Task 生命周期字段（当前 `status: in_progress`、`reviewer: null`、`integration_commit: null`）与集成验证；本报告不代做这些动作。
3. **复核边界**：本报告只对 `3db81c4f0` 有效；head 再变则自动转为历史记录。复核期间仅新建本文件，未 commit / push / checkout；为敏感性实验临时改过的源码已还原，SHA-256 与提交 blob 一致。

## 7. 方法学备注（可复现）

- 敏感性实验的还原脚本在**同一进程**内用 `try/finally` 写回原始字节，避免异常/中断留下脏文件；每个 case 的变体 SHA 与最终还原 SHA 均与提交内容核对。
- `git diff --check 65425a24f 3db81c4f0` 只报告 `verification/.../gates-final.log` 的 CRLF 行尾（生成型日志，用户可见的空白差异），源码/测试无 whitespace 错误；不单列为 finding。
