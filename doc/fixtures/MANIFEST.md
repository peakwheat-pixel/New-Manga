# Fixture 素材清单

状态：**全部未取得（missing）**。当前**未取得任何素材**，仓库中不存在也**不得提交**任何未授权的漫画原图（[D07 §98](../07_NON_FUNCTIONAL_REQUIREMENTS.md)）。本文件只登记素材元数据、许可、生成方案与预期属性。

依据：[D07 §98 最小真实测试资产集](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[D07 §99 性能 Benchmark 数据集](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[TASK-003 验收方法与素材规范](../verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md)。

## 1. 字段定义（必需字段）

| 字段 | 含义 | 取值规则 |
|---|---|---|
| `ID` | 素材唯一标识 | `FX-*`（功能素材）/ `DS-*`（数据集）；一经登记不得重命名 |
| `场景` | 覆盖的测试场景 | 对应 D07 §98 的场景或验收规范中的用途 |
| `来源/许可` | 素材出处、来源类型与许可状态 | 见 §2 的来源类型与许可规则 |
| `生成方式` | 确定性生成脚本或取得途径 | 脚本名与参数摘要；不得依赖随机不可复现过程 |
| `预期属性` | 供验证断言的稳定属性 | 尺寸、编码、Region/Page 数量级、元数据规模等；不得填写未测量的实测值 |
| `Hash` | 内容指纹（SHA256） | 未取得写 `NOT_AVAILABLE`；取得后填 64 位小写十六进制 SHA256 |
| `状态` | 素材生命周期 | `missing` / `available` / `rejected` |

状态枚举：

```text
missing    尚未取得（未取得素材的唯一合法状态；本清单当前全部为此状态）
available  已取得，且许可明确、生成方式可复现、Hash 为真实 SHA256
rejected   评估后不采用（保留记录，说明原因）
```

**Task AC2 要求"未取得素材标缺失"**：只要素材本体尚未生成或取得，状态只能是 `missing`。本清单**不设**"已规划但未取得"的第三态——生成或取得方案写在 `生成方式` 列，`状态` 只描述素材本体的实际存在情况。任何 `missing` 条目都不得用于 PASS 证据。

## 2. 来源类型与许可规则

**`来源/许可` 只允许以下 allowlist 取值**；任何其他值——包括未知来源、明确未授权、`待定`、空值或自造类型（如 `pirated / unknown`）——一律拒绝，相关条目不得标 `available`：

| 允许值 | 类型 | 生成 / 取得要求 | 许可依据 |
|---|---|---|---|
| `generated / 自制（项目生成）` | 项目自制 | 标为 `available` 时必须给出**生成脚本路径与参数**（固定种子） | 无需外部许可 |
| `acquired / CC0` | 外部取得 | 标为 `available` 时必须给出**取得途径与版本** | 公有领域声明（CC0） |
| `acquired / 用户授权` | 外部取得 | 标为 `available` 时必须给出**取得途径、版本与授权依据** | 用户授权的范围与来源记录 |

不在 allowlist 内的行（无论是否已取得）都不得用于任何 PASS 证据；验证脚本对**所有**库存行校验 allowlist，而不是只检查 `available`。

**`available` 的强制条件**（三项同时满足，缺一不可）：

1. `来源/许可` 命中 §2 的 allowlist（仅项目自制、CC0、已记录用户授权）；
2. `Hash` 为真实 64 位小写十六进制 SHA256（不得为 `NOT_AVAILABLE` 或占位值）；
3. `生成方式` 非空、非占位，且满足对应类型要求：`generated` 必须同时给出**脚本路径与参数**；`acquired` 必须同时给出**取得途径、版本与授权依据**。

`missing` 行的 `生成方式` 只描述计划方案即可（脚本实体由后续获授权 Task 提交）；一旦标为 `available`，上述三项即成为硬性条件。

未满足上述任一条件的条目必须保持 `missing`；把未取得素材标为 `available` 属于证据造假，验证脚本会同时拒绝许可、Hash 与生成方式三项中的任何缺口。

## 3. 功能与场景素材

| ID | 场景 | 来源/许可 | 生成方式 | 预期属性 | Hash | 状态 |
|---|---|---|---|---|---|---|
| `FX-MANGA-BW-001` | 日漫黑白页，含横排与竖排对白 | generated / 自制（项目生成） | 合成脚本绘制对话框、竖排文本、网点背景 | 约 1200×1800 px、PNG 灰度、≥8 Region、含 2 处竖排 | NOT_AVAILABLE | missing |
| `FX-MANGA-SCREEN-002` | 黑白网点（复杂底纹） | generated / 自制（项目生成） | 合成网点图案 + 文本叠加 | 约 1200×1800 px、PNG、网点覆盖率固定 | NOT_AVAILABLE | missing |
| `FX-MANGA-SFX-003` | 复杂拟声词（艺术字） | generated / 自制（项目生成） | 手绘风格字形合成 | 含 ≥3 个 `region_type=sfx`，含描边与渐变 | NOT_AVAILABLE | missing |
| `FX-MANGA-TB-004` | 竖排对白专项 | generated / 自制（项目生成） | 竖排文本列合成 | 单页 ≥6 竖排列，列间距固定 | NOT_AVAILABLE | missing |
| `FX-KR-WEBTOON-005` | 韩国彩色 Webtoon | generated / 自制（项目生成） | 彩色长条合成 + 韩文文本 | 约 800×6000 px、PNG 彩色、含横排韩文 | NOT_AVAILABLE | missing |
| `FX-WEBTOON-LONG-006` | 超长 Webtoon（Dataset D） | generated / 自制（项目生成） | 分块合成后拼接 | 约 1600×200000 px、PNG、单逻辑 Page | NOT_AVAILABLE | missing |
| `FX-PNG-ALPHA-007` | 透明 PNG | generated / 自制（项目生成） | Alpha 通道合成 | 含半透明与完全透明区域，RGBA PNG | NOT_AVAILABLE | missing |
| `FX-JPEG-008` | JPEG 有损压缩 | generated / 自制（项目生成） | 由 001 导出为 JPEG（固定质量） | 有损压缩、固定 quality 参数、含压缩伪影 | NOT_AVAILABLE | missing |
| `FX-UNICODE-009` | Unicode 文件名 | generated / 自制（项目生成） | 文件重命名（日文/韩文/中文/emoji 组合） | 文件名含多脚本字符与空格，路径长度受控 | NOT_AVAILABLE | missing |
| `FX-DUP-010` | 重复图片 | generated / 自制（项目生成） | 由 001 生成字节级副本与近似副本 | 至少 1 组完全相同、1 组仅元数据不同 | NOT_AVAILABLE | missing |
| `FX-CORRUPT-011` | 损坏图片 | generated / 自制（项目生成） | 截断/篡改头部字节 | 至少 3 种损坏形态（截断、头部损坏、CRC 错误） | NOT_AVAILABLE | missing |
| `FX-MANY-SMALL-012` | 大量小图 | generated / 自制（项目生成） | 批量生成小尺寸页 | ≥500 张小图（可复用同一模板，尺寸固定） | NOT_AVAILABLE | missing |
| `FX-LARGE-SINGLE-013` | 大分辨率单图 | generated / 自制（项目生成） | 高分辨率合成 | 约 8000×12000 px、PNG | NOT_AVAILABLE | missing |
| `FX-META-LARGE-014` | 大 metadata（Dataset E） | generated / 自制（项目生成） | 直接生成 SQLite 元数据（无真实图片或占位文件） | 2,000 Book / 20,000 Chapter / 100,000 Page 记录 | NOT_AVAILABLE | missing |

## 4. 基准数据集（性能与容量）

| ID | 场景 | 来源/许可 | 生成方式 | 预期属性 | Hash | 状态 |
|---|---|---|---|---|---|---|
| `DS-A` | 普通日漫 | generated / 自制（项目生成） | 由 `FX-MANGA-BW-001` 复制并生成页码/Region 元数据 | 50 Page、每页约 10 Region | NOT_AVAILABLE | missing |
| `DS-B` | 大 Chapter（D07 §99 基线） | generated / 自制（项目生成） | 由模板批量生成 + 缩略图与 metadata | 500 Page，含缩略图与元数据 | NOT_AVAILABLE | missing |
| `DS-B2` | AC-CAP-002 专用大 Chapter | generated / 自制（项目生成） | 在 DS-B 模板上扩展到 1000 Page 并生成元数据 | 1 Chapter ≥1000 Page，含缩略图占位 | NOT_AVAILABLE | missing |
| `DS-C` | Region 压力 | generated / 自制（项目生成） | 单页叠加 200 个 Region 标注 | 1 Page、200 Region | NOT_AVAILABLE | missing |
| `DS-D` | Webtoon（AC-CAP-004） | generated / 自制（项目生成） | 复用 `FX-WEBTOON-LONG-006` | 1 Page、约 1600×200000 px | NOT_AVAILABLE | missing |
| `DS-E` | Library（AC-CAP-001） | generated / 自制（项目生成） | 复用 `FX-META-LARGE-014` | 2,000 Book / 20,000 Chapter / 100,000 Page | NOT_AVAILABLE | missing |

**容量 AC 的数据集路由**：`AC-CAP-001 → DS-E`、`AC-CAP-002 → DS-B2`、`AC-CAP-003 → DS-C`、`AC-CAP-004 → DS-D`（另见[验收规范 §9](../verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md)）。

## 5. 生成与校验规则

- 项目生成（generated）素材必须由**确定性脚本**生成（固定随机种子、固定参数），脚本随对应实现/实验 Task 提交；素材本体按需生成并校验 Hash。
- 生成脚本必须记录：脚本路径、提交、参数、输出 Hash、生成环境；同一参数重复生成必须得到相同 Hash。
- 外部取得（acquired）素材必须先确认许可，再登记取得途径与版本；许可为 `待定` 时不得进入 `available`。
- 素材入库前必须完成：许可确认、体积评估（避免超大二进制进入 Git）、SHA256 登记。
- 体积超过仓库策略的素材（如 `FX-WEBTOON-LONG-006`、`DS-B`、`DS-B2`、`DS-E`）默认**按需生成**，不入库；只提交脚本与本清单记录。
- 素材变更必须更新本清单的 `Hash` 与 `状态`，不得静默替换。

## 6. 许可与合规

- **不得提交未授权的漫画原图或扫描件**（D07 §98）；`acquired / 待定` 的素材不得用于任何 PASS 证据。
- 如后续引入用户提供或第三方素材，必须在该条目的 `来源/许可` 写明授权范围与来源，必要时先在 Task 中取得用户或 Codex 确认。
- 涉及真实作品的 OCR / 翻译 / Inpainting 质量评估，必须使用授权素材；未取得时对应质量项结果为 `BLOCKED` 或 `NOT_RUN`，不得用近似素材冒充。

## 7. 当前状态摘要

| 项 | 数量 | 说明 |
|---|---|---|
| 已取得（available） | 0 | 仓库内无任何素材文件 |
| 未取得（missing） | 20 | 14 个功能素材 + 6 个数据集；生成方案见各行 `生成方式` |
| 已拒绝（rejected） | 0 | — |

素材取得与 Hash 登记由后续获授权 Task 执行；本文件当前不构成任何质量或性能证据，也不构成任何验收结果（结果以 [D13](../13_ACCEPTANCE_TRACEABILITY.md) 为准）。
