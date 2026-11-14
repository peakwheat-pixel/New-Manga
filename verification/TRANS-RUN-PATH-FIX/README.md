# TRANS-RUN-PATH-FIX 证据索引（L1-T-B，2026-11-14）

- Task：`doc/tasks/TRANS-RUN-PATH-FIX.md`（`in_progress`，base `f8a6185f9`）
- 环境：Windows；`C:\Python314\python.exe`；冻结 sidecar = `NewManga-0.1.1-win-x64/core-sidecar`

## 0. AC1 诊断结论（先定位，后修）

**一句话根因**：`INVALID_REQUEST` 不是 Host 传参错位，而是 Core 把 `EMPTY_TARGET_SELECTION`（以及 `TARGET_DELETED`）**折叠**成冻结的 `INVALID_REQUEST` 并配通用文案 "Run request is invalid"，**精确原因从不离开进程**；报告里"Core 直连同 payload 可接受"其实不是同一 payload（见 §0.3）。

### 0.1 复现（同一 payload，两个 Core，结论一致）

探针：用 Host 相同形状的 `StartRun` 帧（`{command:"translate_all", scope:{kind:"chapter",chapter_id}, overrides:{provider_bindings:{ocr:"manga-ocr"}}, idempotency_key}`，minor 3）分别打**打包 sidecar** 与**仓库 Core**，隔离数据根下建书建章（该章无页）：

| Core | 结果 |
|---|---|
| 打包 sidecar `NewManga-0.1.1-win-x64/core-sidecar/core_service.exe` | `INVALID_REQUEST` / "Run request is invalid"（minor 3、去掉 overrides、minor 7 均相同） |
| 仓库 `src/bootstrap/core_service.py`（stdio，同帧） | `INVALID_REQUEST` / "Run request is invalid"（逐字节相同的 error envelope） |

⇒ **不是版本漂移**（打包 0.1.1 与当前仓库行为一致），也不是 Host 与 Core 的形状错位。

### 0.2 被折叠掉的真实原因

在进程内直接调用 `core.pipeline.accept_start_run(...)`（绕过 wire）读到的真实异常：

```
PipelineError: 'EMPTY_TARGET_SELECTION: scope expands to no active pages'
```

抛出点 `src/application/tasks/store.py:413-421`（chapter scope 过滤后没有 active page）。
折叠点 `src/bootstrap/core_service.py:6810-6811`：

```python
if code in {"EMPTY_TARGET_SELECTION", "TARGET_DELETED"}:
    code = "INVALID_REQUEST" if code == "EMPTY_TARGET_SELECTION" else "TARGET_NOT_FOUND"
```

文案表 `src/bootstrap/core_service.py:6826`：`"INVALID_REQUEST": "Run request is invalid"`。
⇒ 任何 `PipelineError("INVALID_REQUEST", ...)`、以及被折叠的 `EMPTY_TARGET_SELECTION`，在 wire 上**长得一模一样**，报告方无法区分"payload 形状错"与"章节没有可处理页面"。

### 0.3 报告里"同 payload"的差异（已排除的假设）

`verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py:197-208` 实际发的是：

| 维度 | 直连探针（成功路径） | Host/App（失败路径） |
|---|---|---|
| command | `translate_untranslated` | `translate_all`（`WorkbenchViewModel.cs:14`） |
| scope | `{"kind":"book","book_id":…}` | `{"kind":"chapter","chapter_id":…}`（`WorkbenchViewModel.cs:172-176`） |
| overrides.provider_bindings | `{ocr: manga-ocr, translate: <provider>}` | `{ocr: manga-ocr}`（`RunBindingDefaults` 当时只有 ocr） |

book scope 能展开到**该书其它章节**的页面，chapter scope 只看本章 ⇒ 隔离根里"本章无 active page"时，直连（book scope）成功、Host（chapter scope）失败，两者并不矛盾。

**已排除的假设**：① 打包/仓库 Core 版本漂移（§0.1 两条路径逐字节一致）；② Host payload 形状错位（字段名/嵌套/scope 解析均与 Core 校验一致：`RunPayloads.StartRun` → `HostCommandDispatcher.cs:547-555` → `core_service.py:6692-6715`）；③ 协议 minor 不匹配（minor 3/7 结果相同）；④ `provider_profiles` 在 minor 3 被拒（App 不注入该键）。

## 1. AC 逐条

| AC | 结论 | 交付 |
|---|---|---|
| **AC1 先诊断后修** | **PASS** | §0；复现脚本与结论；**不改冻结契约** |
| **AC2 修复** | **PASS（可诊断性修复，非行为变更）** | `core_service.py:6808-6819` 在折叠前把精确原因打到 stderr（`[core.run] <Command> refused: <CODE>: <detail>`），Host 已捕获 Core stderr；wire 字节零变更 |
| **AC3 RunBindingDefaults 扩展** | **PASS** | `RunBindingDefaults.cs`：默认 = `{"ocr":"manga-ocr"}`，**当配置了 translate provider 时**追加 `translate`（`NEWMANGA_RUN_TRANSLATE_PROVIDER` 或显式入参）；显式 `overrides.provider_bindings` 仍完全优先（不合并、不覆盖）；`NEWMANGA_RUN_PROVIDER_BINDINGS` 关闭口保持 |
| **AC4 零契约面** | **PASS** | 无新 wire 命令、无新 `IHostController` 成员；`--check` 1/80/6=87；pins 18/18 |
| **AC5 判别测试** | **PASS** | `tests/core/test_trans_run_path_fix.py`（2 例：Host payload 被拒 + stderr 含 `EMPTY_TARGET_SELECTION`；形状错与目标错在日志里可区分）；`TransRunPathFixTests`（4 例：默认含 translate / 无配置保持 ocr-only / dispatcher 注入 translate / 显式 override 优先），后两例在冻 sidecar 上真跑 |
| **AC6 门禁** | **PASS** | 见 §2 |
| **AC7 若不可修** | **不适用（未用限制收尾）** | 根因已定位并修复可诊断性；仍存在的产品侧限制见 §3 |

## 2. 测试与门禁（原始输出见 logs/）

- `C:\Python314\python.exe -m pytest -q tests/core/test_trans_run_path_fix.py` → **2 passed**
- `dotnet test NewManga.CoreClient.Tests --filter TransRunPathFixTests`（`NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向冻结 sidecar）→ **4 passed / 0 skipped**
- 全量与四门禁：`logs/pytest-full.log`（**3564 passed / 10 skipped / 0 failed**，312.93s）、`logs/gates.log`（四门禁 EXIT=0，inventory `1/80/6=87`，pins 18/18）
- .NET（不带 sidecar 环境变量的仓库基线）：CoreClient.Tests **182 / 0 / 26**、Host.Tests **351 / 0 / 44**、App.Tests **915 / 0 / 11**
- 说明：把 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向 0.1.1 发布 sidecar 并让**全部** .NET 测试跑时，会激活一批期望「models sidecar」的用例（CoreClient 1 红、App 6 红）；那是 fixture 不匹配，不是本卡改动引起——本卡的 2 条 dispatcher 用例在该 sidecar 上单独跑是 **4 passed / 0 skipped**。

## 3. 仍存在的限制（如实登记）

1. **wire 仍是 `INVALID_REQUEST` 通用文案**（冻结错误面），终端用户看不到"本章无可处理页面"；要改需契约 UNFREEZE（未做）。当前只能靠 Core stderr 日志定位。
2. **Host 不做前置探测**（如 `list_chapter_pages` 预检），因为那会把产品行为从"Core 拒绝"改成"Host 预判拒绝"，属产品决策，未在本卡擅自引入。
3. **自动注入 translate 的值来源**：本卡用 `NEWMANGA_RUN_TRANSLATE_PROVIDER`（Host 侧配置），未做"从 P15 binding 反查 translate provider"的运行时查询（那会给每次 StartRun 增加一次 Core 往返，且有 T-A 的镜像已覆盖全局槽，属可选优化）。
4. **真实远程翻译未复跑**（REAL-TRANSLATE-PROVIDER-1 AC3 的额度阻塞仍在）。