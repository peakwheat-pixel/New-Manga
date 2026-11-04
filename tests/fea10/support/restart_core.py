"""Two separate Core assembly processes reopen one explicit FEA-10 fixture DB."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'src'))
from tests.core.test_fea00a_pipeline_seam import _new_workspace, _assemble
from domain.tasks.models import PipelineScope, ScopeType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--db', type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--stop', action='store_true')
    action.add_argument('--start', action='store_true')
    args = parser.parse_args()
    root = args.data_root.resolve()
    fixture_root = Path('G:/CODEX/New Manga.workspace/FEA-10/fixtures').resolve()
    if not root.is_relative_to(fixture_root) or args.db.resolve() != root / 'library.db':
        parser.error('only an isolated FEA-10 fixture library.db is allowed')
    root.mkdir(parents=True, exist_ok=True)
    receipt_path = root / 'restart-receipt.json'
    if args.stop:
        core, _, region = _new_workspace(root)
        try:
            scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
            prepared = core.pipeline.prepare_run('ocr_region', scope)
            run, created = core.pipeline.accept_prepared_run(prepared, scope, idempotency_key='restart-durable')
            assert created
            receipt_path.write_text(json.dumps({'run_id': run.run_id, 'region_id': region, 'prepared': prepared}), encoding='utf-8')
            # FEA-10 r2: a mock-local binding only exists under the mock
            # assembly. The production Core this fixture is handed to never
            # registers it, so PrepareRun on that binding must fail closed
            # (RUN_SNAPSHOT_INCOMPLETE). Clear the binding so the real-IPC
            # exercise tests the Prepare/Accept/replay wire path itself.
            core.pipeline_defaults.clear_provider_binding('ocr')
            print('COMMITTED_WITH_ACK_DROPPED run_id=' + run.run_id)
        finally: core.conn.close()
    else:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        core = _assemble(root)
        try:
            # The seeding pass cleared the mock binding for the production
            # Core; this mock-assembly replay must see the binding the seed's
            # prepared quartet was frozen with, or the digest is stale.
            core.pipeline_defaults.save_provider_binding('ocr', 'm2ac1-mock-ocr')
            # Expiry cannot hide an already committed durable receipt.
            receipt['prepared']['expiresAt'] = '2000-01-01T00:00:00+00:00'
            scope = PipelineScope(ScopeType.REGION, selected_ids=(receipt['region_id'],))
            run, created = core.pipeline.accept_prepared_run(receipt['prepared'], scope, idempotency_key='restart-durable')
            assert not created and run.run_id == receipt['run_id']
            assert core.conn.execute('SELECT COUNT(*) FROM pipeline_runs').fetchone()[0] == 1
            print('REOPEN_SAME_DB_RECEIPT_PASS run_id=' + run.run_id)
        finally: core.conn.close()
    print('DataRoot=' + str(root))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
