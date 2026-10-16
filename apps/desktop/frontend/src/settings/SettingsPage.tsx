import { useState } from "react";
import { SettingsPanel } from "./SettingsPanel";
import { SettingsClient } from "./client";
import { tokens } from "../theme/tokens";

export interface SettingsPageProps {
  client?: SettingsClient;
}

const SETTINGS_CATEGORIES = [
  { id: "provider", label: "Provider", gap: "GAP-G21" },
  { id: "network", label: "网络/代理", gap: "GAP-G23" },
  { id: "ocr", label: "OCR", gap: "GAP-G25" },
  { id: "translation", label: "翻译与检测", gap: null }, // Live: hosts SettingsPanel / SfxPolicyControl
  { id: "inpaint", label: "图片修复", gap: "GAP-G25" },
  { id: "typeset", label: "排版样式", gap: "GAP-G25" },
  { id: "model_gpu", label: "模型/GPU", gap: "GAP-G25" },
  { id: "task_concurrency", label: "任务/并发", gap: "GAP-G25" },
  { id: "cache_revision", label: "缓存/Revision", gap: "GAP-G25" },
  { id: "recycle_bin", label: "回收站", gap: "GAP-G2" },
  { id: "backup_restore", label: "备份/恢复", gap: "GAP-G25" },
  { id: "plugins", label: "Plugin/Hooks", gap: "GAP-G25" },
] as const;

export function SettingsPage({ client }: SettingsPageProps) {
  const [activeCategoryId, setActiveCategoryId] = useState<string>("translation");

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
      {/* Left fixed category navigation: 200px width (§5.2) */}
      <nav
        data-testid="settings-category-nav"
        style={{
          width: 200,
          height: "100%",
          boxSizing: "border-box",
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
          const isLive = cat.gap === null;

          return (
            <button
              key={cat.id}
              type="button"
              data-testid={`settings-category-${cat.id}`}
              data-active={isActive}
              onClick={() => setActiveCategoryId(cat.id)}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "8px 10px",
                fontSize: tokens.typography.size.base,
                borderRadius: tokens.radius.button,
                border: "none",
                backgroundColor: isActive ? tokens.color.accent.selected : "transparent",
                color: isActive
                  ? tokens.color.accent.primary
                  : isLive
                  ? tokens.color.text.primary
                  : tokens.color.text.muted,
                cursor: "pointer",
                fontWeight: isActive ? 600 : 400,
                textAlign: "left",
                transition: "background-color 0.1s ease",
              }}
            >
              <span>{cat.label}</span>
              {cat.gap && (
                <span
                  title={`等待能力接入 (${cat.gap})`}
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

      {/* Right content panel */}
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
        {activeCategoryId === "translation" ? (
          <div>
            <h2
              style={{
                margin: 0,
                marginBottom: tokens.spacing.md,
                fontSize: tokens.typography.size.panelTitle,
                fontWeight: 600,
                color: tokens.color.text.primary,
              }}
            >
              翻译与检测 (Translation & Detection)
            </h2>
            {/* Live SFX Policy Control */}
            <SettingsPanel client={client} />
          </div>
        ) : (
          <div
            data-testid={`settings-gap-panel-${activeCategoryId}`}
            style={{
              padding: tokens.spacing.xl,
              backgroundColor: tokens.color.surface.card,
              border: `1px dashed ${tokens.color.border.default}`,
              borderRadius: tokens.radius.card,
              textAlign: "center",
              color: tokens.color.text.secondary,
              maxWidth: 560,
            }}
          >
            <div style={{ fontSize: 36, marginBottom: tokens.spacing.sm }}>⚙️</div>
            <h3 style={{ margin: 0, fontSize: tokens.typography.size.cardTitle, color: tokens.color.text.primary }}>
              {activeCategory?.label} 设置
            </h3>
            <p style={{ fontSize: tokens.typography.size.base, marginTop: tokens.spacing.xs, color: tokens.color.text.muted }}>
              此配置分区的后端契约尚未冻结（{activeCategory?.gap}：等待后续任务规划接入）。
            </p>
            <div
              style={{
                marginTop: tokens.spacing.md,
                fontSize: tokens.typography.size.secondary,
                color: tokens.color.state.skipped,
                fontFamily: tokens.typography.monospace,
              }}
            >
              状态：Disabled（禁止 Mock / 私有路径）
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
