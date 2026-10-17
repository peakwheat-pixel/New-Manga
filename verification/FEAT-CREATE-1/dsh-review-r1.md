# FEAT-CREATE-1 独立 Review（R1，Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | FEAT-CREATE-1（创建能力 1/4：契约冻结 `CreateBook`/`CreateChapter`）|
| Owner | Codex（codex-dispatch CLI）|
| 交付 | `f4aa895b7`（docs(create): freeze book and chapter IPC contract）+ Handoff + `verification/FEAT-CREATE-1/decision-map.md` |
| 结论 | **approved** |

## 逐项验证

| # | 项 | 结果 |
|---|---|---|
| V1 | 范围 | **PASS**：仅 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` + 任务 + decision-map；**零产品代码** |
| V2 | **AC1 冻结完整性** | **PASS**：M2-C1 升至 **rev 2.8**（Core `minor 7→8`）；`CreateBook {title}`、`CreateChapter {book_id,title,chapter_number?}` **FROZEN**；Tauri `library_create_book`/`create_chapter`；新增 **§5.10** 含完整 wire、**未知字段 fail-closed**、Core 为唯一校验/写入方 |
| V3 | **AC2 安全投影** | **PASS**：成功值按**白名单重建**；错误映射稳定 envelope + host 侧 `LibrarySurfaceError` **封闭投影**；不新增事件；未泄露路径/Secret/原始异常 |
| V4 | **AC3 最小字段面** | **PASS**：作品仅 `title`（无 `shelf_id`，未引入未存在的多书架语义）；**章节只建元数据**，页面文件仍经既有 `ImportPages` + host 只读来源授权 → **未发明路径暴露或任意写入面** |
| V5 | **AC4 后三段草案 + 迁移判断** | **PASS**：给出 Core/host/前端边界与 AC 草案；**核对既有 `books`/`chapters`/`pages` 表与 FK 后判定不需新表/迁移**（故无需用户批准迁移）|
| V6 | 范围克制 | **PASS**：`DeleteBook`/`DeleteChapter` 保持 PROPOSAL，未借机扩大 |
| V7 | 顺带修正文档漂移 | **正向**：发现 M2-C1 顶部状态仍标 2.5 而 P15 已推至 2.7（文档漂移），本修订同步更正并说明 |

## 结论：**approved**
契约冻结严谨：additive、fail-closed、封闭投影、最小字段面、无迁移、范围克制。**批准集成**，并释放 **FEAT-CREATE-2**（Core 实现）。