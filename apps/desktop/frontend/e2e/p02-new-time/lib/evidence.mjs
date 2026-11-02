/**
 * P02-NEW-TIME-X6-AC1-AC7 — canonical evidence writer.
 *
 * Every scenario freezes: command, shell/version, cwd, pinned source and
 * binary hashes, non-secret env manifest, stdout/stderr/exit, wall-clock
 * timings. Files land in the Task env logs dir first and are copied into
 * verification/P02-NEW-TIME-X6-AC1-AC7/ by the runner (canonical copy).
 */

import { createHash } from "node:crypto";
import { mkdirSync, readdirSync, statSync, writeFileSync, copyFileSync, constants, readFileSync as readFileBytes } from "node:fs";
import os from "node:os";
import path from "node:path";
import { RUN_ID, SOURCE_BASELINE_COMMIT, PINNED_EXE, PINNED_EXE_SHA256 } from "./env.mjs";

export function sha256Hex(data) {
  return createHash("sha256").update(data).digest("hex").toUpperCase();
}

export function sha256File(filePath) {
  return sha256Hex(readFileBytes(filePath));
}

export class EvidenceStore {
  /** @param {string} baseDir directory for this scenario's raw evidence */
  constructor(baseDir, meta = {}) {
    this.baseDir = baseDir;
    mkdirSync(baseDir, { recursive: true });
    this.meta = {
      run_id: RUN_ID,
      recorded_at: new Date().toISOString(),
      source_baseline_commit: SOURCE_BASELINE_COMMIT,
      pinned_exe: PINNED_EXE,
      pinned_exe_sha256: PINNED_EXE_SHA256,
      host_os: {
        platform: os.platform(),
        type: os.type(),
        release: os.release(),
        version: os.version(),
        arch: os.arch(),
      },
      shell: `node ${process.version}`,
      cwd: process.cwd(),
      argv: process.argv,
      ...meta,
    };
  }

  write(name, content) {
    const target = path.join(this.baseDir, name);
    writeFileSync(target, content);
    return {
      file: target,
      bytes: Buffer.byteLength(content),
      sha256: sha256Hex(content),
    };
  }

  writeJson(name, value) {
    return this.write(name, JSON.stringify(value, null, 2) + "\n");
  }

  writeBinary(name, buffer) {
    const target = path.join(this.baseDir, name);
    writeFileSync(target, buffer);
    return {
      file: target,
      bytes: buffer.length,
      sha256: sha256Hex(buffer),
    };
  }

  writeMetadata(extraMeta = {}) {
    const meta = {
      ...this.meta,
      ...extraMeta,
      completed_at: new Date().toISOString(),
      node_exit_code: process.exitCode || 0,
    };
    return this.writeJson("execution-metadata.json", meta);
  }

  /**
   * Copy this scenario's directory into the canonical verification dir.
   * Uses constants.COPYFILE_EXCL (fail-closed, no-overwrite).
   */
  copyToCanonical(canonicalRoot) {
    mkdirSync(canonicalRoot, { recursive: true });
    const copied = [];
    const walk = (dir, rel) => {
      for (const entry of readdirSync(dir)) {
        const abs = path.join(dir, entry);
        const relPath = rel ? `${rel}/${entry}` : entry;
        if (statSync(abs).isDirectory()) {
          walk(abs, relPath);
        } else {
          const target = path.join(canonicalRoot, relPath);
          mkdirSync(path.dirname(target), { recursive: true });
          copyFileSync(abs, target, constants.COPYFILE_EXCL);
          copied.push({ file: relPath, sha256: sha256File(target) });
        }
      }
    };
    walk(this.baseDir, "");
    return copied;
  }
}

/** Recursively describe a directory (small trees only) for emptiness proof. */
export function describeTree(root) {
  const out = [];
  const walk = (dir, depth) => {
    if (!existsSyncSafe(dir)) return;
    for (const entry of readdirSync(dir)) {
      const abs = path.join(dir, entry);
      const stat = statSync(abs);
      out.push({ path: abs, type: stat.isDirectory() ? "dir" : "file", bytes: stat.isDirectory() ? null : stat.size });
      if (stat.isDirectory() && depth < 3) walk(abs, depth + 1);
    }
  };
  walk(root, 0);
  return out;
}

function existsSyncSafe(p) {
  try {
    statSync(p);
    return true;
  } catch {
    return false;
  }
}
