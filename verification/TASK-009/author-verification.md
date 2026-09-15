---
task_id: TASK-009
author: ZCode
base_commit: 3de750ab7558f4c90841b96005dbbe58b8064e71
delivery_head: f1dd6022e756ab733c5b6eb20c625b6ce340ba27
environment: Windows 10.0.26200 x64 / Python 3.12.3（G:/CODEX/New Manga.task-envs/TASK-005-py312）/ Git 2.52.0 / OpenSSL 3.5.4（Git Bash mingw64）
---

# TASK-009 作者验证记录

固定任务环境执行；全部本地可控端点（127.0.0.1），未访问任何真实/付费 API，未触碰用户漫画库与共享 app.db。临时 SQLite/证书/日志均位于 pytest `tmp_path`。

## 命令与结果

| # | 命令 | 结果 | 退出码 |
|---|---|---|---|
| 1 | `PYTHONPATH=src python -m pytest tests/network -q` | 81 passed | 0 |
| 2 | `PYTHONPATH=src python -m pytest tests/storage tests/library tests/editing -q` | 91 passed | 0 |
| 3 | `PYTHONPATH=src python -m pytest tests -q`（全量，含 tests/core 6） | 178 passed | 0 |
| 4 | `git diff --check 3de750a f1dd602 --` | 无输出 | 0 |
| 4b | `git diff --check 57896ef f1dd602 --`（纯实现范围） | 无输出 | 0 |

注：`3de750a..f1dd602` 的 diff 含 Codex release commit `57896ef` 对 `doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`、`doc/tasks/TASK-009.md` 的 4 处状态修改（认领前已存在，非本作者变更）；实现本体为 `57896ef..f1dd602`，全部位于 Task 白名单（`src/application/settings/**`、`src/infrastructure/{credentials,network,transport}/**`、`src/ports/{network,providers}/**`、`tests/network/**`、`doc/tasks/TASK-009.md`）。

## 覆盖的主责 AC 与证据文件

| AC | 证据（tests/network/） | 说明 |
|---|---|---|
| AC-SET-001 | test_settings_resolution.py（8） | task>chapter>book>global 解析 + 来源标签 |
| AC-OCR-003 / AC-PROVIDER-001/002 | test_provider_bindings.py（7） | 能力×作用域绑定、优先级、无绑定即报错不猜测 |
| AC-PROVIDER-003/004 | test_settings_snapshot.py（4） | 快照冻结于后续全局修改；恢复报 missing/disabled 要求重绑 |
| AC-PRIVACY | test_privacy_notices.py（5） | Local/Remote 区分 + 按能力列出上传数据类型 |
| AC-SEC-001/002 | test_secret_hygiene.py（3） | v2 SQLite 字节 + 捕获日志扫描无 Secret；模型字段无明文承载 |
| AC-SEC-003 | test_credential_stores.py（8，参数化） | 契约测试对 InMemory 与真实 Windows Credential Manager（ctypes advapi32）双重执行，测试项用后即删 |
| AC-SEC-004/005 | test_network_policy.py（7）+ test_transport_tls.py（5） | 新 Profile 默认 verify_tls=True；关闭需显式确认；真实 TLS 握手验证信任/不信任/显式关闭三态 |
| AC-NET-001 | test_route_resolution.py（9） | direct/system/http/https/socks5 + bypass + inherit_system |
| AC-NET-002/003 | test_transport_local.py（12） | 代理失败默认硬失败且不触碰目标；显式开关才一次 Direct 重试 + FallbackEvent 可见 |
| AC-NET-004 | test_connection_tester.py（7） | DNS/TCP/TLS/HTTP/Provider-Auth 分阶段、类型化错误码、失败截断后续 SKIPPED |
| D06 §55/§56 | test_transport_local.py + test_retry_classification.py（4） | fallback 可见性；瞬态可重试/配置与鉴权快速失败的分类 |

本地端点基建（tests/network/servers.py）：受控 HTTP 目标（可注入状态码）、HTTP 代理（绝对形式/CONNECT 拼接/407/502/静默）、SOCKS5 mini 服务器（RFC 1928/1929 user-pass）、openssl 自签 TLS 目标。

## NOT_RUN / N/A

| 项 | 状态 | 原因 |
|---|---|---|
| 真实远程 Provider（OpenAI 等）端到端 | NOT_RUN | Task 测试要求明确不依赖真实付费 API；以本地可控端点覆盖代理/鉴权/超时/429 分类 |
| Provider adapter 本体（模型调用） | N/A | TASK-019；本 Task 只到 Transport/分类边界 |
| UI（设置页/诊断面板渲染） | N/A | TASK-022；本 Task 交付可渲染的数据结构（EffectiveSetting.source_label、ProviderDataNotice、ConnectionTestReport、FallbackEvent） |
| Profile/Binding/NetworkProfile 的 SQLite 持久化 | NOT_RUN | 白名单未含 src/infrastructure/sqlite/**；契约以 Store Protocol + InMemory 实现交付，SQLite adapter 需 Codex 另行协调切片（TASK-029 拥有 DB 层） |
| 多进程并发写 Credential Manager | NOT_RUN | 单实例桌面模型（D07 §79）；Windows 适配器对 CredWrite 已做存在性预检 |
| settings.json 等导出文件 Secret 扫描 | N/A | 本 Task 未实现任何导出；SQLite/日志扫描已覆盖现有落盘物 |
| PyInstaller 打包下的 ctypes/SSL 行为 | NOT_RUN | TASK-004 实验已验证打包路线；打包回归属后续发布 Task |

---

## 修订轮验证（R-001～R-010 修复，`b42fc32`）

DSH Review `2da1a39` changes_requested 后的修订轮（[Handoff TASK-009-b42fc32](../../doc/handoffs/TASK-009-b42fc32.md)）：

| # | 命令 | 结果 | 退出码 |
|---|---|---|---|
| 1 | `PYTHONPATH=src python -m pytest tests/network -q` | 97 passed（81 + 16 新回归，tests/network/test_review_revision.py 按 R-001～R-010 逐项命名） | 0 |
| 2 | `PYTHONPATH=src python -m pytest tests/storage tests/library tests/editing -q` | 91 passed | 0 |
| 3 | `PYTHONPATH=src python -m pytest tests -q` | 194 passed | 0 |
| 4 | `git diff --check 3de750a b42fc32 --` | 无输出 | 0 |

修订变更范围：`git diff --name-only 150c789 b42fc32` = 11 文件（8 源 + 3 测试），全部在 TASK-009 白名单。R-011（httpx 选型偏差）deferred 交 Codex 裁决；R-012 随元数据提交修正。NOT_RUN/N/A 维持上表，未被改写。
