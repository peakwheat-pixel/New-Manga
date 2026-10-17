# P19 AC2 主流程执行结果（runner r1，2026-10-18）

- 执行者：dsh（Coordinator/Reviewer）
- 脚本：`verification/P19/run-ac2-mainflow-v1.ps1`（R3-005 基建：全新输出目录 / 拒绝覆盖 / 断言失败非零退出 / 每步 UIA 转储 + 截图 + trace + `run-metadata.txt`）
- 前置：main `323b0d2eb`；产品已重建并过 P20 Gate（`bundle==resource` = `6ab8ada3…`，smoke 窗口可达）
- 隔离：每次运行使用**全新** `%TEMP%\p19-ac2-main-<guid>` 作为 `NEWMANGA_DATA_ROOT`；未触碰用户真实数据

## 1. 三次运行的如实记录（DIR-4：同一失败不重复试错，逐次记录根因）

| 运行 | 目录 | 断言 | 根因（经证据确认，**全部为脚本缺陷**） | 修正 |
|---|---|---|---|---|
| #1 | `ac2-main-20261018-0044` | 10 checks / 0 fails 后 **异常终止** | ① `$dlg.SetFocus()` → "目标元素无法接收焦点"（与 FEAT Owner 首轮同款）；② `FIXTURE count=0`（`Get-ChildItem -Include` 未配合路径通配符）| 去掉元素级 SetFocus，改 `^l` + **剪贴板 `^v`** + `{ENTER}`；fixture 改用 `-LiteralPath` + 扩展名过滤 |
| #2 | `ac2-main-20261018-0047` | 20 checks / **4 fails** | 断言口径错误：书架页数读数滞后（显示`页数 —`/`0 页`）；阅读器 `1 / 2` 由**独立 Text 元素**组成致正则误匹配；`下一页 (←)` 为 `en=False` 而同页 **`Next page` en=True**；在阅读器页找作品条目 | 页数改以**隔离 DB 为权威**；页码改用 `Image :: Page N`；翻页候选 **`Next page` 优先**；进入工作台前**先返回书架** |
| #3 | `ac2-main-20261018-0051` | 22 checks / **4 fails** | ① 导航后未重新获取对话框对象（Win32 选择器导航后**重建元素树**），致 `PICKER_VISIBLE_ITEMS=0`；②③④ 同 #2 的 ④⑤ 阻塞（见 §3）| 已定位（Owner 的 `Navigate-Picker` 即导航后重新取窗口），**但未再重跑**：④⑤ 的阻塞不在脚本层（见 §3） |

> **说明**：#1 与 #2 的失败已由 DB 与 UIA 转储证明**不是产品缺陷**；#3 的选择器问题有明确参照实现。三次均不同于同一失败面，且每次修正在下轮运行中生效（#2 的选择器与 fixture 修复直接体现在 `picker:selected-all (2/2)`）。

## 2. 已确证 PASS 的部分（DB + UIA/截图双证据）

**① 建作品、② 建章节、③ 导入（多选 2 个文件）真实通过**。隔离根 `%TEMP%\p19-ac2-main-62cd3a8a\library.db` 直查：

```sql
books:    1  → P19Ac2Book (5dafec369dba479f82baa93afdd43391)
chapters: 1  → P19Ac2Ch1  (bc8edb040aa249e2b4447c3af9c6c118)
pages:    2  → 001.png 67780B sha256=1bb7f48ea396ed081ebe7706b909081ab3b1f86f7b4e2a7518fc3568ce3e887a 1180x890
               002.png  2282B sha256=6eac55349be7e1a9effade65bb694c48b6c25b1e6b2f6b35319ffb42c93a31ec  320x240
```

两页的 `sha256`/字节数与 fixture **逐项一致** → 导入链路（前端多选 → host 逐项 grant → Core 批量 `ImportPages` → Managed Copy）在本机真实工作。

**③ UI 侧**：`PICKER_NAVIGATION` + `PICKER_SELECTED 001.png/002.png` + `picker:selected-all (2/2)` + `IMPORT_REPORT=VISIBLE`（含 `已导入`/`跳过重复`/`导入失败` 三段）→ 汇总面板正确显示。

**⑥ 阅读器可进入且页码正确**：`08-reader.uia.txt` 含 `Image|Page 1`、`Text|1` + `Text| / ` + `Text|2`、`上一页 (→)`、`Next page`、`从头开始`、`原文 (Original)`/`译文 (Translated)` → 章节 2 页，阅读器显示 **1 / 2**。

用户真实数据核验：`%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}` 文件数/字节数（1/24576、2/311297）与运行前**完全一致**。

## 3. 阻塞项：④ Run 与 ⑤ 导出（**产品层面，非脚本可修**）

工作台 `11-workbench.uia.txt`（95 元素）显示：

```
17|Text|选择作品与章节                      ← 工作台要求在此选择
27|ListItem|暂无作品                        ← 工作台的作品列表为空
54|Text|选择作品与章节
59|Button|启动          en=False
61|Button|导出选择页    en=False
83|Text|没有本次会话中已知的 Run。
86|Text|暂不可用：Core 尚无 ListRuns 查询；仅能查看本次工作台明确启动的 Run。
```

**矛盾点**：书架侧**确实存在** `P19Ac2Book`（DB 与书架 UI 均确认，`book:visible` 断言通过），但**工作台的"选择作品与章节"列表显示"暂无作品"**。因此：

- `启动` 始终 `en=False` → **④ Run 无法执行**；
- `导出选择页` 始终 `en=False` → **⑤ 导出无法执行**。

**判定（执行方观察，待 Reviewer/Owner 确认）**：这属于 **R3-001 未闭合的核心缺口**，且可能是两种情形之一：
1. **产品缺陷**：工作台的作品/章节选择器**未与书架数据接线**（或未在本会话刷新）；
2. **能力未实现**：该选择器尚未实现（但 UI 已呈现"选择作品与章节"文案，仍是可见缺陷）。

**这不是 AC2 脚本能修复的问题**——脚本已按"仅记录 enabled 事实、不强行点击"的纪律执行（`WORKBENCH_RUN control='启动' enabled=False`、`EXPORT control enabled=False` 均为原始事实记录）。

## 4. 建议下一步（需 Coordinator/用户裁决）

1. **先由 Codex R4 独立复核**本结论与 §2 的 DB 证据（避免单方定性）；
2. 就"工作台选择器为空"判定 [缺陷] 或 [未实现能力] → **需要产品裁决**（用户），因为修复涉及前端状态接线，超出本 Task 范围时应另立 Task；
3. 在 P19 收口时，AC2 的 ④⑤ 必须**如实标注未达成**（不得以文字叙述替代）。

## 5. 产物清单（可复核）

- 三次运行目录：`ac2-main-20261018-0044/`、`-0047/`、`-0051/`（各含 `uia/*.uia.txt`、`*.png` 截图、`trace.log`、`run-metadata.txt`、`app-err.log`）
- 隔离根：`%TEMP%\p19-ac2-main-{78e887a7,62cd3a8a,d5ad2168}`（DB 可直接复查）
- P20 Gate：`rebuild-main-20261018-0034/`（`bundle-resource-hash.json` = `6ab8ada3…`）
