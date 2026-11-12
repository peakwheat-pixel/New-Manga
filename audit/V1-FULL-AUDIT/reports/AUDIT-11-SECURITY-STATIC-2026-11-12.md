# AUDIT-11：安全及异常恢复阶段报告

- 产品基线：`10e4ee013835605800d3830fb960ae8d3aa04167`
- 审计检查 HEAD：`beaa13406438fab46ef56fa5a8852bf04ce7133d`
- 专项结论：**FAIL（存在已实测的 managed-root 越界写；另有已实测 restore 磁盘故障恢复缺口）**
**范围：** 当前 Avalonia/C# Host + Python Core；只读静态检查和已固定的隔离 probes。没有修改产品文件、依赖、构建设置、策略或用户数据。

## 结论摘要

既有隔离 probe `test_managed_publish_follows_directory_junction` 通过真实 `ManagedFileStorage.publish` 将产品生成的 revision bytes 写到 managed root 之外的隔离目录，ZCode 已按 Medium severity / High confidence 分级；因此路径遍历/文件写入边界子项 FAIL。另一个隔离 probe 在模拟磁盘写失败时确认 restore 已将数据库恢复到备份点状态，随后文件写入抛出裸 `OSError`，错误不含 typed code/rollback id，而 pre_restore 包已创建；ZCode 将其分为 Medium / High confidence。nmbak 的 `../` restore probe 没有复现越界写，属于 defense-verified。

其余静态检查只覆盖所列入口和模式，不足以宣布整项安全通过。AUDIT-11 不包含远端 GitHub 可见性核验或补救；既有 `AUDIT-11-INC-001` 仍为 `INVESTIGATE`。真实 Core plugin sandbox 的文件/网络隔离、超时和进程树行为本轮仍无有效运行证据：smoke 7 项在 `icacls` 前置授权失败后未到达 hook 行为；不能把 fail-closed 检查或 Wire PASS 外推为隔离语义通过。

## 证据与执行

| 检查 | 结果 | 证据及边界 |
|---|---|---|
| 只读源代码模式盘点 | EXIT 0；扫描 `src/**`、`apps/desktop-avalonia/src/**` 的 638 个源码文件；Python AST 解析错误 0；候选模式仅供人工定位 | `tests/security_static_inventory.py`、`evidence/audit-11-static-inventory-20261112.json`、`logs/audit-11-static-inventory-20261112.log`。候选命中不是 finding；不读 `.env`、用户设置、图片/数据库内容或生成目录。 |
| 安全相关源码固定 | 23/23 个命名源文件在产品基线与审计 HEAD 间无 diff；每项记录 git blob 和 SHA-256，EXIT 0 | `evidence/audit-11-reviewed-source-manifest-20261112.json`、`logs/audit-11-source-manifest-20261112.log`。 |
| NuGet vulnerability check | `dotnet list apps/desktop-avalonia/NewManga.sln package --vulnerable --include-transitive --no-restore` EXIT 0；配置源报告 18 个项目未发现易受攻击包 | `logs/dependency-vulnerability-scan-20261112.log`。命令列出了 `api.nuget.org`；网络请求是否实际发生未独立追踪。未 restore、安装或上传源代码/用户数据。该结果仅适用于当时配置源和现有 restore 状态。 |
| Python dependency vulnerability check | `pip-audit` 不可用；本轮未安装工具，也未生成 PyPI vulnerability report | inventory 记录 29 个 requirements 条目均有 exact/bounded version constraint；这不是漏洞审计，也不验证 transitive dependency、hash pin 或仓外模型许可。 |
| 既有 `probes` | 2 passed / 1 failed，EXIT 1；两项 security/recovery finding 由 ZCode 只读源码裁定；第三项 path defense 验证成功 | `reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`、`reports/PROBES-RESULT-SEGMENT-B.md`、Canonical Evidence 中的原始 probes JSON/log。隔离数据只在 `tmp_path`，不访问真实漫画或用户数据库。 |
| 既有 `smoke --only core,wire` | 10 PASS / 7 FAIL，程序状态 FAIL、runner EXIT 1；7 项 Core 检查被 ZCode 归类为 `BLOCKED-SANDBOX-GRANT` 及级联；Wire 6/6 PASS | `reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md` 和对应 JSON/log。sandbox 拒绝/允许、hook timeout 和子进程树清理仍为零有效证据。 |
| 既有 `.NET tests` | 8/8 runner EXIT 1、TRX 0 tests，`BLOCKED-TESTHOST-ACCESS` | `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`。没有将其记作产品测试失败或通过。 |

## AUDIT-11 检查矩阵

| 检查面 | 状态 | 静态/运行观察与边界 |
|---|---|---|
| API Key 存储与脱敏 | PARTIAL | Python/C# 均有 Windows Credential Manager adapter；设置/档案保存 `credential_ref` 而非明文 key；`SecretValue.__repr__/__str__` 固定为 redaction marker；Host credential evidence 不写入 secret。未在真实 Windows vault 做读写/崩溃实测（.NET TestHost 未执行）；仍需检查全部错误/导出路径。参考 `src/ports/providers/credentials.py:40-64`、`src/infrastructure/credentials/windows.py:68-131`、`apps/desktop-avalonia/src/NewManga.Host/Credentials/WindowsCredentialStore.cs`、`HostCredentialCoordinator.cs:71-109,191-220`。 |
| 敏感配置泄漏 | PARTIAL | Provider endpoint 与 proxy URL 的设置入口拒绝 username/password userinfo；proxy 密码和 Provider key 使用 vault ref；TLS 默认验证开启，关闭需显式确认。OpenAI adapter 的认证 header 在请求构建时注入，错误映射不回显请求体或认证值。未覆盖用户手工修改 JSON、所有诊断响应与导出面；缺 credential 错误可能输出 opaque `credential_ref`，不是明文 secret。参考 `src/bootstrap/settings_commands.py:1237-1255`、`src/ports/network/profiles.py:33-66`、`src/infrastructure/providers/openai_client.py:202-250`、`src/infrastructure/transport/stdlib.py:443-481`。 |
| 路径遍历 / 文件写入边界 | **FAIL** | `SEG-B-PROBES-001`：攻击前提是在 managed root 中存在外部创建的 directory junction；probe 实测 `publish` 把产品生成的文件写到 junction 目标。`ManagedFileStorage.publish` 检查目标是否存在后创建父目录并 `os.replace`，此处没有与 `remove_managed` 同等 containment/reparse 检查。证据仅证明隔离条件下可在 root 外新建 revision 文件；不证明可覆盖已存在外部文件、任意写入用户内容或越过其他删除入口。ZCode 分级 Medium / High confidence。 |
| 不可信文件输入 / 图像解码 | PARTIAL | Referenced import 在读前限制容器/成员大小、entry 数和总解压预算；单图尺寸在 `image.load()` 前按 decode budget 检查；Core detect 限 PNG/JPEG、32 MiB encoded bytes 和 decoded-pixel budget。未做恶意压缩档案 corpus、图片解码 fuzz、PDF 引擎安全测试或真实用户数据测试。参考 `src/application/importing/referenced/scanner.py`、`reader.py:37-90,155-166`、`src/bootstrap/core_service.py:581-591,2895-2949`。 |
| SQLite 注入 | PARTIAL | 对定位到的主要动态 SQL 站点做了人工抽查：用户值以 bind parameters 传入；动态 table/schema 名来自固定 restore table/已知目录表列表；占位符 SQL 由内部值列表构造。静态 inventory 中 84 个 AST 候选同时包含 f-string/字符串拼接的固定 SQL，不等于 84 个漏洞；本轮没有完整 Roslyn/Python taint 分析、恶意数据库 schema fuzz 或全仓逐调用证明。参考 `src/application/maintenance/restore_plan.py:28-38,72-96,164-209`、`src/bootstrap/settings_commands.py:1142-1144`、`src/infrastructure/sqlite/source_sync.py:232-262`。 |
| 命令执行 | PARTIAL | 已定位的外部进程使用 `subprocess` 参数数组或 C# `ProcessStartInfo.ArgumentList`、`UseShellExecute=false`；没有发现 `shell=True` 模式命中。`icacls` 由 sandbox 设置 ACL，smoke 受权限失败阻断；实际隔离行为未验证。Host 目录打开使用固定 `explorer.exe`，路径来自 Host 目录选择/授权面。此处不是完整全仓命令/参数污点证明。参考 `src/infrastructure/plugins/sandbox.py:276-288`、`plugins/service.py:404-424`、`SidecarProcess.cs:98-125`、`HostGrantCoordinator.cs:606-612`。 |
| WebView/Tauri 权限 | NOT_APPLICABLE（当前架构） | 当前 V1 UI 为 Avalonia；静态 token scan 对 `WebView2` / `Avalonia.WebView` 在当前有效源码中命中 0。旧 Tauri/WebView 代码属于 Legacy，不据此声称旧代码安全，也不纳入当前发布路径。 |
| 依赖漏洞 | PARTIAL | NuGet `--vulnerable --include-transitive --no-restore` 在配置源无发现；Python `pip-audit` 缺失，没有 Python vulnerability database 结论。依赖许可、外部模型文件和最终打包依赖仍须 AUDIT-12/独立许可核验。 |
| 日志隐私 | PARTIAL | Host 日志记录稳定 code/sidecar，不直接记录 key；Host credential evidence 只含 owner hash/操作状态。`SidecarProcess.PumpStderrAsync` 会把 Core stderr 原样追加到本地 log，Core 有若干针对预览/cache 写入异常的 `repr(error)` 输出，OS I/O 异常可能带本地路径。当前证据未证明 API Key 泄漏或日志被外传；未做完整日志 redaction 测试。参考 `HostLog.cs:10-45`、`SidecarProcess.cs:400-424`、`src/bootstrap/core_service.py:4461,4929`。 |
| 文件覆盖 | **FAIL** | 与路径边界同一 `SEG-B-PROBES-001`；现有 `final_path.exists()` 保护已存在目标，但 junction 可让新文件落到 root 外。不得把已验证的 nmbak `../` 拒绝误写成所有文件路径都安全。 |
| 并发竞态 | NOT_TESTED | 本轮未执行并发 credential/profile/managed publication 或数据库压力探针。 |
| 异常退出 / 进程清理 | **FAIL（跨 AUDIT-01 finding）** | `NM-AUD-0001`：真实 `SidecarProcess` API 配合 helper 实测 pre-cancel 和直接 dispose 后子进程仍活着；cleanup 是 probe 随后终止 helper。ZCode reviewed `beaa134...` 后 ACCEPT、同意 P2；生产 Core/Bridge 在正常关闭后的行为仍未测。Review P3 observations N-1/N-2 扩充受影响调用路径，见 `reports/ZCODE-AUDIT-01-02-REVIEW-2026-11-12.md`。 |
| 网络失败 | PARTIAL | transport/provider 静态映射 DNS/TCP/TLS/timeout/auth 和 typed failure；TLS 默认校验开启，proxy fallback 缺省关闭。此前 6 个网络/TLS pytest 用例因环境缺 OpenSSL skip；本轮未打真实 Provider/API 或公网请求。 |
| 磁盘空间 / restore 异常 | **FAIL** | `SEG-B-PROBES-002` 使用隔离真实 SQLite/文件系统和 monkeypatch 模拟磁盘满：pre_restore 包创建后，数据库已变为备份点状态；managed 文件写入抛裸 `OSError`，无 typed code/rollback id。pre_restore 包仍在，未证明不可恢复；多文件部分写仅为静态推断、该 probe 未演示。ZCode 已分级 Medium / High confidence。 |
| 丢失/不可用模型文件 | NOT_TESTED | 未删除、移动或读取模型权重；未做缺文件、校验失败、模型初始化异常的动态测试。 |
| `../` 备份路径拒绝 | defense-verified | `test_nmbak_restore_can_overwrite_outside_managed_root` 被 `nmbak._managed_relative_path` 拒绝，拒绝发生在写入前；测试原本想复现越界写，未复现产品失败。 |
| 历史材料传播 / 远端可见性 | BLOCKED | `AUDIT-11-INC-001` 保持 `INVESTIGATE`：本地 Git 证据支撑历史对象曾进入公开 `main` 的高置信推论；实时远端可见性、授权语境与缓存状态未知。本 Task 不执行 push、远端查询、删除、历史改写或补救。 |

## Finding 分级与边界

- `SEG-B-PROBES-001`：Medium / High confidence（已有 ZCode triage）；攻击者须先在 managed root 中建立 junction；观测结果只写入产品生成的 revision bytes，且已有外部目标被 `exists()` 阻止。没有权限提升证据。
- `SEG-B-PROBES-002`：Medium / High confidence（已有 ZCode triage）；pre_restore 包存在，finding 是恢复期间数据库状态与文件状态不一致的已观察行为，以及缺少 typed rollback 指引；未实测真实磁盘满、多文件中间态或用户数据。
- `NM-AUD-0001`：P2（ZCode 对 2026-11-12 阶段 Review 的结论；见独立 Review 报告）。真实生产 sidecar 和用户可见影响仍未验证。
- 没有把 `AUDIT-11-INC-001` 的高置信传播推论写成已核验的当前远端泄漏，也没有在本报告对它定为 P0/P1。

## 未执行 / 限制

本阶段没有重跑 probes、pytest、.NET tests 或 smoke；引用的是已固定的段 B 证据。没有真实 UI、真实付费 API、真实漫画内容、私人数据库、外网材料访问或干净 Windows 安装测试。没有安装 `pip-audit`、Semgrep、bandit、mypy 等工具。没有修改或读取私有素材内容；没有进行远端仓库查询、清理或补救。以上均不得标记为 PASS。

## 下一步

先由 ZCode 对本 AUDIT-11 交付和映射作独立只读 Review；然后按计划执行 AUDIT-08 隔离数据库专项及 AUDIT-05/06 契约核对，再做 AUDIT-14 V1 覆盖/债务矩阵和 AUDIT-03/04/07/10/13 合成验证。所有产品修复均需单独释放实现 Task。
