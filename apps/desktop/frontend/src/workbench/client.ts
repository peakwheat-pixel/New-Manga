export type WorkbenchInvoke = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export type PipelineCommand =
  | "translate_all" | "translate_untranslated" | "translate_selected" | "translate_single"
  | "rerender_all" | "rerender_selected" | "rerender_single"
  | "reinpaint_all" | "reinpaint_selected" | "reinpaint_single"
  | "reocr_all" | "reocr_selected" | "reocr_single"
  | "ocr_region" | "retranslate_region" | "retranslate_region_full" | "reinpaint_region" | "rerender_region";

export type PipelineScope =
  | { kind: "chapter"; chapter_id: string }
  | { kind: "page_selection"; page_ids: string[] }
  | { kind: "page"; page_id: string }
  | { kind: "region"; region_id: string };

export interface RunAccepted { run_id: string; status: string }
export interface RunSnapshot { run_id: string; command: PipelineCommand; scope: PipelineScope; status: string }
export interface TaskProjection {
  run_id: string;
  run_status: string;
  run_title: string;
  overall_progress: number;
  current_page_id: string | null;
  current_step_type: string;
  step_flow: { type: string; label: string; state: string }[];
  rows: { page_id: string; page_order: number; filename: string; status: string; is_locked: boolean; is_pipeline_current: boolean; error_code: string | null }[];
  tasks: { task_id: string; page_id: string; status: string; error_code: string | null; steps: { step_run_id: string; step_type: string; status: string; retry_no: number; error_code: string | null; provider: string | null; model: string | null; device: string | null }[] }[];
  counts: { total: number; completed: number; failed: number; skipped: number; blocked: number; waiting: number; processing: number };
  blocked_reasons: string[];
  controls: { can_pause: boolean; can_stop: boolean; can_continue: boolean; can_restart: boolean; can_abandon: boolean; can_retry_failed: boolean };
}

export type ExportFormat = "png" | "zip" | "cbz" | "pdf" | "text";
export type ExportFormatOptions = Record<string, string>;
export interface StartExportRequest {
  book_id: string;
  chapter_ids: string[];
  ordered_page_ids: string[];
  format: ExportFormat;
  format_options: ExportFormatOptions;
  stale_policy: "abort" | "continue_existing";
}
export interface ExportSummary { export_id: string; status: string }
export interface ExportSnapshot {
  export_id: string;
  status: string;
  completed_pages: number;
  total_pages: number;
  current_page_id: string | null;
  completed_at: string | null;
  output: { format: string; sha256: string } | null;
  error_code: string | null;
}
export interface ExportHistoryEntry {
  export_id: string;
  book_id: string;
  chapter_ids: string[];
  ordered_page_ids: string[];
  format: string;
  created_at: string;
  completed_at: string | null;
  status: string;
  sha256: string | null;
}

export class WorkbenchClientError extends Error {
  constructor(readonly code: string) {
    super(code);
    this.name = "WorkbenchClientError";
  }
}

const SAFE_ERROR_CODE = /^[A-Z][A-Z0-9_]{0,63}$/;
const SAFE_ID = /^[A-Za-z0-9_.:-]{1,256}$/;

export function isSafeUiId(value: unknown): value is string {
  return typeof value === "string" && SAFE_ID.test(value) && value !== "." && value !== ".." && !/^[A-Za-z]:/.test(value);
}

function assertId(value: string): string {
  if (!isSafeUiId(value)) throw new WorkbenchClientError("INVALID_REQUEST");
  return value;
}

export function safeWorkbenchErrorCode(error: unknown, fallback = "CORE_UNAVAILABLE"): string {
  const candidate = typeof error === "string"
    ? error
    : (error as { code?: unknown } | null)?.code;
  return typeof candidate === "string" && SAFE_ERROR_CODE.test(candidate) ? candidate : fallback;
}

export function newIdempotencyKey(): string {
  if (typeof crypto === "undefined" || typeof crypto.randomUUID !== "function") {
    throw new WorkbenchClientError("IDEMPOTENCY_KEY_UNAVAILABLE");
  }
  return crypto.randomUUID();
}

function object(value: unknown, code = "WORKBENCH_RESPONSE_MALFORMED"): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new WorkbenchClientError(code);
  return value as Record<string, unknown>;
}

function text(value: unknown, code = "WORKBENCH_RESPONSE_MALFORMED"): string {
  if (!isSafeUiId(value)) throw new WorkbenchClientError(code);
  return value;
}

function number(value: unknown, code = "WORKBENCH_RESPONSE_MALFORMED"): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new WorkbenchClientError(code);
  return value;
}

function safeDisplayText(value: unknown, fallback = ""): string {
  if (typeof value !== "string") return fallback;
  if (/(?:[A-Za-z]:|\\\\|(?:https?|file):\/\/|(?:^|[\s"'(])\/[^\s]+|(?:^|[\s"'(])[^\\/\s]+[\\/][^\\/\s]+|(?:token|credential|secret|api[_-]?key)\s*[:=])/i.test(value)) return "详情已隐藏";
  return value.slice(0, 256);
}

function safeFilename(value: unknown): string {
  return typeof value === "string" && !/[\\/\0]/.test(value) && !/^[A-Za-z]:/.test(value)
    ? safeDisplayText(value)
    : "详情已隐藏";
}

function safeDigest(value: unknown): string | null {
  return typeof value === "string" && /^[a-f0-9]{64}$/i.test(value) ? value : null;
}

function projectScope(value: unknown): PipelineScope {
  const scope = object(value);
  if (scope.kind === "chapter") return { kind: "chapter", chapter_id: text(scope.chapter_id) };
  if (scope.kind === "page") return { kind: "page", page_id: text(scope.page_id) };
  if (scope.kind === "region") return { kind: "region", region_id: text(scope.region_id) };
  if (scope.kind === "page_selection" && Array.isArray(scope.page_ids)) {
    return { kind: "page_selection", page_ids: scope.page_ids.map((id) => text(id)) };
  }
  throw new WorkbenchClientError("WORKBENCH_RESPONSE_MALFORMED");
}

function projectTaskProjection(value: unknown): TaskProjection {
  const row = object(value);
  const counts = object(row.counts);
  const controls = object(row.controls);
  if (!Array.isArray(row.step_flow) || !Array.isArray(row.rows) || !Array.isArray(row.tasks) || !Array.isArray(row.blocked_reasons)) {
    throw new WorkbenchClientError("WORKBENCH_RESPONSE_MALFORMED");
  }
  const projection: TaskProjection = {
    run_id: text(row.run_id),
    run_status: text(row.run_status),
    run_title: safeDisplayText(row.run_title),
    overall_progress: number(row.overall_progress),
    current_page_id: row.current_page_id === null ? null : text(row.current_page_id),
    current_step_type: safeDisplayText(row.current_step_type),
    step_flow: row.step_flow.map((value) => {
      const item = object(value);
      return { type: text(item.type), label: safeDisplayText(item.label), state: text(item.state) };
    }),
    rows: row.rows.map((value) => {
      const item = object(value);
      return {
        page_id: text(item.page_id),
        page_order: number(item.page_order),
        filename: safeFilename(item.filename),
        status: text(item.status),
        is_locked: item.is_locked === true,
        is_pipeline_current: item.is_pipeline_current === true,
        error_code: item.error_code === null ? null : typeof item.error_code === "string" ? safeWorkbenchErrorCode(item.error_code, "UNKNOWN") : null,
      };
    }),
    tasks: row.tasks.map((value) => {
      const item = object(value);
      if (!Array.isArray(item.steps)) throw new WorkbenchClientError("WORKBENCH_RESPONSE_MALFORMED");
      return {
        task_id: text(item.task_id),
        page_id: text(item.page_id),
        status: text(item.status),
        error_code: item.error_code === null ? null : typeof item.error_code === "string" ? safeWorkbenchErrorCode(item.error_code, "UNKNOWN") : null,
        steps: item.steps.map((stepValue) => {
          const step = object(stepValue);
          const optionalText = (candidate: unknown) => candidate === null ? null : typeof candidate === "string" ? candidate : null;
          return {
            step_run_id: text(step.step_run_id),
            step_type: text(step.step_type),
            status: text(step.status),
            retry_no: number(step.retry_no),
            error_code: step.error_code === null ? null : typeof step.error_code === "string" ? safeWorkbenchErrorCode(step.error_code, "UNKNOWN") : null,
            provider: optionalText(step.provider) ? safeDisplayText(step.provider) : null,
            model: optionalText(step.model) ? safeDisplayText(step.model) : null,
            device: optionalText(step.device) ? safeDisplayText(step.device) : null,
          };
        }),
      };
    }),
    counts: {
      total: number(counts.total), completed: number(counts.completed), failed: number(counts.failed),
      skipped: number(counts.skipped), blocked: number(counts.blocked), waiting: number(counts.waiting), processing: number(counts.processing),
    },
    blocked_reasons: row.blocked_reasons.filter((value): value is string => typeof value === "string").map((value) =>
      safeDisplayText(value, "原因详情已隐藏"),
    ),
    controls: {
      can_pause: controls.can_pause === true, can_stop: controls.can_stop === true,
      can_continue: controls.can_continue === true, can_restart: controls.can_restart === true,
      can_abandon: controls.can_abandon === true, can_retry_failed: controls.can_retry_failed === true,
    },
  };
  return projection;
}

export class WorkbenchClient {
  constructor(private readonly invoke: WorkbenchInvoke) {}

  private async call<T>(command: string, args?: Record<string, unknown>): Promise<T> {
    try { return await this.invoke(command, args) as T; }
    catch (error) { throw new WorkbenchClientError(safeWorkbenchErrorCode(error)); }
  }

  async startRun(command: PipelineCommand, scope: PipelineScope, idempotencyKey: string): Promise<RunAccepted> {
    if (scope.kind === "chapter") assertId(scope.chapter_id);
    else if (scope.kind === "page") assertId(scope.page_id);
    else if (scope.kind === "region") assertId(scope.region_id);
    else scope.page_ids.forEach(assertId);
    const value = object(await this.call("library_start_run", { command, scope, idempotencyKey }));
    return { run_id: text(value.run_id), status: text(value.status) };
  }

  async controlRun(runId: string, action: string, idempotencyKey?: string): Promise<{ run_id: string; status: string; new_run_id?: string; new_run_status?: string }> {
    assertId(runId);
    const value = object(await this.call("library_control_run", { runId, action, ...(idempotencyKey ? { idempotencyKey } : {}) }));
    return {
      run_id: text(value.run_id), status: text(value.status),
      ...(typeof value.new_run_id === "string" ? { new_run_id: text(value.new_run_id) } : {}),
      ...(typeof value.new_run_status === "string" ? { new_run_status: text(value.new_run_status) } : {}),
    };
  }

  async resumeBlockedRun(runId: string): Promise<{ run_id: string; status: string }> {
    assertId(runId);
    const value = object(await this.call("library_resume_blocked_run", { runId }));
    return { run_id: text(value.run_id), status: text(value.status) };
  }

  async getRunSnapshot(runId: string): Promise<RunSnapshot> {
    assertId(runId);
    const value = object(await this.call("library_get_run_snapshot", { runId }));
    return { run_id: text(value.run_id), command: text(value.command) as PipelineCommand, scope: projectScope(value.scope), status: text(value.status) };
  }

  async getTaskProjection(runId: string): Promise<TaskProjection> {
    assertId(runId);
    return projectTaskProjection(await this.call("library_get_task_projection", { runId }));
  }

  async retryFailedTargets(runId: string, idempotencyKey: string): Promise<RunAccepted> {
    assertId(runId);
    const value = object(await this.call("library_retry_failed_targets", { runId, idempotencyKey }));
    return { run_id: text(value.run_id), status: text(value.status) };
  }

  async startExport(request: StartExportRequest): Promise<ExportSummary | null> {
    assertId(request.book_id);
    request.chapter_ids.forEach(assertId);
    request.ordered_page_ids.forEach(assertId);
    const raw = await this.call<unknown>("library_start_export", { request });
    if (raw === null) return null;
    const value = object(raw);
    return { export_id: text(value.export_id), status: text(value.status) };
  }

  async cancelExport(exportId: string): Promise<ExportSnapshot> {
    assertId(exportId);
    return this.projectExportSnapshot(await this.call("library_cancel_export", { exportId }));
  }

  async getExportSnapshot(exportId: string): Promise<ExportSnapshot> {
    assertId(exportId);
    return this.projectExportSnapshot(await this.call("library_get_export_snapshot", { exportId }));
  }

  private projectExportSnapshot(raw: unknown): ExportSnapshot {
    const value = object(raw);
    let output: ExportSnapshot["output"] = null;
    if (value.output !== null && value.output !== undefined) {
      const safeOutput = object(value.output);
      output = { format: text(safeOutput.format), sha256: safeDigest(safeOutput.sha256) ?? "" };
    }
    return {
      export_id: text(value.export_id), status: text(value.status), completed_pages: number(value.completed_pages),
      total_pages: number(value.total_pages), current_page_id: value.current_page_id === null ? null : text(value.current_page_id),
      completed_at: typeof value.completed_at === "string" ? safeDisplayText(value.completed_at) : null,
      output, error_code: typeof value.error_code === "string" ? safeWorkbenchErrorCode(value.error_code, "UNKNOWN") : null,
    };
  }

  async getExportHistory(): Promise<ExportHistoryEntry[]> {
    const response = object(await this.call("library_get_export_history"));
    if (!Array.isArray(response.exports)) throw new WorkbenchClientError("EXPORT_HISTORY_MALFORMED");
    return response.exports.map((raw) => {
      const item = object(raw);
      if (!Array.isArray(item.chapter_ids) || !Array.isArray(item.ordered_page_ids)) throw new WorkbenchClientError("EXPORT_HISTORY_MALFORMED");
      return {
        export_id: text(item.export_id), book_id: text(item.book_id),
        chapter_ids: item.chapter_ids.map((id) => text(id)), ordered_page_ids: item.ordered_page_ids.map((id) => text(id)),
        format: text(item.format), created_at: typeof item.created_at === "string" ? safeDisplayText(item.created_at) : "",
        completed_at: typeof item.completed_at === "string" ? safeDisplayText(item.completed_at) : null,
        status: text(item.status), sha256: safeDigest(item.sha256),
      };
    });
  }

  async revealExportFolder(exportId: string): Promise<void> {
    assertId(exportId);
    await this.call("library_reveal_export_folder", { exportId });
  }
}
