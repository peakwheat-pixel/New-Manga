/**
 * EVENTS-FWD-1 / M2-C1 rev 2.4 §6.4:
 * Host-to-WebView event forwarding typed listener surface.
 *
 * CRITICAL DISCIPLINE:
 * Events are invalidation hints, NOT state truth.
 * Event payloads MUST NOT contain OS filesystem paths, opaque references,
 * or raw file bytes (M2-C1 §10.2 / §10.3 / §10.4).
 * Consumers MUST re-query the authoritative snapshot upon receiving these events.
 */

export interface TaskFailedPayload {
  run_id: string;
  task_id: string;
  page_id?: string | null;
  error_code?: string | null;
}

export interface RunPausedPayload {
  run_id: string;
  status: "paused" | string;
}

export interface RunCompletedPayload {
  run_id: string;
  status: "completed" | "completed_with_failures" | string;
}

export interface CurrentPageStepChangedPayload {
  run_id: string;
  current_page_id?: string | null;
  current_step_type: string;
}

export interface ExportProgressChangedPayload {
  export_id: string;
  status: string;
  completed_pages: number;
  total_pages: number;
}

export interface ReadingProgressChangedPayload {
  book_id: string;
  chapter_id: string;
  mode: "original" | "translated" | string;
}

export interface LifecycleStatusPayload {
  status: "restarting" | "recovered" | "fatal" | "healthy" | string;
  message: string;
}

export const CORE_EVENT_NAMES = {
  TaskFailed: "core:TaskFailed",
  RunPaused: "core:RunPaused",
  RunCompleted: "core:RunCompleted",
  CurrentPageStepChanged: "core:CurrentPageStepChanged",
  ExportProgressChanged: "core:ExportProgressChanged",
  ReadingProgressChanged: "core:ReadingProgressChanged",
} as const;

export const LIFECYCLE_STATUS_EVENT = "core:lifecycle_status" as const;

export type CoreEventName = (typeof CORE_EVENT_NAMES)[keyof typeof CORE_EVENT_NAMES];

export interface CoreEventMap {
  "core:TaskFailed": TaskFailedPayload;
  "core:RunPaused": RunPausedPayload;
  "core:RunCompleted": RunCompletedPayload;
  "core:CurrentPageStepChanged": CurrentPageStepChangedPayload;
  "core:ExportProgressChanged": ExportProgressChangedPayload;
  "core:ReadingProgressChanged": ReadingProgressChangedPayload;
  "core:lifecycle_status": LifecycleStatusPayload;
}

export type EventCallback<T> = (payload: T) => void;
export type UnlistenFn = () => void;
export type ListenFn = <T>(
  event: string,
  handler: (event: { payload: T }) => void
) => Promise<UnlistenFn>;

async function getDefaultListen(): Promise<ListenFn> {
  const globalWindow = typeof window !== "undefined"
    ? (window as unknown as { __TAURI__?: { event?: { listen: ListenFn } } })
    : undefined;
  if (globalWindow?.__TAURI__?.event?.listen) {
    return globalWindow.__TAURI__.event.listen;
  }
  try {
    const tauriEvent = await import("@tauri-apps/api/event");
    return tauriEvent.listen as unknown as ListenFn;
  } catch {
    throw new Error("TAURI_EVENT_BRIDGE_MISSING");
  }
}

/**
 * Subscribes to a typed Core forwarded event.
 *
 * @param eventName The full namespaced event name (e.g. "core:RunCompleted").
 * @param handler Callback invoked when the event is received.
 * @param customListen Optional custom listener function for testing or custom environments.
 */
export async function listenCoreEvent<K extends keyof CoreEventMap>(
  eventName: K,
  handler: EventCallback<CoreEventMap[K]>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  const listen = customListen || (await getDefaultListen());
  return listen<CoreEventMap[K]>(eventName, (event) => {
    handler(event.payload);
  });
}

export function onTaskFailed(
  handler: EventCallback<TaskFailedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.TaskFailed, handler, customListen);
}

export function onRunPaused(
  handler: EventCallback<RunPausedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.RunPaused, handler, customListen);
}

export function onRunCompleted(
  handler: EventCallback<RunCompletedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.RunCompleted, handler, customListen);
}

export function onCurrentPageStepChanged(
  handler: EventCallback<CurrentPageStepChangedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.CurrentPageStepChanged, handler, customListen);
}

export function onExportProgressChanged(
  handler: EventCallback<ExportProgressChangedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.ExportProgressChanged, handler, customListen);
}

export function onReadingProgressChanged(
  handler: EventCallback<ReadingProgressChangedPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(CORE_EVENT_NAMES.ReadingProgressChanged, handler, customListen);
}

export function onLifecycleStatusChanged(
  handler: EventCallback<LifecycleStatusPayload>,
  customListen?: ListenFn
): Promise<UnlistenFn> {
  return listenCoreEvent(LIFECYCLE_STATUS_EVENT, handler, customListen);
}
