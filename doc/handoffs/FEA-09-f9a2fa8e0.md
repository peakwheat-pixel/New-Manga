# FEA-09 — Codex Phase C–D 工作树检查点（非可集成交付）

- 日期：2026-11-03；Owner：Codex（DSH 额度恢复后续跑）。
- 仓库：G:/CODEX/New Manga；branch：main；Git common dir：.git。
- 基线/当前 HEAD：f9a2fa8e077f21c93131237171a32e85f6942200。
- delivery_head：null；integration_commit：null；Task：in_progress。
- 本轮无新 commit、无 push。git add 实际 EXIT 128，.git/index.lock Permission denied。禁止把当前 HEAD 当成本轮实现交付。
- Phase A：ZCode，d3d7cd564；Phase B：ZCode，ceae03edb。DSH 的 47/69 passed 是历史集成结果，本轮未复现完整 pytest，不重新署名。

## 已做的工作

1. 通过 Node fs/child_process 核实 HEAD、四份原始 Phase C 半成品并接续，未丢弃现场。
2. Core source-read 注册/撤销 host-control 命令、普通 Plan/Start/Receipt/Cancel 命令面；minor 保持 3；增加 source.read/1；旧 ImportPages 注册类未重写。
3. Core scope 保存与比较、签名错误优先级、expiry/generation/EOF fail-closed、绑定 secret_ref 拒绝；strict 源句柄取 identity/size/digest，commit guard 持句柄及 registry 锁直到页事务结束。Python/Win32 volume serial 按 Win32 DWORD 口径比较。
4. Host 私有 SourceAccessRegistry：NMSAR1\0 + JSON 长度 + DPAPI CurrentUser；根身份、generation/撤销；Global→Local mutex 和独占 lock 文件；持锁重载；temp+Flush(true)+原子替换；损坏副本、显式 quarantine/reset。ACL/DPAPI 失败拒绝可用。此实现尚缺原生成功证据和完整故障矩阵。
5. SourceReadCoordinator、8 个 snake_case Host 命令登记及能力门禁、grant 签发 API、撤销持久化后 Core ACK 检查；不新增 IHostController 成员。
6. WireLog.Add 在创建可保存 Frame 前重写 request/response，整对象遮蔽 secret_ref，遮蔽 signing_key、host_session_credential、嵌套 path 和绝对路径字符串；hex 由安全字节重算。传输返回给协议解析器的原始响应不作日志存储。
7. ReferencedImportEnabled 由 HostOptions→CoreServiceOptions→显式 sidecar 环境贯通；Host/Core Plan/Start 拒绝新导入，Receipt/Cancel/既有读入口保留。referenced 资源读未接通时返回 SOURCE_ACCESS_DENIED，不伪装成 PAGE_NOT_FOUND 或任意路径回退。
8. rendition_cache.py：冻结 C-15 表上的缓存组件，key 包含 source/version/entry/kind/decoder/版本/参数；总量/文件/解码预算、并发排队、LRU/同刻大文件优先、活跃引用及 preflight pin、损坏重建、启动孤儿/temp 清理。只管理 derived/source-renditions，未更新 Source 内容身份列。

## 未完成与必须恢复的位置

- **生产 referenced 读取仍未接线**：缓存组件尚未装配到页资源 renderer/catalog/Host/V2 adapter；当前 referenced 页读取为 typed fail-closed，不能宣称双读成功。下一步从 core_service.handle_resolve_page_resource 和 HostRuntime.ReadPage/资源链开始，完成四维 scope→已有 binding/entry/version 的真实映射、decoder 及预算校验，再发布可再生 rendition。不得原样发布 raw user-source。
- **密码生产链未接通**：Host 尚缺安全短期 secret 文件签发、TTL/孤儿清扫及 Core assembly 安全 reader 接线；现有 secret_ref 校验只拒绝未签名绑定引用，不能宣称密码重试产品成功。检查 Phase B secrets.py 的 TTL/目录/同句柄消费及清零删除边界，不得接受普通应用 payload 的任意 OS 路径。
- **完整授权矩阵缺失**：Host 原生 DPAPI/ACL/重启/跨进程锁/根替换/持久化失败/ACK 丢失尚未通过；四维 scope 的组件比较不替代生产 entry/rendition 绑定验收。Host IssueAsync 的 wire 签名需真实跨语言 IPC 复核。
- **Phase B 兼容边界需复核**：Start 的确认前 source/generation/digest 强重验、加密源容器重验、取消/丢 ACK/重启自然键矩阵尚未重新验证；已有 test_plan_stale_when_container_changes 仍期待 accepted 后异步失败，应按 C-16 §5 核对，不把旧测试当契约裁决。
- 无真实 Host IPC + V2 生产 adapter 证据；无 UI 完成声明。
- 完整 pytest 回归未运行；完整 .NET 两次超时并出现真实失败，不能标 PASS；独立 Review、DSH 集成均 NOT_RUN。
- 无分阶段 commit：Git 元数据只读，不能以 Node 直接改写 .git 绕过权限。

## AC 状态（详见 Task 原文）

| AC | 本轮状态 | 证据/缺口 |
|---|---|---|
| AC-1 | PARTIAL | Phase B 格式实现；pytest 格式矩阵 NOT_RUN |
| AC-2 | PARTIAL | Host 自然顺序已补；完整顺序矩阵 NOT_RUN |
| AC-3 | PARTIAL | Phase A/B 保留；跨项目/人工数据回归 NOT_RUN |
| AC-4 | PARTIAL | WireLog 定向通过；密码真实签发/消费未接通，DPAPI 原生失败 |
| AC-5 | PARTIAL | Phase B 状态机保留；取消/重启/丢 ACK 全矩阵 NOT_RUN |
| AC-6 | BLOCKED | 真实 IPC/V2 与生产 rendition 尚缺 |
| AC-7 | PARTIAL | 开关及 typed 拒绝已补；双读成功/迁移回归 NOT_RUN |
| AC-8 | PARTIAL | build/定向/机械门禁通过；全量、commit、独审、集成未通过 |
| AC-9 | PARTIAL | Core grant/strict 句柄组件 5 passed；Host 原生 2 failed、完整矩阵缺 |
| AC-10 | PARTIAL | 缓存组件 5 passed；生产 decoder/通道整链未接线 |

## 验证（所有 shell 通过 Node，cwd 为仓库根）

每份 logs/*.log 头记录 exe、args、cwd、执行时 HEAD，尾记 EXIT；HEAD 一直为上述基线、实现未提交。日志绑定的是 dirty 工作树，不能声称固定 commit 已验证。代码/证据工作树 SHA 见 EV 与本轮恢复清单。

| 实际命令 | EXIT/实际结果 | 日志 |
|---|---|---|
| dotnet build apps/desktop-avalonia/NewManga.sln --nologo | 1，NuGet path1 为 null（当前环境 APPDATA 未配置） | dotnet-phase-c-build.log |
| dotnet build ... --no-restore --nologo | 1，Avalonia 遥测试图写用户目录被拒 | dotnet-phase-c-no-restore.log |
| dotnet build apps/desktop-avalonia/NewManga.sln --no-restore --nologo -p:UsedAvaloniaProducts= | 0，0 warning / 0 error，最后一次见指定日志 | dotnet-build-evidence-final.log |
| dotnet test NewManga.CoreClient.Tests.csproj --no-build --nologo --filter WireLogSourceRedactionTests/DraftCommandRegistryTests/CommandContractV11RTests（精确 filter 见日志） | 0，19 passed / 0 failed / 0 skipped | dotnet-source-command-evidence-final.log |
| 原生 SourceRegistryTests + WireLogSourceRedactionTests 定向 | 1，脱敏 2 passed；DPAPI/ACL 2 failed | dotnet-phase-c-tests.log |
| dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo | EXIT=null，第一次 50s、第二次 170s 超时；第二次观察 9 failed / 55 skip（不是完整总数） | dotnet-full.log / dotnet-full-r2.log + summary.json |
| C:/Python314/python.exe -m pytest tests/fea09 -q --basetemp=<指定 workspace tmp>/pytest-c-baseline | 1，No module named pytest | python-phase-c-baseline.log |
| 安装已声明 pytest==9.1.1 到指定外置 tmp | 2，创建目标目录 PermissionError；不能声称安装成功 | python-test-dependencies.log |
| Python unittest 两组件，精确 -c 见日志 | 0，10 passed / 0 failed（真实句柄组件 5 + 缓存组件 5；不含生产 IPC/UI） | python-components-delivery-checkpoint.log |
| Python AST parse | 0，22 files；仅语法检查 | python-final-syntax.log |
| pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-09.md | 0，PASS（3 warnings）；最终文档更新后再跑 | check-final-r2.log |
| pwsh -NoProfile -File tools/governance/verify_pins.ps1 | 0，17/17 | pins-final.log |
| git show f9a2fa8e0:<4 PNG> 对照工作树 SHA/字节 | 0，4/4 unchanged | fea06-png-audit.json |
| git diff --name-only + git ls-files --others --exclude-standard | 0，未发现 allowed_paths 之外文件 | allowed-paths-audit.json |
| verification/FEA-09 已知合成密码/hex/base64/url 与脱敏哨兵扫描 | 0 命中；**不是尚未执行的真实 Host wire 审计** | password-audit.json |
| git add -- <本轮代码路径> | 128，index.lock Permission denied | git-stage-node-blocked.log |
| 测试残留进程 CIM 只读查询 | 1，拒绝访问；未核实残留，不终止未知进程 | test-process-status.log |

完整 Python tests/import_formats、storage/core/library、旧 ImportPages、m2_resource_channel：NOT_RUN。完整 .NET 没有取得基线 1292/0/57，不能用定向数字替代。
第二次全量里的 55 个观察到的 skip 名称、9 个失败名称及已完成 assembly 的局部计数逐项写入 dotnet-full-r2-summary.json。stdout 未输出逐项 skip 原因，原因未确证，不冒充已解释的 57 个基线 skip。部分失败含 UI 时钟/断言，未在禁止写域返修，也未假定均为环境问题。

## 资源与字节保留

- 原四份 Phase C 半成品已接续；新增与修改路径见 allowed-paths-audit.json。
- 指定 G:/CODEX/New Manga.workspace/FEA-09/tmp/ 安装目标写入失败；没有通过其他位置安装生产依赖，没有新增 requirements/NuGet 依赖。未创建 tmp/*.js 脚本。
- verification/FEA-09/{grant-component,cache-component,native-registry}/ 为本轮**保留的合成证据输入/输出**，不是用户数据；逐文件 SHA-256 登记在 EV.md，失败尝试也保留。native-registry 未取得成功持久化证据。
- 既有 ignored bin/obj 为实际 dotnet 构建输出，未清理；未删除任何 worktree、用户数据、managed/derived 既有文件或历史证据。
- 冻结契约未改字节，17/17；四 PNG 原字节不变。未改 UI Views/ViewModels、共享组合根、FEA-08、packaging 或 requirements。
- 新证据尚未提交，EV commit pin 明确 pending；canonical_evidence_status/resource_closeout_status 保持 pending。

## 下一接收者与可转发指令

推荐 DSH 先处理执行环境和授权写域；同一 FEA-09 由 Codex 续跑，不释放新的产品 Task，不开始同会话自审。

> DSH/Codex：在 G:/CODEX/New Manga、main，基线/当前 HEAD=f9a2fa8e077f21c93131237171a32e85f6942200，先读取 FEA-09 Task、本 Handoff、EV 并核对 dirty SHA；不要 reset/stash 丢弃现场。DSH 先恢复 .git 元数据写入、指定外置 tmp 及 Windows DPAPI/ACL/sidecar 测试环境。Codex 按现有 allowed_paths 继续 Host 密码引用、四维 scope/binding 与生产 rendition/catalog/V2 读取接线，复核 Start 确认前重验，补真实 IPC 与完整失败矩阵；不改冻结契约/UI/共享组合根/依赖/FEA-08，不 push。重跑 Task 列明 Python/.NET/check/pins/四 PNG/范围门禁，保留精确 cwd/head/EXIT/原始输出；取得真实结果后更新 AC/EV，Phase C/D 分别提交中文 commit，再以最终实现 head 生成新 Handoff。独立 Review Appointment 与集成/关闭由 DSH 负责；未运行和受限项继续如实标记。
