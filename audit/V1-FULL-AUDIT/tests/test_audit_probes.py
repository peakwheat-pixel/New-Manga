"""Vulnerability demonstrations, not acceptance tests: PASS confirms the defect."""
import hashlib
import json
from pathlib import Path
import runpy
import zipfile
import subprocess


def test_managed_publish_follows_directory_junction(tmp_path):
    from infrastructure.filesystem.managed_storage import ManagedFileStorage
    managed = tmp_path / 'managed'
    outside = tmp_path / 'outside-controlled-sentinel'
    outside.mkdir()
    storage = ManagedFileStorage(managed)
    storage.ensure_layout()
    junction = managed / 'books'
    result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(junction), str(outside)], capture_output=True)
    assert result.returncode == 0, result.stderr
    temporary = storage.write_temp(b'AUDIT-JUNCTION')
    storage.publish(temporary, 'books/new-revision.png')
    assert (outside / 'new-revision.png').read_bytes() == b'AUDIT-JUNCTION'
    print(json.dumps({'defect_confirmed': True, 'publish_wrote_outside_managed': True, 'scope': 'all paths under isolated tmp_path'}))


def test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[3]
    fixture = runpy.run_path(str(root / 'tests/storage/test_nmbak_backup.py'))['workspace']
    generator = fixture.__wrapped__(tmp_path)
    workspace = next(generator)
    try:
        workspace['seed_page']('page-1', b'BEFORE')
        service, conn = workspace['service'], workspace['conn']
        backup = service.create('manual', 'isolated write-failure probe')
        with conn:
            conn.execute("UPDATE books SET title='USER-EDIT-AFTER-BACKUP'")
        original = Path.write_bytes
        def failing_write(path, data):
            if path.is_relative_to(workspace['managed_root']):
                raise OSError('AUDIT-SIMULATED-DISK-FULL')
            return original(path, data)
        monkeypatch.setattr(Path, 'write_bytes', failing_write)
        try:
            service.restore(backup['backup_id'], confirm_restore=True)
        except OSError as error:
            assert str(error) == 'AUDIT-SIMULATED-DISK-FULL'
            assert not hasattr(error, 'code')
            assert conn.execute('SELECT title FROM books').fetchone()[0] == 'B'
            print(json.dumps({'defect_confirmed': True, 'database_changed': True, 'typed_error': False,
                              'rollback_id_in_error': False, 'pre_restore_packages': len(list(workspace['backup_root'].glob('*.nmbak'))) - 1}))
        else:
            raise AssertionError('Disk failure not propagated; defect behavior changed')
    finally:
        workspace['conn'].close()
        generator.close()


def test_nmbak_restore_can_overwrite_outside_managed_root(tmp_path):
    root = Path(__file__).resolve().parents[3]
    fixture = runpy.run_path(str(root / 'tests/storage/test_nmbak_backup.py'))['workspace']
    generator = fixture.__wrapped__(tmp_path)
    workspace = next(generator)
    try:
        service = workspace['service']
        backup = service.create('manual', 'isolated audit probe')
        package = workspace['backup_root'] / (backup['backup_id'] + '.nmbak')
        with zipfile.ZipFile(package) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        manifest = json.loads(members['manifest.json'])
        payload = b'AUDIT-OVERWRITE'
        manifest['revision_refs'] = [{'managed_path': '../audit-victim.txt', 'sha256': hashlib.sha256(payload).hexdigest()}]
        manifest['managed_file_count'] = 1
        manifest['managed_total_bytes'] = len(payload)
        members['manifest.json'] = json.dumps(manifest).encode()
        members['managed/../audit-victim.txt'] = payload
        members['audit-victim.txt'] = payload
        with zipfile.ZipFile(package, 'w') as archive:
            for name, data in members.items():
                archive.writestr(name, data)
        victim = tmp_path / 'audit-victim.txt'
        victim.write_bytes(b'ORIGINAL-SENTINEL')
        result = service.restore(backup['backup_id'], confirm_restore=True)
        assert victim.read_bytes() == payload, 'Defect not reproduced: inspect implementation changes'
        assert victim.parent == workspace['managed_root'].parent
        print(json.dumps({'defect_confirmed': True, 'outside_managed_root': True,
                          'before': 'ORIGINAL-SENTINEL', 'after': victim.read_text(),
                          'pre_restore_backup_created': bool(result['pre_restore_backup_id'])}))
    finally:
        workspace['conn'].close()
        generator.close()
