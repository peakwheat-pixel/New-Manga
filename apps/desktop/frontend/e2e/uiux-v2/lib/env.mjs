/**
 * UIUX-V2-RUNTIME-REALCORE-1 — isolated launch environment for the REAL
 * packaged Tauri app (release exe built from the frozen delivery head).
 *
 * Reuses the proven discipline of e2e/p02-new-time/lib/env.mjs (Task-local
 * isolation, purge-then-pin, empty-target assertion) but points at THIS
 * Task's build output and evidence root.
 *
 * Isolation contract (every writable path the packaged app can reach):
 *   G:/CODEX/New Manga.workspace/task-envs/UIUX-V2-RUNTIME-REALCORE-1/run-i1/<scenario>/
 * The user's real %APPDATA%/%LOCALAPPDATA%/New Manga library is never touched.
 */

import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

export const TASK_ENV_ROOT =
  "G:/CODEX/New Manga.workspace/task-envs/UIUX-V2-RUNTIME-REALCORE-1";

/**
 * Release exe built in-repo by `cargo tauri build --no-bundle` from the frozen
 * head. `UIUX_E2E_EXE` lets the same script run against the acceptance build
 * (identical code, window config adds `additionalBrowserArgs` so WebView2 opens
 * a CDP endpoint). The report records which exe was measured, so the two can
 * never be confused.
 */
export const PINNED_EXE =
  process.env.UIUX_E2E_EXE ||
  "G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe";

export const CDP_PORT = Number(process.env.UIUX_E2E_CDP_PORT || 9345);

export const REPO_ROOT = path.resolve(
  import.meta.dirname,
  "../../../../../..",
);
export const CANONICAL_ROOT = path.join(
  REPO_ROOT,
  "verification",
  "UIUX-V2-RUNTIME-REALCORE-1",
);

/**
 * Never overwrite a previous run's evidence: pick the first free `run-iN`
 * slot. Empty existing directories are reused.
 */
export function resolveRunName() {
  for (let i = 1; i < 200; i += 1) {
    const name = `run-i${i}`;
    const dir = path.join(TASK_ENV_ROOT, name);
    if (!existsSync(dir) || readdirSync(dir).length === 0) return name;
  }
  throw new Error("no free run slot under TASK_ENV_ROOT");
}

export const runRootFor = (name) => path.join(TASK_ENV_ROOT, name);
export const canonicalFor = (name) => path.join(CANONICAL_ROOT, name);

/** Sub-launches dir (all app-visible writable roots live under scenarioRoot). */
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
});

/**
 * Safety precondition: every Task-local target the app will write must be
 * ABSENT or EMPTY before launch. Anything unexpected -> throw (never overwrite
 * a previous run's evidence).
 */
export function assertLaunchTargetsClean(scenarioRoot) {
  const dirs = launchDirs(scenarioRoot);
  const observed = {};
  for (const [name, target] of Object.entries(dirs)) {
    if (!existsSync(target)) {
      observed[name] = { path: target, state: "ABSENT" };
      continue;
    }
    const stat = statSync(target);
    if (!stat.isDirectory()) {
      throw new Error(`PREEXISTING_NON_DIRECTORY: ${name} at ${target}`);
    }
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

/** Build the isolated launch environment (purge first, then pin). */
export function buildLaunchEnv(scenarioRoot) {
  const dirs = launchDirs(scenarioRoot);
  const env = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (
      key.startsWith("M2RC1_") ||
      key.startsWith("M2RC2_") ||
      key.startsWith("M2AC1_") ||
      key.startsWith("NEWMANGA_")
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
  // The official WebView2 loader switch that opens the CDP endpoint.
  env.WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = `--remote-debugging-port=${CDP_PORT}`;
  // Deliberately NOT set: M2RC1_PROBE_OUT / M2AC1_TEST_MODE / M2RC1_SRC_ROOT
  // (probe/dev surfaces) — the app must boot the production interactive UI.
  return env;
}

/** Non-secret env manifest for evidence files. */
export function envEvidenceManifest(env) {
  const pinned = [
    "M2RC1_PACKAGED",
    "APPDATA",
    "LOCALAPPDATA",
    "TEMP",
    "NEWMANGA_DATA_ROOT",
    "M2RC1_DERIVED_ROOT",
    "M2RC1_MANAGED_ROOT",
    "M2RC2_CATALOG_DB",
    "WEBVIEW2_USER_DATA_FOLDER",
    "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
  ];
  const manifest = {};
  for (const key of pinned) manifest[key] = env[key];
  manifest.__purgedPrefixes = ["M2RC1_*", "M2RC2_*", "M2AC1_*", "NEWMANGA_*"];
  manifest.__neverSet = ["M2RC1_PROBE_OUT", "M2AC1_TEST_MODE", "M2RC1_SRC_ROOT"];
  manifest.__cdpPort = CDP_PORT;
  manifest.__pinnedExe = PINNED_EXE;
  return manifest;
}
