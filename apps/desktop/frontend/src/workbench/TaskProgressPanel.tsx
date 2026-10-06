/**
 * <TaskProgressPanel> — first-slice STATIC SKELETON placeholder (Task AC2:
 * the task data channel rides GetRunSnapshot/GetTaskProjection whose runtime
 * is a §5 PROPOSAL; standing up a new command face for a placeholder is
 * explicitly forbidden, so this slice renders the frozen badge skeleton with
 * no data wire). The nine-state badge mapping and the run controls belong to
 * the later parity slices.
 */

export function TaskProgressPanel() {
  return (
    <section
      data-testid="task-progress-panel"
      style={{
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: 8,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <h2 style={{ fontSize: 12, margin: 0, color: "#d8e0e8" }}>Tasks</h2>
      <p
        data-testid="task-progress-placeholder"
        style={{ color: "#8a94a2", fontSize: 11, margin: 0 }}
      >
        任务进度通道占位（GetTaskProjection runtime 未释放；占位不扩命令面）
      </p>
    </section>
  );
}
