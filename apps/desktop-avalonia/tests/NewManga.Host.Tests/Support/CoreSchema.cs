namespace NewManga.Host.Tests.Support;

/// <summary>
/// SCHEMA-VERSION-ASSERT-1: the database schema version the product code currently ships.
///
/// Why a constant instead of a magic number in each assertion: three IPC tests hard-coded
/// <c>Assert.Equal(9, schema_version)</c> and went red for the wrong reason once the product's migration
/// chain reached v14 (<c>src/infrastructure/sqlite/schema.py</c> registers v1..v14 via
/// <c>default_migrations()</c>). An adjudication by Codex (2026-11-15) ruled that updating such an
/// expectation is NOT "relaxing an assertion" -- it is correcting an expectation that went stale as the
/// product evolved -- provided the new assertion is still an EXACT equality and the expected value does
/// not come from the very artifact under test.
///
/// <para>
/// This value is therefore a deliberate mirror of the Python Core's migration chain, and it must be
/// bumped together with it. <see cref="PythonSchemaMigrationGuardTests"/> guards the mirror by asking
/// Python itself how many migrations it registers, so a v15 added on one side fails loudly on the other.
/// </para>
/// </summary>
internal static class CoreSchema
{
    /// <summary>Number of migrations the frozen Core applies on a fresh library (v1..v14).</summary>
    public const int Current = 14;
}
