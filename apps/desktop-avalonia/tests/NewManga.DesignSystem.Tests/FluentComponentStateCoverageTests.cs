using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-4: declaration coverage for the Fluent component state matrix from
/// `doc/design/fluent-v1/10-component-inventory.md` §1–§3. This proves the style layer declares each
/// required normal/hover/pressed/disabled/selected state; it is NOT a rendered-visual PASS — headless
/// pseudo-class rendering cells that cannot be synthesised reliably stay NOT_RUN in the task evidence.
/// </summary>
public sealed class FluentComponentStateCoverageTests
{
    private static readonly Dictionary<string, string[]> RequiredSelectors = new(StringComparer.Ordinal)
    {
        ["Button.fluent-primary"] = [":pointerover", ":pressed", ":disabled"],
        ["Button.fluent-secondary"] = [":pointerover", ":pressed", ":disabled"],
        ["Button.fluent-danger"] = [":pointerover", ":pressed"],
        [".fluent-book-card"] = [":pointerover", ":pressed", ":disabled"],
        [".fluent-book-row"] = [":pointerover", ":pressed", ":disabled"],
        ["Button.fluent-space-button"] = [":pointerover", ":pressed", ":disabled"],
        ["Button.fluent-command-row"] = [":pointerover", ":pressed", ":disabled"],
        ["Button.segmented-item"] = [".selected", ":pointerover", ":pressed", ":disabled"],
        ["Slider"] = [":pointerover", ":disabled"],
        ["TabItem"] = [":pointerover", ":selected", ":disabled"],
        [".fluent-surface-card"] = [":pointerover", ".selected", ":disabled"],
        [".fluent-chapter-list"] = [],
        [".fluent-streaming-thumb"] = [],
        [".fluent-batch-matrix"] = [],
        [".fluent-run-projection-bar"] = [],
        [".fluent-reader-page"] = [],
        [".fluent-reader-progress"] = [],
        [".fluent-settings-group"] = [],
        [".fluent-settings-field"] = [],
        [".fluent-tab-strip"] = [],

        ["Border.fluent-detail-pane"] = [],
        [".fluent-region-box"] = [":pointerover", ".selected"],
        [".fluent-dialog"] = [],
        ["ds|Drawer.fluent-drawer"] = [],
    };

    [Fact]
    public void Fluent_styles_declare_the_required_component_state_matrix()
    {
        var stylesRoot = Path.Combine(RepositoryRoot(), "apps", "desktop-avalonia", "src", "NewManga.DesignSystem", "Styles");
        var declared = Directory.EnumerateFiles(stylesRoot, "*.axaml")
            .Select(File.ReadAllText)
            .SelectMany(text => StyleSelectors(text))
            .ToHashSet(StringComparer.Ordinal);

        var missing = new List<string>();
        foreach (var (selector, states) in RequiredSelectors)
        {
            if (!declared.Contains(selector))
            {
                missing.Add(selector);
                continue;
            }

            missing.AddRange(states
                .Where(state => !declared.Contains(selector + state))
                .Select(state => selector + state));
        }

        Assert.True(missing.Count == 0, "missing Fluent component/state styles: " + string.Join(", ", missing));
    }

    private static IEnumerable<string> StyleSelectors(string axaml) =>
        System.Text.RegularExpressions.Regex
            .Matches(axaml, "<Style\\s+Selector=\"([^\"]+)\"")
            .Select(match => match.Groups[1].Value);

    private static string RepositoryRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06-RESIDUAL-1.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("repository root not found");
    }
}
