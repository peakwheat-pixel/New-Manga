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


def _pixel_present(entry: dict) -> bool:
    return bool(entry.get("pixel_digest")) and bool(
        entry.get("pixel_digest_algorithm")
    )


def _geometry(entry: dict) -> tuple[int, int]:
    return (int(entry.get("width") or 0), int(entry.get("height") or 0))


def _canonical_params(value) -> str | None:
    """Canonical JSON for a params value (object or JSON text); None if bad.

    Comparability is decided on the **object**, never on the raw stored
    string: key order/whitespace differences must not fork the profile
    (C-17 §7.3 row 2; card C8).
    """
    import json

    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None
    if not isinstance(value, dict):
        # C8: params are a canonical JSON object; a scalar/array is not a
        # profile and must never compare equal by accident.
        return None
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return None


def _profiles_comparable(old: dict, new: dict) -> bool:
    """C-17 §7.3 row 2: all seven dimensions must be equal.

    ``algorithm + decoder + decoder_version + canonical params + width +
    height + orientation``.  A missing side is never comparable.
    """
    if not _pixel_present(old) or not _pixel_present(new):
        return False
    if old.get("pixel_digest_algorithm") != new.get("pixel_digest_algorithm"):
        return False
    if old.get("decoder_name") != new.get("decoder_name"):
        return False
    if old.get("decoder_version") != new.get("decoder_version"):
        return False
    old_params = _canonical_params(old.get("decoder_params_json"))
    new_params = _canonical_params(new.get("decoder_params_json"))
    if old_params is None or new_params is None or old_params != new_params:
        return False
    if _geometry(old) != _geometry(new):
        return False
    if int(old.get("orientation") or 0) != int(new.get("orientation") or 0):
        return False
    return True


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


def _counts(entries: list[dict], getter) -> dict:
    counts: dict = {}
    for entry in entries:
        value = getter(entry)
        if value:
            counts[value] = counts.get(value, 0) + 1
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

    # --- duplicate occurrence statistics, per side (C-15 §3.2): a content
    # digest, a locator or a pixel digest repeated on EITHER side freezes the
    # occurrence group into needs_confirmation.  Pixel digests are part of
    # the identity triad since FEA-11-MATCH-1 (AC-M3).
    old_digest_counts = _counts(old_entries, lambda entry: entry.get("content_digest"))
    new_digest_counts = _counts(new_entries, lambda entry: entry.get("content_digest"))
    old_locator_counts = _counts(old_entries, lambda entry: entry["locator"])
    new_locator_counts = _counts(new_entries, lambda entry: entry["locator"])
    old_pixel_counts = _counts(
        old_entries, lambda entry: entry.get("pixel_digest")
    )
    new_pixel_counts = _counts(
        new_entries, lambda entry: entry.get("pixel_digest")
    )

    def _dup_digest(digest: str | None) -> bool:
        return bool(digest) and (
            old_digest_counts.get(digest, 0) > 1
            or new_digest_counts.get(digest, 0) > 1
        )

    def _dup_locator(locator: str) -> bool:
        return (
            old_locator_counts.get(locator, 0) > 1
            or new_locator_counts.get(locator, 0) > 1
        )

    def _dup_pixel(digest: str | None) -> bool:
        return bool(digest) and (
            old_pixel_counts.get(digest, 0) > 1
            or new_pixel_counts.get(digest, 0) > 1
        )

    def _is_duplicate_member(entry: dict) -> bool:
        return (
            _dup_digest(entry.get("content_digest"))
            or _dup_locator(entry["locator"])
            or (_pixel_present(entry) and _dup_pixel(entry.get("pixel_digest")))
        )

    paired_new_ids: set[str] = set()
    paired_old_ids: set[str] = set()

    def _candidate_for(old: dict) -> dict | None:
        """Best cross-side counterpart for a duplicate member (unpaired only).

        Preference is content digest → locator → pixel digest.  This is a
        diagnostic pairing for an ``ambiguous`` row, never an automatic
        keep/bind decision: duplicate groups are only allowed to end in
        bind/defer decisions downstream.
        """
        digest = old.get("content_digest")
        if digest:
            for entry in new_entries:
                if entry["entry_id"] in paired_new_ids:
                    continue
                if entry.get("content_digest") == digest:
                    return entry
        for entry in new_entries:
            if entry["entry_id"] in paired_new_ids:
                continue
            if entry["locator"] == old["locator"]:
                return entry
        if _pixel_present(old):
            for entry in new_entries:
                if entry["entry_id"] in paired_new_ids:
                    continue
                if (
                    _pixel_present(entry)
                    and entry.get("pixel_digest") == old["pixel_digest"]
                ):
                    return entry
        return None

    # --- duplicate_group pass (old side).  AC-M4: a duplicate member with NO
    # cross-side counterpart is honestly missing/none — a duplicate_group row
    # with one side null would violate the C-17 §5.3 combination guard
    # (ambiguous requires both entries).
    for old in old_entries:
        if not _is_duplicate_member(old):
            continue
        paired_old_ids.add(old["entry_id"])
        candidate = _candidate_for(old)
        if candidate is None:
            result.items.append(
                MatchItem(
                    item_id="",
                    classification="missing",
                    evidence="none",
                    old_entry=old,
                    new_entry=None,
                )
            )
            continue
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

    # --- byte-identity pass: exactly one occurrence on each side.  Identical
    # bytes imply identical pixels, but a repeated pixel occurrence still
    # freezes the group (AC-M3: the byte branch must not bypass duplicates).
    for old in old_entries:
        if old["entry_id"] in paired_old_ids:
            continue
        digest = old.get("content_digest")
        if not digest:
            continue
        matches = [
            entry
            for entry in new_entries
            if entry["entry_id"] not in paired_new_ids
            and entry.get("content_digest") == digest
        ]
        if not (
            len(matches) == 1
            and old_digest_counts.get(digest) == 1
            and new_digest_counts.get(digest) == 1
        ):
            continue
        new = matches[0]
        paired_old_ids.add(old["entry_id"])
        paired_new_ids.add(new["entry_id"])
        pixel_duplicate = (
            (_pixel_present(old) and _dup_pixel(old.get("pixel_digest")))
            or (_pixel_present(new) and _dup_pixel(new.get("pixel_digest")))
        )
        result.items.append(
            MatchItem(
                item_id="",
                classification="ambiguous" if pixel_duplicate else "unchanged",
                evidence=(
                    "duplicate_group" if pixel_duplicate else "unique_pixel"
                ),
                old_entry=old,
                new_entry=new,
            )
        )

    # --- unique pixel continuation pass (C-17 §7.3 row 2): the pixel digest
    # must occur exactly once on each side AND all seven profile dimensions
    # must be comparable, otherwise the pair is not a proven continuation.
    for old in old_entries:
        if old["entry_id"] in paired_old_ids or not _pixel_present(old):
            continue
        pixel_digest = old["pixel_digest"]
        candidates = [
            entry
            for entry in new_entries
            if entry["entry_id"] not in paired_new_ids
            and _pixel_present(entry)
            and entry.get("pixel_digest") == pixel_digest
        ]
        comparable = [
            entry
            for entry in candidates
            if _profiles_comparable(old, entry)
        ]
        if (
            len(candidates) == 1
            and len(comparable) == 1
            and old_pixel_counts.get(pixel_digest, 0) == 1
            and new_pixel_counts.get(pixel_digest, 0) == 1
        ):
            new = comparable[0]
            paired_old_ids.add(old["entry_id"])
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
        elif len(candidates) == 1 and not comparable:
            # R1-01 (AC-M4 first sentence; C-17 §7.3 row 4): the same pixel
            # occurrence exists on the other side but the profiles cannot be
            # compared (e.g. container repacked/renamed together with a
            # Pillow/decoder/params upgrade so every old profile is
            # incomparable).  This is "unverifiable", not "old page gone":
            # degrade the corresponding pair to needs_confirmation so the
            # user can still bind and keep the PageId instead of being forced
            # into missing(tombstone/defer)+added(add).  Duplicate groups were
            # already absorbed by the earlier pass, so exactly one candidate
            # here is the whole (unpaired) occurrence.
            new = candidates[0]
            paired_old_ids.add(old["entry_id"])
            paired_new_ids.add(new["entry_id"])
            result.items.append(
                MatchItem(
                    item_id="",
                    classification="ambiguous",
                    evidence="incomparable",
                    old_entry=old,
                    new_entry=new,
                )
            )

    # --- locator-unique correspondence with different content (C-17 §7.3 row
    # 4).  ``changed`` is only a deterministic assertion when BOTH sides carry
    # complete, comparable pixel evidence and the pixels differ; anything
    # less degrades to needs-confirmation (AC-M4).
    for old in old_entries:
        if old["entry_id"] in paired_old_ids:
            continue
        locator_matches = [
            entry
            for entry in new_entries
            if entry["entry_id"] not in paired_new_ids
            and entry["locator"] == old["locator"]
        ]
        old_locator_matches = [
            entry for entry in old_entries if entry["locator"] == old["locator"]
        ]
        if not (len(locator_matches) == 1 and len(old_locator_matches) == 1):
            continue
        new = locator_matches[0]
        paired_old_ids.add(old["entry_id"])
        paired_new_ids.add(new["entry_id"])
        if not _pixel_present(old):
            # v7-era row (pixel/orientation None; at most W/H present): the
            # positional correspondence is unverifiable — never forge the old
            # profile from the new image (C-17 §7.3 row 4).
            classification, evidence = "ambiguous", "missing_old"
        elif not _pixel_present(new):
            classification, evidence = "ambiguous", "incomparable"
        elif not _profiles_comparable(old, new):
            classification, evidence = "ambiguous", "incomparable"
        elif old.get("pixel_digest") == new.get("pixel_digest"):
            # R1-08 defensive guard: identical pixels with different bytes are
            # an occurrence-identity question (duplicate_group), never a
            # deterministic content change.  Pass ordering currently pairs
            # this case earlier, so this branch is unreachable by construction
            # but keeps ``changed`` honest if the passes are ever reordered.
            classification, evidence = "ambiguous", "duplicate_group"
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

    # --- no correspondence at all: the page is gone from the container.
    for old in old_entries:
        if old["entry_id"] in paired_old_ids:
            continue
        result.items.append(
            MatchItem(
                item_id="",
                classification="missing",
                evidence="none",
                old_entry=old,
                new_entry=None,
            )
        )

    # --- brand-new members.  A duplicate occurrence with no cross-side
    # counterpart is an honest add (AC-M4), not a one-sided ambiguous row.
    for new in new_entries:
        if new["entry_id"] in paired_new_ids:
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
    return result
