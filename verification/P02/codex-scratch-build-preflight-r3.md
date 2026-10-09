# P02 当前 Scratch Isolation Stage-1 Preflight（R3）

- 采样时间：2026-10-10 03:30:19 +08:00；结果：PRESTART_STAGE_1_PASS。
- 父 Task=P02 仍为 in_progress / ACTIVE。Codex-only isolation 子任务 Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。
- 本轮基于 R10 固定候选 92dc7361194f1db8fdf7aff3a15a3d234ae56678；R10 exact-head DSH Review 与 erratum 最终为 APPROVED，P0/P1/P2/P3=0/0/0/0。R10 仅审查已固定的条件闭合证据，不替代本轮 fresh stage-1 evidence 的独立复核。
- 本次观察文件 [observations R3](codex-scratch-build-preflight-observations-r3.json) 使用提交规范字节口径：canonical LF SHA-256=39c484f52fcb1c3e040b5ffdbab62b50e13d2b45c41d9d93d59221bd0fbbb74c，21,705 bytes；此前状态见 [R5 start checkpoint](codex-checkpoint-p02-preflight-r5-start.md)。

## 本轮只读检查

- PowerShell 7.6.6，进程路径 C:\Program Files\PowerShell\7\pwsh.exe；token elevated=false，Environment.UserInteractive=true。PID、Host 名称与其余 shell 属性见 observations R3。没有提权或改变系统功能。
- Get-CimInstance Win32_OptionalFeature 对 Containers-DisposableClientVM 返回 InstallState=1（Enabled）。这只证明 feature 状态，不证明隔离。
- 提案仅要求 BIOS virtualization；本次只读观察到 CIM VirtualizationFirmwareEnabled=true，而 VMMonitorModeExtensions 与 SecondLevelAddressTranslationExtensions 均为 false。提案没有命名这些 CIM 字段，也没有把它们各自设为 Gate；Stage-1 阈值仍按冻结提案原文判定。
- Windows Sandbox 当前用户 AppX 为 MicrosoftWindows.WindowsSandbox_0.8.107.0_x64__cw5n1h2txyewy；实测 wsb.exe 版本=0.8.107.0，156,160 bytes，SHA-256=247e092b5c5bd37820f225a7dd3ddf10ae37a67e2751a19c24b802c84769c441；wsb --version 和 wsb list --raw 均 EXIT=0，列表为空。@oai/sky 捕获时间为 2026-10-09T19:29:16.092Z（2026-10-10 03:29:16.092 +08:00），列出 40 个 apps、4 个 windows，无 Sandbox app/window，未保存 screenshot。
- 12/12 冻结 HostFolder 根的期望存在状态匹配，均未发现根路径自身是 reparse point：1 Scratch RW、9 Smoke RO、2 Build-only RO。此检查不遍历目录，也不证明递归 reparse-point containment。
- 20/20 精确输入文件 SHA-256 匹配；14/14 已注册 expected-size 匹配；另外 6 项没有登记 expected size，size_match 保持 null / NOT_APPLICABLE。 冻结 TSV 的 6 行未登记 expectedBytes 保持原样；其 legacy sizeMatch=True 不作为 R3 尺寸通过依据，R3 明确记录 size_match=null。
- 固定 source commit 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a 存在且为当前 live main 的祖先；三个 Git blob 和预期 CRLF 转换 SHA-256 全匹配。真实 clone checkout 尚未进行。
- 固定 Smoke r3 XML 为 canonical LF 2,609 bytes，SHA-256=9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d；Windows CRLF checkout 为 2,631 bytes；解析得到 11 个 mappings（含 clone-local canary）。
- 固定 clone 路径 G:\CODEX\P02-scratch-build-source 不存在。

## Root 保护复核

- Live root 为 G:\CODEX\New Manga，main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50，共用 Git 目录 G:\CODEX\New Manga\.git。
- 冻结清单 203/203；missing/extra/mismatch=0/0/0；staged=0；unstaged tracked=4；untracked=199；canonical entries SHA-256=3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2 与冻结值相同。
- 四个 tracked modified 路径是 .qoder-credits/report.json、doc/12_ROADMAP.md、doc/tasks/README.md、verification/PROJECT-ROADMAP-20261008/ROADMAP.md；本轮候选路径与 root dirty paths 交集=0。本次更新目标 P02 当前状态文档在 root 均为 clean。
- 第一次聚合命令误把 porcelain 状态 ?? 当成 staged；按 index 列规则修正后 staged=0。第一次门槛聚合命令又引用了规范化磁盘对象中不存在的 FreeSpace 字段；原始 free_bytes 未变化，按记录字段复算 C/G 阈值通过。两个聚合器问题均显式记入 observations R3，未更改 root 或宿主状态。

## Gate 边界与下一步

- 本轮仅 Stage 1=PASS。完整 preflight 仍为 BLOCKED / INCOMPLETE，因为尚未创建并验证 clone，也未生成所有映射根的递归 manifest/reparse traversal。
- Smoke admission 仍为 NOT_ADMITTED，等待本轮固定候选的独立 exact-head Review 与 Codex 单独准入 checkpoint。未创建 clone、未启动 Sandbox、未运行 Smoke、Build、runner、Vitest、GUI 或产品验收。
- Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；P02 AC1–AC7=BLOCKED / NOT_RUN；Hard Build Barrier 仍有效。
- 下一准确动作：完成 Task/Plan/Status/Index 当前段同步，运行路线/差量/链接/manifest 验证，固定新候选 commit，然后正式派发 DeepSeek Harness exact-head Review。只有 Review 通过后，Codex 才可单独将 Smoke admission 记为 ADMITTED；届时仍须在 interactive non-elevated shell 中完成 clone、递归 manifest、session binding、空 list 和 screenshot 等所有 pre-start checks，才能执行一次获准 Smoke。