# M2-SETTINGS-UI-SFX-POLICY 组件快照（SSR renderToString）

事实源：SettingsPanel（apps/desktop/frontend/src/settings/SettingsPanel.tsx）六态 renderToString 输出。
生成方式：esbuild 打包 + node 执行（临时脚本已删）；复现：cd apps/desktop/frontend && npx vitest run src/settings（组件行为断言）。
登记人：ZCode（M2-SETTINGS-UI-SFX-POLICY Owner）

## default-skip

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><fieldset data-testid="settings-group-translation-detection" style="border:1px solid #30363d;border-radius:4px;margin:0;padding:12px"><legend style="font-size:13px;color:#8b949e;padding:0 6px">翻译与检测 (Translation &amp; Detection)</legend><div style="display:flex;align-items:baseline;gap:12px"><label for="sfx-policy-select" style="font-size:13px;min-width:140px;display:inline-block">SFX 翻译策略</label><select id="sfx-policy-select" data-testid="sfx-policy-select" style="padding:4px 8px;font-size:12px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:4px"><option value="skip" selected="">跳过翻译 (skip)</option><option value="translate">翻译 (translate)</option><option value="manual">手动处理 (manual)</option></select><button data-testid="sfx-policy-save-btn" disabled="" style="padding:4px 10px;font-size:12px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;cursor:not-allowed">保存</button></div><div style="font-size:12px;color:#8b949e;margin-top:8px"><div>当前生效值：<span data-testid="sfx-policy-effective">跳过翻译 (skip)</span>（默认）</div><div data-testid="sfx-policy-scope-note" style="margin-top:4px">保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）</div></div></fieldset></section>
```

## translate

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><fieldset data-testid="settings-group-translation-detection" style="border:1px solid #30363d;border-radius:4px;margin:0;padding:12px"><legend style="font-size:13px;color:#8b949e;padding:0 6px">翻译与检测 (Translation &amp; Detection)</legend><div style="display:flex;align-items:baseline;gap:12px"><label for="sfx-policy-select" style="font-size:13px;min-width:140px;display:inline-block">SFX 翻译策略</label><select id="sfx-policy-select" data-testid="sfx-policy-select" style="padding:4px 8px;font-size:12px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:4px"><option value="skip">跳过翻译 (skip)</option><option value="translate" selected="">翻译 (translate)</option><option value="manual">手动处理 (manual)</option></select><button data-testid="sfx-policy-save-btn" disabled="" style="padding:4px 10px;font-size:12px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;cursor:not-allowed">保存</button></div><div style="font-size:12px;color:#8b949e;margin-top:8px"><div>当前生效值：<span data-testid="sfx-policy-effective">翻译 (translate)</span></div><div data-testid="sfx-policy-scope-note" style="margin-top:4px">保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）</div></div></fieldset></section>
```

## manual

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><fieldset data-testid="settings-group-translation-detection" style="border:1px solid #30363d;border-radius:4px;margin:0;padding:12px"><legend style="font-size:13px;color:#8b949e;padding:0 6px">翻译与检测 (Translation &amp; Detection)</legend><div style="display:flex;align-items:baseline;gap:12px"><label for="sfx-policy-select" style="font-size:13px;min-width:140px;display:inline-block">SFX 翻译策略</label><select id="sfx-policy-select" data-testid="sfx-policy-select" style="padding:4px 8px;font-size:12px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:4px"><option value="skip">跳过翻译 (skip)</option><option value="translate">翻译 (translate)</option><option value="manual" selected="">手动处理 (manual)</option></select><button data-testid="sfx-policy-save-btn" disabled="" style="padding:4px 10px;font-size:12px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;cursor:not-allowed">保存</button></div><div style="font-size:12px;color:#8b949e;margin-top:8px"><div>当前生效值：<span data-testid="sfx-policy-effective">手动处理 (manual)</span></div><div data-testid="sfx-policy-scope-note" style="margin-top:4px">保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）</div></div></fieldset></section>
```

## unset-null

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><fieldset data-testid="settings-group-translation-detection" style="border:1px solid #30363d;border-radius:4px;margin:0;padding:12px"><legend style="font-size:13px;color:#8b949e;padding:0 6px">翻译与检测 (Translation &amp; Detection)</legend><div style="display:flex;align-items:baseline;gap:12px"><label for="sfx-policy-select" style="font-size:13px;min-width:140px;display:inline-block">SFX 翻译策略</label><select id="sfx-policy-select" data-testid="sfx-policy-select" style="padding:4px 8px;font-size:12px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:4px"><option value="skip" selected="">跳过翻译 (skip)</option><option value="translate">翻译 (translate)</option><option value="manual">手动处理 (manual)</option></select><button data-testid="sfx-policy-save-btn" disabled="" style="padding:4px 10px;font-size:12px;background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:4px;cursor:not-allowed">保存</button></div><div style="font-size:12px;color:#8b949e;margin-top:8px"><div>当前生效值：<span data-testid="sfx-policy-effective">跳过翻译 (skip)</span>（默认）</div><div data-testid="sfx-policy-scope-note" style="margin-top:4px">保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）</div></div></fieldset></section>
```

## loading

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><div data-testid="settings-loading" style="color:#8b949e;padding:12px 0">正在加载设置数据...</div></section>
```

## load-error

```html
<section data-testid="settings-panel" style="margin-top:20px;padding:16px;border:1px solid #2a3441;border-radius:6px;background:#161b22;color:#e6edf3"><h2 style="font-size:16px;margin:0;margin-bottom:12px;font-weight:600">设置 (Settings)</h2><div data-testid="settings-load-error" style="padding:12px;background:#3c1618;border:1px solid #f85149;border-radius:4px;color:#ff7b72"><div style="font-weight:bold">加载失败: <!-- -->CORE_UNAVAILABLE</div><div style="font-size:12px;margin-top:4px;color:#e6edf3">无法读取设置数据。请检查后台服务状态后重试（系统不会自动重试）。</div></div></section>
```

