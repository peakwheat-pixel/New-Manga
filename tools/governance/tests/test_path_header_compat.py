"""Fixed template label compatibility must not hide ambiguous evidence columns."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean_workspace as guard


class EvidenceSink:
    def __init__(self):
        self.pins = []
        self.errors = []
        self.warnings = []

    def add_evidence_pin(self, path, *args):
        self.pins.append(path)

    def add_error(self, code, *args):
        self.errors.append(code)

    def add_warning(self, code, *args):
        self.warnings.append(code)


class PathHeaderCompatibility(unittest.TestCase):
    alias = "path（仓库相对路径或绝对路径）"

    def parse(self, columns, values):
        text = "## Canonical Evidence\n\n|" + "|".join(columns) + "|\n"
        text += "|" + "|".join(["---"] * len(columns)) + "|\n"
        text += "|" + "|".join(values) + "|\n"
        sink = EvidenceSink()
        guard.parse_markdown_declarations(sink, text, "fixture.md")
        return sink

    def test_template_and_plain_columns_protect_the_declared_pin(self):
        for label in (self.alias, "path", " PATH "):
            with self.subTest(label=label):
                sink = self.parse(["evidence_id", label], ["EV1", "kept/file.txt"])
                self.assertEqual(sink.pins, ["kept/file.txt"])
                self.assertEqual(sink.errors, [])

    def test_duplicate_alias_and_literal_never_choose_one_path(self):
        for labels in (("path", self.alias), (self.alias, "path"),
                       (self.alias, self.alias)):
            with self.subTest(labels=labels):
                sink = self.parse(["evidence_id", *labels], ["EV1", "one", "two"])
                self.assertEqual(sink.pins, [])
                self.assertIn("TABLE_DUPLICATE_IDENTITY_COLUMN", sink.errors)

    def test_unknown_annotations_and_missing_path_still_fail_closed(self):
        for label in ("path（任意文本）", "path (relative path)", "路径", "note"):
            with self.subTest(label=label):
                sink = self.parse(["evidence_id", label], ["EV1", "kept/file.txt"])
                self.assertEqual(sink.pins, [])
                self.assertIn("TABLE_SCHEMA_INCOMPLETE", sink.errors)

    def test_bad_row_shape_is_not_made_valid_by_the_alias(self):
        sink = self.parse(["evidence_id", self.alias], ["EV1", "one", "two"])
        self.assertEqual(sink.pins, [])
        self.assertIn("TABLE_ROW_ARITY", sink.errors)

    def test_resource_identity_columns_do_not_gain_aliases(self):
        for name in ("source_path", "destination_path", "disposition"):
            self.assertIsNone(guard._exact_column([name + "（说明）"], name))


if __name__ == "__main__":
    unittest.main()
