import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClientError, type BackupEntry, type BackupRestoreReport } from "./client";
import { BackupSettingsPanel, type BackupPanelClientLike } from "./BackupSettingsPanel";

/**
 * SETTINGS-OPEN-C-2-BACKUP §3.4 / AC4 — backup/restore operation surface:
 * real list from `backup_list`, create through `backup_create` (no target
 * directory), restore only after the overwrite dialog, delete only after its
 * confirm dialog, typed Core errors mapped to fixed copy (busy / corrupt /
 * not-found), and automatic backup as a read-only note (no fake controls).
 */

function entry(id: string, overrides: Partial<BackupEntry> = {}): BackupEntry {
  return {
    backup_id: id,
    backup_type: "manual",
    created_at: "2026-10-23T02:00:00+00:00",
    size_bytes: 2_048_000,
    schema_version: 5,
    verified: true,
    ...overrides,
  };
}

class FakeBackupClient implements BackupPanelClientLike {
  entries: BackupEntry[];
  failList: unknown = null;
  failCreate: unknown = null;
  failRestore: unknown = null;
  failDelete: unknown = null;
  createCalls = 0;
  listCalls = 0;
  restoreCalls: string[] = [];
  deleteCalls: string[] = [];

  constructor(entries: BackupEntry[] = []) {
    this.entries = entries;
  }

  async listBackups(): Promise<BackupEntry[]> {
    this.listCalls += 1;
    if (this.failList) throw this.failList;
    return [...this.entries];
  }

  async createBackup(): Promise<{ backup_id: string; verified: boolean }> {
    this.createCalls += 1;
    if (this.failCreate) throw this.failCreate;
    const id = "c".repeat(32);
    this.entries = [entry(id), ...this.entries];
    return { backup_id: id, verified: true };
  }

  async restoreBackup(backupId: string): Promise<BackupRestoreReport> {
    this.restoreCalls.push(backupId);
    if (this.failRestore) throw this.failRestore;
    return {
      restored_from: backupId,
      pre_restore_backup_id: "d".repeat(32),
      schema_versions: { backup: 5, restored: 5 },
      managed_consistency: { checked: 2, missing: [] },
    };
  }

  async deleteBackup(backupId: string): Promise<{ removed: boolean }> {
    this.deleteCalls.push(backupId);
    if (this.failDelete) throw this.failDelete;
    this.entries = this.entries.filter((item) => item.backup_id !== backupId);
    return { removed: true };
  }
}

describe("BackupSettingsPanel (SETTINGS-OPEN-C-2-BACKUP §3.4)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;
  const button = (testId: string) => q(`[data-testid="${testId}"]`) as HTMLButtonElement | null;

  const render = async (client: BackupPanelClientLike) => {
    await act(async () => {
      root.render(<BackupSettingsPanel client={client} />);
    });
    await act(async () => {
      await Promise.resolve();
    });
  };

  it("shows the loading skeleton while the first list request is pending", async () => {
    const client: BackupPanelClientLike = {
      listBackups: vi.fn(() => new Promise<BackupEntry[]>(() => {})),
      createBackup: vi.fn(),
      restoreBackup: vi.fn(),
      deleteBackup: vi.fn(),
    };
    act(() => {
      root.render(<BackupSettingsPanel client={client} />);
    });
    expect(q('[data-testid="backup-settings-loading"]')).not.toBeNull();
    expect(button("backup-settings-create-btn")).not.toBeNull();
  });

  it("renders the real list with type, time, size and verification, plus the read-only auto-backup note", async () => {
    const client = new FakeBackupClient([
      entry("a".repeat(32), { backup_type: "manual", verified: true }),
      entry("b".repeat(32), { backup_type: "pre_restore", verified: false }),
    ]);
    await render(client);

    expect(client.listCalls).toBe(1);
    expect(q('[data-testid="backup-settings-summary"]')?.textContent).toContain("备份：2 个");
    expect(q(`[data-testid="backup-settings-item-${"a".repeat(32)}"]`)).not.toBeNull();
    expect(q(`[data-testid="backup-settings-verified-${"b".repeat(32)}"]`)?.textContent).toContain(
      "校验未通过",
    );
    expect(q('[data-testid="backup-settings-policy-note"]')?.textContent).toContain("自动备份");
  });

  it("shows the empty state distinctly from a load failure", async () => {
    const empty = new FakeBackupClient([]);
    await render(empty);
    expect(q('[data-testid="backup-settings-empty"]')).not.toBeNull();

    act(() => {
      root.unmount();
    });
    root = createRoot(container);
    const failing = new FakeBackupClient([]);
    failing.failList = new SettingsClientError("CORE_UNAVAILABLE", "no core");
    await render(failing);
    expect(q('[data-testid="backup-settings-load-error"]')?.textContent).toContain("备份服务当前不可用");
    expect(q('[data-testid="backup-settings-empty"]')).toBeNull();
  });

  it("creates a backup through backup_create (no target directory) and refreshes the list", async () => {
    const client = new FakeBackupClient([]);
    await render(client);
    await act(async () => {
      button("backup-settings-create-btn")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(client.createCalls).toBe(1);
    expect(client.listCalls).toBe(2);
    expect(q('[data-testid="backup-settings-notice"]')?.textContent).toContain("校验通过");
    expect(q(`[data-testid="backup-settings-item-${"c".repeat(32)}"]`)).not.toBeNull();
  });

  it("restores only after the overwrite dialog and reports the rollback package", async () => {
    const target = "a".repeat(32);
    const client = new FakeBackupClient([entry(target)]);
    await render(client);
    expect(client.restoreCalls).toEqual([]);

    await act(async () => {
      button(`backup-settings-restore-btn-${target}`)?.click();
      await Promise.resolve();
    });
    const dialog = q('[data-testid="backup-settings-restore-dialog"]');
    expect(dialog?.textContent).toContain("覆盖当前全部数据");
    expect(dialog?.textContent).toContain("pre_restore");

    await act(async () => {
      button("backup-settings-restore-confirm-btn")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(client.restoreCalls).toEqual([target]);
    expect(q('[data-testid="backup-settings-notice"]')?.textContent).toContain("恢复前备份");
    expect(client.listCalls).toBe(2);
  });

  it("maps BACKUP_RESTORE_BUSY to the fixed 'task running' copy and keeps the dialog", async () => {
    const target = "a".repeat(32);
    const client = new FakeBackupClient([entry(target)]);
    client.failRestore = new SettingsClientError("BACKUP_RESTORE_BUSY", "busy");
    await render(client);
    await act(async () => {
      button(`backup-settings-restore-btn-${target}`)?.click();
      await Promise.resolve();
    });
    await act(async () => {
      button("backup-settings-restore-confirm-btn")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(q('[data-testid="backup-settings-error"]')?.textContent).toContain("有任务正在运行");
    expect(q('[data-testid="backup-settings-restore-dialog"]')).not.toBeNull();
  });

  it("maps BACKUP_CORRUPT to the fixed 'not restored' copy", async () => {
    const target = "a".repeat(32);
    const client = new FakeBackupClient([entry(target)]);
    client.failRestore = new SettingsClientError("BACKUP_CORRUPT", "corrupt");
    await render(client);
    await act(async () => {
      button(`backup-settings-restore-btn-${target}`)?.click();
      await Promise.resolve();
    });
    await act(async () => {
      button("backup-settings-restore-confirm-btn")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(q('[data-testid="backup-settings-error"]')?.textContent).toContain("校验失败");
  });

  it("deletes a backup only after its confirm dialog and refreshes the list", async () => {
    const target = "a".repeat(32);
    const client = new FakeBackupClient([entry(target)]);
    await render(client);
    expect(client.deleteCalls).toEqual([]);

    await act(async () => {
      button(`backup-settings-delete-btn-${target}`)?.click();
      await Promise.resolve();
    });
    expect(q('[data-testid="backup-settings-delete-dialog"]')).not.toBeNull();
    await act(async () => {
      button("backup-settings-delete-confirm-btn")?.click();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(client.deleteCalls).toEqual([target]);
    expect(q('[data-testid="backup-settings-empty"]')).not.toBeNull();
    expect(q('[data-testid="backup-settings-notice"]')?.textContent).toContain("已删除备份");
  });
});
