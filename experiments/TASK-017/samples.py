"""Sample corpus: Japanese/Korean pages, multi-page context, glossary.

Kept tiny and deterministic so every protocol scenario is reproducible
without network or models (D08: samples must be re-runnable evidence).
"""

from __future__ import annotations

from protocol import ContextPage, RegionInput

GLOSSARY = {
    "先輩": "前辈",
    "倒す": "打倒",
    "마법": "魔法",
}

# Page 1 (target of most scenarios): mixed JP/KO regions.
PAGE1_REGIONS = [
    RegionInput("region-1", "先輩、次の試合では絶対に勝ちます！"),
    RegionInput("region-2", "그 마법은 아직 완성되지 않았어."),
    RegionInput("region-3", "倒すべき相手は、3日後に来る。"),
]

# Surrounding pages for multi-page context (D06 §84 Context Groups).
CONTEXT_BEFORE = ContextPage("page-0", "before", "前話：先輩は道場で一言も発しなかった。")
CONTEXT_AFTER = ContextPage("page-2", "after", "次話预告：倒すべきは過去の自分である。")
CONTEXT_PAGES = [CONTEXT_BEFORE, CONTEXT_AFTER]


def budget_scenario_regions(count: int = 40) -> list[RegionInput]:
    """Enough bulk text to overflow a small token budget deterministically."""
    filler = "这是一个用于预算截断实验的填充段落，包含足够的长度。" * 6
    return [RegionInput(f"region-{index}", filler) for index in range(1, count + 1)]
