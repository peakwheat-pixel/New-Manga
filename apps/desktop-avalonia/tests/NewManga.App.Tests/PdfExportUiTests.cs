using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using NewManga.App.Services;
using NewManga.App.Views;
using NewManga.CoreClient.Issuer;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// PDF-EXPORT-UI-1: the export panel now exposes the PDF format the Core already implements
/// (<c>QtFreePdfComposer</c>; image_only / searchable_dual_layer) instead of a ZIP-only flow.
/// These headless tests drive the real panel controls and assert the exact StartExport arguments
/// (<c>format</c> + <c>format_options.pdf_content</c>) plus the completed/failed status text.
/// </summary>
public sealed class PdfExportUiTests
{
    private static string EvidenceDirectory
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            var root = string.IsNullOrWhiteSpace(configured)
                ? Path.Combine(Path.GetTempPath(), "newmanga-pdf-export-ui-evidence")
                : configured;
            var directory = Path.Combine(root, "pdf-export-ui");
            Directory.CreateDirectory(directory);
            return directory;
        }
    }

    private static void WriteEvidence(string name, Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2/AC3");
            write(writer);
            writer.WriteEndObject();
        }

        File.WriteAllBytes(Path.Combine(EvidenceDirectory, name + ".json"), stream.ToArray());
    }

    private static FakeHostController HostWithExportableChapter()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("书A"))
        {
            ExportDirectorySuggestionValue = Path.Combine(Path.GetTempPath(), "newmanga-pdf-ui-exports"),
        };
        host.TranslatedPagesByChapter["ch-1"] = new[] { "p1", "p2", "p3" };
        return host;
    }

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static async Task<ExportPanel> PreparedPanelAsync(FakeHostController host)
    {
        var panel = new ExportPanel(host) { AutoPoll = false };
        await panel.PrepareAsync("book-0", "书A", "ch-1", "第 1 章");
        return panel;
    }

    private const string PdfSha =
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

    // ------------------------------------------------------------------
    // AC1: format selection → exact StartExport parameters
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task PdfFormat_SendsFormatAndPdfContent_AndPdfTargetExtension()
    {
        var host = HostWithExportableChapter();
        var panel = await PreparedPanelAsync(host);
        Assert.False(panel.PdfModeRowVisible, "PDF mode selector is hidden for the default ZIP format");

        panel.FormatSelector.SelectedIndex = 1; // PDF
        Assert.True(panel.PdfModeRowVisible);
        panel.PdfModeSelector.SelectedIndex = 1; // image_only
        Assert.Equal("pdf", panel.SelectedFormat);
        Assert.Equal("image_only", panel.SelectedPdfContent);

        Click(panel.StartButton);
        await panel.LastOperation;

        var call = Assert.Single(host.StartExportCalls);
        Assert.Equal("book-0", call.BookId);
        Assert.Equal("ch-1", call.ChapterId);
        Assert.Equal(new[] { "p1", "p2", "p3" }, call.PageIds);
        Assert.Equal("pdf", call.Format);
        Assert.Equal("image_only", call.PdfContent);
        Assert.EndsWith(".pdf", call.TargetPath, StringComparison.Ordinal);

        WriteEvidence("pdf-format-params", writer =>
        {
            writer.WriteString("scenario", "PDF + image_only -> StartExport(format=pdf, pdf_content=image_only)");
            writer.WriteString("format", call.Format);
            writer.WriteString("pdf_content", call.PdfContent ?? "");
            writer.WriteString("target_extension", Path.GetExtension(call.TargetPath));
            writer.WriteBoolean("pdf_mode_row_visible", panel.PdfModeRowVisible);
        });
    }

    [AvaloniaFact]
    public async Task SearchableDualLayer_IsForwarded_AndZipStaysZip()
    {
        var pdfHost = HostWithExportableChapter();
        var pdfPanel = await PreparedPanelAsync(pdfHost);
        pdfPanel.FormatSelector.SelectedIndex = 1; // PDF
        pdfPanel.PdfModeSelector.SelectedIndex = 0; // searchable_dual_layer
        Click(pdfPanel.StartButton);
        await pdfPanel.LastOperation;
        var pdfCall = Assert.Single(pdfHost.StartExportCalls);
        Assert.Equal("pdf", pdfCall.Format);
        Assert.Equal("searchable_dual_layer", pdfCall.PdfContent);

        var zipHost = HostWithExportableChapter();
        var zipPanel = await PreparedPanelAsync(zipHost);
        Assert.False(zipPanel.PdfModeRowVisible);
        Click(zipPanel.StartButton);
        await zipPanel.LastOperation;
        var zipCall = Assert.Single(zipHost.StartExportCalls);
        Assert.Equal("zip", zipCall.Format);
        Assert.Null(zipCall.PdfContent);
        Assert.EndsWith(".zip", zipCall.TargetPath, StringComparison.Ordinal);

        WriteEvidence("zip-pdf-both", writer =>
        {
            writer.WriteString("scenario", "searchable_dual_layer PDF and ZIP both forwarded");
            writer.WriteString("pdf_content", pdfCall.PdfContent ?? "");
            writer.WriteString("zip_format", zipCall.Format);
            writer.WriteBoolean("zip_pdf_content_null", zipCall.PdfContent is null);
        });
    }

    // ------------------------------------------------------------------
    // AC2: completed state shows real path + sha256 + pages + distinguishable format
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task CompletedPdf_ShowsPathSha256PagesAndMode()
    {
        var host = HostWithExportableChapter();
        host.ScriptedStartResults.Enqueue(new ExportStartInfo("exp-pdf-1", "pending", 3));
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo(
            "exp-pdf-1",
            ExportJobState.Completed,
            3,
            3,
            null,
            Path.Combine(Path.GetTempPath(), "newmanga-pdf-ui-exports", "book.pdf"),
            PdfSha,
            null,
            "pdf"));
        var panel = await PreparedPanelAsync(host);
        panel.FormatSelector.SelectedIndex = 1;
        panel.PdfModeSelector.SelectedIndex = 0; // searchable_dual_layer

        Click(panel.StartButton);
        await panel.LastOperation;
        var status = panel.StatusText.Text ?? string.Empty;

        Assert.Contains("导出完成", status, StringComparison.Ordinal);
        Assert.Contains("PDF · searchable_dual_layer", status, StringComparison.Ordinal);
        Assert.Contains("book.pdf", status, StringComparison.Ordinal);
        Assert.Contains("sha256 " + PdfSha, status, StringComparison.Ordinal);
        Assert.Contains("3 页", status, StringComparison.Ordinal);
        Assert.Equal(ExportJobState.Completed, panel.LastSnapshot?.State);

        WriteEvidence("completed-pdf", writer =>
        {
            writer.WriteString("scenario", "completed PDF snapshot rendered with path/sha256/pages/format");
            writer.WriteString("status", status);
            writer.WriteString("sha256", panel.LastSnapshot?.Sha256 ?? string.Empty);
            writer.WriteNumber("total_pages", panel.LastSnapshot?.TotalPages ?? 0);
        });
    }

    [AvaloniaFact]
    public async Task CompletedZip_IsLabelledAsZipImagePack()
    {
        var host = HostWithExportableChapter();
        host.ScriptedStartResults.Enqueue(new ExportStartInfo("exp-zip-1", "pending", 2));
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo(
            "exp-zip-1",
            ExportJobState.Completed,
            2,
            2,
            null,
            Path.Combine(Path.GetTempPath(), "newmanga-pdf-ui-exports", "book.zip"),
            PdfSha,
            null,
            "zip"));
        var panel = await PreparedPanelAsync(host);
        Click(panel.StartButton);
        await panel.LastOperation;
        var status = panel.StatusText.Text ?? string.Empty;

        Assert.Contains("ZIP 图片包", status, StringComparison.Ordinal);
        Assert.DoesNotContain("PDF ·", status, StringComparison.Ordinal);
        Assert.Contains("sha256 " + PdfSha, status, StringComparison.Ordinal);
        Assert.Contains("2 页", status, StringComparison.Ordinal);

        WriteEvidence("completed-zip", writer =>
        {
            writer.WriteString("scenario", "completed ZIP snapshot keeps its own label");
            writer.WriteString("status", status);
        });
    }

    // ------------------------------------------------------------------
    // AC3: typed errors stay honest
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task FailedSnapshot_ShowsTypedError_AndRefusedStartIsExplicit()
    {
        var failedHost = HostWithExportableChapter();
        failedHost.ScriptedStartResults.Enqueue(new ExportStartInfo("exp-fail-1", "pending", 1));
        failedHost.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo(
            "exp-fail-1",
            ExportJobState.Failed,
            0,
            1,
            null,
            null,
            null,
            "EXPORT_INPUT_UNAVAILABLE",
            "pdf"));
        var failedPanel = await PreparedPanelAsync(failedHost);
        failedPanel.FormatSelector.SelectedIndex = 1;
        Click(failedPanel.StartButton);
        await failedPanel.LastOperation;
        var failedStatus = failedPanel.StatusText.Text ?? string.Empty;
        Assert.Contains("导出失败", failedStatus, StringComparison.Ordinal);
        Assert.Contains("EXPORT_INPUT_UNAVAILABLE", failedStatus, StringComparison.Ordinal);

        var refusedHost = HostWithExportableChapter();
        refusedHost.ScriptedStartResults.Enqueue(null);
        var refusedPanel = await PreparedPanelAsync(refusedHost);
        refusedPanel.FormatSelector.SelectedIndex = 1;
        Click(refusedPanel.StartButton);
        await refusedPanel.LastOperation;
        var refusedStatus = refusedPanel.StatusText.Text ?? string.Empty;
        Assert.Contains("导出被拒绝", refusedStatus, StringComparison.Ordinal);

        WriteEvidence("errors", writer =>
        {
            writer.WriteString("scenario", "failed snapshot + refused start render typed text");
            writer.WriteString("failed_status", failedStatus);
            writer.WriteString("refused_status", refusedStatus);
        });
    }

    // ------------------------------------------------------------------
    // Contract: payload matches what HostIssuer accepts (no Core/Host contract change)
    // ------------------------------------------------------------------

    [Fact]
    public void PayloadOptions_MatchTheHostIssuerPdfContract()
    {
        var pdf = ImportExportPayloads.StartExportRequest(
            "book-0",
            new[] { "ch-1" },
            new[] { "p1", "p2" },
            "pdf",
            "abort",
            "searchable_dual_layer");
        Assert.Equal("pdf", pdf.GetProperty("format").GetString());
        Assert.Equal("searchable_dual_layer", pdf.GetProperty("format_options").GetProperty("pdf_content").GetString());
        var properties = pdf.EnumerateObject().Select(property => property.Name).OrderBy(name => name).ToArray();
        Assert.Equal(new[] { "book_id", "chapter_ids", "format", "format_options", "ordered_page_ids", "stale_policy" }, properties);

        var zip = ImportExportPayloads.StartExportRequest("book-0", new[] { "ch-1" }, new[] { "p1" }, "zip");
        Assert.Equal("standard", zip.GetProperty("format_options").GetProperty("compression").GetString());

        var (format, extension) = HostIssuer.ValidateExportRequest(pdf);
        Assert.Equal("pdf", format);
        Assert.Equal("pdf", extension);
        var (zipFormat, zipExtension) = HostIssuer.ValidateExportRequest(zip);
        Assert.Equal("zip", zipFormat);
        Assert.Equal("zip", zipExtension);

        Assert.EndsWith(".pdf", ImportExportFormatting.DefaultExportFileName("书", "章", "pdf"), StringComparison.Ordinal);
        Assert.EndsWith(".zip", ImportExportFormatting.DefaultExportFileName("书", "章"), StringComparison.Ordinal);
        Assert.Equal("PDF · image_only", ImportExportFormatting.FormatDisplay("pdf", "image_only"));
        Assert.Equal("ZIP 图片包", ImportExportFormatting.FormatDisplay("zip"));

        WriteEvidence("payload-contract", writer =>
        {
            writer.WriteString("scenario", "App payload validated by HostIssuer (no contract change)");
            writer.WriteString("pdf_extension", extension);
            writer.WriteString("zip_extension", zipExtension);
            writer.WriteString("format_options", pdf.GetProperty("format_options").GetRawText());
        });
    }
}
