"""Cache component tests, no UI/system-IPC claim. Runnable without pytest."""
import hashlib
from pathlib import Path
import re
import sqlite3
import threading
import time
import unittest
import uuid

from application.importing.referenced.errors import SourceImportError
from infrastructure.resource_channel.rendition_cache import RenditionCache, rendition_key
from infrastructure.sqlite.schema import MIGRATION_V7_SQL

ROOT = Path(__file__).resolve().parents[2]


class RenditionCacheTests(unittest.TestCase):
    def setUp(self):
        self.evidence = ROOT / "verification" / "FEA-09" / "cache-component" / uuid.uuid4().hex
        self.evidence.mkdir(parents=True)
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        # Exact production cache DDL, isolated from unrelated source mutations.
        ddl = re.search(r"CREATE TABLE rendition_cache .*?;", MIGRATION_V7_SQL, re.S).group()
        self.conn.executescript(ddl)
        self.cache = RenditionCache(data_root=self.evidence, connection=self.conn,
                                    max_bytes=20, max_file_bytes=20, max_decodes=1, clock=lambda: "same-time")

    def tearDown(self):
        self.conn.close()

    def args(self, entry="e1", payload=b"rendered-1"):
        return dict(source_id="s",version_id="v",entry_id=entry,kind="page_preview",
                    decoder="test-renderer",decoder_version="1",params={},width=1,height=1,
                    max_decode_bytes=4,produce=lambda: payload)

    def test_key_changes_with_version_entry_decoder_and_parameters(self):
        base = ["s", "v", "e", "page_preview", "decoder", "1", {}]
        key = rendition_key(*base)
        for index, value in [(1,"v2"),(2,"e2"),(5,"2"),(6,{"scale":2})]:
            changed = list(base); changed[index] = value
            self.assertNotEqual(key, rendition_key(*changed))
        with self.assertRaises(SourceImportError):
            rendition_key("s","v","e","raw","decoder","1",{})

    def test_single_request_budget_precedes_decode(self):
        called = []
        args = self.args(); args.update(width=2,produce=lambda: called.append(True))
        with self.assertRaises(SourceImportError) as caught:
            with self.cache.acquire(**args): pass
        self.assertEqual("SOURCE_BUDGET_EXCEEDED", caught.exception.code)
        self.assertEqual([],called)

    def test_corruption_rebuild_and_crash_recovery(self):
        with self.cache.acquire(**self.args()) as data: self.assertEqual(b"rendered-1",data)
        path = next((self.evidence/"derived"/"source-renditions").glob("*.bin"))
        path.write_bytes(b"corrupt")
        calls = []
        args=self.args(); args["produce"]=lambda: calls.append(1) or b"repaired"
        with self.cache.acquire(**args) as data: self.assertEqual(b"repaired",data)
        self.assertEqual([1],calls)
        orphan=path.parent/("f"*64+".bin");orphan.write_bytes(b"orphan")
        pending=path.parent/"pending-crash.tmp";pending.write_bytes(b"partial")
        self.conn.execute("UPDATE rendition_cache SET active_references=5");self.conn.commit()
        cache=RenditionCache(data_root=self.evidence, connection=self.conn,max_bytes=20,max_file_bytes=20)
        self.assertFalse(orphan.exists());self.assertFalse(pending.exists())
        self.assertEqual(0,self.conn.execute("SELECT sum(active_references) FROM rendition_cache").fetchone()[0])
        with cache.acquire(**args) as data: self.assertEqual(b"repaired",data)

    def test_lru_tie_large_first_and_active_protection(self):
        with self.cache.acquire(**self.args("small",b"small")): pass
        with self.cache.acquire(**self.args("large",b"large-large")): pass
        with self.cache.acquire(**self.args("new",b"new-new-new")): pass
        self.assertEqual({"small","new"},{r[0] for r in self.conn.execute("SELECT entry_id FROM rendition_cache")})
        with self.cache.acquire(**self.args("new",b"new-new-new")):
            with self.cache.acquire(**self.args("four",b"four")): pass
            with self.assertRaises(SourceImportError):
                with self.cache.acquire(**self.args("huge",b"a"*20)):pass
            self.assertIn("new",{r[0] for r in self.conn.execute("SELECT entry_id FROM rendition_cache")})

    def test_preflight_pin_and_concurrent_decode_queue(self):
        key=rendition_key("s","v","pin","page_preview","test-renderer","1",{})
        with self.cache.acquire(**self.args("pin",b"a"*12)):pass
        with self.cache.preflight([key]):
            with self.assertRaises(SourceImportError):
                with self.cache.acquire(**self.args("overflow",b"b"*12)):pass
        active=0;peak=0;lock=threading.Lock();errors=[]
        def produce():
            nonlocal active,peak
            with lock: active+=1;peak=max(peak,active)
            time.sleep(.02)
            with lock:active-=1
            return b"x"
        def request(index):
            try:
                args=self.args(str(index));args["produce"]=produce
                with self.cache.acquire(**args):pass
            except Exception as error:errors.append(error)
        threads=[threading.Thread(target=request,args=(i,)) for i in range(3)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(5)
        self.assertFalse(any(t.is_alive() for t in threads));self.assertEqual([],errors);self.assertEqual(1,peak)


if __name__ == "__main__": unittest.main()
