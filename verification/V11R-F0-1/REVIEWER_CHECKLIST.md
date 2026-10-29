# V11R-F0-1 独立审查清单（Reviewer 使用；Owner 未自审）

高风险任务：core-writer 未自审。以下为建议的审查路径与证据锚点；所有结论以源码 + 实测为准，
不以 Owner 描述为准。证据目录：`verification/V11R-F0-1/`。

## 0. 审查入口

```powershell
git log --oneline ba59a6c0d..HEAD
git diff ba59a6c0d..HEAD -- src/ apps/desktop-avalonia/src/NewManga.CoreClient
# 契约
doc/contracts/V11R_REGION_WRITE_CONTRACT.md
# 复跑
python -m pytest -q
python -m pytest -q tests/core/test_region_write_commands.py tests/editing/test_region_write_guards.py
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
```

## 1. 锁语义（最高风险，逐条核对）

1. `set_region_lock`（C075）是否真的产生 revision（D06 §87）？——看
   `service.py::set_locks` 是否走 `_commit_user_or_raise`/commit seam，而不是直接改列。
2. 三把锁各自写到哪里？`translation_locked` 是否同时写 `RegionText.translation_locked` 与
   `Region.translation_locked`（pipeline LockSnapshot 读列）？见 `entities.py::lock_translation` /
   `set_translation_locked`；测试 `test_set_region_lock_creates_revision_and_persists_both_projections`。
3. 锁变更后机器写是否仍被阻止？——人工保护判定在 `RegionText.apply_machine_translation`
   / `service.apply_machine_translation`；本任务未绕过。
4. 重启后锁是否仍在？——`test_lock_and_geometry_survive_a_core_restart`（真实 SQLite + 重新装配）。
5. 是否存在“锁变更被静默吞掉”：冲突路径必须 `INPUT_REVISION_CHANGED` 零写
   （`test_set_region_lock_conflict_has_zero_write`）。

## 2. current / pinned / 历史安全

1. 所有 revision 写是否唯一经 `commit_region_revision` 原子 seam（无第二条写路径）？
   grep `commit_region_revision` / `_commit_user_or_raise`。
2. `pin_revision`（C076）：是否只翻 `is_pinned`、不建 revision、不动 current、不 upsert 历史？
   测试 `test_pin_revision_flips_only_the_immutable_flag`。
3. `delete_region`（C068）：是否只软删、历史/current 仍可寻址？
   测试 `test_delete_region_soft_deletes_without_touching_history`。
4. merge/split：源是否软删且历史保留、新 region 是否从 revision 1 开始？
   测试 `test_merge_regions_...` / `test_split_region_...`。
5. 是否有任何命令删除/覆盖 `region_revisions` 行或用户数据？

## 3. 乐观锁（expected_revision）语义

1. 单 region：`expected_revision` 解析 revision_no → current id，**在 commit seam 事务内二次校验**；
   过期 ⇒ `INPUT_REVISION_CHANGED`、**零写**（不是吞掉冲突继续写）。逐命令测试覆盖：
   delete / save_region_geometry / split / save_manual_translation / confirm / set_region_lock / pin。
2. 多 region：`expected_revisions` 必须恰好覆盖受影响集合；任一过期 ⇒ 整批零写
   （merge / reorder 测试）。
3. `create_region` 无 guard 的理由是否成立（创建无先前 revision）——契约 §1.4/C067。
4. 未知/非正 revision 编号 ⇒ `INVALID_REQUEST` 还是 conflict？核对契约 §1.4 与实现一致
   （实现：未知编号/非 current ⇒ conflict；非正整数入参 ⇒ validation）。

## 4. 数据面/安全

1. 10 条命令的 payload/result 是否含 OS 路径、文件名、base64 图像、managed path？——应无。
2. 是否读写用户源文件 / Managed Copy 内容？——应无（几何只是 DB 坐标）。
3. 错误消息是否只固定短语/typed reason，不含原始异常、路径、用户文本（人工译文只在成功 result 回显）？
4. `INVALID_REQUEST` 是否在任何持久化之前返回（写前 fail-closed）？

## 5. 协议契约

1. minor：10 条命令是否全部 minor=3、`PROTOCOL_MINOR` 未变？——C# 测试 + Python 响应断言。
2. 冻结 66 快照 JSON 是否未被编辑（`git diff ba59a6c0d..HEAD -- verification/HOST-COMMAND-MIGRATION-1` 空）？
3. C042–C047 语义是否未变（`git diff` 只应有新增，既有 handler 未改）？
4. 追加集是否显式（`HostCommandRegistry.RegionWriteCommandNames`）、parity 测试是否派生式
   而非新的 magic number？
5. 几何：wire 归一化点列 → `normalized_to_page_geometry` → 存储页像素 → read 面
   `page_geometry_to_normalized` 是否可 round-trip（`test_create_region_returns_...` 断言）？

## 6. 诚实性（GAP）

核对 `GAPS.md`：GAP-2（文本只读投影缺失）是否属实？是否被伪装成已实现？
GAP-1 是否明确标注“本任务新增”而非既有能力？

## 7. 输出

Review 结论请按 `doc/templates/REVIEW.md`，明确：
- AC1–AC7 逐项 PASS/FAIL/有条件通过；
- 数据安全与锁语义是否放行；
- 是否需要 I1/I2 返修（具体文件/行/测试）；
- 是否允许 DSH 集成到 main（Owner 无 push 权限，最终由 Lead 集成）。
