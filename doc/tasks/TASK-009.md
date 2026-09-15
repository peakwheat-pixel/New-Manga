---
id: TASK-009
title: 实现 Provider 配置、网络策略与凭据边界
kind: implementation
status: in_review
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-006]
base_commit: 3de750ab7558f4c90841b96005dbbe58b8064e71
branch: agent/zcode/TASK-009-provider-network-credentials
worktree: G:/CODEX/New Manga.worktrees/TASK-009-zcode
integration_commit: null
---

# TASK-009：实现 Provider 配置、网络策略与凭据边界

本 Task 已按现有任务序列释放，状态为 `ready`，等待 ZCode 接管实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §25～28；D06 §49～57；D07 §63～72/87～89；D08 AC-PROVIDER/NET/SEC/SET/PRIVACY。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OCR-003、AC-PROVIDER-001、AC-PROVIDER-002、AC-PROVIDER-003、AC-PROVIDER-004、AC-NET-001、AC-NET-002、AC-NET-003、AC-NET-004、AC-SEC-001、AC-SEC-002、AC-SEC-003、AC-SEC-004、AC-SEC-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 支持多个Provider/Network Profile、按能力和任务/章节/作品/全局解析，记录有效设置来源和用于Run的快照。（`ProviderBindingResolver` 任务>章节>作品>全局 + `UnresolvedCapabilityError` 不猜测；`EffectiveSetting`/`BindingResolution` 来源标签；`build_snapshot` 冻结 + `validate_snapshot` 报 missing/disabled 要求重绑。tests/network 19 项）
- [x] 统一Direct/System/HTTP/HTTPS/SOCKS5/bypass/override策略；代理失败默认禁止直连，显式fallback可追踪。（`StdlibTransport.resolve_route` 统一路由 + `ProviderNetworkResolver` proxy_policy；代理失败类型化硬失败且不触碰目标；显式开关才一次 Direct 重试 + `FallbackEvent`。tests/network 21 项）
- [x] Secret只进入受保护Credential Store，SQLite/日志/普通导出无明文；TLS默认开启；分阶段连接诊断与本地/远程数据提示。（`SecretValue` 全程脱敏 + Windows Credential Manager ctypes 适配器（真实 vault 参数化测试）+ SQLite/日志防泄漏扫描；`verify_tls=True` 默认与关闭确认门控；`ConnectionTester` 五阶段类型化错误码；`describe_provider_data` Local/Remote 提示。tests/network 41 项）
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。2026-09-15 ready 核对确认：当前仓库尚无上述 settings/network/transport/credentials/providers 与 tests/network 目录，因此它们仅作为本 Task 可新增的明确边界；不能自行扩展到整个 src/tests。

- src/application/settings/**
- src/infrastructure/network/**
- src/infrastructure/transport/**
- src/infrastructure/credentials/**
- src/ports/network/**
- src/ports/providers/**
- tests/network/**
- doc/tasks/TASK-009.md
- doc/handoffs/TASK-009-*.md
- verification/TASK-009/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/network；本地可控端点验证代理/bypass/鉴权/超时/429/fallback，不依赖真实付费API。
- 扫描临时数据库与测试日志无测试Secret；Profile修改不改变既有快照。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

实际结果（delivery_head=`f1dd602`，固定 Python 3.12.3 任务环境，全部退出码 0）：

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 本 Task 测试 | `PYTHONPATH=src python -m pytest tests/network -q` | 81 passed | [author-verification](../../verification/TASK-009/author-verification.md) |
| 既有切片回归 | `PYTHONPATH=src python -m pytest tests/storage tests/library tests/editing -q` | 91 passed | 同上 |
| 全量回归 | `PYTHONPATH=src python -m pytest tests -q` | 178 passed | 同上 |
| whitespace / 范围 | `git diff --check 3de750a f1dd602 --`；name-only 过滤 | PASS（0；实现范围 37 文件全在白名单） | 同上 + [Handoff](../handoffs/TASK-009-f1dd602.md) |

本地可控端点（127.0.0.1）：受控 HTTP 目标（可注入状态码）、HTTP 代理（绝对形式/CONNECT/407/502/静默）、SOCKS5 mini 服务器（user-pass）、openssl 自签 TLS 目标；未访问真实付费 API。未执行项（真实远程 Provider 端到端、Provider adapter 本体、UI、Profile 的 SQLite 持久化、并发 vault 写、打包回归）如实记录 NOT_RUN/N/A，见 author-verification。

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)。依赖必须已经集成 done 才可开始。

UI由TASK-022接入；具体OCR/Translation模型适配在TASK-019。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-009-f1dd602](../handoffs/TASK-009-f1dd602.md)，固定 `base_commit=3de750a`、`delivery_head=f1dd602`，status=in_review。
- Review：尚无（等待 DeepSeek Harness 独立 Review）。
- 实际执行/实验/测试：[author-verification](../../verification/TASK-009/author-verification.md)（四条命令全过：network 81 / 回归 91 / 全量 178 / diff --check 0）。
- 最近状态：2026-09-15 实现完成，状态 in_progress → in_review。AC1～AC3 已勾；AC4 待非作者 Review approved 与 Codex 集成后勾选。
- 认领记录：2026-09-15 ZCode 在指定 worktree 接管开始执行，状态 ready → in_progress。基线核验通过：HEAD=`57896ef`（release commit）、base=`3de750a` 为祖先，分支/worktree 如派单，common dir=`G:/CODEX/New Manga/.git`，工作区干净。白名单核对：settings/network/transport/credentials/ports 与 tests/network 目录当前均不存在，属本 Task 拟议新增边界。
