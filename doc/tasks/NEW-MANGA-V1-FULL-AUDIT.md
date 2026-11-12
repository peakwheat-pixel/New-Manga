---
id: NEW-MANGA-V1-FULL-AUDIT
title: V1 全项目独立审计
kind: research
governance_version: 3
status: in_progress
resume_status: in_progress
approval: user_approved
suggested_owner: Codex
owner: Codex
reviewer: ZCode (fresh independent context after delivery)
depends_on: []
base_commit: 10e4ee013835605800d3830fb960ae8d3aa04167
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: audit/V1-FULL-AUDIT
allowed_paths:
  - audit/V1-FULL-AUDIT/**
  - doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# NEW-MANGA-V1-FULL-AUDIT

## 来源与目标
用户2026-10-24粘贴的完整自主审计指令；本轮新增只读审计 Task，不重新激活历史实现。Codex接任Lead Auditor，明确覆盖AUDIT-00–14；允许隔离本地扫描/测试与报告，不授权业务修改、安装、付费API、发布、删除、清理或上传项目材料。

## Acceptance Criteria
- [x] AC1：固定Git/环境及有效源码清单，记录dirty和历史缺口。 <<MET>>
- [ ] AC2：15项专项逐项有真实检查结果或具名阻断，关键链路深读与测试。 <<PARTIAL: AUDIT-01–14 因原始清单缺失保持具名阻断；probes EXIT 1（2 项 Medium / High confidence，1 项 defense-verified）；Python Core pytest EXIT 1（3,519 passed / 16 failed / 10 skipped）；Avalonia .NET 为 BLOCKED-TESTHOST-ACCESS（8/8 EXIT 1、TRX 0 tests）；smoke EXIT 1（Wire 6/6 PASS，Core 4 PASS / 7 BLOCKED-SANDBOX-GRANT，frontend/packaged SKIP）>>
- [ ] AC3：完整日志、问题分级、整改路线、正式报告和Release Gate落盘。 <<PARTIAL: probes 分级、pytest 失败摘要、.NET TestHost、smoke 沙箱阻断和 governance 默认 check 均已记录；完整审计与最终 Release Gate 门禁待完成>>
- [ ] AC4：独立复核、证据pin和治理检查可核验；未满足不得置done。 <<PARTIAL: 段 B 中间证据已提交并 pin；ZCode checkpoint addendum 已关闭 R-1/R-2/R-3（R-4 保持 observation）；最终治理门禁与全审 review 未完成>>

## 允许修改范围
仅frontmatter所列。审计日志/测试脚本由主控单一写入。三名子代理只读同一固定产品HEAD，无并发写入。用户显式审计目录优先于常规verification路径；运行派生产物放相邻workspace task-env。

## 禁止范围
src/**、apps/**、原有tests/**、共享契约、Schema、依赖、真实用户数据、历史证据及Git历史不修改。没有实现任务释放。

## 测试要求
使用 audit/V1-FULL-AUDIT/tests/audit_runner.py，日志保存argv/cwd/shell/interpreter/exit/elapsed；真实GUI若不可捕获则BLOCKED，不用JSX或Mock替代。真实API/模型标注和干净Windows无条件时BLOCKED。

## Canonical Evidence
全审最终证据仍为 pending。当前段 B 范围裁决与阶段 0 证据如下；这些证据不代表 AC 已完成或 Release Gate 已通过。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| SCOPE-1 | 解封范围与传播风险裁决 | `audit/V1-FULL-AUDIT/reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md` | `304a40addb4818f415b1e86d5c5b65205eca3605` | `0BE9C7ECBCE7C4EA6482FF8248DF16179380A742096BB84D51716304DE6D9D54` | CANONICAL | BLOB |
| STAGE0-1 | AC1（段 B 基线/范围前置核验，partial） | `audit/V1-FULL-AUDIT/logs/stage0-resume-verification-20261112.log` | `304a40addb4818f415b1e86d5c5b65205eca3605` | `7E2A4911D7F1AB2D21DE48C4AC4B77F2C8BACCC5FA6CB1D6C2DFF681F32260A7` | CANONICAL | BLOB |
| GATES-1 | AC4（TaskPath/default/pins/API release gates，partial） | `audit/V1-FULL-AUDIT/logs/segment-b-release-gates-df120fb.log` | `4b5aa2d6a327c7ffa2c5b3025473fb5a6f3f1179` | `F426CF2DEC18EA69D5A584950787A15753506D037CE48021CB41FED1771CFA85` | CANONICAL | BLOB |
| BASELINE-1 | AC1（段 B Git/environment，MET） | `audit/V1-FULL-AUDIT/evidence/baseline-segment-b.json` | `1a8238b9f86427efe5c48918f3bc0f2942611732` | `9553030087685016AF6070C2E33AEF373F5AA713950CD179BE06129954F95A3E` | CANONICAL | BLOB |
| SOURCES-1 | AC1（段 B effective source manifest，MET） | `audit/V1-FULL-AUDIT/evidence/source-manifest-segment-b.json` | `1a8238b9f86427efe5c48918f3bc0f2942611732` | `DF83A2D57A1F73A0155951461FCC11C0033E3F020BC9F439B0E8239A7157C727` | CANONICAL | BLOB |
| AUDIT00-LOG-1 | AC1（段 B baseline 命令与 EXIT，MET） | `audit/V1-FULL-AUDIT/logs/audit-00-segment-b.log` | `1a8238b9f86427efe5c48918f3bc0f2942611732` | `A66823B170F3A22BA41912E85C245AE4CC837FF24EF90FF68DC49FE7E7BEEC05` | CANONICAL | BLOB |
| AUDIT00-REPORT-1 | AC1（段 B limitation 与历史缺口，MET） | `audit/V1-FULL-AUDIT/reports/00_BASELINE-SEGMENT-B.md` | `1a8238b9f86427efe5c48918f3bc0f2942611732` | `7E282EEF4DCF46C604F404F7B2E1C4B22C5036B484473F54A8F71D9F9D6555CD` | CANONICAL | BLOB |
| TESTMAP-1 | AC2（suite 适用性与范围缺口；测试未执行） | `audit/V1-FULL-AUDIT/reports/TEST-MAPPING-ADJUDICATION-2026-11-12.md` | `50845a11cc2ab8b7d1ecb1d1eaa64b73ce2bbb5a` | `4E4CE72EBFBEC312310B62BF1B9798E6332B57A4D39999B440F8846239C4637B` | CANONICAL | BLOB |
| TESTMAP-LOG-1 | AC2（ZCode 裁决 CLI / 清单定位命令与 EXIT） | `audit/V1-FULL-AUDIT/logs/test-mapping-adjudication-20261112.log` | `50845a11cc2ab8b7d1ecb1d1eaa64b73ce2bbb5a` | `920368B0E2FCCC139CB0DA48730E08E1909285EEE73C6E6674BFBF9F5E786291` | CANONICAL | BLOB |
| TESTEXEC-1 | AC2（限定 suite 执行范围/输出隔离裁决；测试未执行） | `audit/V1-FULL-AUDIT/reports/TEST-EXECUTION-ADJUDICATION-2026-11-12.md` | `7d2d4d423bf0797c99e4cca2ea3ddb82578ae634` | `943BB6468564ED6440ED9969128598EEC16B4EFD590CE1BA2C754CB77E9F5B21` | CANONICAL | BLOB |
| TESTEXEC-LOG-1 | AC2（ZCode CLI/只读目标核验及 EXIT） | `audit/V1-FULL-AUDIT/logs/test-execution-adjudication-20261112.log` | `7d2d4d423bf0797c99e4cca2ea3ddb82578ae634` | `086F13D7905B45B7B6651A7EE5A6E62BB20C49C262A028622F1D144B74CFE86B` | CANONICAL | BLOB |
| AUDIT-RUNNER-SOURCE-1 | AC2（当前/Legacy suite runner 实现） | `audit/V1-FULL-AUDIT/tests/audit_runner.py` | `5ab8ae006580f4c3aab6d61ce180794921dc7641` | `C3B2FF42251A7BBEB84A80752C82A907D584B37A233EFDCF94166E1693E6782A` | SOURCE_PIN | BLOB |
| PROBES-RESULT-1 | AC2（段 B probes 实际结果，EXIT 1） | `audit/V1-FULL-AUDIT/evidence/audit-probes-segment-b-20261112T081030840760Z.json` | `fbf138af6a0e037f86802ef599277898c7abaa7e` | `A7074CD6264F93DFE258758A0FE5D5C9F85711C10F512DA88C5E21F88085E3B8` | CANONICAL | BLOB |
| PROBES-LOG-1 | AC2（段 B probes 命令、生成 HEAD、EXIT 与原始输出） | `audit/V1-FULL-AUDIT/logs/audit-probes-segment-b-20261112T081030840760Z.log` | `fbf138af6a0e037f86802ef599277898c7abaa7e` | `D1BEF19A173D66D63AC1E8B6F973E5306B19270464A6211D41429A8BE9B402B5` | CANONICAL | BLOB |
| PROBES-REPORT-1 | AC2/AC3（probe 观察、解释边界与待分级风险） | `audit/V1-FULL-AUDIT/reports/PROBES-RESULT-SEGMENT-B.md` | `9ce6bb09dce228018426e979f562c5999df2efc5` | `514680B15B579F26FC340FF08375126A6871692309272A68A3665970EDA942B1` | CANONICAL | BLOB |
| PYTEST-RESULT-1 | AC2（段 B Python Core pytest JSON，EXIT 1） | `audit/V1-FULL-AUDIT/evidence/pytest-segment-b-20261112T081732598825Z.json` | `40f47362894f2ea6dcd66d463a72328aad37bbc6` | `EC113D63AA85C50998E85CF873F6D88528C1B3BBB621695ACB0E3562BEFF2EC8` | CANONICAL | BLOB |
| PYTEST-LOG-1 | AC2（pytest 完整输出、失败栈与 skips/warnings，EXIT 1） | `audit/V1-FULL-AUDIT/logs/pytest-segment-b-20261112T081732598825Z.log` | `40f47362894f2ea6dcd66d463a72328aad37bbc6` | `19B5EB99B96A5F5ABE53D81DE00848F6FBCBA5FA06A38B8F4B9D545F9FBC8754` | CANONICAL | BLOB |
| PYTEST-REPORT-1 | AC2/AC3（pytest 结果分组、限制与未执行项） | `audit/V1-FULL-AUDIT/reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md` | `65328772e3cc62c15509a2d4a5800990df3fdd4d` | `844415277388472A7918945DCE2011A63B9E6777C8946CB8E0E2111D2AF066AA` | CANONICAL | BLOB |
| PROBE-TRIAGE-1 | AC2/AC3（ZCode probe 分级、defense-verified 与限制） | `audit/V1-FULL-AUDIT/reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md` | `65328772e3cc62c15509a2d4a5800990df3fdd4d` | `533C8B036C8B3EAD6068668377A798836984FD9385BD102DC1845E8B8AF2515B` | CANONICAL | BLOB |
| PROBE-TRIAGE-LOG-1 | AC2/AC3（ZCode 只读确认原始回答、session/turn/trace 与 EXIT） | `audit/V1-FULL-AUDIT/logs/probe-triage-confirmation-20261112.log` | `40f47362894f2ea6dcd66d463a72328aad37bbc6` | `3E552DA0DCA0C18C09CED038B71AF93A547B97B4AAFA3AF5F1C8DA1BDE5CABAE` | CANONICAL | BLOB |
| DOTNET-RESULT-1 | AC2/AC3（8 项 Avalonia TestHost 阻断报告与 TRX 指针） | `audit/V1-FULL-AUDIT/reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md` | `fea2be5a600a04a041740973af65ad949ac501b6` | `D9C124D7F3D085B0A5E9C01CFFA5D79DFDC292D95A089B594E2B485FEA24AF0D` | CANONICAL | BLOB |
| DOTNET-ADJUDICATION-LOG-1 | AC2/AC3（ZCode 对 TestHost access block 的只读 adjudication 原文） | `audit/V1-FULL-AUDIT/logs/dotnet-result-adjudication-20261112.log` | `c138643b8d265ce4923be39f7fa7a19a110af9f2` | `351C5EDAF43AF26FA0AA764CA61E158C2C83BCF2116F86F44503AFDEABF81471` | CANONICAL | BLOB |
| DOTNET-APP-RESULT-1 | AC2（App 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-app-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `7EF119A771CE1B1CB65881A311E3F4EA94EF359C909E77D97D905B36FCFB55CE` | CANONICAL | BLOB |
| DOTNET-APP-LOG-1 | AC2（App 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-app-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `D703E7AB25A279ED120DD88B5A01528F9586E7A96B858470136AD49E8ED93FD7` | CANONICAL | BLOB |
| DOTNET-APPEARANCE-RESULT-1 | AC2（Appearance 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-appearance-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `19777F18A802A6A55E2E2E9F02BA7F064842715551E49371EEB02CDBBAC23F86` | CANONICAL | BLOB |
| DOTNET-APPEARANCE-LOG-1 | AC2（Appearance 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-appearance-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `720D2C4E4DEC8655E7F3A06178FE2F30EE3C1BB712024917C020D6B7D968D881` | CANONICAL | BLOB |
| DOTNET-APPLICATIONCORE-RESULT-1 | AC2（ApplicationCore 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-applicationcore-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `A92EAA09FB57B52337B823C9C8CF235B5DBCA2E5074530EFDCAFF166B39D16C0` | CANONICAL | BLOB |
| DOTNET-APPLICATIONCORE-LOG-1 | AC2（ApplicationCore 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-applicationcore-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `849F8FFC19B9E92B481F516633DA2B160D723A689AAEFC5261120786A7B6FC15` | CANONICAL | BLOB |
| DOTNET-CORECLIENT-RESULT-1 | AC2（CoreClient 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-coreclient-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `60CA7B3178928BB00C01248345534E3AF3C8B1E5421680EB4F6E55D33DCBAA8D` | CANONICAL | BLOB |
| DOTNET-CORECLIENT-LOG-1 | AC2（CoreClient 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-coreclient-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `73783A6F3F87E158D26BE27A5825309A2069F0598316F3AB86665C05CC5CD40F` | CANONICAL | BLOB |
| DOTNET-DESIGNSYSTEM-RESULT-1 | AC2（DesignSystem 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-designsystem-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `7317583C73CAB8F8DEEC9CDBFAAFDB610CB694B5959DD581123CA121FE785043` | CANONICAL | BLOB |
| DOTNET-DESIGNSYSTEM-LOG-1 | AC2（DesignSystem 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-designsystem-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `0EA6DFD79CBAC6E2CA13E9B6F1052F6DC012874E2E3EEDC7F4B2F6C5A3FA2DBA` | CANONICAL | BLOB |
| DOTNET-HOST-RESULT-1 | AC2（Host 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-host-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `E19284C3E7AF4D4F47CA82701F07D43821D4CC663CE6B0B9D5EC0729DED81CA8` | CANONICAL | BLOB |
| DOTNET-HOST-LOG-1 | AC2（Host 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-host-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `E66C134FDCB1F1E390FAC233D11D6766403142672C509F5C78910E0321CD4FC5` | CANONICAL | BLOB |
| DOTNET-PRESENTATION-RESULT-1 | AC2（PresentationAvalonia 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-presentationavalonia-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `784E317F978597C3107F4A58E361D18A8CBC35DB1D4960038A3C7C17520D4005` | CANONICAL | BLOB |
| DOTNET-PRESENTATION-LOG-1 | AC2（PresentationAvalonia 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-presentationavalonia-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `07AAA904B14DF71589ED5B143E476E223694FA41B379DBB8FD3E4B8DB407C25B` | CANONICAL | BLOB |
| DOTNET-THEMEENGINE-RESULT-1 | AC2（ThemeEngine 项目 runner JSON，EXIT 1，TRX 0 tests） | `audit/V1-FULL-AUDIT/evidence/dotnet-themeengine-20261112T083119769139Z.json` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `66D55F262A56EE82139210F1FF2C094E292FFA71F4B30F58418E0DB0127FC8B1` | CANONICAL | BLOB |
| DOTNET-THEMEENGINE-LOG-1 | AC2（ThemeEngine 项目完整日志、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/dotnet-themeengine-20261112T083119769139Z.log` | `426a4fc5d5a551f04cf58979176baa4150351d5c` | `370A4DF30EE0CE4F730495F9F2FFFAF786A7F1FC5ADFE4ECDC75A831FA85FB69` | CANONICAL | BLOB |
| SMOKE-REPORT-JSON-1 | AC2（core/wire 分层 checks JSON：17 checks，10 PASS / 7 FAIL） | `audit/V1-FULL-AUDIT/evidence/software-smoke-report-segment-b-20261112T084557725697Z.json` | `d480745da4d263875181bc717c4828df6c8b749e` | `0DBAC92E9525503E486AD6AA4C3F475EC808409504F138F7351DD7C7726E21C8` | CANONICAL | BLOB |
| SMOKE-RUNNER-JSON-1 | AC2（runner argv、生成 HEAD 与 EXIT metadata） | `audit/V1-FULL-AUDIT/evidence/software-smoke-segment-b-20261112T084557725697Z.json` | `d480745da4d263875181bc717c4828df6c8b749e` | `6B452972CFD2C211A32D855011F0FA8F5D6683ACE5EB741FDD978B0CC7535681` | CANONICAL | BLOB |
| SMOKE-LOG-1 | AC2（smoke 完整输出、argv/cwd、生成 HEAD、时点、EXIT） | `audit/V1-FULL-AUDIT/logs/software-smoke-segment-b-20261112T084557725697Z.log` | `d480745da4d263875181bc717c4828df6c8b749e` | `760877EAA32EC76E3FB770CB1F88C1EFEC61C89AB2D6418F5BB6D745279ACAA4` | CANONICAL | BLOB |
| SMOKE-ADJUDICATION-LOG-1 | AC2/AC3（ZCode smoke 只读 adjudication 原文） | `audit/V1-FULL-AUDIT/logs/smoke-result-adjudication-20261112.log` | `fe652ee0be6472b09104a9ab9344d7873eebb653` | `80D76C98750A29E2EC254B71523AC9FACF4611E47609B8E7C0CB3673D8054123` | CANONICAL | BLOB |
| SMOKE-RESULT-1 | AC2/AC3（smoke 分项结果、阻断与证据边界） | `audit/V1-FULL-AUDIT/reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md` | `82603ae84e09fdd77d41489c3697124023c9be55` | `81B69C26DC83BB2BB38E9F1AFF157002E37FC825D2E142F8B0A1DB648C2A486C` | CANONICAL | BLOB |
| GOVERNANCE-RESULT-1 | AC4（default governance runner 结果与最终 gate 限制） | `audit/V1-FULL-AUDIT/reports/GOVERNANCE-RESULT-SEGMENT-B-2026-11-12.md` | `6d40dbc060ed591941b8b6966d73ff9f24afd8d6` | `2DF67291FAB4E38ABF07F1008212DD4F52545DC3D0E618A961457C6FFAD7F97D` | CANONICAL | BLOB |
| GOVERNANCE-JSON-1 | AC4（governance runner argv/HEAD/EXIT，默认 check EXIT 0） | `audit/V1-FULL-AUDIT/evidence/governance-segment-b-20261112T085303591759Z.json` | `1e9c15344e5ad766c0809c9b0e569da9cd9baeb8` | `5CF175527541E915E49DF6A30C92B41D5AF0BB87AEFB02A75222A4A1934599CB` | CANONICAL | BLOB |
| GOVERNANCE-LOG-1 | AC4（governance 原始输出、生成 HEAD 与 EXIT） | `audit/V1-FULL-AUDIT/logs/governance-segment-b-20261112T085303591759Z.log` | `1e9c15344e5ad766c0809c9b0e569da9cd9baeb8` | `D37B62A1916101AE59B56EE041E8769C8105560070BB784E0EA64C2F009ED557` | CANONICAL | BLOB |

说明：裁决文档中记录的阶段 0 日志 `B561…` 是提交前 WORKTREE SHA-256；本表按模板使用 Git BLOB 字节，完整 SHA-256 为 `7E2A…`。

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | — | evidence/baseline.json | 主工作区，不创建/移除worktree |
| task-env | G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT | PRESERVE_REFERENCED | — | audit/V1-FULL-AUDIT | 隔离数据库/构建/临时数据，未授权删除 |
| artifact | audit/V1-FULL-AUDIT | PRESERVE_REFERENCED | — | evidence/ | 审计交付物保留 |
| dataset/model/test-material | — | NOT_APPLICABLE | — | — | 不获取私有漫画/新模型 |
| exchange | — | NOT_APPLICABLE | — | — | 无外部传输 |

## Rolling checkpoint
[audit/V1-FULL-AUDIT/AUDIT_RESUME.md](../../audit/V1-FULL-AUDIT/AUDIT_RESUME.md)。Reviewer 已指定为 ZCode 新独立上下文；checkpoint `499a6b8e6eb293487abf391c46d00263230940ad` 的 `PASS_FOR_CHECKPOINT` 经 addendum 维持，R-1/R-2/R-3 已 CLOSED、R-4 保持 observation（详见原 Review 与 addendum 报告）。此结论不等于全审批准或 Task 关闭；最终治理门禁、全审 review 与集成验证仍待完成，保持 `in_progress`。

## 2026-10-24 推送准备补充授权

用户同意上一轮推荐下一步：Codex 整理审计登记、同步台账，并离线检查 `origin/main..main` 的凭据与材料来源，形成固定 SHA 的推送清单。本补充仅增加 `doc/TASK_LEDGER.md` 的生成同步范围；扫描脚本、报告和证据沿用本 Task 的 audit 路径。不授权 push、历史重写、删除或业务实现，不将本 Task 置 done。

检查基线：`origin/main=6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`、`main=349e61faff5f93067af5d4ce2d9e394e0d665b8c`。两份治理文档的在途修改属于本审计登记；6 个 `verification/P04/diagnostic_p22_*.jsonl` 在审计前已存在，具体生成者未证实，原位保留且不暂存。检查结果见 `audit/V1-FULL-AUDIT/reports/PUSH_READINESS.md`；此记录不替代独立审查。

## 2026-10-24 材料来源复核与差异证据

用户“下一步”授权继续已有推送准备的只读材料核验；不扩大业务或远端权限。按该调查实际需要读取 T1.1.1 的样本 manifest/生成脚本（固定 `ed607b755`）、真实素材记录和 M2-AC1 的合成 fixture 代码；只追溯历史材料，不运行 Legacy 产品诊断/修复。

Codex 记录：`.tmp.driveupload` 中存在169个JPEG，文件名集合、页数和1350×1920尺寸与 `verification/T1.1.1/author-verification.md` §6 和 `real-material/results.json` 完全吻合；但原记录无逐页hash，不能宣称已完成精确同源证明。该文档同时声明“版权像素不入库”，与临时压缩对象夹带图像的事实形成需处置的文档/实现差异；不改写旧证据来消除此差异。4个PNG与历史合成样本manifest精确匹配。详见 `audit/V1-FULL-AUDIT/reports/MATERIAL_CLEARANCE.md` 及 `evidence/push-material-inspection.json`。

34份SQLite主文件使用隔离原字节副本进行immutable只读检查，主文件hash保持不变；12份业务库与M2-AC1合成页hash匹配、5份P18业务库书架/章节/页面为空。发现22个本地路径单元格，未输出记录原文。不能由此证明缺失WAL/删除页无隐私内容，也不签发完整隐私清白结论。推送阻断仍为材料来源/传播许可待证明；已询问用户是否存在原始来源/许可记录，尚未据此获得上传或历史重写授权。

## 2026-10-24 用户材料处置裁决（当前有效）

用户对169张JPEG明确回复：“我自己的，但是不传播”。记录为用户本地持有/提供的素材，**禁止传播**，不推断用户拥有作品著作权，也不登记为可上传许可。该裁决取代此前“等待传播许可资料”的运行分支，不再默认要求用户补许可来放行完整历史。所有169个JPEG及其压缩外层blob均列为禁止上传项；本地对象、原件、旧证据及refs保持原位。

当前main及3个分批候选均包含这些外层blob，不能推送这些历史。后续推荐独立干净源码快照，须先明确目标分支/发布范围并释放Task；本裁决不授权删除、改写历史、实施新发布方案或push。具体裁决和对象指纹见 `audit/V1-FULL-AUDIT/evidence/push-material-disposition.json`。

2026-10-24 后续用户“下一步”授权本地快照准备，已独立冻结为GIT-CLEAN-PUBLICATION-1。完整历史上传因用户禁止传播素材而blocked；主控当前只执行新Task。全审其他AC/独立Review未完成，不置done、不把快照测试算成全审PASS；恢复全审时从in_progress续接，原证据保持原位。

## 2026-10-25 DSH 接管后的效力

DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 保持 `blocked`、`resume_status: in_progress`；Owner/审计作者仍为 Codex，不伪造独立审批。用户“169 张 JPEG 私有、不传播”的裁决不变：禁止推送包含这些字节的完整 main 历史，禁止把它们纳入任何待推对象。

本 Task 不因 DSH 接管自动恢复；重新启动需 DSH 明确范围冻结与独立 Reviewer Appointment。干净快照 push 的独立审查可复用本 Task 的材料隔离结论，但不得据此宣称全审完成或产品发布通过。

## 2026-11-12 ZCode 受托裁决与段 B 解封

本节依用户当前授权“持续推进、全部授权；裁决交给 ZCode”及 ZCode 独立 CLI 裁决记录生效；范围摘要与阶段 0 本地核验见 Canonical Evidence 所 pin 的 `ZCODE-SCOPE-ADJUDICATION-2026-11-12.md` 和日志。

- **状态/范围**：`blocked` 恢复为 `in_progress`。段 A 固定于 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`，既有结果保留为历史；段 B 固定于 `10e4ee013835605800d3830fb960ae8d3aa04167`，AUDIT-00–14 需按当前产品重新核验。段 B 的 AUDIT-00 从 `NOT_RUN` 起，不继承段 A 的 PASS；AUDIT-01–14 保持 `NOT_TESTED`。
- **材料边界**：本地只读审计可继续；169 张 JPEG 及含其内容的对象不得复制、导出、展示、上传或 push。素材内容级访问、OCR/视觉输出和真实本地路径披露均为停止条件。
- **传播风险**：本地 `origin/main` reflog 与仓库文档支持私有素材对象曾随 2026-10-30 main push 进入公开仓库历史的高置信推论；详见裁决记录。当前远端实时可见性、外部可 fetch 状态及远端缓存均未实测。此 Task 不执行远端补救，不 push、不删分支、不改写历史、不 GC/prune。
- **Owner / Reviewer**：Owner=Codex。Reviewer=ZCode 的新独立上下文，仅在审计交付后 Review；不得参与段 B 实施。Review 绑定最终 `reviewed_head`，记录 reviewer 新 session 身份。
- **允许路径与 stop conditions**：沿用 frontmatter 原 `allowed_paths`。如需产品代码、测试、冻结契约、Schema、依赖改动，或治理修复越出允许路径，停止并新建/释放 Task；不得把 NOT_TESTED/NOT_RUN 写成 PASS。
- **阶段 0 结果**：HEAD 精确为段 B base，branch=`main`，工作树 clean；`87f61d8…`、`349e61…` 均是 HEAD 祖先，`349e61…..HEAD` 为 2,366 commits；所有相关 ancestry EXIT=0。细节和未实测项见日志。
