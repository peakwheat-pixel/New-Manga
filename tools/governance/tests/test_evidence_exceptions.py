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
        self.write_registry(clone, [self.entry_for(clone, "EV-11")])
        out = self.check(clone)
        self.assertIn("EXEMPTED[EXC-TEST-EV-11]", out)
        # the row itself must no longer fail (the warning text still quotes the message)
        self.assertNotIn("FAIL: Evidence SHA-256 不匹配：doc/tasks/FEA-11-HOST-AUTH-3.md", out)

    # ---------------------------------------------------------------- negative
    def test_any_field_change_disables_the_exception(self):
        clone = self.clone()
        entry = self.entry_for(clone, "EV-11")
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

    def test_exception_lapses_when_the_card_is_reopened(self):
        # ruling condition 4: reopening the card must invalidate the exception
        clone = self.clone()
        self.write_registry(clone, [self.entry_for(clone, "EV-11")])
        card = clone / CARD
        text = card.read_text(encoding="utf-8")
        self.assertIn("status: done", text)
        card.write_text(text.replace("status: done", "status: in_review", 1),
                        encoding="utf-8", newline="\n")
        out = self.check(clone)
        self.assertNotIn("EXEMPTED[", out)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_prose_commit_is_downgraded_only_with_the_exact_text(self):
        clone = self.clone()
        entry = {"id": "EXC-TEST-CF", "card": "doc/tasks/FEA-GOV-10.md", "task_id": "FEA-GOV-10",
                 "evidence_id": "E-C07", "path": "doc/plan/FEA-C07_API_INVENTORY.md",
                 "commit": "(见提交)",
                 "sha256": "5919b084c906f5cdc79d7e6e1b425f05347d915a77bb5c50f9f97f09c3960b5f",
                 "class": "CANONICAL", "error_type": "COMMIT_FORMAT",
                 "reason": "test", "ruling": "test", "expires_when": "test"}
        self.write_registry(clone, [entry])
        out = self.check(clone, "doc/tasks/FEA-GOV-10.md")
        self.assertIn("EXEMPTED[EXC-TEST-CF]", out)
        # a different prose value must not match
        clone2 = self.clone()
        self.write_registry(clone2, [dict(entry, commit="(见其它提交)")])
        out2 = self.check(clone2, "doc/tasks/FEA-GOV-10.md")
        self.assertNotIn("EXEMPTED[EXC-TEST-CF]", out2)
        self.assertIn("Evidence commit 格式无效", out2)

    def test_multi_digest_cell_requires_the_exact_ordered_list(self):
        clone = self.clone()
        card = "doc/tasks/FEA-05-PORT-1.md"
        text = (clone / card).read_text(encoding="utf-8")
        row = next(l for l in text.split("\n") if l.startswith("| E-FEA05P-PORTS |"))
        cells = [c.strip().strip("`").strip() for c in row.strip().strip("|").split("|")]
        import re as _re
        digests = [d.lower() for d in _re.findall(r"[0-9a-fA-F]{64}", cells[4])]
        entry = {"id": "EXC-TEST-MULTI", "card": card, "task_id": "FEA-05-PORT-1",
                 "evidence_id": "E-FEA05P-PORTS", "path": cells[2], "commit": cells[3],
                 "sha256": digests, "class": cells[5].upper(), "error_type": "SHA_MULTI",
                 "reason": "test", "ruling": "test", "expires_when": "test"}
        self.write_registry(clone, [entry])
        out = self.check(clone, card)
        self.assertIn("EXEMPTED[EXC-TEST-MULTI]", out)
        clone2 = self.clone()
        self.write_registry(clone2, [dict(entry, sha256=list(reversed(digests)))])
        out2 = self.check(clone2, card)
        self.assertNotIn("EXEMPTED[EXC-TEST-MULTI]", out2)

    def test_all_placeholder_row_is_a_structural_error(self):
        clone = self.clone()
        card = clone / "doc/tasks/FEA-11-HOST-AUTH-2.md"
        lines = card.read_text(encoding="utf-8").split("\n")
        start = next(i for i, l in enumerate(lines) if l.strip().startswith("## Canonical Evidence"))
        last = start
        for i in range(start, len(lines)):
            if lines[i].startswith("|"):
                last = i
            elif lines[i].strip().startswith("## ") and i > start:
                break
        lines.insert(last + 1, "| - | - | - | - | - | - |")
        card.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        out = self.check(clone, "doc/tasks/FEA-11-HOST-AUTH-2.md")
        self.assertIn("Canonical Evidence 行结构非法", out)

    def test_wildcard_entry_is_rejected(self):
        clone = self.clone()
        entry = self.entry_for(clone, "EV-11")
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
        entry = self.entry_for(clone, "EV-11")
        second = dict(entry, id="EXC-TEST-EV-11-B")
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
