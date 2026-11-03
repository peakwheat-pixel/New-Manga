---
task_id: FEA-08
author: ZCode CLI（impl session，2026-11-03）
kind: handoff
delivery_scope: 隔离原型 + 技术报告 + 证据（无生产代码改动）
---

# FEA-08 实施 Handoff（impl → Review/DSH）

## 交付概览

- **范围**：严格按 scope-r2 approved 冻结 AC（H4/H5/H6 隔离原型 + 能力矩阵 + 技术报告）；未实施生产 Source/导入、Host grant、Core/DB、UI；未触碰真实库/用户文件/AppData；未 push。
- **结论**：AC-1～AC-4 全部 MET（逐项见下）。矩阵计数 PASS 15 / LIMITED(mocked) 30 / LIMITED(inferred) 10 / UNAVAILABLE(inferred) 5；mock/inferred 无一记 PASS。

## 逐 AC 结果

| AC | 结论 | 关键证据 |
|---|---|---|
| AC-1（H4） | **MET** | 10 场景 measured（`results/h4_results.json`）：①digest 取自同一已验证句柄，读取前后 volume serial+file index+size/mtime 比对；②中途替换/写入只出现 unavailable（S4，含混合流反证）或完整旧 digest（S3b/S6/S7，含"按路径另开=新内容"反证）；③内存映射写两时序实测——**tolerant 模式 mtime 盲区 → undetected_mixed 如实登记为 UNAVAILABLE，strict 模式写者被打开层拒绝（S2/S5c）→ NTFS PASS(strict)** |
| AC-2（H5） | **MET** | 11 场景（9 measured PASS + 2 LIMITED(mocked)）（`results/h5_results.json`）：判定操作双向执行（保留/digest 逐位还原）；覆盖 :512–:514 全分支（含路径被替换 R5/R5b、结果未知 R6b、目录回收 R2/R3）；未调用任何清空类 API（fwin 不封装）；回收站条目测试后全部还原并删除（restore_log 5 条，G: 0→0 零残留）；模拟中断恢复=receipt+文件系统事实核对、零 destructive 重发 |
| AC-3（H6） | **MET** | 15 场景 measured（`results/h6_results.json`）：exact/candidate 二分+逐场景 digest 类型；文件夹成员身份+digest（重命名仅候选）；容器成员 digest（重编码 exact、重复名独立 occurrence→歧义仅候选）；GIF 仅首帧（反证成立）；PDF 页码+渲染参数记录（pdfium 153.0.7999.0/150dpi/RGB8）；加密格式走预生成 fixture+SHA-256（7-Zip 生成，未引入 pyzipper；AES 读取不可用如实登记）；golden fixtures 入库 `verification/FEA-08/fixtures/`（21 项+manifest） |
| AC-4（交付完整） | **MET** | 二维矩阵（4 卷类型 × 5 输入类别 × 3 能力）`results/capability_matrix.{json,md}`；每项 measured/mocked/inferred 标注；mock≤LIMITED(mocked)；报告含依赖/许可（PyMuPDF AGPL 仅研究用不进闭包、pdfium BSD 为生产候选）；**无生产代码改动**（git diff --name-only 仅 allowed_paths，见下） |

## 关键实测发现（进生产设计须吸收）

1. **H4**：strict 共享（不授 FILE_SHARE_WRITE）在打开层挡住一切写者；覆盖式替换（REPLACE_EXISTING）对任何打开句柄一律 error 5；**mmap 写不更新 mtime → 宽容共享下混合流假成功盲区（两时序复现）→ 生产 lease 必须 strict-only 或补 USN/双读**。
2. **H5**：SHFileOperation 批量**遇错短路**（后续项不处理）→ DeletePlan 必须逐项事实核对；Win11 `$I` v2 = 24B 头 + uint32 路径长（含尾 null）+ UTF-16，与流传格式不同。
3. **H6**：容器字节无关的成员级 digest 匹配、PDF 页渲染 digest（重生成 exact）全部成立；AES ZIP 标准库不可读（需 pyzipper，产品裁决）。

## 产物与指针

- 技术报告：`doc/research/FEA-08-source-capability.md`
- 证据：`verification/FEA-08/`（results 7 件 / logs 6 件 / fixtures 21+manifest / prototype_hashes.txt 14 脚本 SHA-256）
- 原型（非 Git）：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（14 脚本；复现 `python run_all.py`，tmp 运行后清理）
- 门禁：dotnet build/test 基线 1292/0/57（见 Task 卡记录）；check.ps1 / verify_pins.ps1 结果见 Task 卡

## 实施边界自证

- `git status` 起始干净（e8b3aea61）；实施写入仅 `doc/research/FEA-08-*`、`doc/handoffs/FEA-08-*`、`doc/tasks/FEA-08.md`、`verification/FEA-08/**`（allowed_paths 子集）。
- 回收站操作经 `recycle_guarded` 白名单断言（仅 lab 合成路径）；C: 用户回收站条目零触碰；无 SHEmptyRecycleBin 调用。
- 测试 SQLite 未引入（BLOCKED 口径）；加密 fixture 密码为合成值。

## 建议 Review 关注点

1. S5a/S5b 盲区结论的判别链（mixed digest 对照组 + mtime 不变证据）是否足以支撑 "tolerant=UNAVAILABLE" 的登记强度。
2. R9 短路语义是否需在 needs-new 中升级为生产 DeletePlan 的硬约束（当前为建议项 3）。
3. IFileOperation 未实跑（报告 §9 登记为需新增验证项）是否接受由 SHFileOperationW 实测承载 H5 结论。

## 下一步

- 独立 impl Review（DSH Appointment，上下文独立；审查 head 见 Task 卡 delivery_head）。
- Review 通过后 DSH 集成验证（dotnet 基线 + check + pins 复跑）→ 关闭。
