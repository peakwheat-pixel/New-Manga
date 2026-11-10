# FEA-14-LIB-1 证据索引（书/章元数据编辑与顺序）

- Task：`FEA-14-LIB-1`（FEA-14 S5 LIB 切片；复用 PREQ 预冻结 wire P5–P8）
- Head：`8e39bb72c`（FONT-1 收口后起点；实现提交见下）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 书元数据 | patch 部分字段（其余保留）；title 非空；无书 typed | **MET**：`LibraryService.patch_book_metadata`（白名单 title/author/series_title/description/notes/original_title/publisher；`apply_edit` 保留未提供字段；空 title → ValueError；未知字段 → ValueError；无书 → `BookNotFound`）；wire P5 映射 TARGET_NOT_FOUND/INVALID_REQUEST |
| AC2 章元数据 | kind/custom_rank/number/title/subtitle/notes；非法 kind 拒绝；无章 typed | **MET**：`patch_chapter_metadata`（kind→chapter_type 并维护方向不变量：webtoon→vertical、离开 webtoon→rtl；custom_rank/number/title/subtitle/notes；标题非空；未知字段拒绝）；wire P7 |
| AC3 章重排 | `ordered_ids` 必须全覆盖（缺/多/重复 → typed）；sort_order 连续；读取顺序一致 | **MET**：`reorder_chapters_strict`（重复 → ValueError；集合不等 → ValueError；成功后 `list_chapters` 与请求一致；未知章 → `ChapterNotFound`）；wire P6 |
| AC4 创建带元数据章 | title/kind/number/import_order 落库；返回 chapter_id/title/kind/number；父书不存在 typed | **MET**：`create_chapter_with_metadata`（继承书默认 kind；import_order 覆盖 import/sort order）；wire P8 返回四字段；无书 → TARGET_NOT_FOUND |
| AC5 迁移/契约/门禁 | v12 additive（旧行无损）；P5–P8 按 PREQ §8；inventory EXIT 0；pins 18/18 | **MET**：v12 `chapters.custom_rank`（additive；v9/v10/v11 证据测试与 fea09/fea11 适配后 **1245 passed**）；wire 四命令；inventory **69/76**；C-07 UNFREEZE **v1.5**（`9c1eb974…`，前 pin v1.4 保留）；`verify_pins` 18/18 |
| AC6 证据 | 定向/全量测试、日志 EXIT、NOT_RUN | **MET**：见下表与 NOT_RUN |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-lib.log` | `test_library_metadata.py` + `test_library_wire.py` **7 passed** | 0 |
| `logs/regression-v12.log` | v12 回归：storage+core+fea09+fea11 **1245 passed** | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **874 passed / 0 failed / 11 skipped** | 0 |
| `logs/pins-api.log` | `verify_pins` 18/18、`generate_api_inventory.py --check` EXIT 0（69/76） | 0 |

**实现提交**：Core（schema v12 + service + wire + 测试）与 Host 三层 + C-07 UNFREEZE v1.5（见 git log）。

## 设计说明与 limitation

- 书 tags 关联未在 P5 patch 中做替换（PREQ 的 `tags` 字段留 LIB-2/UI 卡；patch 白名单不含 tags，未知字段会拒绝——已披露）。
- `chapters.custom_rank` 为新增列（v12 additive）；`chapters.chapter_number` 继续承载 P7 `number`。
- 章 kind 变更会同步 reading_direction（webtoon↔vertical 不变量），避免实体校验失败。
- 不做 Volume 实体（PREQ 未纳入，另行裁决）；不做批量重排 UI。

## NOT_RUN（不得记 PASS）

- LIB 可见 UI（书架/工作台账单的元数据编辑与拖拽重排）= NOT_RUN（FEA-14-LIB-2/UI 卡）。
- tags 替换语义（P5 patch `tags`）= NOT_RUN（登记；需明确 tag 关联写语义）。
- Volume 实体 = NOT_RUN（未纳入本卡范围）。
- 真实大库（万级章）重排性能未压测。

## 复现

```powershell
python -m pytest tests/storage/test_library_metadata.py tests/core/test_library_wire.py -q
python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
