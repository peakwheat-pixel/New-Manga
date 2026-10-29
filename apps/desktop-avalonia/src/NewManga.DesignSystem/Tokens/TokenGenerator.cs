using System.Globalization;
using NewManga.DesignSystem.Accessibility;

namespace NewManga.DesignSystem.Tokens;

/// <summary>One generated artifact: repository-relative-to-project path + full file content (UTF-8, LF).</summary>
public sealed record GeneratedFile(string RelativePath, string Content);

/// <summary>One row of the generated token -> resource-key map (also the AC1 evidence artifact).</summary>
public sealed record GeneratedMappingRow(
    string Scope,
    string TokenPath,
    string ResourceKey,
    TokenValueKind Kind,
    string RawValue);

/// <summary>Deterministic output of one token-pipeline run.</summary>
public sealed record TokenGenerationResult(
    IReadOnlyList<GeneratedFile> Files,
    IReadOnlyList<GeneratedMappingRow> Rows,
    IReadOnlyList<string> Warnings);

/// <summary>
/// Reproducible <c>tokens.json</c> -> Avalonia resource-dictionary generator (AC1). The output depends
/// only on the frozen token document and the static <see cref="TokenMap"/> tables: no timestamps, no
/// machine paths, LF newlines, ordinal ordering.
/// </summary>
public static class TokenGenerator
{
    /// <summary>Repository-relative path of the frozen token source.</summary>
    public const string TokensRelativePath = "doc/design/redesign-v1/40-fusion/tokens.json";

    /// <summary>Generated artifacts, project-directory-relative, in emission order.</summary>
    public static IReadOnlyList<string> GeneratedFilePaths { get; } =
    [
        "Themes/Tokens.Dark.axaml",
        "Themes/Tokens.Light.axaml",
        "Themes/Tokens.Global.axaml",
        "Themes/Tokens.HighContrast.axaml",
        "Themes/Density.Compact.axaml",
        "Themes/Density.Spacious.axaml",
        "Themes/Motion.Reduced.axaml",
        "Generated/NmKeys.g.cs",
        "Generated/StatusCatalog.g.cs",
        "Generated/TokenMap.md",
    ];

    /// <summary>Runs the pipeline in memory.</summary>
    public static TokenGenerationResult Generate(string tokensJson)
    {
        ArgumentNullException.ThrowIfNull(tokensJson);

        var entries = TokenDocument.Parse(tokensJson);
        var dark = ColorEntries(entries, TokenMap.DarkScope);
        var light = ColorEntries(entries, TokenMap.LightScope);

        if (dark.Count == 0 || light.Count == 0)
        {
            throw new InvalidOperationException("tokens.json has no dark/light palettes");
        }

        var darkKeys = dark.Select(entry => TokenMap.ColorResourceKey(entry.Path)).ToArray();
        var lightKeys = light.Select(entry => TokenMap.ColorResourceKey(entry.Path)).ToArray();
        AssertSameKeySet(darkKeys, lightKeys);

        var rows = new List<GeneratedMappingRow>(entries.Count + TokenMap.DerivedGlobals.Count + 64);
        var warnings = new List<string>();

        // ---- Global (theme-invariant) resources -------------------------------------------------
        var globalBindings = TokenMap.GlobalBindings.ToDictionary(
            static binding => binding.TokenPath,
            static binding => binding,
            StringComparer.Ordinal);

        var tokenPaths = new HashSet<string>(StringComparer.Ordinal);
        var resourceKeys = new HashSet<string>(StringComparer.Ordinal);

        var globalRows = new List<(string Key, TokenValueKind Kind, string RawValue)>(TokenMap.GlobalBindings.Count);
        var globalCount = 0;
        foreach (var entry in entries)
        {
            if (entry.Path.StartsWith(TokenMap.DarkScope, StringComparison.Ordinal) ||
                entry.Path.StartsWith(TokenMap.LightScope, StringComparison.Ordinal))
            {
                continue;
            }

            if (!globalBindings.TryGetValue(entry.Path, out var binding))
            {
                throw new InvalidOperationException($"global token '{entry.Path}' has no resource-key mapping");
            }

            ValidateKind(entry, binding.Kind);
            if (!tokenPaths.Add(entry.Path))
            {
                throw new InvalidOperationException($"token '{entry.Path}' is mapped twice");
            }

            if (!resourceKeys.Add(binding.ResourceKey))
            {
                throw new InvalidOperationException($"resource key '{binding.ResourceKey}' is published twice");
            }

            globalRows.Add((binding.ResourceKey, binding.Kind, entry.Value));
            rows.Add(new GeneratedMappingRow("global", entry.Path, binding.ResourceKey, binding.Kind, entry.Value));
            globalCount++;
        }

        foreach (var derived in TokenMap.DerivedGlobals)
        {
            if (!resourceKeys.Add(derived.ResourceKey))
            {
                throw new InvalidOperationException($"derived resource key '{derived.ResourceKey}' collides with a token binding");
            }

            globalRows.Add((derived.ResourceKey, derived.Kind, derived.RawValue));
            rows.Add(new GeneratedMappingRow(
                "global-derived", "(derived)", derived.ResourceKey, derived.Kind, derived.RawValue));
            warnings.Add($"derived token {derived.ResourceKey} = {derived.RawValue} ({derived.Derivation})");
        }

        // ---- Palettes --------------------------------------------------------------------------
        var darkRows = dark
            .Select(entry => (TokenMap.ColorResourceKey(entry.Path), entry.Value))
            .ToArray();
        var lightRows = light
            .Select(entry => (TokenMap.ColorResourceKey(entry.Path), entry.Value))
            .ToArray();

        foreach (var entry in dark)
        {
            rows.Add(new GeneratedMappingRow("dark", entry.Path, TokenMap.ColorResourceKey(entry.Path), TokenValueKind.Brush, entry.Value));
        }

        foreach (var entry in light)
        {
            rows.Add(new GeneratedMappingRow("light", entry.Path, TokenMap.ColorResourceKey(entry.Path), TokenValueKind.Brush, entry.Value));
        }

        // ---- High contrast (derived extension; curated overrides on top of the frozen palette) --
        var highContrastByKey = TokenMap.HighContrast.ToDictionary(
            static entry => entry.ResourceKey,
            StringComparer.Ordinal);

        var darkBrushes = darkRows.ToDictionary(static row => row.Item1, static row => row.Item2, StringComparer.Ordinal);
        var lightBrushes = lightRows.ToDictionary(static row => row.Item1, static row => row.Item2, StringComparer.Ordinal);

        var highContrastDark = new List<(string Key, string RawValue)>(darkBrushes.Count);
        var highContrastLight = new List<(string Key, string RawValue)>(lightBrushes.Count);
        foreach (var key in darkKeys.OrderBy(static value => value, StringComparer.Ordinal))
        {
            // High contrast re-curates every foreground channel but deliberately keeps the frozen
            // five-level background ladder (DESIGN_SYSTEM §1 rule 2); uncovered keys copy the palette.
            var darkValue = highContrastByKey.TryGetValue(key, out var overrides)
                ? overrides.DarkRawValue
                : darkBrushes[key];
            var lightValue = highContrastByKey.TryGetValue(key, out overrides)
                ? overrides.LightRawValue
                : lightBrushes[key];

            highContrastDark.Add((key, darkValue));
            highContrastLight.Add((key, lightValue));
            rows.Add(new GeneratedMappingRow("high-contrast-dark", "(contrast)", key, TokenValueKind.Brush, darkValue));
            rows.Add(new GeneratedMappingRow("high-contrast-light", "(contrast)", key, TokenValueKind.Brush, lightValue));
        }

        // ---- Density overlays ------------------------------------------------------------------
        var compactRows = new List<(string Key, string RawValue)>(TokenMap.Density.Count);
        var spaciousRows = new List<(string Key, string RawValue)>(TokenMap.Density.Count);
        foreach (var density in TokenMap.Density)
        {
            compactRows.Add((density.ResourceKey, density.CompactRawValue));
            spaciousRows.Add((density.ResourceKey, density.SpaciousRawValue));
            rows.Add(new GeneratedMappingRow("density-compact", "(density)", density.ResourceKey, density.Kind, density.CompactRawValue));
            rows.Add(new GeneratedMappingRow("density-spacious", "(density)", density.ResourceKey, density.Kind, density.SpaciousRawValue));
        }

        // ---- Motion reduced overlay ------------------------------------------------------------
        var reducedMotionRows = new List<(string Key, TokenValueKind Kind, string RawValue)>
        {
            ("Nm.Motion.Duration.Instant", TokenValueKind.TimeSpan, "0ms"),
            ("Nm.Motion.Duration.Fast", TokenValueKind.TimeSpan, "0ms"),
            ("Nm.Motion.Duration.Normal", TokenValueKind.TimeSpan, "0ms"),
            ("Nm.Motion.Enabled", TokenValueKind.Boolean, "false"),
        };
        foreach (var (key, kind, value) in reducedMotionRows)
        {
            rows.Add(new GeneratedMappingRow("motion-reduced", "(motion)", key, kind, value));
        }

        // ---- Emit artifacts (after rule validation so a rule violation fails generation) ----------
        ValidateDerivationRules(entries, darkBrushes, lightBrushes, highContrastDark, highContrastLight, compactRows, spaciousRows);

        var files = new List<GeneratedFile>(GeneratedFilePaths.Count)
        {
            new("Themes/Tokens.Dark.axaml",
                TokenDictionaryWriter.BrushDictionary(darkRows, "Dark palette (35 color tokens).")),
            new("Themes/Tokens.Light.axaml",
                TokenDictionaryWriter.BrushDictionary(lightRows, "Light palette (35 color tokens).")),
            new("Themes/Tokens.Global.axaml",
                TokenDictionaryWriter.GlobalDictionary(globalRows,
                    $"Theme-invariant tokens: {globalCount} frozen global tokens + {TokenMap.DerivedGlobals.Count} contract-derived resources.")),
            new("Themes/Tokens.HighContrast.axaml",
                TokenDictionaryWriter.ThemeScopedBrushDictionary(highContrastDark, highContrastLight,
                    "High-contrast extension (complete palette, theme scoped). Derived by rule (contract §2.4): " +
                    "text.primary/secondary/tertiary >= 7:1, status/accent >= 4.5:1 against the frozen surface ladder; " +
                    "not a second truth source.")),
            new("Themes/Density.Compact.axaml",
                TokenDictionaryWriter.GlobalDictionary(
                    compactRows.Select(static row => (row.Key, DensityKind(row.Key), row.RawValue)).ToArray(),
                    "Density overlay: Compact.")),
            new("Themes/Density.Spacious.axaml",
                TokenDictionaryWriter.GlobalDictionary(
                    spaciousRows.Select(static row => (row.Key, DensityKind(row.Key), row.RawValue)).ToArray(),
                    "Density overlay: Spacious.")),
            new("Themes/Motion.Reduced.axaml",
                TokenDictionaryWriter.GlobalDictionary(reducedMotionRows,
                    "Reduced-motion overlay: zeroes every duration and flips Nm.Motion.Enabled to false.")),
            new("Generated/NmKeys.g.cs",
                TokenDictionaryWriter.KeysClass(
                    resourceKeys.Concat(darkKeys).ToArray(),
                    "Token-derived Nm.* resource-key constants (contract §2).")),
            new("Generated/StatusCatalog.g.cs",
                TokenDictionaryWriter.StatusSymbolsClass(
                    entries
                        .Where(static entry => entry.Path.StartsWith("stateSymbols.", StringComparison.Ordinal))
                        .Select(static entry => (TokenMap.PascalCaseSegment(entry.Path["stateSymbols.".Length..]), entry.Value))
                        .ToArray(),
                    "Status symbols generated from the frozen stateSymbols tokens (DESIGN_SYSTEM §2.2).")),
            new("Generated/TokenMap.md",
                TokenDictionaryWriter.MapMarkdown(rows,
                    "Source: doc/design/redesign-v1/40-fusion/tokens.json (FROZEN) + TokenMap tables.")),
        };

        if (files.Select(static file => file.RelativePath).SequenceEqual(GeneratedFilePaths) is false)
        {
            throw new InvalidOperationException("generated file order drifted from GeneratedFilePaths");
        }

        return new TokenGenerationResult(files, rows, warnings);
    }

    /// <summary>Compares generated artifacts with what is committed on disk (AC1 reproducibility check).</summary>
    public static bool IsUpToDate(
        TokenGenerationResult result,
        string designSystemDirectory,
        out IReadOnlyList<string> mismatches)
    {
        ArgumentNullException.ThrowIfNull(result);
        ArgumentException.ThrowIfNullOrWhiteSpace(designSystemDirectory);

        var stale = new List<string>();
        foreach (var file in result.Files)
        {
            var path = Path.Combine(designSystemDirectory, file.RelativePath.Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(path))
            {
                stale.Add($"{file.RelativePath}: missing");
                continue;
            }

            var current = File.ReadAllText(path);
            if (!string.Equals(current, file.Content, StringComparison.Ordinal))
            {
                stale.Add($"{file.RelativePath}: content differs");
            }
        }

        mismatches = stale;
        return stale.Count == 0;
    }

    /// <summary>Writes every generated artifact, creating directories as needed.</summary>
    public static void Write(TokenGenerationResult result, string designSystemDirectory)
    {
        ArgumentNullException.ThrowIfNull(result);
        ArgumentException.ThrowIfNullOrWhiteSpace(designSystemDirectory);

        foreach (var file in result.Files)
        {
            var path = Path.Combine(designSystemDirectory, file.RelativePath.Replace('/', Path.DirectorySeparatorChar));
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            File.WriteAllText(path, file.Content, new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
    }

    private static List<TokenEntry> ColorEntries(IReadOnlyList<TokenEntry> entries, string scope) =>
        entries
            .Where(entry => entry.Path.StartsWith(scope, StringComparison.Ordinal))
            .ToList();

    private static void AssertSameKeySet(IReadOnlyList<string> darkKeys, IReadOnlyList<string> lightKeys)
    {
        if (darkKeys.Count != lightKeys.Count)
        {
            throw new InvalidOperationException(
                $"dark has {darkKeys.Count} color tokens but light has {lightKeys.Count}");
        }

        var darkSet = new HashSet<string>(darkKeys, StringComparer.Ordinal);
        foreach (var key in lightKeys)
        {
            if (!darkSet.Contains(key))
            {
                throw new InvalidOperationException($"light palette key '{key}' is missing from the dark palette");
            }
        }
    }

    private static void ValidateKind(TokenEntry entry, TokenValueKind kind)
    {
        if (entry.Type == "dimension")
        {
            var isEmRatio = entry.Path.StartsWith("font.tracking.", StringComparison.Ordinal) ||
                            entry.Value.Trim().EndsWith("em", StringComparison.OrdinalIgnoreCase);
            var expectedKinds = isEmRatio
                ? new[] { TokenValueKind.EmRatio }
                : new[] { TokenValueKind.Double, TokenValueKind.Thickness, TokenValueKind.CornerRadius };
            if (!expectedKinds.Contains(kind))
            {
                throw new InvalidOperationException(
                    $"token '{entry.Path}' ({entry.Value}) cannot be published as {kind}; " +
                    $"em-relative values must be EmRatio and px/unitless values Double/Thickness/CornerRadius");
            }

            return;
        }

        var expected = entry.Type switch
        {
            "color" => new[] { TokenValueKind.Brush },
            "fontFamily" => new[] { TokenValueKind.FontFamily },
            "fontWeight" => new[] { TokenValueKind.FontWeight },
            "duration" => new[] { TokenValueKind.TimeSpan },
            "number" => new[] { TokenValueKind.Double, TokenValueKind.Int32 },
            "string" => new[] { TokenValueKind.String },
            "cubicBezier" => new[] { TokenValueKind.String },
            _ => throw new InvalidOperationException($"token '{entry.Path}' has unsupported $type '{entry.Type}'"),
        };

        if (!expected.Contains(kind))
        {
            throw new InvalidOperationException(
                $"token '{entry.Path}' ($type {entry.Type}) cannot be published as {kind}");
        }
    }

    /// <summary>
    /// Validates the R-14 derivation rules at generation time so the derived HighContrast/Density/
    /// LineHeight tables can never drift from the rules that justify them (contract §2.4).
    /// </summary>
    private static void ValidateDerivationRules(
        IReadOnlyList<TokenEntry> entries,
        IReadOnlyDictionary<string, string> darkBrushes,
        IReadOnlyDictionary<string, string> lightBrushes,
        IReadOnlyList<(string Key, string RawValue)> highContrastDark,
        IReadOnlyList<(string Key, string RawValue)> highContrastLight,
        IReadOnlyList<(string Key, string RawValue)> compactRows,
        IReadOnlyList<(string Key, string RawValue)> spaciousRows)
    {
        ValidateLineHeightAliases(entries);
        ValidateDensityMonotonic(entries, compactRows, spaciousRows);
        ValidateHighContrastContrast(darkBrushes, lightBrushes, highContrastDark, highContrastLight);
    }

    private static void ValidateLineHeightAliases(IReadOnlyList<TokenEntry> entries)
    {
        var allowed = new[] { 1.25, 1.45, 1.6 };
        var aliasKeys = new[]
        {
            "Nm.LineHeight.Display", "Nm.LineHeight.Title", "Nm.LineHeight.Body",
            "Nm.LineHeight.Label", "Nm.LineHeight.Meta", "Nm.LineHeight.Data",
        };

        foreach (var key in aliasKeys)
        {
            var derived = TokenMap.DerivedGlobals.SingleOrDefault(
                token => string.Equals(token.ResourceKey, key, StringComparison.Ordinal));
            if (derived is null)
            {
                throw new InvalidOperationException($"R-14 line-height alias '{key}' is not published");
            }

            var value = TokenValues.ParseNumber(derived.RawValue);
            if (!allowed.Any(candidate => Math.Abs(candidate - value) < 0.0001))
            {
                throw new InvalidOperationException(
                    $"R-14: line-height alias '{key}' must equal one of Tight/Normal/Loose " +
                    $"(1.25/1.45/1.6), but is {value}");
            }
        }

        // The theme layer whitelist covers corners/motion/fonts; assert the alias set did not silently
        // disappear from the token document either.
        foreach (var path in new[] { "font.lineHeight.tight", "font.lineHeight.normal", "font.lineHeight.loose" })
        {
            if (!entries.Any(entry => string.Equals(entry.Path, path, StringComparison.Ordinal)))
            {
                throw new InvalidOperationException($"frozen token '{path}' is missing");
            }
        }
    }

    private static void ValidateDensityMonotonic(
        IReadOnlyList<TokenEntry> entries,
        IReadOnlyList<(string Key, string RawValue)> compactRows,
        IReadOnlyList<(string Key, string RawValue)> spaciousRows)
    {
        var globalKeys = TokenMap.GlobalBindings.ToDictionary(static binding => binding.ResourceKey, StringComparer.Ordinal);
        var globalValues = entries.ToDictionary(static entry => entry.Path, static entry => entry.Value, StringComparer.Ordinal);

        for (var index = 0; index < compactRows.Count; index++)
        {
            var compactKey = compactRows[index].Key;
            var spaciousKey = spaciousRows[index].Key;
            if (!string.Equals(compactKey, spaciousKey, StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"density rows drifted at index {index}");
            }

            var globalBinding = TokenMap.GlobalBindings.FirstOrDefault(
                binding => string.Equals(binding.ResourceKey, compactKey, StringComparison.Ordinal));
            if (globalBinding is null || !globalValues.TryGetValue(globalBinding.TokenPath, out var rawValue))
            {
                continue;
            }

            if (compactKey.Contains("Padding", StringComparison.Ordinal))
            {
                continue; // thickness aggregates are compared by their leading numeric value only
            }

            var reference = TokenValues.ParseDimension(rawValue);
            var compact = TokenValues.ParseDimension(compactRows[index].RawValue);
            var spacious = TokenValues.ParseDimension(spaciousRows[index].RawValue);
            if (!(compact < reference && reference < spacious))
            {
                throw new InvalidOperationException(
                    $"density derivation for '{compactKey}' must satisfy Compact < Comfortable < Spacious " +
                    $"({compact} / {reference} / {spacious})");
            }
        }

        _ = globalKeys;
    }

    private static void ValidateHighContrastContrast(
        IReadOnlyDictionary<string, string> darkBrushes,
        IReadOnlyDictionary<string, string> lightBrushes,
        IReadOnlyList<(string Key, string RawValue)> highContrastDark,
        IReadOnlyList<(string Key, string RawValue)> highContrastLight)
    {
        static void AssertFloors(
            IReadOnlyDictionary<string, string> basePalette,
            IReadOnlyList<(string Key, string RawValue)> highContrast,
            string label)
        {
            var highContrastMap = highContrast.ToDictionary(static row => row.Key, static row => row.RawValue, StringComparer.Ordinal);
            var panel = TokenValues.ParseColor(basePalette["Nm.Color.Bg.Panel"]);
            var canvas = TokenValues.ParseColor(basePalette["Nm.Color.Bg.Canvas"]);

            foreach (var key in new[] { "Text.Primary", "Text.Secondary", "Text.Tertiary" })
            {
                var color = TokenValues.ParseColor(highContrastMap["Nm.Color." + key]);
                foreach (var surface in new[] { panel, canvas })
                {
                    var ratio = ContrastMath.ContrastRatio(color, surface);
                    if (ratio < 7.0)
                    {
                        throw new InvalidOperationException(
                            $"R-14 high contrast ({label}): {key} is {ratio:F2}:1 against a surface (need >= 7:1)");
                    }
                }
            }

            foreach (var status in new[] { "Queued", "Running", "Done", "Failed", "Blocked", "Stale", "Skipped" })
            {
                var color = TokenValues.ParseColor(highContrastMap["Nm.Color.Status." + status]);
                var ratio = ContrastMath.ContrastRatio(color, panel);
                if (ratio < 4.5)
                {
                    throw new InvalidOperationException(
                        $"R-14 high contrast ({label}): status.{status} is {ratio:F2}:1 (need >= 4.5:1)");
                }
            }

            var accent = TokenValues.ParseColor(highContrastMap["Nm.Color.Accent.Base"]);
            var accentOn = TokenValues.ParseColor(highContrastMap["Nm.Color.Accent.On"]);
            if (ContrastMath.ContrastRatio(accentOn, accent) < 4.5)
            {
                throw new InvalidOperationException($"R-14 high contrast ({label}): accent.on on accent.base < 4.5:1");
            }
        }

        AssertFloors(darkBrushes, highContrastDark, "dark");
        AssertFloors(lightBrushes, highContrastLight, "light");
    }

    private static TokenValueKind DensityKind(string key) => key.Contains("Padding", StringComparison.Ordinal)
        ? TokenValueKind.Thickness
        : TokenValueKind.Double;
}
