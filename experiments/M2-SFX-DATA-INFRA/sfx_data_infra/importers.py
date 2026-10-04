"""AC5：存量资产导入器（桩——红绿纪律先红后绿）。

三份既有资产：
- verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l3-reference-crops.json（BJ13/14/15 七参照框）
- verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json（8 个 sfx region）
- experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json（regions 顶层键、43 项，标 pseudo）
"""

from __future__ import annotations

# 素材根候选（只读）：本 worktree → E2E-MATERIAL worktree（BJ13/14/15 页）→ TA2B worktree（BJ06 页）
DEFAULT_ASSET_ROOTS = (
    r"G:\CODEX\New Manga.worktrees\M2-SFX-DATA-INFRA-zcode\test_assets\comic_golden_suite",
    r"G:\CODEX\New Manga.worktrees\M2-SFX-E2E-MATERIAL-zcode\test_assets\comic_golden_suite",
    r"G:\CODEX\New Manga.worktrees\M2-TA2B-OPEN-ASSETS-zcode\test_assets\comic_golden_suite",
)


def parse_ogkalu_region_key(key: str) -> str:
    """'K01_R035' -> 'K01'。"""
    raise NotImplementedError


def bbox_to_polygon(x, y, w, h):
    raise NotImplementedError


def xyxy_to_polygon(x0, y0, x1, y1):
    raise NotImplementedError


def page_filename_for_case(case_id: str, cases_index: dict) -> str:
    """BJ13 -> 'vol03_p0048.png'（由 cases.json source_id 推）。"""
    raise NotImplementedError


def resolve_asset_roots(extra=()):
    raise NotImplementedError


def find_page_image(case_id: str, cases_index: dict, roots):
    raise NotImplementedError


def import_reference_crops(cases_index, roots, now_iso: str):
    """l3 七参照框 → partial 样本。"""
    raise NotImplementedError


def import_bj06(cases_index, roots, now_iso: str):
    """BJ06 八自证框 → partial 样本。"""
    raise NotImplementedError


def import_ogkalu(cases_index, roots, now_iso: str):
    """ogkalu 43 region → pseudo 样本。"""
    raise NotImplementedError


def import_all(now_iso: str):
    """一键导入三资产 → list[SampleRecord]（7+8+43=58）。"""
    raise NotImplementedError
