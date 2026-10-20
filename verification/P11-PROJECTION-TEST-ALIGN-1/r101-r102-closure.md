# R-101 / R-102 处置：ZCode r189 的两条非阻断建议已闭合

**产出**：2026-10-20 · **来源**：`dsh-zcode-review-r189.md` §二 Findings
**Task**：`P11-PROJECTION-TEST-ALIGN-1`
**性质**：Review 建议（非阻断），本轮主动实施并做判别力验证

## 一、两条建议是什么

### R-101

> **「已处置 Interrupted」只有直调 `_button_enablement` 的用例；
> `build_projection → _button_enablement` 的 `interruption_disposition` 接线
> （`projection.py:262-266`）只有无处置方向被端到端覆盖。
> 若接线漏传该参数，现有测试不红。**

**即**：单元测试证明函数内部逻辑对，**不证明 `build_projection` 把字段传过去了**。

### R-102

> **矩阵用 `enabled.get(...) is True` 对照 5 列，不抓「多余的第 6 键」**
> （如实现给 PENDING 多发 `can_retry_failed=True`，矩阵仍绿）。

**即**：逐列检查**看不到不该存在的键**。

## 二、改动

### R-102：矩阵改为 dict 全等

**前**：

```python
actual = (
    enabled.get("can_pause") is True,
    enabled.get("can_stop") is True,
    ...
)
assert actual == expected      # 逐个 5 列
```

**后**：

```python
P11_BUTTON_MATRIX = {
    PipelineRunStatus.PENDING: {"can_stop": True},
    PipelineRunStatus.RUNNING: {"can_pause": True, "can_stop": True},
    ...
}
assert enabled == expected     # 整字典全等
```

**为什么这能抓到**：实测对照（同一份 `_button_enablement` 输出，人为加一个键）：

| 检查方式 | 结果 |
|---|---|
| 旧五列元组 | `(False, True, False, False, False) == (False, True, False, False, False)` → **True（漏报）** |
| **新字典全等** | `{'can_stop': True, 'can_retry_failed': True} == {'can_stop': True}` → **False（抓到）** |

### R-101：补两条端到端测试

| 新测试 | 断言 |
|---|---|
| `test_interrupted_with_a_disposition_is_wired_through_build_projection` | `run.interruption_disposition = "restarted"` → 5 个按钮全 `False` |
| `test_interrupted_without_a_disposition_still_offers_the_three_ways_out` | `run.interruption_disposition = None` → `continue`/`restart`/`abandon` 为 `True`，`stop` 为 `False` |

**成对的原因**：两条合起来把接线**两个方向**都钉住——
**一个完全忽略该字段的 `build_projection`，无论往哪边错，都会红一条。**

## 三、判别力验证

| 破坏 | 目标测试 | 结果 |
|---|---|---|
| `_button_enablement` 收到 `interruption_disposition=None`（模拟接线丢失）| R-101 新测试 | **RED** |
| PENDING 额外返回 `can_retry_failed=True` | R-102 矩阵 | **RED** |

**`BOTH BLIND SPOTS CLOSED`。**

## 四、验证过程中我犯的错（第三次同类）

**R-102 的第一次 sabotage 是**绿的**——即看起来「建议没价值」。**

**原因不在代码，在我的破坏方式**：

**测试文件写的是**：

```python
from application.tasks.projection import _button_enablement, build_projection
```

**它持有自己的引用。我 patch `application.tasks.projection._button_enablement` 够不到它。**

**改为 patch 测试模块的绑定（`test_projection._button_enablement`）后才 RED。**

### 这是本会话第三次同样的机制

| 轮次 | 场景 | 被谁抵消 |
|---|---|---|
| r184 | 破坏 `_module_present` / `probe_module` | `env_sim` 自己在同一批名字上 patch |
| r189 | 只改 `OPTIONAL_PROVIDER_MODULES` 加 `PIL` | registry 测试用**显式** present 集合 |
| **r190** | 破坏 `_button_enablement` | 测试模块**已 import 了本地引用** |

**三次的共同点**：**我破坏的是一个名字，而代码/测试用的是另一个绑定。**

**而三次都表现为「测试没红」——与「缺陷不存在」在输出上无法区分。**

## 五、结果

| 项 | 前 | 后 |
|---|---:|---:|
| `tests/workbench/test_projection.py` 测试数 | 16 | **18** |
| 运行结果 | 16 passed | **18 passed** |
| R-101 状态 | open（建议） | **已闭合** |
| R-102 状态 | open（建议） | **已闭合** |

## 六、明确未做

- **未改 `src/application/tasks/projection.py`**（两条建议都只涉测试）
- **未改 `P11_BUTTON_MATRIX` 的 9 个状态覆盖**（ZCode 已独立核对与 §4.5 逐行一致）
- **未处理 R-003 / R-103（base_commit 口径）**——移交 Codex
- **判别力脚本未入库**（一次性工具），逻辑见 §三
