"""Historical-evidence policy self-consistency (GOV-DECLARATION-SCAN-CLEANUP-1 AC3).

Ruling: Codex adjudication 2026-11-16 (Q1/Q2).  The policy file and the code's
approved binding identity set must move together:

* every binding ID is in ``HISTORICAL_EVIDENCE_BINDING_IDS`` and vice versa;
* ``HISTORICAL_EVIDENCE_DIGEST`` equals the canonical digest of the file
  (editing the policy without rebasing the constant fails here);
* each binding's ``raw_sha256`` / ``byte_length`` match the real bytes on disk;
* the diagnostic each binding interprets is exactly the one the scanner emits
  for its format (markdown+NULL -> FILE_UNREADABLE, json -> JSON_PARSE);
* a JSON binding is only legitimate while the file still fails to parse.

These tests must fail if a binding is added/removed without the paired code
edit, if a bound file changes bytes, or if a bound JSON becomes parsable.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean_workspace as guard


def canonical(policy):
    return hashlib.sha256(json.dumps(policy, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


class HistoricalBindingPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = REPO / guard.HISTORICAL_EVIDENCE_POLICY
        cls.policy = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.bindings = (cls.policy["template_bindings"]
                        + cls.policy["raw_non_declaration_bindings"])

    def test_binding_ids_match_the_approved_member_invariant(self):
        self.assertEqual([b["id"] for b in self.bindings],
                         list(guard.HISTORICAL_EVIDENCE_BINDING_IDS))

    def test_reference_guard_ids_match_the_approved_member_invariant(self):
        self.assertEqual([g["id"] for g in self.policy["reference_guards"]],
                         list(guard.HISTORICAL_EVIDENCE_REFERENCE_GUARD_IDS))

    def test_digest_constant_is_rebased_after_every_policy_edit(self):
        self.assertEqual(canonical(self.policy), guard.HISTORICAL_EVIDENCE_DIGEST)

    def test_every_binding_has_the_uniform_format_field(self):
        for binding in self.bindings:
            with self.subTest(binding=binding["id"]):
                self.assertIn(binding["format"], ("markdown", "json"))

    def test_raw_identity_matches_the_bytes_on_disk(self):
        for binding in self.bindings:
            with self.subTest(binding=binding["id"]):
                raw = (REPO / binding["origin_file"]).read_bytes()
                self.assertEqual(len(raw), binding["byte_length"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), binding["raw_sha256"])

    def test_control_and_nul_offsets_are_exact(self):
        for binding in self.bindings:
            with self.subTest(binding=binding["id"]):
                raw = (REPO / binding["origin_file"]).read_bytes()
                controls = [{"offset": i, "byte": c} for i, c in enumerate(raw)
                            if c < 32 and c not in (9, 10, 13)]
                self.assertEqual(controls, binding["c0_bytes"])
                if "nul_offsets" in binding:
                    self.assertEqual([o["offset"] for o in controls if o["byte"] == 0],
                                     binding["nul_offsets"])

    def test_bound_diagnostic_matches_the_binding_format(self):
        for binding in self.bindings:
            with self.subTest(binding=binding["id"]):
                self.assertEqual(len(binding["errors"]), 1 if binding["id"] != "HIE-T01" else 2)
                code = binding["errors"][0]["code"]
                if binding["format"] == "json":
                    self.assertEqual(code, "JSON_PARSE")
                    self.assertEqual(binding.get("nul_offsets"), [])
                elif binding.get("nul_offsets"):
                    self.assertEqual(code, "FILE_UNREADABLE")
                elif "fence" in binding:
                    # template binding: markdown whose errors are table errors
                    self.assertIn(code, ("TABLE_ROW_ARITY", "TABLE_DELIMITER",
                                         "TABLE_SCHEMA_INCOMPLETE",
                                         "DECL_UNKNOWN_DISPOSITION"))
                else:
                    self.fail("markdown binding without a NUL offset or template fence")

    def test_json_bindings_are_only_legitimate_while_unparsable(self):
        for binding in self.bindings:
            if binding["format"] != "json":
                continue
            with self.subTest(binding=binding["id"]):
                raw = (REPO / binding["origin_file"]).read_bytes()
                self.assertTrue(guard._json_source_is_unparsable(raw),
                                "bound JSON became parsable; it must be scanned again")

    def test_json_source_helper_accepts_a_valid_document(self):
        self.assertFalse(guard._json_source_is_unparsable(b'{"a": 1}'))
        self.assertFalse(guard._json_source_is_unparsable(b'\xef\xbb\xbf{"a": 1}'))
        self.assertTrue(guard._json_source_is_unparsable(b'{"a": "\\q"}'))

    def test_table_bindings_are_a_contiguous_member_sequence(self):
        tables = self.policy["table_bindings"]
        self.assertTrue(tables, "B1 table bindings must be listed explicitly")
        self.assertEqual([t["id"] for t in tables],
                         ["HIE-B%03d" % n for n in range(1, len(tables) + 1)])
        for table in tables:
            with self.subTest(table=table["id"]):
                self.assertEqual(table["classification"], "B1")
                self.assertEqual(table["interpretation"], "historical_format_preserved")
                self.assertIn(table["section"], ("Resource Manifest", "Canonical Evidence"))

    def test_table_binding_block_bytes_are_exact(self):
        for table in self.policy["table_bindings"]:
            with self.subTest(table=table["id"]):
                raw = (REPO / table["origin_file"]).read_bytes()
                text = raw.decode("utf-8")
                section = guard.section_text(text, table["section"])
                block = dict(guard.iter_table_blocks(section)).get(table["table_start"])
                self.assertIsNotNone(block)
                self.assertGreaterEqual(len(block), 2)
                self.assertEqual(hashlib.sha256("\n".join(block).encode("utf-8")).hexdigest(),
                                 table["block_sha256"])
                self.assertEqual(block[0], table["header_verbatim"])
                self.assertEqual(block[1], table["second_line_verbatim"])
                self.assertEqual(len(block) - 2, table["row_count"])

    def test_table_bindings_only_carry_historical_format_codes(self):
        allowed = {"TABLE_SCHEMA_INCOMPLETE", "TABLE_DELIMITER", "TABLE_ROW_ARITY",
                   "TABLE_HEADER_ARITY", "TABLE_INCOMPLETE",
                   "TABLE_DUPLICATE_IDENTITY_COLUMN"}
        seen = set()
        for table in self.policy["table_bindings"]:
            for error in table["errors"]:
                self.assertIn(error["code"], allowed, error)
                self.assertEqual(error["file"], table["origin_file"])
                self.assertIsNone(error["locator"])
                key = (error["file"], error["code"], error["message"])
                self.assertNotIn(key, seen, "a B1 diagnostic is bound twice")
                seen.add(key)

    def test_pinned_retentions_are_a_contiguous_member_sequence(self):
        items = self.policy.get("pinned_defect_retentions", [])
        self.assertTrue(items, "pinned B2 defects must be listed explicitly")
        self.assertEqual([r["id"] for r in items],
                         ["HIE-R%03d" % n for n in range(1, len(items) + 1)])
        for item in items:
            with self.subTest(item=item["id"]):
                self.assertEqual(item["classification"], "B2")
                self.assertEqual(item["interpretation"], "pinned_defect_retained")
                self.assertIn(item["pin"]["channel"], ("BLOB", "WORKTREE"))
                self.assertTrue(item["pin"].get("path"), "pin must name the protected file")
                self.assertEqual(item["error"]["file"], item["origin_file"])

    def test_pinned_retention_pins_still_verify(self):
        import subprocess
        for item in self.policy.get("pinned_defect_retentions", []):
            pin = item["pin"]
            with self.subTest(item=item["id"]):
                rel = pin.get("path", item["origin_file"])
                raw = (REPO / rel).read_bytes()
                if pin["channel"] == "BLOB":
                    commit = pin["commit"]
                    self.assertRegex(commit or "", r"^[0-9a-f]{7,40}$")
                    blob = subprocess.run(
                        ["git", "-C", str(REPO), "cat-file", "blob",
                         "%s:%s" % (commit, rel)], capture_output=True)
                    self.assertEqual(blob.returncode, 0)
                    self.assertEqual(hashlib.sha256(blob.stdout).hexdigest(), pin["sha256"])
                else:
                    # exactly two registered digests; the live bytes must match one
                    self.assertIn(hashlib.sha256(raw).hexdigest(),
                                  {pin["sha256"], pin["sha256_alt"]},
                                  "live bytes match neither registered digest")

    def test_worktree_alt_digest_is_a_pure_line_ending_transform(self):
        """Ruling Q2=C: the counterpart digest is the same bytes with only
        CRLF<->LF applied, and its LF form must equal the committed blob."""
        import subprocess
        for item in self.policy.get("pinned_defect_retentions", []):
            pin = item["pin"]
            if pin["channel"] != "WORKTREE":
                self.assertEqual(set(pin), {"card", "evidence_id", "commit",
                                            "sha256", "channel", "path"})
                continue
            with self.subTest(item=item["id"]):
                self.assertEqual(set(pin), {"card", "evidence_id", "commit", "sha256",
                                            "channel", "path", "sha256_alt", "alt_kind"})
                self.assertIn(pin["alt_kind"], ("LF", "CRLF"))
                self.assertNotEqual(pin["sha256"], pin["sha256_alt"])
                raw = (REPO / pin["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])
                if pin["alt_kind"] == "CRLF":
                    self.assertNotIn(b"\r", raw)
                    alt_bytes = raw.replace(b"\n", b"\r\n")
                    lf_bytes = raw
                else:
                    alt_bytes = raw.replace(b"\r\n", b"\n")
                    lf_bytes = alt_bytes
                    self.assertNotIn(b"\r", alt_bytes)
                self.assertEqual(hashlib.sha256(alt_bytes).hexdigest(), pin["sha256_alt"])
                blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob",
                                       "HEAD:%s" % pin["path"]], capture_output=True)
                self.assertEqual(blob.returncode, 0)
                self.assertEqual(lf_bytes, blob.stdout,
                                 "LF form must be byte-identical to the committed blob")

    def test_retention_rejects_content_change_and_mixed_eol(self):
        """Negative: a one-byte content change, a mixed-EOL variant and another
        record's digest must all fail against the two registered digests."""
        item = next(i for i in self.policy["pinned_defect_retentions"]
                    if i["pin"]["channel"] == "WORKTREE")
        pin = item["pin"]
        raw = (REPO / pin["path"]).read_bytes()
        allowed = {pin["sha256"], pin["sha256_alt"]}
        pos = raw.index(b"\n") + 1 if b"\n" in raw else 0
        mutated = raw[:pos] + (b"X" if raw[pos:pos + 1] != b"X" else b"Y") + raw[pos + 1:]
        self.assertNotIn(hashlib.sha256(mutated).hexdigest(), allowed,
                         "a one-byte content change must not be accepted")
        mixed = raw.replace(b"\n", b"\r\n", 1)
        self.assertNotIn(hashlib.sha256(mixed).hexdigest(), allowed,
                         "a mixed-EOL variant must not be accepted")
        for other in self.policy["pinned_defect_retentions"]:
            if other["pin"]["path"] == pin["path"]:
                continue
            foreign = {other["pin"]["sha256"]}
            if "sha256_alt" in other["pin"]:
                foreign.add(other["pin"]["sha256_alt"])
            self.assertTrue(foreign.isdisjoint(allowed),
                            "digests must stay bound to their own record")

    def test_pinned_retention_only_covers_real_b2_codes(self):
        b2_ok = {"DECL_RELATIVE_UNRESOLVED", "DECL_ENV", "DECL_GLOB",
                 "DECL_DESTINATION_UNRESOLVED", "DECL_TRAVERSAL",
                 "DECL_RELATIVE_AMBIGUOUS", "DECL_BARE_NAME", "DECL_MISSING_SOURCE"}
        seen = set()
        for item in self.policy.get("pinned_defect_retentions", []):
            code = item["error"]["code"]
            self.assertIn(code, b2_ok, item["id"])
            key = (item["origin_file"], code, item["error"]["message"])
            self.assertNotIn(key, seen, "a pinned defect is retained twice")
            seen.add(key)

    def test_keep_map_only_names_bound_ids(self):
        bound = {b["id"] for b in self.bindings}
        self.assertTrue(set(guard.HISTORICAL_EVIDENCE_KEEP) <= bound)
        for binding in self.bindings:
            expected = guard.HISTORICAL_EVIDENCE_KEEP.get(binding["id"],
                                                          "PRESERVE_REFERENCED")
            self.assertEqual(binding["source_guard"]["keep"], expected)


if __name__ == "__main__":
    unittest.main()
