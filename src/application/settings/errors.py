"""Settings-domain errors (TASK-009)."""

from __future__ import annotations


class SettingsError(ValueError):
    """Invalid settings input (unknown key/scope combination)."""


class UnresolvedCapabilityError(SettingsError):
    """No enabled binding covers the requested capability in scope.

    Raised instead of guessing a provider: the pipeline must surface the
    missing binding to the user (D06 §51 forbids arbitrary fallbacks).
    """

    def __init__(self, capability: str, message: str) -> None:
        super().__init__(message)
        self.capability = capability
