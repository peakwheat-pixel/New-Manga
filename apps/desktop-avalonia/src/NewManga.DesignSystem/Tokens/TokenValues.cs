using System.Globalization;
using Avalonia;
using Avalonia.Media;

namespace NewManga.DesignSystem.Tokens;

/// <summary>
/// Converts the CSS-ish DTCG token value forms used by the frozen baseline into CLR values that the
/// generated Avalonia resource dictionaries serialize. Supports hex colors (<c>#RGB</c>, <c>#RGBA</c>,
/// <c>#RRGGBB</c>, <c>#RRGGBBAA</c>), <c>rgb()</c>/<c>rgba()</c>, <c>px</c>/<c>em</c> dimensions,
/// <c>ms</c> durations and CSS font stacks.
/// </summary>
public static class TokenValues
{
    /// <summary>Parses a DTCG color token into an opaque-or-alpha <see cref="Color"/>.</summary>
    public static Color ParseColor(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var value = raw.Trim();

        if (value.StartsWith('#'))
        {
            return ParseHexColor(value);
        }

        if (value.StartsWith("rgba(", StringComparison.OrdinalIgnoreCase) ||
            value.StartsWith("rgb(", StringComparison.OrdinalIgnoreCase))
        {
            return ParseRgbFunction(value);
        }

        throw new FormatException($"unsupported color token value '{raw}'");
    }

    /// <summary>Parses a DTCG dimension token (<c>12px</c>, <c>0</c>, <c>0.08em</c>) into a number.</summary>
    public static double ParseDimension(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var value = raw.Trim();

        if (value.EndsWith("px", StringComparison.OrdinalIgnoreCase))
        {
            value = value[..^2];
        }
        else if (value.EndsWith("em", StringComparison.OrdinalIgnoreCase) ||
                 value.EndsWith("rem", StringComparison.OrdinalIgnoreCase))
        {
            // Tracking values are authored in em; Avalonia letter spacing is a per-character delta in
            // device-independent pixels, so the raw em ratio is the token semantic handed to the UI.
            value = value.EndsWith("rem", StringComparison.OrdinalIgnoreCase) ? value[..^3] : value[..^2];
        }
        else if (value.EndsWith("pt", StringComparison.OrdinalIgnoreCase))
        {
            value = value[..^2];
        }

        return double.Parse(value, NumberStyles.Float, CultureInfo.InvariantCulture);
    }

    /// <summary>Parses a bare DTCG number token (line-height multipliers, z-index values).</summary>
    public static double ParseNumber(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        return double.Parse(raw.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture);
    }

    /// <summary>Parses a DTCG duration token (<c>90ms</c>, <c>0.15s</c>) into a <see cref="TimeSpan"/>.</summary>
    public static TimeSpan ParseDuration(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var value = raw.Trim();

        if (value.EndsWith("ms", StringComparison.OrdinalIgnoreCase))
        {
            return TimeSpan.FromMilliseconds(
                double.Parse(value[..^2], NumberStyles.Float, CultureInfo.InvariantCulture));
        }

        if (value.EndsWith('s'))
        {
            return TimeSpan.FromSeconds(
                double.Parse(value[..^1], NumberStyles.Float, CultureInfo.InvariantCulture));
        }

        throw new FormatException($"unsupported duration token value '{raw}'");
    }

    /// <summary>
    /// Parses a DTCG font weight token (<c>400</c>, <c>Semibold</c>) into an Avalonia
    /// <see cref="FontWeight"/>.
    /// </summary>
    public static FontWeight ParseFontWeight(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var value = raw.Trim();

        if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var numeric))
        {
            return numeric switch
            {
                100 => FontWeight.Thin,
                200 => FontWeight.ExtraLight,
                300 => FontWeight.Light,
                400 => FontWeight.Normal,
                500 => FontWeight.Medium,
                600 => FontWeight.SemiBold,
                700 => FontWeight.Bold,
                800 => FontWeight.ExtraBold,
                900 => FontWeight.Black,
                _ => throw new FormatException($"unsupported numeric font weight '{raw}'"),
            };
        }

        return value.ToLowerInvariant() switch
        {
            "thin" => FontWeight.Thin,
            "extralight" or "extra-light" => FontWeight.ExtraLight,
            "light" => FontWeight.Light,
            "normal" or "regular" => FontWeight.Normal,
            "medium" => FontWeight.Medium,
            "semibold" or "semi-bold" => FontWeight.SemiBold,
            "bold" => FontWeight.Bold,
            "extrabold" or "extra-bold" => FontWeight.ExtraBold,
            "black" => FontWeight.Black,
            _ => throw new FormatException($"unsupported font weight token value '{raw}'"),
        };
    }

    /// <summary>
    /// Normalizes a CSS font stack into the comma-separated form Avalonia's <see cref="FontFamily"/>
    /// parses: quotes are stripped and CSS generic families (which Avalonia does not resolve) are
    /// dropped so the platform default is used for the tail of the stack.
    /// </summary>
    public static string ParseFontFamily(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);

        var families = new List<string>(4);
        foreach (var part in raw.Split(','))
        {
            var family = part.Trim().Trim('"', '\'').Trim();
            if (family.Length == 0 || IsCssGenericFamily(family))
            {
                continue;
            }

            families.Add(family);
        }

        if (families.Count == 0)
        {
            throw new FormatException($"font family token '{raw}' only contains CSS generic families");
        }

        return string.Join(", ", families);
    }

    /// <summary>Parses a DTCG thickness token: <c>8,12</c>, <c>8</c> or <c>8,12,8,12</c>.</summary>
    public static Thickness ParseThickness(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var parts = raw.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
        var values = parts.Select(ParseDimension).ToArray();

        return values.Length switch
        {
            1 => new Thickness(values[0]),
            2 => new Thickness(values[0], values[1]),
            4 => new Thickness(values[0], values[1], values[2], values[3]),
            _ => throw new FormatException($"unsupported thickness token value '{raw}'"),
        };
    }

    /// <summary>Parses a DTCG corner radius token into Avalonia's <see cref="CornerRadius"/>.</summary>
    public static CornerRadius ParseCornerRadius(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var parts = raw.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
        var values = parts.Select(ParseDimension).ToArray();

        return values.Length switch
        {
            1 => new CornerRadius(values[0]),
            2 => new CornerRadius(values[0], values[1]),
            _ => throw new FormatException($"unsupported corner radius token value '{raw}'"),
        };
    }

    /// <summary>Round-trips a color to the deterministic <c>#AARRGGBB</c> form used in generated XAML.</summary>
    public static string ToHex(Color color) =>
        $"#{color.A:X2}{color.R:X2}{color.G:X2}{color.B:X2}";

    /// <summary>
    /// Converts a CSS <c>cubic-bezier(...)</c> token into the four control-point numbers. Kept as data
    /// because the Theme Engine must be able to export the original CSS form again.
    /// </summary>
    public static (double X1, double Y1, double X2, double Y2) ParseCubicBezier(string raw)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(raw);
        var open = raw.IndexOf('(');
        var close = raw.LastIndexOf(')');
        if (open < 0 || close <= open)
        {
            throw new FormatException($"unsupported easing token value '{raw}'");
        }

        var numbers = raw[(open + 1)..close]
            .Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries)
            .Select(value => double.Parse(value, NumberStyles.Float, CultureInfo.InvariantCulture))
            .ToArray();

        if (numbers.Length != 4)
        {
            throw new FormatException($"cubic-bezier needs 4 control points, got {numbers.Length} in '{raw}'");
        }

        return (numbers[0], numbers[1], numbers[2], numbers[3]);
    }

    /// <summary>Formats a double deterministically (invariant, shortest round-trip representation).</summary>
    public static string FormatDouble(double value) => value.ToString(CultureInfo.InvariantCulture);

    /// <summary>Formats a duration deterministically as an invariant TimeSpan string for XAML.</summary>
    public static string FormatTimeSpan(TimeSpan value) => value.ToString("c", CultureInfo.InvariantCulture);

    private static Color ParseHexColor(string hex)
    {
        var digits = hex[1..];
        if (digits.Length is not (3 or 4 or 6 or 8) || !digits.All(Uri.IsHexDigit))
        {
            throw new FormatException($"unsupported hex color token value '{hex}'");
        }

        if (digits.Length <= 4)
        {
            // Expand shorthand: #RGB -> #RRGGBB, #RGBA -> #RRGGBBAA (CSS Color 4 semantics).
            digits = string.Concat(digits.Select(c => new string(c, 2)));
        }

        static byte Channel(string digits, int offset) =>
            byte.Parse(digits.AsSpan(offset, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);

        // tokens.json is authored in CSS color syntax: 6-digit = #RRGGBB (opaque), 8-digit = #RRGGBBAA.
        // Avalonia's own 8-digit literal form is #AARRGGBB, which is why ToHex() converts explicitly.
        var r = Channel(digits, 0);
        var g = Channel(digits, 2);
        var b = Channel(digits, 4);
        var a = digits.Length == 8 ? Channel(digits, 6) : (byte)255;
        return Color.FromArgb(a, r, g, b);
    }

    private static Color ParseRgbFunction(string raw)
    {
        var open = raw.IndexOf('(');
        var close = raw.LastIndexOf(')');
        if (open < 0 || close <= open)
        {
            throw new FormatException($"unsupported color token value '{raw}'");
        }

        var parts = raw[(open + 1)..close]
            .Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length is not (3 or 4))
        {
            throw new FormatException($"rgb()/rgba() needs 3 or 4 components in '{raw}'");
        }

        static byte Channel(string part) =>
            (byte)Math.Clamp(
                (int)Math.Round(
                    double.Parse(part, NumberStyles.Float, CultureInfo.InvariantCulture),
                    MidpointRounding.AwayFromZero),
                0,
                255);

        var r = Channel(parts[0]);
        var g = Channel(parts[1]);
        var b = Channel(parts[2]);
        var alpha = parts.Length == 4
            ? (byte)Math.Clamp(
                (int)Math.Round(
                    double.Parse(parts[3], NumberStyles.Float, CultureInfo.InvariantCulture) * 255,
                    MidpointRounding.AwayFromZero),
                0,
                255)
            : (byte)255;

        return Color.FromArgb(alpha, r, g, b);
    }

    private static bool IsCssGenericFamily(string family) =>
        family.ToLowerInvariant() is
            "system-ui" or "sans-serif" or "serif" or "monospace" or "cursive" or "fantasy" or
            "ui-sans-serif" or "ui-serif" or "ui-monospace" or "ui-rounded" or "emoji" or
            "math" or "fangsong";
}
