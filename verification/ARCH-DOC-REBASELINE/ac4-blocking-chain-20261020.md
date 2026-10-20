# AC4 的因果链：它等的那个阻塞，当天就解除了

**产出**: 2026-10-20 · **性质**: 只读溯源 · **结论**: **AC4 不能补，但不是因为 P18 还没跑，而是因为 P18 从未重测**

## 一、AC4 的原文（`doc/tasks/ARCH-DOC-REBASELINE.md`）

> P18 的 JA/KO、无字页、质量 AC 对应新链，明确真实样本/真值/阈值/version/device/model/endpoint
> 证据责任；旧结果不继承。

**原报告状态**：`NOT_RUN`

> **未达成（NOT_RUN 原因）**：新链质量要求与 7 维证据责任体系已建立，**实测基准待 P18 消费执行**。

## 二、P18 的实际状态

`doc/tasks/P18.md`：**`closed_with_limitations`**

| AC | 状态 |
|---|---|
| AC1 质量口径缺失清单 | **`[x]`** |
| **AC2 JA/KO 实验方案** | **`[ ]`** —— 「产品发布门槛属产品取舍，Coordinator 不代定」|
| AC3 逐步 terminal 一致性 | **`[x]`** |
| AC4 素材许可与指纹 | **`[x]`** |
| **AC5 最小真实实验切片** | **`[ ]` —— BLOCKED** |
| AC6 不越界 | **`[x]`** |
| AC7 可复核性 | **`[ ]`** |
| AC8 固定 head 审查 | **`[ ]`** |

**P18 的 AC5 被三项技术缺口阻塞，第一条是：**

> **`ImportPages` = `UNKNOWN_COMMAND`** —— **导入侧 wire 从未冻结/实现**
> （契约 rev 2.1 中仍为 PROPOSAL）；此项同时阻塞 **P12** 与 **P19**。

**所以 AC4 的「待 P18 消费执行」= 待一个被 BLOCKED 的 AC。**

## 三、但那个阻塞**当天就解除了**

### 3.1 `ImportPages` 现在确实实现了

**Python core 侧**：`src/bootstrap/core_service.py` 有真正的命令分支：

```python
# P16-C1 rev 2.1 added Reader/Export; P12-C1 rev 2.2 adds ImportPages.
if command == "ImportPages":
```

**Tauri 侧**：`apps/desktop/src-tauri/src/library_bridge.rs:2789`

```rust
let result = self.round_trip("ImportPages", payload) {
```

**还有测试**：`apps/desktop/src-tauri/src/packaged_sidecar_tests.rs:278`

```rust
.expect("batched ImportPages should process all selected sources");
```

### 3.2 时间线（这是关键）

| 事件 | 日期 | commit |
|---|---|---|
| **P18 关闭** | **2026-10-16** | — |
| **`ImportPages` 接入 Python core** | **2026-10-16** | **`cac219fe7`** — `feat(P09-FU2): wire ImportPages runtime through verified source refs` |
| `ImportPages` 出现在 `library_bridge.rs` | 2026-10-16 | `2ad590a31` — `feat(HOST-ISSUER-1): add trusted host reference issuer` |

**P18 的阻塞项与它的修复，是同一天的。**

**P18 的 `run-record.md` 记录的是修复之前的运行**：

> 命令 exit=0（runner 完成归档）；Core sidecar exit=0。
> request-level 结果：`core.ping=ready`；**`ImportPages=UNKNOWN_COMMAND`**

**而此后没有任何一次重跑。**

## 四、所以真实情况是

**不是「P18 还在等一个未实现的功能」。**

**是「P18 等的那个功能当天就实现了，但 P18 从未回去重测」。**

**这与 AC5 是同一个模式**（上一轮）：
- `ARCH-DOC-REBASELINE` AC5 写「待 P20 执行」→ P20 完成后**没人回来接**
- `ARCH-DOC-REBASELINE` AC4 写「待 P18 消费执行」→ P18 的阻塞解除后**没人回来重测**

**两次都是「跨 Task 的等待没有提醒机制」。**

## 五、因此 AC4 的判定

**AC4 依然不能判 MET**——因为：

- P18 的 AC5 仍是 `[ ]`
- P18 的 `closed_with_limitations` 记录里，那条阻塞**被列为未解除**
- **没有一份证据表明有人重跑过 P18 的实验切片**

**但缺口已经变了**：

| 原来的理解 | 实际 |
|---|---|
| AC4 在等一个**未实现**的功能 | AC4 在等一次**重测** |

**前者是开发债务，后者是流程债务。后者便宜得多——`ImportPages` 已经可用。**

## 六、我没有做的事

- **未修改** P18 的任何字段（`closed_with_limitations` 是已生效的终态，
  重开需授权）。
- **未修改** `ac4-p18-quality-and-responsibility.md`。
- **未修改** AC4 的勾选状态。
- **未重跑** P18 的实验切片——那需要真实素材（Manga109 已按 AC4 要求**不重新获取**）、
  标注真值与模型端点，属于产品实验工作，不是本 Agent 在本轮能自行授权的。

## 七、给裁定的三个问题

1. **P18 是否应重开？**
   它的 AC5 阻塞（`ImportPages`）已解除，`ImportPages` 现在有实现和测试。
   重跑实验切片的成本远低于当初。
2. **若不重开**，AC4 能否以「阻塞已解除但未重测」为由判 **PARTIAL** 而非 NOT_RUN？
3. **跨 Task 的「等待」要不要有个登记处？**
   本 Session 已遇到两次同一模式（AC5 等 P20、AC4 等 P18）。
   **被等的一方完成时不会通知等待方。**

## 八、一个方法上的收获

**我一开始以为要「补 AC4 的实测」。**

**查下去才发现**：AC4 自己没有实测可补——它是**映射与责任规范**，
它的「实测」是**消费方 P18 的实测**。

**所以「补 AC4」这件事本身不成立。** 能做的是**解除 P18 的阻塞**，
而那需要重开一个已关闭的 Task。

> **有些 AC 永远不能自己完成。它们只能由别人完成，而别人不知道在等。**

**这次我花了三轮（110/111/112）才看清这一点**：
AC5 是「等的东西有了」、AC6 是「等的东西一半没有」、
AC4 是「等的东西有了但等的人不知道」。
