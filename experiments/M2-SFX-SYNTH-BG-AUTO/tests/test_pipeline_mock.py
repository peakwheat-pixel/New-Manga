"""AC1/AC3：管线行为（mock driver，不联网）。"""

from __future__ import annotations

import pytest

from chatgpt_bg.browser import BGGenerationError
from chatgpt_bg.pipeline import generate_backgrounds

PNG = b"\x89PNG\r\n\x1a\n" + b"fakepngdata" * 10


class MockDriver:
    """可脚本化的 driver：src 序列驱动完成判定。"""

    def __init__(self, script, logged_in=True, blocking=None):
        self.script = list(script)  # 每次 latest_image_src 弹出一项（None=无图）
        self.sent = []
        self.reloaded = 0
        self.fetched = []
        self.logged_in = logged_in
        self.blocking = blocking

    def open_chat(self): ...
    def close(self): ...
    def reload(self): self.reloaded += 1
    def is_logged_in(self): return self.logged_in
    def blocking_state(self): return self.blocking
    def is_busy(self): return False
    def send_prompt(self, text): self.sent.append(text)
    def latest_image_src(self): return self.script.pop(0) if self.script else self.sent and ("blob:last",)
    def fetch_image_bytes(self, src): self.fetched.append(src); return PNG


def test_generates_and_persists_each(tmp_path):
    d = MockDriver(script=[None, "blob:s1", None, "blob:s2"])
    written = generate_backgrounds(d, tmp_path, count=2, poll_s=0)
    assert len(written) == 2 and all(p.exists() for p in written)
    assert all(p.read_bytes().startswith(PNG) for p in written)
    import json
    entries = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert [e["file"] for e in entries] == ["bg_001.png", "bg_002.png"]
    assert entries[0]["source"] == "chatgpt-web-auto" and entries[0]["style"]


def test_fail_closed_not_logged_in(tmp_path):
    d = MockDriver(script=[], logged_in=False)
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=1)
    assert ei.value.state == "NOT_LOGGED_IN"


def test_fail_closed_blocking_state(tmp_path):
    d = MockDriver(script=[], blocking="CLOUDFLARE_CHALLENGE：验证")
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=1, poll_s=0, timeout_s=1)
    assert ei.value.state == "BLOCKED"


def test_fail_closed_consecutive_failures(tmp_path):
    # 永远等不到新图（src 恒 None）+ reload 也不行 → 连续 3 张失败停批
    class Stuck(MockDriver):
        def latest_image_src(self): return None
    d = Stuck(script=[])
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=2, poll_s=0, timeout_s=1)
    assert ei.value.state == "CONSECUTIVE_FAILURES"
    assert d.reloaded >= 2, "每张超时应 reload 重发一次（实测坑④）"


def test_resume_numbering(tmp_path):
    (tmp_path / "bg_007.png").write_bytes(PNG)
    d = MockDriver(script=[None, "blob:s8"])
    written = generate_backgrounds(d, tmp_path, count=1, poll_s=0)
    assert written[0].name == "bg_008.png", "断点续跑按既有最大编号续"
