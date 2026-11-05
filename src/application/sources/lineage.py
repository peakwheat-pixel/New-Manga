"""FEA-11-LINEAGE-1: C-17 §7.1 lineage isolation guard.

The frozen contract (``doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`` §7.1) says
that every read of a *synced* page's current region must prove the region's
current revision belongs to the page's current binding, either directly or
along ``source_binding_publications.previous`` crossing **same_content**
edges only. ``changed`` / ``repoint`` / ``missing`` cut coordinate
inheritance, and ``legacy_unverified`` rows are never coordinate evidence for
the new image.

This module owns the application-level decision; the SQLite adapter supplies
the facts through :class:`LineageFacts`. Two typed, application-layer refusal
codes are raised (they are NOT additions to the C-17 §8 closed set — that
table projects C-17 commands only and old commands are deliberately not
remapped; the DSH ruling is recorded in the task card):

* ``LINEAGE_BINDING_CHANGED`` — the revision belongs to another binding and
  the publication chain is cut (``changed``/``repoint``/``missing``);
* ``LINEAGE_UNVERIFIED`` — the revision has no lineage row at all, its
  binding is ``legacy_unverified`` (``binding_id`` NULL), or the region has
  no current revision; its coordinates cannot be proven for any image.

Scope (frozen reading of §7.1 "对本卡涉及的同步页"): the guard is active
only for pages that participate in source-sync publication history — a page
with a current binding whose binding chain carries a
``source_binding_publications`` row. Managed pages (no binding) and
referenced pages that never went through a sync switch keep the pre
FEA-11-LINEAGE-1 behaviour: their coordinates were captured against the only
binding that page ever had, and both the stock backfill and the read guard
must not make them unreadable. Within the guarded scope every refusal is
fail-closed and typed (never a bare ``RuntimeError`` → ``UNKNOWN``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping, Protocol, Sequence

#: Application-level lineage refusal codes (see the module docstring).
LINEAGE_BINDING_CHANGED = "LINEAGE_BINDING_CHANGED"
LINEAGE_UNVERIFIED = "LINEAGE_UNVERIFIED"

#: Frozen C-17 §7.1 provenance values a lineage row may carry.
LineageProvenance = Literal[
    "native", "migrated", "captured_v7", "legacy_unverified"
]

#: Provenances that are coordinate evidence for the binding they name.
#: ``legacy_unverified`` names no binding at all and is read-diagnosis only.
_EVIDENCE_PROVENANCES = frozenset({"native", "migrated", "captured_v7"})


@dataclass(frozen=True, slots=True)
class RevisionLineageStanding:
    """The lineage facts of one immutable revision (read projection).

    FEA-11-LINEAGE-1 r3 (R2-05): ``region_id`` carries the lineage row's own
    region attribution so the guard can verify C-17 §7.1's "region/revision/page
    归属" requirement; a row that names another region is corrupt data and is
    refused as unverifiable (defense in depth — every production caller reads
    the revision id from the same region row today).
    """

    binding_id: str | None
    provenance: str
    region_id: str | None = None

    @property
    def is_coordinate_evidence(self) -> bool:
        return (
            self.binding_id is not None
            and self.provenance in _EVIDENCE_PROVENANCES
        )


class LineageVerificationError(RuntimeError):
    """Base typed refusal for the C-17 §7.1 isolation guard."""

    code = "LINEAGE_UNVERIFIED"
    #: Wire category family reused by every old command face (conflict).
    category = "conflict"
    #: Fixed safe phrase; details never ride the wire.
    safe_message = "source coordinates are not verifiable for the current binding"

    def __init__(
        self,
        *,
        page_id: str,
        region_id: str | None = None,
        revision_id: str | None = None,
        detail: str = "",
    ) -> None:
        super().__init__(detail or self.safe_message)
        self.page_id = page_id
        self.region_id = region_id
        self.revision_id = revision_id
        self.detail = detail or self.safe_message


class LineageBindingChanged(LineageVerificationError):
    """The revision belongs to a different binding and the chain is cut."""

    code = LINEAGE_BINDING_CHANGED
    safe_message = (
        "region coordinates belong to a previous source binding and were"
        " cut by the sync relation"
    )


class LineageUnverified(LineageVerificationError):
    """No lineage row / legacy_unverified / no current revision."""

    code = LINEAGE_UNVERIFIED
    safe_message = "region coordinates are not verified against the current binding"


class LineageFacts(Protocol):
    """The facts the guard needs, supplied by the storage adapter.

    All calls must observe the caller's open transaction (the write-side
    guard runs inside the revision commit transaction).
    """

    def page_binding(self, page_id: str) -> str | None:
        """The page's current (non-superseded) binding id, or None."""
        ...

    def page_is_sync_managed(self, page_id: str) -> bool:
        """True when the page's binding chain carries a publication row."""
        ...

    def revision_lineages(
        self, revision_ids: Sequence[str]
    ) -> Mapping[str, RevisionLineageStanding]:
        """Lineage standing keyed by revision id (missing ids are omitted)."""
        ...

    def same_content_reachable(
        self, current_binding_id: str, ancestor_binding_id: str
    ) -> bool:
        """True when ``ancestor`` is reachable from ``current`` crossing only
        ``same_content`` publication edges (C-17 §7.1)."""
        ...


@dataclass(frozen=True, slots=True)
class HiddenRegion:
    """One live region whose current revision cannot be proven for the page."""

    region_id: str
    revision_id: str | None
    code: str


@dataclass(frozen=True, slots=True)
class PageLineageVerdict:
    """Result of checking one page's live regions in ONE facts round."""

    #: False when the page is outside the sync scope (guard inactive).
    guarded: bool
    hidden: tuple[HiddenRegion, ...] = ()

    @property
    def hidden_region_ids(self) -> frozenset[str]:
        return frozenset(item.region_id for item in self.hidden)


def _code_for(
    facts: LineageFacts,
    current_binding_id: str,
    region_id: str,
    revision_id: str | None,
    standing: RevisionLineageStanding | None,
) -> str | None:
    """The refusal code for one region, or None when it is verifiable."""
    if revision_id is None:
        # C-17 §7.1: a region without a current revision is history/diagnosis
        # only and must never present itself as a new-image editable region.
        return LINEAGE_UNVERIFIED
    if standing is None:
        return LINEAGE_UNVERIFIED
    # C-17 §7.1 "并验证 region/revision/page 归属" (r3 R2-05): a lineage row
    # that names another region is corrupt data — never coordinate evidence.
    if standing.region_id is not None and standing.region_id != region_id:
        return LINEAGE_UNVERIFIED
    if not standing.is_coordinate_evidence:
        return LINEAGE_UNVERIFIED
    if standing.binding_id == current_binding_id:
        return None
    if facts.same_content_reachable(current_binding_id, standing.binding_id):
        return None
    return LINEAGE_BINDING_CHANGED


def _raise_for(
    page_id: str, region_id: str, revision_id: str | None, code: str
) -> None:
    error_type = (
        LineageBindingChanged if code == LINEAGE_BINDING_CHANGED else LineageUnverified
    )
    raise error_type(
        page_id=page_id, region_id=region_id, revision_id=revision_id
    )


class LineageIsolationGuard:
    """C-17 §7.1 read/write guard over :class:`LineageFacts`."""

    def __init__(self, facts: LineageFacts) -> None:
        self._facts = facts

    # ------------------------------------------------------------- page
    def page_verdict(
        self, page_id: str, regions: Iterable[tuple[str, str | None]]
    ) -> PageLineageVerdict:
        """Check every (region_id, current_revision_id) pair of ONE page.

        One page-binding lookup + one sync-scope decision + one batch lineage
        lookup: the guard never grows a per-region query fan-out (r1 P2-6).
        """
        pairs = list(regions)
        current_binding = self._facts.page_binding(page_id)
        if current_binding is None or not self._facts.page_is_sync_managed(page_id):
            return PageLineageVerdict(guarded=False)
        revision_ids = [revision for _region, revision in pairs if revision]
        standings = self._facts.revision_lineages(revision_ids)
        hidden: list[HiddenRegion] = []
        for region_id, revision_id in pairs:
            standing = standings.get(revision_id) if revision_id else None
            code = _code_for(
                self._facts, current_binding, region_id, revision_id, standing
            )
            if code is not None:
                hidden.append(
                    HiddenRegion(
                        region_id=region_id, revision_id=revision_id, code=code
                    )
                )
        return PageLineageVerdict(guarded=True, hidden=tuple(hidden))

    def is_region_readable(
        self, *, page_id: str, region_id: str, revision_id: str | None
    ) -> bool:
        """False when the region's coordinates cannot be proven for the page."""
        try:
            self.ensure_readable(
                page_id=page_id, region_id=region_id, revision_id=revision_id
            )
        except LineageVerificationError:
            return False
        return True

    # ------------------------------------------------------ single agent
    def ensure_readable(
        self, *, page_id: str, region_id: str, revision_id: str | None
    ) -> None:
        """Typed refusal when one region is not readable on this page."""
        self._ensure(
            page_id=page_id, region_id=region_id, revision_id=revision_id
        )

    def ensure_writable(
        self, *, page_id: str, region_id: str, revision_id: str | None
    ) -> None:
        """Typed refusal when a new revision must not be written on this page.

        FEA-11-LINEAGE-1: an edit must never launder coordinates captured
        against an older binding into a ``native`` row on the current one, so
        the SAME proof the read guard demands is required before the write.
        """
        self._ensure(
            page_id=page_id, region_id=region_id, revision_id=revision_id
        )

    # ----------------------------------------------------------- internals
    def _ensure(
        self, *, page_id: str, region_id: str, revision_id: str | None
    ) -> None:
        verdict = self.page_verdict(page_id, [(region_id, revision_id)])
        if not verdict.guarded or not verdict.hidden:
            return
        hidden = verdict.hidden[0]
        _raise_for(page_id, region_id, revision_id, hidden.code)
