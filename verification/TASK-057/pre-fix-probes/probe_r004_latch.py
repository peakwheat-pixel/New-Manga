"""R-004 门修前判别探针：restore 闩（restore 期间拒绝 startRun）的存在性。

- 修前形态：WorkbenchViewModel 没有 restore 闩 API —— ``vm.beginRestore``
  抛 AttributeError ⇒ restore 期间 ``startRun`` 没有任何拒绝路径
  （Q-008 前置①/R-004：``any_in_transaction`` 是快照不是准入闸门，
  门后 start() 仍可把新写者放进库）；
- 修后形态：闩存在，``beginRestore()`` 置位后 ``startTranslateAll()``
  被拒（不产生 run、controller 空闲），``endRestore()`` 解除。

同一探针两树均可跑，结论进 EXIT（review R-006）：
- 修前树：无闩 API ⇒ PRE-FIX 分支，EXIT=1（门第三件缺失的证据）；
- 修后树：闩拒绝 startRun、endRestore 解除 ⇒ POST-FIX 分支，EXIT=0；
  若闩在但拒绝失效 ⇒ POST-FIX-REGRESSION，EXIT=1。
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "tests" / "workbench"))
# workbench_helpers 自插 src 与其所在目录

from PySide6.QtGui import QGuiApplication  # noqa: E402

_app = QGuiApplication.instance() or QGuiApplication([])

import workbench_helpers as helpers  # noqa: E402

_service, _catalog = helpers.make_pipeline(pages=[("p1", 1), ("p2", 2)])
vm = helpers.make_vm(_service)
vm.setContext("book-1", "chapter-1", "书", "章")

try:
    vm.beginRestore()
except AttributeError as error:
    print(f"PRE-FIX: no restore latch exists (AttributeError: {error})")
    print("=> restore 期间 startRun 无拒绝路径 —— R-004 门第三件在修前树缺失")
    raise SystemExit(1)

latched = vm.beginRestore()
assert latched is True, "idle tree: beginRestore must latch successfully"
assert vm._controller.is_running is False
vm.startTranslateAll()
if vm._controller.is_running:
    print("POST-FIX-REGRESSION: latch did not reject startRun — a run "
          "started during restore")
    vm.shutdown()
    raise SystemExit(1)
print("POST-FIX: restore latch rejects startRun during restore "
      "(no run created, controller idle)")
vm.endRestore()
vm.startTranslateAll()
try:
    assert vm._controller.is_running is True, (
        "after endRestore a run must be startable again")
    print("POST-FIX: endRestore releases the latch — normal run start works")
finally:
    vm.shutdown()
raise SystemExit(0)
