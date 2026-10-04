"""获取 AC4 毛笔体字体（TanukiMagic / たぬき油性マジック）到 data_root/fonts。

r2 新-5：字体本体在 gitignored 区，Git 内必须留可复现通道——本脚本即通道：
下载 → sha256 pin 校验 → 落位。许可：SIL Open Font License（作者 たぬき侍/
tanukifont.com，允许再分发与嵌入；许可全文见官方站 README）。

用法：
  python fetch_fonts.py [--data-root training_data/sfx-v1]
  # 或经 CLI：python -m sfx_data_infra fetch-fonts
零新依赖：stdlib（urllib 走系统代理环境变量）。
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

FONT_URL = "https://tanukifont.com/download/TanukiMagic_1_22.zip"
FONT_ZIP_SHA256 = "67f9ef68b043c036dc8c64cc70c266b9547853978fcf209050a8221c91766e1f"
FONT_SHA256 = "e4a1be7078036ba7482b1102e0a720f4e2848716f6a4862607a2c69d44d43278"
FONT_MEMBER = "TanukiMagic.ttf"
LICENSE_NOTE = (
    "TanukiMagic（たぬき油性マジック）© たぬき侍 / tanukifont.com — "
    "SIL Open Font License；sha256 pin 见本脚本 FONT_SHA256。"
)


def sha256_file(path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def fetch_fonts(data_root: Path) -> Path:
    fonts_dir = data_root / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    dst = fonts_dir / FONT_MEMBER
    if dst.exists() and sha256_file(dst) == FONT_SHA256:
        print(f"[fetch-fonts] already present & verified: {dst}")
        (fonts_dir / "LICENSE-NOTE.txt").write_text(LICENSE_NOTE, encoding="utf-8")
        return dst

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        zpath = tdp / "font.zip"
        print(f"[fetch-fonts] downloading {FONT_URL}")
        with urllib.request.urlopen(FONT_URL, timeout=120) as resp, open(zpath, "wb") as f:
            shutil.copyfileobj(resp, f)
        got = sha256_file(zpath)
        if got != FONT_ZIP_SHA256:
            raise RuntimeError(
                f"字体包 sha256 不符：got {got} != pin {FONT_ZIP_SHA256}\n"
                "上游 zip 更新时请人工核验新包并更新 FONT_ZIP_SHA256（fail-closed，不静默换源）"
            )
        with zipfile.ZipFile(zpath) as z:
            z.extract(FONT_MEMBER, tdp)
        shutil.copy2(tdp / FONT_MEMBER, dst)

    (fonts_dir / "LICENSE-NOTE.txt").write_text(LICENSE_NOTE, encoding="utf-8")
    print(f"[fetch-fonts] verified & installed: {dst}")
    return dst


def main(argv=None) -> int:
    from sfx_data_infra.cli import DEFAULT_DATA_ROOT

    ap = argparse.ArgumentParser(prog="fetch_fonts", description="获取 AC4 毛笔体字体（sha256 pin 校验）")
    ap.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    args = ap.parse_args(argv)
    fetch_fonts(Path(args.data_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
