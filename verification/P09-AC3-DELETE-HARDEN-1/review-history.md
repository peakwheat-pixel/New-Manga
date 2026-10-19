# P09-AC3-DELETE-HARDEN-1 复审与返修历史

> 本文件保存逐轮 Review、裁决与返修叙事。**当前状态以 `doc/tasks/P09-AC3-DELETE-HARDEN-1.md` 与正式 Handoff 为准。**
> 按协作协议 §4.1，**新 head 或新 Review 使旧结论自动降为 HISTORICAL**。

---

## Codex R1 复审与返修记录（2026-10-19）

**复审对象**：固定区间 `a04e4ea78d5b33a0f91efcdc06b396391c4b165e..4824ed5d4872a6dc519ca6e671bfa6485bd47d9a`（48 提交，其中 18 个带 P09 标记）。
**复审结论**：**`changes_requested`**（见 `verification/P09-AC3-DELETE-HARDEN-1/codex-review-r1.md`）。
**逐项 AC 独立结论**：AC2 / AC3 / AC6 / AC8 / AC9 / AC10 = **PASS**；AC1 / AC4 / AC5 / AC7 / AC11 / AC12 = **PARTIAL**。

**Codex 确认的关键事实**（含对本 Task 自述的证伪）：AC3 的真实 Tauri 错误通道确实把 `items` 作为对象字段传给前端（作者担心其无效，**该担心不成立**）；AC7 的 9 条查询经**独立 AST 比对**与 `verify_all.py` 实际一致。

### Finding 处置

| ID | 优先级 | 状态 | 处置提交 |
|---|---|---|---|
| F-001 | P1 | **已关闭（用户裁决方向 A，2026-10-19）** | `10202dc4e` |
| F-002 | P1 | 已修 | `51bd814d1` |
| F-003 | P1 | 已修 | `992bdff36` |
| F-004 | P1 | 已修 | `8af40864b` |
| F-005 | P1 | 已修 | `ac46e162c` / `354971bed` |
| F-006 | P2 | 已修 | `0add9072b` |
| F-007 | P2 | 已修 | `0add9072b` |

**F-001 的范围冲突（本 Task 唯一阻挡项）**：为实现 AC1，本 Task 新增了 IPC 命令 `library_list_recycle_bin_books`。该命令**未在 M2-C1 契约中冻结**，与本 Task 禁止范围「不新增未冻结的 IPC 命令」冲突。Codex 确认「路由事实成立、数据源正确」，但**契约授权超出 Owner 权限**，已上报用户裁决：
- **方向 A**：认定 AC1 原文「把回收站专用删除命令注册到 Tauri production command」**本身即授权**，补记契约 allowlist 后关闭 F-001。
- **方向 B**：暂停 AC1 的命令注册，另立 M2-C1 契约冻结 Task。

### 返修中发现的「按字面修复仍不成立」

**AC4 的 F-002 是两个叠加缺陷**：Codex 只指出 `managed_rel_path` 存了绝对路径；按此修完后验证**仍然失败** —— 生产装配两处 `producer_root` 传的是 `data_root`，而托管路径相对的是 **storage root（`data/managed`）**。**只修 Codex 指出的那一个，GC 依旧无法回收。** 这与作者交付前自报的「AC4 只证明写入、未证明可回收」相互印证。

### 历史 pin 保护

运行 `verify_all.py` 会重写 `verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json`（已 pin 的历史证据）。本次运行后 diff **仅 `verified_at` 一行**，`status: PASS` 与 `ac_results` 逐字节未变 —— 该差异本身即证明 F-005 **未改变任何判定**。按「不得改写历史 pin，只允许追加」的约束，该文件已**恢复为原提交字节**，运行记录**追加**写入 `verification/P09-AC3-DELETE-HARDEN-1/f005-orphan-scan-run.md`。

### 返修后的验证

| 套件 | 结果 |
|---|---|
| `tests/core` | 558 passed |
| `tests/storage` | 86 passed |
| `tests/m2_resource_channel` | 106 passed |
| `tests/pipeline` | 94 passed |
| `tests/packaging` | 52 passed |
| `verification/P09-AC3-DELETE-1/verify_all.py` | exit 0，`Orphan scan: managed=0 derived=0` |
| `cargo test --bin m2rc1-desktop permanently_delete_error_phase` | 1 passed |
| `npx tsc --noEmit` / `npx vitest run` | exit 0 / 327 passed |
| `check.ps1` | PASS |

> 注：上述目录在**同一进程**内一起运行会触发一个既有的收集期错误（与本次改动无关），故**逐目录分别运行**取信。

**返修后的 head**：`0add9072b`。**F-001 未裁决前不得作为最终 `delivery_head` 固定**；`delivery_head` 仍保持 R1 所审查的 `4824ed5d4`，直到裁决完成并送第二轮复审。
