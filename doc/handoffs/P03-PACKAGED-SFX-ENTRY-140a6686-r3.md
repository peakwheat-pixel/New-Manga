---
task_id: P03
title: Packaged 第五 SFX 入口验收补齐 (r3 可追溯性日志规范化与双向可逆验证交付)
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
base_commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
release_commit: ece8765461ce19f7493ce636ff7d69ae6a3e1c4b
start_head: 140a6686ef13e45d4c95de2c7929b61bdaef1d1e
build_source_head: 29024a21939917c6d8eb15f1a2bb9ff46cd5bf23
installer_sha256: 5a14c0a98008442bf4e3b70ec1fcc17373e33313cbadf69414fd9584a25a2fa0
status: in_review
---

# Handoff：P03 Packaged 第五 SFX 入口验收补齐 (r3 可追溯性日志规范化与双向可逆验证交付)

## 交付概览

本交付文档针对 Codex 在只读初审中对 `traceability-rerun/*.log` 提出的日志可读性与编码混合问题进行彻底、形式化、可逆的规范化修订。

在严格遵守禁止修改范围（零修改 `src/**`、`apps/**`、contracts、Schema、依赖、build spec/script；保留原始 01–06 原始字节、历史 raw、未跟踪派发文件原样）的前提下，本次交付：
1. **原样保留原始日志**：`verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/*.log` 原始 6 个文件的原字节完全未动、未被覆盖；
2. **形式化 Grammar 与双向严格映射**：查明源字节混合编码成因，建立了无歧义、逐文件验证且 100% 可逆的 Token 语法与转换机制；
3. **可读规范 UTF-8 副本**：在 `canonical-utf8/` 目录下生成全部 6 个日志文件的标准 UTF-8 副本，彻底消除 NUL，保留完整的执行记录头尾、命令、stdout/stderr 与 `EXIT=0`；
4. **逐位逆变换验证（Bit-for-Bit Reversible）**：通过内联断言验证，从规范副本经逆变换重建的字节与原始二进制文件 100% 逐位、逐字节完全一致（01~06 全部重建成功，零信息损失，零猜测）；
5. **升级 Manifest (Schema 2.0)**：在 [`07-encoding-normalization.json`](../../verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/07-encoding-normalization.json) 中完整记录形式化 Grammar 规范、转换规则、逐文件 Token 统计、原始与规范哈希以及可逆性重建断言结果。

---

## 1. 原始混合编码成因与形式化语法分析

### 1.1 产生根因

在 Windows PowerShell 5.1 环境下，`run_traceable.ps1` 执行行为如下：
1. **Header Segment**：脚本先使用 `Out-File -FilePath $logFull -Encoding utf8` 写入带 BOM 的 UTF-8 头部，以 `=====================================\r\n` 结尾；
2. **Body Segment**：随后调用 `Invoke-Expression "$CommandText *>&1" | Tee-Object -FilePath $logFull -Append`。在 Windows PowerShell 5.1 下，`Tee-Object` 将控制台字符流以 UTF-16LE 追加写入；由于前序换行规整操作在 UTF-8 行拆分视角下处理了包含 UTF-16LE 的二进制块，使得原始的 `\r\x00\n\x00`（4 字节）被拆解并重新以 `\r\n` 拼接，形成了固定的 6 字节序列 `0D 0A 00 0D 0A 00`（即 `\r\n\x00\r\n\x00`）。在直接以 UTF-16LE 解码时，该 6 字节序列被解释为 `U+0A0D U+0D00 U+000A`；
3. **Footer Segment**：脚本最后使用 `$footer | Out-File -FilePath $logFull -Append -Encoding utf8` 追加写入标准的 UTF-8 尾部，以 `EXIT=0` 及结束分隔线结尾。

### 1.2 形式化 Token 语法（Formal Token Grammar）

经对全部原始文件的穷举字节分析，除 05（纯 UTF-8 头部加尾部，Body 为 0 字节）外，01、02、03、04、06 的 Body 区段由且仅由以下两种严格语法单元交替组成：

| 语法单元 | 原始字节模式 | 原始字节长度 | 语义解释 | 规范 UTF-8 映射 | 逆变换重建规则 |
|---|---|---|---|---|---|
| `CHAR_TOKEN` | `[0x00-0x7F, 0x00]`（字节 0 非 CR/LF） | 2 字节 | 单字节 ASCII 字符的标准 UTF-16LE 编码 | 单字节 `c` (UTF-8 ASCII) | `bytes([c, 0])` |
| `NEWLINE_TOKEN` | `0D 0A 00 0D 0A 00` | 6 字节 | 换行序列（`\r\n\x00\r\n\x00`） | `\r\n\r\n` (CRLF CRLF, 4 字节) | `b"\r\n\x00\r\n\x00"` |

全部 5 个文件的 Body 区段（12,160、5,790、14,230、7,470、10,096 字节）**100% 完整、无遗漏、无孤立字节地匹配该语法**，不存在任何奇数偏移、损坏或未定义的字节。

---

## 2. 规范化副本与可逆性验证证据

### 2.1 验证与重建结果汇总

| 文件名 | 原始大小 | 原始 SHA-256 | 规范副本大小 | 规范副本 SHA-256 | CHAR Tokens | NEWLINE Tokens | 逆变换逐位重建 |
|---|---|---|---|---|---|---|---|
| `01-rerun-targeted-tests.log` | 12,648 B | `c7e442c4c7d1ad92...` | 6,618 B | `e10f83acd1ec270a...` | 5,930 | 50 | **MATCH (12648/12648)** |
| `02-rerun-snapshot-check.log` | 6,221 B | `7883b6b4ae324900...` | 3,351 B | `0dfe5bf62ff8fb3b...` | 2,820 | 25 | **MATCH (6221/6221)** |
| `03-rerun-tauri-nsis-build.log` | 14,601 B | `20b5936e8db7969b...` | 7,623 B | `a8b5bbe91a36804a...` | 6,704 | 137 | **MATCH (14601/14601)** |
| `04-rerun-diff-name-only.log` | 7,942 B | `f9a0905a52185883...` | 4,257 B | `86c342139ee72c99...` | 3,585 | 50 | **MATCH (7942/7942)** |
| `05-rerun-diff-check.log` | 468 B | `f45684005e28dcda...` | 468 B | `f45684005e28dcda...` | 0 | 0 (逐字节复制) | **MATCH (468/468)** |
| `06-rerun-packaged-gate.log` | 10,766 B | `63f0410c4d0d5b88...` | 5,770 B | `70497d2f1ac269fc...` | 4,892 | 52 | **MATCH (10766/10766)** |

### 2.2 规范副本质量断言
- **零 NUL 字符**：全部规范日志中的 `\x00` 字节计数严格为 0；
- **UTF-8 纯净解码**：全部规范日志严格通过 UTF-8 / UTF-8-SIG 解码，无任何 `UnicodeDecodeError`；
- **结构完整**：以 `=== Traceability Execution Record ===` 开始，包含完整命令、工作目录、StartTime、EndTime、`EXIT=0`，并以 `=====================================` 结束；
- **逆变换完全闭合**：从规范副本执行逆向 Token 映射生成的重建字节与原始文件比对，`reconstructed_orig == orig` 100% 成立，证明正向映射无信息损失、无主观猜测修补。

---

## 3. 授权差量范围与格式检查

- 差量对比基线：`ece8765461ce19f7493ce636ff7d69ae6a3e1c4b..HEAD`
- 修改与新增路径严格受限于授权边界：
  - `verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/canonical-utf8/**` (新增可读规范副本)
  - `verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/07-encoding-normalization.json` (更新元数据)
  - `verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/verify_normalization.py` (新增内联验证脚本)
  - `verification/P03-PACKAGED-SFX-ENTRY/RESUME.md` (更新恢复点状态)
  - `doc/tasks/P03.md` (更新 Task 状态至 in_review)
  - `doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md` (新增 r3 handoff)
- 代码与测试格式：
  - 核心 Python 代码与测试（`packaging/m2ac5/run_clean_start_e2e.py`、`tests/packaging/test_packaged_fifth_sfx_entry.py`）**零空白错误**。
- `git diff --check 31abde9bf4b73aea2851931dcd48faa0f750b318..HEAD` 精确检查结果：
  - 报出 `canonical-utf8/03-rerun-tauri-nsis-build.log` 的两处尾随空格：L19（空提示行中的空格 ` `）与 L149（rustc 警告长文本自动折行空格 `and `）；
  - **诚实说明与保真决策**：这两处空格源自控制台与 rustc 编译器的原生 stdout 输出。为了保持规范副本与原始控制台捕获二进制文件之间 **100% 逐位可逆（Bit-for-bit Lossless Reconstruction）**，未进行任何猜测性修剪；逆变换断言证明其与原始捕获严格一致。
- 原始文件 `traceability-rerun/*.log` 原样保留；未跟踪文件 `antigravity-dispatch.*` 原样保留。

---

## 4. 复审指令

所有证据及双向可逆性证明完备。Task 恢复至 `in_review`，交由非作者 Reviewer `DeepSeek Harness` 正式复审。

```markdown
# DeepSeek Harness Reviewer 指令：P03 r3 复审

请在独立 worktree 对 Antigravity 交付的 P03 Task r3 可追溯性日志规范化与双向可逆验证进行非作者独立 Review。

- Task ID: P03
- Task 状态: in_review
- Worktree: G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity
- Branch: agent/antigravity/P03-packaged-sfx-entry
- Base Commit: 31abde9bf4b73aea2851931dcd48faa0f750b318
- Build Source HEAD: 29024a21939917c6d8eb15f1a2bb9ff46cd5bf23
- Delivery Handoff: doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md
- 规范 UTF-8 日志: verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/canonical-utf8/**
- 规范化 Manifest: verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/07-encoding-normalization.json
- 双向验证脚本: verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/verify_normalization.py

## 复核重点
1. 运行 `python verification/P03-PACKAGED-SFX-ENTRY/revision-2/traceability-rerun/verify_normalization.py`，验证 6 项规范副本零 NUL、可读 UTF-8 及 100% 逐位逆变换重建；
2. 审阅 `canonical-utf8/*.log` 文本，确认命令记录、stdout/stderr 与 EXIT=0 证据完整；
3. 核对原始 `traceability-rerun/*.log` 原字节保留未动；
4. 核对 NSIS 安装包哈希 `5a14c0a98008442bf4e3b70ec1fcc17373e33313cbadf69414fd9584a25a2fa0` 与 `run-5a14c0a9/cleanstart-gate.json` 28/28 PASS。
```
