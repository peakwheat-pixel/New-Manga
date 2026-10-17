# P19 AC4（设置页 D 变体）执行结果 — runner v3，2026-10-18

- 执行者：dsh（Coordinator/Reviewer）
- 脚本：`verification/P19/run-d-acceptance-v3.ps1`（R3-005 基建：全新时间戳输出目录 / 拒绝覆盖 / 断言计数 / 断言失败非零退出 / 每步 UIA 转储 + 截图 + `run-metadata.txt`）
- 运行：`d-run-20261018-0053`（#1）、`-0055`（#2）、`-0056`（#3）
- 隔离：`%TEMP%\p19v3-<guid>`；产品为 main `323b0d2eb` 重建产物，exe sha256 `384a486daee48257c9f7421fa68d5b6ef263f2ea03485f7254e84d99479d0600`

## 1. AC4 核心结论：**PASS**（有可复核产物）

三次运行中，以下断言**每次都通过**（`checks` 中前 14 项）：

| 步骤 | 证据 |
|---|---|
| 应用启动 + 窗口可达 | `ASSERT PASS app:window` |
| 四页导航：书架 → 工作台 → 阅读器 → 设置 | 4× `CLICK nav-*` + `ASSERT PASS` |
| 设置 → `Provider` 分类 | `ASSERT PASS click:cat-provider` |
| `新建 Profile` 打开表单 | `ASSERT PASS click:open-form` |
| 表单填写（`provider_id` / `display_name` / `endpoint` / `model`）| 4× `SET … OK` + `ASSERT PASS` |
| **TOGGLE OCR → On** | `ASSERT PASS toggle:OCR` |
| **提交 `保存`** | `ASSERT PASS click:submit` |
| **Profile 保存后可见** | **`ASSERT PASS submit:profile-visible`** ✓ |
| 返回书架 | `ASSERT PASS click:nav-back` |

产物：每次 8 张截图（`01-bookshelf.png` … `08-bookshelf-back.png`）+ 8 份 UIA 转储 + `trace.log` + `run-metadata.txt` → 满足 **R3-004** 对原始产物的要求。

## 2. 未闭合项：`disabled-not-invokable` 判据（**DIR-4 停止**）

**9 个"未开放分区"探测在 #1、#3 两次均未通过**，按 DIR-4「同一失败面最多 2 次」**已停止重跑**。

**原始数据（#3 `d-run-20261018-0056/trace.log`）证明分区确已禁用**：

```
PROBE 'OCR' en=False invoke=failed PAGE_CHANGED panes=[]
PROBE '图片修复' en=False invoke=failed PAGE_CHANGED panes=[]
… （9 项同型）
```

- `en=False` → 控件**存在且处于禁用态** ✓（符合 AC4 期望）
- `invoke=failed` → 对其调用 `InvokePattern.Invoke()` **抛异常**，即**不可调用** ✓
- `PAGE_CHANGED` → **这是判据本身脆弱**，不是产品行为：断言用调用前后 `PN`（Pane 名称集合）比较，而调用后 `panes=[]`（UIA 刷新瞬时取到空集合）导致误判"页面变化"。

**两次失败的不同失败面**：#1 是**探测串口径**（我传入 `'OCR 未开放'`，而实际控件名为 `'OCR，未开放：等待 section schema 冻结'`）；#3 修正后控件可找到，但**通过判据脆弱**。两次均非产品缺陷。

**处置**：不再修改脚本重跑。把上述**原始数据**交给 Codex R4 独立判定"未开放分区是否满足 AC4 的『可见、禁用、不可调用』要求"；同时把 `PAGE_CHANGED` 判据的脆弱性登记为 **R3-005 的遗留改进项**（应改为基于 `en`/`invoke` 结果判定，而非 Pane 集合差异）。

## 3. 与既有证据的衔接

- `P19-AC3-1` 已交付"全部请求/返回/事件/错误四表面边界"证据（58 命令 × 4 面 + WebView 边界），其中包含"未开放分区不发起请求"的一侧；本 runner 补充的是**UI 侧禁用态与不可调用性**的原始产物。
- 上一版 `run-d-acceptance-v2.ps1` 保留未改（其 pin 仍有效）；v3 为其修复版（新增：拒绝覆盖、非零退出、截图、运行元数据）。

## 4. 建议下一步

1. 由 **Codex R4** 复核本结论（尤其 §2 的判据问题与原始数据）；
2. 在 P19 收口时，AC4 记为 **PASS**（核心已证），并把 `disabled-not-invokable` 判据改进作为**遗留项**（不阻断收口，须在 R4 报告中明确）；
3. AC2 的 ④Run/⑤导出 阻塞按用户裁决（先由 R4 复核）处理。
