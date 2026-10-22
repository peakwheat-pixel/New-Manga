"""Design-data assertions only; never calls a proposed helper or writes files."""
import collections,hashlib,importlib.util,json,pathlib,subprocess,sys
R=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'G:/CODEX/New Manga')
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('design_current_guard',R/'tools/governance/clean_workspace.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sha=lambda b:hashlib.sha256(b).hexdigest()
def exact(obj,keys):assert type(obj) is dict and set(obj)==set(keys.split()),(set(obj),keys)
def snapshot(idx):return dict(declarations=[{k:getattr(d,k) for k in d.__slots__} for d in idx.declarations],errors=idx.errors,warnings=idx.warnings)
p=json.loads((HERE/'binding-specimen.json').read_text(encoding='utf-8'),object_pairs_hook=g._unique_preservation_object)
exact(p,'schema_version purpose approved_design template_bindings raw_non_declaration_bindings reference_guards');assert type(p['schema_version']) is int and p['schema_version']==1 and p['purpose']=='PRESERVE_EXACT_HISTORICAL_EVIDENCE'
a=p['approved_design'];exact(a,'task_id design_file design_raw_sha256 source_facts_file source_facts_commit source_facts_raw_sha256');assert a['task_id']=='GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1';assert a['design_file']=='verification/'+a['task_id']+'/design.md' and sha((HERE/'design.md').read_bytes())==a['design_raw_sha256']
assert a['source_facts_file']=='verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json' and a['source_facts_commit']=='8a429a889768c18c6b0add5fc7e5c40b83f62746'
factsraw=(R/a['source_facts_file']).read_bytes();assert sha(factsraw)==a['source_facts_raw_sha256'] and factsraw==subprocess.check_output(['git','show',a['source_facts_commit']+':'+a['source_facts_file']],cwd=R);facts=json.loads(factsraw)
idx,scan=g.scan_repo_declarations(str(R),str(R.parent/'New Manga.workspace'));assert len(idx.errors)==12
assert len(p['template_bindings'])==1 and len(p['raw_non_declaration_bindings'])==3 and len(p['reference_guards'])==2
bindings=p['template_bindings']+p['raw_non_declaration_bindings'];assert [b['id'] for b in bindings]==['HIE-T01','HIE-O01','HIE-O02','HIE-O03'];assert {b['origin_file'] for b in bindings}=={f['path'] for f in facts['source_facts']}
expected_origins=dict(zip(['HIE-T01','HIE-O01','HIE-O02','HIE-O03'],['verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md','verification/P14/owner-initiated-dsh-self-review-r1.md','verification/P14/owner-initiated-dsh-self-review-r2.md','verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md']))
errors=[];guards=[]
for b in bindings:
 fields='id origin_file expected_tracking raw_sha256 byte_length strict_utf8 utf8_bom c0_bytes source_guard parser_snapshot errors';exact(b,fields+(' fence rows' if b['id']=='HIE-T01' else ' nul_offsets'))
 rel=b['origin_file'];assert rel==expected_origins[b['id']];raw=(R/rel).read_bytes();text=raw.decode('utf-8',errors='strict');assert sha(raw)==b['raw_sha256'] and type(b['byte_length']) is int and len(raw)==b['byte_length'];assert b['strict_utf8'] is True and type(b['utf8_bom']) is bool and b['utf8_bom']==raw.startswith(b'\xef\xbb\xbf')
 tracking='tracked' if subprocess.check_output(['git','ls-files','--',rel],cwd=R) else 'untracked';assert tracking==b['expected_tracking']
 controls=[dict(offset=n,byte=c) for n,c in enumerate(raw) if c<32 and c not in (9,10,13)];assert b['c0_bytes']==controls
 for c in b['c0_bytes']:exact(c,'offset byte');assert type(c['offset']) is int and type(c['byte']) is int
 guard=b['source_guard'];exact(guard,'abs normalized real keep');normalized=g.norm_abs(str(R/rel));assert guard['abs']==str(R/rel).replace('\\','/') and guard['normalized']==guard['real']==normalized==g.resolve_real_target(normalized,'design source') and normalized in idx.protected
 assert guard['keep']==('PRESERVE_UNKNOWN' if b['id']=='HIE-O03' else 'PRESERVE_REFERENCED');assert (R/rel).is_file();guards.append(normalized)
 isolated=g.ProtectionIndex(str(R),str(R.parent/'New Manga.workspace'));g.parse_markdown_declarations(isolated,text,rel);assert snapshot(isolated)==b['parser_snapshot'];exact(b['parser_snapshot'],'declarations errors warnings')
 for e in b['errors']:exact(e,'code message file locator');assert idx.errors.count(e)==1;errors.append(e)
 if b['id']=='HIE-T01':
  assert len(b['errors'])==2 and len(isolated.declarations)==1 and len(isolated.errors)==2 and len(isolated.warnings)==2
  f=b['fence'];exact(f,'open_global_line close_global_line open_verbatim close_verbatim open_raw_sha256 close_raw_sha256 draft_notice_global_line draft_notice_verbatim draft_notice_raw_sha256');assert (f['open_global_line'],f['close_global_line'],f['draft_notice_global_line'])==(117,239,115)
  lines=raw.splitlines(keepends=True)
  for prefix,n in [('open',117),('close',239),('draft_notice',115)]:assert f[prefix+'_verbatim']==lines[n-1].decode('utf-8') and f[prefix+'_raw_sha256']==sha(lines[n-1])
  assert len(b['rows'])==2
  for row,n,eid,loc in zip(b['rows'],(228,229),('R25','R26'),('line 7','line 8')):
   exact(row,'id global_line parser_locator verbatim raw_line_sha256');assert row['global_line']==n and row['id']==eid and row['parser_locator']==loc and row['verbatim']==lines[n-1].decode('utf-8') and row['raw_line_sha256']==sha(lines[n-1])
  for d in isolated.declarations:assert d.normalized in idx.protected;assert any(x.raw==d.raw and x.disposition==d.disposition and x.source_file==d.source_file and x.locator==d.locator and x.normalized==d.normalized and x.real_normalized==d.real_normalized for x in idx.protected[d.normalized])
 else:
  assert len(b['errors'])==1 and b['errors'][0]['code']=='FILE_UNREADABLE' and b['errors'][0]['locator'] is None and snapshot(isolated)==dict(declarations=[],errors=[],warnings=[])
  assert b['nul_offsets']==[x['offset'] for x in controls if x['byte']==0] and b['nul_offsets']==([12330,20486] if b['id']=='HIE-O03' else [286])
for ref,n,rel in zip(p['reference_guards'],(1,2),('tools/governance/tests','verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1')):
 exact(ref,'id origin_file origin_global_line origin_parser_locator path_rel abs normalized real keep');assert ref['id']=='HIE-REF%02d'%n and ref['origin_file']==p['template_bindings'][0]['origin_file'] and ref['origin_global_line']==229 and ref['origin_parser_locator']=='line 8' and ref['path_rel']==rel
 normalized=g.norm_abs(str(R/rel));assert ref['abs']==str(R/rel).replace('\\','/') and ref['normalized']==ref['real']==normalized==g.resolve_real_target(normalized,'design reference') and ref['keep']=='PRESERVE_REFERENCED' and (R/rel).is_dir() and normalized in idx.protected;guards.append(normalized)
key=lambda e:json.dumps({k:e[k] for k in ('code','message','file','locator')},sort_keys=True)
assert len(errors)==5 and collections.Counter(map(key,errors))==collections.Counter(map(key,facts['five_errors']))
canonical=json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
print(json.dumps(dict(status='DESIGN_DATA_ASSERTIONS_PASSED',canonical_policy_sha256=sha(canonical),binding_ids=[b['id'] for b in bindings],guards=guards,all_six_guard_roots_currently_protected=True,formal_errors=len(idx.errors),five_exact_identities_verified=True,four_original_raw_hashes_verified=True,template_original_declaration_preserved=True,production_helper='NOT_IMPLEMENTED_NOT_RUN',runtime_matrix_T01_T18='PLANNED_NOT_RUN',counts=idx.counts(),scan=scan),ensure_ascii=False,indent=2))
