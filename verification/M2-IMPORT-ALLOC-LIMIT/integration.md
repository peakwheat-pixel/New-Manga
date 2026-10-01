# M2-IMPORT-ALLOC-LIMIT 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-IMPORT-ALLOC-LIMIT`；链：批次 release `8996ca55`（fork；Task 授权基线 8e0de8d0）→ `a5c8adf1`(implement) → `02f306ea`(docs，r1 被审头) → `400046ef`(r1 条件返修，r2 被审头)
- Review 链：DSH r1 `approved_with_conditions`（2×P2 R1 机制锁定/R2 证据超述 + 8×P3/P4；`doc/reviews/M2-IMPORT-ALLOC-LIMIT-a5c8adf1-dsh-r1.md`）→ Owner 条件返修 R1-R10 全 closed → DSH r2 **`approved`（可集成）** 0×P0/P1/P2 新发现（R1 机制锁定用例「真成立」独立核对：同输入仅限值不同；R2 工件真含 stderr 原文/env/decoded_mib，fd2 捕获实现可靠；R3 对照臂消除双变量；`doc/reviews/M2-IMPORT-ALLOC-LIMIT-400046ef-dsh-r2.md`）

## 修复内容（正式）

- `QImageReader.setAllocationLimit(2047MiB)` 每 decode 前断言（域实测最大 345.6MiB ×5.9 余量；非 0 防 OOM fail-closed）；`_reader_error_detail`（errorString 截 300+3 字符）
- MOBI 通道 `render_page` 解码前重新收紧 256MiB（内嵌图=不可信输入保持原 fail-closed 上界，R7）
- 测试：4 新增+1 机制锁定（同输入仅限值不同断言固化）+红态归档 pre-fix-tests-against-base-src.txt（4 failed/1 passed 基线绿）+slow 标记
- 真图验证：K07/K09/K10 生产通道导入 PASS（345.6/264.5/265.0 MiB）+对照组（原始 reader @256 拒/@2047 过=限值唯一变量）+native_stderr 原文归档 → **TA3-B2 F2 从推断升级一级证据**

## 集成运行时项

- 五套件复跑（Owner 返修轮）：production_adapters+providers+core+m2_acceptance+import_formats = **550 passed+1skipped 0 failed**（四套件 522=521+R1 新用例；import_formats 28 例 MOBI 面全绿）；post-merge main 复跑登记于 close commit
- r2 新发现 3×P3+4×P4 全部文档/证据文字级（红线档案摘录不精确等），登记不阻塞——详见 r2 报告
- 全局上界副作用：MOBI/PDF 解码路径的有效上界已由 R7 收紧恢复；TA3-B2 quality-report 的 F2 行（推断口径）未回填——证据在 verification/M2-IMPORT-ALLOC-LIMIT/，原站点回填留编排会话后续 hygiene
