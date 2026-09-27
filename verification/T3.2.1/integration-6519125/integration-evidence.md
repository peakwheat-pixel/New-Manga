# T3.2.1 Codex Integration Evidence — 2026-09-26

## 固定对象与集成链

- 主线基线：master eec1aa49d07119f0aa66ff461ebbb55e4595e624。
- 固定构建输入：08f9bd85137965df922db524bc92917af513bd24；本轮未重新构建。
- 交付 head：b18fa0e70ec4356a207fd7d941cdcf0cb2f1c285；独立 Review branch/head：agent/qoder/T3.2.1-review-78aba7c b66788a813b04c0305226331c54327e178093664。
- delivery merge=230beac2c8e2241b1090c2dc70b3d1c213a2d2ad；Review merge / integration code head=6519125406161924b0021e021e79fea07cf673fc。两者分别保留 merge history，工作区无冲突。
- Review doc/reviews/T3.2.1-78aba7c.md：首轮 78aba7c 为 changes_requested；返修 head b18fa0e 的追加复审为 approved，批准范围仅为“可作集成输入”。这不等于发布批准。

## 集成后重跑

集成 worktree：G:/CODEX/New Manga.worktrees/T3.2.1-integration-20260926；PowerShell；Python 3.12.3 venv。每份日志记录 shell、解释器、integration head、命令和 EXIT：

| 检查 | 结果 | 原始日志 |
|---|---|---|
| python -m pytest tests/packaging tests/core/test_bootstrap.py -q | 34 passed，EXIT=0 | [packaging-and-bootstrap-tests.log](packaging-and-bootstrap-tests.log) |
| verify_artifact.py（source head 08f9bd85137965df922db524bc92917af513bd24，fixed Build 2） | 7/7 checks true，EXIT=0；manifest/包体均为 2,475 文件、234,071,167 bytes；QML 26/26；重型依赖缺席 | [fixed-artifact-verification.log](fixed-artifact-verification.log) |
| python -m compileall -q src/bootstrap packaging | EXIT=0 | [compileall.log](compileall.log) |
| git diff --exit-code 08f9bd85137965df922db524bc92917af513bd24 HEAD -- src packaging tests requirements.txt requirements-dev.txt | NO_DIFF，EXIT=0 | [fixed-input-tree-check.log](fixed-input-tree-check.log) |

Build 2 exe SHA-256：3aac341ace018a6884322ea2602c90c350844330154d63dc51ff16aa0bef74b2；
artifact-manifest.sha256 SHA-256：073b84f509685efe636071dca7794c2a45b0dbb2646e40a6c9e05ff2029d9608。
集成 head 的 src、packaging、tests 与依赖清单相对固定输入无差异，因此未重建包；
本机交互证据仍绑定 08f9bd8，不描述为集成 head 新构建。

## Codex 裁决

- R-003 / AC6：fail-closed run (completed_with_failures / PROVIDER_NOT_CONFIGURED) 是真实 Pipeline 尝试和诊断，不是成功的 Mock/Local Pipeline 输出。它满足 AC5 缺 Provider 诊断证据，但 AC6 的 pipeline 主流程子项不通过；AC6 保持 PARTIAL（11/12），成功的轻量 Mock/Local 烟测登记为 T3.2.1-REPAIR-17 proposed / NOT_RELEASED。
- R-004：用户本机模拟验收路线只扩展到明确获准的 AC3，不延伸到原文要求 clean Windows 的 AC6/AC8。两者本机结果保留作部分证据，当前均 PARTIAL，干净机覆盖 NOT_RUN。
- R-015：STATUS Smoke status、AC3 environment route、Full Release Gate 行与 Current blockers 已对齐为 AC3 PASS（本机模拟路线；非干净机覆盖），同时明确 clean-machine coverage NOT_RUN。
- R-016：REPAIR-15 已限定为 openChapter 存 book/chapter IDs，再由 openExporter 传入；option 2（export_history 非空 CHECK + migration）剥离。Schema 变更需另行授权。
- AC10：Handoff、非作者 Review、固定 head 验证日志/hash 与 Codex integration evidence 齐全，因此 AC10=PASS。父 T3.2.1 仍 in_progress / OPEN。

## 仍挂账

- Windows 10 x64 矩阵：NOT_RUN。
- 真实 docTR 权重成功路径：NOT_RUN。
- 完全未安装 Python 的干净 Windows 启动：NOT_RUN。
- AC6 成功 Mock/Local Pipeline 路径：尚未实现/验收；REPAIR-17 未释放。
- AC6/AC8 clean-Windows 覆盖：NOT_RUN；AC9 真正冷启动测量：NOT_RUN。
- console=True 与 ICU 从宿主 System32 解析：发布前待决，建议登记 D08 发布清单。
- R-017 类别总数文案差异为非阻断记录项，不改变 reviewer 对 R-007 的判读。REPAIR-15/16/17 均仍 proposed / NOT_RELEASED（REPAIR-15 已修正建议范围但未释放）。

未执行 push、上传、安装器制作或签名；这些不在本次授权内。
