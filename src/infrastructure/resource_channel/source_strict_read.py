"""Strict source lease: verify and read through one non-writable handle."""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import stat

from application.importing.referenced.errors import SourceImportError


@contextmanager
def source_lease(path, facts, max_bytes):
    from application.importing.referenced.scanner import _reject_reparse
    target = Path(path)
    if not target.is_absolute():
        raise SourceImportError("SOURCE_ACCESS_DENIED", "source path is not absolute")
    if facts.size > max_bytes:
        raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "source read budget exceeded")
    _reject_reparse(target)
    if os.name == "nt":
        from infrastructure.resource_channel import handle_resolver as hr
        handle = None
        try:
            handle = hr._open_read_handle(target)
            identity = hr._identity_of(handle)
            final = hr._normalized(hr._display_path(hr._final_path_of(handle)))
            if (identity != (facts.volume_serial & 0xffffffff, facts.file_id)
                or hr._size_of(handle) != facts.size
                or hr._attributes_of(handle) & (hr.FILE_ATTRIBUTE_REPARSE_POINT | hr.FILE_ATTRIBUTE_DIRECTORY)
                or final != hr._normalized(str(target))):
                raise SourceImportError("FILE_IDENTITY_CHANGED", "source identity changed")
            data = hr._read_all_through(handle)
            if len(data) != facts.size or hashlib.sha256(data).hexdigest() != facts.sha256:
                raise SourceImportError("FILE_IDENTITY_CHANGED", "source digest changed")
            if hr._identity_of(handle) != identity or hr._size_of(handle) != facts.size:
                raise SourceImportError("FILE_IDENTITY_CHANGED", "source identity changed")
            yield data
        except SourceImportError:
            raise
        except (OSError, hr.TypedResourceChannelError) as error:
            raise SourceImportError("SOURCE_ACCESS_DENIED", "strict source lease unavailable") from error
        finally:
            if handle is not None:
                hr._k32.CloseHandle(handle)
    else:
        try:
            with target.open("rb") as stream:
                info = os.fstat(stream.fileno())
                if (not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino, info.st_size)
                    != (facts.volume_serial, facts.file_id, facts.size)):
                    raise SourceImportError("FILE_IDENTITY_CHANGED", "source identity changed")
                data = stream.read(max_bytes + 1)
                if len(data) != facts.size or hashlib.sha256(data).hexdigest() != facts.sha256:
                    raise SourceImportError("FILE_IDENTITY_CHANGED", "source digest changed")
                yield data
        except OSError as error:
            raise SourceImportError("SOURCE_ACCESS_DENIED", "strict source lease unavailable") from error

def read_verified_bytes(path, facts, max_bytes):
    """Read one granted file through the strict lease (single verified stream)."""
    with source_lease(path, facts, max_bytes) as data:
        return data
