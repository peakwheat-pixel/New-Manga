"""SHA-256 Manifest generation and verification for New Manga distribution."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_manifest(root_dir: Path) -> list[tuple[str, str]]:
    """Scan directory and return sorted list of (sha256, relative_posix_path)."""
    manifest_entries: list[tuple[str, str]] = []
    root_resolved = root_dir.resolve()

    for path in root_resolved.rglob("*"):
        if path.is_file():
            rel_path = path.relative_to(root_resolved).as_posix()
            digest = compute_sha256(path)
            manifest_entries.append((digest, rel_path))

    manifest_entries.sort(key=lambda item: item[1])
    return manifest_entries


def write_manifest(entries: list[tuple[str, str]], output_path: Path) -> None:
    lines = [f"{digest}  {rel_path}\n" for digest, rel_path in entries]
    output_path.write_text("".join(lines), encoding="utf-8")


def compare_manifests(file_a: Path, file_b: Path) -> bool:
    """Compare two manifest files, reporting differences."""
    content_a = file_a.read_text(encoding="utf-8").splitlines()
    content_b = file_b.read_text(encoding="utf-8").splitlines()

    dict_a = dict(line.split("  ", 1)[::-1] for line in content_a if "  " in line)
    dict_b = dict(line.split("  ", 1)[::-1] for line in content_b if "  " in line)

    all_paths = sorted(set(dict_a.keys()) | set(dict_b.keys()))
    diffs = []
    for p in all_paths:
        h_a = dict_a.get(p)
        h_b = dict_b.get(p)
        if h_a != h_b:
            diffs.append((p, h_a, h_b))

    if not diffs:
        print("Manifests match identically.")
        return True

    print(f"Manifest mismatch: {len(diffs)} difference(s):", file=sys.stderr)
    for p, h_a, h_b in diffs:
        print(f"  {p}: A={h_a} vs B={h_b}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify package manifest")
    parser.add_argument("--root", type=Path, help="Root directory of package artifact to scan")
    parser.add_argument("--output", type=Path, help="Target manifest output file")
    parser.add_argument("--compare", nargs=2, type=Path, help="Compare two manifest files")

    args = parser.parse_args()

    if args.compare:
        match = compare_manifests(args.compare[0], args.compare[1])
        return 0 if match else 1

    if not args.root:
        parser.error("Either --root or --compare is required.")

    if not args.root.is_dir():
        print(f"Error: {args.root} is not a directory.", file=sys.stderr)
        return 2

    entries = generate_manifest(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_manifest(entries, args.output)
        print(f"Wrote {len(entries)} file records to {args.output}")
    else:
        for digest, rel in entries:
            print(f"{digest}  {rel}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
