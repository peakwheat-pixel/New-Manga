"""Read-only source identity checks; stdout JSON only; no fixtures or mutations."""
import collections,hashlib,importlib.util,json,pathlib,re,subprocess,sys
R=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'G:/CODEX/New Manga')
S=R/'tools/governance/clean_workspace.py'
spec=importlib.util.spec_from_file_location('identity_guard',S);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sha=lambda b:hashlib.sha256(b).hexdigest()
idx,scan=g.scan_repo_declarations(str(R),str(R.parent/'New Manga.workspace'))
assert len(idx.errors)==12
matrix=json.loads((R/'verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.json').read_text(encoding='utf-8'))['errors']
chosen=[e for e in matrix if e['id'] in ('R25','R26','R27','R28','R32')]
assert len(chosen)==5
key=lambda x:json.dumps({k:x[k] for k in ('code','message','file','locator')},sort_keys=True)
assert not (collections.Counter(map(key,chosen))-collections.Counter(map(key,idx.errors)))
rows=[]
for rel in sorted({e['file'] for e in chosen}):
 raw=(R/rel).read_bytes();text=raw.decode('utf-8',errors='strict');digest=sha(raw)
 assert all(x['source_sha256']==digest for x in chosen if x['file']==rel)
 tracked=bool(subprocess.check_output(['git','ls-files','--',rel],cwd=R))
 blob=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R) if tracked else None
 probe=g.ProtectionIndex(str(R),str(R.parent/'New Manga.workspace'));g.parse_markdown_declarations(probe,text,rel)
 controls=[dict(offset=n,byte=b,line=raw[:n].count(b'\n')+1,context_hex=raw[max(0,n-28):n+45].hex(),context_text=raw[max(0,n-28):n+45].decode('utf-8',errors='replace')) for n,b in enumerate(raw) if b<32 and b not in (9,10,13)]
 assert len([c for c in controls if c['byte']==0])==({'R25':0,'R27':1,'R28':1,'R32':2}[next(e['id'] for e in chosen if e['file']==rel)])
 isolated=[]
 for d in probe.declarations:isolated.append(dict(raw=d.raw,keep=d.disposition,locator=d.locator,normalized=d.normalized))
 rows.append(dict(path=rel,size=len(raw),raw_sha256=digest,tracked=tracked,head_blob_sha256=sha(blob) if blob is not None else None,disk_equals_head_blob=raw==blob if blob is not None else None,lf_normalized_equals_head_blob=raw.replace(b'\r\n',b'\n')==blob if blob is not None else None,strict_utf8=True,utf8_bom=raw.startswith(b'\xef\xbb\xbf'),nul_offsets=[c['offset'] for c in controls if c['byte']==0],non_whitespace_C0=controls,last_git_change=subprocess.check_output(['git','log','-1','--format=%H %an %s','--',rel],cwd=R,text=True).strip(),actual_writer='UNKNOWN; Git committer and embedded Owner do not establish file writer',protected_now=g.norm_abs(str(R/rel)) in idx.protected,memory_only_parser_declarations=isolated,memory_only_parser_errors=probe.errors,memory_only_parser_warning_count=len(probe.warnings),memory_parse_is_not_runtime_acceptance=True))
refs=[]
for rel in ['doc/tasks/P14.md','doc/tasks/P22.md']:
 raw=(R/rel).read_bytes();text=raw.decode('utf-8');matches=[]
 for n,l in enumerate(text.split('\n'),1):
  if any(pathlib.PurePosixPath(x['path']).name in l for x in rows):matches.append(dict(line=n,text=l))
 refs.append(dict(path=rel,raw_sha256=sha(raw),matching_lines=matches))
review=(R/chosen[0]['file']).read_bytes();ls=review.decode('utf-8').split('\n');fences=[n for n,l in enumerate(ls,1) if l.startswith('````')];assert 117 in fences
for n in (228,229):assert n>117 and n<next(x for x in fences if x>117)
proof=dict(task='GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1',canonical_repo=str(R),measurement_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),matrix_path='verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.json',five_errors=chosen,source_count=len(rows),source_facts=rows,bounded_references=refs,template_context=dict(fence_open=117,fence_close=next(x for x in fences if x>117),draft_notice_global_line=115,manifest_heading_global_line=221,row_global_lines=[228,229],row_raw_sha256=[sha(review.splitlines(keepends=True)[n-1]) for n in (228,229)],rows=[ls[n-1].rstrip('\r') for n in (228,229)]),scan_counts=idx.counts(),scan_statistics=scan,remaining_seven=[e for e in idx.errors if key(e) not in {key(x) for x in chosen}],assertions='5 exact prior identities;4 raw hashes unchanged;strict UTF8;NUL counts0/1/1/2;fenced draft positions;12 formal errors')
assert len(proof['remaining_seven'])==7 and len(rows)==4
print(json.dumps(proof,ensure_ascii=False,indent=2))
