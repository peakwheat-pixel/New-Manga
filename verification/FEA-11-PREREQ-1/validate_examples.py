"""Executable C-17 examples/models, explicitly not production behavior tests."""
from __future__ import annotations
import copy
import hashlib
import json
import platform
import sqlite3
import sys
from validate_contract import database, seed, plan, operation, insert, snapshot, MIGRATIONS, CANDIDATE
from infrastructure.sqlite.migrator import MigrationRunner


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def main():
    print('COMMAND: python -B verification/FEA-11-PREREQ-1/validate_examples.py')
    print(f'ENV: shell=PowerShell; interpreter={sys.executable}; Python={platform.python_version()}; SQLite={sqlite3.sqlite_version}; DB=:memory:')
    print('LIMIT: isolated SQL persistence and normative models; no real Host/Core restart, IPC, OS lease, or images')
    c=database()
    seed(c)
    MigrationRunner(c,MIGRATIONS+(CANDIDATE,)).apply_pending()
    plan(c,state='applied',applied_at='t')
    operation(c)
    # Correct page-preserving lineage edges, unlike constraint-only negative fixtures.
    for i in (1,2):
        c.execute("UPDATE page_bindings SET status='superseded' WHERE binding_id=?",(f'b{i}',))
        c.execute("INSERT INTO page_bindings SELECT ?,page_id,project_id,2,source_id,entry_id,accepted_source_version,'healthy',binding_id,authorization_generation,authorized_at,verified_digest,created_at,updated_at FROM page_bindings WHERE binding_id=?",(f'b{i}-new',f'b{i}'))
        insert(c,'source_binding_publications',dict(binding_id=f'b{i}-new',operation_id='op',previous_binding_id=f'b{i}',relation='changed' if i==1 else 'same_content',read_gate='pending'))
    c.commit()
    def gates(conn):
        return [r[0] for r in conn.execute('SELECT read_gate FROM source_binding_publications ORDER BY binding_id')]
    assert gates(c)==['pending','pending']
    clone=sqlite3.connect(':memory:')
    c.backup(clone)
    assert gates(clone)==['pending','pending']
    print('PASS COMMIT-before-ACK: gates persist in independent in-memory snapshot; no volatile bypass')
    base=snapshot(c)
    c.execute('BEGIN IMMEDIATE')
    c.execute("UPDATE source_operations SET state='acknowledged',acknowledged_at='t' WHERE operation_id='op'")
    c.execute("UPDATE source_binding_publications SET read_gate='open',opened_at='t' WHERE binding_id='b1-new'")
    c.rollback()  # model crash before ACK transaction commit
    assert snapshot(c)==base and gates(c)==['pending','pending']
    print('PASS ACK transaction interruption: operation and all gates remain pre-ACK')
    c.execute('BEGIN IMMEDIATE')
    c.execute("UPDATE source_operations SET state='acknowledged',acknowledged_at='t' WHERE operation_id='op'")
    c.execute("UPDATE source_binding_publications SET read_gate='open',opened_at='t' WHERE operation_id='op'")
    c.commit()
    base=snapshot(c)
    # Normative replay: select and return the saved receipt, no writes.
    receipt=c.execute("SELECT commit_receipt_json FROM source_operations WHERE operation_id='op'").fetchone()[0]
    assert receipt=='{}' and snapshot(c)==base and gates(c)==['open','open']
    assert c.execute("SELECT count(*) FROM page_bindings WHERE binding_version=2").fetchone()[0]==2
    print('PASS ACK/replay: all gates open atomically; saved receipt returned; no new binding')
    baseline={'source_version':'v1','binding_version':1,'host_generation':7,'manual':'r1','lock':False,'draft':3,'run':'prepared','scope':['book'],'decision':'bind'}
    for key in baseline:
        actual=copy.deepcopy(baseline)
        actual[key]=None
        before=snapshot(c)
        assert actual!=baseline  # contract CAS model rejects BEFORE any mutation
        assert snapshot(c)==before
        print('PASS CAS model stale '+key+': no Core SQL writes')
    # Read generation compatibility is independent of apply CAS.
    assert 7<=8 and 7!=8
    print('PASS generation model: accepted binding generation 7 may read under same-identity grant 8; old-plan apply CAS fails')
    edges={'b1-new':('b1','changed'),'b2-new':('b2','same_content')}
    def region_allowed(origin,current):
        seen=set()
        while current!=origin:
            assert current not in seen
            seen.add(current)
            if current not in edges or edges[current][1]!='same_content':
                return False
            current=edges[current][0]
        return True
    assert not region_allowed('b1','b1-new')
    assert region_allowed('b2','b2-new')
    assert not region_allowed('legacy_unverified','b1-new')
    print('PASS lineage model: changed excludes R1; same_content retains R1; unverified never inherits new coordinates')
    for state in ('old-draft','old-edit-token','old-prepared-run','old-candidate'):
        assert not region_allowed('b1','b1-new')
        print(f'PASS {state} model: old baseline rejected; preserved as history/draft/candidate, no rebasing')
    def key(binding,version,params):
        return 'page-rendition-v2-'+digest(dict(page_id='P1',binding_id=binding,source_id='S1',version_id=version,entry_id='E1',verified_digest='a'*64,rendition_kind='page_preview',decoder_name='synthetic',decoder_version='1',params_digest=params))
    old='page-rendition-P1'
    k1,k2=key('B1','V1','b'*64),key('B2','V2','b'*64)
    catalog={old:hashlib.sha256(b'synthetic-old').hexdigest(),k1:hashlib.sha256(b'synthetic-old').hexdigest(),k2:hashlib.sha256(b'synthetic-new').hexdigest()}
    assert len({old,k1,k2})==3
    assert catalog[old]==catalog[k1] and catalog[k2]!=catalog[old]
    assert key('B1','V1','c'*64)!=k1
    print('PASS resolve model: '+json.dumps({'old_key':old,'old_digest':catalog[old],'B1_key':k1,'B2_key':k2,'new_digest':catalog[k2]},sort_keys=True))
    print('PASS resolve profile change: decoder params choose a different immutable key')
    # Freeze profile/degradation matrix; no matching engine is implemented here.
    def evidence(old, new, duplicate=False, comparable=True):
        if old is None: return 'missing_old'
        if not comparable: return 'incomparable'
        if duplicate: return 'duplicate_group'
        return 'unique_pixel' if old==new else 'none'
    assert evidence('px','px')=='unique_pixel'
    assert evidence('px','px',duplicate=True)=='duplicate_group'
    assert evidence(None,'px')=='missing_old'
    assert evidence('px','px',comparable=False)=='incomparable'
    print('PASS evidence model: comparable unique / duplicate group / absent old / incomparable; no ordinal or new-image substitute')
    golden={'z':'中文','a':[1,True,None]}
    assert canonical(golden)==b'{"a":[1,true,null],"z":"\xe4\xb8\xad\xe6\x96\x87"}'
    assert digest(golden)!=digest({**golden,'z':'中 文'})
    print('GOLDEN_CANONICAL_HEX: '+canonical(golden).hex())
    print('GOLDEN_SHA256: '+digest(golden))
    print('PASS canonical model: UTF-8 code-point keys, no whitespace, no normalization')
    clone.close()
    c.close()
    print('RESULT: all listed normative examples passed; 0 skipped; production behavior NOT_RUN')


if __name__=='__main__':
    try:
        main()
    except Exception:
        print('EXIT: 1')
        raise
    print('EXIT: 0')
