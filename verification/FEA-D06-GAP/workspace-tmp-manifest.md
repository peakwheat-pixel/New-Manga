# FEA-D06-GAP 仓外临时资源清单（Resource Manifest 载体）

- **采集时间**：2026-11-01
- **目录**：`G:\CODEX\New Manga.workspace\tmp\`（仓库外，未被 git 跟踪；`git status` 不受影响）
- **文件数**：32
- **disposition**：`PRESERVE_UNKNOWN`（**不删除、不移动**）
- **为什么保留**：这些脚本是 2026-11-01 契约线的工作产物，其中 `add_c08_d06.py` 等**直接生成/改写了被冻结契约的字节**（C-08 v6/v7 的 SC-R06…SC-R09、C-08/AC8/AC9 相关记录）。删掉会降低冻结字节的可复现性，属于「不得删除既有证据」的边界，故原地保留并登记。
- **引用/进程检查**：均为一次性 Python 修改器与文本/日志产物；无运行中的进程持有；不在任何 git 工作区内；无用户数据；无 worktree / task-env / dataset / build artifact。
- **与 WORKSPACE_GOVERNANCE 的差异**：未按 `temp/<TASK-ID>/` 分目录（历史遗留，属跨 Task 共享残留）；本清单按「源/哈希/关联/检查结果」逐项闭环，不改动文件位置。

| # | 文件 | 字节 | sha256 | mtime | 关联 |
|---|---|---|---|---|---|
| 1 | `add_c08_d06.py` | 6782 | `746de56b0ee86aaa6d86b3a2372e799dd892dc5cf35a788cca7c68684862532d` | 2026-11-01 11:14 | C-08 SC-R06…R09（冻结字节生成） |
| 2 | `c08pin.txt` | 66 | `3c3f89fa219ca9b844a807cf2e4e4f3ef76e20ed486f1399c65dd5daed1b31e6` | 2026-11-01 11:14 | C-08 pin 记录 |
| 3 | `fix_c08_rec.py` | 1786 | `be2a742537d05998e8527d8391d0c5bfcfb5b8217ad258bfbb5195901d1a22ad` | 2026-11-01 11:19 | C-08 冻结记录 |
| 4 | `fix_c08_r9.py` | 7432 | `84c894864e5e530afaf3fbb31c829f4351c1add41993c92e994d15b468021584` | 2026-11-01 11:18 | C-08 r9 处置 |
| 5 | `fix_c08_r9b.py` | 6823 | `dd309faf6b83257a36fc78f6d5d543e51ebf065930287bbc4a20d440db8d666a` | 2026-11-01 11:18 | C-08 r9 处置（续） |
| 6 | `fix_r11.py` | 4700 | `0c251ea6f36d4bc8003eb3c1704a9fe2c7f9340e7c3d57f5eb50c5e392e3fc3f` | 2026-11-01 11:23 | C-08 r11 记录同步 |
| 7 | `fix_s7.py` | 2124 | `7d118b91275148aa64c60ef2913569aebd970fec16c0771049d3873d2569de6b` | 2026-11-01 11:24 | C-08 §7 结构 |
| 8 | `sync_c08_records.py` | 6370 | `38c68093a495c72eb69d1642ad56caec849688c1809e48f378543cdb6af363f5` | 2026-11-01 11:21 | C-08 记录同步 |
| 9 | `update_c08_record.py` | 2175 | `2e7c689d15761e618e9ec381e0880b122e175f4c7db88868f472bdf3db71a412` | 2026-11-01 11:14 | C-08 冻结记录 |
| 10 | `fix_ac8.py` | 5210 | `7c7e4acebf63b37674bad8a9506f7cfeea5cf356f06163b3c10f79a2f0d78232` | 2026-11-01 11:31 | AC8 D04–D07 覆盖 |
| 11 | `fix_ac9.py` | 2989 | `35e341105db7227480c584db388bba3386e3231fb70e9294ef71575e483e34bc` | 2026-11-01 11:39 | AC9 Gate 判定 |
| 12 | `fix_matrix.py` | 1179 | `7c7286944ec9cf7c3fa7b968dadeb31dd379a40b02896f6191693949fed10d12` | 2026-11-01 10:31 | 冻结矩阵 |
| 13 | `fix_matrix2.py` | 2984 | `0e1401a41db26a2eaa1d0737b62ddb54172bb6fb54be243c72951b9fe8e0e14d` | 2026-11-01 10:31 | 冻结矩阵 |
| 14 | `fix_matrix_final.py` | 2561 | `35ca40c47ae1d8109da3444e410a25157f292529d753fc21aeda78a060e982a7` | 2026-11-01 11:42 | 冻结矩阵（最终） |
| 15 | `fix_tasks_d06_d07.py` | 4572 | `082222065bb04405c2feca80481ac453d8ac41d1e8baedb221862d4937218039` | 2026-11-01 10:51 | FEA-D06-GAP / FEA-D07 任务卡 |
| 16 | `fix_1a_residual.py` | 1779 | `acc9cdd2278ac31d03b4982513e3de230a2e45f358dd6988438e0cf1e045b785` | 2026-11-01 10:30 | 冻结记录 §1A |
| 17 | `fix_1a_residual2.py` | 1476 | `f1c32a175413d624b28d2702e6f86a4d65449fd1ed89171f05e0e61a21c619a5` | 2026-11-01 10:31 | 冻结记录 §1A（续） |
| 18 | `fix_c14_r1.py` | 8063 | `bd2feccc3a28c570fffbb4a946ee206dff8b9ebc16269fb3b98b2183ebe6e58b` | 2026-11-01 10:21 | C-14 r1 处置 |
| 19 | `fix_c14_r2.py` | 3038 | `24341a26103a3285fc59388bf9ff2eb1494762b719f82e458da229f7c87adad6` | 2026-11-01 10:23 | C-14 r2 处置 |
| 20 | `c14_sha.txt` | 66 | `59ba806b8d8dbe336c5474d4457195b69fe55bd993b44701e941ca27d1f86c9f` | 2026-11-01 10:23 | C-14 pin 记录 |
| 21 | `extend_c09.py` | 8881 | `bc481788238b327922c33b1d80996851dc5a7fc851889c7ce00c0ad3bdd07fc1` | 2026-11-01 10:52 | C-09 条款扩展 |
| 22 | `reorder_c09.py` | 1307 | `15576f84a07928205733ead50ceb43df7420fb45ef58bd2cdcd9b5e12faa85e3` | 2026-11-01 10:52 | C-09 章节重排 |
| 23 | `fix_c09_r3.py` | 8592 | `34746e5fd1d6deddfbd0fe04b5838ffdc81b149805a074c895cc0849ac6f9417` | 2026-11-01 10:57 | C-09 r3 处置 |
| 24 | `fix_c09_k.py` | 3380 | `97cec8bb2b1bfd291bfafe7ba7e018057f7c3f85aa7ff822999a6e48aabcf884` | 2026-11-01 11:00 | C-09 K 项处置 |
| 25 | `c09_sha.txt` | 66 | `53f4dbc51e08751687e93f47fb168152ea68fb04e118469c0fc63986ead16993` | 2026-11-01 11:00 | C-09 pin 记录 |
| 26 | `render_status.py` | 7900 | `8e9f5f75f1582b49c9cbb72d26538024268de69f6133a2ccb3817529323386a4` | 2026-11-01 08:06 | 状态图渲染脚本 |
| 27 | `project-status-2026-11-01.png` | 265136 | `78635726b5ccd165d41cb9139dfcd8a2361abe590135c6c9b45630317e4838d4` | 2026-11-01 08:06 | 状态图产物（非证据） |
| 28 | `integration-safety7.log` | 679 | `dfb7e0bbec894a811b784ae22ce19584497e08c082f2633a756d26b92349cb25` | 2026-11-01 01:49 | 早前会话集成检查日志 |
| 29 | `integration-safety8.log` | 679 | `483bf19f99263664d990e21df9a2552f3f7e54c4a8c32839146e00d9071b6012` | 2026-11-01 02:11 | 同上 |
| 30 | `integration-safety9.log` | 679 | `c3ad532b90425ffc84bd1705fc4125cea3e21b314897cda5e5cb88def3a71d45` | 2026-11-01 02:26 | 同上 |
| 31 | `integration-safety10.log` | 682 | `9395254b96f892443b989e2613781b8426b76ea08d323daf45ce16dd9d3748a4` | 2026-11-01 02:54 | 同上 |
| 32 | `integration-safety11.log` | 679 | `7a3749a82b4d5312a1b93060e06d1c64a5fbfba8276c9464d572b83c4d56583f` | 2026-11-01 03:02 | 同上 |

## 关闭处置

- 全部 32 项：`PRESERVE_UNKNOWN` —— 原地保留，不删除、不迁移、不归档；原因是其中多项是**冻结契约字节的生成脚本**，删除会破坏可复现性。
- 计数：`deleted=0 / moved=0 / migrated=0 / archived=0`。
- 复核方法：本文件逐项给出 sha256；任何人可对 `G:\CODEX\New Manga.workspace\tmp\<name>` 重算比对。
