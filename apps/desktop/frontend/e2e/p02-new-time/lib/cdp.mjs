/**
 * P02-NEW-TIME-X6-AC1-AC7 — zero-dependency CDP client for the embedded
 * WebView2 of the packaged Tauri app (Node >= 22 built-in fetch/WebSocket).
 *
 * The remote debugging endpoint is opened via the official WebView2 loader
 * environment variable WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS; no product
 * source, build output or dependency is touched by this module.
 */

import { spawn } from "node:child_process";

export class CdpConnection {
  /** @param {string} wsUrl */
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    /** @type {Map<number, {resolve: Function, reject: Function}>} */
    this.pending = new Map();
    /** @type {Map<string, Function[]>} event listeners */
    this.listeners = new Map();
    this.ws = null;
  }

  static async fetchTargets(port) {
    const response = await fetch(`http://127.0.0.1:${port}/json/list`, {
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) throw new Error(`cdp /json/list HTTP ${response.status}`);
    return response.json();
  }

  static async fetchVersion(port) {
    const response = await fetch(`http://127.0.0.1:${port}/json/version`, {
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) throw new Error(`cdp /json/version HTTP ${response.status}`);
    return response.json();
  }

  /** Poll until the debugging endpoint answers (app cold start). */
  static async waitForEndpoint(port, timeoutMs = 30000) {
    const deadline = Date.now() + timeoutMs;
    let lastError = null;
    while (Date.now() < deadline) {
      try {
        return await CdpConnection.fetchVersion(port);
      } catch (error) {
        lastError = error;
        await sleep(400);
      }
    }
    throw new Error(`CDP endpoint never appeared: ${lastError}`);
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
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Evaluate an expression in the page and return the JSON value. */
export async function evaluate(cdp, expression, awaitPromise = true) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(`page eval failed: ${JSON.stringify(result.exceptionDetails).slice(0, 500)}`);
  }
  return result.result?.value;
}

/**
 * Install the invoke-observer/mock wrapper as a new-document script and
 * reload the page, so EVERY product module resolves the wrapped
 * window.__TAURI__.core.invoke from boot.
 *
 * mockHandlers: { [command]: (args) => value | Promise<value> } — a command
 * present in the map is answered by the mock (which may throw to emulate a
 * denial); commands absent from the map pass through to the REAL Tauri
 * bridge. The wrapper records every call (command, args, wall clock,
 * performance.now()) both in window.__p02InvokeLog (page-side array) and
 * through Runtime binding events (Node-side log).
 */
export const INVOKE_WRAPPER_SOURCE = String.raw`
(() => {
  if (window.__p02InvokeWrapperInstalled) return;
  const core = window.__TAURI__ && window.__TAURI__.core;
  if (!core || typeof core.invoke !== "function") {
    window.__p02InvokeWrapperState = "TAURI_BRIDGE_MISSING";
    return;
  }
  const realInvoke = core.invoke;
  window.__p02InvokeLog = [];
  window.__p02InvokeWrapperState = "ACTIVE";
  window.__p02MockHandlers = window.__p02MockHandlers || {};
  const report = (entry) => {
    try { window.__p02Event(JSON.stringify(entry)); } catch {}
  };
  core.invoke = function patchedInvoke(command, args) {
    const startedAt = performance.now();
    const entry = {
      command,
      args,
      pagePerfNow: startedAt,
      pageEpoch: Math.floor(Date.now()),
      kind: "invoke",
    };
    window.__p02InvokeLog.push(entry);
    report(entry);
    const handler = window.__p02MockHandlers[command];
    if (handler) {
      return Promise.resolve()
        .then(() => handler(args || {}))
        .then((value) => {
          const done = { kind: "settled", command, status: "resolved", pagePerfNow: performance.now(), pageEpoch: Math.floor(Date.now()) };
          window.__p02InvokeLog.push(done);
          report(done);
          return value;
        })
        .catch (function failed(error) {
          const done = { kind: "settled", command, status: "rejected", error: String(error && error.message ? error.message : error), pagePerfNow: performance.now(), pageEpoch: Math.floor(Date.now()) };
          window.__p02InvokeLog.push(done);
          report(done);
          throw error;
        });
    }
    return realInvoke(command, args).then(
      (value) => {
        const done = { kind: "settled", command, status: "resolved", pagePerfNow: performance.now(), pageEpoch: Math.floor(Date.now()) };
        window.__p02InvokeLog.push(done);
        report(done);
        return value;
      },
      (error) => {
        const done = { kind: "settled", command, status: "rejected", error: String(error && error.message ? error.message : error), pagePerfNow: performance.now(), pageEpoch: Math.floor(Date.now()) };
        window.__p02InvokeLog.push(done);
        report(done);
        throw error;
      },
    );
  };
  window.__p02InvokeWrapperInstalled = true;
})();
`;

/**
 * Real keyboard text typing through CDP key events (keyDown/char/keyUp per
 * character) into the currently focused element — the same pipeline real
 * keyboard input takes inside WebView2.
 */
export async function typeText(cdp, text) {
  for (const char of text) {
    await cdp.send("Input.dispatchKeyEvent", {
      type: "keyDown",
      text: char,
      key: char,
      unmodifiedText: char,
      windowsVirtualKeyCode: char.charCodeAt(0),
      nativeVirtualKeyCode: char.charCodeAt(0),
    });
    await cdp.send("Input.dispatchKeyEvent", {
      type: "keyUp",
      key: char,
      windowsVirtualKeyCode: char.charCodeAt(0),
      nativeVirtualKeyCode: char.charCodeAt(0),
    });
  }
}

export async function pressKey(cdp, key, { code, windowsVirtualKeyCode, text = undefined } = {}) {
  const base = {
    key,
    code: code || key,
    windowsVirtualKeyCode,
    nativeVirtualKeyCode: windowsVirtualKeyCode,
  };
  if (text !== undefined) base.text = text;
  await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", ...base });
  await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", ...base });
}

/** Left mouse click at page coordinates. */
export async function mouseClick(cdp, x, y, { button = "left", clickCount = 1 } = {}) {
  await cdp.send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button, clickCount });
  await cdp.send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button, clickCount });
}

/** Query an element's bounding rect by testid selector. */
export async function rectOf(cdp, selector) {
  return evaluate(
    cdp,
    `(() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height,
               cx: r.x + r.width / 2, cy: r.y + r.height / 2,
               tag: el.tagName, text: (el.textContent || "").slice(0, 60) };
    })()`,
    false,
  );
}

/** tasklist /FO CSV /NH process census (project-precedent process view). */
export function listProcesses(filterNames) {
  return new Promise((resolve, reject) => {
    const child = spawn("tasklist", ["/FO", "CSV", "/NH"], {
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (chunk) => (out += chunk.toString("utf16le")));
    child.stderr.on("data", (chunk) => (err += chunk.toString("utf16le")));
    child.on("error", reject);
    child.on("close", (code) => {
      // tasklist /FO CSV emits the console codepage; decode both ways and
      // keep whichever parses (mbcs on zh-CN hosts).
      let text = out;
      const alt = Buffer.from(out, "binary").toString("latin1");
      const lines = (text.length >= alt.length ? text : alt).split(/\r?\n/);
      const rows = [];
      for (const line of lines) {
        const match = line.match(/^"([^"]+)","(\d+)","([^"]*)","(\d+)","(\d+)","(\d+)"/);
        if (match) rows.push({ name: match[1], pid: Number(match[2]), session: match[4], memK: Number(match[5]) });
      }
      resolve({ exit: code, rows, stderr: err.trim(), matched: rows.filter((row) => filterNames.some((name) => row.name.toLowerCase() === name.toLowerCase())) });
    });
  });
}
