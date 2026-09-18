"""TASK-052 AC ①③④: command failures become visible, diagnosable state.

Three real failure classes drive the surface: a selection guard (no
Region / no Page), the provider-binding PipelineError text the pipeline
produces, and a worker crash delivered through the controller's
``runCrashed`` receiver.  The legacy ``commandError`` signal keeps
emitting the bare detail (existing listeners stay pinned); the new
``commandErrorText`` state carries the ``[stage/code] detail``
diagnosis, and ``clearCommandError`` acknowledges it.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)
from test_workbench_viewmodel import completed_vm  # module-local helper

import pytest

from application.tasks.service import PipelineError


def test_selection_failures_surface_with_diagnosis_and_clear(qapp):
    service, vm = completed_vm()
    bare = []
    vm.commandError.connect(bare.append)

    vm.startTranslateSelected()
    assert vm.commandErrorText == "[selection] 未选择任何 Page"
    assert bare == ["未选择任何 Page"]  # legacy signal: bare detail

    vm.startRegionCommand("ocr_region")
    assert vm.commandErrorText == "[selection] 未选择 Region"

    vm.clearCommandError()
    assert vm.commandErrorText == ""
    # clearing again stays a no-op (no spurious notify storms)
    vm.clearCommandError()
    assert vm.commandErrorText == ""


def test_provider_binding_failure_keeps_code_and_detail(qapp):
    service, vm = completed_vm()
    bare = []
    vm.commandError.connect(bare.append)

    # the exact failure text the production chain raises for an unbound
    # step (handlers._chain), through the object branch of the sink
    error = PipelineError(
        "PROVIDER_NOT_CONFIGURED",
        "no provider binding configured for step 'ocr'",
    )
    vm._record_command_error(error)
    assert vm.commandErrorText == (
        "[command/PROVIDER_NOT_CONFIGURED] "
        "no provider binding configured for step 'ocr'"
    )
    assert bare == ["no provider binding configured for step 'ocr'"]


def test_worker_crash_surfaces_with_stage(qapp):
    service, vm = completed_vm()
    vm._on_run_crashed("run-1", "worker exploded")
    assert vm.commandErrorText == "[worker] worker exploded"


