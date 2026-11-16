"""Historical evidence-pin exception registry (Codex ruling Q1=B).

The registry may only downgrade a row that already existed, unchanged, in a
terminal card at the frozen baseline.  These tests prove the gate honours that
and that nothing weaker slips through.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CARD = "doc/tasks/FEA-11-HOST-AUTH-2.md"
TASK_ID = "FEA-11-HOST-AUTH-2"
REGISTRY = "tools/governance/evidence-pin-exceptions.json"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class ExceptionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp(prefix=".pin-exc-test-"))
        head = run(["git", "rev-parse", "HEAD"], REPO).stdout.strip()
        cls.head = head
        # one pristine clone; each test copies it (cheap, keeps HEAD identical)
        cls.template = cls.base / "template"
        run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(REPO), str(cls.template)], REPO)
        # LF checkout: the real working tree is LF, so a CRLF clone would add
        # EOL noise that is unrelated to the exception mechanism under test.
        run(["git", "-C", str(cls.template), "config", "core.autocrlf", "false"], REPO)
        run(["git", "-C", str(cls.template), "checkout", "--quiet", "--detach", head], REPO)
        # the checker under test is the working-tree one, not the committed one
        (cls.template / "tools/governance/check.ps1").write_bytes(
            (REPO / "tools/governance/check.ps1").read_bytes())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def clone(self):
        dst = Path(tempfile.mkdtemp(prefix="clone-", dir=self.base))
        shutil.rmtree(dst)
        shutil.copytree(self.template, dst, symlinks=True)
        return dst

    def write_registry(self, clone, entries, baseline=None):
        doc = {"schema_version": 1,
               "eligibility_baseline": baseline or self.head,
               "entries": entries}
        (clone / REGISTRY).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8", newline="\n")

    def card_row(self, clone, evidence_id):
        text = (clone / CARD).read_text(encoding="utf-8")
        for line in text.split("\n"):
            if line.startswith("| %s |" % evidence_id):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                return cells
        raise AssertionError("row not found: %s" % evidence_id)

    def entry_for(self, clone, evidence_id, error_type="SHA_MISMATCH", **override):
        cells = self.card_row(clone, evidence_id)
        entry = {
            "id": "EXC-TEST-%s" % evidence_id.replace(".", "-"),
            "card": CARD,
            "task_id": TASK_ID,
            "evidence_id": cells[0],
            "path": cells[2],
            "commit": cells[3] if cells[3] not in ("-", "") else "-",
            "sha256": cells[4].lower(),
            "class": cells[5].upper(),
            "error_type": error_type,
            "reason": "test fixture",
            "ruling": "doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-GATE-RULING-2026-11-16.md",
            "expires_when": "card reopened",
        }
        entry.update(override)
        return entry

    def check(self, clone, task=CARD):
        r = run(["pwsh", "-NoProfile", "-File", str(clone / "tools/governance/check.ps1"),
                 "-TaskPath", task], clone)
        return r.stdout + r.stderr

    # ---------------------------------------------------------------- baseline
    def test_without_registry_the_rows_still_fail(self):
        clone = self.clone()
        (clone / REGISTRY).unlink(missing_ok=True)
        out = self.check(clone)
        self.assertNotIn("EXEMPTED[", out)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_empty_registry_changes_nothing(self):
        clone = self.clone()
        self.write_registry(clone, [])
        out = self.check(clone)
        self.assertNotIn("EXEMPTED[", out)
        self.assertIn("Evidence SHA-256 不匹配", out)

    # ---------------------------------------------------------------- positive
    def test_exact_match_is_downgraded_to_a_warning(self):
        clone = self.clone()
        self.write_registry(clone, [self.entry_for(clone, "EV-01")])
        out = self.check(clone)
        self.assertIn("EXEMPTED[EXC-TEST-EV-01]", out)
        # the row itself must no longer fail (the warning text still quotes the message)
        self.assertNotIn(
            "FAIL: Evidence SHA-256 不匹配：apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs",
            out)

    # ---------------------------------------------------------------- negative
    def test_any_field_change_disables_the_exception(self):
        clone = self.clone()
        entry = self.entry_for(clone, "EV-01")
        entry["sha256"] = "0" * 64
        self.write_registry(clone, [entry])
        out = self.check(clone)
        self.assertNotIn("EXEMPTED[", out)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_row_added_after_the_baseline_is_ineligible(self):
        clone = self.clone()
        # add a new canonical row to the card, then try to exempt it
        card = clone / CARD
        text = card.read_text(encoding="utf-8")
        marker = "| EV-17 |"
        idx = text.index(marker)
        line_end = text.index("\n", idx)
        new_row = ("\n| EV-99 | test | doc/STATUS.md | - | " + "1" * 64 + " | CANONICAL |")
        card.write_text(text[:line_end] + new_row + text[line_end:], encoding="utf-8", newline="\n")
        entry = {"id": "EXC-TEST-EV-99", "card": CARD, "task_id": TASK_ID,
                 "evidence_id": "EV-99", "path": "doc/STATUS.md", "commit": "-",
                 "sha256": "1" * 64, "class": "CANONICAL", "error_type": "SHA_MISMATCH",
                 "reason": "added after baseline", "ruling": "none", "expires_when": "never"}
        self.write_registry(clone, [entry])
        out = self.check(clone)
        self.assertNotIn("EXEMPTED[EXC-TEST-EV-99]", out)
        self.assertIn("EVIDENCE_EXCEPTION_INELIGIBLE", out)

    def test_wildcard_entry_is_rejected(self):
        clone = self.clone()
        entry = self.entry_for(clone, "EV-01")
        entry["path"] = "apps/desktop-avalonia/**"
        self.write_registry(clone, [entry])
        out = self.check(clone)
        self.assertIn("EVIDENCE_EXCEPTION_WILDCARD", out)
        self.assertNotIn("EXEMPTED[", out)

    def test_unresolvable_baseline_is_rejected(self):
        clone = self.clone()
        self.write_registry(clone, [self.entry_for(clone, "EV-01")], baseline="0" * 40)
        out = self.check(clone)
        self.assertIn("EVIDENCE_EXCEPTION_BASELINE_UNRESOLVED", out)
        self.assertNotIn("EXEMPTED[", out)

    def test_duplicate_fingerprint_is_rejected(self):
        clone = self.clone()
        entry = self.entry_for(clone, "EV-01")
        second = dict(entry, id="EXC-TEST-EV-01-B")
        self.write_registry(clone, [entry, second])
        out = self.check(clone)
        self.assertIn("EVIDENCE_EXCEPTION_DUPLICATE_ROW", out)

    def test_shipped_registry_is_valid(self):
        doc = json.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(doc["schema_version"], 1)
        self.assertRegex(doc["eligibility_baseline"], r"^[0-9a-f]{40}$")
        for entry in doc["entries"]:
            self.assertEqual(sorted(entry),
                             sorted(["id", "card", "task_id", "evidence_id", "path",
                                     "commit", "sha256", "class", "error_type", "reason",
                                     "ruling", "expires_when"]))
            self.assertNotIn("*", entry["path"])


if __name__ == "__main__":
    unittest.main()
