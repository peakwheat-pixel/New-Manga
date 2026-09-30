# GOAL「检测器家族遗留清算」释放证据（release @095e314d，2026-10-01）

## 授权

用户 2026-10-01「全自动自治执行模式」指令（完整执行授权：自我规划/推进/执行/验证/总结；默认授权原则覆盖项目内常规开发/测试/文档/Git 工作流）。编排会话（代行 Codex）自主设定 Goal=「检测器家族遗留技术债清算」（见 [GOAL.md](../../GOAL.md)）。

## 释放内容（三 Task 同一 base=095e314d）

| Task | 来源依据 | 角色 |
|---|---|---|
| M2-PROD-DETECT-3（T1） | M2-PROD-DETECT-2 AC5 PARTIAL 的 NOT_RUN 子项登记 slice | Owner=ZCode / Reviewer=DSH / Integrator=代行 Codex |
| M2-MANGA-WEIGHTS-SOP（T2） | M2-PROD-DETECT-1 DSH r1 R6 / 遗留 slice② | 同上 |
| M2-FIX-REGISTRY-READINESS-ENV（T3） | DETECT-1 起登记既有环境性失败 / 遗留 slice③ | 同上 |

## 关键侦察事实（T1）

- core_service JSON-lines 协议 `new-manga.core` 1.0（PROTOCOL_MAJOR=1/MINOR=0，core_service.py:40-42）；命令分发 if-chain 三命令（ping/ListBooks/shutdown）+ Unknown typed 错误。
- acceptance_bridge 的 run_pipeline **从 ocr 起步**（L285-288 显式回避 detect=旧 LOCK_CHANGED 流程）且 mock_local_providers 装配——frozen 真实 detect 在既有面下不可达，T1 范围成立。
- detector 装配进 provider_runtime registry（core_assembly.py 装配段），CoreServices 无独立 detector 字段——core.detect handler 经 provider runtime 解析（与 pipeline detect step 同源）。
- 协议扩展先例：M2-FIX-LISTBOOKS 契约 rev 1.2 §5 widening；新增命令=minor bump。

## 代理裁决登记（用户可撤销）

- T1 裁决①：协议 1.0→1.1 minor bump（向后兼容 widening）；裁决②：core.detect payload=base64 页图像+宽高、响应=candidates 直通+elapsed；裁决③：handler 经 provider runtime（不绕过装配）；裁决④：发布形态验证口径=新 NSIS 安装后 frozen 进程 core.detect 真实推理 → DETECT-2 AC5 NOT_RUN 转 RUN（原 Task 历史不改写，集成注记）；裁决⑤：core.detect 为验证与工具面，apps/**（Tauri 命令注册）不扩——产品 UI 仍走 pipeline。
- T2 裁决：脚本 stdlib-only+代理尊重；pin 副本与代码 pin 不一致时脚本 fail；幂等。
- T3 裁决：环境条件化或断言语义改写二选一（Owner 读语境后定，登记理由）；目标=三套件无 failed。

## 执行模式

T1 与 T2+T3 并行派发（独立子 agent/独立 worktree）；DSH 非作者 Review 各自进行；熔断处置按 DETECT-2 先例。
