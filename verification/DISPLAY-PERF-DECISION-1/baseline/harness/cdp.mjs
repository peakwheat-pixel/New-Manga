/**
 * DISPLAY-PERF-DECISION-1 / baseline — minimal zero-dependency CDP client for
 * the embedded WebView2 of the packaged Tauri app (Node >= 22 globals).
 *
 * Written for this Task only; the uiux-v2 client was read for reference but is
 * neither imported nor modified, so no cross-Task coupling exists.
 */

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function delay(ms) {
  return sleep(ms);
}

export class Cdp {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
    this.ws = null;
    this.closed = false;
  }

  static async fetchTargets(port) {
    const response = await fetch(`http://127.0.0.1:${port}/json/list`, {
      signal: AbortSignal.timeout(2500),
    });
    if (!response.ok) throw new Error(`cdp /json/list HTTP ${response.status}`);
    return response.json();
  }

  static async fetchVersion(port) {
    const response = await fetch(`http://127.0.0.1:${port}/json/version`, {
      signal: AbortSignal.timeout(2500),
    });
    if (!response.ok) throw new Error(`cdp /json/version HTTP ${response.status}`);
    return response.json();
  }

  /** Poll until the debugging endpoint answers; returns [version, epochMs]. */
  static async waitForEndpoint(port, timeoutMs = 60000, intervalMs = 40) {
    const deadline = Date.now() + timeoutMs;
    let lastError = null;
    while (Date.now() < deadline) {
      try {
        const version = await Cdp.fetchVersion(port);
        return { version, epochMs: Date.now() };
      } catch (error) {
        lastError = error;
        await sleep(intervalMs);
      }
    }
    throw new Error(`CDP endpoint never appeared on ${port}: ${lastError}`);
  }

  async open() {
    this.ws = new WebSocket(this.wsUrl);
    this.ws.addEventListener("message", (event) => this.#onMessage(String(event.data)));
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", () => resolve(), { once: true });
      this.ws.addEventListener("error", () => reject(new Error("CDP websocket error")), { once: true });
    });
    return this;
  }

  #onMessage(text) {
    let message;
    try {
      message = JSON.parse(text);
    } catch {
      return;
    }
    if (message.id !== undefined && this.pending.has(message.id)) {
      const { resolve, reject } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(`CDP ${message.error.message}`));
      else resolve(message.result);
      return;
    }
    if (message.method !== undefined) {
      const handlers = this.listeners.get(message.method);
      if (handlers) for (const handler of handlers) handler(message.params);
    }
  }

  on(method, handler) {
    if (!this.listeners.has(method)) this.listeners.set(method, []);
    this.listeners.get(method).push(handler);
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      try {
        this.ws.send(JSON.stringify({ id, method, params }));
      } catch (error) {
        this.pending.delete(id);
        reject(error);
      }
    });
  }

  /** Evaluate in the page and return the JSON value. */
  async eval(expression, { awaitPromise = true, timeoutMs = 30000 } = {}) {
    const timer = setTimeout(() => {
      /* the ws message may still arrive; caller handles the rejection below */
    }, timeoutMs);
    timer.unref?.();
    try {
      const result = await this.send("Runtime.evaluate", {
        expression,
        awaitPromise,
        returnByValue: true,
      });
      if (result.exceptionDetails) {
        const detail = JSON.stringify(result.exceptionDetails).slice(0, 700);
        throw new Error(`page eval failed: ${detail}`);
      }
      return result.result?.value;
    } finally {
      clearTimeout(timer);
    }
  }

  async screenshotBase64() {
    const result = await this.send("Page.captureScreenshot", { format: "png", fromSurface: true });
    return result.data;
  }

  async close() {
    this.closed = true;
    try {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
    } catch {}
  }
}

/** Attach to the Tauri page target, polling until it exists. */
export async function attachPage(port, { timeoutMs = 45000, onTarget } = {}) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const targets = await Cdp.fetchTargets(port);
      const page =
        targets.find((t) => t.type === "page" && /tauri/i.test(t.url || "")) ||
        targets.find((t) => t.type === "page");
      if (page && page.webSocketDebuggerUrl) {
        const cdp = await new Cdp(page.webSocketDebuggerUrl).open();
        await cdp.send("Runtime.enable").catch(() => {});
        await cdp.send("Page.enable").catch(() => {});
        if (onTarget) onTarget({ page, targets, epochMs: Date.now() });
        return { cdp, page, targets };
      }
    } catch (error) {
      lastError = error;
    }
    await sleep(25);
  }
  throw new Error(`no page target on CDP endpoint ${port}: ${lastError}`);
}
