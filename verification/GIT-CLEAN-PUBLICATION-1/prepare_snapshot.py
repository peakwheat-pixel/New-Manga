"""Export fixed Git blobs to a new repository; never copy the source object store."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = "349e61faff5f93067af5d4ce2d9e394e0d665b8c"
TASK_ENV = Path("G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1")
EXPORT = TASK_ENV / "source-export-r4"
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "audit/V1-FULL-AUDIT/tests"))
from scan_push_history import inspect


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", "-C", str(cwd), *args])


def allowed(path):
    if PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts or "\\" in path or ":" in path:
        return False
    if path in {"requirements.txt", "requirements-dev.txt", "pytest.ini", "apps/desktop/.gitignore"}:
        return True
    if path == "apps/desktop/src-tauri/icons/icon.ico":
        return True
    if path == "experiments/TASK-016/generate_samples.py":
        return True
    if path == "verification/P04/deterministic_concurrent_sidecar.py":
        return True
    if path == "verification/P22-REBASE-1/deterministic_concurrent_sidecar.py":
        return True
    prefixes = ("src/", "tests/", "apps/desktop/frontend/", "apps/desktop/src-tauri/",
                "packaging/m2ac5/", "tools/smoke/")
    extras = {"packaging/check_qt_closure.py", "packaging/bundle_python_runtime.ps1", "packaging/manifest.py"}
    extensions = {".py", ".qml", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".json", ".lock",
                  ".toml", ".rs", ".ps1", ".spec", ".txt", ".md", ".html", ".css", ".svg"}
    return (path.startswith(prefixes) or path in extras) and not path.startswith("apps/desktop/frontend/e2e/") and (
        PurePosixPath(path).suffix in extensions or PurePosixPath(path).name == ".gitignore")


def selfcheck():
    assert allowed("src/bootstrap/core_service.py") and allowed("apps/desktop/frontend/package-lock.json")
    for path in (".tmp.driveupload/123", "verification/P18/data.db", "tests/private.jpg",
                 "src/private.sqlite", "../src/escape.py", "apps/desktop/frontend/e2e/run.mjs"):
        assert not allowed(path)


def write_once(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_symlink() or path.read_bytes() != data:
            raise ValueError("existing export differs: " + str(path))
    else:
        with path.open("xb") as handle:
            handle.write(data)


def main():
    selfcheck()
    assert git("rev-parse", "HEAD").decode().strip() == BASE
    assert not git("diff", "--cached", "--name-only").strip()
    disposition = json.loads((ROOT / "audit/V1-FULL-AUDIT/evidence/push-material-disposition.json").read_text(encoding="utf-8"))
    denied_oids = {oid for row in disposition["objects"] for oid in (row["outer_object"], row["embedded_git_object"])}
    denied_sha256 = {row["payload_sha256"] for row in disposition["objects"]}
    placeholders = json.loads((ROOT / "audit/V1-FULL-AUDIT/evidence/push-material-provenance.json").read_text(encoding="utf-8"))["credential_dispositions"]
    allowed_findings = {(row["rule"], row["path"], row["value_sha256"]) for row in placeholders}
    # These fixed literals belong to diagnostics redaction and loopback proxy tests.
    allowed_findings.update({
        ("credential_assignment", "tests/diagnostics/test_report.py", "2707ae2b2f52aab7b614d0feefe9dddc5ad7e37962c632ad6063c180c51ac8a1"),
        ("credential_assignment", "tests/network/test_transport_local.py", "9246aa9be8de7b40d64eb664986430793b6cc13a19d2a456981e44f28303f9cf"),
    })
    inventory = []
    for raw in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
        if raw:
            meta, path = raw.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            inventory.append((path.decode(), mode, kind, oid))
    selected, excluded, findings, blockers = [], [], [], []
    payloads = {}
    process = subprocess.Popen(["git", "-C", str(ROOT), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for path, mode, kind, oid in inventory:
            if not allowed(path) or mode not in ("100644", "100755") or kind != "blob":
                excluded.append({"path": path, "reason": "OUTSIDE_FILE_ALLOWLIST_OR_NOT_REGULAR_BLOB"})
                continue
            process.stdin.write((oid + "\n").encode()); process.stdin.flush()
            header = process.stdout.readline().split()
            assert len(header) == 3 and header[0].decode() == oid and header[1] == b"blob"
            data = process.stdout.read(int(header[2]))
            assert len(data) == int(header[2]) and process.stdout.read(1) == b"\n"
            digest = hashlib.sha256(data).hexdigest()
            source_digest = digest
            transform = None
            if path in {"packaging/m2ac5/README.md", "tests/core/test_core_detect.py"}:
                data = data.replace(b"49745", b"USER")
                digest = hashlib.sha256(data).hexdigest()
                transform = "REDACT_PERSONAL_DIRECTORY_LITERAL"
            if oid in denied_oids or digest in denied_sha256:
                blockers.append({"path": path, "reason": "USER_FORBIDDEN_CONTENT"})
            if not path.endswith("/icons/icon.ico"):
                data.decode("utf-8")
                if b"\0" in data:
                    blockers.append({"path": path, "reason": "BINARY_IN_TEXT_ALLOWLIST"})
            if b"/9j/" in data or b"data:image/jpeg;base64," in data:
                blockers.append({"path": path, "reason": "EMBEDDED_IMAGE_REQUIRES_REVIEW"})
            local_hits = []
            inspect(data, oid, path, local_hits)
            for hit in local_hits:
                hit["disposition"] = "TEST_PLACEHOLDER" if (hit["rule"], path, hit["value_sha256"]) in allowed_findings else "BLOCKED"
                findings.append(hit)
                if hit["disposition"] == "BLOCKED":
                    blockers.append({"path": path, "reason": "CREDENTIAL_CANDIDATE"})
            selected.append({"path": path, "source_commit": BASE, "source_blob": oid, "source_sha256": source_digest,
                             "sha256": digest, "bytes": len(data), "transform": transform})
            payloads[path] = data
    finally:
        process.stdin.close(); process.stdout.close()
        assert process.wait() == 0
    report = {"base": BASE, "selected": selected, "excluded": excluded, "findings": findings, "blockers": blockers,
              "icon_provenance": {"path": "apps/desktop/src-tauri/icons/icon.ico", "introduced_at": "991097d770435377d68615ad0fd12503e16bb842"}}
    (EVIDENCE / "selection.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if blockers:
        raise SystemExit("selection blocked; see selection.json (no export written)")
    for path, data in payloads.items():
        write_once(EXPORT / path, data)
    sample_dir = EXPORT / "experiments/TASK-016/samples"
    if not (sample_dir / "manifest.json").exists():
        env = os.environ.copy(); env["QT_QPA_PLATFORM"] = "offscreen"; env["PYTHONDONTWRITEBYTECODE"] = "1"
        subprocess.run([sys.executable, "-B", str(EXPORT / "experiments/TASK-016/generate_samples.py"),
                        "--output-dir", str(sample_dir)], env=env, check=True, capture_output=True)
    fixture_manifest = json.loads((sample_dir / "manifest.json").read_text(encoding="utf-8"))
    assert fixture_manifest["provenance"] == "self-authored raster samples; no third-party artwork"
    expected_samples = {"jp_horizontal.png", "ko_horizontal.png", "jp_vertical.png", "art_text.png", "long_tile.png"}
    assert {row["path"] for row in fixture_manifest["samples"]} == expected_samples
    generated = []
    for row in fixture_manifest["samples"]:
        data = (sample_dir / row["path"]).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == row["sha256"] and digest not in denied_sha256
        generated.append({"path": (sample_dir / row["path"]).relative_to(EXPORT).as_posix(), "sha256": digest,
                          "generator": "experiments/TASK-016/generate_samples.py", "kind": "GENERATED_SYNTHETIC_TEST_FIXTURE"})
    generated.append({"path": "experiments/TASK-016/samples/manifest.json",
                      "sha256": hashlib.sha256((sample_dir / "manifest.json").read_bytes()).hexdigest(), "kind": "GENERATED_FIXTURE_MANIFEST"})
    write_once(EXPORT / "SOURCE_MANIFEST.json", (json.dumps({"source_commit": BASE, "files": selected, "generated_files": generated}, ensure_ascii=False, indent=2) + "\n").encode())
    write_once(EXPORT / ".gitignore", b"__pycache__/\n*.py[cod]\n.pytest_cache/\n.venv/\nnode_modules/\ntarget/\ndist/\nbuild/\n.env*\n*.db\n*.sqlite\n*.jpg\n*.jpeg\n*.zip\n*.pt\n*.onnx\n*.safetensors\n*.jsonl\n*.log\n")
    readme = f"""# New Manga 源码快照

此目录是固定源码 `{BASE}` 的独立快照，目标架构为 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy。SOURCE_MANIFEST.json 记录逐文件来源；源历史、私有漫画/数据、模型、数据库、日志、验证证据及Agent配置未随快照分发。现有Legacy源码仅保留参考，不代表继续演进的目标。未授予新的项目或第三方许可证。

两处文档/测试中的个人目录字面量已替换为USER，清单同时保留源/导出hash。experiments/TASK-016/samples 仅含从自制生成器重建的5个合成测试PNG及manifest，供Rust测试编译，不是漫画素材或模型质量证明。

前端：在 apps/desktop/frontend 中执行 npm ci、npm test、npm run build。Core：在已具备所需Python依赖的环境中，从根目录执行 python -B -m pytest tests/core -q -rs。requirements文件保持源版本，不表示已重新认证全部依赖。

Tauri本地开发检查需设置 M2RC1_DEV_PREVIEW=1 并先构建frontend；生产打包还需要独立准备sidecar、模型与运行环境，详见 packaging/m2ac5/README.md。私有模型/输入不随本快照提供。源码中的历史doc/verification引用属于原项目上下文，此快照不声称包含这些证据。

当前仅供本地检查；没有执行push、发布或签名，构建与审查结果以本次交付记录为准。
"""
    write_once(EXPORT / "README.md", readme.encode())
    if not (EXPORT / ".git").exists():
        git("init", "--initial-branch=codex/clean-source-snapshot", cwd=EXPORT)
        git("config", "core.autocrlf", "false", cwd=EXPORT)
        git("config", "gc.auto", "0", cwd=EXPORT)
        git("config", "maintenance.auto", "false", cwd=EXPORT)
        hooks = TASK_ENV / "empty-hooks"; hooks.mkdir(exist_ok=True)
        git("config", "core.hooksPath", str(hooks), cwd=EXPORT)
    git("add", "--", ".", cwd=EXPORT)
    existing = subprocess.run(["git", "-C", str(EXPORT), "rev-parse", "--verify", "HEAD"], capture_output=True)
    if existing.returncode != 0:
        git("-c", "user.name=Codex", "-c", "user.email=codex@localhost", "commit", "-m", "Source snapshot without private materials or inherited history", cwd=EXPORT)
    assert not git("status", "--porcelain", cwd=EXPORT).strip()
    assert git("rev-list", "--count", "HEAD", cwd=EXPORT).strip() == b"1"
    assert len(git("rev-list", "--parents", "-n", "1", "HEAD", cwd=EXPORT).split()) == 1
    assert not git("remote", cwd=EXPORT).strip()
    checked = subprocess.run(["git", "-C", str(EXPORT), "cat-file", "--batch-check=%(objectname) %(objecttype)"], input=("\n".join(sorted(denied_oids)) + "\n").encode(), capture_output=True, check=True)
    assert all(row.endswith(b" missing") for row in checked.stdout.splitlines())
    result = {"source_commit": BASE, "repository": str(EXPORT), "branch": "codex/clean-source-snapshot",
              "delivery_head": git("rev-parse", "HEAD", cwd=EXPORT).decode().strip(), "root_commits": 1,
              "source_files": len(selected), "source_bytes": sum(row["bytes"] for row in selected),
              "forbidden_object_ids_absent": len(denied_oids), "remotes": [], "tests": "PENDING", "review": "NOT_RUN", "push": "NOT_AUTHORIZED"}
    (EVIDENCE / "snapshot.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
