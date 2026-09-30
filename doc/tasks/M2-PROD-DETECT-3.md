---
id: M2-PROD-DETECT-3
title: "core.detect 命令面扩展 + frozen 进程内真实 detect 端到端验证（M2-PROD-DETECT-2 AC5 PARTIAL 闭合；Goal T1，自治执行 2026-10-01）"
kind: feature
status: ready
approval: user_autonomous_mode_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30、自治授权 2026-10-01）
depends_on: [M2-PROD-DETECT-2]
base_commit: 095e314dad490781ec5d8c1b5b88d53ae0b5d39c
branch: agent/zcode/M2-PROD-DETECT-3
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-3-zcode
---

# M2-PROD-DETECT-3：core.detect 命令面扩展 + frozen detect 端到端验证

## 来源与目标

- 来源：M2-PROD-DETECT-2 AC5=PARTIAL 的 NOT_RUN 子项（frozen 进程内 ML import/detect——frozen 命令面 core.ping/ListBooks/core.shutdown 无 detect RPC，结构性不可达）。登记的后续 slice 由本轮 Goal（GOAL.md T1）释放。
- 目标：core_service 新增 **`core.detect`** 命令（真实 ML 推理的 IPC 面），重新构建发布包，在安装后环境对 frozen 进程直接发 `core.detect` 完成真实推理——把「发布形态 detect 端到端可用」从不可达变为已验证。

## 设计决策（代理裁决，用户可撤销）

1. **协议扩展=minor bump（1.0→1.1）**：新增命令属向后兼容 widening（M2-FIX-LISTBOOKS 契约 rev 1.2 §5 先例）；既有三命令行为零变化；`core.ping` 的 version 字段自然携带新 minor。
2. **core.detect 请求/响应**：请求 payload=`{"page": "<base64 PNG/JPEG bytes>", "width": <int>, "height": <int>}`（字节计数与解码后尺寸由 provider 的 `_validate_request` fail-closed 校验，匿名 label/coordinate space 与 ports.detection 一致）；响应 result=`{"candidates": [{"provider_label","polygon","coordinate_space"}...], "elapsed_ms": <int>}`（provider 原始输出直通，不发明业务 ID）；错误走既有 error envelope（typed：PROVIDER_NOT_CONFIGURED/PROVIDER_FAILED/PROVIDER_DEPENDENCY_MISSING/E_INVALID_REQUEST）。
3. **实现路径**：core_service 的 `assemble_production_core` 产物中 detector 在 provider_runtime registry——命令 handler 经 provider runtime 解析 detect provider（与 pipeline detect step 同源），**不绕过装配**；mock_local_providers 模式下 core.detect 返回 mock provider 输出（装配语义一致）。
4. **发布形态验证口径（AC5 闭合）**：新 NSIS 安装后，探针直接 spawn core_service.exe 发 `core.detect`（合成漫画页）→ 断言 EXIT=0、candidates>0、provider 内部 pin 校验通过 → **M2-PROD-DETECT-2 AC5 的 NOT_RUN 子项转为 RUN**，其 Task 的 PARTIAL 判定由集成方在本 Task 集成时加注升级注记（原 Task 历史不改写）。

## Acceptance Criteria

- [ ] AC1（协议与命令）：`PROTOCOL_MINOR` 1→1.1（常量+docstring Allowed commands 列表）；`core.detect` handler（base64 解码 fail-closed/字节计数校验/provider 解析/typed error envelope/elapsed 计时）；既有三命令与 Unknown command 行为零变化。
- [ ] AC2（单元测试）：core_detect 命令 handler 测试（mock provider：正常输出直通/空页零候选/typed NOT_CONFIGURED/坏 base64/尺寸不符/超大载荷拒绝）+ 既有命令回归。
- [ ] AC3（重建与 GATE）：新 onedir+NSIS 构建；GATE 25/25；M2-AC5 raw 还原（既有先例）。
- [ ] AC4（frozen 端到端探针）：安装后环境 core_service.exe 发 core.detect 真实推理（manga 权重包内）PASS + core.detect 在无权重安装（-SkipWeights 产物或移权重）typed NOT_CONFIGURED PASS + doctr backend 切回语义探针。
- [ ] AC5（回归与纪律）：pytest 三套件基数（401+1 既有失败+新增）；cargo/vitest 留痕；diff --check EXIT=0；禁改面空。
- [ ] AC6（交付）：Task/Handoff/verification 证据回填。

## 允许修改范围

- `src/bootstrap/core_service.py`（PROTOCOL_MINOR+docstring+core.detect handler）
- `src/bootstrap/core_assembly.py`（如 handler 需要 detect provider 解析 helper，仅最小新增）
- `tests/**`（core_detect 测试）
- `packaging/m2ac5/**`（如需最小适配——预期不需要）
- `doc/tasks/M2-PROD-DETECT-3.md`、`doc/handoffs/M2-PROD-DETECT-3-*.md`、`verification/M2-PROD-DETECT-3/**`
- M2-PROD-DETECT-2 AC5 注记由集成方在集成 commit 处理（Owner 不改旧 Task）

## 禁止范围

- `src/infrastructure/providers/**` 两 provider 行为、`src/ports/**` 契约、`requirements.txt`
- acceptance_bridge（其面是 M2-AC1 冻结，本 Task 不触碰）
- `apps/**`、tauri.conf.json、run_clean_start_e2e.py（GATE 口径）
- 权重/模型入库、下载器实现

## 依赖、风险与阻塞

- 依赖：M2-PROD-DETECT-2 `done` @`9e44fb21`（包内运行时+权重就绪）。
- 风险：①frozen 进程内 transformers 懒加载首次触发（探针 L3 闭包外已证，进程内冷启动 6-17s 量级——探针设足够超时）；②base64 大载荷（一页 PNG 数 MB——handler 设合理上限如 32MB 拒绝）；③core.detect 暴露真实推理给 IPC 面（产品安全面——当前 sidecar 只接受本地宿主 spawn，stdio 协议无网络面，风险可接受并登记）。
- 阻塞：无。

## 遗留与边界

- core.detect 仅为验证与工具面；产品 UI 的 detect 走 pipeline（Tauri host 不新增命令注册——apps/** 禁改）。
- T2（weights SOP）/T3（registry 断言）由并行 Task 处理，非本 Task 范围。
