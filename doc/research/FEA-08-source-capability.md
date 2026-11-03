# FEA-08 技术报告：Source 稳定读取 / Windows 回收站 / 精确页面匹配能力矩阵

- Task：[FEA-08](../tasks/FEA-08.md)（scope-r2 approved，2026-11-03；范围冻结 base `2870a9fa5`；本版为 R6 返修后证据收口版）
- 性质：隔离原型（无生产代码改动；实施 diff 仅落 `doc/research|handoffs|tasks` 与 `verification/FEA-08/**`）
- 原型：`G:\CODEX\New Manga.workspace\FEA-08\prototype\`（非 Git；16 脚本 SHA-256 见 `verification/FEA-08/prototype_hashes.txt`）
- 证据：`verification/FEA-08/`（results/logs/fixtures；`run_all` 顶层 EXIT=0 + results verdict 双层校验）
- 依据锚点：提案 `:457/:465/:469/:512–:514/:794–:796/:929`、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)、[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)

## 1. 执行摘要（TL;DR）

| 假设 | 结论 | 一句话 |
|---|---|---|
| H4 稳定源 lease | **NTFS 本地 = PASS（strict 模式）**；tolerant 模式对内存映射写 = **UNAVAILABLE** | strict 共享模式（不授 `FILE_SHARE_WRITE`）在**打开层**挡住一切写者与覆盖式替换；宽容共享下 WriteFile 中途写可被 mtime 检出，但 **mmap 写不更新 mtime → 混合流假成功盲区（实测复现）**。**生产硬约束：strict-only**（放宽须先补 USN/双读缓解） |
| H5 Windows 回收站 | **NTFS 本地 = PASS（9 场景 measured）**；不可回收卷/取消 = LIMITED(mocked) | `SHFileOperationW+ALLOWUNDO` 成功可还原且 digest 逐位一致；失败/占用/替换/中断全部保留原路径或按文件系统事实核对恢复；**批量遇错即短路**，生产必须逐项核对 |
| H6 精确页面匹配 | **五类输入全部 = PASS（内容层，卷无关）**；ZIP 的 AES 分支 = LIMITED(pyzipper) | 未变图片/容器重编码/PDF 重生成/加密带密/GIF 首帧均可**精确匹配**；有损重编码/CMYK/重命名/重复名歧义按冻结口径**只给候选**；dhash 候选阈值边界（距离 10/11）、**尺寸绑定 digest** 与**容器成员唯一映射**均有专项反例 fixture 判别 |

矩阵状态计数（60 格 = 4 卷类型 × 5 输入类别 × 3 能力；NTFS 行状态由 h4/h5/h6 结果 JSON 推导，不硬编码）：
**PASS(strict)/UNAVAILABLE(mmap-blind) 1（NTFS-H4 单图） / PASS 6 / PASS(Non-AES)/LIMITED(pyzipper)(AES) 1（NTFS-H6 ZIP） / LIMITED(inferred: volume-level, format-agnostic) 7（NTFS-H4 文件夹/ZIP/CBZ/PDF + NTFS-H5 ZIP/CBZ/PDF） / LIMITED(mocked) 30 / LIMITED(inferred) 10 / UNAVAILABLE(inferred) 5**。mock/inferred 无一记 PASS（AC-4 口径；NTFS 卷级 measured 但未逐格式实测的格按推断降级 LIMITED 并注明 "volume-level measured, format-agnostic"）。

## 2. 方法与环境

- 环境：Windows 11（10.0.26300），C:/D:/E:/G:/H: 全部固定 NTFS 卷；本机无可移动/网络/云卷 → USB/SMB/云按 mocked/inferred 登记。Python 3.14.6 + ctypes（Win32 直调，无第三方 Windows 封装）。
- 测试隔离：全部写操作限于 `workspace\FEA-08\tmp\`（run_all 末尾实际清理并记录 `tmp_remaining=[]`）与 `verification\FEA-08\`；**未触碰真实库/用户文件/AppData**；回收站操作仅对合成路径（G: 回收站基线 0 条，结束 0 条、零残留）。
- Win32 面：`CreateFileW`（共享模式）、`GetFileInformationByHandle`（volume serial + file index + size + mtime）、句柄 `ReadFile`、`CreateFileMappingW/MapViewOfFile`（写侧）、`SHFileOperationW`（FO_DELETE+ALLOWUNDO）、`SHQueryRecycleBinW`（只读计数）、`$RECYCLE.BIN` `$I/$R` 事实读取与还原。**未封装、未调用任何清空类 API**。
- 脚本口径（F08I1-011）：workspace 原型 **16 个登记脚本**；`run_all.py` 执行 **5 个核心场景步骤**（make_fixtures→h4→h5→h6→matrix）+ 双生成 fixtures + **原子 evidence staging**（失败回滚旧 Canonical，F08I2-006）+ results 双层 verdict 校验；`stage_evidence.py` 单独生成入库 fixtures manifest；`pin_selfcheck.py` 逐行按登记 commit 做 commit/worktree/index/clean-checkout 四方 pin 校验；`gates_capture.py` 采集门禁原始日志与 57 项 skip 来源；其余 `h4_diag*/h5_diag*/h5_cleanup*` 为诊断/清理脚本，`probe_env.py` 为环境探测，不在 run_all 链路。

## 3. H4：稳定源 lease（AC-1，提案 :465/:794）

### 3.1 协议原型

`StableReadLease`：`CreateFileW(GENERIC_READ, share)` 打开即取句柄级身份（volume serial + file index + size + mtime）→ **同一句柄**分块读取（16KB chunk，读取中途可注入故障）→ 读后重验身份，一致才输出 digest，不一致抛 `LeaseUnavailable`。读取路径不存在"按路径另开"（协议代码只持句柄；对照诊断 API 明确标注为错误实现模拟）。

### 3.2 场景矩阵（10 场景全 measured）

| 场景 | lease 共享 | 注入 | 结果分类 |
|---|---|---|---|
| S1 基线 | R\|D | 无 | complete_old_digest |
| S2 写者/替换尝试 | **R（strict）** | WriteFile 句柄打开 + `os.replace` | 写者 open blocked(**win32=32**)；replace blocked(win32=5)；digest=完整旧 |
| S3a 覆盖式替换 | R\|W\|D | `os.replace`（中途） | **blocked(win32=5) + 完整旧 digest**（目标被任何句柄打开时 REPLACE_EXISTING 一律拒绝，与共享模式无关） |
| S3b 换名替换 | R\|W\|D | rename-aside + rename-in（中途） | **完整旧 digest**；路径重开=新内容（错误实现可判别）；旧流以 aside 名存活 |
| S4 共享写 | R\|W\|D | `WriteFile` 写未读区（中途） | **unavailable**（读流确已混合：诊断 digest = 混合流；mtime 检出，`mtime_changed=true` 有真实身份来源） |
| S5a mmap 写（已 unmap） | R\|W\|D | 映射写未读区+flush+unmap | **undetected_mixed（盲区）→ 结果字段评估为 unavailable / LIMITED(mmap-blind)**：读前读后真实 FileIdentity 的 mtime 不变（实测 false，非字段缺失），读流=部分旧+部分新，协议误当有效 |
| S5b mmap 写（映射保持） | R\|W\|D | 同上，映射不关 | 同上（两时序均复现；`mixed_digest_risk=true` 与分类自洽） |
| S5c mmap 写者 vs strict | **R\|D** | 映射写者尝试打开 | blocked(win32=32) + 完整旧 digest |
| S6 删除 | R\|W\|D | `DeleteFile`（中途） | 完整旧 digest（挂起删除；路径已消失如实登记） |
| S7 重命名 | R\|W\|D | `rename`（中途） | 完整旧 digest（流身份不变；路径变化如实登记） |

（win32 错误码记录口径：`Win32Error(code, msg)` 构造下读 `e.args[0]`，与 JSON `writer_attempts.write_open` 一致——报告数字与 JSON 对齐，F08I1-004。）

### 3.3 结论与关键发现

1. **strict 模式（不授 FILE_SHARE_WRITE）= NTFS 可证明一致读取**：一切写者（WriteFile/映射写）在 `CreateFileW` 即被共享模式拒绝（win32=32）；覆盖式替换对**任何**共享模式（含全共享）都被拒（win32=5）——真实可达的替换路径只剩 rename-aside+rename-in，而它对已打开句柄无效（句柄仍绑旧流，读得完整旧 digest）。
2. **实测盲区（最重要发现）与硬约束**：宽容共享（R|W|D）下，**内存映射写不更新 LastWriteTime**（flush/unmap 后亦然）→ 身份+size+mtime 协议完全检测不到 mmap 中途写，读取流混合（A+D+A）却被当作有效 digest 输出——正是 AC-1 断言②禁止的假成功形态。**因此 tolerant 模式对 mmap 场景只能判 UNAVAILABLE；生产 SourceReadLease 必须 strict-only，这是硬约束而非建议**——若产品确需宽容共享（与第三方写者共存），须先补 USN/change journal 或双读校验，此为需新增项。结果 JSON 中 S5a/S5b 的 `mixed_digest_risk=true`、`outcome=unavailable`、`outcome_evaluation=LIMITED(mmap-blind)` 与分类字段自洽（F08I1-003/004）。
3. 判别性证据：S4 无检测对照组证明"不重验身份就会返回混合 digest"（`no_check_control_is_mixed=true`）；S3b 证明"check 后按路径另开"会拿到新内容 digest（`path_reopen_digest_is_new_content=true`）——两种错误实现均可被本判据抓出。
4. SMB/USB：无硬件，身份基（SMB/FAT 的 file index 语义弱化）按文档推断，LIMITED(mocked)。

## 4. H5：Windows 回收站（AC-2，提案 :512–:514）

### 4.1 判定操作（冻结口径的执行化）

每场景按双向判定：**失败/取消/中断 → 目标仍在原路径且 digest 不变**；**成功 → 回收站存在该条目（$I 原路径匹配）且还原后（$R 移回）digest 与回收前逐位一致**。回收站事实以 `SHQueryRecycleBinW`（只读）+ `$RECYCLE.BIN\$I/$R` 双核对；**期望在场的回收站条目经有界轮询确认**（500ms × 上限 12 次，`entries_poll` 记录轮询次数与是否超时——shell 异步落盘存在时序窗口，F08I1-005）；全部条目测试后还原并删除（restore_log 5 条，G: 回收站 0→0，零残留）。harness 双层门禁：`h5_run.py` 对期望 PASS 场景 FAIL 时非零退出；`run_all.py` 另行校验 results JSON 的全部 verdict（不只进程返回码）。

### 4.2 场景矩阵（11 场景）

| 场景 | 操作 | 判定 | 结论 |
|---|---|---|---|
| R1 单文件回收 | FO_DELETE+ALLOWUNDO | ret=0；回收站在场（轮询确认）；还原 digest 一致 | **PASS** |
| R2 非空目录回收 | 同上（目录） | ret=0；$R 为目录形态；还原逐成员 digest 一致 | **PASS** |
| R3 空目录回收 | 同上 | 实测可回收（ret=0，条目在场）——:514 的"不能回收则保留"分支在 Win11+NTFS **未触发**；该分支经 mock 失败注入（ret=0x79 DE_ACCESSDENIEDSRC → 同一 `dispose_unrecyclable` 处置函数 → keep_at_origin、`fallback_rmdir_used=false`）走通并标 **LIMITED(mocked)** | **PASS**（measured recyclable）+ 分支 LIMITED(mocked) |
| R4 占用失败 | 目标被无共享句柄打开 | ret=32；目标保留原路径、digest 不变；回收站无条目 | **PASS** |
| R5 计划-执行间路径被替换 | identity 重验（file_index+mtime） | 不匹配 → 拒绝执行，零 destructive 调用（计数事实），目标保留 | **PASS** |
| R5b 目标被替换为同名目录 | 类型/属性重验（GetFileAttributesW：`0x10` FILE_ATTRIBUTE_DIRECTORY；句柄级 identity 对目录 open_handle 被拒 win32=5，如实记录） | 计划针对文件/现状目录（实测推导）→ 拒绝执行，目标保留 | **PASS** |
| R6a 崩溃于执行前（receipt 恢复） | receipt+事实核对 | 原路径在且 identity 匹配 → 判 retained，不重发（计数事实） | **PASS** |
| R6b 崩溃于执行后（结果未知） | receipt+事实核对 | 原路径不在+回收站在场 → 判 completed；**恢复前后 destructive 计数 5→5（零重发，计数事实）**；还原 digest 一致 | **PASS** |
| R9 批量部分失败（3 项 1 占用） | 逐项事实核对 | a 回收成功、b 占用保留、**c 未被处理而保留（SHFileOperation 短路）**；还原后三项 digest 全一致 | **PASS** |
| R7 不可回收卷/网络盘 | — | 无硬件；D 流程须按卷能力探测禁用 | LIMITED(mocked) |
| R8 用户取消 | — | 无人值守无法触发确认 UI；返回码路径与 R4 同构（保留） | LIMITED(mocked) |

### 4.3 结论与关键发现

1. `SHFileOperationW + FOF_ALLOWUNDO|SILENT|NOCONFIRMATION|NOERRORUI` 在 NTFS 上满足"绝非永久删除"：所有失败/中断分支目标保留；成功分支可从 `$RECYCLE.BIN` 事实还原且 digest 逐位一致。
2. **批量短路语义**：多目标遇错即停，失败项之后的目标**不被处理**（保留原路径）——生产 `DeletePlan` 不能假设全量尝试，必须逐项文件系统事实核对（本原型 R9 判定操作即为该语义的执行化）。
3. **Win11 `$I` v2 实测格式**：24B 头（version=2/filesize/FILETIME）+ `uint32 路径字符数（含尾随 null）` + UTF-16LE 路径——与流传的"null 终止"描述不同，receipt 解析须按实测格式（已写入 needs-new）。
4. 负向约束遵守：未调用任何清空类 API（`fwin.py` 刻意不封装）；回收/还原仅限合成路径（`recycle_guarded` 白名单断言）；C: 卷用户真实回收站条目零触碰。

## 5. H6：精确页面匹配（AC-3，提案 :457/:469）

### 5.1 判定框架

二分 **exact_match / candidate**（附加 needs_password / no_match / needs_confirmation），逐场景附判定 digest 类型：

- 图片：`bytes_sha256`（强 digest）→ `canonical_pixel_sha256`（规范解码：exif_transpose→RGB8→原始分辨率；**R3/F08I2-002 起 digest 绑定尺寸** `sha256("WxH\0"+RGB)`，不同尺寸不得 exact）→ `dhash_candidate`（8×8 差分 hash，汉明距离 ≤10 仅候选）
- 文件夹：`folder_membership + bytes_sha256`（成员身份+逐成员 digest）
- 容器：`member_content_sha256`（成员内容 digest，压缩/顺序无关；同名多 occurrence 按 ZipInfo 句柄独立读取）。**R3/F08I2-003 起 exact 还要求成员映射唯一确定；R4/F08I3-004 细化为按 occurrence 构建“内容 → 成员名多重集”映射**：唯一内容可跨名唯一对应（改名/换位仍 exact，M21）；重复内容必须有相同 name/ordinal 锚（M22 exact）；锚不一致 → `needs_confirmation`（M20）；重复名且内容不同 → `candidate`（M12）；**重复成员名在任一侧都独立核验**（F08I4-003：A 唯一名 vs B 重复名两方向均 candidate，M23）
- PDF：`rendered_pixel_sha256`（pypdfium2 渲染，**digest 绑定页渲染尺寸**，参数记录：pdfium 153.0.7999.0 / dpi 150 / scale 2.0833 / RGB8）+ 内容流 digest 双判据，页码 1-based

### 5.2 场景矩阵（22 场景全 measured；fixtures 全部入库，可从仓库复现）

| 场景 | 判定 | digest 类型 | 说明 |
|---|---|---|---|
| M1 未变图片（另路径副本） | exact_match | bytes_sha256 | 强 digest |
| M2 同像素 JPEG 重编码 | candidate | dhash(距离 0) | 有损重编码不可能逐位精确 → 仅候选 |
| M3 水平翻转 | no_match | dhash 距离>10 | 翻转不自动匹配 |
| M4 EXIF orientation=6 | **exact_match** | canonical_pixel_sha256 | 方向规范化后逐位一致（无损 fixture 判别） |
| M5 物理旋转（无 EXIF） | candidate | dhash(距离 5) | 规范化后不同像素 |
| M6 灰度 vs RGB 存储 | exact_match | canonical_pixel_sha256 | 模式归一后逐位一致 |
| M7 CMYK vs RGB | candidate | dhash(距离 0) | 色彩空间转换有损 → 仅候选 |
| M8 重复同图 | 独立 occurrence | membership | p1/p4 digest 相同但身份独立，不 hash 合并 |
| M9 文件夹 diff | needs_confirmation | membership+digest | unchanged p1 / missing p2,p3 / added p2renamed,p4；**p2→p2renamed 内容 digest 相同 → 仅重命名候选**；p3 真缺失 |
| M10 ZIP 容器重编码 | **exact_match** | member_content_sha256 | STORED+倒序 vs deflate：成员内容多重集相等且成员名集合可对齐（唯一映射） |
| M11 CBZ | exact_match | member_content_sha256 | 与 ZIP 同构 |
| M12 重复成员名 | **candidate** | member_content_sha256 | **独立副本两路径比较**（book_dup.zip vs book_dup_copy.zip，独立构造）：同名两 occurrence 内容不同 → 歧义仅候选；同文件自读对照显式标 `self-consistency` |
| M13 加密 ZIP | 带密 exact / 无密 needs_password | member_content+密码 | **独立第二份密文两路径比较**（book_enc_zipcrypto.zip vs copy，同密码独立加密）；ZipCrypto 独立加密密文与主件逐位不同（7-Zip 条目时间戳参与）；带密 exact、无密 needs_password；**AES：标准库 NotImplementedError → LIMITED(pyzipper)，生产需 pyzipper(MIT)（未引入，登记而非绕过）**；密码走显式入参，不进日志 |
| M14 PDF 重生成 | **exact_match** | rendered_pixel_sha256 | 容器字节不同；页渲染 digest+内容流 digest 双一致；页码/渲染参数全记录 |
| M15 加密 PDF | 带密 exact / 无密 needs_password | rendered+密码 | **独立第二份密文两路径比较**（doc_enc.pdf vs doc_enc_copy.pdf，同密码独立加密、/ID 时间戳不同→密文不同）：带密渲染 digest 一致 → exact；无密探测标 `self-consistency probe` |
| M16 GIF 仅首帧 | **exact_match** | canonical_pixel(帧0) | 帧 0 匹配成立、帧 1 反证不匹配（`blue_frame_digest_would_not_match=true`） |
| M17 dhash 邻界=10 | **candidate** | dhash(距离恰 10) | 9×8 灰度邻界 fixture（翻转格 +100 精确控制）：距离恰 10 → 候选边界内 |
| M18 dhash 邻界=11 | **no_match** | dhash(距离恰 11) | 同法构造：距离恰 11 → 边界外不匹配 |
| M19 不同尺寸同像素字节（F08I2-002 反例） | **candidate** | canonical_pixel_sha256(**dim-bound**) | `img_dims_a`=2×6 与 `img_dims_b`=3×4 像素字节序列相同；尺寸绑定 digest 不同 → 不得 exact（`size_mismatch=true`、`exact_blocked_by_size_mismatch=true`），dhash 距离 0 仅候选 |
| M20 容器重复同图·成员名不同（F08I2-003 反例） | **needs_confirmation** | member_content_sha256 + 身份锚 | `book_dupcontent_a`(a/b) vs `book_dupcontent_b`(c/d) 四成员内容全同；多重集相等但无 name/ordinal 唯一映射 → `duplicate_content_ambiguity`，不误判 exact |\n| M21 唯一内容成员改名/换位（F08I3-004 正例） | **exact_match** | member_content_sha256 + 内容唯一映射 | `book_renamed_left`(a=红,b=绿) vs `book_renamed_right`(c=绿,d=红)：内容各自唯一 → 跨名唯一对应，`unique_content_mapping=true`（不得误拒） |\n| M22 重复内容带同名锚 + 唯一项改名（F08I3-004 正例） | **exact_match** | member_content_sha256 + 身份锚 | `book_dupanchor_left`(a=红,b=红,c=绿) vs `book_dupanchor_right`(a=红,b=红,d=绿)：重复项有相同 name 锚、绿图唯一 → exact |\n| M23 非对称重复名（F08I4-003 反例） | **candidate** | member_content_sha256 + 双侧重复名核验 | `book_asym_left`(a=红,b=绿，唯一名) vs `book_asym_right`(page.png=红,page.png=绿，重复名)：两方向运行均为 candidate（不因 A 侧唯一而误 exact） |

### 5.3 结论

冻结判据全项落地：精确/候选二分、判定 digest 类型披露、文件夹成员身份+digest、容器成员 digest+规范解码像素 digest+**尺寸绑定**+方向+**唯一一对一定位**、重复成员名独立 occurrence、感知 hash 仅候选（含阈值邻界 M17/M18）、GIF 仅首帧、PDF 页码+渲染参数记录。**R3（F08I2-002/003）新增两个真实反例场景**：不同尺寸同像素字节不得 exact（M19）、重复同图但成员身份不同名时只给候选/需确认（M20）；由此 digest 语义从“原始 RGB 字节”升级为“尺寸绑定规范表示”，容器匹配从“内容多重集相等”升级为“内容多重集相等 + 成员唯一映射”。**R4（F08I3-004）补齐正例**：唯一内容成员改名/换位（M21）与重复内容带同名锚+唯一项改名（M22）均为 exact，避免“安全保守”退化成误拒；仅锚不一致时（M20）才 needs_confirmation。**R5（F08I4-003）**：重复成员名改为**双侧独立核验**——任一侧出现重复名即 candidate（M23 两方向均为 candidate），消除“左侧唯一、右侧重复”时的不对称误判。加密格式采用**预生成 fixture+SHA-256**路径（scope-r2 待决项 3 的选项一）：7-Zip 生成 ZipCrypto/AES256（及 ZipCrypto 独立副本）、PyMuPDF 生成 AES-256 PDF（及独立副本）入库（`fixtures/evidence_manifest.json` 登记原件 SHA），未引入 pyzipper 新依赖。**M12/M13/M15 的匹配证据均为两路径独立副本/独立密文比较，非同文件自比**（F08I1-007）。

## 6. 能力矩阵（AC-4）

完整 JSON/MD 见 `verification/FEA-08/results/capability_matrix.{json,md}`。R2 起矩阵逐格含 **current（现状）/needed（需新增）** 字段，NTFS 行状态由 h4/h5/h6 结果 JSON **逐场景推导**（推导不满足时不写 PASS，如实降级；F08I1-008）。**R3（F08I2-004/005）**：每个卷分支显式赋值 H4/H5/H6 各自 evidence（非 NTFS 卷不再继承 measured）；NTFS 行推导不再只看顶层 classification/result，而是消费**语义断言集**（strict 拦截断言、GIF 蓝帧反证、尺寸绑定、容器唯一映射、回收分支计数与类型拒绝）；断言被破坏即降级。**R4（F08I3-001）**：H5 语义门禁进一步收紧——还原 digest、目标保留/类型、不得 fallback 永久 rmdir、destructive 计数必须存在且为整数（`None` 不得通过）、回收站轮询字段合法。**R5（F08I4-001）**：矩阵此前只验过子集，已补齐与 `run_all.verify_results` **逐字段一致**的全部 H5 必需事实（R1/R2/R4/R5/R5b/R6a/R6b/R9/entries_poll）。**R6（F08I5-001/003）**：矩阵补 R6b `restored` 列表逐项断言；计数校验拒绝 JSON boolean（`bool` 不得冒充 `int`）。摘要：

| 卷类型 | 输入类别 | H4 稳定读取 | H5 回收 | H6 精确匹配 | 证据 |
|---|---|---|---|---|---|
| NTFS 本地 | 单图 | **PASS(strict)/UNAVAILABLE(mmap-blind)** | PASS | PASS | measured |
| NTFS 本地 | 文件夹 | LIMITED(inferred: volume-level, format-agnostic) | PASS | PASS | H4=inferred；H5/H6=measured |
| NTFS 本地 | ZIP | LIMITED(inferred: volume-level) | LIMITED(inferred: volume-level) | **PASS(Non-AES)/LIMITED(pyzipper)(AES)** | H4/H5=inferred；H6=measured |
| NTFS 本地 | CBZ | LIMITED(inferred: volume-level) | LIMITED(inferred: volume-level) | PASS | 同上 |
| NTFS 本地 | PDF | LIMITED(inferred: volume-level) | LIMITED(inferred: volume-level) | PASS | 同上 |
| USB FAT32/exFAT | 全部 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB 网络 | 全部 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| 云占位 | 全部 | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |

- **口径说明**：H4/H5 是卷级句柄/路径语义（format-agnostic）——实测以单文件（H4 全场景）与文件/目录（H5 R1-R3）承载；文件夹/ZIP/CBZ/PDF 的 H4 与 ZIP/CBZ/PDF 的 H5 未逐格式实验，按 "volume-level measured, format-agnostic" 推断并按 AC-4 口径降级 LIMITED(inferred)（不记 PASS）。H6 为内容层能力（五类全 measured、卷无关）。
- **mock/推断无一项记 PASS**（AC-4 硬性口径）；NTFS H4 的 PASS 附带 strict 硬约束（§3.3-2）。
- 现状/需新增：逐格 current/needed 见矩阵 JSON；需新增清单（7 项）见 §8。

## 7. 依赖与许可

| 依赖 | 许可 | 用途 | 进生产闭包 |
|---|---|---|---|
| Python 3.14 + ctypes（标准库 zipfile/hashlib/struct） | PSF | 原型主体 | 复用其结论，不绑定 |
| Pillow 12.3.0 | Pillow License（HPND 系，permissive） | 图片 fixture/规范解码 | 候选（生产图片解码另行选型确认） |
| pypdfium2 5.13.0 + PDFium 153.0.7999.0 | Apache-2.0 / BSD-3-Clause | PDF 页渲染 digest（主判据） | **候选（许可友好）** |
| PyMuPDF 1.28.2 | **AGPL-3.0** | PDF fixture 生成 + 内容流分析 | **否——仅研究用途，不进生产闭包**；生产渲染以 pdfium 为准（本报告已用双判据交叉） |
| pywin32（探测用） | MIT | 环境 probe | 否 |
| 7-Zip 24.x（外部程序） | LGPL/BSD（unRAR 限制） | 仅生成加密 ZIP fixture（不链接、不分发） | 否 |
| pyzipper | MIT | **未引入**（AES ZIP 读取不可用 → 如实登记 LIMITED(pyzipper)，未绕过） | 待产品裁决 |

加密 fixture 处理遵守 Task OUT：密码 `FEA08pass` 仅存在于合成 fixture 生成/读取代码与日志，非任何真实凭据。

## 8. 需新增（生产化要点）

1. **SourceReadLease（Host 侧）**：**默认且建议唯一** strict 共享（不授 `FILE_SHARE_WRITE`）——硬约束；tolerant 仅在缓解 mmap 盲区（USN/change journal 或双读校验）后评估。
2. **mmap 盲区缓解**：identity+size+mtime 对映射写失明；需 USN/change journal 或双读校验，或保持 strict-only。
3. **WindowsRecycleBridge**：`IFileOperation` + 逐项 OperationId receipt/journal（:512）；失败分支按 R4/R5/R6/R9 原型语义；批量必须逐项事实核对（短路语义）。
4. **$RECYCLE.BIN receipt 解析**：按 Win11 实测 $I v2 格式（§4.3-3）。
5. **AES ZIP**：标准库不支持（M13 实测）→ pyzipper(MIT) 或仅支持 ZipCrypto，产品裁决。
6. **PDF 渲染引擎**：pdfium（BSD/Apache）实测确定性渲染；勿用 AGPL 引擎进闭包。
7. **USB/SMB/云卷**：LIMITED(mocked/inferred)；须真机实测后升级矩阵。
8. **H6 exact 判据（R3 强化）**：生产实现必须以**尺寸绑定的规范表示**计算强 digest（不得只比原始 RGB 字节），并保留成员身份/ordinal 做唯一映射；重复同图/重复名/一对多场景只能给候选或需用户确认（F08I2-002/003）。

## 9. 限制与未测（诚实登记）

- USB/FAT32/exFAT、SMB、云占位卷：无硬件/未授权触碰，全矩阵 mocked/inferred。
- 用户取消（R8）：无人值守无法触发真实确认 UI，按返回码同构推断 LIMITED(mocked)。
- H5 R3 的"目录不可回收→保留且不 fallback rmdir"分支在 Win11+NTFS 未真实触发，经 mock 失败注入走通处置函数并标 LIMITED(mocked)（F08I1-006）。
- IFileOperation（提案 :512 链接的新 API）：原型实测用 SHFileOperationW（同任务卡列举的两个 API 之一）；IFileOperation 的 per-item sink/flags 语义未实跑，登记为需新增验证项（不构成 H5 结论缺口——判定操作以文件系统事实为准，两 API 语义面等价）。
- SQLite/DB 文件行为不在本卡范围（BLOCKED 登记，scope-r2 确认）。
- H6 感知 hash 用 8×8 dHash 原型实现（阈值邻界 M17/M18 已实测判别）；生产候选器选型（pHash/OCR）另行冻结，本报告只证明"仅候选"边界。
- PyMuPDF 为 AGPL：仅研究原型使用；本 Task 无生产代码改动，不触发整体许可声明条款。
- 门禁 flake（历史）：R3 全量测试采集时 attempt1 曾出现项目既有偶发失败（Host/CoreClient 时序/sidecar 类），原始日志当时保留于 `gates-raw/02-test-attempt1.log` 并重跑通过；R4 采集一次通过（1292/0/57），属仓库既有测试稳定性债务、非本 Task 引入，建议另行登记处置。

## 10. 证据索引

- 结果：`verification/FEA-08/results/`（h4/h5/h6/capability_matrix/fixtures_manifest/run_all_log，共 7 件）
- 日志：`verification/FEA-08/logs/`（每脚本 stdout+EXIT：`make_fixtures.log` / `make_fixtures_regeneration.log` / `stage_evidence.log` / `h4_run.log` / `h5_run.log` / `h6_run.log` / `matrix.log` / `run_all.log` 共 8 件，统一 LF；另 `pin-verify.log`、`gates.log`、`test-skip-inventory.md`（57 项逐项来源）、`gates-raw/`（**7 份** build/test/check/pins/四 PNG/禁止 diff/安全搜索的完整原始输出，均含命令/EXIT/cwd/shell/elapsed，OS/Python/shell 环境见 03-check 与 `gates-raw-manifest.json` + `phase1-values.json`；R6 起采集器按实际结果汇总，失败即非零退出且结论 FAIL），共 72 项证据入库）
- Fixtures：`verification/FEA-08/fixtures/`（目录 **44 文件 = 43 内容文件 + `evidence_manifest.json`**；43 内容 = 21 项预生成原件 + 6 个 folder 成员 + 3 个独立副本 + 3 个 dhash 邻界 + 2 个尺寸反例 + 2 个重复同图容器反例 + 4 个唯一映射正例 + 2 个非对称重复名反例（book_asym_left/right）；`evidence_manifest.json` 登记 43 项原件 SHA-256，双 manifest 各 43 项逐项一致）
- 原型：`workspace\FEA-08\prototype\`（非 Git；`prototype_hashes.txt` **16 脚本** SHA-256；`run_all.py` 执行 5 个核心场景步骤 + 双生成 fixtures + 原子 evidence staging（失败回滚，F08I2-006），`stage_evidence.py` 单独生成 manifest，`pin_selfcheck.py` 逐行 commit/worktree/index/clean-checkout 四方校验，`gates_capture.py` 采集门禁原始日志与 skip 清单）
- 复现（从干净 checkout）：
  ```
  python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py            # 双生成 fixtures → 原子 staging → H4/H5/H6(对入库 fixtures，含 M8M9/M19/M20)/矩阵 → 双层 verdict 校验 → 结果/日志原子晋升 → tmp 清理；失败回滚旧 Canonical
  python G:\CODEX\New Manga.workspace\FEA-08\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures   # H6 全场景独立复跑（不依赖 tmp；fixtures_root 记入 h6_results.json）
  python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1   # 门禁原始日志 + 57 项 skip 来源清单
  python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2   # check 原始日志 + gates.log 摘要 + raw manifest
  ```
- Canonical Evidence pin 口径（F08I1-002 + F08I2-001）：pin sha256 = 被 pin commit 的 **Git blob 字节（LF）** SHA-256，复现 `git cat-file -p <commit>:<path>`；工作树哈希与之一致（`.gitattributes` 已为 `verification/FEA-08` 文本证据钉 `eol=lf`）；`pin_selfcheck.py` **逐行按登记 commit 复核** + stage-index blob + 干净 checkout 四方校验，结果见 `logs/pin-verify.log`（R2 曾因只信 index 而漏报一条 commit 断链，R3 已修；R5 仅 `pin-verify.log` 一项为 SHA-only，其余 71 文件均有 commit pin）。
