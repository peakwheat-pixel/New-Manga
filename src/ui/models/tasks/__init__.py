"""Workbench task projection models (TASK-013).

``TaskProjection`` is the single progress projection shared by PageList and
TaskProgressPanel (D06 §79, AC-PROGRESS-007); ``WorkbenchPageListModel``
exposes it to QML as a filterable, multi-selectable list model.
"""

from ui.models.tasks.page_list_model import WorkbenchPageListModel
from ui.models.tasks.projection import (
    PageProjectionRow,
    TaskProjection,
    build_projection,
)

__all__ = [
    "PageProjectionRow",
    "TaskProjection",
    "WorkbenchPageListModel",
    "build_projection",
]
