"""M2-AC5 frozen entry for ``python -m infrastructure.resource_channel.host_bridge``.

PyInstaller cannot launch a module with ``-m`` directly; each sidecar entry
gets this thin frozen wrapper instead. The wrapper only imports the module's
``main`` and runs it — module-level side effects are identical to the ``-m``
invocation, and the module name is NOT executed twice (the ``__main__`` guard
body is reached through the explicit call, not through runpy).

This file is build tooling only (packaging/**): it is never part of the
product runtime dependency list, and ``src/**`` stays untouched.
"""

from infrastructure.resource_channel.host_bridge import main

if __name__ == "__main__":
    raise SystemExit(main())
