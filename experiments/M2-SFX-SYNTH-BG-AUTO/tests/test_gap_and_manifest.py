"""AC2/AC1：缺口检测与 manifest 追加。"""

from __future__ import annotations

import json

from chatgpt_bg import gap as gap_mod

PNG_HDR = b"\x89PNG\r\n\x1a\n"

from chatgpt_bg.prompts import BG_STYLES, build_prompt, style_cycle


def test_count_and_gap(tmp_path):
    assert gap_mod.count_backgrounds(tmp_path) == 0
    rep = gap_mod.check_gap(tmp_path, 5)
    assert rep.missing == 5 and rep.has_gap
    (tmp_path / "bg_001.png").write_bytes(PNG_HDR + b"x")
    (tmp_path / "bg_002.png").write_bytes(PNG_HDR + b"x")
    (tmp_path / "other.txt").write_bytes(b"x")
    (tmp_path / "bg_003.png").write_bytes(b"broken")  # 半写不计入
    assert gap_mod.count_backgrounds(tmp_path) == 2
    assert gap_mod.check_gap(tmp_path, 5).missing == 3


def test_trigger_if_gap_dry_run_and_satisfied(tmp_path):
    fired = []
    rep, triggered = gap_mod.trigger_if_gap(tmp_path, 3, generate_fn=lambda n: fired.append(n), dry_run=True)
    assert rep.missing == 3 and not triggered and fired == []
    rep, triggered = gap_mod.trigger_if_gap(tmp_path, 0, generate_fn=lambda n: fired.append(n))
    assert not rep.has_gap and not triggered
    (tmp_path / "bg_001.png").write_bytes(PNG_HDR + b"x")
    rep, triggered = gap_mod.trigger_if_gap(tmp_path, 1, generate_fn=lambda n: fired.append(n))
    assert not triggered and fired == [], "足量（missing=0）不触发"
    rep2, triggered2 = gap_mod.trigger_if_gap(tmp_path, 2, generate_fn=lambda n: fired.append(n))
    assert triggered2 and fired == [1], "缺 1 张触发补 1 张"


def test_manifest_append_ordered_and_atomic(tmp_path):
    gap_mod.append_manifest(tmp_path, {"file": "bg_001.png"})
    gap_mod.append_manifest(tmp_path, {"file": "bg_002.png"})
    entries = json.loads((tmp_path / "bg_index.json").read_text(encoding="utf-8"))
    assert [e["file"] for e in entries] == ["bg_001.png", "bg_002.png"]
    assert not list(tmp_path.glob("*.tmp")), "原子写不留 tmp"


def test_prompt_library_frozen_constraints():
    assert len(BG_STYLES) >= 20
    for name in BG_STYLES:
        p = build_prompt(name)
        for kw in ("no text", "no characters", "no speech bubbles", "black and white"):
            assert kw in p, f"{name} 缺公共约束 {kw}"


def test_style_cycle_roundrobins():
    cyc = style_cycle(start=19)
    idxs = [next(cyc)[0] for _ in range(3)]
    assert idxs == [19, 20, 21], "跨风格边界继续轮转"
    names = [n for _, n in (lambda c: [next(c) for _ in range(1)])(style_cycle())]
    assert names[0] == list(BG_STYLES)[0]
