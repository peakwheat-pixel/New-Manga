"""Headless software smoke checks (TOOL-SOFTWARE-SMOKE-1).

The package is intentionally a *tool*, not production code: it imports the real
production assembly, the real AppContainer sandbox and the real Core stdio
server, but it never changes ``src/**`` or a shared contract.
"""

from __future__ import annotations

__version__ = "1"
