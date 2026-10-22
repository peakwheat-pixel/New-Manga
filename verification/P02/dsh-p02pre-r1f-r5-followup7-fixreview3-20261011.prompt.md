# P02PRE-R1F — R1F-R7 修订后第 3 轮独立只读 Review

## 角色与基线

你是 DeepSeek Harness 非作者 Reviewer。Owner/Author/Integrator/Adjudicator 为 Codex /root。仓库：`G:/CODEX/New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。宿主编排 PowerShell=`7.6.6`；R1F 已冻结的 parser/capture executor 是 Windows PowerShell `5.1.26100.9549`。当前只证明 exact candidate 在 5.1 下 parse-only 成功；项目证据没有证明 PowerShell 7 不兼容。请核验文档表述是否一致，不要自行改变已冻结执行器。

这是本轮独立复审的 exact source set（bytes / SHA-256）：

- `AGENTS.md`: 4503 / `46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501`
- `doc/09_COLLABORATION.md`: 19131 / `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D`
- `doc/tasks/P02PRE-R1F.md`: 25471 / `1FF2C8D28F12BACE3D67F2A997B0E8776F7ADB81F54CE2E20EFFB368391031FD`
- `verification/P02/p02pre-r1f-manifest-20261011.md`: 35467 / `7A1BBC504D7E2B908EEEFCBD35657CC25C5916F74FD58E1012B74128A1DFFB2A`
- `doc/REBASELINE_PLAN.md`: 276655 / `CC962BF71421030CAB9CDE259713E28DC27E1528D16533E7348F5B019A51B4A0`
- `doc/STATUS.md`: 285619 / `278247E29F401CC33EE3EB8DC294F5CD059CB1FF00FEAAF0DFC6906E8ABB2611`
- `doc/00_INDEX.md`: 57061 / `74E5B02A01A41288FC3DD58F7FF14018A9B591AD8E42E7EDFAB1F4B14C432F26`
- `doc/tasks/README.md`: 36547 / `175A96C846B5BEED306E50B34286F712B68D3749539AD1DFF1A3952FD549F3D6`
- `doc/tasks/P02.md`: 222209 / `F2D17604D7838E604568F17B5663CEF2E52E81C1FB139A1C47BE49E63902FD34`
- `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md`: 22351 / `7C3B79A130D888017D2E527928553BCE2F0B441CDC452E4C8EAA874810F4C080`
- Frozen capture candidate `verification/P02/p02pre-r1f-capture.ps1`: 67582 / `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316`
- R8 parse-only evidence `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`: 2595 / `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696`

文档冻结前的 pre-prompt Git status（pathspec 排除 `.tmp.driveupload`）= 755 NUL records / 48392 bytes / SHA-256 `5F145B2744E99524F574235B6775A526917A15DA6522AE68FF63A865B3907D4F`，exit 0、stderr 0、连续两次相同；main index SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。本 prompt 是该 snapshot 之后新建的唯一 status artifact，因此当前受控 status 预期为 756 records；final pre-run 前必须重新测量。工作区已有大量其他 dirty/untracked 内容且归属未知，必须原样保留。

## 只读审查范围

只审查上述冻结文件以及下列既有 Review evidence。可进行这些命名文件的只读读取和本地 SHA-256 核验。不要修改/创建/删除仓库文件，不切换 branch/worktree，不读 `.tmp.driveupload` 或其他用户内容，不调用 host getter、AppContainer/profile、registry/ACL API、capture、Build/Cargo、AC1–AC7、Windows feature/Sandbox 或任何系统状态变更。不要释放任何 Gate。

重点核验：

1. Task、manifest、唯一 DAG（REBASELINE_PLAN）、STATUS、索引、Task README、P02 导航和 rolling checkpoint 的 Active Task、依赖、Review 历史、下一步、状态与路径是否一致；状态文案是否把计划/未执行项误写为 PASS/DONE。
2. manifest 的 pre-capture checklist 是否逐项准确：首轮、修复轮、follow-up #2 的 prompt/stdout/stderr/exit/adjudication 均为 FROZEN 且 pins 正确；follow-up #3 的五个精确输出路径仍为 PLANNED；Task allowed/write paths 与它们一致。PLANNED 仍是 final pre-run 的阻塞条件。
3. Codex 三份 adjudication 是否与对应冻结 prompt、原始 DSH stdout/stderr/exit 相符。特别独立核对 follow-up #2 的 P3-1：DSH 报告声称 exact 当前 prompt 把修复轮 exit pin 误写为首轮值；检查该 exact prompt 与 raw DSH tool result 是否真的含有该字段，再判断 Codex 的 `REJECTED_AS_MISATTRIBUTED` 是否有证据。不要只重复任何一方的总结。
4. Review pins、Task/manifest/Plan 文档中的文件尺寸与 SHA-256、status snapshot 和 checkpoint pins 是否互相对应；若 Reviewer 无法独立读取或复算某项，明确标 `UNVERIFIED`，不得猜测。
5. 是否有任何文档误称 PowerShell 7 不兼容，或将 5.1 parse-only 误当成 capture、安全 Gate 或 Build Gate 通过。
6. Owner risk waiver 的五个状态及精确原句是否保持一致：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`。Build Gate 应仍为 `BLOCKED`，Hard Build Barrier=`EFFECTIVE`，Build/Cargo=`NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`，capture=`BLOCKED / NOT_RUN`。

## 必须检查的历史 Review cohort

- R1F-R7 首轮：`verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.prompt.md` (3563 / `9CE41DAEEB7BED5C4B0D812A9E66DF6781DC988F51096BC2B7161F92EA04ACC2`)，stdout (203071 / `E72F8B4CD8AF9513785DB3776A94DC17559DF052A0E9828AC1869331A8F5D4BB`)，stderr (0 / `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`)，exit (2 / `9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA`)，adjudication (4965 / `69B7592A03C9863309EA4168A665F1BFD88D6A28D05D9A62AF2FBE2EADB4359B`)。
- 修复轮：`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.prompt.md` (5802 / `2D25B7F91429957391CF0151CBBE3ECD5F4F5F04A5A423C2D15A70E84067876B`)，stdout (127548 / `F63AC2FDF21A0A5F7133869CE1080B4DD269B0BB8512694BBE11C2BAFC6EE25C`)，stderr (0 / `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`)，exit (3 / `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`)，adjudication (4461 / `51DB906C541D949296F36458C6B0461E0EAAA269A1ABCD9C9C7B1427C96399F8`)。
- follow-up #2：`verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.prompt.md` (5726 / `50E73237B7441DE2B3A4EBE9FC7B800FB511E930B18600880041BC95C83AEBA5`)，stdout (100209 / `F646928900746BB7E2F99E179734015FA317E6D232E50283CB2423A0382421FA`)，stderr (0 / `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`)，exit (3 / `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`)，adjudication (3401 / `4D74A2AAB9661244DFFF9AEAD04248D427D3215A7C5FA293FB2AE54E498508C0`)。

## 输出格式

在本 session 返回：

```
VERDICT: APPROVED | CHANGES_REQUESTED
P0/P1/P2/P3 counts:
Findings (each with exact file/line or JSONL location, observed bytes/hash, why it matters, minimal fix):
Unverified items:
Gate impact: REVIEW ONLY; capture/build/AC remain unreleased.
```

只要有未解决 P0/P1/P2，或影响状态/pin/权限准确性的 P3，就用 `CHANGES_REQUESTED`。不要更改文件；让 Codex 负责 adjudication、修订、重新派发或释放后续步骤。

