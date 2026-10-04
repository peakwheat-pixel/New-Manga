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
    def latest_image_src(self):
        if self.script:
            return self.script.pop(0)
        return "blob:last" if self.sent else None
    def fetch_image_bytes(self, src): self.fetched.append(src); return PNG


def test_generates_and_persists_each(tmp_path):
    d = MockDriver(script=[None, "blob:s1", None, "blob:s2"])
    written = generate_backgrounds(d, tmp_path, count=2, poll_s=0)  # r2: 签名去 min_backgrounds
    assert len(written) == 2 and all(p.exists() for p in written)
    assert all(p.read_bytes().startswith(PNG) for p in written)
    import json
    entries = json.loads((tmp_path / "bg_index.json").read_text(encoding="utf-8"))
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
    assert ei.value.state == "CLOUDFLARE_CHALLENGE", "r2 P2-2：子类状态码不再折叠"


def test_fail_closed_consecutive_failures(tmp_path):
    # 永远等不到新图（src 恒 None）+ reload 也不行 → 连续 3 张失败停批
    class Stuck(MockDriver):
        def latest_image_src(self): return None
    d = Stuck(script=[])
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=2, poll_s=0, timeout_s=1)
    assert ei.value.state == "CONSECUTIVE_FAILURES"
    assert d.reloaded >= 2, "每张超时应 reload 重发一次（实测坑④）"


def test_non_png_dropped_counts_as_failure(tmp_path):
    class BadPng(MockDriver):
        def fetch_image_bytes(self, src): return b"NOTPNG" + b"0" * 16
    d = BadPng(script=[None] * 9)
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=1, poll_s=0, timeout_s=1)
    assert ei.value.state == "CONSECUTIVE_FAILURES"
    assert not list(tmp_path.glob("bg_*.png")), "坏图不得落盘"


def test_reload_then_success(tmp_path):
    # r2 P1-1 回归：超时→reload→重取基准→重发后出新图成功续跑
    # 状态驱动 mock：reload 前 latest 恒 None（卡死触发超时）；reload 后首读返回
    # "旧图新 URL"（stale），后续返回真新图——pipeline 未重取基准时会误判 stale 落盘。
    class ReloadOk(MockDriver):
        def __init__(self):
            super().__init__(script=[])
            self.reloaded = 0
            self.post_reload_reads = 0

        def reload(self):
            self.reloaded += 1

        def latest_image_src(self):
            if self.reloaded == 0:
                return None
            self.post_reload_reads += 1
            if self.post_reload_reads == 1:
                return "blob:stale-new-url-after-reload"
            return "blob:real-new-image"

    d = ReloadOk()
    written = generate_backgrounds(d, tmp_path, count=1, poll_s=0, timeout_s=1)
    assert d.reloaded == 1, "应触发一次 reload 重发"
    assert len(written) == 1
    import json
    e = json.loads((tmp_path / "bg_index.json").read_text(encoding="utf-8"))[0]
    assert e["chatgpt_blob_src"] == "blob:real-new-image", "落盘的必须是真新图而非 stale 旧图"


def test_resume_numbering(tmp_path):
    (tmp_path / "bg_007.png").write_bytes(PNG)
    d = MockDriver(script=[None, "blob:s8"])
    written = generate_backgrounds(d, tmp_path, count=1, poll_s=0)
    assert written[0].name == "bg_008.png", "断点续跑按既有最大编号续"


def test_reload_rechecks_blocking_state(tmp_path):
    """r3 P3-4 回归：reload 后登录态丢失应报 NOT_LOGGED_IN 而非计入连续失败。"""
    class ReloadLostLogin(MockDriver):
        def __init__(self):
            super().__init__(script=[])
            self.reloaded = 0
        def reload(self):
            self.reloaded += 1
        def is_logged_in(self):
            return self.reloaded == 0
        def latest_image_src(self):
            return None  # 卡死：永远等不到新图（触发超时→reload）
        def blocking_state(self):
            if self.reloaded:
                return "NOT_LOGGED_IN：登录态丢失（跑 chatgpt_bg login 重新登录）"
            return None

    d = ReloadLostLogin()
    with pytest.raises(BGGenerationError) as ei:
        generate_backgrounds(d, tmp_path, count=1, poll_s=0, timeout_s=1)
    assert ei.value.state == "NOT_LOGGED_IN"
