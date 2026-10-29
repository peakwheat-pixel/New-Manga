using Avalonia.Input;

namespace NewManga.App.Shell.V2;

/// <summary>
/// One keyboard gesture as registered in <see cref="KeyMap"/>. Modifier comparison is normalised so
/// CapsLock/NumLock style bits never create a false mismatch.
/// </summary>
public sealed record ShellKeyGesture(Key Key, KeyModifiers Modifiers = KeyModifiers.None)
{
    private const KeyModifiers MaskedModifiers =
        KeyModifiers.Control | KeyModifiers.Shift | KeyModifiers.Alt | KeyModifiers.Meta;

    public string Display => ShortcutText.Format(Key, Modifiers);

    public bool Matches(Key key, KeyModifiers modifiers) =>
        Key == key && (modifiers & MaskedModifiers) == (Modifiers & MaskedModifiers);
}

public sealed record KeyMapConflict(
    ShellKeyGesture Gesture,
    ShellCommandDefinition First,
    ShellCommandDefinition Second)
{
    public string Describe() =>
        $"按键冲突 {Gesture.Display}: 「{First.Id}」与「{Second.Id}」的作用域重叠";
}

/// <summary>
/// A command the shell can execute. <see cref="ScopeLabel"/> is the palette annotation
/// 「空间 · 模式 · 作用域」 required by the frozen contract §6.3 / DESIGN_SYSTEM §6.2.
/// </summary>
public sealed record ShellCommandDefinition(
    string Id,
    string Title,
    string ScopeLabel,
    SpaceId? Space,
    StudioMode? Mode,
    IReadOnlyList<ShellKeyGesture> Gestures,
    bool IsAvailable = true,
    string? UnavailableReason = null)
{
    public bool AppliesTo(SpaceId space, StudioMode mode) =>
        (Space is null || Space == space) && (!(Mode is not null && Space == SpaceId.Studio) || Mode == mode);

    public string GestureText => Gestures.Count == 0
        ? "—"
        : string.Join(" / ", Gestures.Select(gesture => gesture.Display));

    public bool HasGesture => Gestures.Count > 0;
}

/// <summary>
/// V11R-B-1: the single keyboard registry required by contract §6.3. Every global shortcut of the
/// new shell is declared exactly once here; conflicting registrations fail the shell's startup
/// assertion (and the dedicated unit test).
/// </summary>
public sealed class KeyMap
{
    private static readonly Lazy<KeyMap> DefaultMap = new(CreateDefault);

    private readonly List<(ShellCommandDefinition Command, ShellKeyGesture Gesture)> _gestures = new();

    public KeyMap(IEnumerable<ShellCommandDefinition> definitions)
    {
        Definitions = definitions.ToList();
        foreach (var command in Definitions)
        {
            foreach (var gesture in command.Gestures)
            {
                _gestures.Add((command, gesture));
            }
        }

        Conflicts = FindConflicts(Definitions);
    }

    public static KeyMap Default => DefaultMap.Value;

    public IReadOnlyList<ShellCommandDefinition> Definitions { get; }

    public IReadOnlyList<KeyMapConflict> Conflicts { get; }

    public bool IsValid => Conflicts.Count == 0;

    /// <summary>Startup assertion: a conflicting registry must never reach a running shell.</summary>
    public static void EnsureValid(KeyMap? map = null)
    {
        var mapped = map ?? Default;
        if (mapped.Conflicts.Count == 0)
        {
            return;
        }

        throw new InvalidOperationException(
            "KeyMap 注册冲突：" + string.Join("；", mapped.Conflicts.Select(conflict => conflict.Describe())));
    }

    public static IReadOnlyList<KeyMapConflict> FindConflicts(IEnumerable<ShellCommandDefinition> definitions)
    {
        var registered = new List<(ShellCommandDefinition Command, ShellKeyGesture Gesture)>();
        foreach (var definition in definitions)
        {
            foreach (var gesture in definition.Gestures)
            {
                registered.Add((definition, gesture));
            }
        }

        var conflicts = new List<KeyMapConflict>();
        for (var i = 0; i < registered.Count; i++)
        {
            for (var j = i + 1; j < registered.Count; j++)
            {
                var (firstCommand, firstGesture) = registered[i];
                var (secondCommand, secondGesture) = registered[j];
                if (!GesturesEqual(firstGesture, secondGesture))
                {
                    continue;
                }

                if (ScopesOverlap(firstCommand, secondCommand))
                {
                    conflicts.Add(new KeyMapConflict(firstGesture, firstCommand, secondCommand));
                }
            }
        }

        return conflicts;
    }

    public bool TryMatch(
        Key key,
        KeyModifiers modifiers,
        SpaceId space,
        StudioMode mode,
        out ShellCommandDefinition command)
    {
        foreach (var (candidate, gesture) in _gestures)
        {
            if (candidate.AppliesTo(space, mode) && gesture.Matches(key, modifiers))
            {
                command = candidate;
                return true;
            }
        }

        command = null!;
        return false;
    }

    public IReadOnlyList<ShellCommandDefinition> ForScope(SpaceId space, StudioMode mode) =>
        Definitions.Where(definition => definition.AppliesTo(space, mode)).ToList();

    public ShellCommandDefinition? Find(string id) =>
        Definitions.FirstOrDefault(definition => string.Equals(definition.Id, id, StringComparison.Ordinal));

    private static bool ScopesOverlap(ShellCommandDefinition first, ShellCommandDefinition second)
    {
        var spaceOverlap = first.Space is null || second.Space is null || first.Space == second.Space;
        var modeOverlap = first.Mode is null || second.Mode is null || first.Mode == second.Mode;
        return spaceOverlap && modeOverlap;
    }

    private static bool GesturesEqual(ShellKeyGesture first, ShellKeyGesture second) =>
        first.Key == second.Key &&
        (first.Modifiers & (KeyModifiers.Control | KeyModifiers.Shift | KeyModifiers.Alt | KeyModifiers.Meta)) ==
        (second.Modifiers & (KeyModifiers.Control | KeyModifiers.Shift | KeyModifiers.Alt | KeyModifiers.Meta));

    private static KeyMap CreateDefault()
    {
        var map = new KeyMap(ShellCommands.Definitions);
        if (!map.IsValid)
        {
            throw new InvalidOperationException(
                "KeyMap 默认注册表冲突：" +
                string.Join("；", map.Conflicts.Select(conflict => conflict.Describe())));
        }

        return map;
    }
}

/// <summary>Display formatting for gestures (single source used by palette rows and the F1 sheet).</summary>
public static class ShortcutText
{
    public static string Format(Key key, KeyModifiers modifiers)
    {
        var parts = new List<string>();
        if (modifiers.HasFlag(KeyModifiers.Control))
        {
            parts.Add("Ctrl");
        }

        if (modifiers.HasFlag(KeyModifiers.Shift))
        {
            parts.Add("Shift");
        }

        if (modifiers.HasFlag(KeyModifiers.Alt))
        {
            parts.Add("Alt");
        }

        if (modifiers.HasFlag(KeyModifiers.Meta))
        {
            parts.Add("Win");
        }

        parts.Add(KeyName(key));
        return string.Join("+", parts);
    }

    public static string KeyName(Key key) => key switch
    {
        Key.Tab => "Tab",
        Key.Escape => "Esc",
        Key.Enter => "Enter",
        Key.Space => "Space",
        Key.OemOpenBrackets => "[",
        Key.OemCloseBrackets => "]",
        Key.OemComma => ",",
        Key.OemPeriod => ".",
        Key.OemQuestion => "/",
        Key.OemMinus => "-",
        Key.OemPlus => "=",
        Key.OemPipe => "\\",
        Key.Up => "↑",
        Key.Down => "↓",
        Key.Left => "←",
        Key.Right => "→",
        Key.PageUp => "PgUp",
        Key.PageDown => "PgDn",
        >= Key.F1 and <= Key.F12 => key.ToString(),
        >= Key.A and <= Key.Z => key.ToString(),
        >= Key.D0 and <= Key.D9 => key.ToString()[1..],
        _ => key.ToString(),
    };
}
