import { useRef, useState } from "react";
import { SettingsClient } from "./client";
import { CapabilityBindingPanel } from "./CapabilityBindingPanel";
import { DisabledSection } from "./DisabledSection";
import { NetworkProfilePanel } from "./NetworkProfilePanel";
import { ProviderProfilePanel } from "./ProviderProfilePanel";
import { SfxPolicyControl } from "./SfxPolicyControl";
import { tokens } from "../theme/tokens";

/**
 * P15 Settings page (AD-001 §5). Layout is frozen by §5.2: the AppShell's
 * 64px Nav Rail is outside this component; here it is the fixed 200px
 * SettingsCategoryNav plus the SettingsContentPanel. The twelve categories
 * are in a FIXED order and switching is React local state — there is no
 * sub-route.
 *
 * Editability follows P15-C1 §7 (G25) exactly: Provider (profiles +
 * capability bindings), Network/Proxy, and the sfx.policy section are the
 * only open surfaces; every other partition renders the disabled
 * placeholder with the reason "等待 section schema 冻结".
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
  { id: "ocr", label: "OCR", open: false },
  { id: "translation", label: "翻译", open: true },
  { id: "inpaint", label: "图片修复", open: false },
  { id: "typeset", label: "排版样式", open: false },
  { id: "model_gpu", label: "模型/GPU", open: false },
  { id: "task_concurrency", label: "任务/并发", open: false },
  { id: "cache_revision", label: "缓存/Revision", open: false },
  { id: "recycle_bin", label: "回收站", open: false },
  { id: "backup_restore", label: "备份/恢复", open: false },
  { id: "plugins", label: "Plugin/Hooks", open: false },
];

/** Every disabled partition (P15-C1 §7 lower table) with its placeholder
 * test id — asserted one by one in the AC2 tests. */
export const DISABLED_SECTION_TEST_IDS = {
  ocr: "settings-disabled-section-ocr",
  translationContext: "settings-disabled-section-translation-context",
  inpaint: "settings-disabled-section-inpaint",
  typeset: "settings-disabled-section-typeset",
  readingDirection: "settings-disabled-section-reading-direction",
  modelGpu: "settings-disabled-section-model-gpu",
  taskConcurrency: "settings-disabled-section-task-concurrency",
  cacheRevision: "settings-disabled-section-cache-revision",
  recycleBin: "settings-disabled-section-recycle-bin",
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

  const activeIndex = SETTINGS_CATEGORY_ORDER.indexOf(activeCategoryId);

  const moveSelection = (delta: number) => {
    const nextIndex = Math.min(SETTINGS_CATEGORY_ORDER.length - 1, Math.max(0, activeIndex + delta));
    const nextId = SETTINGS_CATEGORY_ORDER[nextIndex];
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
              onClick={() => setActiveCategoryId(cat.id)}
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
                cursor: "pointer",
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
            <DisabledSection testId={DISABLED_SECTION_TEST_IDS.translationContext} title="翻译参数 / 上下文策略" />
          </div>
        )}

        {activeCategoryId === "ocr" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.ocr} title="OCR 参数" />}
        {activeCategoryId === "inpaint" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.inpaint} title="图片修复" />}
        {activeCategoryId === "typeset" && (
          <div data-testid="settings-content-typeset" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg }}>
            <DisabledSection testId={DISABLED_SECTION_TEST_IDS.typeset} title="排版 / Text Style" />
            <DisabledSection
              testId={DISABLED_SECTION_TEST_IDS.readingDirection}
              title="阅读方向"
              reason="等待 section schema 冻结（G24 仅提供只读解析，无写 wire）"
            />
          </div>
        )}
        {activeCategoryId === "model_gpu" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.modelGpu} title="模型 / GPU" />}
        {activeCategoryId === "task_concurrency" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.taskConcurrency} title="任务 / 并发" />}
        {activeCategoryId === "cache_revision" && <DisabledSection testId={DISABLED_SECTION_TEST_IDS.cacheRevision} title="缓存 / Revision" />}
        {activeCategoryId === "recycle_bin" && (
          <DisabledSection
            testId={DISABLED_SECTION_TEST_IDS.recycleBin}
            title="回收站"
            reason="等待 section schema 冻结（G2 回收站 wire 明确未授权）"
          />
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
