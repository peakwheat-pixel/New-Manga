# FEA-13-SRC-6 证据索引（源授权元数据入包 · C-09 SC-B01/SC-B07 ④）

- Task：`FEA-13-SRC-6`（SC-B01 ④ 源引用/授权元数据入包；Host staging 交接面）
- Base：`1a8bb1235`（scope 冻结点）；scope 依据 `doc/reviews/FEA-13-SRC-6-scope-r1.md`（READY-TO-FREEZE，14 paths / 6 AC）
- 契约：C-09 `SC-B01`/`SC-B01a`/`SC-B07 ④` 已预留 → **无需 UNFREEZE**；C-06/C-17 零字节、零新命令、零新错误码、零 DDL
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 入包段与加密不可读 | manifest sha/size、包内字节 == 源、`NMSAR1\0`、无明文、源文件字节/mtime 不变 | **PASS**（`logs/pytest-src6.log`） |
| AC2 缺失/不可读/空边界 | 缺失无段、空 entries 入包、不可读 `BACKUP_CREATE_FAILED` | **PASS** |
| AC3 恢复后授权可用 | overwrite restore → handoff → Host 导入 `List()`/`Authorize`；幂等/零写 | **PASS**（`logs/pytest-src6.log` + `logs/dotnet-restore-tests.log`） |
| AC4 revoked/代次/冲突 | live 优先、候选 revoked 不复活、receipt 防启动复活、read-only 零写 | **PASS**（`logs/dotnet-restore-tests.log`） |
| AC5 跨机/版本/identity 负例 | 注入必败 protector → `SOURCE_ACCESS_DENIED`/`dpapi_unprotectable`；NMSAR2 → `registry_version_unsupported`；截断 → Host 边界 `handoff_corrupt`（registry 级为 `registry_corrupt`）；live 零写 | **PASS（simulated）**；**真实跨机 DPAPI = NOT_RUN**（单机无法构造；不得记 PASS） |
| AC6 门禁/证据/变异 | `check.ps1` 默认 + `-TaskPath` PASS；`verify_pins` 18/18；定向 pytest/.NET 0 failed；diff ⊆ 14 paths；**2 变异真实 RED + 1 变异不可判别（无效，已登记）** | **PASS** |

## 门禁（本目录日志）

| 日志 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-src6.log` | 新测试 7 passed | 0 |
| `logs/pytest-nmbak-suite.log` | nmbak 全套 54 passed | 0 |
| `logs/dotnet-restore-tests.log` | Host 导入测试 9 passed | 0 |
| `logs/dotnet-host-tests.log` | Host.Tests 全量 321 / 0 / 74（总计 395） | 0 |
| `logs/gates-check.log` | check.ps1 默认 + `-TaskPath` | 0 |
| `logs/gates-pins.log` | verify_pins 18/18 | 0 |

## 变异（`mutations/`；MA 无效已如实登记）

| 变异 | 判别 | 结果 |
|---|---|---|
| MA 冲突 guard 禁用 | `LiveEntryWinsOverAnOlderOrRevokedCandidate` | **无效（NOT RED，EXIT 0）**——该变异在当前合并语义下不可判别（generation 检查先行）；R-005 如实登记，不得据此声称判别力 |
| MB 异机 DPAPI 失败映射为 no-op | `ForeignDpapiSnapshotIsRejected` | **RED**（EXIT 1） |
| MC 包内写明文 stub | `test_registry_is_packaged_verbatim` 等 | **RED**（3 failed） |

> 判别力声明：MB/MC 为真实 RED；MA 在当前合并语义下**不可判别**（不等于判别力成立），仅登记为无效变异。

## 交接面（四段）

1. 导出：`<DataRoot>/host/source-access/registry.v1.dat`（`NMSAR1` + DPAPI 密文，Core **只读不解密**）
2. 包内段：`extras/source-access/registry.v1.dat` + manifest sha256/size
3. 恢复 handoff：`<backup_root>/restore-handoff/<backup_id>/source-access/registry.v1.dat` + `handoff.json`
4. 导入 live：Host `ImportRestoredSnapshot` 原子 Save（只新增缺失 registry_id；失败 live 零写）+ `import-receipt.json`

## NOT_RUN / limitation（不得记 PASS）

- **真实跨机/他用户 DPAPI 恢复 = NOT_RUN**：单机无法构造；以注入 protector 的 simulated 负例覆盖（`ForeignDpapiSnapshotIsRejected`），二者差异已在测试与卡面写明。
- **merge restore（`mode=defer/use_backup`）不产生 handoff**：C# 未暴露 merge restore（scope r1 §5.4），登记缺口，不表现为静默成功。

## 复现

```powershell
python -m pytest tests/storage/test_nmbak_source_access.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --filter "FullyQualifiedName~SourceAccessRestoreTests"
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
