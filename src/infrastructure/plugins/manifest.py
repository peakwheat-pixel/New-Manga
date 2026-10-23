"""Local-directory plugin manifest v1 (PLUGIN-RUNTIME-1, design §4.2).

Fail-closed by construction: every rejection is a typed :class:`ManifestError`
whose ``code`` is a stable, non-sensitive identifier (the audit ledger stores
the code + a short detail, never payloads or absolute paths outside the
plugin root).

Security boundary (review r1 P1-1, honest downgrade): a plugin is **trusted
local code**. ``permissions: []`` means the Core grants it NO capability
handles -- no Core objects, no database, no model or credentials, no
configured paths, no network configuration -- and the hook subprocess runs
with a minimal environment and ``-I``. It is NOT an OS-level sandbox: the
plugin process still runs with the user's OS rights, so a malicious plugin can
still open files or sockets itself. The first release therefore documents
"trusted code + zero granted capabilities"; an OS sandbox
(PLUGIN-RUNTIME-SANDBOX-1) is a separate, unauthorized follow-up.

Frozen field set (§4.2):

=== ====== ==== ========================================================
id     string yes ``[a-z0-9-]{3,64}``, must equal the directory name
name   string yes display name, <= 80 chars
version string yes semver ``MAJOR.MINOR.PATCH``
entry  string yes relative ``.py`` path inside the plugin directory
hooks  array  yes subset of :data:`HOOK_NAMES`
permissions array yes subset of :data:`ALLOWED_PERMISSIONS`; the first
                     release only loads ``permissions: []`` (design §4.3)
min_app_version string no lower bound is refused
description string no <= 200 chars
=== ====== ==== ========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

#: Design §4.4 — the frozen six-hook contract (C-3 froze the names; this
#: release wires `before_*`/`after_*` pairs for detect / OCR / export).
HOOK_NAMES: tuple[str, ...] = (
    "before_detect",
    "after_detect",
    "before_ocr",
    "after_ocr",
    "before_export",
    "after_export",
)

#: Design §4.3 — the permission vocabulary (closed). The first release only
#: loads plugins that declare ``permissions: []``.
ALLOWED_PERMISSIONS: tuple[str, ...] = (
    "files_read",
    "files_write",
    "network",
    "model",
)

#: `before_*` hooks may return an override object; `after_*` are read-only.
WRITABLE_HOOKS: tuple[str, ...] = (
    "before_detect",
    "before_ocr",
    "before_export",
)

#: §4.2 frozen field set: any other top-level key rejects the manifest
#: (review r1 P1-2: unknown keys were silently accepted before).
_ALLOWED_KEYS = frozenset(
    {
        "id",
        "name",
        "version",
        "entry",
        "hooks",
        "permissions",
        "min_app_version",
        "description",
    }
)

_ID_PATTERN = re.compile(r"^[a-z0-9-]{3,64}$")
_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_MAX_MANIFEST_BYTES = 64 * 1024
_MAX_NAME_CHARS = 80
_MAX_DESCRIPTION_CHARS = 200


class ManifestError(ValueError):
    """A typed manifest rejection. ``code`` is stable audit material."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    entry: str
    hooks: tuple[str, ...]
    permissions: tuple[str, ...]
    description: str
    min_app_version: str | None
    root: Path

    @property
    def entry_path(self) -> Path:
        return self.root / self.entry


def _require_str(raw: dict, key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError("PLUGIN_MANIFEST_INVALID", f"missing or empty {key}")
    return value


def _parse_semver(value: str, key: str) -> tuple[int, int, int]:
    match = _VERSION_PATTERN.match(value)
    if not match:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", f"{key} is not semver: {value!r}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _string_array(raw: dict, key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError("PLUGIN_MANIFEST_INVALID", f"{key} must be a string array")
    return tuple(value)


def parse_manifest(plugin_root: Path, *, app_version: str) -> PluginManifest:
    """Validate one ``<plugin_root>/<plugin_id>/manifest.json``.

    Raises :class:`ManifestError` with a stable code for any drift; the
    caller records ``load_rejected`` and keeps the plugin unloaded.
    """

    if plugin_root.is_symlink():
        raise ManifestError(
            "PLUGIN_MANIFEST_INVALID", "plugin directory must not be a symlink"
        )
    root_resolved = plugin_root.resolve()
    manifest_path = plugin_root / "manifest.json"
    if not manifest_path.is_file():
        raise ManifestError("PLUGIN_MANIFEST_MISSING", "manifest.json not found")
    if not manifest_path.resolve().is_relative_to(root_resolved):
        raise ManifestError(
            "PLUGIN_MANIFEST_INVALID", "manifest.json escapes the plugin directory"
        )
    try:
        if manifest_path.stat().st_size > _MAX_MANIFEST_BYTES:
            raise ManifestError("PLUGIN_MANIFEST_INVALID", "manifest.json is too large")
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", f"invalid JSON: {error.msg}") from error
    except OSError as error:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", f"unreadable manifest: {error.strerror}") from error
    if not isinstance(raw, dict):
        raise ManifestError("PLUGIN_MANIFEST_INVALID", "manifest must be a JSON object")
    unknown_keys = sorted(set(raw) - _ALLOWED_KEYS)
    if unknown_keys:
        raise ManifestError(
            "PLUGIN_MANIFEST_INVALID",
            f"unknown manifest keys: {', '.join(unknown_keys)}",
        )

    plugin_id = _require_str(raw, "id")
    if not _ID_PATTERN.match(plugin_id):
        raise ManifestError("PLUGIN_MANIFEST_INVALID", "id must match [a-z0-9-]{3,64}")
    if plugin_id != plugin_root.name:
        raise ManifestError(
            "PLUGIN_ID_MISMATCH", f"id {plugin_id!r} does not match directory {plugin_root.name!r}"
        )

    name = _require_str(raw, "name")
    if len(name) > _MAX_NAME_CHARS:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", "name is too long")

    version = _require_str(raw, "version")
    _parse_semver(version, "version")

    entry = _require_str(raw, "entry")
    entry_relative = Path(entry)
    if entry_relative.is_absolute() or ".." in entry_relative.parts:
        raise ManifestError("PLUGIN_ENTRY_INVALID", "entry must be a relative path")
    if entry_relative.suffix != ".py":
        raise ManifestError("PLUGIN_ENTRY_INVALID", "entry must be a .py file")
    entry_path = (plugin_root / entry_relative).resolve()
    if not entry_path.is_relative_to(plugin_root.resolve()):
        raise ManifestError("PLUGIN_ENTRY_INVALID", "entry escapes the plugin directory")
    if not entry_path.is_file():
        raise ManifestError("PLUGIN_ENTRY_INVALID", "entry file does not exist")

    hooks = _string_array(raw, "hooks")
    unknown_hooks = [hook for hook in hooks if hook not in HOOK_NAMES]
    if unknown_hooks:
        raise ManifestError(
            "PLUGIN_UNKNOWN_HOOK", f"unknown hooks: {', '.join(sorted(unknown_hooks))}"
        )

    permissions = _string_array(raw, "permissions")
    unknown_permissions = [item for item in permissions if item not in ALLOWED_PERMISSIONS]
    if unknown_permissions:
        raise ManifestError(
            "PLUGIN_UNKNOWN_PERMISSION",
            f"unknown permissions: {', '.join(sorted(unknown_permissions))}",
        )
    if permissions:
        # Design §4.3 first-release limit: only permission-free plugins load.
        raise ManifestError(
            "PLUGIN_PERMISSIONS_UNSUPPORTED",
            "this release only loads plugins with permissions: []",
        )

    description_raw = raw.get("description", "")
    if description_raw is None:
        description = ""
    elif isinstance(description_raw, str):
        description = description_raw
    else:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", "description must be a string")
    if len(description) > _MAX_DESCRIPTION_CHARS:
        raise ManifestError("PLUGIN_MANIFEST_INVALID", "description is too long")

    min_app_version_raw = raw.get("min_app_version")
    min_app_version: str | None = None
    if min_app_version_raw is not None:
        if not isinstance(min_app_version_raw, str):
            raise ManifestError(
                "PLUGIN_MANIFEST_INVALID", "min_app_version must be a string"
            )
        if _parse_semver(min_app_version_raw, "min_app_version") > _parse_semver(
            app_version, "app_version"
        ):
            raise ManifestError(
                "PLUGIN_MIN_APP_VERSION",
                f"requires app >= {min_app_version_raw}",
            )
        min_app_version = min_app_version_raw

    return PluginManifest(
        plugin_id=plugin_id,
        name=name,
        version=version,
        entry=entry,
        hooks=hooks,
        permissions=permissions,
        description=description,
        min_app_version=min_app_version,
        root=plugin_root,
    )
