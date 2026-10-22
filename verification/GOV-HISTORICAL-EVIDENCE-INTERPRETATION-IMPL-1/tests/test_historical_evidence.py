"""T01-T18 use owned synthetic Git fixtures, never real resource operations."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'broad_fixture', ROOT/'verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/tests/test_broad_preservation.py')
broad_fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(broad_fixture)
guard = broad_fixture.guard
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def digest(policy):
    return sha(json.dumps(policy, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def snapshot(index):
    return dict(declarations=[{k: getattr(d, k) for k in d.__slots__}
                              for d in index.declarations],
                protected={root: [{k: getattr(d, k) for k in d.__slots__}
                                  for d in values]
                           for root, values in index.protected.items()},
                errors=copy.deepcopy(index.errors),
                warnings=copy.deepcopy(index.warnings),
                non_protective=list(index.non_protective),
                tops=copy.deepcopy(index._repo_tops))


class HistoricalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.broad = broad_fixture.BroadPreservationTests(methodName='runTest')
        self.broad.setUp()
        self.addCleanup(self.broad.doCleanups)
        self.broad.install()
        self.f = self.broad.f
        self.repo = Path(self.f.repo)
        self.policy = json.loads((ROOT/'verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1/binding-specimen.json').read_bytes())
        self.bindings = self.policy['template_bindings'] + self.policy['raw_non_declaration_bindings']
        template = self.bindings[0]
        raw = (ROOT/template['origin_file']).read_bytes().replace(
            b'G:/CODEX/New Manga', str(self.repo).replace('\\', '/').encode())
        self.f.write(template['origin_file'], raw.decode())
        old_path = template['parser_snapshot']['declarations'][0]['raw'].replace(
            'G:/CODEX/New Manga', str(self.repo).replace('\\', '/'))
        Path(old_path).mkdir(parents=True)
        for ref in self.policy['reference_guards']:
            (self.repo/ref['path_rel']).mkdir(parents=True, exist_ok=True)
            absolute = str(self.repo/ref['path_rel']).replace('\\', '/')
            ref.update(abs=absolute, normalized=guard.norm_abs(absolute),
                       real=guard.norm_abs(absolute))
        for b in self.bindings[1:3]:
            self.f.write(b['origin_file'], 'x'*286+'\x00'+' fixture raw\n')
        a = self.policy['approved_design']
        self.f.write(a['design_file'], 'fixture design\n')
        self.f.write(a['source_facts_file'], '{}\n')
        self.f.write('doc/tasks/seven-other-errors.md',
                     '## Resource Manifest\n\n|resource_type|source_path|disposition|destination_path|\n'
                     '|---|---|---|---|\n'+''.join(
                         '| fixture | ambiguous-%d | BAD | - |\n' % n for n in range(7)))
        a.update(source_facts_commit=self.f.commit('fixture historical sources'),
                 design_raw_sha256=sha((self.repo/a['design_file']).read_bytes()),
                 source_facts_raw_sha256=sha((self.repo/a['source_facts_file']).read_bytes()))
        self.f.write(self.bindings[3]['origin_file'], 'x'*12330+'\x00'+'x'*8155+'\x00\x0b\x0c\x08\n')
        # HIE is still absent here: ordinary reader/parser supplies the targets.
        self.base, self.scanned = guard.scan_repo_declarations(self.f.repo, self.f.ws)
        self.assertEqual(len(self.base.errors), 12)
        for b in self.bindings:
            path = self.repo/b['origin_file']
            raw = path.read_bytes()
            b.update(raw_sha256=sha(raw), byte_length=len(raw),
                     c0_bytes=[dict(offset=n, byte=c) for n, c in enumerate(raw)
                               if c<32 and c not in (9,10,13)])
            absolute = str(path).replace('\\', '/')
            b['source_guard'].update(abs=absolute, normalized=guard.norm_abs(absolute),
                                     real=guard.norm_abs(absolute))
            isolated = guard.ProtectionIndex(self.f.repo, self.f.ws)
            guard.parse_markdown_declarations(isolated, raw.decode(), b['origin_file'])
            b['parser_snapshot'] = {k: snapshot(isolated)[k]
                                    for k in ('declarations','errors','warnings')}
            b['errors'] = [copy.deepcopy(e) for e in self.base.errors
                           if e['file']==b['origin_file']]
            if b is template:
                lines = raw.splitlines(keepends=True)
                for prefix in ('open','close','draft_notice'):
                    line = lines[b['fence'][prefix+'_global_line']-1]
                    b['fence'][prefix+'_verbatim'] = line.decode()
                    b['fence'][prefix+'_raw_sha256'] = sha(line)
                for row in b['rows']:
                    line = lines[row['global_line']-1]
                    row.update(verbatim=line.decode(), raw_line_sha256=sha(line))
            else:
                b['nul_offsets'] = [n for n,c in enumerate(raw) if c==0]
        self.install()

    def install(self, policy=None, tracked=True):
        policy = policy or self.policy
        self.f.write(guard.HISTORICAL_EVIDENCE_POLICY,
                     json.dumps(policy, ensure_ascii=False))
        if tracked:
            self.f.git('add','--',guard.HISTORICAL_EVIDENCE_POLICY)

    def apply(self, policy=None, index=None, scanned=None):
        policy = policy or self.policy
        with mock.patch.object(guard, 'HISTORICAL_EVIDENCE_DIGEST', digest(policy)):
            return guard._apply_historical_evidence_interpretation(
                index or copy.deepcopy(self.base), dict(scanned or self.scanned))

    def rejected(self, policy=None, index=None, code=None):
        original = index or copy.deepcopy(self.base)
        before = snapshot(original)
        result, counts = self.apply(policy, original)
        self.assertIs(result, original)
        after = snapshot(result)
        for key in before:
            if key!='errors':
                self.assertEqual(after[key], before[key], key)
        self.assertEqual(result.errors[:-1], before['errors'])
        self.assertEqual(result.errors[-1]['file'], guard.HISTORICAL_EVIDENCE_POLICY)
        self.assertEqual(counts['errors'], len(before['errors'])+1)
        if code:
            self.assertEqual(result.errors[-1]['code'], code)
        return result

    def test_t01_positive_exact_atomic_effect(self):
        before = snapshot(self.base)
        index, counts = self.apply(index=self.base)
        self.assertIsNot(index,self.base)
        self.assertEqual(snapshot(self.base),before)
        targets = [e for b in self.bindings for e in b['errors']]
        self.assertEqual(index.errors,[e for e in self.base.errors if e not in targets])
        self.assertEqual(len(index.errors),7)
        self.assertEqual(len(index.declarations)-len(self.base.declarations),6)
        self.assertEqual(len(index.warnings)-len(self.base.warnings),4)
        self.assertTrue(set(self.base.protected)<=set(index.protected))
        for b in self.bindings:
            self.assertEqual(sha((self.repo/b['origin_file']).read_bytes()),b['raw_sha256'])
        self.assertEqual(counts['declarations'],len(index.declarations))
        self.assertEqual(counts['warnings'],len(index.warnings))

    def test_t02_direct_reader_and_unlisted_nul_still_reject(self):
        for b in self.bindings[1:]:
            with self.assertRaises(guard.GuardError):
                guard.read_text(str(self.repo/b['origin_file']),'raw')
        self.f.write('verification/unlisted.md','ordinary\x00text')
        with mock.patch.object(guard,'HISTORICAL_EVIDENCE_DIGEST',digest(self.policy)):
            i,_=guard.scan_repo_declarations(self.f.repo,self.f.ws)
        self.assertEqual(len(i.errors),8)
        self.assertTrue(any(e['file']=='verification/unlisted.md' for e in i.errors))

    def test_t03_policy_tracking_presence_git_and_read_failure(self):
        path=self.repo/guard.HISTORICAL_EVIDENCE_POLICY
        self.f.git('rm','--cached','--',guard.HISTORICAL_EVIDENCE_POLICY)
        self.rejected(code='POLICY_UNTRACKED')
        raw=path.read_bytes();path.unlink()
        i,c=self.apply(index=self.base)
        self.assertIs(i,self.base);self.assertEqual(c,self.scanned)
        path.write_bytes(raw);self.f.git('add','--',guard.HISTORICAL_EVIDENCE_POLICY);path.unlink()
        self.rejected(code='POLICY_MISSING');path.write_bytes(raw)
        with mock.patch.object(guard,'git_checked',side_effect=guard.GuardError('GIT_FAILED','fixture failure')):
            self.rejected(code='GIT_FAILED')
        with mock.patch.object(guard.io,'open',side_effect=OSError('fixture read failure')):
            self.rejected()

    def test_t04_schema_and_nested_mutations_unapproved(self):
        mutations=[lambda p:p.update(unknown=1),lambda p:p.pop('purpose'),
                   lambda p:p.update(schema_version=True),lambda p:p.update(schema_version=1.0),
                   lambda p:p['raw_non_declaration_bindings'].append(copy.deepcopy(self.bindings[1])),
                   lambda p:p['reference_guards'].append(copy.deepcopy(p['reference_guards'][0])),
                   lambda p:p['raw_non_declaration_bindings'][0].update(id='HIE-T01'),
                   lambda p:p['template_bindings'][0].update(byte_length=True),
                   lambda p:p['template_bindings'][0].update(extra='unknown')]
        for mutation in mutations:
            p=copy.deepcopy(self.policy);mutation(p);self.install(p)
            self.rejected()
        path=self.repo/guard.HISTORICAL_EVIDENCE_POLICY
        path.write_bytes(b'{"schema_version":1,"schema_version":1}')
        self.rejected(code='POLICY_INVALID')

    def test_t05_digest_provenance_and_format(self):
        self.install();path=self.repo/guard.HISTORICAL_EVIDENCE_POLICY
        path.write_bytes(json.dumps(self.policy,ensure_ascii=False,indent=4).replace('\n','\r\n').encode())
        self.assertEqual(len(self.apply()[0].errors),7)
        with mock.patch.object(guard,'HISTORICAL_EVIDENCE_DIGEST','0'*64):
            i,_=guard._apply_historical_evidence_interpretation(copy.deepcopy(self.base),self.scanned)
            self.assertEqual(i.errors[-1]['code'],'POLICY_DIGEST_MISMATCH')
        for field in ('design_file','source_facts_file'):
            path=self.repo/self.policy['approved_design'][field];raw=path.read_bytes()
            path.write_bytes(raw+b' ');self.rejected(code='SOURCE_DRIFT');path.write_bytes(raw)
        p=copy.deepcopy(self.policy);p['approved_design']['source_facts_commit']='0'*40
        self.install(p);self.rejected(p)

    def test_t06_all_four_source_byte_and_control_drift(self):
        for b in self.bindings:
            path=self.repo/b['origin_file'];raw=path.read_bytes()
            for changed in (raw+b' ',b'\xef\xbb\xbf'+raw,raw.replace(b'\x00',b'x'),raw+b'\xff'):
                if changed==raw:continue
                path.write_bytes(changed);self.rejected(code='SOURCE_DRIFT')
            path.write_bytes(raw)

    def test_t07_missing_directory_and_real_identity(self):
        path=self.repo/self.bindings[0]['origin_file'];raw=path.read_bytes()
        path.unlink();self.rejected(code='SOURCE_DRIFT')
        path.mkdir();self.rejected(code='SOURCE_DRIFT');path.rmdir();path.write_bytes(raw)
        original=guard.resolve_real_target
        for b in self.bindings:
            target=b['source_guard']['normalized']
            with mock.patch.object(guard,'resolve_real_target',side_effect=lambda n,w: n+'/alias' if n==target else original(n,w)):
                self.rejected(code='REAL_DRIFT')

    def test_t08_tracking_changes(self):
        b=self.bindings[3];self.f.git('add','--',b['origin_file'])
        self.rejected(code='SOURCE_DRIFT');self.f.git('rm','--cached','--',b['origin_file'])
        b=self.bindings[1];self.f.git('rm','--cached','--',b['origin_file'])
        self.rejected(code='SOURCE_DRIFT')

    def test_t09_template_boundary_and_row_checks(self):
        for mutate in (lambda b:b['fence'].update(open_global_line=118),
                       lambda b:b['fence'].update(close_verbatim='changed'),
                       lambda b:b['fence'].update(draft_notice_raw_sha256='0'*64),
                       lambda b:b['rows'][0].update(raw_line_sha256='0'*64)):
            p=copy.deepcopy(self.policy);mutate(p['template_bindings'][0]);self.install(p)
            self.rejected(p,code='RECORD_DRIFT')

    def test_t10_original_declaration_and_parse_preserved(self):
        frozen=self.bindings[0]['parser_snapshot']['declarations'][0]
        for missing in ('declaration','lexical','real'):
            i=copy.deepcopy(self.base)
            if missing=='declaration':i.declarations=[d for d in i.declarations if d.source_file!=frozen['source_file']]
            else:i.protected.pop(frozen['normalized' if missing=='lexical' else 'real_normalized'])
            self.rejected(index=i,code='RECORD_DRIFT')
        original=guard.parse_markdown_declarations
        def changed(i,t,o):
            original(i,t,o)
            if o==self.bindings[0]['origin_file']:i.add_warning('NEW','fixture',o)
        with mock.patch.object(guard,'parse_markdown_declarations',side_effect=changed):
            self.rejected(code='RECORD_DRIFT')

    def test_t11_references_missing_real_and_keep(self):
        for ref in self.policy['reference_guards']:
            path=self.repo/ref['path_rel'];path.rmdir();self.rejected(code='SOURCE_DRIFT');path.mkdir()
        for keep in ('DELETE_SAFE','PRESERVE_UNKNOWN'):
            p=copy.deepcopy(self.policy);p['reference_guards'][0]['keep']=keep
            self.install(p);self.rejected(p,code='POLICY_INVALID')

    def test_t12_nul_empty_parse_is_recomputed(self):
        original=guard.parse_markdown_declarations
        for kind in ('declaration','error','warning'):
            def changed(i,t,o):
                original(i,t,o)
                if o!=self.bindings[1]['origin_file']:return
                if kind=='error':i.add_error('NEW','fixture',o)
                elif kind=='warning':i.add_warning('NEW','fixture',o)
                else:i._register_protective(guard.Declaration('raw','PRESERVE_REFERENCED',o,'fixture',guard.norm_abs(str(self.repo/'README.md'))))
            with mock.patch.object(guard,'parse_markdown_declarations',side_effect=changed):
                self.rejected(code='RECORD_DRIFT')

    def test_t13_each_error_identity_unique(self):
        for b in self.bindings:
            for e in b['errors']:
                for mutation in ('missing','duplicate','message','file','locator'):
                    i=copy.deepcopy(self.base);n=i.errors.index(e)
                    if mutation=='missing':i.errors.pop(n)
                    elif mutation=='duplicate':i.errors.append(copy.deepcopy(e))
                    else:i.errors[n][mutation]='changed'
                    self.rejected(index=i,code='ERROR_MISMATCH')

    def test_t14_staging_failures_publish_nothing(self):
        original=guard.ProtectionIndex._register_protective
        for fail_at in (1,6):
            calls=[0]
            def register(i,d):
                # Isolated template parsing also registers; count only HIE guards.
                if '/raw-file' in d.locator or '/HIE-REF' in d.locator:
                    calls[0]+=1
                    if calls[0]==fail_at:raise RuntimeError('fixture staging failure')
                return original(i,d)
            with mock.patch.object(guard.ProtectionIndex,'_register_protective',register):
                self.rejected(code='POLICY_INVALID')
        original_warning=guard.ProtectionIndex.add_warning
        def warning(i,code,*args):
            if code=='DECL_HISTORICAL_EVIDENCE_PRESERVED':raise RuntimeError('fixture warning failure')
            return original_warning(i,code,*args)
        with mock.patch.object(guard.ProtectionIndex,'add_warning',warning):self.rejected()
        finish=guard._finish_declaration_scan
        calls=[0]
        def counts(i,s):
            calls[0]+=1
            if calls[0]==1:raise RuntimeError('fixture counts failure')
            return finish(i,s)
        with mock.patch.object(guard,'_finish_declaration_scan',side_effect=counts):self.rejected()

    def test_t15_final_inputs_tracking_and_seven_targets_rechecked(self):
        finish=guard._finish_declaration_scan
        paths=[guard.HISTORICAL_EVIDENCE_POLICY,guard.BROAD_PRESERVATION_POLICY,
               self.policy['approved_design']['design_file'],self.policy['approved_design']['source_facts_file']]+[b['origin_file'] for b in self.bindings]
        for relative in paths:
            path=self.repo/relative;raw=path.read_bytes()
            def mutate(i,s):
                path.write_bytes(raw+b' ');return finish(i,s)
            with mock.patch.object(guard,'_finish_declaration_scan',side_effect=mutate):self.rejected(code='SOURCE_DRIFT')
            path.write_bytes(raw)
        # Change each of the six new guards and original line227 only after counts.
        original=guard.resolve_real_target
        roots=[b['source_guard']['normalized'] for b in self.bindings]+[r['normalized'] for r in self.policy['reference_guards']]+[self.bindings[0]['parser_snapshot']['declarations'][0]['normalized']]
        for target in roots:
            staged=[False]
            def mark(i,s):staged[0]=True;return finish(i,s)
            with mock.patch.object(guard,'_finish_declaration_scan',side_effect=mark),mock.patch.object(guard,'resolve_real_target',side_effect=lambda n,w:n+'/drift' if staged[0] and n==target else original(n,w)):
                self.rejected(code='REAL_DRIFT')
        def track(i,s):self.f.git('add','--',self.bindings[3]['origin_file']);return finish(i,s)
        with mock.patch.object(guard,'_finish_declaration_scan',side_effect=track):self.rejected(code='SOURCE_DRIFT')

    def test_t16_three_actual_cli_share_rejection(self):
        launcher=("import sys;sys.path.insert(0,sys.argv.pop(1));import clean_workspace as g;"
                  "g.HISTORICAL_EVIDENCE_DIGEST=sys.argv.pop(1);"
                  "m=__import__(sys.argv.pop(1));raise SystemExit(m.main(sys.argv[1:]))")
        inventory=Path(self.f.out)/'empty.json';inventory.write_text('{"worktrees":[],"protected_worktree_names":{}}')
        for module in ('clean_workspace','remove_worktrees','consolidate'):
            args=[sys.executable,'-B','-c',launcher,str(ROOT/'tools/governance'),digest(self.policy),module,
                  '--repo',self.f.repo,'--workspace-root',self.f.ws,'--out',str(Path(self.f.out)/module)]
            if module=='remove_worktrees':args+=['--inventory',str(inventory)]
            if module=='consolidate':args+=['--mainline','main']
            result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(result.returncode,0,(module,result.stdout,result.stderr))
            filename={'clean_workspace':'clean-workspace-refused.json','remove_worktrees':'worktree-removal-refused.json','consolidate':'inventory.json'}[module]
            report=json.loads((Path(self.f.out)/module/filename).read_bytes())
            expected=[e for e in self.base.errors if e not in [e for b in self.bindings for e in b['errors']]]
            self.assertEqual(report['declaration_errors'],expected)
            self.assertEqual(len(report['declaration_errors']),7)
            for b in self.bindings:self.assertTrue((self.repo/b['origin_file']).is_file())

    def test_t17_scanned_metadata_and_original_containers(self):
        self.scanned['protected_roots']=len(self.base.protected)
        s=copy.deepcopy(self.scanned)
        before=snapshot(self.base)
        result,counts=self.apply(index=self.base,scanned=self.scanned)
        self.assertEqual(self.scanned,s);self.assertEqual(snapshot(self.base),before)
        self.assertEqual(counts['protected_roots'],len(result.protected))
        for root in self.base.protected:self.assertIsNot(result.protected[root],self.base.protected[root])
        for d in self.base.declarations:self.assertIn(d,result.declarations)

    def test_t18_broad_fatal_noop_and_exact_roles(self):
        i=copy.deepcopy(self.base);i.add_error('POLICY_INVALID','fixture',guard.BROAD_PRESERVATION_POLICY)
        before=snapshot(i);r,_=self.apply(index=i);self.assertIs(r,i);self.assertEqual(snapshot(r),before)
        for mutation in ('missing_warning','duplicate_warning','spoof','declaration','root'):
            i=copy.deepcopy(self.base)
            wi=next(n for n,w in enumerate(i.warnings) if w['code']=='DECL_BROAD_ROOT_PRESERVED')
            di=next(n for n,d in enumerate(i.declarations) if d.normalized==guard.norm_abs(self.f.ws))
            if mutation=='missing_warning':i.warnings.pop(wi)
            elif mutation=='duplicate_warning':i.warnings.append(copy.deepcopy(i.warnings[wi]))
            elif mutation=='spoof':i.warnings[wi]['message']+=' changed'
            elif mutation=='declaration':i.declarations.pop(di)
            else:i.protected.pop(guard.norm_abs(self.f.ws))
            self.rejected(index=i,code='DEPENDENCY_INACTIVE')
        # 83 unrelated declarations from the same broad sources do not affect 12 roles.
        i=copy.deepcopy(self.base)
        for n in range(83):
            i._register_protective(guard.Declaration('fixture-%d'%n,'PRESERVE_REFERENCED',broad_fixture.FIRST,'extra%d'%n,guard.norm_abs(str(self.repo/('extra%d'%n)))))
        self.assertEqual(len(self.apply(index=i)[0].errors),7)
        path=self.repo/guard.BROAD_PRESERVATION_POLICY
        self.f.git('rm','--cached','--',guard.BROAD_PRESERVATION_POLICY);path.unlink()
        self.rejected(code='DEPENDENCY_INACTIVE')
        with mock.patch.object(guard,'HISTORICAL_EVIDENCE_DIGEST',digest(self.policy)):
            inactive,_=guard.scan_repo_declarations(self.f.repo,self.f.ws)
        self.assertEqual(len(inactive.errors),25)
        self.assertEqual(inactive.errors[-1]['code'],'DEPENDENCY_INACTIVE')
        self.f.git('rm','--cached','--',guard.HISTORICAL_EVIDENCE_POLICY)
        (self.repo/guard.HISTORICAL_EVIDENCE_POLICY).unlink()
        i,c=self.apply(index=self.base);self.assertIs(i,self.base);self.assertEqual(c,self.scanned)


if __name__=='__main__':
    unittest.main()
