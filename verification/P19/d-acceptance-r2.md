# P19 D 变体验收证据 R2（用户裁决 A 后补齐）

- 日期：2026-10-17；执行者 dsh；**用户裁决 A**（接受 D 为等效验收）
- 脚本：`verification/P19/run-d-acceptance-v2.ps1`（**可重放**；隔离 `NEWMANGA_DATA_ROOT`，不触碰用户数据）
- 产物：`verification/P19/d-run-v2/`（`trace.log` + `uia/01..08` 原始转储 + `app-err.log`）
- 被测：`m2rc1-desktop.exe`（含 P19-BOOT-1 修复 + 重建 sidecar，sidecar sha256 `41932ced…`）

## 1. 导航/动作轨迹（trace.log，节选）

| 动作 | 结果 |
|---|---|
| READY 门（等到 pane 不含 starting） | 书架 **37** 元素 ✓ |
| `🛠️ 工作台` | OK (en=True) → **95** 元素 |
| `📖 阅读器` | OK → **30** 元素 |
| `⚙️ 设置` | OK → **58** 元素 |
| `Provider` 分类 | OK → 58 元素 |
| `新建 Profile` | OK → **78** 元素（表单） |

## 2. **表单提交（隔离数据）—— PASS**

- 填入：`provider_id=e2e-provider-a`、`display_name=E2E Provider A`、`endpoint=https://api.example.test/v1`、`model=e2e-model`；`OCR` 勾选 → **ToggleState=On**
- 点 `保存` → **`SUBMIT PROFILE_VISIBLE -> PASS`**（提交后 74 元素，列表中出现 `E2E Provider A`）
- **旁证（校验正确性）**：首次提交时留空 `endpoint`/`model`，表单**正确拦下**并给出逐字段提示：
  `endpoint 必须是绝对 HTTP(S) 地址，且不含 userinfo/query/fragment`、`model 不能为空` → **校验准确、无泄密**

## 3. UIA enabled/disabled 观察（AC4 待裁量）

**9 个「未开放」分类均为 `enabled=True`，且点击后页面变化（`PAGE_CHANGED`）**：

`OCR / 图片修复 / 排版样式 / 模型GPU / 任务并发 / 缓存Revision / 回收站 / 备份恢复 / Plugin-Hooks`

→ **交互层可点可导航**；功能层不可用（分区内容标「未开放」）。**是否满足 AC4"可见但不可操作"须由 Reviewer/用户裁量**（执行方不自判）。

## 4. 结果判定（执行方视角，待 Codex 复核）

| 判据 | 状态 |
|---|---|
| 导航/动作轨迹 | **PASS**（trace.log 全量时间戳） |
| 表单提交（隔离数据） | **PASS**（含校验正确性旁证） |
| 原始 UIA 转储 | **PASS**（8 份，含每页 enabled/offscreen 字段） |
| 可重放脚本 | **PASS**（v2，隔离根，exit 0） |
| AC4「不可操作」 | **待裁量**（观察到可点可导航） |
| 未跑真实主流程 | **导入→Run→导出、阅读器翻页仍未跑**（非本 Task 已覆盖项，如实保留） |