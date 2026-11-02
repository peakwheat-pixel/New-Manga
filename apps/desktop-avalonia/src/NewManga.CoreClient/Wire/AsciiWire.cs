using System.Globalization;
using System.Text;

namespace NewManga.CoreClient.Wire;

/// <summary>
/// The cp936 wire contract: the frozen PyInstaller sidecars decode stdin with the ANSI code page,
/// so every non-ASCII character must cross the pipe as a <c>\uXXXX</c> escape. Escaping at the host
/// is lossless for the Core (Python's json.loads restores the character) and needs no sidecar
/// rebuild. See the S0 spike report §2.6 and <c>apps/desktop/src-tauri/src/library_bridge.rs</c>.
/// </summary>
public static class AsciiWire
{
    public static string Escape(string text)
    {
        var needsEscape = false;
        foreach (var ch in text)
        {
            if (ch >= 0x80)
            {
                needsEscape = true;
                break;
            }
        }

        if (!needsEscape)
        {
            return text;
        }

        var builder = new StringBuilder(text.Length + 16);
        foreach (var ch in text)
        {
            if (ch < 0x80)
            {
                builder.Append(ch);
            }
            else
            {
                builder.Append("\\u").Append(((int)ch).ToString("x4", CultureInfo.InvariantCulture));
            }
        }

        return builder.ToString();
    }

    public static bool IsAscii(string text)
    {
        foreach (var ch in text)
        {
            if (ch >= 0x80)
            {
                return false;
            }
        }

        return true;
    }

    public static byte[] ToBytes(string line) => Encoding.UTF8.GetBytes(line);

    public static string Hex(ReadOnlySpan<byte> bytes) => Convert.ToHexString(bytes).ToLowerInvariant();
}
