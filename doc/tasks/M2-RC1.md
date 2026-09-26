---
id: M2-RC1
title: Contract-Aligned Large-Media Resource Channel Runtime
kind: implementation
status: in_review
release_state: LARGE_MEDIA_RESOURCE_CHANNEL_RUNTIME_RELEASED
approval: approved_by_user_2026-09-27
execution_approval: approved_by_user_2026-09-27_explicit_task_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [M2-C1, M2-S1, M2-S2, M2-C2, M2-S3]
base_commit: 2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1
branch: agent/zcode/M2-RC1-large-media-resource-channel-runtime
worktree: G:/CODEX/New Manga.worktrees/M2-RC1-zcode
integration_commit: null
---

# M2-RC1 — Contract-Aligned Large-Media Resource Channel Runtime

## 来源与目标

来源：AD-001 的 React + TypeScript / Tauri / Python Core 边界；[M2-C1 Typed IPC Contract 1.1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §10（固定 Contract blob `fc35913801297ee1876ea395f9c5041a16226f20`）；M2-S1 T1–T7 阈值与 S1-B2/B3/B5/B6/B8/B11/B12 遗留项；M2-S2 的句柄校验与 Core 映射 ID 原型；[M2-S3 的 S1-B1 真实 Tauri/WebView2 探针](../research/M2-S3_TAURI_ASSET_PROTOCOL_PROBE.md) 及集成证据。

目标：实现一个受 Contract 1.1 约束的大媒体资源通道最小垂直切片：Python Core 授权资源引用与生命周期，Tauri/Rust 通过 `m2res` 自定义 protocol 解析不透明映射 ID 并有界提供字节，React/WebView 只取得形如 `http://m2res.localhost/m2id/<opaque-id>` 的 URL。S3 已验证的是有界探针，不是产品实现；本 Task 现在授权 runtime 实现，但不授权打包发布或超出证据范围的产品级安全声明。

精确的 Core↔host 内部 control DTO 与进程桥接由 Owner 在本 Task 范围内定义并留档；必须保持资源字节在普通 JSON/Base64 IPC 之外。此内部实现 seam 不修改共享 Contract。WebView 可见对象只包含受限 protocol URL，不得包含 OS 路径、资源标识、revision fingerprint、摘要或 scope root。

## Acceptance Criteria

- [x] **RC1-AC1 固定基线与范围**：Owner worktree 从 base `2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1` 创建；记录 toplevel、common-dir、branch、status、HEAD、工具版本与 Contract blob。实现 diff 限于下列允许路径，所有新目录在证据中标明为拟议目标路径。
- [x] **RC1-AC2 端到端字节通道**：真实 Tauri 2 / Windows WebView2 / React 消费者以 Core 授权的合成 `derived-cache` 资源成功加载并校验字节摘要；WebView 仅收到 `m2res` protocol URL 和必要的呈现响应，不触碰文件系统或 OS 路径。资源字节不得进入普通 JSON、Base64、事件、日志或错误对象；超限、无效与未授权请求不得部分交付。
- [x] **RC1-AC3 生命周期与恢复**：引用绑定 resource ID + revision fingerprint；默认 300 s sliding TTL，revision 切换、删除与 pin release 立即撤销；已开始的读取不被强制中断。定义并验证 Core 重启后的旧引用行为，确保旧 ID 不会被重新绑定；React remount/reconnect 从 Core 快照重取状态并重新签发引用，不复用失效 URL。
- [x] **RC1-AC4 安全解析**：从同一已打开句柄校验 containment、文件身份、issue-time size 与 T1 上限；仅通过该句柄读取，校验 issue-time content digest 并在读取后复核身份。以合成 fixture 覆盖 malformed/unknown/revoked/expired ID、范围逃逸、reparse/junction、句柄后同尺寸改写、摘要不匹配、共享冲突、超大资源和只读约束；返回 Contract 1.1 §10.2 对应稳定 typed error 且不泄漏路径或映射表。`user-source` scope 不得获得前端可见实现。
- [x] **RC1-AC5 容量与性能**：验证单资源最多 256 MiB、至少 32 个活跃引用、每资源至少 16 个并发订阅者；超限返回 typed throttle/size error。记录缓冲区与 Core 额外内存测量，遵守流式 resident buffer ≤32 MiB 与每资源 Core 额外峰值 ≤资源字节数 +64 MiB，不物化完整资源。记录 ≤25 MiB 页面热缓存 first-byte-to-host P95（目标 ≤200 ms）；尝试按 S1-B6 进行冷缓存测量，无法安全清缓存时逐项记 `NOT_RUN`，不得声称达到 1 s 冷缓存目标。
- [x] **RC1-AC6 安全与发布边界**：逐项记录 S1-B3（同用户 ACL/完整性级别）、S1-B5（进程重启/密钥生命周期）、S1-B6（冷缓存）、S1-B8（目标打包/沙箱）的执行状态。未实测项保持 `UNVERIFIED`/`NOT_RUN` 并列明解锁条件；在 S1-B3 与 S1-B8 关闭前，不得宣称产品级安全或打包就绪。模型权重通道、数据 Schema 与正式发布均不属于本 Task。
- [x] **RC1-AC7 独立交付**：提供测试原始日志、合成 fixture 哈希、逐项 AC 结果、Handoff 与固定 delivery head；DeepSeek Harness 对该精确 head 独立 Review；Codex 集成前后核对范围、禁改路径与 diff-check。Review 和集成前不得把 Task 改为 `done`。

## 允许修改范围

- `apps/desktop/**`：拟议的新 React/TypeScript + Tauri 2 应用；仅本资源通道垂直切片及其 scoped manifests/locks/tests。
- `src/application/resource_channel/**`：拟议的 Python Core 引用签发、撤销与 revision 生命周期用例。
- `src/infrastructure/resource_channel/**`：拟议的句柄解析与受限资源读取 adapter。
- `tests/m2_resource_channel/**`：本 Task 的 Core 与资源解析测试。
- `doc/tasks/M2-RC1.md`、`doc/handoffs/M2-RC1-*.md`、`verification/M2-RC1/**`。
- `doc/reviews/M2-RC1-<reviewed-head>.md`：仅由非作者 DeepSeek Harness 编写。
- `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`：Codex 仅回填状态、Task 导航与证据链接。

## 禁止范围

不得修改 `doc/contracts/**`（本 Task 必须符合固定 Contract 1.1 blob；M2-C2 的 F-01..F-04 仍 deferred，只有未来独立 Contract 修订获授权时才能处置）、`src/ui/**`、`src/bootstrap/app.py`、非 resource-channel 的 `src/domain/**` / `src/application/**` / `src/ports/**` / `src/infrastructure/**`、现有 PySide6/QML 产品路径、`packaging/**`、SQLite schema/migrations、根目录依赖/锁文件、M2-S1/S2/C2/S3 的原报告/Task/Review/证据、AD-001、协作协议、用户漫画/源文件、真实凭据或模型权重。不得把 S3 探针结论扩大为打包或产品安全保证。任何超出 allowed paths 的变化先停下并向 Codex 提出范围变更。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| RC1-AC1 基线/范围 | `git rev-parse` 五件套 + Contract blob 核对 + `git diff --name-status <base>..<delivery>` | ZCode linked worktree；Windows | executed 2026-09-27：全项一致；30 文件全授权路径 | `verification/M2-RC1/baseline-selfcheck.md`、`final-verification.log` |
| RC1-AC2/3 WebView 与生命周期 | `cargo test --locked`（9 passed，exit 0）；`npm test -- --run`（8 passed，exit 0）；真实 Tauri/WebView2 端到端矩阵 `run_e2e.py`（10/10 PASS，exit 0，两次运行逐项一致） | Windows + WebView2 153.0.4234.48；合成 derived-cache fixture | executed：端到端 issue→分块 fetch→字节校验、撤销/过期/未知 ID 类型化拒绝、remount 新引用、TTL 续期语义修复后实测 | `raw/e2e-results-first.json`、`raw/e2e-results-repeat.json`、`final-verification.log` |
| RC1-AC4 Python Core/句柄安全 | `python -m pytest tests/m2_resource_channel -q`（35 passed，exit 0） | ZCode Core 环境；合成 fixture | executed：junction 逃逸、等大小读中改写（预持写句柄、digest 拦截）、共享冲突 fail-closed、身份/大小/摘要全链 | `tests/m2_resource_channel/**`（pytest 输出在 `final-verification.log`） |
| RC1-AC5 阈值/性能 | 256 MiB 边界 pytest + 端到端 E-08 分块流式 + E-07 热缓存 P95 | Windows；合成 fixture | executed：256 MiB 边界 PASS、越界 RESOURCE_TOO_LARGE PASS、热缓存 P95≈1 ms（≤200 ms 预算）；**冷缓存 S1-B6 NOT_RUN**（无安全清缓存方法） | `final-verification.log`、报告 NOT_RUN 清单 |
| RC1-AC6 B3/B5/B6/B8 | 逐项执行或记录 BLOCKED/NOT_RUN | Windows | executed（记录）：S1-B3/S1-B8 NOT_RUN（解锁条件列明）；S1-B5 部分（重启旧 ID 不重绑已测、密钥生命周期未做）；S1-B6 NOT_RUN；**未宣称产品级安全或打包就绪** | Handoff 与 Task 运行记录 |
| RC1-AC7 集成前检查 | `git diff --check <base> <delivery>`；禁改路径过滤；release build + 前端 production build | 固定 delivery head | executed：--check 干净；禁改路径零触碰；cargo build --release 与 npm run build 均成功 | `verification/M2-RC1/final-verification.log` |

## 依赖、风险与阻塞

硬依赖均已 `done`：M2-C1、M2-S1、M2-S2、M2-C2、M2-S3。固定 Contract blob=`fc35913801297ee1876ea395f9c5041a16226f20`。M2-S3 对 `m2res` 自定义 protocol 的 PASS 仅覆盖单宿主、模拟映射表、一次性 body、未打包探针；本 Task 必须重新验证真实 Core/Rust 运行链。S1-B3/S1-B8 是任何产品级安全声明的前置条件；S1-B6 未测前冷缓存 1 s 仅为目标。M2-C2 的 4×P3 维持 deferred，因为本 Task 禁止修改共享 Contract。

## 交付与运行记录

- Release：Codex，2026-09-27；证据：[release-2dca20cd.md](../../verification/M2-RC1/release-2dca20cd.md)（在治理 commit `fb87414a`/主线，本分支经 `git show` 只读，不携带）。
- 2026-09-27（Owner ZCode，实现交付）：三栈垂直切片完成——①Python Core：`src/application/resource_channel/`（ResourceChannelService：256-bit 不透明 ID、300 s 滑动 TTL、revision 切换/删除/pin release 立即撤销、32 引用/16 订阅者类型化限流、256 MiB T1 上限、user-source 签发拒绝、重启旧 ID 不重绑）+ `src/infrastructure/resource_channel/`（HandleVerifiedFileReader：pre-open reparse walk + open-once 窄/宽共享双模式 + 句柄 containment/identity/size/digest + 读后身份复核 + 有界分块流式；ScopeRoots；stdio JSON-lines host_bridge）+ `tests/m2_resource_channel/`（35 passed）。②Tauri/Rust：`apps/desktop/src-tauri/`（m2res 协议：ID 格式门→grant 缓存→open-then-verify→首验全量 digest 流→16 MiB 分块→读后复核；no-store+CORS；stdio Core sidecar 桥+catalog；9 cargo tests 含真 sidecar 集成）。③React/TS：`apps/desktop/frontend/`（ResourceChannelClient 仅见不透明 URL+size；分块 fetchAll；typed 错误映射；探针矩阵；8 vitest tests）。④端到端：真实 Python Core↔Tauri↔WebView2 三栈矩阵 10/10 PASS（exit 0，两次运行一致）——E-01 issue+分块 fetch+digest 自证、E-02 渲染、E-03/04/05 unknown/revoked/expired 类型化拒绝、E-06 remount 新引用、E-07 热缓存 P95≈1 ms、E-08 256 MiB 分块、E-09 超限拒绝。bring-up 缺陷如实记录于 `verification/M2-RC1/run-log.md`。NOT_RUN：S1-B3/B6/B8、冷缓存、模型权重、产品级安全声明全部保留。Gate：Owner 实现完成，交非作者 Reviewer（DeepSeek Harness）。
- 2026-09-27（Owner ZCode，开工）：RC1-AC1 基线自检 PASS（toplevel/git-dir/common-dir/HEAD=2dca20cd/分支/干净工作区/Contract blob=`fc359138…`=Task 固定 blob），证据 `verification/M2-RC1/baseline-selfcheck.md`。事实记录：base `2dca20cd` 不含释放 commit `fb87414a`（其父即本 base）；Owner 按指令仅以 `git checkout fb87414a -- doc/tasks/M2-RC1.md` 取入本 Task 文件，不合并释放 commit。无 BLOCKED。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无；本次只登记与释放 Task，未运行产品测试。
- 最终由 Codex 在独立 Review 与集成后验证均通过后填写 `integration_commit` 并改为 `done`。
