---
task_id: DETECT-MEMORY-GUARD-1
author: DSH
recipient: Codex（Lead / Integrator）
base_commit: 2c569457c
delivery_head: fa8615dc5
branch: agent/dsh/DETECT-MEMORY-GUARD-1
status: draft
---

# Handoff：DETECT-MEMORY-GUARD-1

## 交付结果

**目标**：补 `SEC-FMT-005` 第 ① 项「检查可用物理内存」与第 ③ 项「清晰内存警告」。
**来源**：`codex-adjudicate-tiling-closeout-r36.md` 建议另立本 Task。

**改动**（2 个代码文件 + 2 份证据 + 1 份 Review）：

| 文件 | 内容 |
|---|---|
| `src/bootstrap/core_service.py` | 新增 `_available_physical_bytes()`、两个常量、准入判据 |
| `tests/core/test_core_detect.py` | 新增 4 个测试 |
| `verification/DETECT-MEMORY-GUARD-1/stage1-memory-api.md` + `.json` | API 实测 |
| `verification/DETECT-MEMORY-GUARD-1/stage2-admission-rule.md` | 规则设计与理由 |
| `verification/DETECT-MEMORY-GUARD-1/dsh-zcode-review.md` | 独立 Review |

**规则**：

```
拒绝 当且仅当：
  (1) 页像素数 > MAX_DETECT_PIXELS            # 主判据，永远生效
  或
  (2) 页所需缓冲 > 可用物理内存 × 0.25         # 兜底
```

## 一个必须让接收者知道的事实

**判据 (2) 在正常机器上永不触发。**

**阶段 1 实测**：本机可用 8.7 GB，上限页需求 42.7 MB（**0.49%**）。
**只有可用内存低于约 170 MB 时它才开始起作用。**

**ZCode 在 Review 里专门讨论了「这个 Task 是否值得存在」，结论是值得**，理由四条：

1. `SEC-FMT-005` 是明文要求，缺失已被 `DETECT-TILING-1` 逐项映射证实
2. **防御性判据天生如此——除零保护在除数非零时同样不触发**
3. 实现质量非敷衍（真实 API、确定性判据、可区分消息、安全回退）
4. **证据把「永不触发」量化写进标题级位置**

**限定**：**收口文档不得宣传为「OOM 防护完成态」。** 它的价值上限就是兜底。

## 验证证据

### 测试

```
python -m pytest tests/core/test_core_detect.py -q
40 passed in 2.17s
```

**4 个新增**：

| 测试 | 验证什么 |
|---|---|
| `test_detect_memory_backstop_rejects_when_host_is_short` | 模拟 8 MiB 可用，拒绝一个 **4 M px（未超像素上限）** 的页；**并 spy `convert` 断言未被调用** |
| `test_detect_memory_backstop_allows_when_host_is_fine` | 模拟 8 GiB，放行（防止「总是拒绝」的 bug 也能过上一条）|
| `test_detect_memory_probe_failure_falls_back_to_pixel_cap` | 探测返回 `None` 时：超限仍拒、普通页仍处理 |
| `test_memory_probe_returns_real_value_on_windows` | **不 patch 探测函数**，断言真实返回正 int |

### 关键实证：顺序护栏真的会响

**把整个内存判据块移到 `image.convert("RGB")` 之后，第一条测试转红**：

```
AssertionError: memory rejection must happen before any convert() call;
convert was called with [(2000, 2000)]
```

**还原后 40 passed。**

**这是本 Task 最重要的证据**——它证明护栏不是形式上的。

### 治理

```
Governance check: PASS
```

## 接收方式

```
git checkout agent/dsh/DETECT-MEMORY-GUARD-1
git log --oneline -6         # 应为 fa8615dc5
git merge --ff-only antigravity/P09-AC3-DELETE-HARDEN-1   # 先同步主线
git diff 2c569457c..fa8615dc5
python -m pytest tests/core/test_core_detect.py -q
```

**主线 `antigravity/P09-AC3-DELETE-HARDEN-1` 停在 `2c569457c`，不含本次产品改动。**

## 未完成项（不得写为 PASS）

| AC | 状态 |
|---|---|
| AC1 可用内存探测 | **完成**（含失败回退与不 patch 的实证）|
| AC2 准入规则设计 | **完成**（规则 + 0.25 的三条理由）|
| AC3 与既有上限关系 | **完成**（diff 验证无常量被改）|
| AC4 清晰内存警告 | **完成**（消息含实际可用、需求、预算、建议）|
| AC5 回归 + 独立审查 | 回归 40 通过；**Review 已做（ZCode），但其 P1/P2 处置见下** |

**独立 Review 的处置**（`dsh-zcode-review.md`：`APPROVE_WITH_COMMENTS`，P0 无）：

| 项 | 处置 |
|---|---|
| P1-1 缺「拒绝先于 convert」护栏 | **已修**（`80fb11811`）并拿到红色证据 |
| P2-1 `worst-case` 注释口径过强 | **已修**（`fa8615dc5`）：改为「目标缓冲口径，峰值约 6N–7N 由安全系数覆盖」 |
| P2-2 真实 probe 无自动化覆盖 | **已修**（`80fb11811`）|
| P2-3 测试 3 断言弱 | **已修**（`80fb11811`）|
| P2-4 「无时间依赖」措辞过强 | **已修**（`fa8615dc5`）|
| P2-5 MB/MiB 单位 | **已修**（`fa8615dc5`）|

**6/6 已处置。**

## 下一任务建议（必填）

**`ARCH-DOC-REBASELINE` 是唯一剩下的 READY 节点**，但它的 7 个 AC 全部在等下游
（见 `verification/ARCH-DOC-REBASELINE/ac1-ac3-gap-analysis-20261020.md`）。

**所以本 Task 收口后，建议 Codex 裁定**：

1. **`ARCH-DOC-REBASELINE` 的 AC 拆分**（Gate 层 vs 消费层），或
2. **以 limitation 收口**，或
3. **指派新的实质 Task**

**在裁定之前，无需派发新的实现任务。**

## 风险与遗留

### R1：判据 (2) 在正常机器上永不触发

**这是设计意图，不是缺陷**（ZCode 明确论证过）。
**但它意味着「本 Task 的代码在绝大多数运行中不执行」——收口文档必须如实说明。**

### R2：只有本机数据

**8.7 GB / 42.7 MB 是这一台机器的读数。**
**低配机（例如 4 GB 内存、可用 200 MB）上的行为未测。**

### R3：Windows 专有

`GlobalMemoryStatusEx` 是 Windows API。**当前产品边界是 Windows 单平台（AD-001），所以这是范围而非缺陷。**

### R4：安全系数 0.25 未经调优

**它是「只在极端时才说话」的值。** 在上限页需求 42.7 MB 的前提下，
**0.25 意味着拒绝线在可用内存 170 MB 附近**——这个位置是否合适，**没有跨机器数据支撑。**

### R5：转换峰值未被直接测量

**P2-1 指出 RGBA 源转 RGB 的峰值约 6N–7N，这是推算，不是本 Task 实测。**
**`DETECT-TILING-1` 测过 `convert_full` 与 `tobytes` 的峰值，但那是另一组样本。**
**若将来要精调 0.25，应先测这一项的峰值。**

## 实验附录

- `stage1-memory-api.json`：三次读数的原始值
- 阶段 1 md §二：`42.7 MB ÷ 8700 MB = 0.49%`
