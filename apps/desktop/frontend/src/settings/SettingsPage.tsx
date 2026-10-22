import { useRef, useState } from "react";
import { CacheRevisionPanel } from "./CacheRevisionPanel";
import { SettingsClient } from "./client";
import { CapabilityBindingPanel } from "./CapabilityBindingPanel";
import { DisabledSection } from "./DisabledSection";
import { InpaintSettingsPanel } from "./InpaintSettingsPanel";
import { ModelGpuSettingsPanel } from "./ModelGpuSettingsPanel";
import { NetworkProfilePanel } from "./NetworkProfilePanel";
import { OcrSettingsPanel } from "./OcrSettingsPanel";
import { ProviderProfilePanel } from "./ProviderProfilePanel";
import { RecycleBinSettingsPanel } from "./RecycleBinSettingsPanel";
import { SfxPolicyControl } from "./SfxPolicyControl";
import { TasksSettingsPanel } from "./TasksSettingsPanel";
import { TranslationParamsPanel } from "./TranslationParamsPanel";
import { TypesetSettingsPanel } from "./TypesetSettingsPanel";
import { tokens } from "../theme/tokens";

/**
 * P15 Settings page (AD-001 §5). Layout is frozen by §5.2: the AppShell's
 * 64px Nav Rail is outside this component; here it is the fixed 200px
 * SettingsCategoryNav plus the SettingsContentPanel. The twelve categories
 * are in a FIXED order and switching is React local state — there is no
 * sub-route.
 *
 * Editability: Provider (profiles + capability bindings), Network/Proxy,
 * SFX policy, the four SETTINGS-OPEN-A-1 batch A sections (design
 * doc/design/SETTINGS_SECTION_SCHEMAS.md §3), the SETTINGS-OPEN-B-1
 * model/GPU (§4.1) and tasks/concurrency (§4.2) sections, batch B-2's
 * cache/Revision cleanup operation surface (§4.3), and — batch C-1 — the
 * recycle-bin view/clear operation surface (design
 * doc/design/SETTINGS_SECTION_C_SCHEMAS.md §2). Only the two remaining batch C
 * partitions (backup/restore, plugins) still render the disabled placeholder
 * with the reason "等待 section schema 冻结"; the nav badge "未开放" only
 * applies to those still-closed categories.
 */
export const SETTINGS_CATEGORY_ORDER = [
  "provider",
  "network",
  "ocr",
  "translation",
  "inpaint",
  "typeset",
  "model_gpu",
  "task_concurrency",
  "cache_revision",
  "recycle_bin",
  "backup_restore",
  "plugins",
] as const;

export type SettingsCategoryId = (typeof SETTINGS_CATEGORY_ORDER)[number];

const SETTINGS_CATEGORIES: ReadonlyArray<{
  id: SettingsCategoryId;
  label: string;
  open: boolean;
}> = [
  { id: "provider", label: "Provider", open: true },
  { id: "network", label: "网络/代理", open: true },
  { id: "ocr", label: "OCR", open: true },
  { id: "translation", label: "翻译", open: true },
  { id: "inpaint", label: "图片修复", open: true },
  { id: "typeset", label: "排版样式", open: true },
  { id: "model_gpu", label: "模型/GPU", open: true },
  { id: "task_concurrency", label: "任务/并发", open: true },
  { id: "cache_revision", label: "缓存/Revision", open: true },
  { id: "recycle_bin", label: "回收站", open: true },
  { id: "backup_restore", label: "备份/恢复", open: false },
  { id: "plugins", label: "Plugin/Hooks", open: false },
];

/** Every still-disabled partition with its placeholder test id — asserted
 * one by one in the AC2 tests. Batch A's ocr / translation-context / inpaint /
 * typeset placeholders, batch B-1's model-GPU / task-concurrency placeholders
 * and batch B-2's cache/Revision placeholder are gone: those categories now
 * host real panels. Batch C-1 opens the recycle bin (view/clear). Only the
 * two remaining batch C partitions (backup/restore, plugins) stay closed. */
export const DISABLED_SECTION_TEST_IDS = {
  backupRestore: "settings-disabled-section-backup-restore",
  plugins: "settings-disabled-section-plugins",
} as const;

export interface SettingsPageProps {
  client?: SettingsClient;
}

export function SettingsPage({ client }: SettingsPageProps) {
  const [activeCategoryId, setActiveCategoryId] = useState<SettingsCategoryId>("provider");
  const navRef = useRef<HTMLElement | null>(null);
  const activeClient = client ?? new SettingsClient();

  const openCategories = SETTINGS_CATEGORIES.filter((category) => category.open);
  const activeIndex = openCategories.findIndex((category) => category.id === activeCategoryId);

  const moveSelection = (delta: number) => {
    const nextIndex = Math.min(openCategories.length - 1, Math.max(0, activeIndex + delta));
    const nextId = openCategories[nextIndex].id;
    setActiveCategoryId(nextId);
    const button = navRef.current?.querySelector<HTMLButtonElement>(`[data-testid="settings-category-${nextId}"]`);
    button?.focus();
  };

  const activeCategory = SETTINGS_CATEGORIES.find((c) => c.id === activeCategoryId);

  return (
    <div
      data-testid="settings-page"
      style={{
        display: "flex",
        width: "100%",
        height: "100%",
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.app,
        overflow: "hidden",
      }}
    >
      {/* Fixed 200px category navigation (§5.2) */}
      <nav
        ref={navRef}
        data-testid="settings-category-nav"
        aria-label="设置分类"
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") {
            e.preventDefault();
            moveSelection(1);
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            moveSelection(-1);
          }
        }}
        style={{
          width: 200,
          height: "100%",
          boxSizing: "border-box",
          flexShrink: 0,
          backgroundColor: tokens.color.bg.rail,
          borderRight: `1px solid ${tokens.color.border.default}`,
          padding: tokens.spacing.sm,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          overflowY: "auto",
        }}
      >
        <div
          style={{
            padding: `${tokens.spacing.sm}px ${tokens.spacing.xs}px`,
            fontSize: tokens.typography.size.secondary,
            fontWeight: 600,
            color: tokens.color.text.secondary,
            textTransform: "uppercase",
            letterSpacing: 0.5,
          }}
        >
          系统设置
        </div>

        {SETTINGS_CATEGORIES.map((cat) => {
          const isActive = activeCategoryId === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              data-testid={`settings-category-${cat.id}`}
              data-active={isActive}
              data-open={cat.open}
              disabled={!cat.open}
              aria-disabled={!cat.open}
              aria-label={cat.open ? undefined : `${cat.label}，未开放：等待 section schema 冻结`}
              title={cat.open ? undefined : "等待 section schema 冻结"}
              onClick={() => {
                if (cat.open) setActiveCategoryId(cat.id);
              }}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: tokens.spacing.xs,
                padding: "8px 10px",
                fontSize: tokens.typography.size.base,
                borderRadius: tokens.radius.button,
                border: "none",
                backgroundColor: isActive ? tokens.color.accent.selected : "transparent",
                color: isActive ? tokens.color.accent.primary : cat.open ? tokens.color.text.primary : tokens.color.text.muted,
                cursor: cat.open ? "pointer" : "not-allowed",
                fontWeight: isActive ? 600 : 400,
                textAlign: "left",
                transition: "background-color 0.1s ease",
              }}
            >
              <span>{cat.label}</span>
              {!cat.open && (
                <span
                  title="等待 section schema 冻结"
                  style={{
                    fontSize: tokens.typography.size.badge,
                    color: tokens.color.state.skipped,
                    opacity: 0.7,
                  }}
                >
                  未开放
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Content panel — category switching is local state, no sub-route */}
      <main
        data-testid="settings-content-panel"
        style={{
          flex: 1,
          height: "100%",
          overflowY: "auto",
          padding: tokens.spacing.lg,
          boxSizing: "border-box",
        }}
      >
        {activeCategoryId === "provider" && (
          <div data-testid="settings-content-provider" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg }}>
            <ProviderProfilePanel client={activeClient} />
            <CapabilityBindingPanel client={activeClient} />
          </div>
        )}

        {activeCategoryId === "network" && (
          <div data-testid="settings-content-network">
            <NetworkProfilePanel client={activeClient} />
          </div>
        )}

        {activeCategoryId === "translation" && (
          <div data-testid="settings-content-translation" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg }}>
            <SfxPolicyControl client={activeClient} />
            <TranslationParamsPanel client={activeClient} />
          </div>
        )}

        {activeCategoryId === "ocr" && (
          <div data-testid="settings-content-ocr">
            <OcrSettingsPanel client={activeClient} />
          </div>
        )}

        {activeCategoryId === "inpaint" && (
          <div data-testid="settings-content-inpaint">
            <InpaintSettingsPanel client={activeClient} />
          </div>
        )}

        {activeCategoryId === "typeset" && (
          <div data-testid="settings-content-typeset" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg }}>
            <TypesetSettingsPanel client={activeClient} />
            {/* §3.4: reading direction is a Book/Chapter property — the
             * settings page shows guidance only, never a fake global control
             * (no DisabledSection placeholder: this partition is not the
             * batch A surface and must not claim to be "waiting schema"). */}
            <section
              data-testid="settings-reading-direction-note"
              style={{
                padding: tokens.spacing.md,
                backgroundColor: tokens.color.surface.card,
                border: `1px solid ${tokens.color.border.default}`,
                borderRadius: tokens.radius.card,
                maxWidth: 780,
                color: tokens.color.text.secondary,
                fontSize: tokens.typography.size.secondary,
                lineHeight: tokens.typography.lineHeight,
              }}
            >
              阅读方向（rtl / ltr / vertical）是书籍 / 章节属性：请在书架或章节属性中修改；
              设置页不提供全局默认方向。若需要“新建章节默认方向”，另立契约后再开放。
            </section>
          </div>
        )}
        {activeCategoryId === "model_gpu" && (
          <div data-testid="settings-content-model-gpu">
            <ModelGpuSettingsPanel client={activeClient} />
          </div>
        )}
        {activeCategoryId === "task_concurrency" && (
          <div data-testid="settings-content-task-concurrency">
            <TasksSettingsPanel client={activeClient} />
          </div>
        )}
        {activeCategoryId === "cache_revision" && (
          <div data-testid="settings-content-cache-revision">
            <CacheRevisionPanel client={activeClient} />
          </div>
        )}
        {activeCategoryId === "recycle_bin" && (
          <div data-testid="settings-content-recycle-bin">
            <RecycleBinSettingsPanel />
          </div>
        )}
        {activeCategoryId === "backup_restore" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.backupRestore} title="备份 / 恢复" />}
        {activeCategoryId === "plugins" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.plugins} title="Plugin / Hooks" />}

        <div data-testid="settings-active-category" data-category-id={activeCategoryId} style={{ display: "none" }}>
          {activeCategory?.label}
        </div>
      </main>
    </div>
  );
}
