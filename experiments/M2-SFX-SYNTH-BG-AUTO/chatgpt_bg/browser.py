"""AC1/AC3：ChatGPT 网页驱动抽象层。

ChatGPTDriver 是 Protocol（测试用 mock 实现之）；PlaywrightChatGPTDriver 是
Playwright 实现（延迟 import——单测环境无需装 playwright）。实测四坑固化于
实现内：发送点发送按钮（Enter 不可靠）；完成判据=blob src 变化且无
停止/微调/思考中；微调(98%)阶段排除；思考卡死超时 reload 重发。
"""

from __future__ import annotations

import time
from typing import Protocol, runtime_checkable

BLOB_PREFIX = "blob:"


class BGGenerationError(RuntimeError):
    """fail-closed：生成失败且重试耗尽（AC3，禁止静默降级）。"""

    def __init__(self, state: str, detail: str):
        super().__init__(f"[{state}] {detail}")
        self.state = state
        self.detail = detail


@runtime_checkable
class ChatGPTDriver(Protocol):
    """浏览器交互抽象（mock 与 Playwright 实现共同合同）。"""

    def open_chat(self) -> None: ...
    def is_logged_in(self) -> bool: ...
    def send_prompt(self, text: str) -> None: ...
    def latest_image_src(self) -> str | None: ...
    def is_busy(self) -> bool: ...
    def blocking_state(self) -> str | None: ...
    def reload(self) -> None: ...
    def fetch_image_bytes(self, src: str) -> bytes: ...
    def close(self) -> None: ...


def wait_new_image(
    driver: ChatGPTDriver,
    prev_src: str | None,
    timeout_s: int = 150,
    poll_s: int = 5,
) -> str:
    """轮询等待新图（AC1 判据：最新 blob src 变化 + 无忙碌标记）。

    超时抛 TimeoutError（pipeline 转 reload 重发，实测坑④：思考卡死不自愈）。
    阻塞态（Cloudflare/未登录/限额）立即抛 BGGenerationError（AC3 fail-closed）。
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        state = driver.blocking_state()
        if state is not None:
            code, _, detail = state.partition("：")
            raise BGGenerationError(code or "BLOCKED", detail or state)
        if not driver.is_busy():
            src = driver.latest_image_src()
            if src and src.startswith(BLOB_PREFIX) and src != prev_src:
                return src
        time.sleep(poll_s)
    raise TimeoutError(f"生成等待超时 {timeout_s}s")


class PlaywrightChatGPTDriver:
    """Playwright 实现：persistent context + 本机 Chrome（真实指纹，降低自动化检测）。"""

    def __init__(self, user_data_dir: str, headless: bool = False, timeout_ms: int = 3000):
        self.user_data_dir = user_data_dir
        self.headless = headless
        self._timeout_ms = timeout_ms
        self._pw = None
        self._ctx = None
        self._page = None

    # -- 生命周期 --
    def open_chat(self) -> None:
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self._ctx = self._pw.chromium.launch_persistent_context(
            self.user_data_dir,
            channel="chrome",
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
        )
        self._page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()
        self._page.goto("https://chatgpt.com/", wait_until="domcontentloaded")
        self._page.wait_for_timeout(6000)  # 首屏/Cloudflare 稳定窗

    def close(self) -> None:
        if self._ctx:
            self._ctx.close()
        if self._pw:
            self._pw.stop()

    # -- 状态 --
    def is_logged_in(self) -> bool:
        page = self._page
        if page.get_by_role("button", name="登录").count() > 0:
            return False
        return (page.get_by_role("button", name="打开个人资料菜单").count() > 0
                or page.locator('[data-testid="profile-button"]').count() > 0)

    def blocking_state(self) -> str | None:
        """返回机器可读状态码|人工处置说明（r2 P2-2：状态码不再折叠为 BLOCKED）。"""
        page = self._page
        title = page.title() or ""
        if "请稍候" in title or "Just a moment" in title:
            return "CLOUDFLARE_CHALLENGE：人机验证页未通过（等待人工或稍后重试）"
        if page.get_by_text("登录或注册").count() > 0 and not self.is_logged_in():
            return "NOT_LOGGED_IN：登录态丢失（跑 chatgpt_bg login 重新登录）"
        for marker in ("您已达到使用上限", "usage cap", "rate limit", "请求过于频繁", "稍后再试"):
            if page.get_by_text(marker, exact=False).count() > 0:
                return "RATE_LIMITED：触发 ChatGPT 限额/风控（等待或换账号）"
        return None

    def is_busy(self) -> bool:
        """生成中判定（r2 P2-1）：停止按钮定位器优先（inner_text 取不到 aria-label），
        文本兜底只扫最后一条 assistant 消息（历史消息的旧文本不参与）。"""
        page = self._page
        if page.locator('[data-testid="stop-button"]').count() > 0:
            return True
        if page.locator('button[aria-label*="Stop" i]').count() > 0:
            return True
        turns = page.locator('main [data-message-author-role="assistant"]')
        if turns.count() == 0:
            return False
        tail = turns.last.inner_text() if turns.last.count() else ""
        return ("微调" in tail) or ("思考中" in tail) or ("98%" in tail)

    # -- 动作 --
    def send_prompt(self, text: str) -> None:
        page = self._page
        box = page.get_by_role("textbox", name="询问 ChatGPT")
        if box.count() == 0:
            box = page.locator("#prompt-textarea")
        box.first.wait_for(state="visible", timeout=self._timeout_ms)
        box.first.click()
        box.first.fill(text)
        page.wait_for_timeout(800)
        # 发送按钮：data-testid 优先，aria 名兜底；Enter 在对话页不可靠（实测坑①）
        btn = page.locator('[data-testid="send-button"]')
        if btn.count() == 0:
            btn = page.get_by_role("button", name="发送")
        if btn.count() == 0:
            btn = page.locator('button[aria-label*="Send" i]')
        btn.first.click(timeout=self._timeout_ms)

    def latest_image_src(self) -> str | None:
        imgs = self._page.locator('main img[src^="blob:"]')
        if imgs.count() == 0:
            return None
        return imgs.last.get_attribute("src")

    def reload(self) -> None:
        self._page.reload(wait_until="domcontentloaded")
        self._page.wait_for_timeout(5000)

    def fetch_image_bytes(self, src: str) -> bytes:
        """页面内 fetch blob→base64→bytes（blob URL 出不了页面上下文）。"""
        data_url = self._page.evaluate(
            """async (u) => {
                const r = await fetch(u);
                const blob = await r.blob();
                const fr = new FileReader();
                return await new Promise((res, rej) => {
                    fr.onload = () => res(fr.result);
                    fr.onerror = rej;
                    fr.readAsDataURL(blob);
                });
            }""",
            src,
        )
        import base64

        return base64.b64decode(str(data_url).split(",", 1)[1])
