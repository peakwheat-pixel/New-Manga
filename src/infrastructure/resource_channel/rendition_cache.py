"""Bounded, disposable decoded renditions (C-14 SC-S14..17/C-15 2.7).

This store is not a source reader. Callers must hold a verified source lease
and supply a decoder; raw source bytes may not be published through this API.
Source identity columns are never written here.
"""
from contextlib import contextmanager
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import uuid

from application.importing.referenced.errors import SourceImportError

KINDS = frozenset({"thumbnail", "tile", "pdf_raster", "archive_page", "page_preview"})


def rendition_key(source_id, version_id, entry_id, kind, decoder, decoder_version, params):
    if kind not in KINDS:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "raw source is not a rendition")
    material = json.dumps([source_id, version_id, entry_id, kind, decoder,
                           decoder_version, params], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode()).hexdigest()


class RenditionCache:
    def __init__(self, *, data_root, connection, max_bytes=512 * 1024 * 1024,
                 max_file_bytes=256 * 1024 * 1024, max_decodes=2, clock=None):
        if any(isinstance(n, bool) or not isinstance(n, int) or n <= 0
               for n in (max_bytes, max_file_bytes, max_decodes)):
            raise ValueError("cache limits must be positive integers")
        self._root = Path(data_root) / "derived" / "source-renditions"
        self._reject_links(self._root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._conn = connection
        self._max_bytes = max_bytes
        self._max_file_bytes = min(max_file_bytes, max_bytes)
        self._slots = threading.BoundedSemaphore(max_decodes)
        self._condition = threading.Condition(threading.RLock())
        self._inflight = set()
        self._preflight_pins = Counter()
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        # The Core owns this connection/namespace exclusively at construction.
        # A crashed process cannot leave a live reader; clear only ephemeral refs.
        self._conn.execute("UPDATE rendition_cache SET active_references=0")
        self._conn.commit()
        self._recover()

    @staticmethod
    def _reject_links(path):
        from application.importing.referenced.scanner import _reject_reparse
        probe = Path(path)
        while not probe.exists() and probe != probe.parent:
            probe = probe.parent
        _reject_reparse(probe.absolute())

    def _path(self, key):
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise SourceImportError("SOURCE_ACCESS_DENIED", "invalid rendition key")
        path = self._root / (key + ".bin")
        self._reject_links(path)
        return path

    def _recover(self):
        # Only our generated filenames; never sweep any other derived channel.
        with self._condition:
            for path in self._root.iterdir():
                if path.is_symlink():
                    raise SourceImportError("SOURCE_ACCESS_DENIED", "cache namespace is redirected")
                if path.name.startswith("pending-") and path.suffix == ".tmp":
                    path.unlink()
            for row in self._conn.execute("SELECT cache_key,rel_path,size_bytes,content_digest FROM rendition_cache").fetchall():
                key, rel_path, size, digest = row
                try:
                    path = self._path(key)
                    data = path.read_bytes()
                    valid = (rel_path == "source-renditions/" + key + ".bin"
                             and len(data) == size and hashlib.sha256(data).hexdigest() == digest)
                except (OSError, SourceImportError):
                    valid = False
                if not valid:
                    self._drop(key)
            known = {r[0] + ".bin" for r in self._conn.execute("SELECT cache_key FROM rendition_cache")}
            for path in self._root.glob("*.bin"):
                stem = path.stem
                if len(stem) == 64 and all(c in "0123456789abcdef" for c in stem) and path.name not in known:
                    path.unlink()
            self._evict(0)
            self._conn.commit()

    def _drop(self, key):
        self._path(key).unlink(missing_ok=True)
        self._conn.execute("DELETE FROM rendition_cache WHERE cache_key=?", (key,))

    def _evict(self, incoming):
        total = self._conn.execute("SELECT coalesce(sum(size_bytes),0) FROM rendition_cache").fetchone()[0]
        candidates = self._conn.execute(
            "SELECT cache_key,size_bytes FROM rendition_cache WHERE active_references=0 ORDER BY last_used_at ASC,size_bytes DESC,cache_key ASC").fetchall()
        for key, size in candidates:
            if total + incoming <= self._max_bytes:
                break
            if key in self._preflight_pins or key in self._inflight:
                continue
            self._drop(key)
            total -= size
        if total + incoming > self._max_bytes:
            raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "active renditions exhaust cache capacity")

    @contextmanager
    def preflight(self, keys):
        # Keep deletion previews stable while the caller holds its snapshot.
        with self._condition:
            keys = tuple(keys)
            self._preflight_pins.update(keys)
        try:
            yield
        finally:
            with self._condition:
                self._preflight_pins.subtract(keys)
                self._preflight_pins += Counter()
                self._condition.notify_all()

    @contextmanager
    def acquire(self, *, source_id, version_id, entry_id, kind, decoder,
                decoder_version, params, width, height, max_decode_bytes, produce):
        if (isinstance(width, bool) or isinstance(height, bool) or width <= 0 or height <= 0
            or width * height * 4 > max_decode_bytes):
            raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "rendition decode budget exceeded")
        key = rendition_key(source_id, version_id, entry_id, kind, decoder, decoder_version, params)
        path = self._path(key)
        with self._condition:
            while key in self._inflight:
                self._condition.wait()
            self._inflight.add(key)
        try:
            with self._condition:
                row = self._conn.execute("SELECT size_bytes,content_digest FROM rendition_cache WHERE cache_key=?", (key,)).fetchone()
                data = None
                if row:
                    try:
                        candidate = path.read_bytes()
                        if len(candidate) == row[0] and hashlib.sha256(candidate).hexdigest() == row[1]:
                            data = candidate
                    except OSError:
                        pass
                    if data is None:
                        active = self._conn.execute("SELECT active_references FROM rendition_cache WHERE cache_key=?", (key,)).fetchone()[0]
                        if active:
                            raise SourceImportError("SOURCE_ACCESS_DENIED", "active rendition is corrupt")
                        self._drop(key)
            if data is None:
                with self._slots:
                    data = produce()
                if not isinstance(data, bytes) or not data or len(data) > self._max_file_bytes:
                    raise SourceImportError("SOURCE_BUDGET_EXCEEDED", "rendition exceeds file budget")
                with self._condition:
                    self._evict(len(data))
                    temporary = self._root / ("pending-" + uuid.uuid4().hex + ".tmp")
                    try:
                        with temporary.open("xb") as stream:
                            stream.write(data)
                            stream.flush()
                            os.fsync(stream.fileno())
                        os.replace(temporary, path)
                        now = self._clock()
                        params_digest = hashlib.sha256(json.dumps(params, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                        self._conn.execute(
                            "INSERT INTO rendition_cache(cache_key,source_id,version_id,entry_id,rendition_kind,decoder_name,decoder_version,params_digest,rel_path,size_bytes,content_digest,created_at,last_used_at,active_references) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                            (key,source_id,version_id,entry_id,kind,decoder,decoder_version,params_digest,
                             "source-renditions/" + key + ".bin",len(data),hashlib.sha256(data).hexdigest(),now,now))
                        self._conn.commit()
                    finally:
                        temporary.unlink(missing_ok=True)
            with self._condition:
                self._conn.execute("UPDATE rendition_cache SET active_references=active_references+1,last_used_at=? WHERE cache_key=?", (self._clock(),key))
                self._conn.commit()
        finally:
            with self._condition:
                self._inflight.discard(key)
                self._condition.notify_all()
        try:
            yield data
        finally:
            with self._condition:
                self._conn.execute("UPDATE rendition_cache SET active_references=active_references-1 WHERE cache_key=? AND active_references>0", (key,))
                self._conn.commit()
                self._condition.notify_all()
