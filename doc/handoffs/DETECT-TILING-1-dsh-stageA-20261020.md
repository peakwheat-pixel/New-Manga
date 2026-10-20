---
task_id: DETECT-TILING-1
author: DSH（阶段 A 实施；原定 Owner 为 Antigravity，见 §风险与遗留 R1）
recipient: Codex（Lead / Integrator）；Reviewer 应为非作者
base_commit: 5885b182e
delivery_head: 843cfe705
branch: agent/antigravity/DETECT-TILING-1
status: draft
---

# Handoff：DETECT-TILING-1 阶段 A

## 交付结果

**范围**：只做 AC1（预解码安全拒绝 + 内存证据）与 AC4 的 PNG 部分。
AC2 / AC3 / AC5 未开始。

**改动**（3 个文件）：

| 文件 | 改动 |
|---|---|
| `src/bootstrap/core_service.py` | `handle_detect` 的超限拒绝错误信息 |
| `tests/core/test_core_detect.py` | 更新断言 + 增加新消息断言 |
| `verification/DETECT-TILING-1/` | 证据（新增 2 个文件）|

**代码位置不变**：仍在 `image.convert("RGB")` **之前**。
**拒绝时机没有改变，只有错误信息变了。**

**错误信息对照**：

```
改前：
core.detect page exceeds the pixel limit (690x62133 = 42871770 px > 11184810 px)

改后：
core.detect page is too large to process safely: 690x62133 = 42871770 px
exceeds the 11184810 px limit (3.83x over). The page was rejected before any
pixel decoding, so no page-sized buffer was allocated. Reduce the page to at
most 11184810 pixels (about 3344x3344) and retry, or split a tall page into
several shorter images.
```

**新增四项**：超出倍数、拒绝时机说明、可操作目标（等价边长）、替代方案。

**未改任何常量**（`MAX_DETECT_PIXELS` / `MAX_DETECT_PAGE_BYTES` 值不变）。
**未改** PNG/JPEG 白名单、base64 校验、`width`/`height` 一致性校验。

## 验证证据

### 内存实测（AC1 的核心要求）

样本 `690×62133 = 42,871,770 px`，PNG，**mode = RGBA**：

| 项 | 值 |
|---|---:|
| 文件大小 | 20.0 MB |
| 满幅 RGB24 缓冲 | 122.7 MB |
| **满幅 RGBA 缓冲** | **163.5 MB** |
| 打开后峰值增量 | 37.3 MB |
| **拒绝时峰值增量** | **37.3 MB** |

**结论**：拒绝时峰值 37.3 MB，**约为满幅 RGBA 的 23%**。
37.3 MB 主要是 20 MB 编码文件读入 + Pillow 头部解析，**不是像素缓冲**。

证据：`verification/DETECT-TILING-1/stageA-rejection-memory.json`
与 `stageA-rejection-memory.md`。

**测量方法**（阶段 1 踩过四个坑，均记录在案）：

```
- 不用 tracemalloc（Pillow 在 C 层分配）
- 每个样本独立子进程（PeakWorkingSetSize 不回落）
- SetProcessWorkingSetSize 从 kernel32（不在 psapi）
- GetProcessMemoryInfo 显式声明 argtypes（否则 HANDLE 截断、返回 False、读到全 0）
```

### 测试

```
python -m pytest tests/core/test_core_detect.py -q
34 passed in 1.85s
```

**含改动后的 `test_detect_decoded_pixel_cap_rejected`**，
新增断言覆盖：实际尺寸、像素数、上限、超出倍数、拒绝时机、等价边长目标、替代方案。

### 治理检查

```
pwsh -NoProfile -File tools/governance/check.ps1
Governance check: PASS (1 warnings)
```

## 接收方式

```
git checkout agent/antigravity/DETECT-TILING-1
git log --oneline -1        # 应为 843cfe705
git diff 5885b182e..843cfe705 -- src/bootstrap/core_service.py
python -m pytest tests/core/test_core_detect.py -q
```

**主线 `antigravity/P09-AC3-DELETE-HARDEN-1` 停在 `5885b182e`，
不含本次产品改动**（按 `WORKSPACE_GOVERNANCE.md` 的「治理主线分支」规则 §2）。

## 未完成项（不得写为 PASS）

| AC | 状态 | 说明 |
|---|---|---|
| **AC1** | **代码与实测完成，测试已补** | 但**需要独立 Review 才能算完成** |
| **AC4** | **`PARTIAL`** | PNG 已测；**JPEG 超限样本不存在** |
| AC2（`SEC-FMT-005` 四项映射） | **未开始** | |
| AC3（RGBA 阈值缺陷登记） | **未开始** | 但缺陷已在 `stage2-candidate-paths.md` 记录 |
| AC5（回归 + 独立审查） | **回归已跑**（34 通过）；**独立审查未做** | |

### AC4 的 JPEG 缺口

**实测 `test-materials` 的 34 个 JPEG，没有任何一个超过 `MAX_DETECT_PIXELS`。**

**所以 AC4 原文「至少覆盖一个 PNG 与一个 JPEG」无法满足。**

**需 Codex 裁定的三个选项**：

| 选项 | 说明 |
|---|---|
| A. 用合成 JPEG | 生成超限 JPEG，验证拒绝路径但不验证真实内容 |
| B. 改 AC4 为「PNG 必测，JPEG 有则测」 | 承认素材现实 |
| C. 补一张超限 JPEG 到 `test-materials` | 需新素材，触及许可 |

## 下一任务建议（必填）

**建议先由 DSH 做独立 Review（Reviewer 不能是作者本人，而本次实施者就是 DSH，
因此需要 Codex 指派他人，或接受「本 Session 无人可派」并记 limitation）。**

**然后**：

1. **AC2 / AC3 由同一个人续做**（都不需要设计决策，纯登记与映射）。
2. **AC5 的独立审查**须由非作者执行。

**若无人可派**：这本身就是一个治理事实，应记录，而不是让 Task 在没有独立审查的情况下
进入 `done`。

## 风险与遗留

### R1：Owner 不符

**Task 的 `owner` 字段是 `Antigravity`，但实际实施者是 DSH。**

**原因**：`agy`（Antigravity CLI）在本环境**两次卡死**：

| 次 | 日期 | 卡住时长 | 观测 |
|---|---|---:|---|
| 1 | 2026-10-20 上午 | 42 分钟 | CPU 20 秒只涨 0.2s，输出 0 字节 |
| 2 | 2026-10-20 中午 | 10 分钟 | CPU 15 秒**完全没动**，目标文件未改 |

**对照**：同一 `agy` 做**只读探测**任务时 **98.9 秒成功**（正确报出两个常量的值
与行号）。

**所以 `agy` 在本环境能做只读分析，做不了实施类任务。**

**这一条不是本 Task 的缺陷，是环境约束，应登记到治理层。**

### R2：AC4 的 JPEG 缺口（见上）

### R3：RGBA 阈值缺陷仍存在

`MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3` 按 RGB24 计，
而实测样本可为 RGBA。32 MiB ÷ 4 = 8,388,608 px 才是 RGBA 上限。

**本 Task 明确禁止改常量。此缺陷需另立 Task。**

### R4：Handoff 的 `author` 与 `owner` 不一致

**必须由 Codex 在集成时裁定**：是把 `owner` 改为 DSH，
还是保留 Antigravity 并记录「实施由 DSH 代做」。

## 实验附录（仅实验任务）

**阶段 1 与阶段 2 的实测数据**：

- `verification/DETECT-TILING-1/stage1-decoder-memory.md` —— 裁剪不限定解码内存
- `verification/DETECT-TILING-1/stage2-candidate-paths.md` —— 五个候选全部失败
- `verification/DETECT-TILING-1/decoder-memory-probe.json`
- `verification/DETECT-TILING-1/decoder-candidates-probe.json`
- `verification/DETECT-TILING-1-dispatch-incident-20261020.md` —— `agy` 首次卡死
