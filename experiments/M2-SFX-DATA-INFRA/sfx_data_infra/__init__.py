"""sfx_data_infra: SFX 训练数据基础设施（M2-SFX-DATA-INFRA / T1a）。

manifest schema（AC1）/ 分组隔离拆分器（AC2）/ 去重+原子写（AC3）/
合成渲染 PoC（AC4）/ 存量资产导入器（AC5）/ CLI（AC6）。

零新依赖：stdlib + PIL + numpy。
"""

SCHEMA_VERSION = "sfx-data-infra/sample@1"
MANIFEST_KIND = "sfx-data-infra/manifest@1"
