# 阶段 2：准入规则设计与实现

**产出**: 2026-10-20 · **对应**: `DETECT-MEMORY-GUARD-1` 的 AC2 / AC3 / AC4
**实施提交**: `dd9d61c43`（分支 `agent/dsh/DETECT-MEMORY-GUARD-1`）

## 一、规则（AC2）

**AC2 要求「给出固定上限与可用内存如何组合的规则，并说明为什么这样组合」。**

**实现的规则**：

```
拒绝 当且仅当：
  (1) 页像素数 > MAX_DETECT_PIXELS                        # 主判据，永远生效
  或
  (2) 页所需缓冲 > 可用物理内存 × 0.25                     # 兜底
```

**代码位置**：`src/bootstrap/core_service.py` 的 `handle_detect`，
判据 (1) 在 `image.convert("RGB")` 之前，判据 (2) 紧随其后、仍在 `convert()` 之前。

**为什么这样组合**：

| 理由 | 说明 |
|---|---|
| **可用内存不能是唯一判据** | 阶段 1 实测：本机可用 8.7 GB，上限页只需求 42.7 MB。**只用可用内存等于无限制**——永远放行。 |
| **固定上限不能独自承担极端场景** | 固定上限与机器无关。一台只剩 100 MB 的机器上，11.18 M px 的页（RGBA 42.7 MB）会通过固定上限，然后真的可能 OOM。 |
| **两者组合** | 固定上限负责**正常情况**（实测中它永远是真正的约束），可用内存负责**极端环境**（容器、内存压力、病态小主机）。 |
| **两者都是「收紧」** | 判据 (2) 只在可用内存极低时才额外拒绝，不会放宽判据 (1)。 |

**判定确定性**：给定（页尺寸, 可用内存），结果确定。**没有随机、没有时间依赖。**

## 二、安全系数 0.25 的理由

**`SEC-FMT-005` 只说「适当限制」，没给数值。所以这是我必须给出理由的一个决定。**

**选 0.25，理由三条**：

1. **页缓冲是瞬态副本，不是工作集**。`convert("RGB")` 产生的是一份临时缓冲，
   用完即弃（`tobytes()` 后丢弃）。它不会常驻。
2. **同进程还有其它占用者**：sidecar 本身、检测模型、Pillow 的解码器内部缓冲。
   **若允许一页吃掉 100% 可用内存，其它占用者会被换出或失败。**
3. **0.25 在实际中极宽松**：本机 8.7 GB × 0.25 = 2.2 GB 预算，
   而上限页只需 42.7 MB。**这个系数在健康机器上完全不受约束**——
   它只在可用内存低于约 170 MB 时才开始起作用。

**所以 0.25 不是一个紧的阈值，是一个「只在极端时才说话」的阈值。**

**若将来要调整**，它是一个常量（`_DETECT_MEMORY_SAFETY_RATIO`），改动面小。

## 三、AC3：与既有上限的关系

| 项 | 状态 |
|---|---|
| `MAX_DETECT_PAGE_BYTES` 值未改 | ✅ `32 * 1024 * 1024` |
| `MAX_DETECT_PIXELS` 值未改 | ✅ `MAX_DETECT_PAGE_BYTES // 3` = 11,184,810 |
| 新判据只收紧、不放宽 | ✅ 见 §一 |
| provider 契约未改 | ✅ |
| `ports.detection` 的 byte gate 未改 | ✅ |

**验证**：`git diff` 显示只新增了常量、函数与判据块，
**没有修改任何既有常量的赋值。**

## 四、AC4：错误信息含实际数值

**因内存不足被拒时的实际消息**（实测输出）：

```
core.detect page needs more memory than this host can safely spare:
2000x2000 needs about 15.3 MB, but only 8.0 MB is available and the page
may claim at most 2.0 MB (25% of available). Close other applications and
retry, reduce the page size, or split a tall page into several shorter images.
```

**四项要求都在**：

| 要求 | 消息中对应 |
|---|---|
| 实际可用内存 | `only 8.0 MB is available` |
| 本页需求估算 | `needs about 15.3 MB` |
| 预算 | `may claim at most 2.0 MB (25% of available)` |
| 可操作建议 | `Close other applications… reduce the page size… split a tall page` |

**这是 `SEC-FMT-005` 第 ③ 项（清晰内存警告）的补全。**

**与像素上限拒绝的消息是两条不同的文本**——可区分是哪个判据触发的。

## 五、探测失败的行为（AC1）

```python
avail_bytes = _available_physical_bytes()
if avail_bytes is not None:
    ...
```

**`None` 时直接跳过判据 (2)，退回判据 (1)。**

**这满足 AC1 的「不得回退为放行，而是退到『仅用固定上限』」**：

- 页面已经过了判据 (1) 才走到这里
- 所以 `None` 意味着「用那个已经生效的约束」，不是「什么都放行」

**测试覆盖**：`test_detect_memory_probe_failure_falls_back_to_pixel_cap`
同时断言「超限仍被拒」与「普通页仍处理」。

## 六、测试

**新增 3 个，全文件 39 个通过**：

```
tests/core/test_core_detect.py::test_detect_memory_backstop_rejects_when_host_is_short
tests/core/test_core_detect.py::test_detect_memory_backstop_allows_when_host_is_fine
tests/core/test_core_detect.py::test_detect_memory_probe_failure_falls_back_to_pixel_cap
```

**第一个用的页是 `2000×2000 = 4 M px`，远低于像素上限**——
**所以只有内存判据能拒绝它**，这保证了测试测的是新判据而不是旧判据。

**第二个是「防止总是拒绝」的对照**——否则一个「拒绝一切」的 bug 也能过第一个。

## 七、明确未做

- **未测「可用内存极低时的真实拒绝」**——用 monkeypatch 模拟，不是真的把机器内存吃光。
  理由是那会危及本机其它进程；**模拟是更安全的等价验证**。
- **未在其他机器上验证**——只有本机数据。
- **未实现跨平台**（`GlobalMemoryStatusEx` 是 Windows 专有）。
- **未改任何既有常量值**。
- **未写 Handoff**（下一步）。
