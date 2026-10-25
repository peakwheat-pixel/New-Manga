# 本地主线推送准备检查

日期：2026-10-24（Asia/Shanghai）。执行者：Codex。状态：**BLOCKED_MATERIAL_PROVENANCE**。本记录不关闭全量审计，不是产品发布验收，也没有独立 Reviewer 批准。

当前裁决更新：用户回复“我自己的，但是不传播”。推送状态改为 **BLOCKED_OWNER_NO_DISTRIBUTION**；169张JPEG及其外层压缩blob列为禁止上传项，不再等待许可来默认放行这段完整历史。旧来源检查作为事实保留，最新处置见 MATERIAL_CLEARANCE.md 和 evidence/push-material-disposition.json。

## 固定范围与结论

- 已用 `git ls-remote --heads origin main` 核实远端 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`，与缓存一致。
- 本地 `main=349e61faff5f93067af5d4ce2d9e394e0d665b8c`，领先 2888、落后 0，含 208 个 merge commit；2026-09-25 至 2026-10-23。净差异 11973 个路径。
- 当前候选只能是固定范围的普通 fast-forward；不使用 force、mirror、all 或历史重写。用户本轮授权准备检查，没有授权上传。
- **暂缓 push**：启发式凭据检查没有确认真实凭据，但历史材料的来源与传播许可未核清。分批不隔离这些历史内容，最新提交删除文件也不能从祖先历史排除内容。

## 工作区归属及登记

`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 的原在途差异均用于登记 `NEW-MANGA-V1-FULL-AUDIT`；Task 与 `audit/V1-FULL-AUDIT/` 属于 Codex 的未完成审计工作。保留 `in_progress`、pending evidence 和未分配 Reviewer 的真实状态。

本轮同步 `doc/TASK_LEDGER.md`：357 个 Task、355 个终态、2 个非终态。Task 仍未跟踪时，生成器准确记录 tracked 356 / untracked 1；若以后暂存或提交 Task，必须再次生成台账，不能把此数字解释为已提交。

Status 刷新日期，历史 dsh 租约不再宣称已由本轮验证；Plan 去掉已完成沙箱的待授权候选表述。不改历史限制、产品 Gate 或既有 evidence pin。

6 个 `verification/P04/diagnostic_p22_*.jsonl` 在审计基线前已存在，具体生成者未证明；只记录 SHA-256，保留原位，不暂存、不归入当前审计交付。见 `evidence/push-worktree-ownership.json`。

本轮不提交整包在途审计，避免把尚未冻结的审计证据、旧的进度占位文档一并入库。工作区登记已同步，后续审计 checkpoint 提交须逐项选取文件并保证其恢复引用随提交可用；不使用 `git add .`。本轮没有 commit、push、stash、清理或历史改写。

## 历史凭据筛查

命令：`python audit/V1-FULL-AUDIT/tests/scan_push_history.py`。仅本地读取 Git 对象，不在线验证凭据，不安装工具或上传项目内容。脚本自检覆盖命中脱敏、行号、UTF-16、zlib 类型和已知 token 格式。

扫描新增可达的 **17455 个 blob**，覆盖历史版本而非仅最终 checkout；另解压 **2144 个 zlib Git 对象**，检查 **3 个 ZIP 的 28 个成员**。没有解压失败或大小限制阻断。zlib 内含 tree 1017 / blob 926 / commit 201。

7 类规则：私钥标头、GitHub/OpenAI/AWS/Google/Slack 凭据格式及带引号的 credential assignment。共 **4 个命中、3 个不同值**；两版历史 `tests/pipeline/test_pipeline_production_seam.py` 中的 `do-not-store` 脱敏测试占位值，已逐个核对，不是本轮确认的真实凭据。证据只保留位置与值的 SHA-256，不记录凭据原文。

这是离线启发式筛查，不能证明所有凭据不存在：未扫描图片文字，未穷举编码、短密码、所有 token 提供方或任意深度压缩；路径只取代表路径，非全部历史别名。未安装 gitleaks/trufflehog，也未用其他远程扫描服务。

## 材料来源与阻断项

`.tmp.driveupload` 共 2148 个路径，其引入提交为 `87f61d8b02c9b678e96b65798042ec3d83b9db87`。其中 2144 个为 zlib Git 对象；不能按临时文件名假设不含源材料。解压后有 **169 个 JPEG、4 个 PNG**。这些图像对象尚未从当前 main 的标准可达对象路径定位来源；454 个嵌入 blob 没有该路径映射。本轮进一步解析 1017 个嵌入 tree、182 个不同 commit 根 tree，对其中 89 个 blob 重建了路径，431 个取得文件名线索（两数有重叠）。4 个 PNG 得到 verification 路径线索；169 个 JPEG 仍只有如 `065.jpg` 的文件名线索，不能据此证明来源或许可。详细矩阵保存于 `push-material-provenance.json` 的 `embedded_tree_trace`。

外层新增 blob 另含 PNG 222、JPEG 26、SQLite 34（按不同 blob 计数，不是最终文件数）。既有数据库快照涉及 `verification/M2-AC1/**`、`verification/P18/**`；后续已完成34份主文件的immutable只读检查，12份M2-AC1业务库与生成页hash匹配、5份P18业务库领域记录为空，但仍有22个本地路径单元格，未排除WAL/删除页内容。4个嵌入PNG已与历史合成样本manifest精确匹配，169个JPEG与商业日漫记录高度关联而无传播证明。最新裁定与限制见 [MATERIAL_CLEARANCE](MATERIAL_CLEARANCE.md)，不再将这些项目统一称为未检查。

只读比对 `G:/CODEX/New Manga.workspace/data-registry/registry.json` 的 3089 个登记对象：外层材料与 zlib 解出的 payload 均未精确匹配。该表的原始 SHA-256 与比对结果保存于 `evidence/push-material-provenance.json`。**未匹配不等于无权利，也不等于已许可**；只能说明这份登记表未提供对应的来源/许可证明。

本轮按需要读取 `doc/WORKSPACE_GOVERNANCE.md` 的材料条款和 `verification/test-materials-licence-check-20261020.md`：前者要求保留来源与许可，不明材料按 private-only；后者只证明其指定工作区素材没有完整许可登记，不能直接代替本次每个图像的许可核验。本次未修改或复制仓外素材/registry。

## 推送清单与策略

机器清单：`evidence/push-manifest.json`；记录固定 base/head、远端、目标 ref、证据 SHA-256 和阻断状态。

| 候选终点 | 本批提交 | 累计 | 包含临时上传对象引入提交 |
|---|---:|---:|---|
| `9cb31430e`（主线收敛） | 2762 | 2762 | 是 |
| `7e242db00`（设置 C 收口） | 72 | 2834 | 是 |
| `349e61faf`（当前 HEAD） | 54 | 2888 | 是 |

材料检查和独立复核通过、且用户明确授权 push 后，优先一次普通快进至经过检查的固定 SHA；只有实际传输不稳定时才采用上述祖先节点分批。执行前重新核实远端 SHA、候选 SHA、保护规则与材料结论。当前没有发布可直接执行的 push 命令；现有“不 push”约束保留。

如果用户要求剔除历史材料，应另行冻结具体范围和恢复方案；当前没有历史重写、删除或改写共享 evidence pin 的授权。

## 验证与恢复

- `python tools/governance/task_ledger.py --write`：已执行，357 / 355 / 2；保留 Task 未跟踪的真实分类。
- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md`：PASS，3 warnings（两个非终态 Task、Status/Plan 体量提示）。
- 扫描脚本自检及 4 个命中的已知测试字面量断言：PASS。
- 本轮未改业务代码，业务测试 NOT_RUN；独立 Review NOT_RUN；全量审计仍 in_progress。

下一步建议：按最新 [MATERIAL_CLEARANCE](MATERIAL_CLEARANCE.md) 的来源矩阵和阻断处理，等待用户提供169页材料的许可/来源记录；若无可传播证明，由Codex冻结独立的材料排除发布方案供裁决，不重复相同扫描，不擅自重写main。固定审计交付后，由独立 Reviewer 复核清单。未完成前不建议 push。

可直接转发的最新完整继续指令见 [MATERIAL_CLEARANCE 的处置建议](MATERIAL_CLEARANCE.md#处置建议与下一步)；旧的材料追踪步骤已被该报告的实际检查结果收窄，不能据旧文字重复启动。
