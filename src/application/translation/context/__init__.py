"""Translation context layer: builder, constraint freeze, SFX gate and
translate step (D06 §10~18)."""

from application.translation.context.builder import ContextBuilder
from application.translation.context.gate import decide_sfx_translation
from application.translation.context.snapshot import freeze_constraints
from application.translation.context.step import execute_translate_step

__all__ = [
    "ContextBuilder",
    "decide_sfx_translation",
    "execute_translate_step",
    "freeze_constraints",
]
