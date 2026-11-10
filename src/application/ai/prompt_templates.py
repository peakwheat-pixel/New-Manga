"""FEA-14-AI-1 (PREQ AI P21-P25): prompt templates.

Builtin templates are read-only Core constants; user templates are stored in
schema v14. The service never triggers a network/AI call (PREQ §6). Deleting a
template requires a replacement: existing reference rows are reassigned to the
replacement inside the same transaction before the target is soft deleted.
"""

from __future__ import annotations

import uuid

from domain.ai.entities import BuiltinPromptTemplate, PromptTemplate, PromptTemplateReference
from domain.books.entities import utc_now

#: Read-only builtins (PREQ DDL §2.4: builtins never land in the database).
BUILTIN_PROMPT_TEMPLATES: tuple[BuiltinPromptTemplate, ...] = (
    BuiltinPromptTemplate(
        template_id="builtin-translate-default",
        name="Default Translation",
        body="Translate the source text into the target language. Keep names, "
             "honorifics and sound effects faithful to the source.",
    ),
    BuiltinPromptTemplate(
        template_id="builtin-sfx-detect",
        name="SFX Description",
        body="Describe each sound effect in the image, its reading order and "
             "whether it should stay as artwork or be redrawn as text.",
    ),
)

_MAX_NAME = 120
_MAX_BODY = 20000


class PromptTemplateError(Exception):
    """Typed AI template failure (the wire maps the code to an envelope)."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


class PromptTemplateService:
    """Prompt-template use cases (PREQ §8 P21-P25)."""

    def __init__(self, repository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # P21 list (builtins + user templates)
    # ------------------------------------------------------------------
    def list_templates(self) -> tuple[list[dict], int]:
        builtins = [
            {
                "template_id": template.template_id,
                "name": template.name,
                "version": template.version,
                "builtin": True,
            }
            for template in BUILTIN_PROMPT_TEMPLATES
        ]
        user = [
            {
                "template_id": template.template_id,
                "name": template.name,
                "version": template.version,
                "builtin": False,
            }
            for template in self._repo.list_templates()
        ]
        return builtins + user, len(builtins)

    # ------------------------------------------------------------------
    # P22 save (create or bump version)
    # ------------------------------------------------------------------
    def save_template(self, name: str, body: str, template_id: str | None = None) -> PromptTemplate:
        clean_name = self._require_text(name, "name", _MAX_NAME)
        clean_body = self._require_text(body, "body", _MAX_BODY)
        if template_id is None:
            if self._repo.find_by_name(clean_name) is not None:
                raise PromptTemplateError("TEMPLATE_NAME_EXISTS", "Template name already exists")
            template = PromptTemplate(
                template_id=uuid.uuid4().hex,
                name=clean_name,
                body=clean_body,
                version=1,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            self._repo.add_template(template)
            return template

        template = self._require_user_template(template_id)
        duplicate = self._repo.find_by_name(clean_name)
        if duplicate is not None and duplicate.template_id != template.template_id:
            raise PromptTemplateError("TEMPLATE_NAME_EXISTS", "Template name already exists")
        template.name = clean_name
        template.body = clean_body
        template.version += 1
        template.updated_at = utc_now()
        self._repo.update_template(template)
        return template

    # ------------------------------------------------------------------
    # P23 delete with mandatory replacement
    # ------------------------------------------------------------------
    def delete_template(self, template_id: str, replacement_id: str) -> bool:
        template = self._require_user_template(template_id)
        if not isinstance(replacement_id, str) or not replacement_id:
            raise PromptTemplateError("INVALID_REQUEST", "replacement_id is required")
        if replacement_id == template.template_id:
            raise PromptTemplateError("INVALID_REQUEST", "replacement_id must differ from template_id")
        if self._builtin(replacement_id) is not None:
            raise PromptTemplateError(
                "INVALID_REQUEST", "builtin templates cannot be a replacement target"
            )
        replacement = self._repo.get_template(replacement_id)
        if replacement is None:
            raise PromptTemplateError("TARGET_NOT_FOUND", "Replacement template was not found")
        # F-01 (r1): reassign references AND soft-delete the target in ONE store
        # transaction, so a failure can never leave references moved while the
        # template is still visible.
        self._repo.delete_with_reassign(template.template_id, replacement.template_id, utc_now())
        return True

    # ------------------------------------------------------------------
    # P24 copy a builtin into an editable copy
    # ------------------------------------------------------------------
    def copy_builtin(self, builtin_id: str, name: str | None = None) -> PromptTemplate:
        builtin = self._builtin(builtin_id)
        if builtin is None:
            raise PromptTemplateError("TARGET_NOT_FOUND", "Builtin template was not found")
        clean_name = self._require_text(
            name if name is not None else f"{builtin.name} (copy)", "name", _MAX_NAME
        )
        if self._repo.find_by_name(clean_name) is not None:
            raise PromptTemplateError("TEMPLATE_NAME_EXISTS", "Template name already exists")
        template = PromptTemplate(
            template_id=uuid.uuid4().hex,
            name=clean_name,
            body=builtin.body,
            version=1,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        self._repo.add_template(template)
        return template

    # ------------------------------------------------------------------
    # P25 references
    # ------------------------------------------------------------------
    def list_references(self, template_id: str) -> list[PromptTemplateReference]:
        if self._builtin(template_id) is not None:
            return list(self._repo.list_references(template_id))
        self._require_user_template(template_id)
        return list(self._repo.list_references(template_id))

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _builtin(template_id: str) -> BuiltinPromptTemplate | None:
        for template in BUILTIN_PROMPT_TEMPLATES:
            if template.template_id == template_id:
                return template
        return None

    @staticmethod
    def _require_text(value, field: str, limit: int) -> str:
        if not isinstance(value, str) or not value.strip():
            raise PromptTemplateError("INVALID_REQUEST", f"{field} must be a non-empty string")
        if len(value) > limit:
            raise PromptTemplateError("INVALID_REQUEST", f"{field} must be at most {limit} characters")
        return value

    def _require_user_template(self, template_id: str) -> PromptTemplate:
        if not isinstance(template_id, str) or not template_id:
            raise PromptTemplateError("INVALID_REQUEST", "template_id must be a non-empty string")
        if self._builtin(template_id) is not None:
            raise PromptTemplateError(
                "INVALID_REQUEST", "builtin templates are read-only"
            )
        template = self._repo.get_template(template_id)
        if template is None:
            raise PromptTemplateError("TARGET_NOT_FOUND", "Template was not found")
        return template
