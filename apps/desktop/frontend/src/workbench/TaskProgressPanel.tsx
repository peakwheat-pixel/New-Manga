import type { CSSProperties } from "react";
import type { TaskProjection } from "./client";
import { DisabledFeature } from "./DisabledFeature";
import { WorkbenchError } from "./WorkbenchError";

export interface TaskProgressPanelProps {
  projection: TaskProjection | null;
  loading?: boolean;
  busy?: boolean;
  error?: string | null;
  collapsed: boolean;
  onToggleCollapsed: () => void;
  onControl: (action: "pause" | "stop" | "continue" | "restart" | "abandon") => void;
  onResumeBlocked: () => void;
  onRetryFailed: () => void;
  onFilterStatus: (status: string) => void;
  onLocatePage: (pageId: string) => void;
  onRetry: () => void;
  pendingControl?: "pause" | "stop" | null;
}

const controlStyle = (enabled: boolean): CSSProperties => ({
  border: "1px solid #d9d9d6", borderRadius: 4, padding: "4px 8px", fontSize: 11,
  color: enabled ? "#1f2328" : "#6b7280", background: enabled ? "#fff" : "#f5f5f4",
  cursor: enabled ? "pointer" : "not-allowed", opacity: enabled ? 1 : 0.45,
});

export function TaskProgressPanel({
  projection, loading = false, busy = false, error, collapsed, onToggleCollapsed,
  onControl, onResumeBlocked, onRetryFailed, onFilterStatus, onLocatePage, onRetry, pendingControl = null,
}: TaskProgressPanelProps) {
  const progress = Math.max(0, Math.min(1, projection?.overall_progress ?? 0));
  const controls = projection?.controls;
  const can = (name: keyof NonNullable<typeof controls>) => !busy && controls?.[name] === true;
  const actionButtons = [
    { id: "pause", label: "暂停", enabled: can("can_pause"), onClick: () => onControl("pause") },
    { id: "stop", label: "停止", enabled: can("can_stop"), onClick: () => onControl("stop") },
    { id: "continue", label: "继续", enabled: can("can_continue"), onClick: () => onControl("continue") },
    { id: "restart", label: "重新启动", compact: "重启", enabled: can("can_restart"), onClick: () => onControl("restart") },
    { id: "abandon", label: "放弃", compact: "放弃", enabled: can("can_abandon"), onClick: () => onControl("abandon") },
    { id: "resume-blocked", label: "解除阻塞", compact: "解阻", enabled: !busy && projection?.run_status === "blocked", onClick: onResumeBlocked },
    { id: "retry-failed", label: "重试失败页", compact: "重试", enabled: can("can_retry_failed"), onClick: onRetryFailed },
  ];
  const controlsView = (
    <div data-testid="run-controls" style={{ display: "flex", flex: "0 0 auto", flexWrap: collapsed ? "nowrap" : "wrap", gap: 6 }}>
      {actionButtons.map((button) => (
        <button
          key={button.id}
          data-testid={`run-control-${button.id}`}
          type="button"
          aria-label={button.label}
          disabled={!button.enabled}
          title={button.enabled ? undefined : projection ? "当前 Run 状态不支持该操作" : "尚无可控制的 Run"}
          style={controlStyle(button.enabled)}
          onClick={button.onClick}
        >
          {collapsed ? button.compact ?? button.label : button.label}
        </button>
      ))}
    </div>
  );

  return (
    <section
      data-testid="task-progress-panel"
      aria-label="任务进度"
      onKeyDown={(event) => {
        if (!event.ctrlKey && !event.metaKey) return;
        if (event.key.toLowerCase() === "p") {
          if (can("can_pause")) { event.preventDefault(); onControl("pause"); }
          else if (can("can_continue")) { event.preventDefault(); onControl("continue"); }
        } else if (event.key === "." && can("can_stop")) {
          event.preventDefault();
          onControl("stop");
        }
      }}
      style={{
        flex: "0 0 auto", height: collapsed ? 44 : 220, minHeight: collapsed ? 44 : 220,
        overflow: "auto", background: "#fff", border: "1px solid #d9d9d6", borderRadius: 6,
        boxSizing: "border-box", padding: collapsed ? "4px 8px" : 8,
        display: "flex", flexDirection: collapsed ? "row" : "column", alignItems: collapsed ? "center" : undefined,
        gap: collapsed ? 8 : 6, color: "#1f2328",
      }}
    >
      <header style={{ display: "flex", alignItems: "center", gap: 8, minHeight: collapsed ? 0 : 24 }}>
        <h2 style={{ fontSize: 13, fontWeight: 600, margin: 0, flex: 1 }}>任务进度</h2>
        {projection && <strong data-testid="run-percent" style={{ fontVariantNumeric: "tabular-nums" }}>{Math.round(progress * 100)}%</strong>}
        <button type="button" onClick={onToggleCollapsed} aria-expanded={!collapsed} aria-label={collapsed ? "展开任务进度" : "折叠任务进度"}>
          {collapsed ? "展开" : "折叠"}
        </button>
      </header>
      {collapsed ? (
        <div style={{ display: "flex", flex: 1, minWidth: 0, gap: 8, alignItems: "center", minHeight: 24, fontSize: 11, overflowX: "auto", whiteSpace: "nowrap" }}>
          <span style={{ flex: 1 }}>{pendingControl ? (pendingControl === "pause" ? "正在暂停…" : "正在停止…") : projection?.run_title ?? (loading ? "正在读取任务…" : "当前没有已知任务")}</span>
          {projection?.current_page_id && <button type="button" onClick={() => onLocatePage(projection.current_page_id!)}>当前页：{projection.current_page_id}</button>}
          {projection && <span>当前步骤：{projection.current_step_type || "—"}</span>}
          <progress aria-label="整体进度" max={1} value={progress} style={{ width: 120 }} />
          {controlsView}
        </div>
      ) : (
        <>
          {pendingControl && <div data-testid="run-control-pending" role="status">{pendingControl === "pause" ? "正在暂停…" : "正在停止…"}</div>}
          {loading && <div data-testid="task-progress-loading" role="status">正在读取任务快照…</div>}
          {error && <div data-testid="task-progress-error"><WorkbenchError code={error} onRetry={onRetry} /></div>}
          {!projection && !loading && !error && <div data-testid="task-progress-empty">没有本次会话中已知的 Run。</div>}
          <DisabledFeature
            id="gap-g15-run-discovery"
            label="查看已有任务与中断 Run"
            reason="暂不可用：Core 尚无 ListRuns 查询；仅能查看本次工作台明确启动的 Run。"
          />
          {projection && (
            <>
              <DisabledFeature id="gap-g18-current-page-thumbnail" label="当前页缩略图" reason="低清预览/缩略图通道尚未接入，当前不会把原图当缩略图加载。" />
              <div style={{ display: "flex", gap: 12, alignItems: "center", fontSize: 11 }}>
                <span>{projection.run_title}</span>
                <span>状态：{projection.run_status}</span>
                {projection.current_page_id && <button type="button" onClick={() => onLocatePage(projection.current_page_id!)}>当前页：{projection.current_page_id}</button>}
                <span>当前步骤：{projection.current_step_type || "—"}</span>
              </div>
              <progress data-testid="run-progress" aria-label="整体进度" max={1} value={progress} style={{ width: "100%" }} />
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, fontSize: 11 }}>
                {(["completed", "failed", "skipped", "waiting", "blocked"] as const).map((status) => {
                  const count = status === "waiting" ? projection.counts.waiting + projection.counts.processing : projection.counts[status];
                  return <button key={status} type="button" onClick={() => onFilterStatus(status)}>{status} {count}</button>;
                })}
              </div>
              {projection.blocked_reasons.length > 0 && (
                <ul aria-label="阻塞原因" style={{ margin: 0, paddingLeft: 20, fontSize: 11 }}>
                  {projection.blocked_reasons.map((reason, index) => <li key={index}>{reason}</li>)}
                </ul>
              )}
              <div data-testid="run-step-flow" style={{ display: "flex", gap: 6, overflowX: "auto", fontSize: 10 }}>
                {projection.step_flow.map((step, index) => (
                  <span key={`${step.type}-${index}`} aria-current={step.state === "running" ? "step" : undefined} style={{ whiteSpace: "nowrap", fontWeight: step.state === "running" ? 700 : 400 }}>
                    {step.label} · {step.state}{index < projection.step_flow.length - 1 ? " →" : ""}
                  </span>
                ))}
              </div>
              <details data-testid="task-detail-popover" style={{ position: "relative", alignSelf: "flex-start" }}>
                <summary>任务详情（{projection.tasks.length}）</summary>
                <div style={{ position: "absolute", zIndex: 20, right: 0, bottom: "calc(100% + 4px)", width: 420, maxHeight: 160, overflow: "auto", fontSize: 11, background: "#fff", border: "1px solid #d9d9d6", borderRadius: 4, padding: 8, boxShadow: "0 2px 8px rgba(0,0,0,.15)" }}>
                  {projection.tasks.map((task) => (
                    <details key={task.task_id}>
                      <summary>{task.page_id} · {task.status}{task.error_code ? ` · ${task.error_code}` : ""}</summary>
                      <ul style={{ marginTop: 4 }}>
                        {task.steps.map((step) => <li key={step.step_run_id}>
                          {step.step_type} · {step.status} · 重试 {step.retry_no}
                          {step.error_code ? ` · ${step.error_code}` : ""}
                          {[step.provider, step.model, step.device].filter(Boolean).join(" / ") && ` · ${[step.provider, step.model, step.device].filter(Boolean).join(" / ")}`}
                        </li>)}
                      </ul>
                    </details>
                  ))}
                </div>
              </details>
            </>
          )}
          {controlsView}
        </>
      )}
    </section>
  );
}
