"""FEA-11 page/entry matching (C-15 §3.2 rules, C-17 §7.3 mapping).

Two frozen paths (AC11-3):

* same container digest → ``direct`` continuation (EntryId/PageId/order all
  preserved; a decoder observation change alone never resyncs);
* changed container → per-item evidence matching over pixel profiles:
  one-to-one unique ``unique_pixel`` continuation, whole-group
  ``duplicate_group`` when a name or pixel occurrence repeats on either
  side, and honest degradation to ``missing_old`` / ``incomparable`` when
  the v7-era evidence is absent or not comparable — never forging old
  evidence from the new image, never auto-carrying manual work across an
  ordinal/locator guess.

The matcher is pure: rows in, classified pairs out. PageId attachment and
decision validation happen in the planner.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Evidence completeness for a v7-era entry row: the import runtime wrote
#: pixel/orientation None, so width/height presence is the observable proof
#: the entry was ever decode-verified (C-17 §7.3 note on _entry_row).
def _old_evidence_complete(entry: dict) -> bool:
    width = entry.get("width") or 0
    height = entry.get("height") or 0
    return int(width) > 0 and int(height) > 0


def _pixel_present(entry: dict) -> bool:
    return bool(entry.get("pixel_digest")) and bool(
        entry.get("pixel_digest_algorithm")
    )


def _profiles_comparable(old: dict, new: dict) -> bool:
    """C-15 §3.2: same algorithm/decoder/version/params only."""
    return (
        old.get("pixel_digest_algorithm") == new.get("pixel_digest_algorithm")
        and old.get("decoder_name") == new.get("decoder_name")
        and old.get("decoder_version") == new.get("decoder_version")
        and old.get("decoder_params_json") == new.get("decoder_params_json")
    )


@dataclass
class MatchItem:
    """One classified old→new pair (page binding happens upstream)."""

    item_id: str
    classification: str
    evidence: str
    old_entry: dict | None = None
    new_entry: dict | None = None


@dataclass
class MatchResult:
    items: list[MatchItem] = field(default_factory=list)

    @property
    def totals(self) -> dict[str, int]:
        counts = {
            "unchanged": 0, "added": 0, "missing": 0, "changed": 0,
            "ambiguous": 0,
        }
        for item in self.items:
            counts[item.classification] += 1
        return counts


def match_entries(
    old_entries: list[dict],
    new_entries: list[dict],
    *,
    same_container: bool,
) -> MatchResult:
    """Classify every old/new entry pair under the frozen C-15 §3.2 rules."""
    result = MatchResult()
    if same_container:
        # Path 1: direct continuation. Entry ids are preserved as-is; every
        # page keeps EntryId/PageId/user order (C-17 §7.3 row 1).
        for index, old in enumerate(old_entries):
            result.items.append(
                MatchItem(
                    item_id=f"di-{index:06d}",
                    classification="unchanged",
                    evidence="direct",
                    old_entry=old,
                    new_entry=next(
                        (
                            entry
                            for entry in new_entries
                            if entry["entry_id"] == old["entry_id"]
                        ),
                        old,
                    ),
                )
            )
        return result

    old_by_id = {entry["entry_id"]: entry for entry in old_entries}
    new_by_id = {entry["entry_id"]: entry for entry in new_entries}
    all_entries = [*old_entries, *new_entries]

    # --- duplicate groups first: a digest or a locator occurring more than
    # once on EITHER side freezes the whole occurrence group into
    # needs_confirmation — no ordinal/locator anchoring, no automatic manual
    # work carry (C-15 §3.2, C-17 §7.3 row 3).
    digest_counts: dict[str, int] = {}
    locator_counts: dict[str, int] = {}
    for entry in all_entries:
        digest = entry.get("content_digest")
        if digest:
            digest_counts[digest] = digest_counts.get(digest, 0) + 1
        locator_counts[entry["locator"]] = locator_counts.get(
            entry["locator"], 0
        ) + 1

    duplicated_digests = {
        digest for digest, count in digest_counts.items() if count > 1
    }
    duplicated_locators = {
        locator for locator, count in locator_counts.items() if count > 1
    }

    paired_new_ids: set[str] = set()

    def _pair_for(old: dict) -> dict | None:
        digest = old.get("content_digest")
        if digest:
            for entry in new_entries:
                if entry.get("content_digest") == digest:
                    return entry
        for entry in new_entries:
            if entry["locator"] == old["locator"]:
                return entry
        return None

    # duplicate_group pass (old-side rows; new-side-only members surface as
    # ambiguous added rows below via the same duplicate sets).
    for old in old_entries:
        digest = old.get("content_digest")
        if digest in duplicated_digests or old["locator"] in duplicated_locators:
            candidate = _pair_for(old)
            if candidate is not None and (
                candidate.get("content_digest") in duplicated_digests
                or candidate["locator"] in duplicated_locators
            ):
                paired_new_ids.add(candidate["entry_id"])
            result.items.append(
                MatchItem(
                    item_id="",
                    classification="ambiguous",
                    evidence="duplicate_group",
                    old_entry=old,
                    new_entry=candidate,
                )
            )

    # --- unique digest / pixel continuation pass.
    for old in old_entries:
        if any(item.old_entry is old for item in result.items):
            continue
        digest = old.get("content_digest")
        matches = [
            entry
            for entry in new_entries
            if digest and entry.get("content_digest") == digest
        ]
        if len(matches) == 1 and digest_counts.get(digest) == 2:
            # exactly one occurrence on each side → byte/page-identity
            # equality; the pixel profile comparison follows from the
            # identical bytes (the only honest "recompute" of missing old
            # evidence C-17 §7.3 row 4 permits — same bytes, same pixels).
            new = matches[0]
            paired_new_ids.add(new["entry_id"])
            result.items.append(
                MatchItem(
                    item_id="",
                    classification="unchanged",
                    evidence="unique_pixel",
                    old_entry=old,
                    new_entry=new,
                )
            )
            continue
        if _pixel_present(old):
            pixel_matches = [
                entry
                for entry in new_entries
                if _pixel_present(entry)
                and entry["pixel_digest"] == old["pixel_digest"]
                and entry["entry_id"] not in paired_new_ids
            ]
            unique = [
                entry
                for entry in pixel_matches
                if _profiles_comparable(old, entry)
            ]
            pixel_total = sum(
                1
                for candidate in [*old_entries, *new_entries]
                if _pixel_present(candidate)
                and candidate.get("pixel_digest") == old["pixel_digest"]
            )
            if len(unique) == 1 and pixel_total == 2:
                new = unique[0]
                paired_new_ids.add(new["entry_id"])
                result.items.append(
                    MatchItem(
                        item_id="",
                        classification="unchanged",
                        evidence="unique_pixel",
                        old_entry=old,
                        new_entry=new,
                    )
                )
                continue
        # --- locator-unique correspondence with different content.
        locator_matches = [
            entry for entry in new_entries if entry["locator"] == old["locator"]
        ]
        old_locator_matches = [
            entry for entry in old_entries
            if entry["locator"] == old["locator"]
        ]
        if len(locator_matches) == 1 and len(old_locator_matches) == 1:
            new = locator_matches[0]
            paired_new_ids.add(new["entry_id"])
            if not _old_evidence_complete(old):
                # v7-era row without decode evidence: the correspondence is
                # positional only — degrade to needs-confirmation, never
                # forge the old profile from the new image (C-17 §7.3 P1/P3).
                classification, evidence = "ambiguous", "missing_old"
            elif _pixel_present(old) and _pixel_present(new) and not (
                _profiles_comparable(old, new)
            ):
                classification, evidence = "ambiguous", "incomparable"
            else:
                classification, evidence = "changed", "direct"
            result.items.append(
                MatchItem(
                    item_id="",
                    classification=classification,
                    evidence=evidence,
                    old_entry=old,
                    new_entry=new,
                )
            )
            continue
        # --- no correspondence at all: the page is gone from the container.
        result.items.append(
            MatchItem(
                item_id="",
                classification="missing",
                evidence="none",
                old_entry=old,
                new_entry=None,
            )
        )

    # --- brand-new members.
    for new in new_entries:
        if new["entry_id"] in paired_new_ids:
            continue
        if new.get("content_digest") in duplicated_digests or new[
            "locator"
        ] in duplicated_locators:
            result.items.append(
                MatchItem(
                    item_id="",
                    classification="ambiguous",
                    evidence="duplicate_group",
                    old_entry=None,
                    new_entry=new,
                )
            )
            continue
        result.items.append(
            MatchItem(
                item_id="",
                classification="added",
                evidence="none",
                old_entry=None,
                new_entry=new,
            )
        )

    # Deterministic ordering: old-side items by old ordinal, then new-only
    # items by new ordinal; ids are assigned in that order so the diff is
    # sorted by item_id (C-17 §5.3).
    def _order(item: MatchItem) -> tuple[int, int, str]:
        if item.old_entry is not None:
            return (0, int(item.old_entry["ordinal"]), item.old_entry["entry_id"])
        assert item.new_entry is not None
        return (1, int(item.new_entry["ordinal"]), item.new_entry["entry_id"])

    result.items.sort(key=_order)
    for index, item in enumerate(result.items):
        item.item_id = f"di-{index:06d}"
    # Keep only entries the caller knows about (defensive; superset of none).
    del old_by_id, new_by_id
    return result
