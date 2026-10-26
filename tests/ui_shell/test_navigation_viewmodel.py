"""NavigationViewModel: QML-facing bridge over NavigationService."""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication  # noqa: E402

from ui.viewmodels.navigation.viewmodel import NavigationViewModel  # noqa: E402


@pytest.fixture()
def vm(qapp):
    return NavigationViewModel()


class Spy:
    def __init__(self, signal) -> None:
        signal.connect(self.record)
        self.calls: list = []

    def record(self, *args) -> None:
        self.calls.append(args if len(args) != 1 else args[0])


def test_defaults_to_bookshelf_with_four_entries(vm) -> None:
    assert vm.currentPage == "bookshelf"  # AC-NAV-001
    entries = vm.pages
    assert [entry["id"] for entry in entries] == [
        "bookshelf",
        "workbench",
        "reader",
        "settings",
    ]  # AC-NAV-002
    assert [entry["label"] for entry in entries] == ["书架", "工作台", "阅读器", "设置"]


def test_navigate_updates_property_and_signal(vm) -> None:
    spy = Spy(vm.currentPageChanged)
    vm.navigate("settings")
    assert vm.currentPage == "settings"
    assert spy.calls == ["settings"]


def test_navigate_rejects_fifth_route(vm) -> None:
    with pytest.raises(ValueError):
        vm.navigate("book_detail")


def test_workbench_context_exposed_and_kept(vm) -> None:
    vm.enterWorkbench("book-a", "ch-12")
    assert vm.currentPage == "workbench"
    vm.navigate("settings")
    vm.navigate("workbench")
    assert vm.workbenchContext["book_id"] == "book-a"  # AC-NAV-003
    assert vm.workbenchContext["chapter_id"] == "ch-12"


def test_reader_context_with_progress(vm) -> None:
    vm.enterReader("book-a", "ch-2", "page-23", "12/48")
    assert vm.currentPage == "reader"
    assert vm.readerContext["progress"] == "12/48"


def test_workbench_badge_property(vm) -> None:
    spy = Spy(vm.workbenchBadgeChanged)
    vm.setWorkbenchActivity(True, "运行中")
    assert vm.workbenchBadge == "运行中"
    assert vm.workbenchRunning is True
    assert spy.calls  # badge change signalled
    vm.navigate("bookshelf")  # leaving workbench keeps the badge
    assert vm.workbenchBadge == "运行中"
