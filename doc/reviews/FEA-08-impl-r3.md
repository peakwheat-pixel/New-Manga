---
task_id: FEA-08
reviewer: "Codex，impl-r3 独立新会话 01a19f7a-fa86-7171-993d-a40713a5f168（/root；未参与 R3 实现）"
reviewer_kind: agent
author: "DSH（Lead/Integrator，R3 直接实施）"
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: f4846031620e44adfcdcae026039abc7e2494201
implementation_commit: f7f00848f
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 0
p2: 5
provenance:
  head_delta: "0；开始与定稿均为 f4846031620e44adfcdcae026039abc7e2494201"
  isolated_evidence_dir: "G:/CODEX/New Manga.workspace/FEA-08/impl-r3-review-codex-20261103-1136"
  repository_write_scope: "仅 doc/reviews/FEA-08-impl-r3.md；不提交、不 push"
  assisting_reviewers:
    - "Reviewer /root/h6_review；01a19f7b-ad56-7232-af23-e9b5af404583；独立上下文，只读原件"
    - "Reviewer /root/matrix_transaction_review；01a19f7b-d5f9-7831-ab3b-d47b397f4b83；独立上下文，只读原件"
  uncovered:
    - "USB/SMB/Cloud 真卷、真实用户取消、IFileOperation per-item sink、AES ZIP 新依赖：维持原 LIMITED/未测边界"
    - "未模拟 process kill/断电/回滚再次 I/O 失败/并发读者；晋升故障为隔离 OSError 注入"
    - "未运行真实全链 run_all；实际 H4/H5/H6 各自隔离复跑，事务用 fake-repo/stub 逐阶段注入"
---

# FEA-08 impl-r3 独立 Review

## 结论

**changes_requested；P0=0 / P1=0 / P2=5。** R2 的三个危险 P1 反例已不再误通过：67 项 pin 完整成立，异尺寸同像素不会 exact，重复同图且无身份锚的容器返回需确认。R3 的一般步骤失败已能回滚；但晋升本身失败及最终自日志失败仍破坏 Canonical 完整性，H5 的必要语义证据失败也仍可生成 PASS。另有唯一内容改名的误拒，以及门禁日志元数据遗漏。不能据此登记“R2 findings 全部闭合”或直接关闭 Task。

本报告采用仓库 REVIEW 模板的 Standards / Spec / Architecture / Verification 四个视角，均 executed。两名辅助 Reviewer 只承担本次审查，无人参与实现/返修；主 Reviewer核验其脚本、原始输出、结果与被审代码后承担汇总结论。未修改 Task/Handoff/证据/STATUS/PLAN。

## 范围与依据

- 固定点：`base=2870a9fa5`；`reviewed_head=f48460316`；R3 实施交付 `f7f00848f`，登记 `f48460316`；R2 `7b176be6a`。全程 main，common directory `.git`；head_delta=0。
- 当前依据：`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`（含 AD-003 后继说明）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/FEA-08.md` 冻结 AC、`doc/reviews/FEA-08-impl-r2.md`、rolling checkpoint §168/§169、协作协议 §4/§4.1/§4.3/§5.1，及 Task 引用的提案 :457/:469。
- 被审：Task 的 67 项 EV；`doc/research/FEA-08-source-capability.md`；`doc/handoffs/FEA-08-impl-r3.md`；`verification/FEA-08/**`；非 Git 原型 `G:/CODEX/New Manga.workspace/FEA-08/prototype/` 的 16 个登记脚本。
- 以下 `R/` 表示上方 `isolated_evidence_dir`；`P/` 表示原型目录。所有 Python 执行均使用 `C:/Python314/python.exe` 3.14.6；门禁由 pwsh/Python subprocess 调用；原始日志含命令、cwd、EXIT、解释器/环境与耗时。被审脚本的 SHA 在 `R/pins.json`、两子任务 provenance 中可复算。
- 仓库运行证据是交付快照；本轮复跑日志保存在 R，不冒充已入库的 R3 交付原始记录。独立 Review 与 DSH 集成验证、Task 关闭是不同动作。

## Standards（executed）

按 AGENTS 产品/写域边界、Task OUT、协作协议 §4.1 的可复现证据及 §4.3 的诚实 MET 审查。`f7f00848f` 实际 45 文件全部在允许的 verification/research/handoff/Task 路径；`f48460316` 为五个登记/治理文件；`07724b88d` 仅 `.gitattributes`，已明示 DSH 集成处置。产品路径从 base 到 head diff=0。未发现新增生产 Schema、共享接口或依赖变更。

硬性问题为 F08I3-001/002/003/005：判据与原始事实矛盾仍 PASS、失败批次未完整回滚/成功日志误导、原始日志缺要求的耗时。F08I3-004 为精确映射行为缺口。未将 Fowler smell 判断项另计 finding；可维护性建议不替代可复现问题。

## Spec（executed）

### 逐 AC

| AC | 独立实证 | 当前判断 |
|---|---|---|
| AC-1 H4：同句柄、读前后身份、混合流不得成功 | 隔离运行十场景：7 complete_old_digest、S4 unavailable、S5a/S5b undetected_mixed；tolerant mmap 协议返回 digest 但评估 unavailable，strict S5c 实测拦截；指定负控降级 | **限定 strict 的已测结论成立**；tolerant mmap 仍 UNAVAILABLE。不能外推到未测卷 |
| AC-2 H5：保留或回收且还原 digest 一致；不 fallback 永久删除；恢复不重发 | 隔离实跑 9 PASS+2 LIMITED，G: 0项/0字节→0项/0字节，5 项还原，lab leftover=0；正常结果的保留/digest/计数成立 | **正常 measured 主链成立，自动证据判据 PARTIAL**：F08I3-001 可把反证发布为 PASS。R3 不可回收 mock、R7/R8 均未升级 measured |
| AC-3 H6：尺寸/方向/唯一性、occurrence、GIF/PDF参数 | 隔离 19 场景与 Canonical 逐项相等；独立异形图与 PDF 绑定尺寸、12 对 ZIP 覆盖同名/异名/顺序/重复；未发现新增误 exact | **安全反例修复成立；整体 PARTIAL**：可唯一一对一的改名容器被误报无法唯一映射（F08I3-004）。不得用其“安全保守”代替本轮要求的唯一正例 |
| AC-4：60格现状/需新增/来源；可复现完整交付 | 60/60 格字段/来源自洽；67/67 EV 与16脚本匹配；原始 build/test/skip 已入库；完整性与原子失败仍有反例 | **PARTIAL**：F08I3-001/002/003/005；不能维持不带限制的完整 MET |

此表是 Review 判断，不代改 Task marker。DSH 应在 adjudication/返修时处理仍为 MET 的 AC-3/AC-4，以及 AC-2 的判据完整性；已知 LIMITED 子能力不得改写 MET/PASS。

### F08I2-001…007 闭合核验

| R2 finding | 本轮复现与证据 | 结论 |
|---|---|---|
| F08I2-001 pin逐commit | 独立解析67行：66个非`-` commit逐条 `git cat-file -p commit:path` 原始字节，文件存在66/66、SHA66/66；SHA-only1/1；WT/index/干净checkout均67/67。旧 EV43 的 prototype_hashes 现为 **EV59**，@f7f00848f SHA=`e3880c46d6a6b1356a764301e9c18ed3ed67e423ef3f6fa190f103074f326dd3`。隔离 selfcheck 正常EXIT0；改该行旧commit、改为不含文件的base、改SHA分别EXIT1，且对应commit列DIFF | **FIXED**；R/pins.json、pin-selfcheck-probes.json、pin-selfcheck-*.log；逐EV见附录A |
| F08I2-002 尺寸绑定 | 独立RGB序列相同的1×8/2×4 PNG→candidate，size_mismatch/exact_blocked_by_size_mismatch=true；canonical digest不同；同尺寸同内容异编码→exact。M19(2×6/3×4)三断言均true；PDF72dpi异形digest不同、同形相同，默认150dpi异形需确认 | **FIXED**；R/h6/probe_results.json、out/h6_results.json；含dim-bound字段 |
| F08I2-003 容器唯一性 | 自建重复同图a/b→c/d不再exact；同名顺序改变且唯一、同名重复内容有稳定occurrence锚可exact；重复名异内容candidate；M10/M11/M13保持exact、M12 candidate、M20 needs_confirmation | **原P1误exact已修**；唯一内容改名仍误拒→新P2 F08I3-004；R/h6/probe.py与probe_results.json |
| F08I2-004 来源污染 | 4卷×5类×3能力=60格逐格核对status/evidence/current/needed；USB/SMB三能力全mocked、Cloud全inferred，无非NTFS measured；MD各能力逐格显示来源，状态计数重算一致 | **FIXED**；R/matrix-transaction/matrix-60-cells.json（0错误） |
| F08I2-005 缺必要断言 | 正常derive不误降；指定S5c/M16/M19/M20/R5b/R6b共12个字段负控均降级，单删一个计数也降级；但还原digest=false、永久fallback=true、同时缺两计数仍PASS且可被真实main晋升 | **PARTIAL**→F08I3-001；matrix-mutations.json + cases/semantic-* |
| F08I2-006 失败混合证据 | fake-repo重定向全部目标；fixtures生成/stage前与后/H4/H5/H6/matrix失败均恢复旧路径+hash集合；正常仅更新managed文件，gates/pin/raw保留，所有案例tmp空。但真实promote move/copy失败丢旧文件；最终自日志失败无回滚且可留EXIT0 | **PARTIAL**→F08I3-002/003；R/matrix-transaction/transactions.json、29个cases，见附录C |
| F08I2-007 原始门禁/skip | 8个raw log均有命令/EXIT/cwd/shell、完整程序集输出与失败栈；attempt1失败保留、摘要如实注明重试。57条skip集合与02-test.log完全相等，源文件:行/属性57/57准确，原因可沿SidecarFixture/HostFixture等guard核对；03-check独缺耗时，解释器/环境仅manifest级快照 | **主要交付FIXED，元数据PARTIAL**→F08I3-005；R/logs-audit.json；无证据宣称发生原始输出截断 |

### 独立反例与负控摘录

1. 尺寸：`RGB=[50,80,110]×8`，两PNG的RGB SHA同为 `5c658f65bdc10f464c75d16ab302efb5c90da84cc23f8834a1e6c8a041743ec1`；规范digest分别 `36ae544856361a2f8f4d0853986210d135c38038f29b202ba7da40a75cba2030` / `b42ddbb56b81a7d34d847f5029d5c230eb608245ad891539b27a1fbd8b557c2b`。异形candidate；同形exact。不是仅复跑M19。
2. ZIP：`a=红,b=绿 → c=绿,d=红`，两digest各出现一次，唯一对应明确，实际仍needs_confirmation/member_identity_ambiguity。相同两digest仅交换现有名字却exact。`a=红,b=红,c=绿 → a=红,b=红,d=绿`重复项有同名锚且剩余绿图唯一，也被整体降级。没有实际错误搬运人工内容。
3. H5语义：分别仅改 R1.restored_digest_matches=false；R3.disposition.fallback_rmdir_used=true；同时删 R6b.after_execute/after_recovery计数。三次隔离main均EXIT0、晋升矩阵H5=PASS。当前Canonical原件不存在这些坏值；反例证明的是检查器未能拒绝矛盾证据。
4. 事务：在“旧目标已备份→写新目标”之间注入OSError，Canonical旧文件缺失但failure JSON声称rolled_back=true；在最后run_all_log.json复制时失败，Canonical已是新集且run_all.log含EXIT0。不是只模拟前置H4失败。

## Findings

以下全部 open；脚本非Git，用 Task EV59 的原型SHA pin绑定版本，`P/`的绝对根见范围说明。P2沿用上一轮对研究原型的证据/判据问题分级，不将其冒充已发生的生产数据事故。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F08I3-001 | P2 | `P/matrix.py:87–111`；`P/run_all.py:150–156`；Task:74/79 | H5仍主要相信verdict；R1还原digest=false、R3 mock启用永久fallback、R6b两计数均缺失时仍PASS。`None==None`使缺失计数通过，违背AC-2及“必要反证失败即降级” | `R/matrix-transaction/cases/semantic-r1-digest/`、`semantic-r3-permanent-fallback/`、`semantic-r6b-counts-missing/`：实际main EXIT0、矩阵measured_core_pass=true、run_all.log EXIT0；matrix-mutations.json另含R2/R5b反例 | 校验固定必需场景与直接AC事实；计数须存在且为合法整数；核对还原digest、目标保留/类型、无永久fallback、执行/恢复计数；matrix/verify_results共享强判据 | open |
| F08I3-002 | P2 | `P/run_all.py:73–95,268–269` | 旧目标移到backup后，写新目标失败；JOURNAL尚未追加，rollback漏该目标，Canonical丢旧fixtures/result/log，失败记录仍称已回滚；下次清OUT还可能删除唯一backup | `cases/promote-fixtures-move`、`promote-first-result-copy`、`promote-managed-log-copy`：EXIT1，分别缺fixtures/old.bin、h4_results.json、h4_run.log，rolled_back=true；全部实际managed复制点负控一致 | 在首次可见修改前记录恢复状态，或helper异常自行恢复；恢复后核对完整旧集合再写rolled_back | open |
| F08I3-003 | P2 | `P/run_all.py:290–302` | finally先commit_journal删整批旧backup，再晋升自日志；这些失败在except外。无法整体回滚，最终JSON失败还留下EXIT0的新日志 | `cases/final-run-log-copy`、`final-run-json-copy`：EXIT1、无failure.json；后者新run_all.log EXIT0且run_all_log.json缺失 | 自日志构建/晋升纳入同一异常保护事务；所有必需产物成功后才提交journal、发布成功标记；finally仅清理 | open |
| F08I3-004 | P2 | `P/h6_run.py:183–190`；Task AC-3；提案:457 | 内容各自唯一、尺寸/方向相同但成员名改动，因names_sorted_equal=false一律需确认并称“无法唯一映射”；实际可按强digest唯一对应。重复项有锚而唯一项改名也误拒；造成不必要人工确认 | `R/h6/probe_results.json` containers.unique_all_renamed / unique_swapped_names / dup_anchored_unique_rename；真实合成ZIP/成员digest在同目录 | 按occurrence构建唯一一对一映射，名字/ordinal只用作歧义消解锚；唯一内容改名可exact。若产品确需一律确认，先由DSH明确裁决该限制并修正文案/正例要求 | open |
| F08I3-005 | P2 | `verification/FEA-08/logs/gates-raw/03-check.log:1–6`；`P/gates_capture.py:225–233`；R3 Handoff §3 | check原始日志缺elapsed；phase2单独调用subprocess且自建header绕过run_capture计时。不能完整兑现本轮要求的命令/EXIT/cwd/shell/解释器/耗时证据，报告“全部具备”过强 | `R/logs-audit.json`：8个raw log中只有03 elapsed=false；其余7项有elapsed；缺的值无法从快照准确追溯 | phase2复用统一采集器或显式计时，新跑后登记真实耗时/运行环境并re-pin；保留旧日志，不补造时间 | open |

附带计数勘误（不另计严重性）：实际fixtures目录 **38文件=37内容+1 evidence_manifest**，双manifest各37项且SHA全部一致、确定性30/37；Task:85/research §10称“38内容+1 manifest”、子任务按目录计“38 fixtures”不代表38内容。67 EV总数无缺漏。`R/fixture-manifest-audit.json` 可逐项复算。Task及Handoff中gates/check称SHA-only的历史说明也应按实际EV表理解：本轮仅pin-verify.log一项为`-`，其他66项均有commit。

## 验证（独立运行）

以下 head 均为 `f48460316`；`C=R/gate-repo` 为 shared clone 的 detached checkout，原仓库 .git/index/HEAD 未改。默认全量命令未加filter，也未修改测试源码/属性或runsettings。

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 固定点/写域 | git rev-parse HEAD；branch；common-dir；status；diff-tree逐commit | main/.git，开始clean，head_delta0；f7=45允许文件；f484=5治理；077仅attributes | R/status-before.txt、pins.json、logs-audit.json；末尾定稿核验 |
| build | 在C：`dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | EXIT0；0 warning / 0 error；12.6s | R/gates/build.log |
| 全量test初次隔离 | 在C：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo` | EXIT0；**1289/0/60**，总1349；额外3个ModelSidecarFact因隔离workspace默认路径缺fixture而skip，不能冒充目标1292/0/57 | R/gates/test-attempt1.log；RunBindingFixTests:530–590 |
| 全量test补齐隔离输入 | 同一无过滤命令；复制模型sidecar与BOOK合成fixture到R，显式设置MODELS_SIDECAR_DIR/BOOK_FIXTURE_ROOT；TEMP/TMP/EVIDENCE均R | **EXIT0；1292 passed / 0 failed / 57 skipped**，总1349；183.1s；无过滤，57 skip与原交付集合完全相同 | R/gates/test-isolated-fixtures*.log、fixture-isolation.json |
| 治理检查 | 在C：`pwsh -NoProfile -File tools/governance/check.ps1` | EXIT0；PASS(3 warnings)：9非终态、STATUS/PLAN预算80%；不替代语义审查 | R/gates/governance.log；报告落盘后再核验 |
| 冻结pins | 在C：`pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 字节保持隔离副本 **EXIT0、15/15**。默认clone先FAIL14，均为冻结文档CRLF变换；15个原仓库字节与HEAD blob一致，复制原始字节后通过。与FEA08的67pin干净checkout通过分开记录，不隐去首次失败 | R/gates/freeze-pins.log（首次）、frozen-byte-control.json、freeze-pins-byte-preserving.log |
| 旧FEA06四PNG | SHA256原始字节，与既有登记比对 | 4/4相同，见附录B | R/logs-audit.json |
| 产品边界 | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools` | EXIT0、空，src_changes=0 | R/gates/forbidden-diff.log |
| 清空类API | `git grep -n -E 'SHEmptyRecycleBin\|EmptyRecycleBin\|SHERB_' -- src apps experiments tests packaging scripts tools`；人工核对P/fwin | grep EXIT1表示无命中；代码路径调用0；原型仅注释提及禁令，无封装/调用 | R/gates/clearing-api.log；P/fwin.py |
| EV逐commit及独立checkout | Python subprocess原始bytes；独立GIT_INDEX_FILE读head，`git -c core.autocrlf=true checkout-index -f --prefix=R/checkout-index/ -- <67 files>` | 全部67/67；66commit存在且SHA通过，1SHA-only；WT/index/checkout67/67；无未登记文件 | R/audit_pins.py.log、pins.json；附录A |
| selfcheck可移植与负控 | 仅重定向REPO/V/TASK/LOG/tempfile到R副本；依次正常/旧commit/commit缺文件/错SHA | EXIT **0/1/1/1**；脚本实际读取行commit，未只信index | R/pin-selfcheck-*.log、pin-selfcheck-probes.json |
| 脚本/manifest | 16脚本逐SHA；两manifest逐项重算 | 16/16；37/37+37/37；fixtures38文件含manifest | R/pins.json、fixture-manifest-audit.json |
| H4 | `python -B R/h45/prototype/h4_run.py` | EXIT0；10场景，strict/mmap分类与原证据一致 | R/h45/h4_run.py.log、out/h4_results.json |
| H5 | `python -B R/h45/prototype/h5_run.py`；前后查询G:；合成lab限定恢复/清理 | EXIT0；9 PASS/2 LIMITED；G:0/0→0/0，5项还原，lab leftover0；tmp清理 | R/h45/h5_run.py.log、out/h5_results.json、safety.json |
| H6 | `python R/h6/prototype/h6_run.py --fixtures R/h6/fixtures`；另`python R/h6/probe.py` | EXIT0；19场景逐项相等；异尺寸/容器歧义安全通过，唯一改名P2误拒 | R/h6/run_meta.json、probe_results.json、verification.json、full-h6-stdout.log |
| 矩阵/负控/事务 | `python -B R/matrix-transaction/probe.py` | 60格0来源错误；状态计数重算：strict双态1、PASS6、volume-level inferred7、Non-AES双态1、LIMITED(mocked)30、LIMITED(inferred)10、UNAVAILABLE(inferred)5，合计60；19变异、29事务案例；已记录FAIL与不触发案例，不以N passed替代判别力结果 | matrix-60-cells.json、matrix-mutations.json、transactions.json、cases/*/result.json；附录C |
| 原交付raw/57skip | `python -B R/audit_logs.py`；逐源方法/最近属性与guard核对 | skip57/57集合/来源/属性一致；attempt1失败原始栈保留，摘要明确重试；03耗时缺失 | R/audit_logs.py.log、logs-audit.json |

门禁输入说明：初次隔离测试的3个额外skip为 RunBindingFixTests 的 `ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured`、`ModelsBuild_BookRun_WithInjectedBindings_OcrNoLongerProviderNotConfigured`、`ModelsBuild_UnknownProviderBinding_SurfacesTypedProviderError`。这些测试用自己的临时dataRoot复制合成BOOK，未对原fixture/原模型包执行写操作；第二轮输入为完整副本（sidecar1964文件/868843916字节，BOOK28文件/8739421字节），见fixture-isolation.json。主sidecar环境变量保持未设置，57项既有skip原因不变。最终逐程序集为 Appearance 21/0/0、Presentation 38/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 117/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 653/0/7（通过/失败/跳过）；合计1292/0/57、总1349，详见R/gates/final-test-summary.json。

## Architecture（executed）

**边界结论：无生产架构越界；研究判据仍有未闭合点。** Avalonia/Host/Python Core/SQLite/ReferencedSource边界与冻结契约未被本次代码修改。H4的strict-only硬约束继续成立；tolerant+mmap盲区不能靠size/mtime包装为稳定lease，FEA-09+必须消费unavailable并保留generation/CAS边界。

H6的dim-bound digest已覆盖EXIF规范化后的宽高与RGB；PDF同样绑定渲染尺寸，并记录页码、DPI/scale/颜色/引擎。后续SourceVersion/PageBinding精确身份不能退回裸RGB digest。容器必须保留独立occurrence，用强digest和必要身份锚构造唯一对应；重复内容多重集相等不等于映射唯一，唯一内容改名也不应被描述成天然一对多。pHash/dHash/OCR仍仅候选，不授权自动迁移人工内容、区域坐标或pinned revision。

H5正常主链不代表证据门禁可以信任顶层PASS。FEA-09/11/12/13复用判据前须修F08I3-001并固化必需字段/负控；显式永久删除与原文件保护仍按ADJ-001，不能由SHFileOperation的成功码推断。USB/SMB/Cloud、取消与AES等LIMITED保持原级，不升级产品承诺。

本轮未增加依赖；许可边界仅核对Task/研究登记，未批准生产引入PyMuPDF/pyzipper。研究原型的journal也不是数据库事务：F08I3-002/003说明它尚不具备声称的整批失败原子性，不能作为后续跨文件系统/DB原子保证的实证。

## Verification 结论

字节身份、已测OS正常行为、H6危险误exact反例、非NTFS来源分类可重复成立。指定的底层负控已增强，但扩展语义负控仍穿透，晋升失败的完整性声明不成立。**门禁命令成功不消除这五项finding；当前不能给impl-r3 approved。** 本轮没有发现真实Canonical已损坏、真实回收不还原或当前结果被变异污染；所有坏值/故障仅在R的隔离副本。

## 复审与下一步

推荐下一步：**DSH处置本Review并冻结FEA-08 R4返修；FEA-09仍等待FEA-08集成关闭。** 本报告不释放新Task、不替DSH行使范围/处置/最终push权限。

可直接转发给DSH：

> Task：FEA-08 impl-r3 adjudication / R4返修。工作路径 `G:/CODEX/New Manga`，main；base `2870a9fa5`，被审head `f4846031620e44adfcdcae026039abc7e2494201`，实施交付 `f7f00848f`。先逐项处置 `doc/reviews/FEA-08-impl-r3.md` 的F08I3-001…005，再在Task/STATUS按协议冻结返修Owner、Reviewer、范围及新base/head；Owner推荐DSH或其明确指定的协作Agent，复审需独立新上下文。允许修改本卡既有workspace/prototype、verification/FEA-08/**与FEA-08 research/handoff/Task登记；禁止产品src/apps/experiments/tests/packaging/scripts/tools改动，不新增Schema/接口/依赖，不push。交付：H5共享强判据与缺字段负控、全部晋升点失败可恢复旧集合/不产假成功、唯一容器改名正例或明确范围裁决、完整原始门禁元数据、重出Canonical/re-pin/Handoff并纠正fixture计数与AC marker。验证：隔离重跑本报告反例，正常路径不误降；66/67模式按新实际EV表逐commit+WT/index/clean-checkout；build0w/0e、无过滤test至少1292/0/57、check PASS(3)、冻结pins15/15、四PNG不变、产品diff0、H5仅合成lab且G:0→0并恢复清理。保留每次失败/skip原因与原始日志。新head独立Review、DSH集成验证和资源closeout后方可关闭FEA-08并考虑释放FEA-09 scope。

## 附录A：67项逐行pin复核

每行使用Task登记SHA作expected；下表“commit”=文件确实存在于登记commit且原始blobSHA匹配；“WT/index/checkout”各自独立SHA匹配。完整expected/actual SHA与commit_exists字段见 `R/pins.json`；脚本为`R/audit_pins.py`，没有PowerShell文本管道重编码。`pin-verify.log`仅SHA-only，自身由独立审计核对，未要求其自校验收敛。

| EV | path（verification/FEA-08/下） | 登记commit | commit存在/字节 | WT | index | checkout |
|---|---|---|---|---|---|---|
| EV-F08-01 | fixtures/anim.gif | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-02 | fixtures/book_dup.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-03 | fixtures/book_dup_copy.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-04 | fixtures/book_dupcontent_a.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-05 | fixtures/book_dupcontent_b.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-06 | fixtures/book_enc_aes.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-07 | fixtures/book_enc_zipcrypto.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-08 | fixtures/book_enc_zipcrypto_copy.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-09 | fixtures/book_v1.cbz | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-10 | fixtures/book_v1.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-11 | fixtures/book_v1_recompressed.zip | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-12 | fixtures/doc_enc.pdf | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-13 | fixtures/doc_enc_copy.pdf | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-14 | fixtures/doc_v1.pdf | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-15 | fixtures/doc_v1_regen.pdf | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-16 | fixtures/evidence_manifest.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-17 | fixtures/firstframe_extract.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-18 | fixtures/folder_v1/p1.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-19 | fixtures/folder_v1/p2.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-20 | fixtures/folder_v1/p3.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-21 | fixtures/folder_v2/p1.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-22 | fixtures/folder_v2/p2renamed.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-23 | fixtures/folder_v2/p4.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-24 | fixtures/img_base.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-25 | fixtures/img_cmyk.jpg | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-26 | fixtures/img_copy.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-27 | fixtures/img_dhash_dist10.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-28 | fixtures/img_dhash_dist11.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-29 | fixtures/img_dhash_ref.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-30 | fixtures/img_dims_a.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-31 | fixtures/img_dims_b.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-32 | fixtures/img_exif_o6.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-33 | fixtures/img_flipped.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-34 | fixtures/img_gray.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-35 | fixtures/img_gray_as_rgb.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-36 | fixtures/img_reenc.jpg | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-37 | fixtures/img_rotated_phys.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-38 | fixtures/wrongframe_blue.png | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-39 | logs/gates-raw/01-build.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-40 | logs/gates-raw/02-test-attempt1.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-41 | logs/gates-raw/02-test.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-42 | logs/gates-raw/03-check.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-43 | logs/gates-raw/04-freeze-pins.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-44 | logs/gates-raw/05-fea06-png.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-45 | logs/gates-raw/06-forbidden-diff.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-46 | logs/gates-raw/07-clearing-api-search.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-47 | logs/gates-raw/gates-raw-manifest.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-48 | logs/gates-raw/phase1-values.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-49 | logs/gates.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-50 | logs/h4_run.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-51 | logs/h5_run.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-52 | logs/h6_run.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-53 | logs/make_fixtures.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-54 | logs/make_fixtures_regeneration.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-55 | logs/matrix.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-56 | logs/run_all.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-57 | logs/stage_evidence.log | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-58 | logs/test-skip-inventory.md | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-59 | prototype_hashes.txt | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-60 | results/capability_matrix.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-61 | results/capability_matrix.md | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-62 | results/fixtures_manifest.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-63 | results/h4_results.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-64 | results/h5_results.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-65 | results/h6_results.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-66 | results/run_all_log.json | f7f00848f | PASS | PASS | PASS | PASS |
| EV-F08-67 | logs/pin-verify.log | - | N/A(SHA-only) | PASS | PASS | PASS |

## 附录B：旧FEA-06四PNG

| 文件 | SHA-256 |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

## 附录C：矩阵负控与事务故障覆盖

`R/matrix-transaction/REPORT.md`与provenance记录副本SHA、注入方法、命令/EXIT/cwd/解释器/耗时；完整before/after文件hash在transactions.json。下面按真实触发统计，不能把未触发故障的案例记作故障覆盖。

| 负控/路径 | 实测 |
|---|---|
| 正常derive | H4 strict=true、H5=true、H6五类=true，无误降 |
| S5c拦截断言false / writer=opened | 两项均H4降级 |
| M16蓝帧反证false | 单图H6降级 |
| M19 not_exact / size_mismatch / canonical_differs分别false | 三项均单图H6降级 |
| M20 ambiguity / multiset断言分别false | 两项均ZIP降级 |
| R5b no_destructive/refused分别false | 两项均H5降级 |
| R6b recovery计数改变 / no_destructive_reissued=false | 两项均H5降级；单删一计数亦降级 |
| 额外R1还原digestfalse、R2成员digestfalse、R3永久fallbacktrue、R5b类型/保留事实破坏、R6b还原digestfalse或双计数缺失 | 仍PASS，详见F08I3-001；19个单函数负控总计13降级/6未降级；双计数缺失与R3 fallback另经完整main独立注入 |
| fixtures生成失败 / stage写前失败 / stage写两个manifest后失败 / H4/H5/H6/matrix失败 | 旧Canonical路径+SHA集合全部恢复；failure.json存在；非零；tmp空 |
| fixtures promote move失败 | 旧fixtures缺失；非零；错误声称rolled_back；tmp空 |
| 5个实际result与7个managed log的copy逐点失败 | 每次对应旧目标缺失；非零；tmp空；F08I3-002 |
| 最终run_all.log / run_all_log.json复制失败 | 无整批回滚、无failure.json；后者保留新EXIT0日志；F08I3-003 |
| 三个H5语义反例进入main | 均EXIT0并晋升H5 PASS；F08I3-001 |
| success / copy-result-fixtures_manifest.json未触发注入 | 均实际成功；只替换managed文件，gates/pin/gates-raw保持；后者不计入故障覆盖 |

29个事务案例的unmanaged文件全部不变、tmp全部空；测试只证明已注入故障点，不证明断电/kill/回滚二次失败原子性。隔离输出及synthetic artefact保留供DSH复现，不作为新的Canonical Evidence，也不授权清理旧workspace资料。

## 定稿核验

`HEAD=f4846031620e44adfcdcae026039abc7e2494201`，head_delta=0；原仓库开始clean，定稿`git status --porcelain=v1`仅`?? doc/reviews/FEA-08-impl-r3.md`。67个Canonical文件与16个原型脚本复算前后字节全部不变；原仓库index/分支未改，无提交、无push。报告落盘后的隔离治理检查EXIT0、PASS(3 warnings)。证据：`R/final-state.json`、`status-after.txt`、`gates/governance-after-report.log`。
