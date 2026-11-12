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

## 段 B（当前产品基线 `10e4ee013835605800d3830fb960ae8d3aa04167`）

- `reports/00_BASELINE-SEGMENT-B.md`：当前架构的 AUDIT-00 基线结论、有效源码范围和历史缺口。
- `evidence/baseline-segment-b.json`：固定 Git/environment、dirty 状态、目录范围和排除计数。
- `evidence/source-manifest-segment-b.json`：1,301 个源码/构建配置条目的 Git blob SHA-1、SHA-256、字节数与分类。
- `logs/audit-00-segment-b.log`：基线清单生成的命令、shell/interpreter、生成时 HEAD、时点与 EXIT。
- `tests/rebaseline_audit00.py`：段 B 基线生成器；只读取所选代码/配置 blob，不读取排除数据目录的内容。
- `reports/TEST-MAPPING-ADJUDICATION-2026-11-12.md`：ZCode 对段 B 当前/Legacy 测试 suite 的只读映射裁决，以及 .NET suite 建议和原始 AUDIT-01–14 清单缺失限制。
- `logs/test-mapping-adjudication-20261112.log`：ZCode session/turn、命令/EXIT 与原始清单定位搜索结果。
