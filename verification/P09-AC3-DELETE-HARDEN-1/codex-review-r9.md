<!-- codex session: 01a15265-c7d0-74a3-b12e-79078ce53de5 | reviewed_head: 6f75041f6 -->

**reviewed_head:** `6f75041f60f93a7ca1cb1a078978edb86564a528`  
**decision:** `changes_requested`  
**findings count:** 2（本轮新增）

## A. R8 的四项发现

1. **已解决。** [Task 第 43 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:43>)：“`[ ] AC4 ... 判 FAIL 并转出`”；该行还说明原实现只绑定 origin，不能证明永久删除可回收。
2. **已解决。** [Task 第 77 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:77>)：“`PARTIAL（判 FAIL 并转出）`”；行内说明测试证明 origin 绑定，但没有覆盖永久删除后残留归零。
3. **已解决。** [Task 第 262 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:262>)写“`8 处读取/导出路径`”；[第 289 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:289>)写明“`7 处比较点 + handle_resolver.resolve_namespace_identity`”。[Handoff 第 96 行](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:96>)也列为 8 处并包含 `handle_resolver`。
4. **已解决。** [Handoff 第 8 行](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md:8>)说明路线 B 下仅在删除路径范围内收口，AC4 判 FAIL 并转出；第 49 行标题为“`探针清单（9 个，全部在库）”，对应表格有 9 行探针；第 95 行写 successor task“已创建”，且该 Task 文件存在于目标分支。

## B. 其他矛盾

**发现两处，文件目前仍不完全一致。**

- [Task 第 182 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:182>)写“**无未关闭 AC**”，但第 43、77、299 行均记录 AC4 未完成、判 FAIL 并转出。
- [Task 第 183 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:183>)称当前 `delivery_head` 是 `4824ed5d...`，但 frontmatter 第 17 行记录为 `1878f0b126e8a0e2603570f9b2009d8b70a259f1`。两者都是有效 commit；第 183 行的现行指针表述与 frontmatter 不符。

## C. 能否关闭

**现在不能。** 最小的下一步是一笔文档修正，统一 Closeout Record：明确记录 AC4 未关闭但已转交，并修正或标明第 183 行的旧指针。修正后可按路线 B **带限制收口**，无需等待 AC4 的独立 Task 完成。

## 验证与新增 findings

- 竞态 probe：注入触发，结果 `SAFE`；异常为 `ImmutablePathViolation`，外部文件存活。
- `tests/storage`：86 passed。
- `tests/core`：558 passed，1 个 deprecation warning。
- 其他 probes 未运行。AC4 的永久删除回收行为本轮 **NOT_VERIFIED**；已检查对应测试，它覆盖 origin、retired 标记和 GC 候选，不执行永久删除。
- `P09` 的 AC3 delete 子条件仍为 `BLOCKED`：已核对目标分支的 `doc/STATUS.md` 与 `doc/tasks/P09.md`。

1. **P1 — Closeout 对未关闭 AC 的陈述错误**  
   [Task 第 182 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:182>)。复现：对照第 43 行的未勾选 AC4，以及第 299 行的“判定为 FAIL 并转出”，与“无未关闭 AC”冲突。

2. **P2 — Closeout 中的 `delivery_head` 过期**  
   [Task 第 183 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:183>)。复现：对照 frontmatter 第 17 行；`git rev-parse` 确认两条哈希都存在，但当前字段分别指向不同提交。

推荐下一步：修正上述两处 Closeout Record 后复审并关闭；保持 P09 AC3 delete 子条件为 `BLOCKED`。我未修改仓库文件，probe 只使用授权的隔离 fixture 目录。