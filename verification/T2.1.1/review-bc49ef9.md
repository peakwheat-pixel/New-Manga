# T2.1.1 Non-author Review — delivery `bc49ef9`

## Review identity

- Repository: `G:/CODEX/New Manga`
- Base: `7f34135`
- Implementation delivery: `bc49ef9`
- Author evidence/Handoff head: `ddb2044` (evidence/docs only after `bc49ef9`)
- Author: Qoder
- Reviewer/integrator: Codex
- Author branch: `agent/qoder/T2.1.1-design-f-qml`
- Author worktree was clean at review time.

## Scope decision before code review

1. `Main.qml` palette roles and `AppShell.qml` rail width are in scope. The
   released write set is `src/ui/qml/**`; the palette binding is required for
   Qt Controls and Labels to consume the F surface through the real entry
   window. No bootstrap or context-property seam was changed.
2. `SettingsView.qml` is also in scope as QML presentation code. The delivery
   changes only colors/borders and the theme import; it does not change the
   Settings service, ViewModel, persistence, or form behavior.
3. The CanvasCaption pill is an accepted F implementation of the `.vfloat`
   pattern. In light mode `bg-canvas=#26262a` cannot carry the ink tokens at
   4.5:1, so viewer/overlay captions need the audited panel ground.
4. The reader page shell remains `bg-page` while the paged image viewport uses
   `bg-canvas`. This is accepted as a bounded shell/viewport interpretation,
   but the webtoon `Flickable` still has no explicit canvas ground and is
   recorded as an IMPORTANT deferred consistency finding below.

## Findings and disposition

### BLOCKING

**B-001 — navigation status badge violated the F status contract — RESOLVED.**

`src/ui/qml/shell/NavBadge.qml` used `Tokens.stRun` as a solid background and
`Tokens.onAccent` as the label color. This produced the recorded 2.54:1 dark
contrast and did not implement the §7.2 `*-soft` ground + `st-*` text triple
encoding. A focused test was first run red, then the minimum fix changed the
badge to `Tokens.runSoft` + `Tokens.stRun`. Codex fix commit:
`5da1cf6`. The focused guard is now green.

### IMPORTANT

**I-001 — webtoon canvas ground is not the paged canvas ground — DEFER.**

`ReaderView.qml` gives the paged viewer `Tokens.bgCanvas`, but its production
`Flickable` has no background item and therefore exposes the page shell
`Tokens.bgPage`. This is a visual consistency gap, not a data or navigation
failure. It is assigned to the already proposed T2.2.1 Reader & Workbench
Polish window; no scope expansion was made here.

**I-002 — platform ComboBox/Dialog styling remains only palette-driven — DEFER.**

The top-level window palette is correctly wired, but platform popup/dialog
shape details are not fully restyled to every F radius/control token. This is
visual polish, not a broken production path, and remains outside this bounded
token/application slice.

**I-003 — no GUI visual/DPI manual evidence — DEFER.**

The author explicitly recorded GUI visual inspection as `NOT_RUN`. Real QML
load, the full QML suites, bootstrap smoke, and source/static gates run; no
claim of human visual acceptance is made. A manual visual pass remains a
follow-up release check if required before packaging.

### NON_BLOCKING

- F-01: `Tokens.mode` is dark by default and has no user setting seam yet;
  light values are present and parity-tested. Defer theme switching to a
  released Settings/UI task.
- F-02: the six Region pipeline states have no current production renderer;
  accepted/completed semantic tokens and contrast are tested, while the
  missing renderer is not invented in this task.
- F-04: `*-soft` audit uses the panel ground while shelf cards are raised;
  the independently reported worst contrast remains 4.93:1, above 4.5:1.
- F-06: ROI selected fill is a pre-existing paint-path follow-up; no headless
  paint claim is made here.
- F-10: the author commit chain is linear and reversible; no action required.

F-09 documentation drift is closed by the Codex governance update accompanying
the integration. No author branch history was rewritten.

## Architecture / standards review

- `Tokens.qml` is a `pragma Singleton` registered by `qmldir`; its 42 color
  values per mode and 21 geometry values are parity-tested against the F JSON.
- QML changes stay under `src/ui/qml/**`; no `src/**/*.py`, bootstrap, ports,
  schema, provider/runtime, or dependency file was changed.
- `Main.qml` and `ExportWindow.qml` each declare the needed flat Qt palette
  roles; the second top-level window does not rely on inheritance.
- QML does not add database, filesystem, provider, or model construction
  paths. Existing dialogs continue to delegate through existing ViewModels.
- Existing object names, page routes, and ViewModel context-property contracts
  remain intact in the fresh QML suites and smoke path.

## Verification review

The author mutation record `verification/T2.1.1/mutation-discrimination-bc49ef9.md`
contains seven target-logic mutations (color, size, palette, card geometry,
and graphic-only status tokens). M5/M6 initially escaped and were repaired;
the recorded restore check is clean. The final author worktree was clean and
the Codex B-001 focused mutation was independently reproduced red then green.

Fresh on the Codex integration worktree, after `5da1cf6`:

| Gate | Result |
|---|---|
| `pytest tests/ui_shell tests/workbench tests/reading_export -q -p no:cacheprovider -rs` | **382 passed**, 0 failed, exit 0 |
| `pytest tests -q -p no:cacheprovider -rs` | **1178 passed, 11 skipped, 0 failed, 1 warning**, exit 0 |
| `python -m compileall -q src tests` | exit 0 |
| `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` | exit 0; fresh SQLite created |
| `git diff --check -- src tests doc verification` | clean, exit 0 |

The full-suite skip delta from the author’s 1183/5 evidence is environmental:
this environment lacks docTR, numpy, torch, and OpenSSL. The skipped tests
were reported as skips, not failures; the author’s evidence remains useful
for the dependency-equipped run and is not silently reclassified.

## Review decision

**APPROVED FOR CODEX INTEGRATION.** The one blocking finding was repaired in
the isolated integration worktree and fresh evidence is green. The deferred
items above do not block T2.1.1 integration, but T2.1.1 must not be described
as human-GUI/DPI accepted beyond the evidence recorded here.
