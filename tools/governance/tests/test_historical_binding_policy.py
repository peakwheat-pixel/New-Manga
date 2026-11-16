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

    def test_keep_map_only_names_bound_ids(self):
        bound = {b["id"] for b in self.bindings}
        self.assertTrue(set(guard.HISTORICAL_EVIDENCE_KEEP) <= bound)
        for binding in self.bindings:
            expected = guard.HISTORICAL_EVIDENCE_KEEP.get(binding["id"],
                                                          "PRESERVE_REFERENCED")
            self.assertEqual(binding["source_guard"]["keep"], expected)


if __name__ == "__main__":
    unittest.main()
