/* =============================================================================
   New Manga · 方向 C「工坊 Atelier」· app.js
   状态 + 事件 + 键盘 + URL 参数。全部原生 JS，零依赖，无网络请求。
   ============================================================================= */
'use strict';

(function () {
  var NM = window.NM, V = NM.v;
  var root = document.documentElement;
  var $ = function (id) { return document.getElementById(id); };

  var el = {
    railTabs: $('railTabs'), gate: $('gateStrip'), tree: $('tree'), matrix: $('matrix'),
    chips: $('chips'), surface: $('surface'), bulk: $('bulk'), runStrip: $('runStrip'),
    runPanel: $('runPanel'), drawer: $('drawer'), states: $('states'), palette: $('palette'),
    scrim: $('scrim'), dialog: $('dialog'), dlgScrim: $('dlgScrim'), demo: $('demoNote'),
    themeIcon: $('themeIcon'), app: $('app')
  };

  /* ---------------- 状态 ---------------- */
  var ui = {
    stage: 'detect',
    theme: 'dark',
    filter: 'all',
    chapter: 'c12',
    pages: [],
    sel: {},
    anchor: { r: 0, c: 0 },
    focus: { r: 0, c: 0 },
    activeCol: -1,
    runOpen: false,
    runState: 'running',
    drawer: null,
    state: null,
    palOpen: false, palQ: '', palActive: 0,
    statesOpen: false,
    matrixMax: false,
    dlg: null
  };
  ui.statesOf = function (key) {
    var a = key.split(':');
    return ui.pages[+a[0]].states[+a[1]];
  };

  /* ---------------- 数据装载 ---------------- */
  function loadChapter(id) {
    ui.chapter = id;
    if (id === 'c12') {
      ui.pages = NM.PAGES;
    } else {
      var ch = NM.CHAPTERS.filter(function (c) { return c.id === id; })[0];
      ui.pages = NM.genChapter(ch);
    }
    ui.sel = {};
    ui.focus = { r: 0, c: 0 };
    ui.anchor = { r: 0, c: 0 };
    ui.drawer = null;
  }

  /* ---------------- 渲染 ---------------- */
  function renderRail() {
    el.railTabs.innerHTML = V.tabs(ui.stage);
    el.gate.innerHTML = V.gate(ui.stage);
  }
  function renderTree() { el.tree.innerHTML = V.tree(ui); }
  function renderChips() { el.chips.innerHTML = V.chips(ui); }
  function renderMatrix() {
    el.matrix.innerHTML = V.matrix(ui, ui.pages);
    paintFocus();
  }
  function renderSurface() { el.surface.innerHTML = V.surface(ui, ui.pages); }
  function renderBulk() {
    var n = count(ui.sel);
    if (!n) { el.bulk.hidden = true; return; }
    el.bulk.hidden = false;
    el.bulk.innerHTML = V.bulk(ui);
  }
  function renderRun() {
    el.runStrip.innerHTML = V.runstrip(ui);
    if (ui.runOpen) {
      el.runPanel.hidden = false;
      el.runPanel.innerHTML = V.runpanel(ui);
    } else {
      el.runPanel.hidden = true;
      el.runPanel.innerHTML = '';
    }
  }
  function renderDrawer() {
    if (!ui.drawer) {
      el.drawer.dataset.open = '0';
      el.drawer.setAttribute('aria-hidden', 'true');
      el.drawer.innerHTML = '';
      return;
    }
    var d = V.drawer(ui);
    el.drawer.innerHTML = d.head + '<div class="dr-body">' + d.body + '</div>' + d.foot;
    el.drawer.dataset.open = '1';
    el.drawer.setAttribute('aria-hidden', 'false');
  }
  function renderStates() {
    var d = V.states(ui);
    el.states.innerHTML = d.head + d.body + d.foot;
    el.states.dataset.open = ui.statesOpen ? '1' : '0';
    el.states.setAttribute('aria-hidden', ui.statesOpen ? 'false' : 'true');
  }
  function renderPalette() {
    el.palette.innerHTML = V.palette(ui);
    el.palette.classList.toggle('hidden', !ui.palOpen);
    el.scrim.classList.toggle('hidden', !ui.palOpen);
    if (ui.palOpen) {
      var inp = $('palInput');
      if (inp) { inp.value = ui.palQ; inp.focus(); inp.setSelectionRange(inp.value.length, inp.value.length); }
    }
  }
  function renderAll() { renderRail(); renderTree(); renderChips(); renderMatrix(); renderSurface(); renderBulk(); renderRun(); renderDrawer(); renderStates(); renderPalette(); }

  function count(o) { return Object.keys(o).length; }

  /* ---------------- 选中与焦点 ---------------- */
  var rowsCache = null;
  function cells() {
    if (!rowsCache) rowsCache = el.matrix.querySelectorAll('.cell[data-r]');
    return rowsCache;
  }
  function paintSel() {
    var cs = cells();
    for (var i = 0; i < cs.length; i++) {
      var k = cs[i].dataset.r + ':' + cs[i].dataset.c;
      cs[i].dataset.selected = ui.sel[k] ? '1' : '0';
    }
  }
  function paintFocus() {
    rowsCache = null;
    var cs = el.matrix.querySelectorAll('.cell[data-r]');
    for (var i = 0; i < cs.length; i++) {
      var f = (+cs[i].dataset.r === ui.focus.r && +cs[i].dataset.c === ui.focus.c);
      cs[i].dataset.focus = f ? '1' : '0';
      var row = cs[i].closest('.mx-row');
      if (row) row.dataset.focus = (+cs[i].dataset.r === ui.focus.r) ? '1' : '0';
    }
  }
  function selectRange(a, b, additive) {
    if (!additive) ui.sel = {};
    var r0 = Math.min(a.r, b.r), r1 = Math.max(a.r, b.r);
    var c0 = Math.min(a.c, b.c), c1 = Math.max(a.c, b.c);
    for (var r = r0; r <= r1; r++) for (var c = c0; c <= c1; c++) ui.sel[r + ':' + c] = 1;
  }
  function commitSel() { paintSel(); renderBulk(); renderMatrixSelLine(); }
  function renderMatrixSelLine() {
    var foot = el.matrix.querySelector('.mx-sel');
    if (!foot) return;
    foot.innerHTML = V.selSummary(ui) + '<span class="keyhint">点击选中 · Shift 框选 · Enter 下钻 · 空格切换</span>';
  }

  /* ---------------- 提示条 ---------------- */
  var noteTimer = null;
  function note(msg) {
    el.demo.classList.remove('hidden');
    el.demo.innerHTML = V.ic('i-check', 'icon-12') + '<span>' + msg + '</span>';
    clearTimeout(noteTimer);
    noteTimer = setTimeout(function () { el.demo.classList.add('hidden'); }, 4200);
  }
  function noteState() {
    if (!ui.state) { el.demo.classList.add('hidden'); return; }
    var s = NM.STATES.filter(function (x) { return x.key === ui.state; })[0];
    if (!s) return;
    el.demo.classList.remove('hidden');
    el.demo.innerHTML = V.ic('i-eye', 'icon-12') +
      '<span>状态演示 <b>' + s.n + '/12</b> · ' + V.esc(s.t) + ' · ' + V.esc(s.d) + '</span>';
  }

  /* ---------------- 抽屉 ---------------- */
  function openDrawer(r, c) {
    ui.drawer = { r: r, c: c };
    ui.focus = { r: r, c: c };
    renderDrawer(); paintFocus();
  }
  function closeDrawer() { ui.drawer = null; renderDrawer(); }

  /* ---------------- 对话框 ---------------- */
  function openDialog(spec) {
    ui.dlg = spec;
    var d = V.dialog(spec);
    el.dialog.innerHTML = d.head + d.body + d.foot;
    el.dialog.classList.remove('hidden');
    el.dlgScrim.classList.remove('hidden');
  }
  function closeDialog() {
    ui.dlg = null;
    el.dialog.classList.add('hidden');
    el.dlgScrim.classList.add('hidden');
    el.dialog.innerHTML = '';
  }

  /* ---------------- 对话框内容 ---------------- */
  function dlgGateRender() {
    openDialog({
      kicker: 'QUALITY GATE · RENDER', title: '12 页未修复，导出将缺失成品',
      body: '<p>批次 <code style="font-family:var(--font-data)">' + NM.BATCH.id + '</code> 中有 12 页的修复轨未完成，成品页会缺字。</p>' +
        '<div class="impact">' +
        '<div><span>影响页数</span><b class="bad">12</b></div>' +
        '<div><span>其中失败（ModelLoadError）</span><b>4</b></div>' +
        '<div><span>其中待修复（排队中）</span><b>8</b></div>' +
        '<div><span>可撤销</span><b>是（保留 Revision）</b></div>' +
        '<div><span>导出格式</span><b>PNG · 1200×1800</b></div>' +
        '</div>' +
        '<p class="note">选择「先修复」将把 12 页加入 INPAINT 队列；选择「仍然导出」会生成缺失成品的批次并在报告中标注。</p>',
      actions: [{ label: '先修复 12 页（推荐）', act: 'do-repair' }, { label: '仍然导出', act: 'do-export', tone: 'danger' }]
    });
  }
  function dlgStop() {
    openDialog({
      kicker: 'DESTRUCTIVE · STOP RUN', title: '停止 Run #R-8831？',
      body: '<p>停止后本次未完成的 5 页将回到等待状态，已完成的 18 页成果保留。</p>' +
        '<div class="impact"><div><span>当前进度</span><b>62% · 18/23 页</b></div>' +
        '<div><span>未处理</span><b>5</b></div><div><span>已消耗</span><b>12:07</b></div>' +
        '<div><span>可撤销</span><b class="bad">否（需重新排队）</b></div></div>' +
        '<p class="note">已完成成果不会回滚；可稍后用「继续」从剩余页恢复（不重新跑已完成页）。</p>',
      actions: [{ label: '停止并保留成果', act: 'do-stop', tone: 'danger' }]
    });
  }
  function dlgResume() {
    openDialog({
      kicker: 'INTERRUPTED · RECOVER', title: 'Run #R-8827 上次异常退出',
      body: '<p>第8话 translate_all 中断，已完成 7/20 页。</p>' +
        '<div class="impact"><div><span>中断范围</span><b>第8话 · 20 页</b></div>' +
        '<div><span>已完成</span><b>7</b></div><div><span>剩余</span><b>13</b></div>' +
        '<div><span>中断原因</span><b class="bad">异常退出（exit 1）</b></div></div>' +
        '<p class="note">继续：从剩余 13 页恢复；重新开始：清空该 Run 的中间产物并全量重跑；放弃：标记为 cancelled，保留已完成成果。</p>',
      actions: [{ label: '继续（剩余 13 页）', act: 'do-resume' }, { label: '重新开始', act: 'do-restart', tone: 'danger' }, { label: '放弃', act: 'do-discard' }],
      ok: true
    });
  }
  function dlgExport() {
    openDialog({
      kicker: 'EXPORT · BATCH', title: '导出批次 B-012',
      body: '<p>范围：第1–10章 · 240 页；已确认 182 页，待确认 40 页。</p>' +
        '<div class="impact"><div><span>输出</span><b>PNG 顺页序</b></div>' +
        '<div><span>命名</span><b>{book}/{chapter}/{page}</b></div>' +
        '<div><span>门禁</span><b class="bad">RENDER 12 页未修复</b></div>' +
        '<div><span>预计体积</span><b>1.4 GiB</b></div></div>' +
        '<p class="note">导出只读源文件，不修改原始素材；成品写入 Managed Copy 输出目录。</p>',
      actions: [{ label: '导出已确认的 182 页', act: 'do-export' }, { label: '含待确认一并导出', act: 'do-export-all' }]
    });
  }
  function dlgProvider() {
    openDialog({
      kicker: 'BLOCKED · PROVIDER', title: 'Provider 认证失效（401）',
      body: '<p>Run #R-8828 因 Provider 凭据失效被阻塞，影响第9话 21 页。</p>' +
        '<div class="impact"><div><span>Provider</span><b>deepseek-v3</b></div>' +
        '<div><span>影响范围</span><b>21 页 · 4 队列项</b></div>' +
        '<div><span>错误</span><b class="bad">ProxyConnectionError / 401</b></div>' +
        '<div><span>网络</span><b>socks5://127.0.0.1:1080</b></div></div>' +
        '<p class="note">修复后需要手动「恢复队列」；系统不会自动静默重试（保持状态诚实）。</p>',
      actions: [{ label: '打开 Provider 设置', act: 'do-provider' }, { label: '切直连并恢复', act: 'do-resume' }]
    });
  }

  /* ---------------- 12 状态演示 ---------------- */
  function applyState(key) {
    ui.state = key;
    ui.statesOpen = true;
    renderStates();
    var s = NM.STATES.filter(function (x) { return x.key === key; })[0];
    if (!s) return;
    if (key === 'partial') {
      openDialog({
        kicker: 'STATE 09 · PARTIAL REGION', title: 'Region 部分完成（同一页状态不一致）',
        body: '<p>021.jpg 共 9 个 Region：OCR / 配色 / 术语全部完成，其中 <b>1 个 Region 翻译失败</b>（ProviderRateLimitError），其余 8 个已完成。</p>' +
          '<div class="import-list">' +
          '<div class="import-row" data-s="done"><span>R01–R06</span><span class="fn">对白 · 竖排</span><span>translate ✓</span><span class="st">done</span></div>' +
          '<div class="import-row" data-s="failed"><span>R07</span><span class="fn">旁白 · 横排</span><span>ProviderRateLimitError</span><span class="st">failed</span></div>' +
          '<div class="import-row" data-s="pending"><span>R08–R09</span><span class="fn">拟声词 / 注释</span><span>等待</span><span class="st">pending</span></div>' +
          '</div>' +
          '<p class="note">页级综合状态为「部分完成」；失败只影响 R07，重试该 Region 即可，不必整页重跑。</p>',
        actions: [{ label: '只重试 R07', act: 'do-retry-failed' }, { label: '换 Provider', act: 'do-provider' }]
      });
      return;
    }
    if (key === 'stale') {
      openDialog({
        kicker: 'STATE 10 · STALE', title: '过期 stale（曾成功但已失效）',
        body: '<p>020.jpg 的 <b>render / save</b> 为 <code>stale</code>：019.jpg 的 Region 几何在上次修复后变更，导致下游渲染结果不再是当前有效结果。</p>' +
          '<div class="import-list">' +
          '<div class="import-row" data-s="done"><span>DETECT–INPAINT</span><span class="fn">上游 8 个阶段</span><span>completed</span><span class="st">done</span></div>' +
          '<div class="import-row" data-s="stale"><span>RENDER</span><span class="fn">过期原因：geometry@019</span><span>历史 r3 保留</span><span class="st">stale</span></div>' +
          '</div>' +
          '<p class="note">stale ≠ not_started，也 ≠ failed：结果曾经有效、历史版本仍在，只是当前不再是最新。重跑过期项即可恢复。</p>',
        actions: [{ label: '重跑过期项', act: 'do-rerun-stale' }, { label: '查看过期原因', act: 'do-detail' }]
      });
      return;
    }
    switch (key) {
      case 'empty':
        openDialog({
          kicker: 'STATE 01 · EMPTY', title: '还没有作品', ok: true,
          body: '<div class="empty" style="height:auto;padding:0"><div class="empty-inner">' +
            '<h2>把第一章放进来</h2>' +
            '<p>支持文件夹批量导入（jpg / png / webp / cbz）。源文件只读，成品写入 Managed Copy。</p>' +
            '<div class="row">' + V.ic('i-folder', 'icon-12') + 'D:\\Manga\\夜光列车\\第12话</div>' +
            '<div class="paths"><span>数据根 <b>D:\\NewManga\\library</b></span>' +
            '<span>缓存 <b>D:\\NewManga\\cache · 2.1 GiB</b></span></div>' +
            '</div></div>',
          actions: [{ label: '导入文件夹', act: 'do-import' }, { label: '导入文件', act: 'do-import' }]
        });
        break;
      case 'importing':
        openDialog({
          kicker: 'STATE 02 · IMPORTING', title: '正在导入 23 个文件', ok: true,
          body: '<p>目标：夜光列车 / 第12话。已完成 18，失败 2，剩余 3。</p>' +
            '<div class="import-list">' +
            '<div class="import-row" data-s="done"><span>001</span><span class="fn">001.jpg</span><span>1200×1800</span><span class="st">done</span></div>' +
            '<div class="import-row" data-s="running"><span>019</span><span class="fn">019.jpg</span><span>1200×1800</span><span class="st">38%</span></div>' +
            '<div class="import-row" data-s="failed"><span>021</span><span class="fn">021.CR2</span><span>不支持</span><span class="st">failed</span></div>' +
            '<div class="import-row" data-s="failed"><span>022</span><span class="fn">022.jpg</span><span>重复页</span><span class="st">failed</span></div>' +
            '</div>',
          actions: [{ label: '取消导入', act: 'do-cancel' }]
        });
        break;
      case 'import_part_fail':
        openDialog({
          kicker: 'STATE 03 · PARTIAL FAIL', title: '导入完成，2 个文件失败',
          body: '<p>21 个文件已导入第12话，2 个未导入。</p>' +
            '<div class="import-list">' +
            '<div class="import-row" data-s="failed"><span>021</span><span class="fn">021.CR2</span><span>格式不支持</span><span class="st">failed</span></div>' +
            '<div class="import-row" data-s="failed"><span>022</span><span class="fn">022.jpg</span><span>与 019 重复</span><span class="st">failed</span></div>' +
            '</div>' +
            '<p class="note">可重试失败项（先转换格式 / 改名），或跳过继续进入 DETECT。</p>',
          actions: [{ label: '重试失败项', act: 'do-retry-import' }, { label: '跳过继续', act: 'do-skip' }]
        });
        break;
      case 'chapter_empty':
        openDialog({
          kicker: 'STATE 04 · EMPTY CHAPTER', title: '本章还没有页面', ok: true,
          body: '<p>第13话「回送」当前 0 页。</p><div class="split2">' +
            '<div><h3>上一章</h3><div class="lst">第12话 · 23 页</div></div>' +
            '<div><h3>下一章</h3><div class="lst">第14话 · 18 页</div></div></div>' +
            '<p class="note">可导入页面，或从上一章复制批处理设置。</p>',
          actions: [{ label: '导入页面', act: 'do-import' }]
        });
        break;
      case 'page_no_region':
        openDialog({
          kicker: 'STATE 05 · NO REGION', title: '022.jpg 未检测到文字区域', ok: true,
          body: '<p>DETECT 已完成 0.4s，输出 0 个 Region。</p>' +
            '<div class="impact"><div><span>页</span><b>022.jpg · 1200×1800</b></div>' +
            '<div><span>置信阈值</span><b>0.30</b></div><div><span>建议</span><b>降低阈值或手绘 Region</b></div></div>' +
            '<p class="note">可能是空白过渡页；若确为纯黑页可标记 not_applicable 并在导出时保留空白。</p>',
          actions: [{ label: '降低阈值重检测', act: 'do-redetect' }, { label: '手动新建 Region', act: 'do-newregion' }]
        });
        break;
      case 'running':
        ui.runState = 'running'; ui.runOpen = true; ui.stage = 'queue'; go('queue');
        renderRun(); break;
      case 'paused':
        ui.runState = 'paused'; ui.runOpen = true; ui.stage = 'queue'; go('queue');
        renderRun(); break;
      case 'done_with_fail':
        ui.runOpen = true; renderRun();
        openDialog({
          kicker: 'STATE 08 · COMPLETED WITH FAILURES', title: 'Run #R-8831 完成，2 页失败', ok: true,
          body: '<p>18 页完成，2 页失败，1 页跳过，2 页等待。成果已保留。</p>' +
            '<div class="impact"><div><span>ProviderRateLimitError</span><b class="bad">1 · p018</b></div>' +
            '<div><span>ModelLoadError</span><b class="bad">1 · p019</b></div>' +
            '<div><span>stale（下游过期）</span><b>1 · p020</b></div>' +
            '<div><span>报告</span><b>run-R-8831.json</b></div></div>' +
            '<p class="note">「只重试失败」不会重跑已完成的 18 页（增量口径）。</p>',
          actions: [{ label: '只重试失败 2 页', act: 'do-retry-failed' }, { label: '查看报告', act: 'do-report' }]
        });
        break;
      case 'blocked':
        ui.runOpen = true; go('queue'); renderRun(); dlgProvider(); break;
      case 'resume': dlgResume(); break;
      case 'review_backlog':
        ui.filter = 'review'; go('verify');
        renderChips(); renderMatrix(); renderBulk(); break;
      case 'danger': dlgStop(); break;
      default: break;
    }
    noteState();
    syncURL();
  }

  /* ---------------- 导航 ---------------- */
  function go(stage) {
    ui.stage = stage;
    renderRail();
    renderSurface();
    document.body.classList.toggle('matrix-max', ui.matrixMax);
    syncURL();
  }
  function setTheme(t) {
    ui.theme = t;
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('nm.atelier.theme', t); } catch (e) { /* 忽略：离线文件可能禁用存储 */ }
    if (el.themeIcon) el.themeIcon.innerHTML = '<use href="' + (t === 'dark' ? '#i-sun' : '#i-moon') + '"></use>';
    syncURL();
  }
  function toggleTheme() { setTheme(ui.theme === 'dark' ? 'light' : 'dark'); }
  function setFilter(k) {
    ui.filter = (ui.filter === k && k !== 'all') ? 'all' : k;
    renderChips(); renderMatrix(); renderBulk();
    var n = 0;
    if (ui.filter !== 'all') n = ui.pages.filter(function (p) { return p.derived === ui.filter; }).length;
    if (ui.filter !== 'all' && !n) note('筛选「' + ui.filter + '」在本章 0 行 · 全批 ' + (NM.CHIPS.filter(function (c) { return c.k === ui.filter; })[0] || {}).n + ' 页（矩阵仅展示第12话 23 行）');
    else if (ui.filter !== 'all') note('已筛选：' + ui.filter + ' · 本章 ' + n + ' 行');
    syncURL();
  }

  /* ---------------- URL ---------------- */
  var URL_KEYS = ['stage', 'theme', 'state', 'filter', 'matrix', 'run', 'drawer'];
  function syncURL() {
    if (!history.replaceState) return;
    var p = new URLSearchParams(location.search);
    p.set('stage', ui.stage); p.set('theme', ui.theme);
    if (ui.state) p.set('state', ui.state); else p.delete('state');
    if (ui.filter !== 'all') p.set('filter', ui.filter); else p.delete('filter');
    if (ui.matrixMax) p.set('matrix', 'max'); else p.delete('matrix');
    if (ui.runOpen) p.set('run', '1'); else p.delete('run');
    if (ui.drawer) p.set('drawer', ui.drawer.r + ':' + ui.drawer.c); else p.delete('drawer');
    var selKeys = Object.keys(ui.sel);
    if (selKeys.length) p.set('sel', selKeys.join(',')); else p.delete('sel');
    try { history.replaceState(null, '', location.pathname + '?' + p.toString()); } catch (e) { /* file:// 下部分环境禁写 */ }
  }
  function readURL() {
    var p = new URLSearchParams(location.search);
    var stage = p.get('stage');
    if (stage && NM.TABS.some(function (t) { return t.k === stage; })) ui.stage = stage;
    var theme = p.get('theme') || null;
    if (!theme) { try { theme = localStorage.getItem('nm.atelier.theme'); } catch (e) { theme = null; } }
    setTheme(theme === 'light' ? 'light' : 'dark');
    var f = p.get('filter');
    if (f && NM.CHIPS.some(function (c) { return c.k === f; })) ui.filter = f;
    ui.matrixMax = p.get('matrix') === 'max';
    ui.runOpen = p.get('run') === '1';
    var dr = p.get('drawer');
    if (dr && dr.indexOf(':') > 0) {
      var a = dr.split(':');
      ui.drawer = { r: Math.min(+a[0] || 0, ui.pages.length - 1), c: Math.min(+a[1] || 0, 10) };
      ui.focus = { r: ui.drawer.r, c: ui.drawer.c };
    }
    /* 深链选中：?sel=17:4,18:7（也用于截图验证批量动作条） */
    var selp = p.get('sel');
    if (selp) {
      selp.split(',').forEach(function (kv) {
        var a2 = kv.split(':'), r = +a2[0], c = +a2[1];
        if (ui.pages[r] && c >= 0 && c <= 10) { ui.sel[r + ':' + c] = 1; ui.focus = { r: r, c: c }; }
      });
    }
    var st = p.get('state');
    if (st) setTimeout(function () { applyState(st); }, 0);
    if (p.get('palette') === '1') setTimeout(openPalette, 0);
  }

  /* ---------------- 事件：点击委托 ---------------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    var tab = t.closest('[data-stage]');
    if (tab && tab.classList.contains('tab')) { go(tab.dataset.stage); return; }

    var chip = t.closest('[data-chip]');
    if (chip) { setFilter(chip.dataset.chip); return; }

    var tr = t.closest('.tree-row');
    if (tr) {
      if (tr.dataset.chapter) { loadChapter(tr.dataset.chapter); renderTree(); renderMatrix(); renderBulk(); renderSurface(); note('已切换：' + tr.textContent.trim()); }
      else if (tr.dataset.batch) note('批次 ' + tr.dataset.batch + ' · 240 页（原型固定演示 B-012）');
      else if (tr.dataset.run) { ui.runOpen = true; renderRun(); note('Run ' + tr.dataset.run + ' 已展开'); }
      else if (tr.dataset.book != null) note('作品：' + tr.querySelector('.tw').textContent);
      return;
    }

    var act = t.closest('[data-action]');
    if (act) { doAction(act.dataset.action, act.dataset); return; }

    var dlg = t.closest('[data-dlg]');
    if (dlg) { doDialog(dlg.dataset.dlg); return; }

    var st = t.closest('[data-state]');
    if (st) { applyState(st.dataset.state); return; }

    var cmd = t.closest('[data-cmd]');
    if (cmd) { runCmd(cmd.dataset.cmd); return; }

    var page = t.closest('[data-page]');
    if (page) { note('页 ' + page.dataset.page + ' · 打开该页工作面（原型：矩阵/抽屉已提供入口）'); return; }

    var region = t.closest('[data-region]');
    if (region) { note('Region ' + region.dataset.region + ' · 四轨状态见抽屉'); return; }
  });

  /* 矩阵：指针选择 + 框选 */
  var drag = null, mqEl = null;
  el.matrix.addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    var cell = e.target.closest('.cell');
    if (!cell || cell.dataset.sum === '1') return;
    e.preventDefault();
    drag = {
      sx: e.clientX, sy: e.clientY, moved: false,
      r: +cell.dataset.r, c: +cell.dataset.c,
      base: (e.altKey || e.metaKey) ? Object.assign({}, ui.sel) : {}
    };
    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp, { once: true });
  });

  function onMove(e) {
    if (!drag) return;
    if (!drag.moved && Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) > 4) drag.moved = true;
    if (!drag.moved) return;
    var rows = el.matrix.querySelector('.mx-rows');
    if (!rows) return;
    if (!mqEl) { mqEl = document.createElement('div'); mqEl.className = 'marquee'; rows.appendChild(mqEl); }
    var rr = rows.getBoundingClientRect();
    var x0 = Math.min(drag.sx, e.clientX), x1 = Math.max(drag.sx, e.clientX);
    var y0 = Math.min(drag.sy, e.clientY), y1 = Math.max(drag.sy, e.clientY);
    mqEl.style.left = (x0 - rr.left) + 'px';
    mqEl.style.top = (y0 - rr.top) + 'px';
    mqEl.style.width = (x1 - x0) + 'px';
    mqEl.style.height = (y1 - y0) + 'px';

    ui.sel = Object.assign({}, drag.base);
    var cs = el.matrix.querySelectorAll('.cell[data-r]');
    for (var i = 0; i < cs.length; i++) {
      var b = cs[i].getBoundingClientRect();
      if (b.left < x1 && b.right > x0 && b.top < y1 && b.bottom > y0) {
        ui.sel[cs[i].dataset.r + ':' + cs[i].dataset.c] = 1;
      }
    }
    paintSel();
    renderMatrixSelLine();
    renderBulk();
  }

  function onUp(e) {
    document.removeEventListener('pointermove', onMove);
    if (mqEl) { mqEl.remove(); mqEl = null; }
    if (!drag) return;
    var d = drag; drag = null;
    if (!d.moved) {
      var cell = e.target.closest ? e.target.closest('.cell') : null;
      var r = cell ? +cell.dataset.r : d.r, c = cell ? +cell.dataset.c : d.c;
      ui.focus = { r: r, c: c };
      if (e.shiftKey) { selectRange(ui.anchor, { r: r, c: c }, e.altKey || e.metaKey); }
      else if (e.altKey || e.metaKey) {
        var k = r + ':' + c;
        if (ui.sel[k]) delete ui.sel[k]; else ui.sel[k] = 1;
        ui.anchor = { r: r, c: c };
      } else {
        ui.anchor = { r: r, c: c };
        ui.sel = {}; ui.sel[r + ':' + c] = 1;
      }
    } else {
      ui.anchor = { r: d.r, c: d.c };
    }
    renderMatrix(); renderBulk();
  }

  el.matrix.addEventListener('dblclick', function (e) {
    var cell = e.target.closest('.cell');
    if (!cell || cell.dataset.sum === '1') return;
    openDrawer(+cell.dataset.r, +cell.dataset.c);
  });

  /* 命令面板输入 */
  el.palette.addEventListener('input', function (e) {
    if (e.target.id !== 'palInput') return;
    ui.palQ = e.target.value; ui.palActive = 0;
    renderPalette();
  });
  el.palette.addEventListener('keydown', function (e) {
    if (!ui.palOpen) return;
    var items = el.palette.querySelectorAll('.pal-item');
    if (e.key === 'ArrowDown') { e.preventDefault(); ui.palActive = Math.min(ui.palActive + 1, items.length - 1); markPal(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); ui.palActive = Math.max(ui.palActive - 1, 0); markPal(); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      if (items[ui.palActive]) runCmd(items[ui.palActive].dataset.cmd);
    } else if (e.key === 'Escape') { e.preventDefault(); closePalette(); }
  });
  function markPal() {
    var items = el.palette.querySelectorAll('.pal-item');
    for (var i = 0; i < items.length; i++) items[i].dataset.active = i === ui.palActive ? '1' : '0';
    if (items[ui.palActive] && items[ui.palActive].scrollIntoView) items[ui.palActive].scrollIntoView({ block: 'nearest' });
  }
  function openPalette() { ui.palOpen = true; ui.palQ = ''; ui.palActive = 0; renderPalette(); }
  function closePalette() { ui.palOpen = false; renderPalette(); }

  /* ---------------- 动作表 ---------------- */
  function doAction(a) {
    switch (a) {
      case 'palette': openPalette(); break;
      case 'theme': toggleTheme(); break;
      case 'states': ui.statesOpen = !ui.statesOpen; renderStates(); break;
      case 'states-close': ui.statesOpen = false; ui.state = null; renderStates(); noteState(); syncURL(); break;
      case 'state-next': nextState(); break;
      case 'state-clear': ui.state = null; ui.statesOpen = false; closeDialog(); renderStates(); noteState(); syncURL(); break;
      case 'settings': note('设置（原型）：Provider deepseek-v3 / manga_ocr / anime_lama_v2 · 代理 socks5://127.0.0.1:1080 · 并发 4/1/8'); break;
      case 'matrix-max': ui.matrixMax = !ui.matrixMax; document.body.classList.toggle('matrix-max', ui.matrixMax); note(ui.matrixMax ? '矩阵最大化（工作面已隐藏）' : '恢复三栏'); syncURL(); break;
      case 'only-abnormal': setFilter('failed'); break;
      case 'drawer-close': closeDrawer(); break;
      case 'retry': bulkRetry(); break;
      case 'advance': advanceSel(); break;
      case 'skip': note('已跳过 ' + count(ui.sel) + ' 个单元（原因：人工跳过 · 可恢复）'); break;
      case 'switch-provider': dlgProvider(); break;
      case 'clear-sel': ui.sel = {}; renderMatrix(); renderBulk(); break;
      case 'detail': if (ui.drawer) closeDrawer(); else openDrawer(ui.focus.r, ui.focus.c); break;
      case 'retry-one': note('已提交重试：' + (ui.drawer ? ui.pages[ui.drawer.r].pid : '') + ' · ' + (ui.drawer ? NM.STAGES[ui.drawer.c].full : '') + '（新 Run #R-8832）'); break;
      case 'advance-one': note('已推进 ' + (ui.drawer ? ui.pages[ui.drawer.r].pid : '') + ' 到下一阶段'); break;
      case 'skip-one': note('已跳过该单元（记录原因：人工跳过）'); break;
      case 'open-log': note('日志：run-R-8831.log · 最近 40 行（原型未内联）'); break;
      case 'pause': ui.runState = 'paused'; renderRun(); note('暂停已请求 · 将在当前步骤（translate）安全结束后生效'); break;
      case 'resume': ui.runState = 'running'; renderRun(); note('已继续 · Run #R-8831'); break;
      case 'stop': dlgStop(); break;
      case 'toggle-runpanel': ui.runOpen = !ui.runOpen; renderRun(); syncURL(); break;
      case 'gate-render': dlgGateRender(); break;
      case 'gate-review': setFilter('review'); go('verify'); break;
      case 'gate-detect': note('DETECT 门禁通过：23/23 页已检测，0 页无 Region'); break;
      case 'export': case 'export-anyway': dlgExport(); break;
      case 'open-provider': dlgProvider(); break;
      case 'resume-queue': note('队列已恢复 · R-8828 重新排队（21 页）'); break;
      case 'resume-run': dlgResume(); break;
      case 'discard-run': note('R-8827 已标记 cancelled · 已完成 7 页成果保留'); break;
      case 'redetect': note('已提交重检测 · 23 页（Run #R-8833）'); break;
      case 'reocr': note('已提交重 OCR · 6 页低置信（Run #R-8834）'); break;
      case 'reocr-one': note('已提交单页重 OCR'); break;
      case 'reinpaint': note('已提交重修复 · 换路线 BrushNet（4 页）'); break;
      case 'rerender': note('已提交重渲染 · 2 页溢出 + 3 页缺失'); break;
      case 'confirm-page': note('已确认第 007 页 6 个 Region（2 条待确认 → confirmed）'); break;
      case 'lock': note('已加锁 Region 3（needs_review）· 自动流程不再覆盖'); break;
      case 'route': note('修复路线：anime_lama_v2 → BrushNet（仅影响彩色背景 Region）'); break;
      case 'install-model': note('模型安装：anime_lama_v2（284 MiB）· 安装后需重跑 4 页'); break;
      case 'toggle-mask': note('Mask 叠加：开 / 关（原型固定为开）'); break;
      case 'toggle-diff': note('差分视图：原图与 clean 的差异高亮（原型未实现像素级差分）'); break;
      case 'sort-conf': note('按平均置信升序排序（最可疑在最上）'); break;
      case 'only-overflow': note('仅显示越界单元：2 页'); break;
      default: note('动作 ' + a + '（原型演示）'); break;
    }
  }

  function bulkRetry() {
    var n = 0;
    Object.keys(ui.sel).forEach(function (k) { if (ui.statesOf(k) === 'failed') n++; });
    if (!n) { note('选中的 ' + count(ui.sel) + ' 个单元里没有 failed 单元（重试只作用于 failed）'); return; }
    note('已提交重试 ' + n + ' 个 failed 单元 · 新 Run #R-8832 · 预计 1m10s');
  }
  function advanceSel() {
    var n = count(ui.sel);
    if (!n) { note('先选中单元再推进'); return; }
    note('已推进 ' + n + ' 个单元到下一阶段（已完成/已锁定的会被跳过并给出原因）');
  }

  function doDialog(a) {
    closeDialog();
    switch (a) {
      case 'do-repair': note('12 页已加入 INPAINT 队列 · 其中 4 页需先安装 anime_lama_v2'); break;
      case 'do-export': note('导出已开始：182 页 → D:\\NewManga\\out\\夜光列车（后台任务）'); break;
      case 'do-export-all': note('导出已开始：222 页（含 40 页待确认，报告中标注）'); break;
      case 'do-stop': ui.runState = 'paused'; renderRun(); note('Run #R-8831 已停止 · 18 页成果保留 · 剩余 5 页等待重新排队'); break;
      case 'do-resume': ui.runState = 'running'; renderRun(); note('已继续：从剩余 13 页恢复（不重跑已完成页）'); break;
      case 'do-restart': note('已重新开始：清空 R-8827 中间产物并全量重跑 20 页'); break;
      case 'do-discard': note('R-8827 已标记 cancelled'); break;
      case 'do-import': note('导入入口已打开（原型不发真实文件选择）'); break;
      case 'do-cancel': note('导入已取消 · 已导入的 18 页保留'); break;
      case 'do-retry-import': note('重试 2 个失败文件'); break;
      case 'do-skip': note('已跳过失败项，进入 DETECT'); go('detect'); break;
      case 'do-redetect': note('以阈值 0.20 重新检测 022.jpg'); break;
      case 'do-newregion': note('手动新建 Region 模式（画布内拖拽）'); break;
      case 'do-retry-failed': note('只重试失败 2 页 · 不重跑已完成 18 页'); break;
      case 'do-report': note('报告 run-R-8831.json 已打开'); break;
      case 'do-provider': note('Provider 设置：认证失效，需要重新填写 API Key'); break;
      case 'cancel': note('已取消'); break;
      default: note('已确认'); break;
    }
  }

  function nextState() {
    var i = 0;
    if (ui.state) i = NM.STATES.findIndex(function (s) { return s.key === ui.state; });
    i = (i + 1) % NM.STATES.length;
    applyState(NM.STATES[i].key);
  }

  function runCmd(label) {
    closePalette();
    var c = NM.CMD.filter(function (x) { return x.label === label; })[0];
    if (!c) return;
    var map = {
      '1': 'detect', '2': 'ocr', '3': 'verify', '4': 'inpaint', '5': 'render', 'Q': 'queue'
    };
    if (map[c.kk]) { go(map[c.kk]); return; }
    switch (label) {
      case '重试选中失败单元': bulkRetry(); break;
      case '跳过选中单元': doAction('skip'); break;
      case '推进所选到下一阶段': advanceSel(); break;
      case '导出批次 B-012': dlgExport(); break;
      case '矩阵筛选：只看失败': setFilter('failed'); break;
      case '矩阵筛选：只看过期': setFilter('stale'); break;
      case '矩阵最大化': doAction('matrix-max'); break;
      case '打开状态演示面板（12 状态真相）': ui.statesOpen = true; renderStates(); break;
      case '切换深/浅主题': toggleTheme(); break;
      case '暂停当前 Run': doAction('pause'); break;
      case '停止当前 Run': dlgStop(); break;
      case '恢复队列': doAction('resume-queue'); break;
      default: note(c.label);
    }
  }

  /* ---------------- 键盘 ---------------- */
  document.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase();
    var typing = tag === 'input' || tag === 'textarea';
    var mod = e.ctrlKey || e.metaKey;

    if (ui.palOpen) return; // 面板自己处理

    if (e.key === 'Escape') {
      if (ui.dlg) { closeDialog(); return; }
      if (ui.drawer) { closeDrawer(); return; }
      if (ui.statesOpen) { ui.statesOpen = false; renderStates(); return; }
      if (count(ui.sel)) { ui.sel = {}; renderMatrix(); renderBulk(); return; }
      return;
    }
    if (mod && e.key.toLowerCase() === 'k') { e.preventDefault(); openPalette(); return; }
    if (typing) return;
    if (mod && e.shiftKey && e.key.toLowerCase() === 'r') { e.preventDefault(); bulkRetry(); return; }
    if (mod && e.shiftKey && e.key.toLowerCase() === 'k') { e.preventDefault(); doAction('skip'); return; }
    if (mod && e.key === 'Enter') { e.preventDefault(); advanceSel(); return; }
    if (mod && e.key.toLowerCase() === 'e') { e.preventDefault(); dlgExport(); return; }

    var nav = { '1': 'detect', '2': 'ocr', '3': 'verify', '4': 'inpaint', '5': 'render', 'q': 'queue' };
    if (nav[e.key.toLowerCase()]) { e.preventDefault(); go(nav[e.key.toLowerCase()]); return; }
    if (e.key.toLowerCase() === 't') { toggleTheme(); return; }
    if (e.key.toLowerCase() === 's') { ui.statesOpen = !ui.statesOpen; renderStates(); return; }
    if (e.key.toLowerCase() === 'm') { doAction('matrix-max'); return; }

    var dr = 0, dc = 0;
    if (e.key === 'ArrowDown') dr = 1;
    else if (e.key === 'ArrowUp') dr = -1;
    else if (e.key === 'ArrowRight') dc = 1;
    else if (e.key === 'ArrowLeft') dc = -1;
    else if (e.key === ' ') { e.preventDefault(); toggleFocusCell(); return; }
    else if (e.key === 'Enter') { e.preventDefault(); openDrawer(ui.focus.r, ui.focus.c); return; }
    else return;

    e.preventDefault();
    var r = Math.max(0, Math.min(ui.pages.length - 1, ui.focus.r + dr));
    var c = Math.max(0, Math.min(10, ui.focus.c + dc));
    if (!e.shiftKey) { ui.focus = { r: r, c: c }; ui.anchor = { r: r, c: c }; }
    else { ui.focus = { r: r, c: c }; selectRange(ui.anchor, ui.focus, false); }
    renderMatrix(); renderBulk();
    var cur = el.matrix.querySelector('.cell[data-r="' + r + '"][data-c="' + c + '"]');
    if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  });

  function toggleFocusCell() {
    var k = ui.focus.r + ':' + ui.focus.c;
    if (ui.sel[k]) delete ui.sel[k]; else ui.sel[k] = 1;
    ui.anchor = { r: ui.focus.r, c: ui.focus.c };
    paintSel(); renderBulk(); renderMatrixSelLine();
  }

  /* ---------------- 启动 ---------------- */
  loadChapter('c12');
  readURL();
  renderAll();
  var ctx = $('ctxScope');
  if (ctx) ctx.textContent = NM.BATCH.scope + ' · ' + NM.BATCH.pages + ' 页';
  var ctxB = $('ctxBatch');
  if (ctxB) ctxB.textContent = NM.BATCH.id;
  document.body.classList.toggle('matrix-max', ui.matrixMax);
  if (ui.state) noteState();
  window.addEventListener('resize', function () { rowsCache = null; });

  /* 外层（截图脚本/评审）可调用的最小 API */
  window.Atelier = {
    go: go, setTheme: setTheme, setFilter: setFilter, applyState: applyState,
    openDrawer: openDrawer, select: function (r, c) { ui.sel = {}; ui.sel[r + ':' + c] = 1; ui.focus = { r: r, c: c }; renderMatrix(); renderBulk(); },
    ui: ui
  };
})();
