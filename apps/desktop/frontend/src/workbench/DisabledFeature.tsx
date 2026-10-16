export function DisabledFeature({
  id,
  label,
  reason,
}: {
  id: string;
  label: string;
  reason: string;
}) {
  return (
    <span
      data-testid={id}
      title={reason}
      style={{ display: "inline-flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}
    >
      <button type="button" disabled aria-describedby={`${id}-reason`} style={{ opacity: 0.45, cursor: "not-allowed" }}>
        {label}
      </button>
      <small id={`${id}-reason`} style={{ color: "#6b7280", fontSize: 10, lineHeight: 1.3 }}>{reason}</small>
    </span>
  );
}
