import { tokens } from "../theme/tokens";

/**
 * The P15 AC2 disabled-partition placeholder: every section whose schema is
 * not frozen (OCR / translation-context / inpaint / typography / reading
 * direction / model-GPU / concurrency / cache-revision / recycle bin (G2) /
 * backup / plugins) is VISIBLE, NOT operable, and states the reason
 * "等待 section schema 冻结". No mock values, no invented keys.
 */
export const DISABLED_SECTION_REASON = "等待 section schema 冻结";

export function DisabledSection({
  testId,
  title,
  reason = DISABLED_SECTION_REASON,
}: {
  testId: string;
  title: string;
  reason?: string;
}) {
  return (
    <section
      data-testid={testId}
      aria-disabled="true"
      data-disabled-reason={reason}
      style={{
        padding: tokens.spacing.xl,
        backgroundColor: tokens.color.surface.card,
        border: `1px dashed ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        textAlign: "center",
        color: tokens.color.text.secondary,
        maxWidth: 560,
        opacity: 0.75,
      }}
    >
      <div style={{ fontSize: 30, marginBottom: tokens.spacing.sm }}>🔒</div>
      <h3
        data-testid={`${testId}-title`}
        style={{
          margin: 0,
          fontSize: tokens.typography.size.cardTitle,
          color: tokens.color.text.primary,
          fontWeight: 600,
        }}
      >
        {title}
      </h3>
      <p
        data-testid={`${testId}-reason`}
        style={{
          fontSize: tokens.typography.size.base,
          marginTop: tokens.spacing.xs,
          color: tokens.color.text.muted,
          lineHeight: tokens.typography.lineHeight,
        }}
      >
        该分区暂不可编辑：{reason}。此处不会以占位数据或本地推断填充任何设置值。
      </p>
      {/* Operable-looking control rendered disabled so the partition is
       * visibly present but cannot be interacted with. */}
      <button
        type="button"
        disabled
        aria-disabled="true"
        title={reason}
        style={{
          marginTop: tokens.spacing.md,
          padding: "4px 12px",
          fontSize: tokens.typography.size.base,
          border: `1px solid ${tokens.color.border.default}`,
          borderRadius: tokens.radius.button,
          background: tokens.color.bg.toolbar,
          color: tokens.color.text.muted,
          cursor: "not-allowed",
          opacity: 0.45,
        }}
      >
        编辑该分区
      </button>
    </section>
  );
}
