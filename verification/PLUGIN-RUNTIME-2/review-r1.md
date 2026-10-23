---
task_id: PLUGIN-RUNTIME-2
reviewer: reviewer-settings-a
author: reviewer-settings-a
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
reviewed_head: 050530dfb78afaa9877eac1ce727cd40f69f5837
decision: changes_requested
---

# Review：PLUGIN-RUNTIME-2 r1

本次变更将本地插件接入 detect、ocr、export 的真实输入及结果观察点。独立审查发现两项导出行为缺陷，固定 head 需要修复后复审；既有 81 项定向测试通过不能覆盖这两项真实 StartExport 场景。

## 范围与依据

- 依据：AGENTS.md、AD-001、STATUS/Plan 当前 DAG、PLUGIN-RUNTIME-2 冻结范围与 AC1/AC2、PLUGIN-RUNTIME-1 最新 r3 Review 及已接受的 trusted-code 限制、协作协议与 Review 模板。
- 独立 reviewer 非实现者；仅新增本报告，不改生产、测试、他人治理文件，不提交，不执行 push/merge/reset/stash。
- 审查固定 base/head 的 diff、PluginService、runner、ProductionHandlers、Core assembly，以及真实 CoreServiceServer → P16ExportRuntime → ExportService 调用链。以下行号均为固定 reviewed_head 的行号。
- 开始时 main、Git common directory `.git`，六个既有 P04 未跟踪诊断文件保留。主 Agent 随后提交文档至 `695efe5cbd73e6a4193798b48ad20e1bff31029d`，该提交相对 reviewed_head 只有 Task/Handoff/validation 文档变化；复现和定向检查完成后主 Agent 开始修订生产代码，本报告不对其后修订给出批准。

## Findings

### R1 — P1：文本导出合法覆盖未作用于实际输出

- 位置：`src/application/export/service.py:257`、`:503`；相关调用者 `src/bootstrap/core_service.py:2945`。
- 触发：原始 StartExport 请求 `format=text, format_options={"text_representation":"txt"}`，插件 before_export 返回 `{"format_options":{"text_representation":"json"}}`。
- 问题：Core 在 Hook 前已经按 TXT 生成 `text_content`；Hook 只替换 options，而 `_build_payload` 直接返回原先的 `request.text_content`。Run 完成，底层历史却记录 JSON，实际输出仍是 TXT。违反 AC1 的“合法覆盖实际输入”。
- 复现：下方真实 Core 脚本输出 `SNAPSHOT text completed`、`SQLITE_HISTORY text {'text_representation': 'json'}`、`ACTUAL_TEXT_IS_JSON False`，没有 plugin_error。
- 最小完整修复方向：在派生文本内容前确定最终 Hook 输入，或基于最终 options 延迟生成文本内容；加入真实 StartExport 的 TXT→JSON 回归，断言输出可解析且内容与最终参数一致。不得只改历史字段。
- 状态：open，固定 head 未修复。

### R2 — P2：插件覆盖与持久化运行历史使用不同输入快照

- 位置：`src/application/export/service.py:257`；关联 `:779`、`:795`、`:854`、`:857`。
- 触发：StartExport 请求 ZIP compression=standard，插件改为 store。
- 问题：P16ExportRuntime.start 提前把旧 options 存入 job.history；ExportService 的局部 replace 没有同步 job。history() 优先返回 job.history，并跳过相同 export_id 的底层真实历史，所以用户读取的历史仍是 standard，实际 ZIP 已是 STORED；重启从 job store 恢复后同样保留错误快照。后续根据历史参数重复导出会使用错误输入。
- 复现：下方脚本输出 `RUNTIME_HISTORY zip [{'compression': 'standard'}]`、`SQLITE_HISTORY zip {'compression': 'store'}`、`ACTUAL_ZIP_COMPRESSION 0`（ZIP_STORED）。
- 最小完整修复方向：在建立运行/历史快照前确定最终输入，使实际导出、job history、底层 history 共用最终参数；确保 Hook 一次调用，不可通过重复执行插件同步快照。加入经真实 P16ExportRuntime 的参数、输出及恢复历史一致性回归。
- 状态：open，固定 head 未修复。

## Architecture

白名单覆盖只允许 detect.options、ocr.script/direction/options、export.format_options，未授予身份、源图字节、目标路径、Lock/Revision 或发布回调覆盖权。非法 OCR 值可回退并审计；after 返回值被丢弃。Core assembly 共用同一 PluginService；未新增 IPC/UI/Schema/依赖。子进程 UTF-8 显式配置解决 `-I` 下环境编码变量无效的问题，日文 OCR payload 及中文输出上限回归通过。

Architecture 结论：隔离与冻结字段范围未发现新增越权，但导出 Hook 时机晚于派生内容与历史快照，导致 R1/R2；当前固定 head 不可批准。沿用已接受的 trusted-code、stdin/进程树限制，不把既有 OS 沙箱缺失重复列为新 finding。

## Verification

执行环境：Windows PowerShell，`C:\Python314\python.exe`，Python `3.14.6`，`python -X utf8`；源实现为固定 reviewed_head，之后文档提交不改变源实现。没有 skipped。

| 检查 | 结果 | 判别力证据 |
|---|---|---|
| runtime/provider/Core wire/Core assembly 定向检查 | PASS，61 passed / 0 skipped | 原始输出与命令见下 |
| 与 Handoff 相同四文件定向检查 | PASS，81 passed / 0 skipped | 原始输出与命令见下；与上行重叠，不累计为 142 个独立用例 |
| 真实 StartExport ZIP/TEXT 插件覆盖 | FAIL，R1/R2 | 完整可复制脚本及输出见下 |
| governance check | PASS，3 warnings | 原始输出见下 |
| detect/export 的完整 PipelineRun 故障矩阵 | NOT_RUN | 新增 detect 测试直调 Handler、export 测试直调 ExportService；OCR 测试经 PipelineService，覆盖 disabled/crash/timeout/invalid；本次额外验证真实 StartExport 的成功路径 |
| GUI、完整模型、全量 pytest、安装包 | NOT_RUN | 本切片无 UI/IPC/打包改动；没有相应新证据 |

### 原始执行日志

```text
SHELL=PowerShell; PYTHON=C:\Python314\python.exe; VERSION=3.14.6; UTF8=-X utf8
COMMAND=python -X utf8 -m pytest tests/infrastructure/test_plugin_runtime.py tests/providers/test_handlers_pipeline.py tests/core/test_core_plugin_wire.py tests/core/test_core_assembly.py -q --basetemp='G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r1'
.............................................................            [100%]
61 passed in 4.62s
EXIT=0

COMMAND=python -X utf8 -m pytest tests/providers/test_handlers_pipeline.py tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py tests/reading_export/test_export.py -q --tb=short --basetemp='G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r1'
........................................................................ [ 88%]
.........                                                                [100%]
81 passed in 4.29s
EXIT=0

COMMAND=pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\PLUGIN-RUNTIME-2.md
WARN: 存在 3 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3163 bytes / 31 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5445 bytes / 51 lines
Governance check: PASS (3 warnings)
EXIT=0
```

### 真实 Core 复现脚本

于仓库根目录，固定 reviewed_head 源实现运行。PowerShell here-string 管道执行，不创建脚本文件。测试素材仅在指定 workspace temp 子目录；后续 pytest 重建 basetemp，故本报告内嵌脚本/原始输出是保留证据，不能依赖临时文件存在。

```powershell
@'
import sys, runpy, json, zipfile
from pathlib import Path
sys.path.insert(0, 'src')
m=runpy.run_path('tests/core/test_p16_reader_export.py')
p=Path('G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r1/repro')
p.mkdir(parents=True, exist_ok=True)
core, server, catalog, pages=m['_seed_core'](p)
try:
    plugin=p/'data'/'plugins'/'review-hook'
    plugin.mkdir(parents=True)
    (plugin/'manifest.json').write_text(json.dumps({'id':'review-hook','name':'Review','version':'1.0.0','entry':'plugin.py','hooks':['before_export'],'permissions':[]}),encoding='utf-8')
    (plugin/'plugin.py').write_text("def before_export(payload):\n    opts=payload['input']['format_options']\n    return {'format_options': {'compression':'store'} if 'compression' in opts else {'text_representation':'json'}}\n",encoding='utf-8')
    core.plugins.set_plugin_enabled('review-hook',True)
    core.plugins.set_global_enabled(True)
    ids=[x['page'].page_id for x in pages['chapter']]
    for fmt,opts in [('zip',{'compression':'standard'}),('text',{'text_representation':'txt'})]:
        target=p/('result.'+fmt)
        ref,_=m['_make_grant'](server,target,fmt)
        response=m['_rpc'](server,'StartExport',m['_export_payload']('chapter',ids,fmt,opts,ref))
        assert response['error'] is None,response
        snap=m['_wait_export'](server,response['result']['export_id'])
        print('SNAPSHOT',fmt,snap['status'])
        eid=response['result']['export_id']
        print('RUNTIME_HISTORY',fmt,[x['format_options'] for x in server._exports.history() if x['export_id']==eid])
        stored=[x for x in core.export_history_store.read() if x['export_id']==eid][0]
        print('SQLITE_HISTORY',fmt,json.loads(stored['scope_snapshot_json'])['format_options'])
        if fmt=='zip':
            with zipfile.ZipFile(target) as z: print('ACTUAL_ZIP_COMPRESSION',z.infolist()[0].compress_type)
        else:
            try: json.loads(target.read_text(encoding='utf-8')); print('ACTUAL_TEXT_IS_JSON',True)
            except ValueError: print('ACTUAL_TEXT_IS_JSON',False)
        print('PLUGIN_ERRORS', [e['detail'] for e in core.plugins.audit_list(100) if e['event_type']=='plugin_error'])
finally:
    catalog.close()
    core.conn.close()
'@ | python -X utf8 -
```

```text
SHELL=PowerShell; PYTHON=C:\Python314\python.exe; VERSION=3.14.6; UTF8=-X utf8
SNAPSHOT zip completed
RUNTIME_HISTORY zip [{'compression': 'standard'}]
SQLITE_HISTORY zip {'compression': 'store'}
ACTUAL_ZIP_COMPRESSION 0
PLUGIN_ERRORS []
SNAPSHOT text completed
RUNTIME_HISTORY text [{'text_representation': 'txt'}]
SQLITE_HISTORY text {'text_representation': 'json'}
ACTUAL_TEXT_IS_JSON False
PLUGIN_ERRORS []
EXIT=0
```

Verification 结论：既有定向测试通过，但真实 Core 复现反证 AC1 全面满足；判定 changes_requested。

## 结论与下一步

**changes_requested**。固定 head 的 R1/R2 修复并加入真实导出回归后，提交新 head/Handoff，再由非实现者复审。当前 Task 保持 in_review/按 Codex 裁决转入修复，不在本报告关闭 Task。

推荐下一步：Codex 在 PLUGIN-RUNTIME-2 内修复上述两项，明确授权涉及的 Core 调用者路径，保持禁止 IPC/UI/Schema/依赖扩展；交付新固定 head、真实 StartExport 回归和验证记录给 reviewer-settings-a。无需释放新的产品 Task。

未检查：GUI、真实模型质量、全量 pytest 与打包；它们不替代本次两项导出缺陷回归。
剩余风险：受信任插件仍有用户 OS 权限；既有 stdin 阻塞与进程树限制沿用前期接受的边界。
