"""Physical source identity normalization (C-16 §3 / C-17 §5).

The same physical file must present one identity everywhere: scanner facts,
the grant scope, the Windows handle probe, the strict read lease and the
import scope check. Raw NTFS file indices are 64-bit unsigned and can exceed
SQLite INTEGER / the wire's representable range, so every producer and every
comparator calls :func:`normalize_identity` — never the raw ``st_ino``.

Normalization is idempotent: applying it twice yields the same pair.
"""

from __future__ import annotations

#: Volume serial number fits the 32-bit value the Windows BY_HANDLE probe
#: returns (``dwVolumeSerialNumber``).
_VOLUME_MASK = 0xFFFFFFFF

#: File indices cross the wire as the C-17 ``N``/``G`` integer family; 53
#: bits keeps every value exactly representable (2**53 - 1 max).
_FILE_MASK = (1 << 53) - 1


def normalize_identity(
    volume_serial: int, file_id: int
) -> tuple[int, int]:
    """The single physical identity pair used by facts/grants/reads/storage."""
    return (int(volume_serial) & _VOLUME_MASK, int(file_id) & _FILE_MASK)
