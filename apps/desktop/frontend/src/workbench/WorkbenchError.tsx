import { parseSemanticError } from "../bookshelf/error";

export function WorkbenchError({
  code,
  onRetry,
  fullArea = false,
}: {
  code: string;
  onRetry?: () => void;
  fullArea?: boolean;
}) {
  const error = parseSemanticError(code);
  return (
    <section role="alert" data-testid="workbench-error" style={{
      color: "#1f2328", background: "#fff", border: "1px solid #d9d9d6", borderRadius: 6,
      padding: 12, fontSize: 12, ...(fullArea ? { flex: 1, display: "grid", placeContent: "center", textAlign: "center" as const } : {}),
    }}>
      <strong>{error.title}</strong>
      <p style={{ margin: "6px 0" }}>{error.message}</p>
      <small>错误代码：{error.code}</small>
      {onRetry && error.retryable && <div><button type="button" onClick={onRetry}>重试</button></div>}
    </section>
  );
}
