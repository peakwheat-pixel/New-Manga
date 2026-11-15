---
task: BLOCKED-ITEM-AUDIT-1 / CRASHPOINT-FAIL-NATURE-1 / L-L1-2-CONSTRAINT-VERIFY-1
reviewer: zcode (subagent agent-8, independent context, read-only)
reviewed_head: ffeaaa4f9
verdict: REJECT
date: 2026-11-15
---

# 三份交付独立复核（ZCode）—— **REJECT**

| 交付 | 判定 |
|---|---|
| `CRASHPOINT-FAIL-NATURE-1` | **ACCEPT** |
| `BLOCKED-ITEM-AUDIT-1` | **REJECT** —— 中心主张被证伪 |
| `L-L1-2-CONSTRAINT-VERIFY-1` | **ACCEPT_WITH_LIMITATIONS** |

整体取最严：**REJECT**。

## ★ 交付 2 被证伪：我找到了"第三个"

**DSH 声称「没有第三个被误判为需人、实际可做的项」。这是错的。**

**`yolo11s-seg.onnx` 一直在仓库里**：

```
apps/desktop/src-tauri/target/{debug,release}/resources/core-sidecar/models/detector/yolo11s-seg.onnx
```

- 各 **40,824,255 B**（2026-10-05）
- SHA-256 = `944e8114…acd418d`，与 `src/infrastructure/providers/detection_sfx.py:131` 的
  `SFX_WEIGHTS_SHA256` **逐位一致**（该 pin 本就是 fail-closed 校验，字节一致即可信）
- **DSH 的"全盘搜索过、工作区不存在"是事实性错误** —— 推测它搜的是 **Git 索引**，
  而 `target/` **被 gitignore**。

**⇒ 复制进新 sidecar 即可完成 GATE4-REMAINING-1 §2 的验证，无需用户提供任何东西。**

**这与 `L-F1-3` / `E-9` 同一模式（没看关键文件就下"做不到"结论），
且恰好出现在宣称"没有第三个"的那张卡里。**

## 交付 1 ACCEPT（两个小瑕疵）

- 测试断言与注释逐字核实属实（`:213-214/:271-272` 的前置断言、`:207` "never self-terminates"）；
- "不得新增 skip"纪律有真实出处（协作协议 §6 临时条款 3；`HANDOFF:124`）；
- 底层证据真实且**互相咬合**：`commit_digest` 一致（`46475b…`）、host_pid 不同（14064→29708）、
  `second_call=recovered`、`gate_open=true`；
- 第三种做法（Trait 过滤/独立 playlist）技术上存在但改"全量"语义且更隐蔽 ⇒ **保持 fail 更好**；
- **瑕疵**：README 引用的 `CRASH_POINT=PASS … EXIT=0` **汇总 stdout 未归档**，无法逐字复核
  （底层数据在，汇总行是转述）。

## 交付 3 ACCEPT_WITH_LIMITATIONS（结论对，一处引用错位）

- **① 成立且复核者给了更强的证据**：真实 wire 命令 `list_chapters`（`library.py:241-247`）
  `ORDER BY sort_order` **单一键** —— 比 DSH 引的 `:1200/:1228`（内部指针查询）**更直接**。
  C# 侧 `ShelfViewModel.cs:194` `OrderBy(SortOrder)` 是同键消费端重申，**未发现叠加异义排序**。
- **② 成立但引用错**：四个 C# 位置（275/639/223/116）全对；但 DSH 表格里
  "Core | `runtime.py:865` `sort_order=source_order`" 是**错位引用** ——
  那是**页面导入**的 source_order（`referenced/runtime.py:864`），**与章节 reorder 无关**。
  真实链路是 `service.py:209-225 reorder_chapters`（单事务）→ `update_chapters_atomic`（`library.py:266`）。
- **③ 成立**：两测试文件真实存在且有判别断言（`LastReorderIds`、原子性 5 个测试函数）；
  `c459b279f` 实测为 commit 且是 HEAD 祖先。

## 是否有"空转"内容

| 交付 | 空转痕迹 |
|---|---|
| 3 | **`runtime.py:865` 引用是未打开文件核对的转述** —— 作者没确认该行与 reorder 相关 |
| 1 | 汇总 stdout 是转述（有底层证据支撑，可接受） |
| **2** | **"全盘搜索"是不完整搜索支撑的核心结论 —— 最严重的一种** |

## 复核者自陈未完成

- 未实际执行"复制权重 → 跑检测路径验证"（属修复动作，超出只读复核）；
- crash 汇总 stdout 原文未在归档中定位，10 项 CHECK 无法逐字核对。

## DSH 的处理（2026-11-15，已按裁决执行）

1. **更正 `BLOCKED-ITEM-AUDIT-1`**：登记**第三个误判**，并改写方法论结论 ——
   "我声称逐项回到代码/实测核实，但这一项**只做了索引搜索**，没做文件系统搜索。
   **『搜索』的定义没想清，就等于没搜。**"
2. **已复制模型并三重验证**（SHA 与 pin 逐位一致 + 长度一致 + **onnxruntime 实测 `LOADED OK`**，
   输入 `[1,3,1024,1024]` 与 `SFX_DEFAULT_IMGSZ` 一致）——
   证据：`verification/GATE4-MODEL-RECOVERED-1/README.md`。
3. **STATUS 条件 4** 由"三项残留（模型/证书需用户，reader 需 F11）"
   改为"两项残留（证书需用户；`reader` 需 F11；模型已就位并验证可加载）"。
4. **交付 3 的引用错位**已知悉，待下一轮更正（本轮优先处理 REJECT）。
