# T2.1.1 — mutation discrimination (delivery HEAD bc49ef9)

Each row applies the regression by hand to a committed file, runs
`tests/ui_shell/test_design_f_applied.py` (plus `tests/workbench` where noted),
then restores with `git checkout --`. A guard that stays green under its own
mutation is not a guard, so all seven were measured rather than assumed.

| # | Mutation (the regression the task is meant to catch) | Result |
|---|---|---|
| M1 | `Tokens.bgHover : Tokens.bgRaised` → `Tokens.bgHover : "#fafafa"` in `BookCard.qml` | FAIL `test_no_page_re_declares_a_color_literal` — reports `{'bookshelf\BookCard.qml': ['#fafafa']}` |
| M2 | `font.pixelSize: Tokens.fsSm` → `font.pixelSize: 11` in `RegionInspector.qml` | FAIL `test_no_page_hardcodes_a_font_size` |
| M3 | delete `palette.windowText: Tokens.ink` from `Main.qml` | FAIL `test_both_top_level_windows_declare_the_same_palette_surface` **and** `test_every_text_in_the_product_tree_resolves_to_a_token` |
| M4 | `cellWidth: Tokens.cardW + shelfList.cardGutter * 2` → `cellWidth: 168` (the pre-F cell) in `BookGrid.qml` | FAIL static cell guard **and** `test_bookshelf_cells_are_the_accepted_158px_grid` |
| M5 | `fg: Tokens.stOkT` → `fg: Tokens.stOk` in `TaskProgressPanel.badgeStyles` | FAIL `test_no_label_paints_with_a_graphic_only_token` |
| M6 | `completed: Tokens.stOkT,` → `completed: Tokens.stOk,` in `PageListPanel.qml` status map | FAIL `test_no_label_paints_with_a_graphic_only_token` |
| M7 | delete `import "../theme"` from `BookGrid.qml` | FAIL `test_every_file_that_reads_tokens_imports_the_module` + the runtime 158px grid test |

## M5/M6 are the reason the graphic-token rule exists

The first version of that guard anchored `color:` / `fg:` to line start. Both
mutations passed the whole suite with the defect in place, because QML object
literals put the binding mid-line:

```qml
completed:  { bg: Tokens.okSoft, fg: Tokens.stOk, glyph: "✓" },
```

The rule was rewritten to read per line and excuse only stroke/fill/border
contexts, and re-mutated: M5 and M6 now fail. Neither contrast check notices
under M5/M6 — they audit token pairs, not page bindings — and the ratio is not
a reliable proxy anyway: `st-ok` on `bg-raised` measures 5.08:1 light and
7.02:1 dark, so it clears the bar while still being the wrong token. Only
`st-ok` on `ok-soft` in light mode (4.43:1) happens to fall below it, which is
the evidence that the contract picked `st-ok-t` deliberately rather than
arbitrarily.

## M3 is the reason the palette is asserted two ways

`test_every_text_in_the_product_tree_resolves_to_a_token` walks the real
`Main.qml` tree. Under M3 it catches text resolving to `#ff000000`; the static
role-list test catches the same edit without Qt. One guard is a message, the
other is the user-visible failure.
