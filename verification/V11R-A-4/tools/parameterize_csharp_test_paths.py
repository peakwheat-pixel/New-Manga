"""V11R-A-4: replace hardcoded machine checkout paths in .NET tests with TestWorkspacePaths.

The helper resolves NEWMANGA_WORKSPACE_ROOT first, then a workspace sibling of the repository root
(the same rule the PowerShell scripts use), so a clean clone never needs this machine's G:/ path.
"""

from __future__ import annotations

import re
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[3]
TESTS = WORKTREE / "apps" / "desktop-avalonia" / "tests"

HELPER = """using System;
using System.IO;

namespace {namespace};

/// <summary>
/// V11R-A-4: resolves workspace/task-env fixture paths without a hardcoded maintainer checkout.
/// Order: NEWMANGA_WORKSPACE_ROOT, then the workspace sibling of the repository root
/// (&lt;repo&gt;/../&lt;repo-name&gt;.workspace), then a clearly missing temp path (tests self-skip).
/// </summary>
internal static class TestWorkspacePaths
{{
    private static readonly Lazy<string> Root = new(Resolve);

    public static string Workspace => Root.Value;

    public static string Path(string relative) =>
        System.IO.Path.Combine(Workspace, relative.Replace('/', System.IO.Path.DirectorySeparatorChar));

    private static string Resolve()
    {{
        var configured = Environment.GetEnvironmentVariable("NEWMANGA_WORKSPACE_ROOT");
        if (!string.IsNullOrWhiteSpace(configured))
        {{
            return configured;
        }}

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {{
            if (File.Exists(System.IO.Path.Combine(directory.FullName, "AGENTS.md")) &&
                Directory.Exists(System.IO.Path.Combine(directory.FullName, "apps", "desktop-avalonia")))
            {{
                return System.IO.Path.Combine(directory.Parent!.FullName, directory.Name + ".workspace");
            }}

            directory = directory.Parent;
        }}

        return System.IO.Path.Combine(System.IO.Path.GetTempPath(), "newmanga-workspace-missing");
    }}
}}
"""

PROJECTS = {
    "NewManga.App.Tests": "NewManga.App.Tests",
    "NewManga.CoreClient.Tests": "NewManga.CoreClient.Tests",
    "NewManga.Host.Tests": "NewManga.Host.Tests",
}

LITERAL = re.compile(
    r'@"G:[\\/]CODEX[\\/]New Manga\.workspace[\\/](?P<rel>[^"]+)"'
)
CONST_LITERAL = re.compile(
    r"private const string (?P<name>\w+) = @" r'"G:[\\/]CODEX[\\/]New Manga\.workspace[\\/](?P<rel>[^"]+)"' r";"
)


def main() -> int:
    for project, namespace in PROJECTS.items():
        helper_path = TESTS / project / "TestWorkspacePaths.cs"
        helper_path.write_text(HELPER.format(namespace=namespace), encoding="utf-8")
        print(f"wrote {helper_path.relative_to(WORKTREE).as_posix()}")

    total = 0
    for path in sorted(TESTS.rglob("*.cs")):
        if path.name == "TestWorkspacePaths.cs":
            continue
        original = path.read_text(encoding="utf-8")
        if "G:/CODEX" not in original and "G:\\CODEX" not in original:
            continue

        def const_repl(match: re.Match) -> str:
            rel = match.group("rel").replace("\\", "/")
            return (
                f"private static string {match.group('name')} => "
                f'TestWorkspacePaths.Path("{rel}");'
            )

        updated = CONST_LITERAL.sub(const_repl, original)

        def literal_repl(match: re.Match) -> str:
            rel = match.group("rel").replace("\\", "/")
            return f'TestWorkspacePaths.Path("{rel}")'

        updated = LITERAL.sub(literal_repl, updated)
        if updated == original:
            continue
        count = len(LITERAL.findall(original)) + len(CONST_LITERAL.findall(original))
        total += count
        path.write_text(updated, encoding="utf-8")
        print(f"{path.relative_to(WORKTREE).as_posix()}: {count} replacement(s)")
    print(f"total replacements: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
