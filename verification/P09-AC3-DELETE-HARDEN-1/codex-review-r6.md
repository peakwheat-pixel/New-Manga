<!-- codex session: 01a15218-26f0-7991-a5f3-40de232e38e6 | reviewed_head: 24fcb0f95 -->

# P09-AC3-DELETE-HARDEN-1 第六轮独立复审（R6）

- `reviewed_head`: `24fcb0f95d2a722d9a7aa037502de48b4f973b80`
- `decision`: `changes_requested`
- `findings`: **5**（P1 × 2，P2 × 3）

## 五项裁决

1. **两项 R5b 修复分别堵住了所测竞态。** `remove_managed()` 和 `collect_orphans()` 都通过句柄链重新打开并验证路径段，最后对同一个叶子文件句柄执行删除；没有发现“链内校验后又按原路径名解析”的窗口。另有 `render_preview` 异常清理仍按路径删除，R6 探针确认它可以误删根外文件。
2. **保留 `is_file()` 不会重开外部删除竞态。** 它只控制提前返回；文件存在时，删除仍由句柄链重新验证。它保留的是静态情况下“缺失则跳过、越界则报错”的差异；路径在检查期间变化时，缺失/越界分类本身不保证稳定。
3. **将七个读取/导出路径单独处理是合理的。** 读取需要确定并持续使用可信文件身份，和一次性句柄删除不同。不过目前只有草案，没有正式 Task；而且草案没有纳入已复现的 `handle_resolver` 竞态。
4. **仍有未关闭项。** R5b 两个 P1 删除修复通过了对应探针；R3/R4 的根锚定、缺失组件及探针问题也通过了本轮对应检查。仍未闭合的是 AC4 的真实 Reader 预览生命周期、`render_preview` 异常清理、R5b 的 `handle_resolver` 读取竞态，以及证据 pin 和 Task 交接缺口。
5. **尚未达到 `done` 或集成条件。** 有两个未解决 P1，AC4、AC5 未通过；另有 P2 与未完成的交接和证据项。

## AC1–AC12

| AC | R6 verdict | 依据 |
|---|---|---|
| AC1 | PARTIAL | `tests/core` 通过；本轮未运行 Rust 与前端测试。 |
| AC2 | PASS | `tests/core` 通过，覆盖多目标删除路径。 |
| AC3 | PARTIAL | Core 测试通过；本轮未运行前端逐项重试测试。 |
| AC4 | **FAIL** | 真实 Reader 发布后永久删除，预览仍留在磁盘，且未进入 GC 候选。 |
| AC5 | **FAIL** | 新增探针复现 `publish_original()` 异常清理删除根外文件。 |
| AC6 | PASS | `tests/core` 与 `verify_all.py` 通过。 |
| AC7 | PASS | `verify_all.py` 实际执行查询并通过。 |
| AC8 | PASS | `tests/core` 通过；`verify_all.py` 孤儿扫描为 0。 |
| AC9 | NOT_VERIFIED | 本轮未运行 Cargo 测试。 |
| AC10 | NOT_VERIFIED | 本轮未运行 packaging 测试。 |
| AC11 | PARTIAL | 11 个当前 evidence pin 中 10 个匹配；另有 Handoff 和正式转交 Task 未完成。 |
| AC12 | NOT_VERIFIED | 本轮未运行全量 `pytest tests`；仅运行了指定的 `tests/storage` 与 `tests/core`。 |

## 探针与验证

| Probe | `injection_fired` | `outside_survived` | 结果 |
|---|---:|---:|---|
| `n002-race-probe.py` | False | True | **INCONCLUSIVE**：该探针钩住 `Path.is_file`，当前实现不调用它。 |
| `n002-race-probe2.py` | True | True | SAFE |
| `n004-ancestor-probe.py` | True | True | SAFE |
| `n004-production-order-probe.py` | True（脚本确认 junction 创建成功） | True | SAFE |
| `r5-p1-managed-remove-probe.py` | True | True | SAFE |
| `r5-p1-cleanup-book-files-probe.py` | True | True | SAFE |
| `r5b-p1-remove-managed-race-probe.py` | True | True | SAFE |
| `r5b-p1-collect-orphans-race-probe.py` | True | True | SAFE |
| R6 `publish_original()` 异常清理探针 | True | **False** | **VULNERABLE** |
| R6 `handle_resolver` 重定向探针 | True | True | **VULNERABLE**：句柄身份函数接受了 `outside\derived`，外部字节可读。 |

Reader 生命周期复现不是注入探针：`injection_fired` / `outside_survived` 不适用。真实 `GetReaderProjection` 发布后再执行永久删除，观察到 `retired=False`、catalog 项仍存在、预览文件仍存在、该项不是 retired GC candidate。

指定命令结果：

- `python -m pytest tests/storage -q`：**86 passed**。
- `python -m pytest tests/core -q`：**558 passed**，1 条 Pillow 弃用警告。
- `python verification/P09-AC3-DELETE-1/verify_all.py`：**exit 0**。已拦截其历史 JSON 写入；文件 SHA-256 保持 `67D4DBDB008A0603AA662471E22F80C2AF669FB1EAB784D92CEC52F94D4D6261`，AppData 前后摘要一致。

R6 未修改仓库文件；HEAD 保持不变，Git status 条目数与运行前相同（1591）。

## Findings

### Standards

- **P2 — evidence pin 过期**：[P09-AC3-DELETE-HARDEN-1.md](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:163>) 中 `library.py` 的预期 SHA-256 为 `abfab663…`，当前磁盘值为 `82b0868a…`；11 项中只有这一项不匹配。协作协议将 SHA 不匹配列为检查失败条件：[doc/09_COLLABORATION.md](<G:/CODEX/New Manga/doc/09_COLLABORATION.md:86>)。
- **P2 — 交接尚未正式完成**：当前 Task 仍注明 Handoff 待创建（[Task:98](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:98>)）。七个读取/导出路径指向的 `P09-MANAGED-READ-ROOT-TRUST-1` 目前只有草案，草案明示尚未创建 Task；该节点也未进入 [REBASELINE_PLAN](<G:/CODEX/New Manga/doc/REBASELINE_PLAN.md>)。在正式承接前，不能把这些路径视为已完成转交。

### Spec

- **P1 — `publish_original()` 的异常清理仍可误删根外文件**：[render_preview.py:130](<G:/CODEX/New Manga/src/infrastructure/resource_channel/render_preview.py:130>)，同样模式也在 [render_preview.py:88](<G:/CODEX/New Manga/src/infrastructure/resource_channel/render_preview.py:88>)。复现：`pages_dir.resolve()` 通过后将 `pages` 换成指向外部目录的 junction，再用缺失源文件调用 `publish_original()`。注入成功，触发 `FileNotFoundError`，随后 `target.unlink()` 删除了外部 `known.png`。
- **P1 — AC4 的真实 Reader 预览没有随永久删除退休**：[core_service.py:1977](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1977>) 每次真实 Reader 请求发布带 `retired=0` 的随机 key；永久删除只清理确定性的 `page-original-*` 项（[library.py:1124](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1124>)）。本轮真实调用复现：删除返回成功，但译图文件和 catalog 项都保留，且不在 retired GC 候选中。这推翻了以 rerender rotation 测试关闭 F-002 的依据。
- **P2 — R5b 的 `handle_resolver` 竞态不在七项转交范围内**：[handle_resolver.py:609](<G:/CODEX/New Manga/src/infrastructure/resource_channel/handle_resolver.py:609>) 先 walk，再 `resolve()`，最终按已重定向后的路径比较（[handle_resolver.py:616](<G:/CODEX/New Manga/src/infrastructure/resource_channel/handle_resolver.py:616>)）。本轮在首次 walk 后注入祖先 junction，函数仍接受并返回外部路径；应纳入正式读取安全 Task 或另行承接。

## 集成结论

**明确答复：不建议标为 `done`，当前不能批准集成。** `P09` 的 AC3 delete 子条件仍为 **`BLOCKED`**，本轮没有改变该状态（[P09.md:59](<G:/CODEX/New Manga/doc/tasks/P09.md:59>)）。

推荐下一步：保持本 Task 为 `in_review` / `changes_requested`，交 Owner `dsh` 修复两个 P1、把 `handle_resolver` 纳入正式读取安全范围、更新失配 pin 并补齐 Handoff；随后固定新 head 再复审。