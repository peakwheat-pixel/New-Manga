"""Reproduce the governance inventory; read Git and task metadata, not user data."""
from pathlib import Path
import collections
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def git(*args, cwd=ROOT):
    p = subprocess.run(['git', *args], cwd=cwd, capture_output=True, encoding='utf-8', errors='replace')
    return {'command': ['git', *args], 'exit': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}


def metadata(text):
    blocks = re.split(r'^---[ \t]*\r?$', text, flags=re.M)
    found = []
    for block in blocks:
        d = dict(re.findall(r'^([\w_]+):[ \t]*(.*)$', block, re.M))
        if 'id' not in d:
            continue
        dep = re.search(r'^depends_on:[ \t]*(.*?)(?=^\w+:|\Z)', block, re.M | re.S)
        d['deps'] = re.findall(r'\b(?:M2-[A-Z0-9-]+|TASK-\d{3}|T\d\.\d\.\d(?:-REPAIR-\d+)?|GOV-001|DIAG-[A-Z0-9-]+|DOC-FIX-[A-Z0-9-]+)\b', dep.group(1) if dep else '')
        found.append(d)
    return found


def clean(value):
    return value.split(' #')[0].strip().strip('"').replace('|', '/')


if '--check' in sys.argv:
    sample = '---\nid: OLD\nstatus: proposed\ndepends_on: []\n---\ntext\n---\ntext\n---\nid: CURRENT\nstatus: done\ndepends_on:\n- M2-C1\n- TASK-001\n---\n'
    parsed = metadata(sample)
    assert [x['id'] for x in parsed] == ['OLD', 'CURRENT']
    assert parsed[-1]['deps'] == ['M2-C1', 'TASK-001']
    snapshot = json.loads((OUT / 'inventory.json').read_text(encoding='utf-8'))
    tasks = snapshot['tasks']
    assert len(tasks) == 190 and len({r['id'] for r in tasks}) == 190
    assert sum(snapshot['counts'].values()) == 190
    assert not snapshot['missing_dependency_ids']
    assert next(r for r in tasks if r['id'] == 'M2-TA2B')['raw_status'] == 'done'
    graph = (OUT / 'TASK_GRAPH.md').read_text(encoding='utf-8')
    assert graph.count('```') % 2 == 0
    assert all(r['id'] + '<br/>' in graph for r in tasks)
    for block in re.findall(r'```mermaid\n(.*?)```', graph, re.S):
        declared = re.findall(r'^  (N\d+|X\d+)\[', block, re.M)
        assert len(declared) == len(set(declared))
        edge_nodes = set(re.findall(r'^  (\w+) --> (\w+)$', block, re.M))
        assert all(a in declared and b in declared for a, b in edge_nodes)
    for path in [OUT / 'REPORT.md', OUT / 'TASK_GRAPH.md']:
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            assert (path.parent / link.split('#')[0]).exists(), (path, link)
    print('PASS: multi-block metadata, multiline deps, 190 unique task nodes, counts, dependency coverage, Mermaid nodes/edges, report links')
    raise SystemExit(0)


head = git('rev-parse', 'HEAD')['stdout']
cache_path = OUT / 'inventory.json'
cache = json.loads(cache_path.read_text(encoding='utf-8')) if '--reuse-git' in sys.argv and cache_path.exists() else {}
assert not cache or cache['audit_head'] == head, 'Git cache HEAD changed; rerun without --reuse-git'
cached_tasks = {r['id']: r for r in cache.get('tasks', [])}
plan = (ROOT / 'doc/REBASELINE_PLAN.md').read_text(encoding='utf-8-sig')
wt = git('worktree', 'list', '--porcelain')
worktrees = cache.get('worktrees', [])
for block in ([] if cache else wt['stdout'].split('\n\n')):
    d = dict(line.split(' ', 1) for line in block.splitlines() if ' ' in line)
    if 'worktree' in d:
        d['status'] = git('status', '--porcelain', cwd=d['worktree'])
        worktrees.append(d)

rows = []
for path in sorted((ROOT / 'doc/tasks').glob('*.md')):
    text = path.read_text(encoding='utf-8-sig')
    blocks = metadata(text)
    if not blocks:
        continue
    d = blocks[-1]
    task = clean(d['id'])
    state = clean(d.get('status', 'UNKNOWN'))
    owner = clean(d.get('owner', 'NOT_ASSIGNED'))
    if owner in ('null', 'TBD', '') or owner.startswith('TBD '):
        owner = 'NOT_ASSIGNED（建议 ' + clean(d.get('suggested_owner', 'UNKNOWN')) + '）'
    notes = []
    effective = state
    if task.startswith('TASK-'):
        num = int(task[-3:])
        effective = 'LEGACY_VERIFIED_COMPLETE'
        if num in [1, 2, 3, 24, 28]: effective = 'LEGACY_DOC_ONLY'
        if num in [4, 16, 17, 18, 19, 20, 21, 23, 33]: effective = 'LEGACY_PARTIAL'
        if num in [22, 25, 26, 27, 47, 48]: effective = 'LEGACY_SUPERSEDED'
    elif task.startswith('T3.2.1-REPAIR-') and not state.startswith('done'):
        effective = 'LEGACY_ARCHIVED_UNFINISHED'
        notes.append('父任务已 closed_with_limitations；原状态不授予实施权限')
    elif task == 'T3.2.1': effective = 'CLOSED_WITH_LIMITATIONS'
    elif task in ['T2.1.1', 'T2.2.1']: effective = 'LEGACY_VERIFIED_COMPLETE'
    elif task in ['M2-SFX-ANNOTATE-R2', 'M2-SFX-SYNTH-BG-AUTO']:
        effective = 'DONE_RECORDED'
        if not state.startswith('done'): notes.append('STATE_CONFLICT：Task 页头落后于 Plan 与集成历史')
        notes.append('Review 原报告在当前 tracked 树未定位；仅确认已有批准记录，不追加独立批准')
    elif state.startswith('done'): effective = 'DONE_RECORDED'
    elif state.startswith('verified_complete'): effective = 'DONE_RECORDED'
    if task == 'M2-TA2B': notes.append('两套 metadata；采用后部开放素材方案，Manga109 永久取消')
    if task == 'M2-TA3-B': notes.append('阶段一 done；阶段二旧 blocker 已由 B2/KO-RERUN/B3 后继任务取代')
    if task == 'M2-DOCTR-QUAL-RUN': notes.append('任务完成；质量结论 FAIL，后续 C4/C1 与 PROD-DETECT 路线已完成')
    if task == 'M2-DERIVED-GC-1': notes.append('PARTIAL mitigation；有行有文件的轮换旧 preview 回收未实现')
    if task == 'M2-TA3-B2': notes.append('任务完成；当轮 Gate FAIL；后继 B3 8/8 export OK，非全产品质量 PASS')
    candidates = []
    for b in blocks:
        candidates += re.findall(r'\b[0-9a-f]{7,40}\b', b.get('integration_commit', ''))
    for line in text.splitlines():
        if re.search(r'integration[_ =]|集成.*(?:merge|commit|=)|merge=', line, re.I):
            candidates += re.findall(r'\b[0-9a-f]{7,40}\b', line)
    for line in plan.splitlines():
        if line.startswith('|') and (f'[{task}]' in line or re.search(r'\| ' + re.escape(task) + r' \|', line)):
            candidates += re.findall(r'\b[0-9a-f]{7,40}\b', line)
    checked = cached_tasks.get(task, {}).get('commit_checks', [])
    for sha in ([] if task in cached_tasks and checked else dict.fromkeys(candidates)):
        obj = git('rev-parse', '--verify', sha + '^{commit}')
        if obj['exit'] == 0:
            anc = git('merge-base', '--is-ancestor', obj['stdout'], head)
            checked.append({'sha': sha, 'commit': obj['stdout'], 'ancestor_exit': anc['exit']})
    integration = next((x['sha'] for x in checked if x['ancestor_exit'] == 0), 'NOT_VERIFIED')
    if integration == 'NOT_VERIFIED': notes.append('未从集成字段/记录定位有效主线祖先；不等同于未实现')
    refs = re.findall(r'(?:doc/)?(?:\.\./)?(?:reviews|handoffs|verification)/[^\s)<>`]+\.md', text)
    rows.append({'id': task, 'title': clean(d.get('title', task)), 'raw_status': state,
                 'state': effective, 'owner': owner, 'reviewer': clean(d.get('reviewer', 'NOT_ASSIGNED')),
                 'integrator': clean(d.get('integrator', 'NOT_ASSIGNED')), 'deps': d['deps'],
                 'base': clean(d.get('base_commit', 'UNKNOWN')), 'branch': clean(d.get('branch', 'UNKNOWN')),
                 'worktree': clean(d.get('worktree', 'UNKNOWN')), 'integration_candidate': integration,
                 'commit_checks': checked, 'file': path.relative_to(ROOT).as_posix(), 'notes': notes,
                 'evidence_refs': list(dict.fromkeys(refs))})

ids = {r['id'] for r in rows}
assert len(ids) == len(rows), 'duplicate task IDs'
# T1.1.2 is explicitly a roadmap task backed by historical TASK-013, without its own file.
rows.append({'id': 'T1.1.2', 'title': 'Region Canvas & Creator（Roadmap 映射）',
             'raw_status': 'NO_DEDICATED_TASK_FILE', 'state': 'LEGACY_VERIFIED_COMPLETE',
             'owner': 'Qoder', 'reviewer': 'Codex（非作者；Plan Roadmap 映射）', 'integrator': 'Codex',
             'deps': ['TASK-008', 'TASK-049'], 'base': 'UNKNOWN', 'branch': 'UNKNOWN', 'worktree': 'UNKNOWN',
             'integration_candidate': '5b91745', 'commit_checks': [], 'file': 'doc/REBASELINE_PLAN.md',
             'notes': ['Owner 取 TASK-013 Canvas 切片记录；无专用 Task 是已登记追溯缺口'], 'evidence_refs': []})
data = {'audit_head': head, 'branch': git('branch', '--show-current')['stdout'],
        'common_dir': git('rev-parse', '--path-format=absolute', '--git-common-dir')['stdout'],
        'working_tree_at_scan': git('status', '--short'), 'worktrees': worktrees, 'tasks': rows,
        'counts': dict(collections.Counter(r['state'] for r in rows)),
        'missing_dependency_ids': sorted({dep for r in rows for dep in r['deps']} - {r['id'] for r in rows})}
OUT.mkdir(exist_ok=True)
(OUT / 'inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
lines = ['# REBASELINE 全任务台账与流程图（2026-10-07）', '',
         f'审计基线：`main@{head}`；编排器 Codex；189 个 Task 文件 + T1.1.2 Roadmap 映射节点。', '',
         '本文件是派生证据；授权仍以 REBASELINE_PLAN 与 STATUS 为准。DONE_RECORDED 表示已登记完成，Git 核验只证明提交在主线历史中；本次未重新审核所有实现、复跑全部产品测试或创造新的独立批准。', '',
         '节点只显示 ID、Owner、有效状态；详细标题、原状态、Reviewer、依赖、基线和提交在下面的台账与 inventory.json。箭头仅来自 Task depends_on；分组不代表新增依赖。', '',
         '## 数量', '', '| 有效状态 | 数量 |', '|---|---:|']
lines += [f'| {state} | {count} |' for state, count in data['counts'].items()]
lines += ['', '当前正在执行/已释放：0（STATUS）；历史 ready/in_review 不列入当前执行队列。', '',
          '## 全任务依赖图', '', '每张图最多约 20 个任务；跨图依赖显示为外部输入节点。Legacy 图只作历史追溯，不可执行。']
groups = collections.defaultdict(list)
for r in rows:
    if r['id'].startswith('TASK-'): group = 'Legacy TASK ' + str((int(r['id'][-3:])-1)//15+1)
    elif r['id'].startswith('T'): group = 'Legacy Roadmap / Repair'
    elif r['id'].startswith('M2-SFX-'): group = 'M2 SFX 研究与数据'
    elif r['id'].startswith(('M2-TA', 'M2-DOCTR', 'M2-OCR', 'M2-KO', 'M2-QUAL')): group = 'M2 素材与质量验收'
    elif r['id'].startswith(('M2-PROD', 'M2-DETECT', 'M2-TASKS', 'M2-IMPORT', 'M2-SETTINGS', 'M2-REGION-RETYPE', 'M2-REGION-OVERLAP', 'M2-MANGA')): group = 'M2 Provider 与业务能力'
    elif r['id'].startswith(('DIAG', 'DOC-FIX', 'M2-FIX')): group = '诊断与修复'
    else: group = 'M2 架构与 UI'
    groups[group].append(r)
node = {r['id']: 'N'+str(i) for i,r in enumerate(rows)}
for group, members in groups.items():
    for part in range(0, len(members), 18):
        chunk = members[part:part+18]; own = {r['id'] for r in chunk}
        lines += ['', '### ' + group + (' · '+str(part//18+1) if len(members)>18 else ''), '', '```mermaid', 'flowchart TD']
        external = {dep for r in chunk for dep in r['deps'] if dep not in own}
        for i, dep in enumerate(sorted(external)):
            n = node.get(dep, 'X'+str(i))
            lines.append(f'  {n}["{dep} · 外部依赖"]')
        for r in chunk:
            owner = r['owner'].split('（')[0].split('(')[0].strip().replace('"','')
            state = r['state'].replace('LEGACY_', '历史 ').replace('DONE_RECORDED', '完成记录')
            lines.append(f'  {node[r["id"]]}["{r["id"]}<br/>{owner} · {state}"]')
            for dep in r['deps']:
                n = node.get(dep, 'X'+str(sorted(external).index(dep))) if dep not in own else node[dep]
                lines.append(f'  {n} --> {node[r["id"]]}')
        lines += ['```', '', '| Task / 标题 | 有效状态 / 原状态 | Owner / Reviewer | 依赖 / 主线祖先候选 | 备注 |', '|---|---|---|---|---|']
        for r in chunk:
            file = '../../' + r['file']
            lines.append(f'| [{r["id"]}]({file}) {r["title"]} | {r["state"]} / {r["raw_status"]} | {r["owner"]} / {r["reviewer"]} | {", ".join(r["deps"]) or "无"} / `{r["integration_candidate"]}` | {"；".join(r["notes"]) or "—"} |')
lines += ['', '## 边界与未知', '',
          '未找到专用 Task 文件的依赖 ID：' + (', '.join(data['missing_dependency_ids']) or '无') + '。不得推断其实现状态。', '',
          '完整 branch/worktree/base/提交核验与每个 linked worktree 的 dirty 列表见 inventory.json。所有工作区均只读核验，未 reset、clean、stash、prune 或覆盖改动。']
(OUT / 'TASK_GRAPH.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'head': head, 'task_nodes': len(rows), 'counts': data['counts'],
                  'worktrees': len(worktrees), 'dirty_worktrees': sum(bool(x['status']['stdout']) for x in worktrees),
                  'missing_dependency_ids': data['missing_dependency_ids'],
                  'unverified_integration': [r['id'] for r in rows if r['integration_candidate']=='NOT_VERIFIED']}, ensure_ascii=False))
