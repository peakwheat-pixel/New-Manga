from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).parent / "fixture"
font = ImageFont.load_default()
for page in (1, 2):
    image = Image.new("RGB", (900, 1400), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 24, 876, 1376), outline="black", width=4)
    draw.text((52, 50), f"NEW MANGA AC3 SYNTHETIC TEST PAGE {page}", fill="black", font=font)
    panels = [
        (52, 110, 420, 560), (448, 110, 848, 560),
        (52, 590, 848, 940), (52, 970, 420, 1320),
        (448, 970, 848, 1320),
    ]
    for i, box in enumerate(panels, start=1):
        draw.rectangle(box, outline="black", width=3)
        x1, y1, x2, y2 = box
        draw.ellipse((x1 + 45, y1 + 45, x1 + 145, y1 + 145), outline="black", width=3)
        draw.line((x1 + 30, y1 + 185, x2 - 30, y1 + 185), fill="black", width=2)
        draw.line((x1 + 30, y1 + 220, x2 - 70, y1 + 220), fill="black", width=2)
        draw.text((x1 + 24, y2 - 36), f"Panel {i} - page {page}", fill="black", font=font)
    image.save(root / f"synthetic-page-{page:02}.png", format="PNG", optimize=False)
print(f"fixture_dir={root}")
for path in sorted(root.glob("*.png")):
    print(f"{path.name} bytes={path.stat().st_size}")
