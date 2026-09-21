# Stage A Rebaseline Evidence

```text
== env ==
repo: G:\CODEX\New Manga
code baseline: ce21ff9ea5738970bbda9a86079b673918c76048
shell: PowerShell
python: C:\Users\49745\AppData\Local\Temp\new-manga-audit-py314-20260921\Scripts\python.exe
python version: 3.14.6
pytest: 9.1.1
PYTHONPATH: src
PYTHONDONTWRITEBYTECODE: 1
QT_QPA_PLATFORM: unset

== commands ==
python -m pytest tests --collect-only -q -p no:cacheprovider
python -m pytest tests -q -p no:cacheprovider -rs
python -m compileall -q src tests
python -m bootstrap.app --smoke-test --data-root <temporary directory>

== results ==
collect: 982 collected, EXIT=0
full suite: 976 passed, 6 skipped, EXIT=0
skips: six existing tests/network OpenSSL-unavailable TLS cases
compileall: EXIT=0
smoke: EXIT=0
== audit_exit == 0
```

The evidence is valid for the tracked source/test baseline above. The main
checkout's unrelated dirty files were preserved and are listed in
`doc/STATUS.md`; they were not included in the test result.
