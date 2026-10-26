/**
 * DISPLAY-PERF-DECISION-1 / baseline — isolated launch environment.
 *
 * Owner: teammate `baseline-scout` (task-3). Self-contained: this file does NOT
 * import the uiux-v2 harness (that one is only read for reference), and no run
 * of this file can write into another Task's evidence tree.
 *
 * Isolation contract (every writable path the packaged app can reach):
 *   G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/runs/<label>/
 * The user's real %APPDATA% / %LOCALAPPDATA% / media library is never touched:
 * every root below is re-derived under the Task environment root above.
 */

import { existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

export const TASK_ENV_ROOT =
  "G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1";

/** Release exe pinned by the parent Task (SHA-256 recorded below).
 * `DP1_EXE` lets a measured run point at the preserved baseline copy or at the
 * CDP-enabled acceptance build; the report always records which exe ran. */
export const PINNED_EXE =
  process.env.DP1_EXE ||
  "G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/new-manga.exe";
export const PINNED_EXE_SHA256 =
  "1136bb0a8d582a30c6ef0b16959b86a62dd26d2c6d9ce49e298c9b86c3343226";

/** Evidence root inside the repo (the ONLY in-repo write scope of task-3). */
export const EVIDENCE_ROOT =
  "G:/CODEX/New Manga/verification/DISPLAY-PERF-DECISION-1/baseline";

/** CDP port base; each launch gets base+offset so a stale endpoint can never
 * be mistaken for a fresh one. Task hard constraint: >= 9360. */
export const CDP_PORT_BASE = 9361;

export const runRootFor = (label) => path.join(TASK_ENV_ROOT, "runs", label);
export const evidenceFor = (...parts) => path.join(EVIDENCE_ROOT, ...parts);

/** Sub-launch dirs — all app-visible writable roots live under scenarioRoot. */
export const launchDirs = (scenarioRoot) => ({
  roaming: path.join(scenarioRoot, "appdata-roaming"),
  localAppData: path.join(scenarioRoot, "appdata-local"),
  tmp: path.join(scenarioRoot, "tmp"),
  dataRoot: path.join(scenarioRoot, "data-root"),
  derived: path.join(scenarioRoot, "scope", "derived"),
  managed: path.join(scenarioRoot, "scope", "managed"),
  catalogDb: path.join(scenarioRoot, "catalog", "catalog.sqlite"),
  webview2Udd: path.join(scenarioRoot, "webview2-udd"),
  logs: path.join(scenarioRoot, "logs"),
  shots: path.join(scenarioRoot, "shots"),
  probe: path.join(scenarioRoot, "probe"),
});

/**
 * Safety precondition: every Task-local target the app will write must be
 * ABSENT or EMPTY before launch; anything else means a previous run left state
 * behind and the label must be changed instead of overwriting evidence.
 */
export function assertLaunchTargetsClean(scenarioRoot) {
  if (process.env.DP1_ALLOW_DIRTY === "1") { return { __allowDirty: true, path: scenarioRoot }; }
  const dirs = launchDirs(scenarioRoot);
  const observed = {};
  for (const [name, target] of Object.entries(dirs)) {
    if (!existsSync(target)) {
      observed[name] = { path: target, state: "ABSENT" };
      continue;
    }
    const stat = statSync(target);
    if (!stat.isDirectory()) throw new Error(`PREEXISTING_NON_DIRECTORY: ${name} at ${target}`);
    const entries = readdirSync(target);
    if (entries.length > 0) {
      throw new Error(
        `PREEXISTING_CONTENTS: ${name} at ${target} has ${entries.length} entries: ${entries
          .slice(0, 10)
          .join(", ")}`,
      );
    }
    observed[name] = { path: target, state: "EMPTY_DIR" };
  }
  return observed;
}

/** Build the isolated launch environment (purge then pin, never merge). */
export function buildLaunchEnv(scenarioRoot, { cdpPort }) {
  const dirs = launchDirs(scenarioRoot);
  const env = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (
      key.startsWith("M2RC1_") ||
      key.startsWith("M2RC2_") ||
      key.startsWith("M2AC1_") ||
      key.startsWith("NEWMANGA_") ||
      key.startsWith("WEBVIEW2_")
    ) {
      continue;
    }
    env[key] = value;
  }
  if (!env.SystemRoot) env.SystemRoot = process.env.SystemRoot || "C:\\Windows";
  if (!env.PATH) env.PATH = process.env.PATH || "";

  env.M2RC1_PACKAGED = "1"; // packaged mode: frozen sidecar, real Core
  env.APPDATA = dirs.roaming;
  env.LOCALAPPDATA = dirs.localAppData;
  env.TEMP = dirs.tmp;
  env.TMP = dirs.tmp;
  env.NEWMANGA_DATA_ROOT = dirs.dataRoot;
  env.M2RC1_DERIVED_ROOT = dirs.derived;
  env.M2RC1_MANAGED_ROOT = dirs.managed;
  env.M2RC2_CATALOG_DB = dirs.catalogDb;
  env.WEBVIEW2_USER_DATA_FOLDER = dirs.webview2Udd;
  // Official WebView2 loader switch that opens the CDP endpoint.
  env.WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = `--remote-debugging-port=${cdpPort}`;
  // Deliberately NOT set: M2RC1_PROBE_OUT / M2AC1_TEST_MODE / M2RC1_SRC_ROOT
  // (probe/dev surfaces) — the app must boot the production interactive UI.
  return env;
}

/** Non-secret env manifest for evidence files. */
export function envManifest(env, cdpPort) {
  const pinned = [
    "M2RC1_PACKAGED",
    "APPDATA",
    "LOCALAPPDATA",
    "TEMP",
    "TMP",
    "NEWMANGA_DATA_ROOT",
    "M2RC1_DERIVED_ROOT",
    "M2RC1_MANAGED_ROOT",
    "M2RC2_CATALOG_DB",
    "WEBVIEW2_USER_DATA_FOLDER",
    "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
  ];
  const manifest = {};
  for (const key of pinned) manifest[key] = env[key];
  manifest.__purgedPrefixes = ["M2RC1_*", "M2RC2_*", "M2AC1_*", "NEWMANGA_*", "WEBVIEW2_*"];
  manifest.__neverSet = ["M2RC1_PROBE_OUT", "M2AC1_TEST_MODE", "M2RC1_SRC_ROOT"];
  manifest.__cdpPort = cdpPort;
  manifest.__pinnedExe = PINNED_EXE;
  manifest.__pinnedExeSha256 = PINNED_EXE_SHA256;
  return manifest;
}

/** Verified inside every launch: the isolation invariant must actually hold. */
export function assertTaskEnvironment(env) {
  const taskRoot = `${path.resolve(TASK_ENV_ROOT).toLowerCase()}${path.sep}`;
  for (const key of [
    "APPDATA",
    "LOCALAPPDATA",
    "TEMP",
    "TMP",
    "NEWMANGA_DATA_ROOT",
    "M2RC1_DERIVED_ROOT",
    "M2RC1_MANAGED_ROOT",
    "M2RC2_CATALOG_DB",
    "WEBVIEW2_USER_DATA_FOLDER",
  ]) {
    const value = env[key];
    if (!value || !`${path.resolve(value).toLowerCase()}`.startsWith(taskRoot.replace(/\\$/g, ""))) {
      throw new Error(`UNSAFE_LAUNCH_ENV: ${key} must stay under ${TASK_ENV_ROOT}, got ${value}`);
    }
  }
  if (env.M2RC1_PACKAGED !== "1") throw new Error("UNSAFE_LAUNCH_ENV: M2RC1_PACKAGED must be 1");
  const port = Number(/--remote-debugging-port=(\d+)/.exec(env.WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS)?.[1]);
  if (!Number.isInteger(port) || port < 9360) {
    throw new Error(`UNSAFE_LAUNCH_ENV: CDP port must be >= 9360, got ${port}`);
  }
}

export function ensureDir(dir) {
  mkdirSync(dir, { recursive: true });
  return dir;
}

/** First free run label so evidence is never overwritten. */
export function nextRunLabel(prefix) {
  for (let i = 1; i < 500; i += 1) {
    const label = `${prefix}-${String(i).padStart(2, "0")}`;
    if (!existsSync(runRootFor(label))) return label;
  }
  throw new Error(`no free run label for ${prefix}`);
}

