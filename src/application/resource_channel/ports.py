"""Resource channel application-layer ports (M2-RC1).

Kept inside the resource_channel module on purpose: the Task's allowed paths
do not extend to ``src/ports/**``.
"""

from __future__ import annotations

from typing import Protocol

from application.resource_channel.dto import ResourceFacts


class IssueTimeFactSource(Protocol):
    """Captures issue-time facts for a file the Core is about to authorise.

    The production adapter opens the file once and reads identity/size/digest
    through that handle (M2-S2 semantics, ``capture_facts``)."""

    def capture_facts(self, absolute_path: str) -> ResourceFacts: ...


class Clock(Protocol):
    def __call__(self) -> float: ...
