# Studio · Page 消费指南（F0-1 写命令 + F0-2 文本读投影）

- 面向：`ui-studio`（Studio · Page 模式实现）与 `core-bridge`（IHostController 便捷方法如需包装）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` v1.2（C067–C077）
- 状态：F0-1 + F0-2 + I1 在同一分支 `v11r/region-write`；合并进 main 后即可接入（以 Lead 合并通知为准）
- 禁止：UI 直连 SQLite / 任意 OS 路径 / Python Core 内部对象；全部经 Host/IPC

## 1. 可用命令一览（全为 `core` 通道、minor=3、C# 命令名与 Core 同名）

| 用途 | 命令 | 入参（snake_case） | 返回（真实投影） |
|---|---|---|---|
| **首帧载入整页（推荐唯一读）** | `list_page_region_texts` | `page_id!`；`region_ids?`（严格过滤） | `{page_id, page_size: {width,height}\|null, regions: RegionTextDetail[]}` |
| 最小列表（仅需要 5 字段时） | `list_regions` | `page_id!` | `{regions: [...], page_size}`（无文本） |
| 历史摘要 / 恢复 | `list_region_revisions` / `restore_region_revision` | `region_id!`（+`revision_no!`,`expected_revision!`） | revision 摘要 / 恢复后有效状态 |
| 新建 Region | `create_region` | `page_id!`；`geometry{points}!`；`region_type?`；`reading_order?` | `{region_id, revision_no, reading_order, region_type, sfx_policy}` |
| 删除 Region | `delete_region` | `region_id!`；`expected_revision?` | `{region_id, deleted:true}` |
| 几何编辑 | `save_region_geometry` | `region_id!`；`geometry!`；`expected_revision?` | `{region_id, revision_no, geometry}` |
| 合并 | `merge_regions` | `page_id!`；`region_ids!`(≥2)；`expected_revisions?` | `{region_id, revision_no, reading_order, region_type, sfx_policy, deleted_region_ids}` |
| 拆分 | `split_region` | `region_id!`；`parts!`(≥2 点列)；`expected_revision?` | `{source_region_id, source_deleted, regions[]}` |
| 手动排序 | `reorder_regions` | `page_id!`；`ordered_region_ids!`（全排列）；`expected_revisions?` | `{page_id, regions[]}` |
| 保存人工译文 | `save_manual_translation` | `region_id!`；`edited_translation!`（允许空串）；`expected_revision?` | `{region_id, revision_no, review_state, text{四轨}}` |
| 确认终稿 | `confirm_region_final` | `region_id!`；`expected_revision?` | 同外形，`review_state="confirmed"` |
| 三锁 | `set_region_lock` | `region_id!`；`region_locked?`/`translation_locked?`/`inpaint_locked?`（至少一）；`expected_revision?` | `{region_id, revision_no, review_state, 三锁}` |
| pin revision | `pin_revision` | `region_id!`；`revision_no!`；`pinned!`；`expected_revision?` | `{region_id, revision_no, is_pinned, current_revision_no}` |
| 重渲染（既有） | `rerender_page` | `page_id!` | 页产物 revision / preview |

几何 wire 形状：`{"points": [[x,y], ...]}`，**归一化 0..1**（2 点=矩形，≥3 点=多边形）；回读形状
`{"bbox":[x,y,w,h], "polygon":[[x,y],...]}` 同为归一化。

## 2. C# 侧消费方式（接入点）

```csharp
// 命令入口（HostRuntime 已暴露 HostCommandDispatcher）：
var result = await hostRuntime.Commands.InvokeAsync("list_page_region_texts",
    RegionWritePayloads.PageTexts(pageId), cancellationToken);

// 读面严格解析（F0-2 提供；缺字段抛 FormatException，不静默空值）：
var projection = RegionPageTextProjection.Parse(result.Value);
foreach (var region in projection.Regions)
{
    // region.Text.OcrText / MachineTranslation / EditedTranslation / FinalTranslation / FinalSource
    // region.Locks.RegionLocked / TranslationLocked / InpaintLocked
    // region.ReviewState / Origin / RevisionNo / CurrentRevisionId
    // region.IsPinned / PinnedRevisionNos
    // region.Geometry?.Bbox / Polygon（null 只在页行不可用的真实情形）
}
```

- `RegionWritePayloads` 若不存在可由 UI 用 `JsonSerializer`/`JsonDocument` 构造 payload；payload 键必须与上表一致
  （`HostCommandDispatcher` 会做发帧前校验，非法值在发出前抛 `HostCommandInvalidArgumentsException`）。
- 失败：`InvokeAsync` 抛 `CoreOperationException`（`Code` = typed code）或 `SidecarException`；
  按 §4 分类处理，不要吞掉 conflict。

## 3. 首帧载入（1 次命令，禁止 N+1）

1. 用户选中页 → **只调用一次** `list_page_region_texts {page_id}`；
2. `page_size == null`（未知页/不完整页行）→ 显示空状态 + 重试，不要用 0 或默认值伪造几何；
3. `regions == []` 且无错误 → 真实「该页无 region / 未知 page」空数据（C043 惯例），不是失败；
4. 文本：`text` 是**真实持久值**——未编辑 region 的 `ocr_text=""`、`final_source="none"` 就是真实空稿，
   不得显示成“加载中”；读取失败（error/exception）则显示“载入失败 + 重试”，**绝不能把失败当空稿**；
5. 选中/刷新单个 region 可带 `region_ids` 严格过滤（未知/跨页 id → `TARGET_NOT_FOUND`）。

## 4. 写操作的时机、`expected_revision` 与失败处理（强制约定）

**通用规则**：每个写请求都带上一次读到的 current `revision_no`（`RegionTextDetail.RevisionNo` /
写命令返回的 `revision_no`）。收到 `INPUT_REVISION_CHANGED` 时：

- **不要自动重试写**；重新 `list_page_region_texts`（或 `list_regions`）刷新，
- 若用户的操作仍适用，提示「内容已在别处更新」并由用户确认后再执行（用新 revision）；
- 冲突是正常并发语义，不是程序错误，不得静默吞掉或乐观覆盖。

| 用户动作 | 命令 | `expected_revision` | 成功后 UI | 失败处理 |
|---|---|---|---|---|
| 画布框选新建 | `create_region` | 无（创建无先前 revision） | 用返回 `region_id/revision_no` 立即渲染；可局部刷新 | INVALID_REQUEST=UI bug（几何退化/越界）；TARGET_NOT_FOUND=页已删 |
| 拖拽/缩放结束 | `save_region_geometry`（防抖后一次） | 上次 `revision_no` | 用返回 `geometry` 更新覆盖层 | conflict→刷新+用户确认；INVALID_REQUEST=几何非法 |
| 合并选中 | `merge_regions` | `{每个源 region: revision_no}` 必须全覆盖 | 移除源、插入新 region；清空选择 | conflict→刷新；TARGET_NOT_FOUND=源已删 |
| 拆分 | `split_region` | 源 `revision_no` | 用 `regions[]` 渲染 parts | 同上 |
| 手动排序拖放 | `reorder_regions` | `{每个 region: revision_no}`（全量） | 按返回顺序重排 | conflict→刷新并提示 |
| 保存人工译文 | `save_manual_translation` | 上次 `revision_no` | 用返回 `text`/`review_state` 更新检查器 | INVALID_REQUEST=载荷错误；空串是合法的“清空人工稿” |
| 确认终稿（Enter） | `confirm_region_final` | 上次 `revision_no` | `review_state=confirmed`，按返回 `text.final_*` 更新 | conflict→刷新后再次确认 |
| 锁开关 | `set_region_lock`（只发变化的字段） | 上次 `revision_no` | 用返回三锁更新角标/检查器 | 同上 |
| 历史页签 pin/unpin | `pin_revision`（`revision_no` 为目标历史号） | 可选（守卫 current 指针） | 用返回 `is_pinned/current_revision_no` 更新 | TARGET_NOT_FOUND=历史号不存在/region 已删 |
| 删除 Region | `delete_region` | 上次 `revision_no` | 移除该 region 覆盖层 | **UI 先二次确认**；二次调用会 TARGET_NOT_FOUND（安全失败） |

**幂等/重试**：geometry/manual/confirm/lock/merge/split 都是 append-only（重试会多一条 revision），
所以“网络/超时不确定”时先刷新再决定，不要盲目重发；`reorder_regions` 相同顺序是效果幂等；
`pin_revision` 幂等；`delete_region` 二次调用安全返回 not_found。

## 5. 锁与文本展示约定

- **Translation Lock（人工保护）**：以 `RegionTextDetail.Text.TranslationLocked` 为准（与既有 manual save
  语义一致）；`RegionTextDetail.Locks.TranslationLocked` 是 region 级投影（pipeline LockSnapshot 读它）。
  **既有 manual save 只写文本级、不改 region 列（GAP-3，保持现状）**——所以二者可能不一致，UI 不要把
  两者混为一个开关；显示「人工保护」用 `Text.TranslationLocked`，显示「区域快照锁」用 `Locks.*`。
- 显式 `set_region_lock` 会同步两个投影；merge/split 会继承“有效锁”（region 级 OR 文本级）并写双投影
  （I1/P1-3）。合并/拆分后仍锁定的 region 不应再出现机器翻译覆盖。
- `review_state` / `is_pinned` / `origin` / `revision_no` 全部来自 current revision，不要本地推算。

## 6. 错误分类 → UI 处理

| `code` | category | UI 处理 |
|---|---|---|
| `INVALID_REQUEST` | validation | 视为前端/参数 bug：提示操作无效并记录诊断；不要自动重试 |
| `INPUT_REVISION_CHANGED` | conflict | 刷新当前页真实状态 + 提示“内容已更新，请确认后重做”；不写 |
| `TARGET_NOT_FOUND` | not_found | 对象已删/不存在：刷新列表并移除本地对象；不重试 |
| `UNKNOWN` | internal | 显示“操作失败，可重试”；保留用户编辑草稿；记录日志（不含路径/用户文本明文） |
| `INVALID_ARGUMENTS`（Host 本地，未发 Core） | validation | UI bug：不发送；修正 payload 构造 |
| `NOT_READY` / sidecar 异常 | 环境 | 显示“Core 未就绪”，不要降级成本地伪造数据 |

## 7. 边界与已知限制（不得伪造）

- **page/book ACL**：项目未定义按书授权；单 region 命令按 id 定位。**UI 只传自己已加载的 page/region id**；
  跨书 id 的授权由 Host 未来 ACL 承担（契约 §3 安全边界）。本次不加假授权。
- 文本读面已由 F0-2 关闭 GAP-2：**不要再为 Studio Page 做 NotWired 占位**；若 `list_page_region_texts`
  返回错误，按 §6 显示载入失败。
- `IHostController` 的强类型便捷方法属 core-bridge 写域；UI 可直接消费 `HostRuntime.Commands`（或等其包装），
  不要绕过 Host 直连 Core。
- 契约 v1.2 与 I1 复审清单：`verification/V11R-F0-1-I1/{README,REVIEW_CHECKLIST}.md`。
