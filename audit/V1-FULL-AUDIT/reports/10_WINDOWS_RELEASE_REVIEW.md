# 10 Windows 构建与交付审查

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**阶段结论：** PARTIAL（AUDIT-12）。

## 已验证

- 在 AUDIT-09 使用的 current product tree 上运行 Avalonia Release configuration build：EXIT 0、0 warnings / 0 errors；从未安装的 Release build output 启动 GUI 作 AUDIT-09 观察。
- Python sidecar 目标路径存在。
- 交付 inventory 仅读取 workspace 中旧包的目录/大小/哈希/metadata。2026-10-26 与 2026-10-28 的 zip/setup 不是当前固定产品基线的交付证明；历史 setup SHA-256 与其 build-info 记录一致，metadata 标记 NotSigned。
- AUDIT-12-CAND-001 记录 publish.ps1 默认 repo 内输出路径和递归清理调用。脚本未执行，没有证明发生误删。

## 未验证 / NOT_RUN

本 Task 明确不执行安装、发布或卸载。没有当前基线 single-file publish / installer、模型资源完整性核验、干净 Windows 安装、admin/non-admin、中文路径、缺少 runtime、安装后启动/卸载或当前包 provenance 验证。历史包未安装、启动、解压或执行。

## 证据

- reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md
- tests/audit12_delivery_inventory.py
- logs/audit12-delivery-inventory-20261112T223042315179Z.log
- logs/audit09-ui-build-20261112T213917Z.log

现有 Release build 成功不能外推为安装包或 Windows 发布通过；Release Gate BLOCKED。
