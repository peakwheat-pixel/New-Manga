---
task_id: PLUGIN-RUNTIME-2
reviewer: reviewer-settings-a
author: reviewer-settings-a
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
reviewed_head: 55af609b0cbb4d7dc29160df150b116989b3b0be
decision: changes_requested
---

# Review：PLUGIN-RUNTIME-2 r2

R1/R2 的正常覆盖路径已修复，但新增参数校验放行空对象，导致插件能使文本导出在创建 job 前失败，且没有 plugin_error 审计。固定 head 仍需修复后复审。

## 范围与依据

本次复审沿用 r1 的架构、Task 冻结字段和 trusted-code 边界，重点核对 `050530dfb..55af609b0` 的生产/测试修改及关联调用者。Task 已明确允许 `src/bootstrap/core_service.py`；未新增 IPC/UI/Schema/依赖。Reviewer 非实现者，仅写本报告，不改生产/测试，不提交。六个既有 P04 未跟踪诊断文件保留。

## r1 处置复核

| Finding | 状态 | 依据 |
|---|---|---|
| R1 文本实际输出未应用覆盖 | fixed | `text_content_factory` 按最终参数生成文本；真实 StartExport TXT→JSON 回归断言 JSON 内容 |
| R2 job history 与最终参数不一致 | fixed | P16ExportRuntime.start 在保存 job 前调用 prepare_request，accept/history 使用同一最终参数；恢复 Runtime history 也检查一致 |

`hooks_prepared` 使 start 和 export 共用准备结果，真实 Core 测试检查 before/after 共 2 个 hook_invoked，避免重复执行 before；after 返回 status=failed 不改变 completed。上述回归实际通过。

## Finding

### R3 — P1：空 format_options 覆盖绕过校验，使文本导出失败且未审计

- 固定 head 位置：`src/application/export/service.py:259`（`if options and ...`），`:273`（调用 text_content_factory）；关联 `src/bootstrap/core_service.py:3081`（读取 `options["text_representation"]`）。
- 触发：合法文本 StartExport 请求含 `{"text_representation":"txt"}`，插件返回 `{"format_options":{}}`。
- 实际行为：空对象跳过新增校验，进入 factory 后 KeyError；StartExport 返回 UNKNOWN/internal，未创建 job、未生成文件，没有 plugin_error。违反 AC2/函数注释所要求的坏覆盖跳过并审计、主链继续，也违背 Handoff “拒绝非法值后用原输入继续”的承诺。target_ref 在此之前已经消耗，用户需要重新取得导出授权。
- 最小修复：对具有必需选项的真实 P16 请求拒绝空覆盖，走已有 apply_input 的 PLUGIN_INVALID_OVERRIDE 审计和原输入回退；若需要保留旧式直接 ExportService 空 options 的兼容行为，应依据原始请求明确区分。增加真实 StartExport 回归，断言 completed、原格式输出与 history 一致，并出现 plugin_error。
- 状态：open；本报告只判定固定 head，不覆盖其后修订。

## Architecture / Verification 结论

Architecture：R1/R2 的准备时机、最终快照和幂等处理符合冻结范围；内部 callback/标记没有进入 IPC。新校验遗漏空对象边界，错误逃出插件隔离处理，当前不可批准。

Verification：Windows PowerShell、`C:\Python314\python.exe`、Python 3.14.6，UTF-8。源文件与固定 reviewed_head 在运行前核对无 diff。

| 检查 | 结果 | 证据 |
|---|---|---|
| Core P16 + ExportService 定向测试 | PASS，49 passed / 0 skipped | 下方实际原始输出；包括新增 ZIP/TEXT 两项真实 Core 回归 |
| 空 format_options 真实 Core 复现 | FAIL，R3 | 下方完整脚本及原始输出 |
| r1 的 OCR timeout/crash/disabled 矩阵 | NOT_RUN（本轮不重复） | r1 已验证，本轮未修改相应实现；不把历史结果计为新执行 |
| GUI、全量 pytest、模型质量、打包 | NOT_RUN | 未产生此类证据 |

```text
SHELL=PowerShell; PYTHON=C:\Python314\python.exe; VERSION=3.14.6; UTF8=-X utf8
COMMAND=python -X utf8 -m pytest tests/core/test_p16_reader_export.py tests/reading_export/test_export.py -q --tb=short --basetemp='G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r2'
.................................................                        [100%]
49 passed in 4.61s
EXIT=0
```

## 可复制复现

固定 head 源实现、仓库根目录执行；仅创建 workspace temp 测试素材，不修改真实用户数据。

```powershell
@'
import sys,runpy,json
from pathlib import Path
sys.path.insert(0,'src')
m=runpy.run_path('tests/core/test_p16_reader_export.py')
p=Path('G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r2/empty-options-repro')
p.mkdir(parents=True,exist_ok=True)
core,server,catalog,pages=m['_seed_core'](p)
try:
    plugin=p/'data'/'plugins'/'empty-options'
    plugin.mkdir(parents=True)
    (plugin/'manifest.json').write_text(json.dumps({'id':'empty-options','name':'Empty','version':'1.0.0','entry':'plugin.py','hooks':['before_export'],'permissions':[]}),encoding='utf-8')
    (plugin/'plugin.py').write_text("def before_export(payload):\n    return {'format_options': {}}\n",encoding='utf-8')
    core.plugins.set_plugin_enabled('empty-options',True)
    core.plugins.set_global_enabled(True)
    target=p/'result.txt'
    ref,_=m['_make_grant'](server,target,'text')
    response=m['_rpc'](server,'StartExport',m['_export_payload']('chapter',[pages['chapter'][0]['page'].page_id],'text',{'text_representation':'txt'},ref))
    print('RESPONSE',json.dumps(response,ensure_ascii=False))
    print('TARGET_EXISTS',target.exists())
    print('PLUGIN_ERRORS',[x['detail'] for x in core.plugins.audit_list(100) if x['event_type']=='plugin_error'])
    print('JOBS',len(server._exports._jobs))
finally:
    catalog.close()
    core.conn.close()
'@ | python -X utf8 -
```

```text
SHELL=PowerShell; PYTHON=C:\Python314\python.exe; VERSION=3.14.6; UTF8=-X utf8
RESPONSE {"protocol": "new-manga.core", "version": {"major": 2, "minor": 3}, "request_id": "ca9a852b4ccd4d3e84124653e05eefe9", "result": null, "error": {"code": "UNKNOWN", "category": "internal", "message": "Reader or export operation failed", "retryable": false}}
TARGET_EXISTS False
PLUGIN_ERRORS []
JOBS 0
EXIT=0
```

## 结论与下一步

**changes_requested**。推荐 Codex 在本 Task 修复 R3、补真实 Core 空覆盖回归，固定新提交并交非实现者复审；不释放新产品 Task，不在本报告关闭 Task。

未检查：GUI、模型质量、完整测试集与打包；本轮复审不重复未修改的 OCR 隔离矩阵。
剩余风险：R3 仍使合法导出被插件坏覆盖中断；既有 trusted-code/进程树边界不变。
