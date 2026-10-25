"""Trace embedded trees and inspect immutable copies of historical SQLite blobs."""
import collections
import ast
import hashlib
import json
import io
from pathlib import Path
import re
import sqlite3
import subprocess
import zlib

from PIL import Image

from scan_push_history import ROOT, git, inspect

EVIDENCE = ROOT / "audit/V1-FULL-AUDIT/evidence"
COPIES = Path("G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/push-materials")
SECRET_KEYS = {"api_key", "apikey", "password", "passwd", "access_token", "refresh_token",
               "auth_token", "client_secret", "secret", "credential"}


def parse_tree(payload):
    result, offset = [], 0
    while offset < len(payload):
        end = payload.index(b"\0", offset)
        mode, name = payload[offset:end].split(b" ", 1)
        oid = payload[end + 1:end + 21]
        if len(oid) != 20:
            raise ValueError("truncated tree object")
        result.append((mode.decode(), name.decode("utf-8", errors="replace"), oid.hex()))
        offset = end + 21
    return result


def secret_fields(value, counts):
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in SECRET_KEYS and item not in (None, "", False):
                counts[str(key).lower()] += 1
            secret_fields(item, counts)
    elif isinstance(value, list):
        for item in value:
            secret_fields(item, counts)


def fixture_hashes():
    source = git("show", "HEAD:src/bootstrap/acceptance_bridge.py").decode()
    tree = ast.parse(source)
    nodes = [node for node in tree.body if
             (isinstance(node, ast.FunctionDef) and node.name in {"_fixture_pixel", "_png_chunk", "synthetic_page_png"}) or
             (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in
              {"FIXTURE_PAGE_WIDTH", "FIXTURE_PAGE_HEIGHT", "FIXTURE_PAGE_COUNT"} for target in node.targets))]
    namespace = {"zlib": zlib}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "frozen-acceptance-fixture", "exec"), namespace)
    return {hashlib.sha256(namespace["synthetic_page_png"](index)).hexdigest()
            for index in range(namespace["FIXTURE_PAGE_COUNT"])}


def database_report(data, oid, expected_hashes=None):
    COPIES.mkdir(parents=True, exist_ok=True)
    path = COPIES / (oid + ".sqlite")
    if not path.exists():
        with path.open("xb") as handle:
            handle.write(data)
    if path.read_bytes() != data:
        raise ValueError("existing isolated database copy differs")
    counts, secrets, findings = collections.Counter(), collections.Counter(), []
    path_columns = collections.Counter()
    result = {"copy": str(path), "sha256": hashlib.sha256(data).hexdigest(),
              "header_journal_versions": list(data[18:20]), "tables": []}
    connection = sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("PRAGMA trusted_schema=OFF")
        result["quick_check"] = [row[0] for row in connection.execute("PRAGMA quick_check")]
        tables = connection.execute("SELECT name, sql FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        for name, sql in tables:
            if "CREATE VIRTUAL" in (sql or "").upper():
                result["tables"].append({"name": name, "status": "SKIPPED_VIRTUAL_TABLE"})
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = connection.execute("SELECT * FROM " + quoted)
            columns = [column[0] for column in cursor.description]
            rows = 0
            for row in cursor:
                rows += 1
                for column, value in zip(columns, row):
                    if column.lower() in SECRET_KEYS and value not in (None, "", False):
                        secrets[column.lower()] += 1
                    if not isinstance(value, str):
                        continue
                    counts["text_cells"] += 1
                    if re.search(r"(?i)(?:[a-z]:[\\/]|\\\\[^\\])", value):
                        counts["local_path_cells"] += 1
                        path_columns[name + "." + column] += 1
                    if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", value):
                        counts["email_like_cells"] += 1
                    if re.search(r"https?://", value):
                        counts["url_cells"] += 1
                    inspect(value.encode(), oid, "sqlite:" + name + "." + column, findings)
                    try:
                        decoded = json.loads(value)
                    except (ValueError, RecursionError):
                        continue
                    secret_fields(decoded, secrets)
            result["tables"].append({"name": name, "columns": columns, "rows": rows})
        names = {table["name"] for table in result["tables"]}
        if {"books", "chapters", "pages"} <= names:
            pages = connection.execute("SELECT source_hash, source_filename FROM pages").fetchall()
            titles = connection.execute("SELECT title FROM books").fetchall()
            result["domain_rows"] = {name: connection.execute("SELECT COUNT(*) FROM " + name).fetchone()[0]
                                     for name in ("books", "chapters", "pages")}
            if pages and expected_hashes:
                result["synthetic_fixture_match"] = (
                    set(row[0] for row in pages) == expected_hashes
                    and all(row[1] in {"fixture-page-1.png", "fixture-page-2.png"} for row in pages)
                    and titles == [("M2-AC1 Acceptance Fixture",)])
    finally:
        connection.close()
    assert path.read_bytes() == data
    result.update({"cell_markers": dict(counts), "nonempty_secret_fields": dict(secrets),
                   "local_path_columns": dict(path_columns),
                   "heuristic_findings": findings, "copy_unchanged": True})
    return result


def selfcheck():
    oid = "01" * 20
    assert parse_tree(b"100644 sample.jpg\0" + bytes.fromhex(oid)) == [("100644", "sample.jpg", oid)]
    try:
        parse_tree(b"100644 sample.jpg\0x")
    except ValueError:
        pass
    else:
        raise AssertionError("truncated tree accepted")
    counts = collections.Counter()
    secret_fields({"context_token_budget": 4096, "nested": [{"api_key": "fixture", "password": ""}]}, counts)
    assert counts == {"api_key": 1}
    memory = sqlite3.connect(":memory:")
    try:
        memory.execute("CREATE TABLE sample(value TEXT)")
        memory.execute("INSERT INTO sample VALUES ('fixture')")
        memory.commit()
        serialized = memory.serialize()
        result = database_report(serialized, "selfcheck-" + hashlib.sha256(serialized).hexdigest())
        assert result["quick_check"] == ["ok"] and result["tables"][0]["rows"] == 1
        assert result["nonempty_secret_fields"] == {} and result["copy_unchanged"]
        with sqlite3.connect(Path(result["copy"]).as_uri() + "?mode=ro&immutable=1", uri=True) as readonly:
            try:
                readonly.execute("INSERT INTO sample VALUES ('must-not-write')")
            except sqlite3.OperationalError:
                pass
            else:
                raise AssertionError("immutable copy accepted a write")
        assert Path(result["copy"]).read_bytes() == serialized
    finally:
        memory.close()


def main():
    selfcheck()
    scan = json.loads((EVIDENCE / "push-history-scan.json").read_text(encoding="utf-8"))
    assert git("rev-parse", "HEAD").decode().strip() == scan["head"]
    process = subprocess.Popen(["git", "-C", str(ROOT), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(oid):
        assert re.fullmatch(r"[0-9a-f]{40}", oid)
        process.stdin.write((oid + "\n").encode())
        process.stdin.flush()
        header = process.stdout.readline().split()
        if len(header) == 2 and header[1] == b"missing":
            return None
        assert len(header) == 3 and header[0].decode() == oid
        data = process.stdout.read(int(header[2]))
        assert len(data) == int(header[2]) and process.stdout.read(1) == b"\n"
        return header[1].decode(), data

    trees, roots, missing = {}, set(), set()
    databases, image_paths, visited = [], collections.defaultdict(set), set()
    image_headers = {}
    expected_hashes = fixture_hashes()
    assert len(expected_hashes) == 2
    try:
        for entry in scan["compressed"]:
            outer_type, data = read(entry["object"])
            assert outer_type == "blob"
            decoded = zlib.decompress(data)
            header, payload = decoded.split(b"\0", 1)
            assert hashlib.sha1(decoded).hexdigest() == entry["git_object"]
            if header.startswith(b"tree "):
                trees[entry["git_object"]] = parse_tree(payload)
            elif header.startswith(b"commit "):
                first = payload.split(b"\n", 1)[0]
                assert first.startswith(b"tree ")
                roots.add(first[5:].decode())
        wanted = {entry["git_object"] for entry in scan["compressed"] if entry.get("payload_kind") in ("jpeg", "png")}
        pending = [(root, "", 0) for root in sorted(roots)]
        while pending:
            oid, prefix, depth = pending.pop()
            if (oid, prefix) in visited:
                continue
            if depth > 128 or len(visited) >= 100000:
                raise ValueError("tree traversal bound exceeded")
            visited.add((oid, prefix))
            if oid not in trees and oid not in missing:
                raw = read(oid)
                if raw is None:
                    missing.add(oid)
                else:
                    assert raw[0] == "tree"
                    trees[oid] = parse_tree(raw[1])
            for mode, name, child in trees.get(oid, []):
                path = prefix + "/" + name if prefix else name
                if child in wanted:
                    image_paths[child].add(path)
                if mode == "40000":
                    pending.append((child, path, depth + 1))
        for entry in scan["compressed"]:
            if entry.get("payload_kind") in ("jpeg", "png"):
                raw = read(entry["git_object"])
                assert raw is not None and raw[0] == "blob"
                assert hashlib.sha256(raw[1]).hexdigest() == entry["payload_sha256"]
                with Image.open(io.BytesIO(raw[1])) as image:
                    image_headers[entry["git_object"]] = {"width": image.width, "height": image.height, "mode": image.mode}
        for entry in scan["material"]:
            if entry["kind"] == "sqlite":
                _, data = read(entry["object"])
                try:
                    result = database_report(data, entry["object"], expected_hashes)
                except sqlite3.DatabaseError as exc:
                    result = {"status": "BLOCKED_DATABASE_READ", "error_type": type(exc).__name__}
                databases.append({"object": entry["object"], "path": entry["path"], **result})
    finally:
        process.stdin.close()
        process.stdout.close()
        assert process.wait() == 0
    images = [{"outer_object": entry["object"], "embedded_object": entry["git_object"],
               "kind": entry["payload_kind"], "sha256": entry["payload_sha256"],
               "historical_paths": sorted(image_paths.get(entry["git_object"], set())),
               "basename_hints": sorted({name for children in trees.values() for _, name, oid in children if oid == entry["git_object"]}),
               "header": image_headers[entry["git_object"]],
               "rights_status": "NOT_ESTABLISHED"}
              for entry in scan["compressed"] if entry.get("payload_kind") in ("jpeg", "png")]
    synthetic_commit = git("rev-parse", "ed607b755").decode().strip()
    synthetic_manifest = git("show", synthetic_commit + ":verification/T1.1.1/samples/manifest.json")
    synthetic = {value["sha256"]: value["file"] for value in json.loads(synthetic_manifest).values()}
    for image in images:
        if image["sha256"] in synthetic:
            image["source_status"] = "SYNTHETIC_SOURCE_CONFIRMED"
            image["source_file"] = synthetic[image["sha256"]]
    real_records = git("show", "HEAD:verification/T1.1.1/real-material/results.json")
    expected_names = {entry["page"] for entry in json.loads(real_records)["records"]}
    jpeg_names = {name for image in images if image["kind"] == "jpeg" for name in image["basename_hints"]}
    material_correlation = {"document": "HEAD:verification/T1.1.1/author-verification.md",
                            "document_sha256": hashlib.sha256(git("show", "HEAD:verification/T1.1.1/author-verification.md")).hexdigest(),
                            "records": "HEAD:verification/T1.1.1/real-material/results.json",
                            "records_sha256": hashlib.sha256(real_records).hexdigest(),
                            "jpeg_count": sum(image["kind"] == "jpeg" for image in images),
                            "documented_page_count": len(expected_names),
                            "all_filenames_match": jpeg_names == expected_names,
                            "jpeg_dimensions": dict(collections.Counter(str((image["header"]["width"], image["header"]["height"])) for image in images if image["kind"] == "jpeg")),
                            "status": "CORRELATED_NOT_HASH_PROVEN",
                            "limit": "Historical numeric records contain no page-content hash; filename/count/dimension correlation cannot prove exact source or redistribution rights."}
    result = {"base": scan["base"], "head": scan["head"], "sqlite_runtime": sqlite3.sqlite_version,
              "scan_sha256": hashlib.sha256((EVIDENCE / "push-history-scan.json").read_bytes()).hexdigest(),
              "synthetic_fixture_source": "HEAD:src/bootstrap/acceptance_bridge.py",
              "synthetic_fixture_source_sha256": hashlib.sha256(git("show", "HEAD:src/bootstrap/acceptance_bridge.py")).hexdigest(),
              "synthetic_fixture_page_sha256": sorted(expected_hashes),
              "synthetic_image_source_commit": synthetic_commit,
              "synthetic_image_manifest_sha256": hashlib.sha256(synthetic_manifest).hexdigest(),
              "synthetic_image_generator_sha256": hashlib.sha256(git("show", synthetic_commit + ":verification/T1.1.1/scripts/generate_samples.py")).hexdigest(),
              "jpeg_material_correlation": material_correlation,
              "trees_loaded": len(trees), "root_trees": len(roots), "missing_trees": sorted(missing),
              "images": images, "databases": databases,
              "limits": ["Historical paths establish repository provenance, not redistribution rights.",
                         "SQLite copies are immutable committed main files; WAL state, deleted rows, free pages and unrecognized/encoded secrets are not cleared.",
                         "Database cell markers are heuristic counts, not raw user records or a privacy clearance."]}
    (EVIDENCE / "push-material-inspection.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"images": len(images), "images_with_paths": sum(bool(x["historical_paths"]) for x in images),
                      "trees_loaded": len(trees), "missing_trees": len(missing), "databases": len(databases),
                      "database_failures": sum(x.get("status") == "BLOCKED_DATABASE_READ" for x in databases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
