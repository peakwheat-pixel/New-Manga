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
- [ ] AC2：15项专项逐项有真实检查结果或具名阻断，关键链路深读与测试。 <<PARTIAL: 原始 AUDIT-00–14 清单已恢复并由 ZCode 映射至 AD-002；AUDIT-00 当前仅基线/源码清单范围 PASS，补充盘点待完成；AUDIT-01–14 均为 NOT_TESTED。既有 suite 结果仅作背景证据：probes EXIT 1（2 项 Medium / High confidence，1 项 defense-verified）；Python Core pytest EXIT 1（3,519 passed / 16 failed / 10 skipped）；Avalonia .NET BLOCKED-TESTHOST-ACCESS（8/8 runner EXIT 1、TRX 0 tests）；smoke EXIT 1（Wire 6/6 PASS，Core 4 PASS / 7 BLOCKED-SANDBOX-GRANT，frontend/packaged SKIP）>>
- [ ] AC3：完整日志、问题分级、整改路线、正式报告和Release Gate落盘。 <<PARTIAL: 已有 probes 分级、pytest 失败摘要、TestHost/sandbox 阻断和治理门禁记录；专项报告、去重问题台账、整改计划、正式报告及 Release Gate 尚未完成>>
- [ ] AC4：独立复核、证据pin和治理检查可核验；未满足不得置done。 <<PARTIAL: ZCode checkpoint review @453327ff1 为 PASS_FOR_CHECKPOINT（0 P0/0 P1），原件恢复、范围裁决与当前阶段治理证据已 pin；最终全审 Review、交付 HEAD 独立复核与集成验证未完成>>

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
| ZCODE-REVIEW-REPORT-1 | AC4（checkpoint 独立 Review 报告，结论 `PASS_FOR_CHECKPOINT`） | `audit/V1-FULL-AUDIT/reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md` | `f8feb02ca2a2c8ddf5a775066433f6db889c4e64` | `5B5E37E2C4E498905288A180599746336829CEB0E4323C3894D2C1799C9CE46A` | CANONICAL | BLOB |
| ZCODE-REVIEW-LOG-1 | AC4（ZCode 首轮独立 Review 原始 CLI 记录） | `audit/V1-FULL-AUDIT/logs/zcode-checkpoint-review-20261112.log` | `16c468060a18b795ba8c78bcb52eedbb2ef183ef` | `3C340D4CE6BF43B2ED433CC5909F0E82645D5E01C065164F8B818F4E914C3AD3` | CANONICAL | BLOB |
| ZCODE-REVIEW-FINDINGS-LOG-1 | AC4（ZCode Review findings 原始记录） | `audit/V1-FULL-AUDIT/logs/zcode-checkpoint-review-findings-20261112.log` | `16c468060a18b795ba8c78bcb52eedbb2ef183ef` | `B0B9E5B573EDF13BDBC81F64AC7A347E95B37C73CD951B8160D0E4058ECD90C4` | CANONICAL | BLOB |
| REVIEW-RECHECK-LOG-1 | AC4（37 路径与 46 pins 只读补验，EXIT 0；经 ZCode 接受为 R-1 closure evidence） | `audit/V1-FULL-AUDIT/logs/review-checkpoint-recheck-20261112.log` | `16c468060a18b795ba8c78bcb52eedbb2ef183ef` | `4DC1E678761B8D171CFA2539DBC544ECD3BEC9AF6B7ACA97BA21161842E09254` | CANONICAL | BLOB |
| ZCODE-REVIEW-ADDENDUM-REPORT-1 | AC4（ZCode addendum 报告：R-1/R-2/R-3 CLOSED，R-4 observation） | `audit/V1-FULL-AUDIT/reports/ZCODE-CHECKPOINT-REVIEW-ADDENDUM-2026-11-12.md` | `405f82e30a349e210e97053356aa110e9f7dc4ee` | `EE22A68E509FA392F1CC7AC7D49F0085C6DEDCAD8882A6693CA0D5D2481AB6EF` | CANONICAL | BLOB |
| ZCODE-REVIEW-ADDENDUM-LOG-1 | AC4（ZCode addendum 原始 CLI 记录，EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-checkpoint-review-addendum-20261112.log` | `90d26381616e58bf94acd42827002d4b5774e3d0` | `ADC51C34780CA3E940F7CDD013768E20E09588D92A820F97067FBCA994CDCF94` | CANONICAL | BLOB |
| ZCODE-FINAL-REVIEW-REPORT-1 | AC4（ZCode 最终 checkpoint review 报告，`PASS_FOR_CHECKPOINT`；F-1/F-2/F-3） | `audit/V1-FULL-AUDIT/reports/ZCODE-FINAL-CHECKPOINT-REVIEW-2026-11-12.md` | `75e3aefb2c35c276086fad50ece70421a67fbb53` | `F599F694A5DCDBAE870FF9DBBB00E9C0CC2ECD099602900666F11742ECF58950` | CANONICAL | BLOB |
| ZCODE-FINAL-REVIEW-LOG-1 | AC4（ZCode 最终 checkpoint review 原始 CLI 输出、session/turn/trace、EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-final-audit-review-20261112.log` | `75e3aefb2c35c276086fad50ece70421a67fbb53` | `FB437BDB78B69C80572BEC37B104FB91EDEADA15A02DF328F5F176B337C7D1A0` | CANONICAL | BLOB |
| REVIEW-FINAL-INTEGRITY-LOG-1 | AC4（两段 diff 路径范围与 52 行 BLOB SHA-256 复算，reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225`，EXIT 0） | `audit/V1-FULL-AUDIT/logs/review-final-integrity-20261112.log` | `b9b6c5801060370eb4171c30eb77a935800e2f6f` | `7226A48417184636F92611599BDCB5385BA97584D1A356C09ACF22DD3E6CC4A3` | CANONICAL | BLOB |
| FINAL-GOVERNANCE-GATES-1 | AC4（default/TaskPath governance、18 pins、API inventory 完整输出；4 项 EXIT 0） | `audit/V1-FULL-AUDIT/logs/final-governance-gates-20261112.log` | `9f41ddf4b8b6e4fe147c7c06b742637166e342cb` | `6E40CDFEB73C35FE221328163595F3BFDC86DE8AF87ABD3C17D2B9489FC43F7F` | CANONICAL | BLOB |
| POSTREVIEW-FINAL-VERIFICATION-1 | AC4（generated HEAD=`ac188dde5`：default/TaskPath、18 pins、API inventory 与 56 行 Task pin 逐项复算；全部 EXIT 0） | `audit/V1-FULL-AUDIT/logs/postreview-final-verification-20261112.log` | `6dc3d634da0bd6c4083509c50d99a0bc0efb4742` | `6E900FF4F6F367EA1EA6B6B6F5452F0A9186618EE767D03754C0D0F6B3EC528A` | CANONICAL | BLOB |
| ZCODE-FINAL-REVIEW-ADDENDUM-REPORT-1 | AC4（ZCode checkpoint addendum：F-1/F-2/F-3 CLOSED，R-4 observation；`PASS_FOR_CHECKPOINT`） | `audit/V1-FULL-AUDIT/reports/ZCODE-FINAL-REVIEW-ADDENDUM-2026-11-12.md` | `b17fead6d2cbbd2324ffb0a85096eb50448050ff` | `90C4B6743683A77F78CC5B84C74887BF86DBAD12EA3A5E4D38DC93FA2D5DC22A` | CANONICAL | BLOB |
| ZCODE-FINAL-REVIEW-ADDENDUM-LOG-1 | AC4（ZCode addendum 原始 CLI 输出、session/turn/trace 与 EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-final-review-addendum-20261112.log` | `b17fead6d2cbbd2324ffb0a85096eb50448050ff` | `A50F9CA3520923A88628494DABB59146E61E27CF32C367F3652C6B308E9B9C0A` | CANONICAL | BLOB |
| POSTADDENDUM-INTEGRITY-LOG-1 | AC4（generated HEAD=`b17fead6`、reviewed_head=`d9478939`：11/11 diff 路径 allowed、57/57 既有 pin 匹配，EXIT 0） | `audit/V1-FULL-AUDIT/logs/postaddendum-integrity-20261112.log` | `0588e024ef9364dedae91231623b6b92b141e9b1` | `B34B332CC6C7DB315531EC963E0930F27D8BD1F2FF7C5DE0F67A3EBDE0C2BAE1` | CANONICAL | BLOB |
| ZCODE-CURRENT-HEAD-REVIEW-REPORT-1 | AC4（ZCode fresh checkpoint review of `453327ff1`: `PASS_FOR_CHECKPOINT`, 0 P0/0 P1; N-1/N-2 P3, N-3/R-4 observations） | `audit/V1-FULL-AUDIT/reports/ZCODE-CURRENT-HEAD-CHECKPOINT-REVIEW-2026-11-12.md` | `172bca13396d27cd8af7b39d1d675e516f422332` | `53E5DE691819A7923ADA31564430E99DAF346F2E15645E49E6CE54FEB0B2BCC8` | CANONICAL | BLOB |
| ZCODE-CURRENT-HEAD-REVIEW-LOG-1 | AC4（reviewed_head=`453327ff1` 的原始 ZCode CLI JSON、session/turn/trace 与 EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-current-head-checkpoint-review-20261112.log` | `172bca13396d27cd8af7b39d1d675e516f422332` | `63589140BB8147C61DC4EAC9CF2EA0BEF3D01D0BFDB215ADA4AC23768FBECBA8` | CANONICAL | BLOB |
| FINAL-POST-PINBACKFILL-GATES-1 | AC4（generated HEAD=`453327ff1`：default/TaskPath governance、18 pins、API inventory 四项 EXIT 0，含命令/UTC/输出） | `audit/V1-FULL-AUDIT/logs/final-post-pinbackfill-gates-20261112.log` | `172bca13396d27cd8af7b39d1d675e516f422332` | `E7D19C884D2EB94326649946BC855C134DF147885C91C37FC72E812A097CF0B0` | CANONICAL | BLOB |
| ZCODE-LIFECYCLE-ADJUDICATION-REPORT-1 | AC4（初次生命周期裁决摘要；明确标记 SUPERSEDED，不能作为关闭依据） | `audit/V1-FULL-AUDIT/reports/ZCODE-LIFECYCLE-ADJUDICATION-2026-11-12.md` | `a04a3e9ac314ec136d243551c3a6f0d892e558db` | `C1AC2F481BA4C00D0B8405158B458DB3FA50A6D2DC920384E9A78BD914DF4DCE` | CANONICAL | BLOB |
| ZCODE-LIFECYCLE-ADJUDICATION-LOG-1 | AC4（初次 ZCode 生命周期裁决原始 CLI JSON，EXIT 0；已由更正版撤回） | `audit/V1-FULL-AUDIT/logs/zcode-lifecycle-adjudication-20261112.log` | `a04a3e9ac314ec136d243551c3a6f0d892e558db` | `4961EC24F3B609936013D63C7A7B350EBF30F2B710F4F115D55512B0A583C1E6` | CANONICAL | BLOB |
| ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-REPORT-1 | AC4（更正后最终生命周期裁决：Task 保持 in_progress，等待用户明确接受限制） | `audit/V1-FULL-AUDIT/reports/ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-2026-11-12.md` | `a04a3e9ac314ec136d243551c3a6f0d892e558db` | `E88623C6B4324A6028B6B0F11487BE9A48F2805BC34E22A621A024DB2F95073A` | CANONICAL | BLOB |
| ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-LOG-1 | AC4（更正后 ZCode 原始 CLI JSON、turn/trace 与 EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-lifecycle-adjudication-correction-20261112.log` | `a04a3e9ac314ec136d243551c3a6f0d892e558db` | `65865C8B42F5CED9706B0D2947611EE3B05522525A4345D15E4CBB5A4D24F9A7` | CANONICAL | BLOB |
| ORIGINAL-CHECKLIST-GIT-HISTORY-SEARCH-1 | AC2/AC4（Task 可达 Git 历史与定向 `-S` 搜索；最早 Task blob 无 AUDIT-01–14 逐项定义，EXIT 0） | `audit/V1-FULL-AUDIT/logs/original-checklist-git-history-search-20261112.log` | `d530a59662d0b2ca00496c854e84fe8885818d8e` | `6D3231499855929973CA108818A05B17A30F319D35A13681718FB4741074AA85` | CANONICAL | BLOB |
| ORIGINAL-INSTRUCTIONS-SOURCE-1 | AC2（用户原始 AUDIT-00–14 指令；附件恢复，源 SHA-256 与 Git blob 一致） | `audit/V1-FULL-AUDIT/source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt` | `033c3cf1af0e00e34172224c37a6c841277333bb` | `3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF` | SOURCE_PIN | BLOB |
| ORIGINAL-INSTRUCTIONS-RECOVERY-REPORT-1 | AC2（附件来源、完整性及恢复边界） | `audit/V1-FULL-AUDIT/reports/ORIGINAL-USER-AUDIT-SCOPE-RECOVERY-2026-11-12.md` | `033c3cf1af0e00e34172224c37a6c841277333bb` | `457469AE93513E7AA6C45146E4954D573175AC4FC8120EAD929C804E4DA1721B` | CANONICAL | BLOB |
| ORIGINAL-INSTRUCTIONS-RECOVERY-LOG-1 | AC2（原附件复制、长度和 SHA-256 对照，EXIT 0） | `audit/V1-FULL-AUDIT/logs/original-instructions-recovery-20261112.log` | `033c3cf1af0e00e34172224c37a6c841277333bb` | `1ED5DD8C99046E3860448FE245F1CD4AAE9F4BB7248B77539444108BABA046C8` | CANONICAL | BLOB |
| ORIGINAL-INSTRUCTIONS-PRESERVATION-LOG-1 | AC2（恢复源文件原字节、index blob 与 Git 配置保留，EXIT 0） | `audit/V1-FULL-AUDIT/logs/original-instructions-stage-preservation-20261112.log` | `033c3cf1af0e00e34172224c37a6c841277333bb` | `86D7C713DD3D37B0346DC1A8A341C858CF358C5A55AE86258D6D13B09CA376D0` | CANONICAL | BLOB |
| ZCODE-ORIGINAL-SCOPE-ADJUDICATION-1 | AC2（原件恢复后的范围/生命周期裁决；AUDIT-01–14 设为 NOT_TESTED） | `audit/V1-FULL-AUDIT/reports/ZCODE-ORIGINAL-SCOPE-READJUDICATION-2026-11-12.md` | `5f88bbcb643cf368536b10010677e1664d5082b5` | `88AE184FE04E2951BFE5D7D2FCA8E1A95145037146950B333CBC261282192578` | CANONICAL | BLOB |
| ZCODE-ORIGINAL-SCOPE-LOG-1 | AC2（ZCode CLI envelope/session/turn/trace、EXIT 与独立原件复核） | `audit/V1-FULL-AUDIT/logs/zcode-original-scope-readjudication-20261112.log` | `5f88bbcb643cf368536b10010677e1664d5082b5` | `B2A6658E58BDA4F75C95A1EB151811C709BF471B26D0CD7DA29A746144053995` | CANONICAL | BLOB |
| ZCODE-ORIGINAL-SCOPE-GATES-1 | AC4（裁决证据提交前 default/TaskPath/pins/API 检查；generated HEAD=`033c3cf1`，四项 EXIT 0） | `audit/V1-FULL-AUDIT/logs/zcode-readjudication-gates-20261112.log` | `5f88bbcb643cf368536b10010677e1664d5082b5` | `BE9DB4795773E6C8C1D0010EBFE12A943147044822B5EC37174EA8452DAF06E2` | CANONICAL | BLOB |
| SCOPE-POSTCOMMIT-GATES-1 | AC4（裁决证据提交后 default/TaskPath/pins/API 复核；generated HEAD=`5f88bbcb`，四项 EXIT 0） | `audit/V1-FULL-AUDIT/logs/gates-after-scope-adjudication-20261112.log` | `0f76e6a79` | `0D297905555BA98800FA7E8A1CF5FE9B4AE439D69A4083884738694ED5B6CE8D` | CANONICAL | BLOB |
| POST-SCOPE-RESET-GATES-1 | AC2/AC4（scope reset 提交后 default/TaskPath/pins/API 复核；generated HEAD=`2c6b15b067f9156b702c0b8058f0db18a85148d3`，四项 EXIT 0） | `audit/V1-FULL-AUDIT/logs/post-scope-reset-gates-20261112.log` | `92aca0cc34e288404871d5155664a657e34dc769` | `374D6D7197B92BB5988387E512DF7623EA66851E54424D5E81A5097199043446` | CANONICAL | BLOB |

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
[audit/V1-FULL-AUDIT/AUDIT_RESUME.md](../../audit/V1-FULL-AUDIT/AUDIT_RESUME.md)。ZCode 对 `499a6b8e6eb293487abf391c46d00263230940ad`、`d9478939f2cee81104f18ea757d81cec71c36225` 与 `453327ff19ea012026b76d2e10cdcf2c93c58038` 的 checkpoint 结论均为 `PASS_FOR_CHECKPOINT`。这些中间 Review 与门禁仍是有效历史证据，但不代表全审完成。原始指令附件已恢复，AUDIT-01–14 当前均为 `NOT_TESTED`；ZCode 原件恢复裁决、来源完整性及其门禁复核见 Canonical Evidence。Task 保持 `in_progress`，AC2/AC3/AC4 与最终集成验证未完成。

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

## 2026-11-12 ZCode 生命周期更正裁决（历史结论，已被原件恢复裁决取代）

- ZCode 初次裁决曾建议 `closed_with_limitations`，但其授权论证误把 Codex prompt 中的“选项 2”当成用户原话。ZCode 已无条件撤回该归因与状态建议；初次报告明确为 `SUPERSEDED`，不得作为关闭依据。
- 更正后的最终裁决：Task 保持 `in_progress`，不转 `in_review`，暂不执行 `closed_with_limitations`。依据 [协作协议 §4](../09_COLLABORATION.md) 的限制性关闭标准，用户委托 ZCode 和“免人工批准”授权不足以替代用户对本 Task 具体永久限制的明确接受。
- 实际用户授权原文为“持续推进，全部授权，自动计划，不需要用户介入，裁决交给zcode”“不需要人工批准，你自己批准”“额度已恢复，继续停止的任务”。不得将 Codex 的提示词选项归为用户选择。
- Task 自身 Git history 的定向核验见 Canonical Evidence `ORIGINAL-CHECKLIST-GIT-HISTORY-SEARCH-1`：可达历史最早 Task blob=`1248f2b8a` 只有通用 AC1–AC4 和 `AUDIT-00–14` 范围；对 Task 与 `audit/V1-FULL-AUDIT` 的 `AUDIT-14`/`15项专项` 历史搜索未找到逐项定义。它确认当前仓库可达历史中没有该清单，不证明仓外来源不存在。
- 历史状态：当时清单尚未恢复，ZCode 更正裁决要求等待用户对限制性关闭语义作具体取舍。附件恢复后，该等待条件与 `BLOCKED-ORIGINAL-CHECKLIST-MISSING` 状态均已过时；本节保留裁决历史，不再作为当前任务指令。

旧报告与原始记录见 `audit/V1-FULL-AUDIT/reports/ZCODE-LIFECYCLE-ADJUDICATION-2026-11-12.md`、`audit/V1-FULL-AUDIT/reports/ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-2026-11-12.md` 及既有 Canonical Evidence pins；它们仅作为历史依据保留。

## 2026-11-12 ZCode 原始范围恢复裁决（当前有效）

- 原始附件包含 AUDIT-00–14 全部专项、授权边界、结果/严重级别规则、报告交付物和完成条件；文件 SHA-256=`3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF`，与 Git blob 对应字节一致。来源、裁决与证据 commit 均列于 Canonical Evidence。
- AUDIT-01–14 从 `BLOCKED-ORIGINAL-CHECKLIST-MISSING` 纠正为 `NOT_TESTED`。既有 suite 结果与逐项结论分离；没有任何专项由本次范围裁决推断为 PASS。
- AUDIT-00 保留段 B baseline limited PASS；启动入口、后端 command 面、数据库 schema、模型/资源 pin 与结构图/模块索引仍需完成 `01_PROJECT_INVENTORY.md`。ZCode 回复提到的 command 数量尚未独立核实，最终清单以实际源码盘点为准。
- Task 维持 `in_progress`。此前“等待用户接受永久限制”的分支终止；按原任务授权继续审计，无需新增用户输入。Release Gate 仍 `BLOCKED`，AC2/AC3/AC4 仍 `PARTIAL`。
- 执行顺序：AUDIT-00 盘点；AUDIT-01 架构与 AUDIT-02 静态扫描；既有 suite→专项映射；AUDIT-11 安全静态；AUDIT-08 隔离数据库检查及 AUDIT-05/06 契约核对；AUDIT-14 覆盖/债务矩阵；AUDIT-03/04/07/10/13 的安全合成验证；最后补齐 `00–13` 与 `FINAL_AUDIT_REPORT.md`、问题台账、整改计划和 BLOCKED Release Gate。
- 继续遵守 `allowed_paths`、禁止业务修改与原始素材边界。真实 GUI、TestHost、sandbox grant、干净 Windows、付费 API 和私有素材内容检查分别记录为具名 `BLOCKED`/`NOT_RUN`，不得用替代证据冒充实测。
