"""C-17 contract-only SQLite probe. Never opens an application database."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from infrastructure.sqlite.schema import Migration, default_migrations
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.connection import SchemaTooNewError

DOC = ROOT / 'doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md'
SQL = DOC.read_text(encoding='utf-8').split('```sql\n', 1)[1].split('```', 1)[0]
MIGRATIONS = default_migrations()
CANDIDATE = Migration(8, 'v8__source_sync', SQL)
COUNT = 0


def ok(label):
    global COUNT
    COUNT += 1
    print(f'PASS {label}')


def database():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    return conn


def snapshot(conn):
    return tuple(conn.iterdump())


def seed(conn):
    conn.execute("INSERT INTO books(book_id,title,created_at,updated_at) VALUES('book','synthetic','t','t')")
    conn.execute("INSERT INTO chapters(chapter_id,book_id,title,created_at,updated_at) VALUES('chapter','book','c','t','t')")
    for p in ('p1', 'p2', 'p3'):
        conn.execute("INSERT INTO pages(page_id,chapter_id,sort_order,created_at,updated_at) VALUES(?, 'chapter',0,'t','t')", (p,))
    conn.execute("INSERT INTO sources(source_id,source_kind,created_at,updated_at) VALUES('s','image','t','t')")
    conn.execute("INSERT INTO source_locations(location_id,source_id,registry_id,authorization_generation,content_digest,volume_serial,file_id,size_bytes,observed_at,created_at) VALUES('loc','s','reg',1,?,1,2,3,'t','t')", ('a'*64,))
    conn.execute("INSERT INTO source_versions(version_id,source_id,location_id,content_digest,size_bytes,observed_at,created_at) VALUES('v','s','loc',?,3,'t','t')", ('a'*64,))
    for i in range(1, 4):
        conn.execute("INSERT INTO source_entries(source_id,version_id,entry_id,locator,ordinal,stable_sort_key,content_digest_kind,content_digest,size_bytes,created_at) VALUES('s','v',?,?,?,?,'encoded',?,3,'t')", (f'e{i}', f'{i}.png', i, str(i), 'a'*64))
        conn.execute("INSERT INTO page_bindings(binding_id,page_id,project_id,binding_version,source_id,entry_id,accepted_source_version,status,authorization_generation,authorized_at,verified_digest,created_at,updated_at) VALUES(?,?,'book',1,'s',?,'v','healthy',1,'t',?,'t','t')", (f'b{i}', f'p{i}', f'e{i}', 'a'*64))
    conn.commit()


def plan(conn, **changes):
    row = dict(plan_id='plan', source_id='s', kind='resync', state='confirmed', plan_digest='b'*64,
               body_json='{}', created_at='t', expires_at='u', previewed_at='t', confirmed_at='t')
    row.update(changes)
    insert(conn, 'source_sync_plans', row)


def operation(conn, **changes):
    row = dict(operation_id='op', plan_id='plan', plan_digest='b'*64, kind='resync',
               request_digest='c'*64, state='core-committed', authorization_digest='d'*64,
               authorization_json='{}', host_receipt_id='host', commit_receipt_json='{}',
               commit_digest='e'*64, created_at='t', updated_at='t', committed_at='t')
    row.update(changes)
    insert(conn, 'source_operations', row)


def insert(conn, table, values):
    # Identifiers below are fixed probe-owned dictionary keys, never external input.
    conn.execute(f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", tuple(values.values()))


def negative(conn, label, call):
    before = snapshot(conn)
    conn.execute('SAVEPOINT negative')
    try:
        call()
    except sqlite3.IntegrityError as error:
        print(f'EXPECTED {label}: {error}')
        conn.execute('ROLLBACK TO negative')
        conn.execute('RELEASE negative')
        assert snapshot(conn) == before, label
        ok(label)
    else:
        raise AssertionError(f'negative accepted: {label}')


def run():
    print(f'COMMAND: python -B verification/FEA-11-PREREQ-1/validate_contract.py')
    print(f'ENV: shell=PowerShell; interpreter={sys.executable}; Python={platform.python_version()}; SQLite={sqlite3.sqlite_version}; DB=:memory:; no TEMP/AppData/real DB')
    print('BASELINE: ' + str(ROOT))
    print('CANDIDATE_SQL_SHA256: ' + hashlib.sha256(SQL.encode()).hexdigest())
    print('V1_V7_CHECKSUMS: ' + json.dumps({str(m.schema_version): m.checksum for m in MIGRATIONS}, sort_keys=True))
    assert [m.schema_version for m in MIGRATIONS] == list(range(1, 8))
    c = database()
    seed(c)
    old_data = {t: tuple(map(tuple, c.execute(f'SELECT * FROM {t}'))) for t in ('pages','page_bindings','source_versions','source_entries')}
    MigrationRunner(c, MIGRATIONS + (CANDIDATE,)).apply_pending()
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    for t, rows in old_data.items():
        assert tuple(map(tuple, c.execute(f'SELECT * FROM {t}'))) == rows
    ok('candidate migration / FK check / old source-page-binding data conserved')
    plan(c)
    operation(c)
    c.commit()
    negative(c, 'plan source FK', lambda: plan(c, plan_id='other', source_id='absent'))
    negative(c, 'plan state CHECK', lambda: plan(c, plan_id='other', state='invalid'))
    negative(c, 'plan digest CHECK', lambda: plan(c, plan_id='other', plan_digest='Z'*64))
    negative(c, 'plan confirmation timestamp CHECK', lambda: plan(c, plan_id='other', confirmed_at=None))
    negative(c, 'plan applied timestamp CHECK', lambda: plan(c, plan_id='other', state='applied'))
    negative(c, 'plan stale reason CHECK', lambda: plan(c, plan_id='other', state='stale'))
    negative(c, 'operation plan UNIQUE', lambda: operation(c, operation_id='op2'))
    negative(c, 'operation composite plan FK', lambda: operation(c, operation_id='op2', plan_id='absent'))
    plan(c, plan_id='other')
    c.commit()
    negative(c, 'operation plan digest FK', lambda: operation(c, operation_id='op2', plan_id='other', plan_digest='f'*64))
    negative(c, 'operation plan kind FK', lambda: operation(c, operation_id='op2', plan_id='other', kind='relink'))
    negative(c, 'operation state CHECK', lambda: operation(c, operation_id='op2', plan_id='other', state='done'))
    negative(c, 'operation ACK timestamp CHECK', lambda: operation(c, operation_id='op2', plan_id='other', state='acknowledged'))
    negative(c, 'operation commit receipt CHECK', lambda: operation(c, operation_id='op2', plan_id='other', commit_receipt_json=None))
    negative(c, 'operation failure code CHECK', lambda: operation(c, operation_id='op2', plan_id='other', state='failed'))
    pub = dict(binding_id='b1', operation_id='op', previous_binding_id='b2', relation='changed', read_gate='pending')
    insert(c, 'source_binding_publications', pub)
    c.commit()
    negative(c, 'publication binding UNIQUE', lambda: insert(c, 'source_binding_publications', pub))
    negative(c, 'publication binding FK', lambda: insert(c, 'source_binding_publications', {**pub, 'binding_id':'absent'}))
    negative(c, 'publication operation FK', lambda: insert(c, 'source_binding_publications', {**pub, 'binding_id':'b3','operation_id':'absent'}))
    negative(c, 'publication pending-open timestamp CHECK', lambda: c.execute("UPDATE source_binding_publications SET read_gate='open'"))
    negative(c, 'publication relation CHECK', lambda: c.execute("UPDATE source_binding_publications SET relation='added'"))
    # SQL intentionally does not enforce page ownership or allowed transition events.
    # Positive pub above is a constraint fixture only, NOT a valid semantic mapping.
    c.execute("INSERT INTO regions(region_id,page_id,region_type,geometry_json,text_json,style_json,created_at,updated_at) VALUES('r','p1','speech','{}','{}','{}','t','t')")
    c.execute("INSERT INTO region_revisions(region_revision_id,region_id,revision_no,snapshot_json,origin,review_state,created_at) VALUES('rev','r',1,'{}','user','confirmed','t')")
    c.execute("UPDATE regions SET current_revision_id='rev' WHERE region_id='r'")
    lineage = dict(revision_id='rev', region_id='r', binding_id='b1', provenance='native', created_at='t')
    insert(c, 'source_revision_lineage', lineage)
    c.commit()
    negative(c, 'lineage revision UNIQUE', lambda: insert(c,'source_revision_lineage',lineage))
    negative(c, 'lineage binding FK', lambda: c.execute("UPDATE source_revision_lineage SET binding_id='absent'"))
    negative(c, 'lineage unknown-with-binding CHECK', lambda: c.execute("UPDATE source_revision_lineage SET provenance='legacy_unverified'"))
    negative(c, 'lineage migrated-source CHECK', lambda: c.execute("UPDATE source_revision_lineage SET provenance='migrated'"))
    negative(c, 'lineage source FK', lambda: c.execute("UPDATE source_revision_lineage SET provenance='migrated',from_revision_id='absent'"))
    negative(c, 'lineage self-cycle CHECK', lambda: c.execute("UPDATE source_revision_lineage SET provenance='migrated',from_revision_id='rev'"))
    # Whole plan transaction, last item fails after earlier page mutation and receipt creation.
    base = snapshot(c)
    c.execute('BEGIN IMMEDIATE')
    try:
        c.execute("UPDATE pages SET sort_order=99 WHERE page_id='p1'")
        c.execute("UPDATE pages SET sort_order=99 WHERE page_id='p2'")
        c.execute("UPDATE source_sync_plans SET state='applied',applied_at='t' WHERE plan_id='other'")
        operation(c, operation_id='op2', plan_id='other')
        c.execute("INSERT INTO source_binding_publications(binding_id,operation_id,relation,read_gate) VALUES('absent','op2','added','pending')")
        raise AssertionError('failure injection did not fire')
    except sqlite3.IntegrityError:
        c.rollback()
    assert snapshot(c) == base
    ok('whole plan last-item failure rolls back pages/plan/operation/publication')
    # Actual stale v7 runner must reject with no SQL writes on a candidate v8 DB.
    base = snapshot(c)
    traced = []
    c.set_trace_callback(traced.append)
    try:
        MigrationRunner(c, MIGRATIONS).apply_pending()
        raise AssertionError('old writer accepted')
    except SchemaTooNewError:
        pass
    c.set_trace_callback(None)
    assert snapshot(c) == base
    assert not any(s.lstrip().upper().startswith(('INSERT','UPDATE','DELETE','CREATE','ALTER','BEGIN')) for s in traced)
    ok('actual v7 runner SchemaTooNewError before writes; DB identical')
    # DDL mid-stream failure and failure after both metadata writes.
    for label, statements in (
        ('mid-DDL', MigrationRunner._split_statements(SQL)[:3] + ['INSERT INTO absent VALUES(1)']),
        ('after-metadata', MigrationRunner._split_statements(SQL) + [
            "INSERT INTO schema_migrations(schema_version,migration_name,applied_at,checksum) VALUES(8,'probe','t','probe')",
            "UPDATE application_metadata SET value_json='8' WHERE metadata_key='schema_version'",
            'INSERT INTO absent VALUES(1)']),
    ):
        d = database()
        seed(d)
        base = snapshot(d)
        try:
            d.execute('BEGIN IMMEDIATE')
            for statement in statements:
                d.execute(statement)
            d.commit()
            raise AssertionError('failure not injected')
        except sqlite3.OperationalError:
            d.rollback()
        assert snapshot(d) == base
        ok(f'migration failure {label}: schema/data/both metadata rolled back to v7')
        d.close()
    # Use the actual runner rollback path as a second discriminating check.
    d = database()
    base = snapshot(d)
    broken = Migration(8,'v8__source_sync', SQL + '\nINSERT INTO absent VALUES(1);\n')
    try:
        MigrationRunner(d, MIGRATIONS + (broken,)).apply_pending()
        raise AssertionError('runner failure not injected')
    except sqlite3.OperationalError:
        pass
    assert snapshot(d) == base
    ok('actual MigrationRunner mid-migration rollback')
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    ok('final FK check')
    c.close()
    d.close()
    print(f'RESULT: {COUNT} passed; 0 skipped; contract probes only')


if __name__ == '__main__':
    try:
        run()
    except Exception:
        print('EXIT: 1')
        raise
    print('EXIT: 0')
