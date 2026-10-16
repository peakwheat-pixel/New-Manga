import { describe, expect, it, vi } from "vitest";
import { WorkbenchClient, WorkbenchClientError, safeWorkbenchErrorCode } from "./client";

const digest = "a".repeat(64);

describe("WorkbenchClient IPC boundary", () => {
  it("rejects path-shaped identifiers before invoking the host", async () => {
    const invoke = vi.fn(async () => null);
    const client = new WorkbenchClient(invoke);

    await expect(client.getRunSnapshot("C:private")).rejects.toMatchObject({ code: "INVALID_REQUEST" });
    await expect(client.getRunSnapshot("..")).rejects.toBeInstanceOf(WorkbenchClientError);
    expect(invoke).not.toHaveBeenCalled();
  });

  it("projects only safe task fields and removes path, credential, and raw error details", async () => {
    const invoke = vi.fn(async () => ({
      run_id: "run-1",
      run_status: "running",
      run_title: "C:\\Users\\Manga\\private",
      overall_progress: 0.5,
      current_page_id: "page-1",
      current_step_type: "render",
      step_flow: [{ type: "render", label: "https://internal.example/path", state: "running", local_path: "C:\\secret" }],
      rows: [{ page_id: "page-1", page_order: 0, filename: "folder\\page.png", status: "processing", is_locked: false, is_pipeline_current: true, error_code: null, error_message: "C:\\secret" }],
      tasks: [{ task_id: "task-1", page_id: "page-1", status: "failed", error_code: "OCR_FAILED", error_message: "token=secret", path: "C:\\secret", steps: [] }],
      counts: { total: 1, completed: 0, failed: 1, skipped: 0, blocked: 0, waiting: 0, processing: 0 },
      blocked_reasons: ["api_key=secret", "等待资源"],
      controls: { can_pause: false, can_stop: true, can_continue: false, can_restart: false, can_abandon: false, can_retry_failed: true },
      export_target_ref: "opaque-secret",
    }));
    const projection = await new WorkbenchClient(invoke).getTaskProjection("run-1");

    expect(projection.run_title).toBe("详情已隐藏");
    expect(projection.step_flow[0].label).toBe("详情已隐藏");
    expect(projection.rows[0].filename).toBe("详情已隐藏");
    expect(projection.blocked_reasons).toEqual(["详情已隐藏", "等待资源"]);
    expect(JSON.stringify(projection)).not.toMatch(/secret|internal\.example|local_path|error_message|export_target_ref/i);
  });

  it("sends the export request without host refs and drops output paths from responses", async () => {
    const invoke = vi.fn(async (command: string, _args?: Record<string, unknown>) => {
      if (command === "library_start_export") return { export_id: "export-1", status: "pending", target_ref: "private-ref" };
      if (command === "library_get_export_snapshot") return {
        export_id: "export-1", status: "completed", completed_pages: 1, total_pages: 1,
        current_page_id: null, completed_at: "2026-10-16T00:00:00Z", output: { format: "zip", sha256: digest },
        error_code: null, output_path: "C:\\private\\out.zip", target_ref: "private-ref",
      };
      if (command === "library_get_export_history") return { exports: [{
        export_id: "export-1", book_id: "book-1", chapter_ids: ["chapter-1"], ordered_page_ids: ["page-1"],
        format: "zip", created_at: "2026-10-16T00:00:00Z", completed_at: null, status: "completed", sha256: digest,
        output_path: "C:\\private\\out.zip", target_ref: "private-ref",
      }] };
      return null;
    });
    const client = new WorkbenchClient(invoke);
    const request = {
      book_id: "book-1", chapter_ids: ["chapter-1"], ordered_page_ids: ["page-1"],
      format: "zip" as const, format_options: { compression: "standard" }, stale_policy: "abort" as const,
    };

    await client.startExport(request);
    expect(invoke).toHaveBeenCalledWith("library_start_export", { request });
    expect(JSON.stringify(invoke.mock.calls[0][1])).not.toMatch(/target_ref|output_path|private-ref/i);

    const snapshot = await client.getExportSnapshot("export-1");
    const history = await client.getExportHistory();
    expect(JSON.stringify(snapshot)).not.toMatch(/output_path|target_ref|private/i);
    expect(JSON.stringify(history)).not.toMatch(/output_path|target_ref|private/i);
    expect(history[0].sha256).toBe(digest);
  });

  it("replaces path-shaped errors with a stable fallback code", () => {
    expect(safeWorkbenchErrorCode("C:\\Users\\private\\failure")).toBe("CORE_UNAVAILABLE");
    expect(safeWorkbenchErrorCode({ code: "ACCESS_DENIED" })).toBe("ACCESS_DENIED");
    expect(safeWorkbenchErrorCode({ code: "token=secret", message: "C:\\Users\\private\\failure" })).toBe("CORE_UNAVAILABLE");
  });
});
