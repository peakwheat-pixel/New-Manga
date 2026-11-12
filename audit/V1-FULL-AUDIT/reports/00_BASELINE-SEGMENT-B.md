# AUDIT-00：段 B 当前产品基线

日期：2026-11-12
固定产品 base：`10e4ee013835605800d3830fb960ae8d3aa04167`
生成审计证据时 HEAD：`c310f01658f99ddc654d3439777b147fe6d3b7e5`
分支：`main`；产品源码相对 base 的净变更：0 个已选清单路径。

## 结果

- 段 B 当前产品已明确为 AD-002 的 Avalonia/.NET + Python Core 架构；原段 A `349e61faff5f93067af5d4ce2d9e394e0d665b8c` 属 Legacy Tauri/React 时期。段 A 证据保持历史，不迁移到段 B。
- 固定 Git tree 共 21,046 个 tracked file；当前源码与构建清单 1,301 项：target source 633、target tests 571、developer tools 42、packaging 17、root config/license 36、CI config 2。每项 `SHA-256` 对应 base commit 的原始 Git blob 字节，详见 `evidence/source-manifest-segment-b.json`。
- 生成时为 `main`；产品文件相对固定 base 无净差异。完整环境、路径范围、计数与排除范围见 `evidence/baseline-segment-b.json`；命令、解释器、时点、HEAD 与 EXIT 见 `logs/audit-00-segment-b.log`。

## 明确排除与历史缺口

- `.tmp.driveupload` 有 2,148 个 tracked 条目，`test_assets` 有 86 个，`apps/desktop/` Legacy 源码有 284 个；均未读取其 blob 内容并未放入当前源码清单。私有漫画及其压缩对象只保留此前材料报告中的元数据级传播证据。
- `archive/`、`verification/`、`audit/`、`doc/`、`docs/`、`experiments/` 不属于本轮有效产品源码清单；树中计数见 baseline JSON。没有扫描 Git 不可达对象、远端实时 ref、全历史路径演化或 GitHub 当前可见性。
- 清单按已定义的目标目录与代码/构建配置扩展名生成，不含二进制资产、SQLite、模型、漫画、通用 `test_assets`、历史 Tauri/Rust UI 实现或完整文档库。
- 环境记录显示 SDK `10.0.401`；AD-002 目标为 .NET 9。AUDIT-00 只记录环境，不据此推定 .NET 构建兼容或测试通过。
- 原 `audit_runner.py` 的 `frontend`、`rust`、`desktop` 目标仍指向 Legacy `apps/desktop/frontend` 与 `apps/desktop/src-tauri`，没有当前 Avalonia/.NET suite。AUDIT-00 未运行产品测试；后续执行前须按当前架构映射有效命令并把旧 suite 明确标成历史或 `NOT_RUN`。

## 状态

AUDIT-00（段 B）：`PASS`，限于当前 Git/environment/source inventory 与上述已披露边界。此状态不表示 AUDIT-01–14、GUI、集成测试、隐私复核或 Release Gate 通过。
