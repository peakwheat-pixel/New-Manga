# 稳定规划汇总有界核对（2026-10-08）

## 身份与范围

这是父级 Codex 请求的规划一致性核对，不是产品 Independent Review，不新增 `approved`，不释放或派发实现。核对输入：`REPORT.md`、`ROADMAP.md`、`RESUME.md`、`doc/REBASELINE_PLAN.md` 顶部当前路线；仅以本轮已落盘 `core-audit.md`、`desktop-audit.md`、`plan-audit.md` 校对关键结论，不重新全仓审计，不修改上述文件。

Live Git：`G:/CODEX/New Manga`，`main@e4242ecd419eb0eea098d2f63b40f709aa5caeea`。检查时 Plan modified、审计目录 untracked，另有既有 Qoder/dispatch dirty；这些写入按原作者保留。只新增本文件。产品测试/GUI/构建/模型/API=`NOT_RUN`。

## 结论

**主要事实、条件路线与授权边界一致，未发现将未实现产品面记为 done/PASS 或偷解冻 Reader。交付闭环尚需父级补齐两项恢复/证据事实。** 下列问题针对当前文件字节与落盘状态，不推断最终交付是否随后补齐。

| 编号 | 类别 | 位置与当前事实 | 影响与建议 |
|---|---|---|---|
| PC-01 | 恢复点过时；交付前需更新 | `RESUME.md:7` 为 `ExecutionState: ACTIVE`；`:10-12` 仍“等待审计产物”“继续汇总REPORT/路线图”“规划检查待执行”。当前三份审计、REPORT、ROADMAP和Plan覆盖层均已落盘；`REPORT.md:9,84-88` 将它们作为整体规划结果与恢复材料引用 | 恢复者会被指向已经完成的汇总，而不能直接识别剩余事项，可能重复推演或误把本轮治理dirty视为外部漂移。建议交付前将实际阶段改为汇总已落盘、待规划校验/父级收口（或完成），列出本轮所有受控新增/修改文件、结果与下一确切步骤；仍保留live Git核验与他人dirty保护。不要修改产品Task状态来代替规划ExecutionState |
| PC-02 | 证据引用尚不存在；交付前需补齐 | `REPORT.md:78` 声称“另执行本轮台账/祖先/依赖/链接/范围与空白检查，结果见validation.log”；本次 `Get-ChildItem verification/PROJECT-ROADMAP-20261008` 仅见三审计、REPORT、RESUME、ROADMAP与CSV，**没有 `validation.log`** | 当前读者无法复核该“已执行”声明且链接不可用。父级若正在生成日志，可在收口前真实执行并落盘含环境/HEAD/命令/EXIT的日志；否则将未执行项如实改为待执行/NOT_RUN。不能用本规划核对代替缺少的台账/链接等检查日志 |

PC-01/02不代表产品代码缺陷；本核对不替父级写修订，也不对未落盘日志给 PASS。当前无需产品实施修复。

## 已核对且未发现矛盾的事项

1. **done与能力边界分开。** REPORT明确 UI1仅设计、AC1测试模式不是正式用户入口、DOCTR正式FAIL/B2当轮FAIL、四页完整产品未完成；Plan将105节点标“登记完成”，同时明确不能代表研究质量/四页/发布PASS。台账汇总算术自洽：114+48+5=167，9+13+1+6=29，总计196。未重新核验105份产品测试或独立Review，祖先核验仍按已落盘plan-audit/CSV来源读取。
2. **桌面关键缺口均保留。** Console↔Workbench、Library/SFX section；真实15命令不含Import/StartRun/TaskProjection/Reader/Export；1×1 decoder；TaskProgress占位；第五SFX入口已构建但最新packaged覆盖缺口；GC2已done且G7迁移条件保留；stdio并发/期限只列静态候选。没有把已被后继闭合的page资源/导航/undo重渲染重新记待实施。
3. **Packaged PASS没有越界。** REPORT绑定source=`3d532c1f99e49da703d2076bd67d46b710866637`和installer=`ef617573ab39c0469079203489f4db4af78ae4e3437f8d97d87a3565bb40fa75`；保留Guard没有fresh整包Gate。RG1用户本机接受裁决被尊重，没有强行推翻历史PASS或宣称Win10/完整四页现测通过。
4. **未来范围未偷解冻。** P01–P21全部placeholder且不计入正式196任务；建议Owner不是实际认领；正式release须Task/base/worktree/allowlist/非作者Reviewer。P08用户范围裁决→P16 Reader解冻→P17 UI，跨页/缩略图保持非默认；BJ13阈值0.90/手工改标+skip与Manga109取消被保留；P21删除Legacy是可选另授权。
5. **依赖没有环。** P09/P10/P11在P08范围后设计，P13依赖P09/P11，P14/P16依赖P13，P17依赖P16，P18依赖P10/P13，P19合流P12/P14/P15/P17/P18，P20再合流P03/P06；表与图一致。P13允许deterministic provider先验收，因此未直接依赖P10并非矛盾；真实质量Gate仍由P18要求可用受控模型/endpoint。
6. **恢复安全骨架可沿用。** RESUME要求核Live Git/Plan/STATUS、保留dirty、DRIFT先分析、不reset/clean/stash、不重审全仓、不启动产品Task，路径与base有效。需要PC-01刷新当前工作点，而不是重新创建一套恢复机制。

## 正式范围冻结前的三项澄清建议（不是当前事实错误）

- **P01→P08只应要求取证/处置有结论。** Plan当前解释已能支持这样读。两份原Review找不到时保留NOT_VERIFIED，不能把“必须找回所有历史载体”变成无期限阻断设计。P01是否另有元数据修订Task由Codex决定，不凭图自动修历史文档。
- **“完整四页”依赖用户选择Reader。** 若P08继续暂缓Reader，P19/P20应改为“选定范围E2E/发布验收”；不能删除P17依赖后仍声称四页完整，也不能把Reader记N/A达到完整性。
- **Core已发现的格式/维护/样式边界应进入P08的must/deferred/out。** `core-audit.md:35,40,44-45` 分别记录PDF/MOBI可选parser闭包、`_StubStyleAnalyzer`返回空数组、production ExportService未注入PDF composer、backup/restore/trash生产IPC缺失与停写要求。根REPORT已链接该详细报告，故未定性为遗漏后就宣称完成；但目前P09/P16/P15的粗节点不能自动证明全格式导入/导出、源字体色彩保持或完整用户库备份。正式Task必须明确选取格式、样式保持标准、maintenance是否in/out；若备份恢复进入范围，应用级worker/连接停写Gate单独冻结，数据库备份不能宣传成含原图的完整库备份。

## 下一步与可转发指令

**推荐下一步：Codex在本轮PLAN_ONLY范围收口PC-01/PC-02，再准备P08范围矩阵；不启动任何产品实现。** Owner=Codex，planning材料有界核对由本报告提供；后续正式P08设计Task建议Reviewer=DSH，Task branch/worktree仍待Codex创建。

可直接转发给父级Codex：在 `G:/CODEX/New Manga`、`main`，核对当前HEAD与审计base=`e4242ecd419eb0eea098d2f63b40f709aa5caeea`，保留Qoder/dispatch dirty及其他作者审计文件。仅收口 `verification/PROJECT-ROADMAP-20261008/RESUME.md` 的实际阶段/新增文件/剩余步骤，并真实落盘REPORT引用的规划validation.log（环境、HEAD、命令、EXIT）；未运行项如实NOT_RUN，不改变历史PASS或产品Task。用已有core/desktop/plan审计检查链接、节点依赖、统计与零生产差量，更新最终恢复点；无需全仓审计、产品测试或整包构建。P08只准备must/deferred/out与格式/样式/维护/Reader/Windows裁决选项，正式释放前仍不实施。结果完成后再给用户可恢复交付。

本核对结束后无已释放产品Task，**无需下一步操作（产品实施层）**。是否正式创建P08或R-003验收Task由Lead按用户授权与当前STATUS单独登记。
