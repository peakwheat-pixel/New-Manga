from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_reader_and_export_qml_expose_required_controls():
    reader = (ROOT / "src/ui/qml/reader/ReaderView.qml").read_text(encoding="utf-8")
    export = (ROOT / "src/ui/qml/windows/ExportWindow.qml").read_text(encoding="utf-8")
    for value in ("Original", "Translated", "RTL", "LTR", "stale", "readerPage"):
        assert value in reader
    for value in ("png", "zip", "cbz", "pdf", "txt", "exportOverwrite"):
        assert value in export
