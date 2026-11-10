"""SQLite persistence for AI prompt templates (FEA-14-AI-1, schema v14)."""

from __future__ import annotations

from domain.ai.entities import PromptTemplate, PromptTemplateReference

_COLUMNS = "template_id, name, body, version, created_at, updated_at, deleted_at"


class SqlitePromptTemplateStore:
    """Repository for ``prompt_templates`` / ``prompt_template_references``."""

    def __init__(self, conn) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # template rows
    # ------------------------------------------------------------------
    def add_template(self, template: PromptTemplate) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO prompt_templates"
                f" ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    template.template_id,
                    template.name,
                    template.body,
                    template.version,
                    template.created_at,
                    template.updated_at,
                    template.deleted_at,
                ),
            )

    def get_template(self, template_id: str) -> PromptTemplate | None:
        row = self._conn.execute(
            "SELECT " + _COLUMNS + " FROM prompt_templates"
            " WHERE template_id = ? AND deleted_at IS NULL",
            (template_id,),
        ).fetchone()
        return None if row is None else _template_from_row(row)

    def find_by_name(self, name: str) -> PromptTemplate | None:
        row = self._conn.execute(
            "SELECT " + _COLUMNS + " FROM prompt_templates"
            " WHERE name = ? AND deleted_at IS NULL",
            (name,),
        ).fetchone()
        return None if row is None else _template_from_row(row)

    def list_templates(self) -> list[PromptTemplate]:
        rows = self._conn.execute(
            "SELECT " + _COLUMNS + " FROM prompt_templates"
            " WHERE deleted_at IS NULL ORDER BY name, template_id"
        ).fetchall()
        return [_template_from_row(row) for row in rows]

    def update_template(self, template: PromptTemplate) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE prompt_templates SET name = ?, body = ?, version = ?,"
                " updated_at = ?, deleted_at = ? WHERE template_id = ?",
                (
                    template.name,
                    template.body,
                    template.version,
                    template.updated_at,
                    template.deleted_at,
                    template.template_id,
                ),
            )

    # ------------------------------------------------------------------
    # reference rows
    # ------------------------------------------------------------------
    def list_references(self, template_id: str) -> list[PromptTemplateReference]:
        rows = self._conn.execute(
            "SELECT template_id, kind, owner_id, label FROM prompt_template_references"
            " WHERE template_id = ? ORDER BY kind, owner_id",
            (template_id,),
        ).fetchall()
        return [
            PromptTemplateReference(
                template_id=str(row[0]), kind=str(row[1]),
                owner_id=str(row[2]), label=str(row[3]),
            )
            for row in rows
        ]

    def reassign_references(self, source_id: str, replacement_id: str) -> None:
        """Point every reference at the replacement (delete already shadows)."""
        with self._conn:
            self._conn.execute(
                "UPDATE OR REPLACE prompt_template_references SET template_id = ?"
                " WHERE template_id = ?",
                (replacement_id, source_id),
            )


def _template_from_row(row) -> PromptTemplate:
    return PromptTemplate(
        template_id=str(row[0]),
        name=str(row[1]),
        body=str(row[2]),
        version=int(row[3]),
        created_at=str(row[4]),
        updated_at=str(row[5]),
        deleted_at=None if row[6] is None else str(row[6]),
    )
