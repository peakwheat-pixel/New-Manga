# P02PRE-R0S1 独立 Review 派发说明

你是 P02PRE-R0S1 的正式非作者 Reviewer（DeepSeek Harness）。Owner/Author 是 Codex `/root`，你没有编写本 Task、manifest 或 evidence。请只读审查本提示列出的已 pin 文档；不要修改文件、运行 PowerShell/OS/API/registry/ACL/path 查询、启动 capture、执行测试或尝试任何修复。

## 基线与审查对象 pins

- Repo=`G:/CODEX/New Manga`；branch=`main`；reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。工作树文件处于未提交状态，以下文件哈希而非 HEAD 绑定本次审查对象。
- `doc/tasks/P02PRE-R0S1.md` — `8303 bytes / BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD`
- `verification/P02/p02-readonly-preflight-r0s1-manifest-20261011.md` — `22925 bytes / CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3`
- `verification/P02/codex-checkpoint-p02-readonly-preflight-r0s1-20261011.md` — `7583 bytes / EE26F209B56F5A249B5BED9BFE9E5E54A6FEDBBE062F292A2F3032D66C63AEDB`
- `verification/P02/p02-readonly-preflight-r0s1-evidence-20261011.md` — `5489 bytes / 05C2DD247D3B0238809DCB90E62B633AAD6B4E777186E4025CD371B371F3FCBD`
- 背景仅供比对：`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` — `99592 bytes / AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`；`verification/P02/p02-readonly-preflight-r0-review-20261011.md` — `29404 bytes / 427F582D87A54E8C5B7CB65FB72F1B067BD226B8E6DFA66873FDC996E6B5C554`；`verification/P02/codex-p02pre-r0-adjudication-20261011.md` — `11145 bytes / E66131960E35A35C8E6F051EFE0F1C167CEBE2DBC78D849DA00A2642D901375E`。

## 必须核对的事项

1. 对照冻结 Task/manifest/checkpoint，判断唯一 runner、停止边界、目标路径范围及用户批准的只读范围是否一致；指出任何 scope creep 或错误的安全保证。
2. 将原始 stdout、退出码、capture PID、identity/SID/thread-token 字段与 manifest 的分支控制流对照。明确区分“shell 已启动并安全停止”与 `NOT_RUN`，不要因 `RUN_EXIT=0` 宣称采集成功。
3. 判断“Management/Utility 模块路径为空”是否只支持当前 runner 的模块可信前置条件未满足，以及是否能推断模块文件缺失或任一 scratch path 的存在/内容。两个 scratch leaf 未查询、未枚举；不得给其状态 `PASS_WITH_EVIDENCE` 或 `FAILED`。
4. 审查本 evidence 的五类分类：模块继续执行前提=`NOT_SAFE_FOR_R0`；L1/L2 empty-or-absent=`UNPROVABLE`；精确时间与 shell startup/profile effects=`UNPROVABLE`。如有分类错误，给出最小修正建议。
5. 核对 evidence 是否如实披露 stderr/精确时间戳不可用、`login=false` 不等于已证明 `-NoProfile`，且没有把未观察到写入扩大为全局无副作用证明。
6. 确认其未改变风险 waiver，也没有对 P02PRE/Technical Gate/Build Gate/Hard Build Barrier/AC1–AC7 产生 PASS 或放行效力。

## 输出格式

请用简体中文输出一份独立 Review，至少包含：metadata（task/author/reviewer/reviewed HEAD 和文档 pins）、范围与限制、逐项审查结论、findings（ID、级别 P0–P3、对象/证据、影响、建议、状态；若无问题明确写“在审查范围内未发现问题”）、验证表（只读文档审查；所有未执行 OS 检查标 `NOT_RUN`，并说明原因）、决定和剩余风险。

决定限定为 `APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`、`CHANGES_REQUESTED` 或 `BLOCKED`。批准只能表示这份有限证据交付可被 Codex adjudicate，不能表示 scratch 条件通过或任何 Gate 通过。对工作树对象哈希/HEAD、进程启动副作用或 OS 状态，若你没有独立证据，应明确写未核验，不得猜测。Codex 会独立 adjudicate，不以本 Review 代替其职责。
