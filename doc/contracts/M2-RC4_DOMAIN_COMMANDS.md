# RC-4 域命令面（2026-10-07，Codex 冻结）

来源：M2-C1 §5/§8/§10、M2-SFX-MISROUTE-UI-MITIGATION §4.1–4.4，用户本次授权。仅扩展新架构，既有命令语义不变。C1 rev 1.6 指向本文件；envelope minor 3→4（新增命令）。不释放通用 PipelineRun 命令族或 pin 写命令。

## 命令与 DTO

Tauri 名与 Core wire 名均采用以下 snake_case；Tauri arguments 使用既有 camelCase 转换惯例。

- `list_region_revisions {region_id}` → `{region_id, current_revision_no, revisions: RevisionSummary[]}`，revision_no 升序；未知/软删除 region 为 TARGET_NOT_FOUND。RevisionSummary = `{region_revision_id, revision_no, origin, review_state, is_pinned, restored_from_revision_id: string|null, created_at, region_type, sfx_policy, is_current}`。只读摘要，不传完整快照、路径或图像 bytes。
- `restore_region_revision {region_id, revision_no, expected_revision}` → `{region_id, revision_no, region_type, sfx_policy}`。两个编号均为正整数，expected_revision 必填；未知 region/源 revision 为 TARGET_NOT_FOUND。显式用户恢复复制源完整快照到一笔 NEW restored revision，标记 needs_review 与 restored_from_revision_id，不移动指针回旧 revision，不更改既有历史或 pin。沿现有 restore 语义恢复快照内人工文字和 Lock；当前版本通过事务内 expected_current_revision_id 比较，冲突 INPUT_REVISION_CHANGED 且零写。恢复是用户明确行为，不冒充机器写或反向改标。不得自动解锁、清理历史或覆盖源文件。
- `rerender_page {page_id}` → `{page_id, artifact_id, revision_no, reports: [{region_id,status,skip_reason,font_substituted}], preview: {resource_id, revision}|null, preview_error: string|null}`。同步调用已有 RenderService.rerender_page，不运行 Detect/OCR/Translation/Inpaint，不伪造 PipelineRun。消费当前 clean 和 current final_translation，遵守 SFX skip/manual 与 Region lock 现有门；无 clean=MISSING_REQUIRED_INPUT，页不存在=TARGET_NOT_FOUND，提交冲突=INPUT_REVISION_CHANGED 或 COMPOSITION_BASE_CHANGED，写失败=ARTIFACT_WRITE_FAILED。错误消息固定安全短语，细节仅 stderr。成功追加 translated ArtifactRevision，不覆盖旧 current 文件。preview 为现有 resource channel 可读取的不透明资源标识，绝不将 managed path/base64 交 WebView。预览发布失败不得伪报渲染失败：已提交结果保留，preview=null 与 preview_error 明示，可再次重渲染重试。

## 应用与 UI 约束

1. restore 的 expected_revision 先校验读取编号，再将该 current ID 传入现有原子 seam；所有调用者共享服务层守卫。旧 Python 调用签名允许省略编号，但服务始终保护自己观察到的 current ID。保留所有历史，包括人工文字与 pinned revision。
2. 当前 headless Core 渲染依赖为 object()；本任务授权用已安装 Pillow 提供实际 FontCatalog/Layout/Compositor，保留现有 ports 和 RenderService。Windows 字体从系统字体表/目录由 Core 解析，缺字体明确 substitution；不得引入 Qt、模型、新依赖或通用排版框架。横排、竖排、换行、描边、对齐与 fit 至少可测；能力限制记录，不能以空文本冒烟替代真实文字渲染。
3. 预览仅 Core 将已提交 PNG 发布到现有 derived 只读根并通过 ResourceCatalogStore 登记。Rust 仅向生产 Core 子进程传递同一 catalog/derived 配置，不接触 DB；保持旧 spawn 调用可用。生产 command allowlist/ACL 同步，probe/AC1 面不得获得新命令。
4. Undo 保存改标前 revision_no、改标结果 expected_revision 和原 suspect；10 秒窗口内恢复源 revision，不调用 set_region_type。切页/新操作/过期立即失效；busy 与陈旧响应不得跨页污染。恢复后重新读取 Core 权威列表并恢复原 suspect；失败呈现 typed error，不自动重试或乐观修改。
5. Inspector 常驻历史入口显示摘要/current/pinned/source，显式确认恢复目标；窗外仍可恢复。重渲染成功使用已有 loadPageImageUrl 加载 preview，错误明确显示。三入口解除硬禁用，busy/无目标等资格禁用仍保留。复用现有视觉，不重新设计 A/B/C。
6. React 实际点击成功/失败/过期/切页隔离需可运行检查；仅 SSR/纯函数不算交互闭环。优先复用 testSupport/mockDom，确实不够才在 Task 登记一项测试依赖增加（不自动授权生产依赖）。

## 验证 Gate

必须包含真实 SQLite restore（历史/pin/人工文字/Lock、过期与事务中竞态）、真实生产 headless 文字渲染及 skip 图像像素断言、真实 stdio round-trip、Rust bridge/allowlist/ACL、React 点击与错误可见性、preview resource读取；日志含 shell/解释器/commit/命令/EXIT。既有 test_catalog 122≠97 基线失败单列，不得归零或静默跳过；不修 Legacy。
