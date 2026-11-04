"""Grant/strict-handle component evidence, not a Host IPC/UI test."""
import base64
import copy
import hashlib
import hmac
import json
import os
from pathlib import Path
import unittest
import uuid

from application.importing.referenced.errors import SourceImportError
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry

ROOT = Path(__file__).resolve().parents[2]


def b64(data): return base64.urlsafe_b64encode(data).decode().rstrip("=")


class SourceGrantTests(unittest.TestCase):
    def setUp(self):
        self.folder=ROOT/"verification"/"FEA-09"/"grant-component"/uuid.uuid4().hex
        self.folder.mkdir(parents=True)
        self.path=self.folder/"source.bin";self.path.write_bytes(b"synthetic source")
        self.now=1000.
        self.registry=SourceReadGrantRegistry(clock=lambda:self.now)

    def payload(self, generation=1):
        info=self.path.stat()
        p=dict(grant_id="grant-"+uuid.uuid4().hex,session_id="session",operation="source-read",
               scope_class="user-source",registry_id="registry",generation=generation,expires_at=self.now+100,
               budget=dict(max_bytes=1024,max_decode_bytes=1024,max_entries=10),
               scope=dict(source_id="source",version="version",rendition=dict(decoder="image",scale=1,params_digest="0"*64),
                          entries=[dict(entry_key="entry",entry_id=None,locator=self.path.name,ordinal=0,path=str(self.path),
                          facts=dict(volume_serial=int(info.st_dev) & 0xFFFFFFFF,file_id=int(info.st_ino) & ((1<<53)-1),size=info.st_size,
                                     sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()))]))
        return self.sign(p)

    def sign(self,p):
        fields={k:v for k,v in p.items() if k not in ("signing_key","signature")}
        fields["expires_at"]=f'{p["expires_at"]:.6f}'
        key=b"x"*32
        p["signing_key"]=b64(key)
        p["signature"]=b64(hmac.new(key,json.dumps(fields,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(),hashlib.sha256).digest())
        return p

    def assert_code(self,code,call):
        with self.assertRaises(SourceImportError) as caught:call()
        self.assertEqual(code,caught.exception.code)

    def test_signature_priority_and_entry_budget(self):
        p=self.payload();p["signature"]="bad";p["expires_at"]=0
        self.assert_code("REF_SIGNATURE_INVALID",lambda:self.registry.register(p))
        p=self.payload();p["budget"]["max_entries"]=1;p["scope"]["entries"]*=2;self.sign(p)
        self.assert_code("SOURCE_BUDGET_EXCEEDED",lambda:self.registry.register(p))

    def test_all_four_scope_dimensions_are_bound(self):
        p=self.payload();self.registry.register(p)
        self.registry.verify_scope(p["grant_id"],**p["scope"])
        for field in ("source_id","version","rendition","entries"):
            changed=copy.deepcopy(p["scope"])
            changed[field] = "other" if field in ("source_id","version") else {} if field=="rendition" else []
            self.assert_code("SOURCE_ACCESS_DENIED",lambda:self.registry.verify_scope(p["grant_id"],**changed))

    def test_generation_revoke_and_eof(self):
        p=self.payload();self.registry.register(p)
        self.registry.revoke_grants("registry",2,[])
        self.assert_code("SOURCE_GRANT_REVOKED",lambda:self.registry.verify_before_commit(p["grant_id"]))
        fresh=self.payload(2);self.registry.register(fresh)
        self.registry.verify_before_commit(fresh["grant_id"])
        self.registry.revoke_all_for_session()
        self.assert_code("SOURCE_GRANT_REVOKED",lambda:self.registry.verify_before_commit(fresh["grant_id"]))
        self.assert_code("SOURCE_GRANT_REVOKED",lambda:self.registry.register(self.payload(2)))

    def test_expiry_and_changed_identity_refuse_commit(self):
        p=self.payload();self.registry.register(p)
        self.registry.verify_before_commit(p["grant_id"])
        self.path.write_bytes(b"different bytes")
        self.assert_code("FILE_IDENTITY_CHANGED",lambda:self.registry.verify_before_commit(p["grant_id"]))
        self.now+=101
        self.assert_code("SOURCE_GRANT_EXPIRED",lambda:self.registry.resolve(p["grant_id"]))

    def test_strict_handle_blocks_replacement_until_commit_ends(self):
        p=self.payload();self.registry.register(p)
        with self.registry.commit_guard(p["grant_id"]):
            if os.name == "nt":
                with self.assertRaises(OSError):self.path.rename(self.folder/"replaced.bin")
        replacement=self.folder/"replaced.bin";self.path.rename(replacement)
        self.path.write_bytes(b"synthetic source")
        self.assert_code("FILE_IDENTITY_CHANGED",lambda:self.registry.verify_before_commit(p["grant_id"]))


    def test_import_binding_requires_exact_source_version_entry(self):
        """R1-I002: resolve only honors the grant that imported this binding."""
        p=self.payload();self.registry.register(p);g=p["grant_id"]
        self.registry.bind_imported_entry(g,"src-1","sv-1","se-1")
        found,resolved=self.registry.find_bound_for_source("src-1","sv-1","se-1")
        self.assertEqual(g,found)
        self.assertEqual(g,resolved.grant_id)
        for args in (("src-1","sv-2","se-1"),("src-1","sv-1","se-2"),
                     ("src-2","sv-1","se-1")):
            self.assert_code("SOURCE_ACCESS_DENIED",
                             lambda a=args:self.registry.find_bound_for_source(*a))
        self.registry.revoke_grants("registry",2,[])
        self.assert_code("SOURCE_ACCESS_DENIED",
                         lambda:self.registry.find_bound_for_source("src-1","sv-1","se-1"))



    def test_unbound_grant_cannot_resolve_and_wrong_version_is_refused(self):
        """P2-3: a live grant with no import binding never authorizes a page."""
        p = self.payload()
        self.registry.register(p)
        self.assert_code(
            "SOURCE_ACCESS_DENIED",
            lambda: self.registry.find_bound_for_source("source-1", "version-1", "entry-1"),
        )
        self.registry.bind_imported_entry(p["grant_id"], "source-1", "version-1", "entry-1")
        found, _resolved = self.registry.find_bound_for_source("source-1", "version-1", "entry-1")
        self.assertEqual(p["grant_id"], found)
if __name__=="__main__":unittest.main()
