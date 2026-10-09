"""Prove the planning validator rejects drift in every repeated P-node declaration."""
import contextlib
import io
import runpy
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE.parent / "PROJECT-ROADMAP-20261008" / "verify_plan.py"
ROADMAP = HERE.parent / "PROJECT-ROADMAP-20261008" / "ROADMAP.md"
ORIGINAL_READ_TEXT = Path.read_text


def expect_rejected(old: str, new: str, expected: str) -> None:
    def mutated_read_text(path: Path, *args, **kwargs) -> str:
        text = ORIGINAL_READ_TEXT(path, *args, **kwargs)
        if path.resolve() == ROADMAP.resolve():
            assert old in text, f"mutation source not found: {old}"
            return text.replace(old, new, 1)
        return text

    with patch.object(Path, "read_text", mutated_read_text):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                runpy.run_path(str(VALIDATOR), run_name="__main__")
            except AssertionError as error:
                assert expected in str(error), str(error)
                print(f"REJECTED: {expected}")
                return
    raise AssertionError(f"validator accepted roadmap drift: {expected}")


if __name__ == "__main__":
    validator_scope = runpy.run_path(str(VALIDATOR), run_name="validator_scope_probe")
    exceptions = validator_scope["P01_PRODUCT_PATH_EXCEPTIONS"]
    assert exceptions == {"apps/desktop/frontend/e2e/workbench_driver_protocol.ts"}
    unexpected = validator_scope["unexpected_p01_product_changes"]
    e2e_driver = "apps/desktop/frontend/e2e/workbench_driver_protocol.ts"
    product_source = "apps/desktop/frontend/src/App.tsx"
    assert unexpected([e2e_driver]) == []
    assert unexpected([e2e_driver, product_source]) == [product_source]
    print("PASS: P02 E2E-only delta is allowed and adding a product source path is rejected")
    expect_rejected(
        "P04<br/>proposed / 未释放",
        "P04<br/>ready / 未释放",
        "('P04', 'ready', 'proposed')",
    )
    expect_rejected(
        "P03<br/>done / Review与Codex集成Gate通过",
        "P03<br/>blocked / Review与Codex集成Gate通过",
        "('P03', 'blocked', 'done')",
    )
    print("PASS: both roadmap status drift probes were rejected")
