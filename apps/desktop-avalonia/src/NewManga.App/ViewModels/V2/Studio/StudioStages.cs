namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-3/B-4: one pipeline stage column. <see cref="CoreStepType"/> is the Core step vocabulary
/// (<c>projection.py</c> <c>_STEP_LABELS</c>); null means the stage is a product-level column that the
/// task projection does not carry (it must render as "no projection", never as a fabricated state).
/// </summary>
public sealed record StudioStage(
    string Key,
    string Abbreviation,
    string Label,
    int Index,
    string? CoreStepType);

/// <summary>
/// The ten stages of the Page pipeline band and the Batch status matrix
/// (DESIGN_SYSTEM §6.3 "列=10 阶段", A-darkroom <c>footer.pipeline</c> dot array).
/// Keys 1–9 are the Core task-projection steps (detect…render); <c>save</c> is the product-level
/// 保存/导出 column and therefore carries no projection step type.
/// </summary>
public static class StudioStages
{
    public static IReadOnlyList<StudioStage> Canonical { get; } = new[]
    {
        new StudioStage("detect", "DET", "检测", 1, "detect"),
        new StudioStage("ocr", "OCR", "识别", 2, "ocr"),
        new StudioStage("color", "CLR", "配色", 3, "color"),
        new StudioStage("term", "TERM", "术语", 4, "term_extract"),
        new StudioStage("translate", "TRAN", "翻译", 5, "translate"),
        new StudioStage("segment", "SEG", "分割", 6, "segment"),
        new StudioStage("mask", "MASK", "掩膜", 7, "mask_refine"),
        new StudioStage("inpaint", "INP", "修复", 8, "inpaint"),
        new StudioStage("render", "REND", "渲染", 9, "render"),
        new StudioStage("save", "SAVE", "保存", 10, null),
    };

    public static int Count => Canonical.Count;

    /// <summary>Index of the <c>save</c> column (the only projection-less product column).</summary>
    public static StudioStage Save { get; } = Canonical[^1];

    /// <summary>Finds the canonical stage for a Core step type (null when the step is not a column).</summary>
    public static StudioStage? FindByCoreStep(string? coreStepType)
    {
        if (string.IsNullOrWhiteSpace(coreStepType))
        {
            return null;
        }

        foreach (var stage in Canonical)
        {
            if (stage.CoreStepType is not null &&
                string.Equals(stage.CoreStepType, coreStepType, StringComparison.OrdinalIgnoreCase))
            {
                return stage;
            }
        }

        return null;
    }

    /// <summary>Compact label used by the Page pipeline band ("OCR 识别" → "识别").</summary>
    public static string BandLabel(StudioStage stage) => stage.Label;

    /// <summary>Column header text for the Batch matrix ("识别" → "OCR 识别" is too wide at 18px).</summary>
    public static string MatrixHeader(StudioStage stage) => stage.Abbreviation;
}
