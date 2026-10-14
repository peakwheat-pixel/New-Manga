Static preflight findings (owner test harness only; no product code changes):

1. AC1–AC6 create EvidenceStore before launchApp. EvidenceStore constructor mkdirs RUN_ROOT/logs/<scenario>; launchApp then calls assertLaunchTargetsClean, which rejects non-empty RUN_ROOT/logs. Reorder minimal so the clean prelaunch observation happens before evidence writes, while still creating isolated logs after the guard.
2. RUN_ROOT is fixed at the shared run-r1 root. Independent scripts reuse launchDirs under that root, while the guard requires absent/empty paths; after one AC creates appdata/data/log files, the next AC will reject those prior synthetic outputs. Use a distinct never-before-used Task-local scenario directory per AC under run-r1, preserve completed evidence, and never clean or overwrite it.
3. ac6-contrast.mjs nests unescaped template delimiters in the String.raw COLLECT_SOURCE, causing the previously recorded Node syntax error near rgb. Fix only the allowed test harness and require node --check to pass for all ten .mjs files before any app launch.

Classification: test-driver code (T); no product defect asserted. AC1–AC7 remain NOT_RUN. Do not launch until all three harness conditions are repaired and rechecked.
