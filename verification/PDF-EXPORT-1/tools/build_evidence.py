"""PDF-EXPORT-1: aggregate the three real PDF artefacts into the evidence JSON."""
import hashlib
import json
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\PDF-EXPORT-1")
REPO = Path(r"G:\CODEX\New Manga")
VD = REPO / "verification" / "PDF-EXPORT-1"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(name: str) -> dict:
    path = TASK_ENV / "evidence" / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


wire = load("pdf-export.json")
supp = load("supplementary.json")

agg = {
    "task": "PDF-EXPORT-1",
    "base": "170878dc4",
    "verdict": "PDF export is ALREADY implemented Qt-free at HEAD (QtFreePdfComposer, wired in "
               "core_assembly.py); this card records the acceptance evidence and the Record Decision. "
               "No new Pillow composer was written (Pillow's Image.save('PDF') is lossy JPEG and "
               "drops the text layer -> would regress the existing asset).",
    "extension_point": {
        "port": "src/application/export/ports.py: PdfComposer.compose(images) / compose_searchable(images, regions)",
        "service": "src/application/export/service.py: ExportFormat.PDF + _build_payload pdf branch "
                   "('pdf_content' = image_only | searchable_dual_layer)",
        "production_wiring": "src/bootstrap/core_assembly.py:1374 ExportService(..., pdf_composer=QtFreePdfComposer())",
        "composer": "src/infrastructure/export/qt_free.py QtFreePdfComposer (Qt-free: stdlib zlib/struct + "
                    "Pillow only for searchable-mode font metrics; no PySide6/Qt import in the closure)",
        "wire": "StartExport format='pdf' + format_options={'pdf_content': ...}; host-control "
                "RegisterExportTarget/grant; src/bootstrap/core_service.py handle_start_export",
    },
    "artefacts": {},
    "regression": {},
}
a = wire.get("artifact") or {}
agg["artefacts"]["wire_image_only_3pages"] = {
    "case": "real host-control grant + handle_start_export, BOOK-FIXTURE chapter (8-page book, 3 translated pages)",
    "pages_requested": wire.get("ordered_page_ids"),
    "status": (wire.get("snapshot") or {}).get("status"),
    "export_id": wire.get("export_id"),
    "path": a.get("path"), "bytes": a.get("bytes"), "sha256": a.get("sha256"),
    "header": a.get("header"), "eof": a.get("eof"),
    "pdf_page_count": a.get("pdf_page_count"),
    "pages": a.get("pages"), "sizes_match_db": a.get("sizes_match_db"),
    "page_count_matches": a.get("page_count_matches"),
    "progress_events": len(wire.get("polls") or []),
}
e8 = supp.get("engine_8page") or {}
agg["artefacts"]["engine_8page"] = {
    "case": "engine-level whole-book export: 3 translated renders + 5 original fallbacks "
            "(stale_policy=continue_existing)",
    "pages_requested": e8.get("pages_requested"),
    "translated_pages": e8.get("translated_pages"),
    "status": e8.get("status"),
    "artifact": e8.get("artifact"),
}
ws = supp.get("wire_searchable") or {}
agg["artefacts"]["wire_searchable_3pages"] = {
    "case": "wire-level pdf_content=searchable_dual_layer (text layer over translated pages)",
    "status": (ws.get("snapshot") or {}).get("status"),
    "error_code": ws.get("error_code"),
    "artifact": ws.get("artifact"),
}
# copy the small 3-page artefact into repo evidence (precedent: IMPORT-EXPORT-UI-1 kept the 7 MB ZIP)
artifacts_dir = VD / "artifacts"
artifacts_dir.mkdir(parents=True, exist_ok=True)
src_pdf = Path(a.get("path", ""))
if src_pdf.is_file():
    dst = artifacts_dir / "BOOK-FIXTURE-1-3pages-image-only.pdf"
    dst.write_bytes(src_pdf.read_bytes())
    agg["artefacts"]["wire_image_only_3pages"]["committed_copy"] = {
        "rel": dst.relative_to(REPO).as_posix(), "bytes": dst.stat().st_size, "sha256": sha(dst),
    }
    agg["artefacts"]["wire_image_only_3pages"]["committed_copy_matches"] = (
        sha(dst) == a.get("sha256"))
else:
    agg["artefacts"]["wire_image_only_3pages"]["committed_copy"] = None

VD.mkdir(parents=True, exist_ok=True)
out = VD / "pdf-artifacts.json"
out.write_text(json.dumps(agg, indent=2, ensure_ascii=False), encoding="utf-8")
print("written", out, out.stat().st_size, "bytes")
for key, value in agg["artefacts"].items():
    art = value.get("artifact") or value
    print(f"  {key:<26} bytes={art.get('bytes')} pages={art.get('pdf_page_count')} "
          f"sha={(art.get('sha256') or '')[:16]}…")
