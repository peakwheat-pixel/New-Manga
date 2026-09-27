"""RC2-AC2 (F-05): sidecar import isolation.

The sidecar entry (``python -m infrastructure.resource_channel.host_bridge``)
must load only the modules the resource channel needs. Importing the
``infrastructure`` package must not drag in the filesystem/sqlite adapters
(and through them ``domain.books``), so future heavyweight imports added to
those packages cannot break the sidecar or widen its attack/loader surface.

Pre-fix evidence: ``verification/M2-RC2/raw/sidecar-import-before-fix.log``
recorded the sidecar transitively loading ``infrastructure.filesystem``,
``infrastructure.sqlite``, ``infrastructure.sqlite.reading_export`` and
``domain.books.entities``. These tests run the import in a clean subprocess
(the pytest process itself has already imported the packages), capture the
loaded-module set, and gate on a whitelist.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

#: Everything the resource-channel sidecar is allowed to load from the
#: project tree (any other ``infrastructure``/``application``/``domain``
#: module is a isolation violation).
_ALLOWED_PREFIXES = (
    "application",
    "infrastructure",
)
#: Adapters that must NOT load for the sidecar entry (F-05 isolation gate).
_FORBIDDEN_MODULES = (
    "infrastructure.filesystem",
    "infrastructure.sqlite",
    "infrastructure.sqlite.reading_export",
    "domain",
    "domain.books",
    "domain.books.entities",
)

_DUMP_SNIPPET = (
    "import sys, json; "
    "import infrastructure.resource_channel.host_bridge; "
    "print(json.dumps(sorted(sys.modules)))"
)


def _loaded_modules(entry: str) -> list[str]:
    completed = subprocess.run(
        [sys.executable, "-c", entry],
        capture_output=True,
        text=True,
        cwd=SRC_ROOT,
        timeout=120,
        check=True,
    )
    return json.loads(completed.stdout.strip().splitlines()[-1])


class TestSidecarImportIsolation:
    def test_host_bridge_entry_loads_no_unrelated_adapters(self):
        modules = _loaded_modules(_DUMP_SNIPPET)
        project_modules = [
            module
            for module in modules
            if module.split(".")[0] in _ALLOWED_PREFIXES or module.split(".")[0] == "domain"
        ]
        forbidden = sorted(set(project_modules) & set(_FORBIDDEN_MODULES))
        assert forbidden == [], (
            f"sidecar entry loaded unrelated modules: {forbidden}; "
            f"full project set: {project_modules}"
        )

    def test_host_bridge_entry_project_module_whitelist(self):
        modules = _loaded_modules(_DUMP_SNIPPET)
        project_modules = [
            module
            for module in modules
            if module.split(".")[0] in _ALLOWED_PREFIXES
        ]
        for module in project_modules:
            assert module in (
                "application",
                "application.resource_channel",
                "application.resource_channel.dto",
                "application.resource_channel.service",
                "infrastructure",
                "infrastructure.resource_channel",
                "infrastructure.resource_channel.catalog_store",
                "infrastructure.resource_channel.handle_resolver",
                "infrastructure.resource_channel.host_bridge",
                "infrastructure.resource_channel.scope",
            ), f"unexpected project module loaded by the sidecar entry: {module}"

    def test_catalog_loader_entry_loads_no_unrelated_adapters(self):
        entry = (
            "import sys, json; "
            "import infrastructure.resource_channel.catalog_loader; "
            "print(json.dumps(sorted(m for m in sys.modules if m.startswith(('infrastructure', 'domain')))))"
        )
        modules = _loaded_modules(entry)
        forbidden = sorted(set(modules) & set(_FORBIDDEN_MODULES))
        assert forbidden == [], f"catalog loader entry loaded unrelated modules: {forbidden}"

    def test_lazy_infrastructure_attribute_access_still_works(self):
        """Product call sites keep ``from infrastructure import sqlite`` (PEP
        562 lazy import) -- isolation must not break the existing consumers."""

        entry = (
            "import json; "
            "from infrastructure import sqlite; "
            "from infrastructure import filesystem; "
            "print(json.dumps(sorted(sqlite.__all__)))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", entry],
            capture_output=True,
            text=True,
            cwd=SRC_ROOT,
            timeout=120,
            check=True,
        )
        exported = json.loads(completed.stdout.strip().splitlines()[-1])
        assert "SqliteReadingProgressStore" in exported
