# 证据索引

- evidence/baseline.json：Git/环境。
- evidence/source-manifest.json：源码/config路径、SHA256、语法结果。
- evidence/static-summary.json：扫描统计和例外。
- logs/：完整执行命令、解释器、EXIT、耗时。
- reports/PUSH_READINESS.md：固定历史范围、未提交归属、推送阻断与后续指令。
- evidence/push-manifest.json：推送候选 SHA、阻断项和证据指纹（不表示上传授权）。
- evidence/push-history-scan.json：全历史新增 blob、压缩 Git 对象与 ZIP 的脱敏扫描。
- evidence/push-material-provenance.json：命中裁定、registry 比对与材料来源缺口。
- evidence/push-worktree-ownership.json：6 个既有 P04 日志的保护指纹。
- logs/push-preparation-checks.json：本轮登记、扫描自检与治理检查结果。
- reports/MATERIAL_CLEARANCE.md：4个合成PNG精确溯源、169个JPEG关联证据与34份数据库只读核查，当前材料阻断裁定。
- evidence/push-material-inspection.json：历史tree路径、图像头、源manifest/hash、逐库结构/计数与限制（不含记录原文）。
- tests/inspect_push_materials.py：复跑材料核查及只读自检；派生SQLite副本只保留在workspace task-env。
- logs/push-material-checks.json：本轮材料核查、自检和治理检查的实际argv/exit。
- reports/MATERIAL_DISPOSITION_OPTIONS.md：完整历史/独立干净快照/暂不推送的具体方案；仅设计，待用户裁决，未释放实施。
- evidence/push-material-disposition.json：用户“不传播”裁决及169个JPEG/压缩外层blob的禁止上传指纹；本地保留。
