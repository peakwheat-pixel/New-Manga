# 恢复入口

2026-10-24；HEAD 349e61faff5f93067af5d4ce2d9e394e0d665b8c；branch main；worktree G:/CODEX/New Manga。

先核对 git status / git rev-parse HEAD 与 evidence/source-manifest.json；保留原6个P04诊断文件。已完成基线/盘点。下一步查看 evidence/*.json 和 logs/*.log 的 EXIT，未有结果的套件通过 `python audit/V1-FULL-AUDIT/tests/audit_runner.py <suite>` 执行；suite=pytest/frontend/rust/smoke/governance/dependencies。所有运行数据 G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT。不得直接复跑未知仍运行任务；先检查进程。审计未完成，不宣称PASS。

## 2026-10-24 推送准备 checkpoint

TaskStatus=in_progress；ExecutionState=BLOCKED_MATERIAL_PROVENANCE（仅推送准备阻断，全量审计未关闭）。产品 start/head 仍为上述 `349e61faf`；没有新增提交、暂存、上传、清理或历史改写。

已同步 Status/Plan/Task/TASK_LEDGER；治理检查 PASS（3 warnings），不表示全量审计 PASS。工作区仍有本审计未提交文件、3 份已修改治理文档和6份既有P04日志；具体保护 hash 见 `evidence/push-worktree-ownership.json`，P04均不暂存。完整结果和后续指令见 `reports/PUSH_READINESS.md`；固定推送候选、base和证据hash见 `evidence/push-manifest.json`。

历史离线扫描已覆盖17455个新增blob、2144个zlib对象与3份ZIP；4项凭据命中均为测试占位值。材料许可/数据库隐私仍未证明，173个嵌入图像未取得当前主线标准对象路径映射；不能push。下一精确步骤：按报告追溯嵌入tree/材料来源；不因本次文档同步批量暂存整包审计，尚未冻结的全量审计证据与未分配Reviewer状态均保留。

## 材料复核 checkpoint（当前恢复点）

产品HEAD/branch/worktree不变，Task仍in_progress；推送准备仍BLOCKED_MATERIAL_PROVENANCE。读取 `reports/MATERIAL_CLEARANCE.md` 和 `evidence/push-material-inspection.json`；上面的初次“继续追踪”步骤已被本轮实际检查收窄。

4个嵌入PNG与 `ed607b755` 合成manifest精确匹配。169个JPEG名称集合/页数/尺寸与T1.1.1商业日漫卷册记录完全吻合，但缺逐页源hash，不能把关联当许可。沿182个根tree及本地对象共读取1449个tree，无缺失tree；仍不能从这些根定位169个JPEG完整路径。34份库已readonly immutable检查，12份M2-AC1业务库与生成页hash匹配、5份P18业务库领域表为空；存在22个路径单元格，不签发WAL/删除页隐私结论。

隔离数据库副本保留在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/push-materials/`，只读核查前后hash一致，不清理。6个P04日志仍保护且未暂存，无新增commit/push/历史改写。继续精确步骤：取得用户的来源/许可记录或材料处置选择，按最新报告记录证据；如果缺许可，冻结独立发布方案供裁决，不擅自把清理/历史重写当下一步。全量审计其他AC与独立Review仍未完成。

备选方案已具体写入 `reports/MATERIAL_DISPOSITION_OPTIONS.md`：完整历史推送仍需材料传播证明；许可不足时建议独立的干净源码快照新分支，保留原main/远端main和全部证据。仅设计，未创建导出/分支/新仓库或释放新Task。下一步等待用户材料信息或方案选择，不自动实施。

当前用户裁决覆盖上述等待许可分支：用户明确“我自己的，但是不传播”。169个JPEG及其压缩外层blob已登记禁止上传（`evidence/push-material-disposition.json`），push=BLOCKED_OWNER_NO_DISTRIBUTION。保留全部本地素材与历史；不再重复索要许可，也不推完整main或3个分批候选。推荐下一步由Codex冻结独立干净源码快照的发布目标与Task；尚未释放、不自动创建分支或push。
