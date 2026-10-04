"""AC4：底图 prompt 风格变体库（冻结常量，黑白漫画、无文字/人物/气泡）。

来源：2026-10-04 实测 20/20 风格批量验证（外部树 task-envs/sfx-synth-exp/）。
公共约束后缀强制"三无一留白"——无文字/人物/气泡，留白区供程序叠字。
"""

from __future__ import annotations

PROMPT_SUFFIX = (
    ", black and white manga comic style, no text, no letters, no characters, "
    "no people, no speech bubbles, no onomatopoeia"
)
PROMPT_PREFIX = "Generate an image: "

# 20 风格：名 → 英文风格描述（叠字适配=描述中含留白区指引）
BG_STYLES: dict[str, str] = {
    "radial_speed_lines": "dramatic radial speed lines converging from the edges toward the center, rough ink brush texture, a large empty white space in the center",
    "parallel_speed_lines": "parallel horizontal speed lines sweeping from left to right, strong motion streaks, a clean empty white horizontal band across the center",
    "halftone_gradient": "halftone screentone gradient, dots fading from dense black at the bottom to pure white at the top, clean empty middle band",
    "explosion_smoke": "billowing explosion smoke clouds, dark cumulus clouds with white highlights filling the frame edges, an empty bright gap in the center",
    "shattered_glass": "shattered glass, cracks radiating from an off-screen impact point at the upper right, sharp angular fragments, empty center area",
    "heavy_rain": "heavy rain scene, diagonal rain streaks over a dark stormy sky, empty bright area in the center",
    "lightning": "dramatic white lightning bolts on a dark background, branching sparks along the edges, empty dark area in the center",
    "flames": "flames rising along the bottom edge, bold ink-style fire tongues on white background, empty upper area",
    "city_night": "city skyline silhouette at night, simple building shapes with a few lit windows along the bottom, large empty sky above",
    "ocean_waves": "stylized manga ocean waves with curling foam along the bottom, decorative wave pattern, empty sky above",
    "vortex": "swirling vortex, spiral energy lines rotating around a clean empty center",
    "ink_splatter": "random black ink splatter and droplets on a white background, splashes pushed to the edges, empty white center",
    "inverted_burst": "inverted radial burst, glowing white streaks exploding outward on a solid black background, empty black center",
    "dust_debris": "dust and debris explosion, small rocks and dust clouds flying up from the bottom edge, empty center",
    "bamboo_forest": "bamboo forest background, tall bamboo stalks and leaves silhouettes framing both sides, empty center path",
    "geometric_collage": "abstract geometric collage, diagonal screentone stripes, dots and circles arranged around a clean empty white panel in the center",
    "impact_shockwave": "impact shockwave, concentric circular rings expanding from the center, ground cracks at the bottom, empty center",
    "cloud_frame": "soft stylized clouds framing the edges of the frame, big empty sky area in the center",
    "street_perspective": "one-point perspective street alley, simple line art buildings converging to the center, empty road in the middle",
    "water_splash": "dynamic water splash crown rising from the bottom, flying droplets, empty upper area",
}


def build_prompt(style: str) -> str:
    """按风格名构建完整 prompt（KeyError=未知风格，fail-fast）。"""
    return f"{PROMPT_PREFIX}{BG_STYLES[style]}{PROMPT_SUFFIX}"


def style_cycle(start: int = 0):
    """按冻结顺序循环产出 (序号, 风格名)——同批内风格均匀覆盖。"""
    names = list(BG_STYLES)
    n = len(names)
    i = start
    while True:
        yield (i, names[i % n])
        i += 1
