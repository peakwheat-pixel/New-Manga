<!-- FEA-09 implementation rework review r1 (r1-rework) -->
# FEA-09 实现 Review r1 返修复核（r1-rework）

- Reviewer：ZCode 独立会话（GLM-5.3），session `sess_b421a1f9-2ab5-4693-90df-2c58d07e0e16`；未参与 FEA-09 实现/返修、I001 裁决、UNFREEZE 起草。
- 只读：未修改仓库/commit/push；reviewed_head `59ad0b9fed912c636bf5e6b46287a4554c95bdee`。

---

全部证据已集齐：4 个子代理定位 + 我亲自核读了 reader.py（I007 关键路径）、infra/importing.py（PDF raster 端口）、HostRuntime.cs（fresh-grant 协议）、source_read_refs.py、resolve.py、secrets.py、entities.py。关键交叉验证：加密 PDF 的 resolve render 面 `document_raster.open(raw)` 无 password 形参（infra/importing.py:315 端口签名确认），而 Host 重试只认 `SOURCE_PASSWORD_REQUIRED`。以下是复核报告。

---

# FEA-09 实现 Review r1 返修复核（r1-rework）

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | ZCode 独立会话（本会话；GLM-5.3）；未参与 FEA-09 实现、I001 裁决、UNFREEZE 起草/返修 |
| 方式 | 静态审查：直读关键源码/测试 + 4 个只读 Explore 子任务定位；**本轮未运行任何测试/构建/门禁**（plan-mode 只读约束） |
| reviewed_head | `59ad0b9fed912c636bf5e6b46287a4554c95bdee`（main，工作树 clean） |
| 对照 | findings=`doc/reviews/FEA-09-impl-r1.md`（reviewed_head `6a164253d`）；处置表=`doc/tasks/FEA-09.md` |
| 契约边界 | C-05 v1.2/C-15 v1.1/C-16 v1.1 已冻结 17/17，本轮不重开 UNFREEZE 语义 |
| 只读声明 | 未修改仓库任何文件、未 add/commit/push、未触碰用户数据 |

## 1. Verdict

**`changes_requested` — P0=0／P1=1／P2=4（另 I011 按约定保留 OPEN 至 closeout）。**

## 2. 逐项判定

| ID | verdict | 依据（关键证据） |
|---|---|---|
| I001 | **CLOSED** | `_visible_page_where`（library.py:394-411）managed=artifact∨copy witness、双 witness 带 `created_at<=t`；get/list 经 `_page_or_view_from_row`（:635-669）managed 列不全回退 PageView→artifact-only 可见、无 witness 行被谓词排除（双向反例测试在）；迁移 union 基线（migrator.py:469-476 `v_ids∣copy_ids`）+断言 1/2/**2b 同事务生产读三路径**（:557-592）/3/4/**5 非空基线强制 verifier**（:660-667，负测在）；资源选择 `get_visible_original_path`（library.py:548-570）original-artifact 优先→copy ref，core_service.py:3492-3498 同序 |
| I002 | **CLOSED** | 提交单元后 `bind_imported_entry`（runtime.py:564-569）+ 读面 `find_bound_for_source`（source_read_refs.py:442-475，source/version/entry 精确、rendition 由 source kind 派生）；`find_for_identity` 生产零调用、`find_for_source` 仅防御回退（生产 registry 具备 bound finder，不可达） |
| I003 | **CLOSED** | runtime.py:398-410 整源 skip 仅 `will_import==0`；部分已绑定逐 entry 补齐（:509-513/:570-573）；`test_partial_import_retry_imports_remaining_pages` 断言与处置表逐字吻合（1→重试 imported=2/skipped=1/共 3 页） |
| I004 | **CLOSED** | scanner.py:391-404 encrypted→structural-only plan；runtime.py:458-467+`_encrypted_participants`（:609-628）解密 rescan 参与页/计数/条目集变化 STALE；pdf_probe.py:56-68 密码编码修复；真实加密 PDF 无密/错密/正确密码测试齐（test_referenced_password.py:322 等） |
| I005 | **OPEN（P1，见 §3）** | zip/cbz 面与 Host 协议成立；**PDF resolve 面密码未接线** |
| I006 | **CLOSED** | folder 经 `bind_imported_entry` 取 Core 分配 `src-*`（测试桩默认不预注册 source_id，走真实分配路径）；`test_folder_import_resolves_through_bound_grant` 通过绑定解析；无路径回退 |
| I007 | **残留 OPEN（P2-1）** | PDF page_size→预算→render、图片 header→预算→load（reader.py:126-128/:139-141，亲读确认）、runtime probe 同序、decoder 零调用负测在；但 `archive.read` 前未检查成员 `file_size`（解压尺寸上限缺失，见 §3） |
| I008 | **CLOSED** | 生产 resolve=prepare→RenditionCache（rendition_cache.py:145-161 命中不解码/:154-158 损坏重建/:80-96 崩溃恢复/LRU/信号量），`source-renditions/` 前缀（:40）+表行（:175-179）；集成测试断言解码计数/损坏重建/前缀；附 P2-4 观察 |
| I009 | **CLOSED** | PlanRecord.book_id（planner.py:45-56/:120-124）+start 复核项目/策略→`SOURCE_PLAN_STALE`（runtime.py:207-217）；policy 分支负测在（batch1:60）；book 改挂分支无专属负测→并入 P2-3 |
| I010 | **CLOSED** | `_STORAGE_ERROR_CODES` 映射（runtime.py:43-46）+转换点（:358-370）保留 failed_sources/pending_pages；`test_project_mismatch_rolls_back_unit` 断言 reason_code/计数/回滚全在 |
| I011 | **OPEN（保留，closeout 前置）** | EV 收敛确实尚未执行；按处置约定保留为 closeout 前置项，不阻塞本轮其余判定 |

## 3. P1 与 P2 详情

**P1-1（I005 PDF 子域，处置不完整）**：`render_entry_png` 收到 Secret-G 明文密码，但 PDF 分支 `document_raster.open(raw)`（reader.py:123）无法传递——documents 端口 `open(self, data: bytes)`（ports.py:59）无 password 形参，infra PdfRaster 对加密 PDF 抛 `DocumentDecodeError("ENCRYPTED")`（importing.py:330-338）。后果链：加密 PDF 导入成功（I004 已修）后，resolve cache-miss 会**先一次性消费 Secret-G（文件已零填充删除）再 render 失败**，且 `ENCRYPTED` 非 `SOURCE_PASSWORD_REQUIRED`，Host fresh-grant 重试（HostRuntime.cs:591-592）永不触发——加密 PDF import→resolve 链路死锁。I005 原文最小修复明含"raster 接口适配"，未做。测试印证缺口：`test_i005_encrypted_resolve.py` 仅覆盖 cbz。
**最小修复**：documents 端口 open 增加 password（或等价适配），infra 传 `pdfium.PdfDocument(data, password=…)`、加密错误转 `SOURCE_PASSWORD_REQUIRED`；补真实加密 PDF import→resolve e2e 测试。

**P2-1（I007 残留）**：`read_entry_bytes` zip/cbz 分支 `archive.read(info, pwd=…)`（reader.py:80）前未检查 `info.file_size`；`max_bytes` 只限容器磁盘字节，解压炸弹成员可先耗尽内存（预算检查在其后）。最小修复：read 前对 `info.file_size` 超限（如 `>max_decode_bytes`）typed 拒绝。

**P2-2（新发现，回归隐患）**：`PageView` 定义了两个 `deleted` property（entities.py:107-109 `return False` 被 :117-119 遮蔽），后者引用不存在的 `deleted_at` 字段——任何 `.deleted` 访问必 `AttributeError`。当前无生产消费方/无测试触达，属编辑残留。最小修复：删除 :117-119。

**P2-3（测试/文档缺口合并）**：a) `find_bound_for_source` 的 typed 拒绝（unbound/错 version）无直接单测；b) I009 chapter 改挂另一 book 分支无专属负测（仅代码条件覆盖）；c) Task 处置表 I005 行仍写"Host 待续/批次 5"，而 `59ad0b9fe` 已提交 Host 实现——下轮处置刷新时更正。

**P2-4（I008 观察）**：RenditionCache 装配失败仅日志并置 `None`（core_service.py:6285-6290），resolve 静默降级 legacy 无预算/LRU/并发约束路径。建议装配失败 fail-closed 或至少能力降级 typed 化。

## 4. NOT_RUN（本轮未执行，不据此判 P1）

- .NET build/全量测试（含 `SourceSecretStoreTests`、`Fea09RealIpcTests`）；真实加密 Host↔Core IPC e2e（commit message 自认"待补"）；folder 真实 IPC。
- Python 套件、`check.ps1`、`verify_pins.ps1`：本轮 plan-mode 只读未复跑；处置表所记"Python 全绿"系作者记录，非本 Reviewer 复现。

## 5. 结论与推荐下一步

返修质量整体扎实：I001/I002/I003/I004/I006/I008/I009/I010 处置成立、可交付；唯 I005 在 PDF 子域不成立（P1），须补 raster 密码接线后连同 I011 EV 收敛一起进入 closeout。Task 不得置 done。

> **DSH**：请原字节归档本报告为 `doc/reviews/FEA-09-impl-r1-rework-r1.md`，登记 changes_requested（P0=0/P1=1/P2=4；I011 保留 closeout 前置）。将 P1-1（PDF resolve 密码接线+raster 端口适配+e2e 测试）与 P2-1/2/3 交原实现会话返修（不得由本会话执行）；P2-4 可登记债务候选由 DSH 裁决。返修后新上下文复核，随后 DSH 最终集成。不重开 UNFREEZE，不 push。