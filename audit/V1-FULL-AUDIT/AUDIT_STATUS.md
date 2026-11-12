# 审计状态
## 当前执行状态（2026-11-13）

ZCode 裁决确认附件完整，AUDIT-01–14 可执行。AUDIT-00 limited PASS；01 FAIL/P2；02 BLOCKED；03 FAIL；04 PARTIAL（定向合成测试 175+40 passed / EXIT 0；真实模型/GT/GUI NOT_RUN）；05/06 PARTIAL（阶段报告与合成测试已完成）；08 FAIL；11 阶段 FAIL（两个 Medium / High confidence findings，经 ZCode Review ACCEPT，1 个 P3 scanner 尾随空格差异已披露、未重跑）；14 PARTIAL（静态 V1 完整性/历史债务盘点，V1/未来承诺总账缺失、真实 GUI/安装/模型 NOT_RUN）。05/06 与 14 候选均待 ZCode 独立定级；真实模型、GUI 和付费 API 均 `NOT_RUN`。其余专项按矩阵列为 PARTIAL / NOT_TESTED / BLOCKED。Task `in_progress`，AC2/AC3/AC4 `PARTIAL`，Release Gate `BLOCKED`。

ZCode 范围裁决证据与源文件哈希复核见 `reports/ZCODE-ORIGINAL-SCOPE-READJUDICATION-2026-11-12.md`。AUDIT-08 closure 对 `6375afacb` 为 `ACCEPT`、P3-3 CLOSED；P3-4 披露已补，fresh re-review 待执行。AUDIT-05/06 报告、测试与门禁证据已固定；此前 plan Review 因 provider `1310`/HTTP `429` 无有效答复。用户报告额度恢复后，对固定 HEAD 的 AUDIT-05/06 + 14 fresh plan Review 再试仍收 provider `1310`/HTTP `429`，提示 2026-11-17 18:40:33 重置，EXIT 1、无 session/response。7 项候选均继续 `REVIEW_PENDING`。AUDIT-14 报告、采集器和门禁日志已形成；AUDIT-03 活动 Core 87 passed、ReferencedSource 77 passed（各 EXIT 0），但 junction publication probe 确认 managed root 越界新文件写入，阶段记 FAIL；桌面 UI/项目搬迁 NOT_RUN。AUDIT-04 providers 175 passed、Core detect 40 passed / 各 EXIT 0；fake engine/坐标测试不表示模型准确率，真实权重、GT、CPU inference 与 GUI NOT_RUN。下一项按 DAG 继续 AUDIT-07。
阶段提交 `e0bbe10c3` 后首次 default/TaskPath check 因 `doc/STATUS.md` 超防膨胀预算而 EXIT 1；状态摘要已在 `c3bd266cb` 压缩并复核。`c3bd266cb01007b8e9da679790433a149dfdc00e` 上复跑：default check EXIT 0（3 warnings）、TaskPath check EXIT 0（3 warnings）、pins 18/18 EXIT 0、API inventory 1/79/6=86 EXIT 0。首轮失败日志及修正后日志均保留；详细记录在 `logs/audit-11-gate-*.log`。
Task Canonical Evidence pinbackfill HEAD=`9bcb1886bcdd6f49eadeb57d208458e52a994b2c` 后复跑 default/TaskPath（各 EXIT 0、3 warnings）、18 pins（EXIT 0、18/18）、API inventory（EXIT 0、1/79/6=86）；generated HEAD 与完整输出见 `logs/audit-11-post-pinbackfill-*.log`。这些日志固定于 evidence commit `1d245610e` 并已列入 Task pins。
追加 Canonical Evidence rows 的 HEAD=`1e9f34e03a0cf10fede372c7e6ad11ffb8777eb0` 上再次复跑四项门禁均 EXIT 0（default/TaskPath 各 3 warnings；pins 18/18；API 1/79/6=86）；日志在 `4177c2d31d327bb98f4bab0948449cdba223661f` 固定并已在后续 pinbackfill 中列入 Canonical Evidence。
IN_PROGRESS：段 A 基线、盘点与测试日志已保存；段 B 于 2026-11-12 解封，固定当前架构 HEAD `10e4ee013835605800d3830fb960ae8d3aa04167`。Release Gate 仍为 BLOCKED（段 B 审计和 Review 未完成）。

2026-10-24 推送准备：登记和台账已同步，治理 PASS（3 warnings）。历史凭据筛查未确认真实凭据；材料来源、许可及数据库隐私未核清，push=BLOCKED_MATERIAL_PROVENANCE。未commit/push；独立Review尚未执行。详见 reports/PUSH_READINESS.md。

材料复核更新：4个PNG确认合成来源；169个JPEG与T1.1.1商业日漫记录的页名/数量/尺寸全部吻合，缺逐页源hash及传播证明。34份数据库已immutable只读核查，无已知非空secret字段，但存在22个本地路径单元格及WAL/删除页限制。最新报告 reports/MATERIAL_CLEARANCE.md；“我自己的，但是不传播”的后续裁决已覆盖等待许可分支，不再索要传播许可；不重复相同扫描、不push。

当前裁决：用户明确素材“我自己的，但是不传播”。169个JPEG及其压缩blob禁止上传，push=BLOCKED_OWNER_NO_DISTRIBUTION；此前等待传播许可分支被覆盖。本地原件/历史保留，独立干净快照方案尚未释放。

2026-11-12 风险披露：本地 `origin/main` reflog 记有 2026-10-30 三次 main push；私有素材对象曾进入公开仓库历史为高置信推论，见 `reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md`。实时远端可见性未核验，未执行远端补救；本地审计继续，任何传播/删除/历史改写均不在本 Task 授权内。

段 B suite 级证据状态（逐项状态以原件恢复后的最新裁决为准）：AUDIT-00 静态盘点 limited PASS；AUDIT-01 `FAIL`（`NM-AUD-0001`，ZCode 维持 P2）；AUDIT-02 `BLOCKED`；AUDIT-03 `FAIL`（SEG-B-PROBES-001）；AUDIT-04 `PARTIAL`（合成 Provider/Core 检查通过，真实模型与 GT 未测）；AUDIT-07/09/10/12/13 `NOT_TESTED`；AUDIT-05/06 `PARTIAL`；AUDIT-08 `FAIL`；AUDIT-11 安全静态阶段 `FAIL`、其余检查面具名 PARTIAL/NOT_TESTED；AUDIT-14 `PARTIAL`（静态盘点，真实 GUI/安装/模型未跑）。已有 probes EXIT 1（2 项 Medium / High confidence，1 项防线已验证）；Python Core pytest EXIT 1（3,519 passed / 16 failed / 10 skipped / 11 warnings）；Avalonia .NET `BLOCKED-TESTHOST-ACCESS`（8/8 runner EXIT 1、TRX 0 tests）；smoke `core,wire` EXIT 1（Wire 6/6 PASS；Core 4 PASS、7 项 `BLOCKED-SANDBOX-GRANT`；frontend/packaged SKIP）。suite 结果只作映射证据，不推导专项 PASS。

Checkpoint Review：ZCode fresh context 对 reviewed_head=`499a6b8e6eb293487abf391c46d00263230940ad` 的结论为 `PASS_FOR_CHECKPOINT`。ZCode addendum 已将 R-1/R-2/R-3 记为 CLOSED；R-4 保持 observation。R-1 的补验由实现侧 Codex 执行，ZCode 接受其日志作为 closure evidence：37/37 diff 路径在 allowed_paths 内，46/46 Canonical/SOURCE_PIN 的 raw Git blob SHA-256 匹配，EXIT 0；Reviewer 未亲自重算 actual 值。详见原 Review 和 [addendum 报告](reports/ZCODE-CHECKPOINT-REVIEW-ADDENDUM-2026-11-12.md)。该结论不等于全审通过或 Task 关闭；最终治理门禁和全审 review 仍待完成。

历史 checkpoint review：ZCode 对当时 reviewed_head 的结论及门禁仍是该提交范围内的有效历史记录；当时关于原始清单缺失和生命周期等待的状态已被附件恢复后的裁决更新。历史搜索只证明可达 Git 历史未保存逐项清单，不否定仓外附件来源。
