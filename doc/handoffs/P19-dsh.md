# P19 Handoff（Owner/执行者：dsh）—— 版本 R3（2026-10-17）

> **本版按 Codex R3 复核（`verification/P19/codex-review-r3.md`，decision=`changes_requested`）重写**，取代此前过度声称的 R1/R2 版本。**未完成项一律如实标注**。

## 1. Task 与交付
- Task：P19（四页安全 E2E 验收）；`status: in_review`；`delivery_head: 4fb8fc8aacc3798cdcc46049171cc6c9d740a5d3`（全 SHA）
- 验收方式：**D**（真实 WebView2 + UIA 语义断言）—— 用户 2026-10-17 裁决 A 接受；**CDP 在本机构建不可用**（Tauri 覆盖 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`）
- 隔离：全部 GUI 运行使用 `NEWMANGA_DATA_ROOT` 隔离根（真实布局只读复制），并有 `source_unchanged=true` 保全检查

## 2. AC 状态（**以 Codex R3 为准**）
| AC | R3 判定 | 说明 |
|---|---|---|
| AC1 验收方式 | **PASS** | 用户裁决 A 接受 D |
| AC2 四页主流程 | **FAIL** | ① 建作品、② 建章节 **实测 PASS**（隔离根真实持久化）；**③ 导入未完成**（选择器可弹出，确认动作未达成，0 页入库）；**④ Run / ⑤ 导出 / ⑥ 阅读器翻页 未执行** |
| AC3 安全边界 | **FAIL** | 仅做过 UI 文本层观察；**缺**全命令「请求/返回/事件/错误」四处扫描与 WebView 访问面证明；**不得**以 Host 反例或 UI 文本替代 → 已另立 `P19-AC3-1` |
| AC4 未开放能力不可操作 | **PASS** | 重建产品实测 9/9 `IsEnabled=False`，可见性与原因文案保留（`ac4-verified-rebuilt-r5.md`）|
| AC5 可复现与证据 | **FAIL** | 可复现性不足（缺原始轨迹/转储/退出码的完整性）|
| AC6 交付与关闭材料 | **FAIL** | 元数据与证据表已于本轮修正（全 SHA、状态 `in_progress`、**Canonical Evidence 表 10 行**）；**resource closeout 未完成** |

## 3. R3 findings 与处置
| ID | 级别 | 处置 |
|---|---|---|
| R3-001 | P1 | **待执行**：AC2 主流程（重试 ③ 确认 → ④⑤⑥），逐步留原始轨迹 |
| R3-002 | P1 | **在飞**：`P19-AC3-1`（全域四扫描 + WebView 边界证明）|
| R3-003 | P1 | **部分完成**：`delivery_head` 全 SHA ✓、`canonical_evidence_status: in_progress` ✓、Canonical Evidence 表已建（10 行含 SHA-256）✓；**resource closeout 与旧叙述清理待办** |
| R3-004 | P2 | 待办：AC2/AC4 新实测补原始轨迹/转储/时间戳/退出码 |
| R3-005 | P2 | 待办：D 重放脚本改为**全新输出目录 + 拒绝覆盖 + 断言失败返回非零** |

## 4. 已修并集成的缺陷（P19 的真实产出）
1. **启动即崩（exit 101）** → `P19-BOOT-1`（done，`c6d2e9a30`）：自举判据错置 + 类型化失败 + 锁写入截断。
2. **打包 sidecar 早于修复** → 重建 bundle 并校验 hash 一致（源码修好 ≠ 产品修好）。
3. **9 个「未开放」分区可点可操作**（AC4）→ `P19-UI-FIX-1`（done，`8a0afacea`）真禁用 + 保留可见性与原因。
4. **顶栏导入静默无反馈** → `P19-UI-FIX-2`（done，`ebec0b030`）弹窗 + 可见原因 + 三入口一致。
5. **`+ 新建作品` 不可用**（用户裁决 A）→ 经硬门核对发现**整条创建能力从未实现** → 立功能链 `FEAT-CREATE-1..4`（全部 done）：契约 rev 2.8 → Core（535 passed）→ host（51 命令；107/0/1；12/0）→ 前端（278 passed，GUI 实测 `IsEnabled=True`）。

## 5. 已知限制与风险
- **③ 导入的确认动作**：本机 Explorer 文件夹选择器不暴露确认按钮（UIA `SetValue/FindFirst` 超时、`Alt+S` 无效）→ 待攻；**若最终仍不可驱动，须由用户/R4 裁定是否接受为工具限制**，不得自行关闭。
- **执行者自述的 3 次失误**（已留痕）：入口选错误报缺陷、导入中杀进程、对 Explorer 选择器误用 UIA。
- **测试基线**：Core 535 · 前端 278 · Rust source 107/0/1（须设 `M2RC1_PYTHON`）· packaged 12/0。

## 6. 下一步（不由本 Handoff 关闭任何 AC）
1. 完成 `P19-AC3-1`（AC3）。
2. A 线：修脚本基建（R3-005）→ 攻 ③ → ④⑤⑥。
3. 补 R3-004 的原始产物；完成 resource closeout 与旧叙述清理。
4. 送 **Codex R4** 复核；据 R4 结论 closeout P19（`done` 或**经用户确认**的 `closed_with_limitations`）。