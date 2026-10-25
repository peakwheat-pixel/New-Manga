import json

import pytest

import diagnose
import freeze_review


def test_write_refuses_changed_evidence(tmp_path):
    path = tmp_path / 'pin.json'
    diagnose.write(path, {'exit': 0})
    diagnose.write(path, {'exit': 0})
    with pytest.raises(AssertionError, match='refusing overwrite'):
        diagnose.write(path, {'exit': 1})
    assert json.loads(path.read_text()) == {'exit': 0}


def test_package_validation_rejects_missing_referenced_log(tmp_path, monkeypatch):
    checks = tmp_path / 'checks.json'
    checks.write_text(json.dumps({'log': 'missing.log', 'exit': 0}))
    diagnose.write(tmp_path / 'PACKAGE_MANIFEST.json',
                   {'files': [{'path': checks.name, 'sha256': diagnose.sha(checks)}]})
    monkeypatch.setattr(freeze_review, 'PACKAGE', tmp_path)
    with pytest.raises(AssertionError, match='missing.log'):
        freeze_review.verify()


def test_package_validation_rejects_changed_bytes(tmp_path, monkeypatch):
    raw = tmp_path / 'original.log'
    raw.write_bytes(b'original')
    diagnose.write(tmp_path / 'PACKAGE_MANIFEST.json',
                   {'files': [{'path': raw.name, 'sha256': diagnose.sha(raw)}]})
    raw.write_bytes(b'changed')
    monkeypatch.setattr(freeze_review, 'PACKAGE', tmp_path)
    with pytest.raises(AssertionError):
        freeze_review.verify()
