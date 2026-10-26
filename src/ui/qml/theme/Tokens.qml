pragma Singleton
import QtQuick

// T2.1.1 · F "Graphite Atelier" design tokens (ND-1 / DDR-9, DDR-10).
// GENERATED from doc/design/tokens-cand-f.json by verification/T2.1.1/
//    generate_tokens.py -- do not hand-edit values; contract §7 makes
//    the JSON the source of truth. tests/ui_shell/test_design_tokens.py
// fails on any drift between a token here and the contract.
//
// F is dark by default with light fully provided (contract §3, §11).
// Modes are a design-surface concern: nothing in the product switches
// them yet, and wiring a user setting is out of this slice.
QtObject {
    id: tokens

    property string mode: "dark"

    readonly property var _dark: ({
        "bg-page": "#1a1a1d",
        "bg-rail": "#141417",
        "bg-panel": "#222226",
        "bg-raised": "#29292e",
        "bg-inset": "#121215",
        "bg-canvas": "#0e0e10",
        "bg-hover": "#2e2e34",
        "bg-active": "#38383f",
        "bg-press": "#26262b",
        "border": "#34343b",
        "border-strong": "#4a4a54",
        "divider": "#2b2b31",
        "ink": "#ececee",
        "ink-2": "#a9a9b3",
        "ink-3": "#91919c",
        "ink-dis": "#70707b",
        "ink-inv": "#101013",
        "accent": "#4d63e8",
        "accent-hov": "#5f73f0",
        "accent-press": "#3f52d6",
        "accent-text": "#8ca3ff",
        "accent-soft": "rgba(91,118,247,.14)",
        "on-accent": "#ffffff",
        "st-ok": "#4ade80",
        "st-ok-t": "#5ee9a0",
        "st-run": "#60a5fa",
        "st-warn": "#fbbf24",
        "st-warn-t": "#fcd34d",
        "st-fail": "#f87171",
        "st-skip": "#a5b0c0",
        "st-lock": "#c084fc",
        "st-block": "#fdba74",
        "ok-soft": "rgba(74,222,128,.12)",
        "run-soft": "rgba(96,165,250,.13)",
        "warn-soft": "rgba(251,191,36,.12)",
        "fail-soft": "rgba(248,113,113,.13)",
        "skip-soft": "rgba(165,176,192,.12)",
        "lock-soft": "rgba(192,132,252,.13)",
        "block-soft": "rgba(253,186,116,.13)",
        "focus": "#8ca3ff",
        "shadow": "0 6px 18px rgba(0,0,0,.45)",
        "shadow-sm": "0 2px 8px rgba(0,0,0,.4)",
    })

    readonly property var _light: ({
        "bg-page": "#f4f4f3",
        "bg-rail": "#ebebea",
        "bg-panel": "#ffffff",
        "bg-raised": "#ffffff",
        "bg-inset": "#efefee",
        "bg-canvas": "#26262a",
        "bg-hover": "#f0f0ef",
        "bg-active": "#e6e6e4",
        "bg-press": "#e2e2e0",
        "border": "#d9d9d6",
        "border-strong": "#bcbcba",
        "divider": "#e6e6e4",
        "ink": "#1b1b1f",
        "ink-2": "#4f4f58",
        "ink-3": "#63636c",
        "ink-dis": "#8d8d96",
        "ink-inv": "#ffffff",
        "accent": "#4356d6",
        "accent-hov": "#4d61e0",
        "accent-press": "#3a4ac2",
        "accent-text": "#4356d6",
        "accent-soft": "rgba(67,86,214,.10)",
        "on-accent": "#ffffff",
        "st-ok": "#1a7f37",
        "st-ok-t": "#116329",
        "st-run": "#0550ae",
        "st-warn": "#9a6700",
        "st-warn-t": "#7d5200",
        "st-fail": "#c01c28",
        "st-skip": "#57606a",
        "st-lock": "#6639ba",
        "st-block": "#953800",
        "ok-soft": "rgba(26,127,55,.10)",
        "run-soft": "rgba(9,105,218,.10)",
        "warn-soft": "rgba(154,103,0,.11)",
        "fail-soft": "rgba(207,34,46,.10)",
        "skip-soft": "rgba(87,96,106,.11)",
        "lock-soft": "rgba(130,80,223,.11)",
        "block-soft": "rgba(188,76,0,.11)",
        "focus": "#4356d6",
        "shadow": "0 4px 16px rgba(28,28,32,.13)",
        "shadow-sm": "0 1px 5px rgba(28,28,32,.10)",
    })

    readonly property var _geometry: ({
        "fs-base": 13,
        "fs-sm": 12,
        "fs-lg": 14,
        "fs-sub": 16,
        "fs-title": 19,
        "fs-disp": 23,
        "ctl-h": 36,
        "row-h": 42,
        "rail-w": 68,
        "pad-page": 16,
        "gap": 12,
        "rad-sm": 8,
        "rad-md": 11,
        "rad-lg": 14,
        "rad-win": 16,
        "tb-h": 52,
        "list-w": 176,
        "insp-w": 288,
        "prog-h": 150,
        "det-w": 336,
        "card-w": 158,
    })

    readonly property var _palette: mode === "light" ? _light : _dark

    function value(name) {
        var raw = _palette[name];
        return raw === undefined ? "" : raw;
    }

    function geometry(name) {
        var raw = _geometry[name];
        return raw === undefined ? 0 : raw;
    }

    // The contract writes translucent tokens in CSS rgba(). QML rejects
    // that form for a color property, so the conversion happens here and
    // nowhere else: pages keep binding `Tokens.<name>` as a color.
    // An unrecognized value yields a fully transparent color, which the
    // parity test reads as a failure instead of rendering as a guess.
    function colorFor(name) {
        var raw = String(value(name));
        if (raw.charAt(0) === "#") {
            return raw;
        }
        var open = raw.indexOf("(");
        if (raw.indexOf("rgba") === 0 && open > 0) {
            var parts = raw.substring(open + 1, raw.length - 1).split(",");
            if (parts.length === 4) {
                return Qt.rgba(Number(parts[0]) / 255, Number(parts[1]) / 255,
                               Number(parts[2]) / 255, Number(parts[3]));
            }
        }
        return Qt.rgba(0, 0, 0, 0);
    }

    // ---- named surface used by the pages --------------------------
    readonly property color bgPage: colorFor("bg-page")
    readonly property color bgRail: colorFor("bg-rail")
    readonly property color bgPanel: colorFor("bg-panel")
    readonly property color bgRaised: colorFor("bg-raised")
    readonly property color bgInset: colorFor("bg-inset")
    readonly property color bgCanvas: colorFor("bg-canvas")
    readonly property color bgHover: colorFor("bg-hover")
    readonly property color bgActive: colorFor("bg-active")
    readonly property color bgPress: colorFor("bg-press")
    readonly property color border: colorFor("border")
    readonly property color borderStrong: colorFor("border-strong")
    readonly property color divider: colorFor("divider")
    readonly property color ink: colorFor("ink")
    readonly property color ink2: colorFor("ink-2")
    readonly property color ink3: colorFor("ink-3")
    readonly property color inkDis: colorFor("ink-dis")
    readonly property color inkInv: colorFor("ink-inv")
    readonly property color accent: colorFor("accent")
    readonly property color accentHov: colorFor("accent-hov")
    readonly property color accentPress: colorFor("accent-press")
    readonly property color accentText: colorFor("accent-text")
    readonly property color accentSoft: colorFor("accent-soft")
    readonly property color onAccent: colorFor("on-accent")
    readonly property color stOk: colorFor("st-ok")
    readonly property color stOkT: colorFor("st-ok-t")
    readonly property color stRun: colorFor("st-run")
    readonly property color stWarn: colorFor("st-warn")
    readonly property color stWarnT: colorFor("st-warn-t")
    readonly property color stFail: colorFor("st-fail")
    readonly property color stSkip: colorFor("st-skip")
    readonly property color stLock: colorFor("st-lock")
    readonly property color stBlock: colorFor("st-block")
    readonly property color okSoft: colorFor("ok-soft")
    readonly property color runSoft: colorFor("run-soft")
    readonly property color warnSoft: colorFor("warn-soft")
    readonly property color failSoft: colorFor("fail-soft")
    readonly property color skipSoft: colorFor("skip-soft")
    readonly property color lockSoft: colorFor("lock-soft")
    readonly property color blockSoft: colorFor("block-soft")
    readonly property color focus: colorFor("focus")
    readonly property string shadow: value("shadow")
    readonly property string shadowSm: value("shadow-sm")

    // ---- geometry (mode independent) ------------------------
    readonly property int fsBase: geometry("fs-base")
    readonly property int fsSm: geometry("fs-sm")
    readonly property int fsLg: geometry("fs-lg")
    readonly property int fsSub: geometry("fs-sub")
    readonly property int fsTitle: geometry("fs-title")
    readonly property int fsDisp: geometry("fs-disp")
    readonly property int ctlH: geometry("ctl-h")
    readonly property int rowH: geometry("row-h")
    readonly property int railW: geometry("rail-w")
    readonly property int padPage: geometry("pad-page")
    readonly property int gap: geometry("gap")
    readonly property int radSm: geometry("rad-sm")
    readonly property int radMd: geometry("rad-md")
    readonly property int radLg: geometry("rad-lg")
    readonly property int radWin: geometry("rad-win")
    readonly property int tbH: geometry("tb-h")
    readonly property int listW: geometry("list-w")
    readonly property int inspW: geometry("insp-w")
    readonly property int progH: geometry("prog-h")
    readonly property int detW: geometry("det-w")
    readonly property int cardW: geometry("card-w")
}
