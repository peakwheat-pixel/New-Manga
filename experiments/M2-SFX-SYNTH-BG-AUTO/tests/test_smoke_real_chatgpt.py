"""AC5 真实冒烟（manual/slow：需 CHATGPT_BG_SMOKE=1 + 已登录 profile）。

集成方在人工登录后跑：CHATGPT_BG_SMOKE=1 pytest -m slow experiments/M2-SFX-SYNTH-BG-AUTO/tests
取证点：2 张落盘 + bg_index 2 条 + 编号续跑 + src 为 blob 形态 + r2 P1-1 不复现
（manifest 的 chatgpt_blob_src 互不相同）。
"""

import pytest

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        __import__("os").environ.get("CHATGPT_BG_SMOKE") != "1",
        reason="真实冒烟需 CHATGPT_BG_SMOKE=1 + 已登录 profile（manual）",
    ),
]


def test_real_smoke_two_backgrounds(tmp_path):
    from chatgpt_bg.browser import PlaywrightChatGPTDriver
    from chatgpt_bg.cli import DEFAULT_PROFILE_DIR
    from chatgpt_bg.pipeline import generate_backgrounds

    driver = PlaywrightChatGPTDriver(user_data_dir=DEFAULT_PROFILE_DIR, headless=False)
    driver.open_chat()
    try:
        written = generate_backgrounds(driver, tmp_path, count=2, poll_s=5, timeout_s=150)
    finally:
        driver.close()
    assert len(written) == 2, "应落盘 2 张"
    assert all(p.stat().st_size > 10_000 for p in written), "底图应非空（>10KB）"
    import json
    entries = json.loads((tmp_path / "bg_index.json").read_text(encoding="utf-8"))
    assert len(entries) == 2
    srcs = [e["chatgpt_blob_src"] for e in entries]
    assert len(set(srcs)) == 2, "r2 P1-1：两张 blob src 必须不同（不得旧图重复落盘）"
