"""Exercise the real governance checker against isolated authority-document mutations."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent / (ROOT.name + ".workspace") / "agent-output" / "codex"
STATIC = (
    "AGENTS.md", "doc/00_INDEX.md", "doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md",
    "doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
    "doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md",
    "doc/STATUS.md", "doc/REBASELINE_PLAN.md", "doc/09_COLLABORATION.md",
    "doc/WORKSPACE_GOVERNANCE.md", "doc/tasks/README.md", "doc/TASK_LEDGER.md",
    "doc/templates/TASK.md", "doc/templates/REVIEW.md", "doc/templates/HANDOFF.md",
)
SENTINEL = "Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource"
LINK = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)\s]+)")


class ArchitectureAssertions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="fea-assertions-", dir=WORKSPACE)
        cls.fixture = Path(cls.temp.name)
        for relative in (*STATIC, "doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md",
                         "tools/governance/check.ps1"):
            target = cls.fixture / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = ROOT / relative
            if relative == "tools/governance/check.ps1" and os.environ.get("FEA_CHECKER_SOURCE"):
                source = Path(os.environ["FEA_CHECKER_SOURCE"])
            shutil.copy2(source, target)
        # The ledger check counts current task files. Copy exactly that input set.
        for source in (ROOT / "doc/tasks").glob("*.md"):
            shutil.copy2(source, cls.fixture / "doc/tasks" / source.name)

        # The real checker checks selected documents' link targets for existence,
        # but does not read target contents. Create only those target placeholders.
        selected = list(STATIC) + ["doc/tasks/REALUSE-DATA-SAFETY-6.md"]
        for relative in selected:
            document = cls.fixture / relative
            for raw in LINK.findall(document.read_text(encoding="utf-8-sig")):
                link = unquote(re.split(r"[?#]", raw, maxsplit=1)[0])
                if not link or re.match(r"^(https?|mailto|codex)://", link, re.I):
                    continue
                target = (document.parent / link).resolve()
                if not target.is_relative_to(cls.fixture.resolve()):
                    raise AssertionError(f"fixture link escapes isolated root: {relative}: {raw}")
                original = ROOT / target.relative_to(cls.fixture.resolve())
                if target.exists():
                    continue
                if original.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.touch()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_checker(self):
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(self.fixture / "tools/governance/check.ps1")],
            cwd=self.fixture, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        return result.returncode, result.stdout + result.stderr

    def mutate(self, relative, change, expected_success):
        path = self.fixture / relative
        original = path.read_bytes()
        try:
            text = original.decode("utf-8-sig")
            changed = change(text)
            self.assertNotEqual(changed, text, "mutation must actually change its input")
            path.write_text(changed, encoding="utf-8", newline="\n")
            code, output = self.run_checker()
            self.assertEqual(code == 0, expected_success, output)
        finally:
            path.write_bytes(original)

    def test_current_authorities_pass(self):
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_stale_or_incidental_sentinel_is_rejected(self):
        field = f"Architecture sentinel: `{SENTINEL}`"
        variants = {
            "comment_only": f"<!-- {field} -->",
            "unclosed_comment": f"<!--\n{field}",
            "wrong_with_history": f"Architecture sentinel: React + Tauri (history: {SENTINEL})",
            "duplicate": field + "\nArchitecture sentinel: React + Tauri",
            "fenced_only": "```text\n" + field + "\n```",
        }
        for name, replacement in variants.items():
            with self.subTest(name=name):
                self.mutate("doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
                            lambda text: text.replace(field, replacement, 1), False)

    def test_index_and_historical_sentinel_require_exact_fields(self):
        historic = "Windows + C#/.NET + Avalonia + Python Core + SQLite + Managed Copy"
        cases = (
            ("doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md",
             f"Target architecture sentinel: `{historic}`",
             f"Target architecture sentinel: React + Tauri (history: {historic})"),
            ("doc/00_INDEX.md", f"**当前架构哨兵（机器校验字段）**：`{SENTINEL}`",
             f"**当前架构哨兵（机器校验字段）**：React (history: {SENTINEL})"),
        )
        for relative, original, replacement in cases:
            with self.subTest(relative=relative):
                self.mutate(relative, lambda text: text.replace(original, replacement, 1), False)

    def test_index_requires_current_authority_links(self):
        for name, target in (("AD-003", "AD-003_REFERENCED_SOURCE_ARCHITECTURE.md"),
                             ("ADJ-001", "contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md")):
            def replace_row(text):
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith(f"| [{name}]("):
                        lines[i] = f"| [{name}]({target}) | HISTORICAL | historical mention |"
                        return "\n".join(lines) + "\n"
                raise AssertionError(f"missing {name} row")
            with self.subTest(name=name):
                self.mutate("doc/00_INDEX.md", replace_row, False)

    def test_agents_requires_actual_current_architecture(self):
        actual = "Windows / C# .NET + Avalonia / Python Core / SQLite / ReferencedSource"
        self.mutate("AGENTS.md", lambda text: text.replace(
            actual, "React + Tauri（历史名称 ReferencedSource）", 1), False)

    def test_agents_requires_real_authority_link(self):
        self.mutate("AGENTS.md", lambda text: text.replace(
            "[AD-003 存储架构补充决策](doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)",
            "历史说明 AD-003_REFERENCED_SOURCE_ARCHITECTURE.md", 1), False)

    def test_agents_rejects_link_in_code_or_image(self):
        pattern = r"(\[AD-003[^\]]*\]\(doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE\.md\))"
        variants = {
            "code_span": lambda link: f"`{link}`",
            "double_code_span": lambda link: f"``{link}``",
            "image": lambda link: f"!{link}",
            "escaped_link": lambda link: f"\\{link}",
            "html_code": lambda link: f"<code>{link}</code>",
            "html_pre_attributes": lambda link: f'<pre class="sample">{link}</pre>',
            "html_attribute": lambda link: f'<span title="{link}">example</span>',
            "html_attribute_with_gt": lambda link: f'<span title="> {link}">example</span>',
            "nested_image_alt": lambda link: f"![example {link}](cover.png)",
        }
        for name, wrap in variants.items():
            with self.subTest(name=name):
                self.mutate("AGENTS.md", lambda text: re.sub(
                    pattern, lambda m: wrap(m.group(1)), text, count=1), False)

    def test_html_code_blocks_cannot_declare_sentinel(self):
        field = f"Architecture sentinel: `{SENTINEL}`"
        variants = {
            "pre": f"<pre>\n{field}\n</pre>",
            "code": f"<code>\n{field}\n</code>",
            "uppercase_with_attributes": f'<PRE class="sample">\n{field}\n</PRE>',
            "multiline_open": f'<pre\n class="sample">\n{field}\n</pre>',
        }
        for name, replacement in variants.items():
            with self.subTest(name=name):
                self.mutate("doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
                            lambda text: text.replace(field, replacement, 1), False)

    def _cross_line(self, relative, needle, replacement=None):
        def change(text):
            base = text.replace("\r\n", "\n")
            index = base.index(needle)
            line_start = base.rfind("\n", 0, index) + 1
            line_end = base.find("\n", index)
            line = base[line_start:line_end]
            if replacement is not None:
                line = line.replace(needle, replacement, 1)
            return base[:line_start] + "`跨行示例\n" + line + "`\n" + base[line_end + 1:]
        self.mutate(relative, change, False)

    def test_cross_line_code_span_link_is_rejected(self):
        self._cross_line("AGENTS.md", "当前唯一继续演进的产品架构为")

    def test_cross_line_code_span_image_is_rejected(self):
        link = "[AD-003 存储架构补充决策](doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)"
        image = "![AD-003 图](doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)"
        self._cross_line("AGENTS.md", link, image)

    def test_cross_line_code_span_sentinel_is_rejected(self):
        self._cross_line("doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
                         f"Architecture sentinel: `{SENTINEL}`")

    def test_cross_line_code_span_in_prose_is_not_flagged(self):
        self.mutate("AGENTS.md", lambda text: text + "\n\n历史示例：`跨行\n代码示例`。\n", True)

    def test_historical_inline_code_does_not_hide_real_link(self):
        fake = "`[AD-003 example](doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)`"
        self.mutate("AGENTS.md", lambda text: text.replace(
            "与 [AD-003", f"与 {fake} [AD-003", 1), True)

    def test_historical_html_examples_do_not_hide_real_sentinel(self):
        field = f"Architecture sentinel: `{SENTINEL}`"
        variants = ("历史示例 `<pre>` 不表示本文开始代码块。\n", "```text\n<pre>\n```\n")
        for example in variants:
            with self.subTest(example=example):
                self.mutate("doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
                            lambda text: text.replace(field, example + field, 1), True)

    def test_duplicate_authority_row_is_rejected(self):
        def duplicate(text):
            lines = text.splitlines()
            row = next(line for line in lines if line.startswith("| [AD-003]("))
            return text + "\n" + row + "\n"
        self.mutate("doc/00_INDEX.md", duplicate, False)

    def test_historical_prose_is_not_a_conflicting_assertion(self):
        self.mutate("doc/STATUS.md", lambda text: text +
                    "\n历史记录：当前目标架构为 React + TypeScript；该表述已被取代。\n", True)


if __name__ == "__main__":
    unittest.main()
