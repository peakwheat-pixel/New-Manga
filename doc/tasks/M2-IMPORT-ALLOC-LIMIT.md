---
id: M2-IMPORT-ALLOC-LIMIT
title: "大图导入 QImageReader allocation limit 可配置化（建议 B：Qt 256MB 默认上限拒绝 webtoon 导入）"
kind: feature
status: done
# DSH r1 approved_with_conditions → 条件返修 R1-R10 全 closed（r2 approved：机制锁定用例+stderr 补档+MOBI 收紧；五套件 550+1sk 全绿）

approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2]
base_commit: 8e0de8d0 # Task 授权基线；分支实际 fork 自 release 8996ca55（a5c8adf1 的父提交即 8996ca55，dsh r1 R5）
branch: agent/zcode/M2-IMPORT-ALLOC-LIMIT
worktree: G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode
delivery_head: a5c8adf1
---

# M2-IMPORT-ALLOC-LIMIT：大图导入 allocation limit 修复

## 背景（M2-TA3-B2 F2）

TA3-B2 实证：K07（690×131289，≈345.6MiB 解码）K09/K10（≈264.5/265.0MiB）被 Qt `QImageReader` **内建默认 256MB allocation limit** 拒绝导入（`src/infrastructure/importing.py:45-59` 是唯一 QImageReader 使用点，无 allocation limit 设置点）；F1 五例 <256MiB 且 import OK——尺寸边界自洽。webtoon 长条漫是产品目标域，256MB 默认上限直接阻断。

## 交付（AC）

1. **AC1 修复**：导入路径显式设置 allocation limit——方案自选并留痕（如 `QImageReader.setAllocationLimit(N)`，Qt 6.5+ API；N 取安全值如 2047 或从 settings 读取，须论证选择的理由与内存上界风险）；同时评估 degraded/失败路径的 typed 错误信息改善（r1 R4：当前 per-file detail 为空串，应携带 reader 级错误原文）。
2. **AC2 测试**：先红后绿——现有 256MB 上限下超大尺寸图（伪造大尺寸头，不造真大文件）导入 FAIL 的测试；修复后同图导入 PASS（或 typed 可诊断）；setAllocationLimit 调用断言。
3. **AC3 真图验证**：K07 真实文件（`test_assets/comic_golden_suite/韩漫_KO/01_webtoon_..."` 路径见 TA3-B2 case-selection/qual-K07.json）经生产 import 通道跑通，尺寸/宽高登记。
4. **AC4 文档**：memory 上界选择论证（为何该值安全）、Task/Handoff 登记；F2 的「推断」口径可升级为一级证据（复跑 K09 原始错误归档，若顺带）。

## 允许修改面 / 禁改面

允许：`src/infrastructure/importing.py`、`tests/`（import 相关）、`experiments/M2-IMPORT-ALLOC-LIMIT/**`（真图验证脚本）、`verification/M2-IMPORT-ALLOC-LIMIT/**`、Task/Handoff。
禁改：`src/ports/**`、其他 infrastructure 文件、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`。

## 纪律

- fail-closed 语义不放宽（超上限仍 typed 失败，只是上限更合理+错误可诊断）；内存上界必须有论证（不能简单 setAllocationLimit(0) 无限放行，除非论证 Qt 内存管理可控并登记风险）。
- 基线不回退：main 509+1skipped 0 failed。

## 交付证据（owner 回填 2026-10-01，delivery_head=`a5c8adf1`，续接熔断半成品 8996ca55 并修正 2 处）

| AC | 结果 | 证据 |
|---|---|---|
| AC1 修复 | `QtImageDecoder.decode()` 每次 read 前显式断言 `QImageReader.setAllocationLimit(2047)`（`src/infrastructure/importing.py` 唯一 QImageReader 使用点，模块常量 `_ALLOCATION_LIMIT_MIB=2047` 带完整论证注释：非 0 防 OOM / 域实测 345.6MiB×~5.9 余量（外推 921MiB×~2.2，r1 R6 统一 MiB 口径）/ Qt int 内 / 分配前检查非预分配 / 进程全局幂等断言）；per-file 失败 detail 携带 reader.errorString() 原文（strip+截断 300 字符，r1 R4） | commit `a5c8adf1` src diff |
| AC2 测试 | 先红后绿：红态（基线 src + 新测试）**3 failed / 4 新增**（webtoon 长条 690×110000≈289.5MiB 导入被 256 默认上限拒；decoder 未调用 setAllocationLimit；5000 字符错误不截断——第 4 个 fail-closed 保护测试基线即绿，256 上限同样拒绝 2048MiB）；绿态 **4/4 passed**，四套件（production_adapters/providers/core/m2_acceptance）**517→521 passed, 1 skipped, 0 failed**；伪造大尺寸头不造真大文件（`make_thin_png` 手写 IHDR/IDAT，流式 zlib 批量压缩峰值 ~8MiB，超限测试用声明 2048MiB IHDR+单行 IDAT 利用 Qt 分配前拒绝） | commit `a5c8adf1` tests diff + handoff §3 |
| AC3 真图验证 | 生产通道（`ImportImagesUseCase`+`QtImageDecoder`+`ManagedCopyStoreAdapter`+内存 sink）：**K07 690×131289（盘上 57,012,442B，解码 ≈345.6MiB）导入 OK**、K09 690×100480、K10 690×100674 均 imported 零 failed，宽高/managed ref 全登记（r1 R4：domain `Page` 无 mime 字段，不登记 mime） | [verify-k07.json](../../verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json) + `experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py` |
| AC4 文档 | 上限论证落 importing.py 注释+handoff §2；**F2 口径升级为一级证据**：对照组（原始 QImageReader 读法、Qt 默认 256MiB）复跑 K07/K09/K10 三例全部拒绝，errorString=`'Unable to read image data'`（Qt limit 拒绝不进 errorString 细节）；stderr 分类日志 `QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes` **原文已按 case 归档进 JSON**（r1 R2，OS 级 fd2 捕获），对照组另含 @2047 同 reader 同字节正向臂（r1 R3） | handoff §4 + verify-k07.json `control_qt_default_256`（schema v2） |

半成品处置：续接前 owner（熔断 agent）在 8996ca55 上已写 importing.py 修复+测试方向，回填 owner 核实采纳，修正 2 处（①`LongErrorReader` fake 缺 `setAllocationLimit`，与新 decode 前置断言冲突→补齐；②`make_thin_png` 工厂内 `row*height` 一次性分配 ~2GB 与自身注释矛盾且 fail-closed 测试耗时 6.9s→流式压缩+`rows` 截断参数，<0.01s）。
