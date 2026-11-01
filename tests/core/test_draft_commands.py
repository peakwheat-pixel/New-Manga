"""FEA-05-WIRE-1: Draft command surface (C078-C083) protocol tests.

The handlers only bridge the frozen M2-C1 envelope to the existing
``DraftProtectionService`` methods; these tests pin the bridge (field
mapping, error envelope, unknown-command rejection) with a fake service so
they do not need SQLite or the full assembly.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from application.editing.errors import DraftError
from bootstrap.core_service import CoreServiceServer, _draft_error_envelope


class _FakeDraft:
    def __init__(self, draft_id: str = "d1") -> None:
        self.draft_id = draft_id

    def to_json(self) -> dict:
        return {"draftId": self.draft_id}


class _FakeToken:
    def to_json(self) -> dict:
        return {
            "tokenId": "t1",
            "DraftId": "d1",
            "DraftSequence": 1,
            "SessionId": "s1",
            "issuedAt": "2026-11-02T00:00:00Z",
            "expiresAt": "2026-11-02T00:15:00Z",
        }


class _FakeCandidate:
    def to_json(self) -> dict:
        return {"candidateId": "c1", "RegionId": "r1", "BaseRevisionId": "rev1", "Origin": "user"}


class _FakeDrafts:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def open_draft(self, session_id, page_id, region_id, *, base_revision_id, page_binding_version):
        self.calls.append(("open", session_id, page_id, region_id, base_revision_id, page_binding_version))
        return SimpleNamespace(draft=_FakeDraft(), can_edit=True, token=_FakeToken())

    def patch_draft(self, draft_id, session_id, patch, *, undo_cursor=None, schedule_flush=True):
        self.calls.append(("patch", draft_id, session_id, patch, undo_cursor))
        return _FakeDraft()

    def prepare_candidate(self, region_id, patch, *, origin, draft_id=None, base_revision_id=None):
        self.calls.append(("prepare", region_id, patch, origin, draft_id, base_revision_id))
        return _FakeCandidate()

    def apply_candidates(self, token, candidate_ids=()):
        self.calls.append(("apply", token, tuple(candidate_ids)))
        return {"r1": "rev2"}

    def get_draft(self, draft_id):
        self.calls.append(("get", draft_id))
        return _FakeDraft(draft_id)

    def list_drafts(self, *, session_id=None):
        self.calls.append(("list", session_id))
        return [_FakeDraft("d1"), _FakeDraft("d2")]

    def discard_draft(self, draft_id, session_id):
        self.calls.append(("discard", draft_id, session_id))


def _server(drafts: _FakeDrafts) -> CoreServiceServer:
    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(drafts=drafts)
    return server


def test_drafts_open_maps_request_and_response():
    drafts = _FakeDrafts()
    result = _server(drafts)._dispatch_draft_command(
        "drafts_open",
        {
            "sessionId": "s1",
            "pageId": "p1",
            "regionId": "r1",
            "baseRevisionId": "rev1",
            "pageBindingVersion": 2,
        },
    )
    assert drafts.calls == [("open", "s1", "p1", "r1", "rev1", 2)]
    assert result["canEdit"] is True
    assert result["draft"] == {"draftId": "d1"}
    assert result["token"]["tokenId"] == "t1"


def test_drafts_patch_maps_request():
    drafts = _FakeDrafts()
    result = _server(drafts)._dispatch_draft_command(
        "drafts_patch", {"draftId": "d1", "sessionId": "s1", "patch": {"text": {"zh": "x"}}}
    )
    assert drafts.calls[0][0] == "patch"
    assert drafts.calls[0][3] == {"text": {"zh": "x"}}
    assert result["draft"]["draftId"] == "d1"


def test_drafts_prepare_maps_request():
    drafts = _FakeDrafts()
    result = _server(drafts)._dispatch_draft_command(
        "drafts_prepare", {"regionId": "r1", "patch": {}, "origin": "user", "draftId": "d1"}
    )
    assert drafts.calls[0][0] == "prepare"
    assert result["candidate"]["candidateId"] == "c1"


def test_drafts_apply_passes_whole_token_and_candidate_ids():
    drafts = _FakeDrafts()
    token = {"tokenId": "t1", "DraftId": "d1", "DraftSequence": 1, "SessionId": "s1",
             "issuedAt": "2026-11-02T00:00:00Z", "expiresAt": "2026-11-02T00:15:00Z"}
    result = _server(drafts)._dispatch_draft_command(
        "drafts_apply", {"token": token, "candidateIds": ["c1", "c2"]}
    )
    assert drafts.calls[0] == ("apply", token, ("c1", "c2"))
    assert result == {"r1": "rev2"}


def test_drafts_status_requires_exactly_one_selector():
    drafts = _FakeDrafts()
    server = _server(drafts)
    with pytest.raises(DraftError) as excinfo:
        server._dispatch_draft_command("drafts_status", {"draftId": "d1", "sessionId": "s1"})
    assert excinfo.value.code == "DRAFT_INVALID"

    assert server._dispatch_draft_command("drafts_status", {"draftId": "d1"})["draft"]["draftId"] == "d1"
    listed = server._dispatch_draft_command("drafts_status", {"sessionId": "s1"})
    assert [d["draftId"] for d in listed["drafts"]] == ["d1", "d2"]


def test_drafts_discard_acknowledges():
    drafts = _FakeDrafts()
    result = _server(drafts)._dispatch_draft_command("drafts_discard", {"draftId": "d1", "sessionId": "s1"})
    assert drafts.calls == [("discard", "d1", "s1")]
    assert result == {"discarded": True}


def test_invalid_payload_is_typed_validation_error():
    server = _server(_FakeDrafts())
    with pytest.raises(DraftError) as excinfo:
        server._dispatch_draft_command("drafts_open", {"sessionId": "s1"})
    assert excinfo.value.code == "DRAFT_INVALID"
    envelope = _draft_error_envelope(excinfo.value)
    assert envelope["category"] == "validation"
    assert envelope["retryable"] is False


def test_unknown_draft_command_is_rejected():
    server = _server(_FakeDrafts())
    with pytest.raises(DraftError) as excinfo:
        server._dispatch_draft_command("drafts_close", {"draftId": "d1"})
    assert excinfo.value.code == "UNKNOWN"


def test_error_envelope_uses_frozen_category_table():
    expired = DraftError("EDIT_TOKEN_EXPIRED", "expired")
    envelope = _draft_error_envelope(expired)
    assert envelope["code"] == "EDIT_TOKEN_EXPIRED"
    assert envelope["category"] == "conflict"
    assert envelope["retryable"] is False

    locked = _draft_error_envelope(DraftError("LOCK_CHANGED", "lock"))
    assert locked["category"] == "conflict"
    assert locked["retryable"] is False

    cause = _draft_error_envelope(DraftError("INTERNAL", "boom", cause_code="E_X"))
    assert cause["details"] == [{"causeCode": "E_X"}]

def test_each_command_rejects_invalid_payload():
    server = _server(_FakeDrafts())
    cases = [
        ("drafts_patch", {"draftId": "d1"}),
        ("drafts_patch", {"draftId": "d1", "sessionId": "s1", "patch": "not-an-object"}),
        ("drafts_prepare", {"regionId": "r1", "patch": {}}),
        ("drafts_prepare", {"regionId": "r1", "patch": "x", "origin": "user"}),
        ("drafts_apply", {"token": "not-an-object"}),
        ("drafts_apply", {"token": {}, "candidateIds": "not-a-list"}),
        ("drafts_discard", {"draftId": "d1"}),
        ("drafts_open", {"sessionId": "s1"}),
    ]
    for command, payload in cases:
        with pytest.raises(DraftError) as excinfo:
            server._dispatch_draft_command(command, payload)
        envelope = _draft_error_envelope(excinfo.value)
        assert envelope["code"] in ("DRAFT_INVALID", "DRAFT_PATCH_INVALID", "EDIT_TOKEN_INVALID")
        assert envelope["category"] == "validation"


def test_drafts_dispatch_is_registered_and_typed():
    """The command surface is wired into the request dispatcher, not just the helper."""
    import inspect

    source = inspect.getsource(CoreServiceServer._dispatch_request)
    for command in (
        "drafts_open",
        "drafts_patch",
        "drafts_prepare",
        "drafts_apply",
        "drafts_status",
        "drafts_discard",
    ):
        assert command in source

def test_main_contract_lists_drafts_commands():
    """The 6 Draft commands must be visible to CommandContractV11RTests.

    That parser resets its section on any ``## ``/``### `` heading and only
    accepts rows whose section starts with ``## 8.``; a ``### 8.x`` sub-heading
    would silently hide the rows (impl-r2 P1). Pin the shape here so the
    contract cannot regress to an invisible sub-section.
    """
    from pathlib import Path

    contract = Path(__file__).resolve().parents[2] / "doc" / "contracts" / "V11R_COMMAND_CONTRACT_V1.md"
    section = ""
    visible: list[str] = []
    for line in contract.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            section = stripped
            continue
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or not cells[1].replace("`", "").strip().startswith("drafts_"):
            continue
        if section.startswith("## 8."):
            visible.append(cells[0].strip())
    assert visible == ["C078", "C079", "C080", "C081", "C082", "C083"]
