"""AI application services (FEA-14-AI-1 prompt templates)."""

from application.ai.prompt_templates import (
    BUILTIN_PROMPT_TEMPLATES,
    PromptTemplateError,
    PromptTemplateService,
)

__all__ = ["BUILTIN_PROMPT_TEMPLATES", "PromptTemplateError", "PromptTemplateService"]
