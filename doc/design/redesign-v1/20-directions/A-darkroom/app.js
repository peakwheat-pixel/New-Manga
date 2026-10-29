/* =============================================================================
   方向 A · 暗房（Darkroom） — 交互层
   纯原生 JS，零依赖。驱动 index.html 中已冻结的 DOM 骨架。
   所有视觉值来自 styles.css 的令牌变量；本文件只做数据与行为。
   ============================================================================= */
(function () {
  'use strict';

  /* ---------------------------------------------------------------------------
     0. 统一假数据（与 30-prototype/00_SAMPLE_DATA.md 一致）
     ------------------------------------------------------------------------ */
  var BOOK = { title: '夜光列车', author: '架空 灯', chapters: 14, type: '日漫 · Paged · RTL' };

  var STEPS = [
    { key: 'detect', name: '检测' }, { key: 'ocr', name: 'OCR' }, { key: 'color', name: '配色' },
    { key: 'term', name: '术语' }, { key: 'translate', name: '翻译' }, { key: 'segment', name: '分割' },
    { key: 'mask', name: 'Mask' }, { key: 'inpaint', name: '修复' }, { key: 'render', name: '渲染' },
    { key: 'save', name: '保存' }
  ];

  // 23 页：status 取值 ok | review | fail | stale | run | todo
  var PAGE_STATUS = ['ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok',
    'review','fail','fail','stale','run','todo','todo'];

  var PAGES = PAGE_STATUS.map(function (st, i) {
    var no = String(i + 1).padStart(3, '0');
    var err = st === 'fail' ? (i + 1 === 18 ? 'ProviderRateLimitError' : 'ModelLoadError') : '';
    return { no: i + 1, file: no + '.jpg', status: st, err: err, regions: (i + 1) % 7 + 3 };
  });

  // 第 007 页的 6 个 Region（几何按页面 1200×1800 换算成百分比）
  var REGIONS = [
    { no: 1, type: '对白', jp: 'おはよう、また会えたね', mt: '早上好，又见面了呢', et: '', state: 'confirmed', lock: '', x: 12.3, y: 11.7, w: 26.8, h: 14.9 },
    { no: 2, type: '对白', jp: 'この雨、三日は止まないらしい', mt: '这场雨，好像三天都不会停', et: '这场雨，恐怕要下三天', state: 'confirmed', lock: 'translation', x: 51.0, y: 10.3, w: 25.0, h: 13.6 },
    { no: 3, type: '旁白', jp: '三日後の朝', mt: '三天后的早晨', et: '', state: 'needs_review', lock: '', x: 11.7, y: 31.1, w: 53.3, h: 5.3 },
    { no: 4, type: '拟声词', jp: 'ザァァァ', mt: '—（SFX 策略 skip）', et: '', state: 'unreviewed', lock: 'region', x: 58.3, y: 35.6, w: 21.7, h: 10.0 },
    { no: 5, type: '对白', jp: '切符をなくした', mt: '我把车票弄丢了', et: '', state: 'confirmed', lock: '', x: 35.8, y: 54.4, w: 24.7, h: 12.9 },
    { no: 6, type: '注释', jp: '※時刻表は変更されています', mt: '※时刻表已更改', et: '', state: 'needs_review', lock: '', x: 10.0, y: 86.7, w: 35.0, h: 6.7 }
  ];

  // 第 007 页的阶段状态
  var STAGE_STATE = { detect: 'ok', ocr: 'ok', color: 'ok', term: 'ok', translate: 'ok', segment: 'ok', mask: 'ok', inpaint: 'ok', render: 'ok', save: 'ok' };

  var RUN = { id: 'R-8831', cmd: 'translate_untranslated', status: 'running', pct: 62,
    current: { page: 21, step: 'translate', stepIdx: 4 },
    counts: { total: 23, ok: 18, fail: 2, skip: 1, wait: 2 } };

  var COMMANDS = [
    { name: '全部翻译（跳过已翻译）', key: 'Ctrl+Shift+T', scope: '本章 23 页', icon: 'spark' },
    { name: '重新渲染当前 Region', key: 'Shift+Enter', scope: '当前 Region', icon: 'retry' },
    { name: '重跑当前 Region 全链路', key: 'Ctrl+Shift+R', scope: '当前 Region', icon: 'spark' },
    { name: '重新 OCR 当前 Region', key: 'Ctrl+Shift+O', scope: '当前 Region', icon: 'text' },
    { name: '确认当前 Region', key: 'Enter', scope: '当前 Region', icon: 'check' },
    { name: '确认本页全部', key: 'Ctrl+Enter', scope: '第 007 页 · 6 Region', icon: 'check' },
    { name: '锁定 / 解锁当前 Region', key: 'L', scope: '当前 Region', icon: 'lock' },
    { name: '跳转到下一个失败单元', key: 'Ctrl+Shift+F', scope: '本章 · 2 个', icon: 'warn' },
    { name: '打开任务面板', key: 'Ctrl+Shift+E', scope: '本章', icon: 'steps' },
    { name: '导出本章', key: 'Ctrl+E', scope: '本章 23 页', icon: 'export' },
    { name: '切换资料柜', key: 'Ctrl+1', scope: '空间', icon: 'library' },
    { name: '切换控制台', key: 'Ctrl+3', scope: '空间', icon: 'console' },
    { name: '切换到第 7 页', key: '', scope: '页', icon: 'page' },
    { name: '配置 Provider：deepseek-v3', key: '', scope: '设置', icon: 'plug' }
  ];

  var STATES = [
    { id: 'empty', no: '§9-01', name: '空工作区', desc: '首次启动，无任何作品', where: '资料柜' },
    { id: 'importing', no: '§9-02', name: '导入中 / 部分失败', desc: '3 文件夹 · 2 个文件格式不支持', where: '资料柜 · 导入条' },
    { id: 'no-pages', no: '§9-03', name: '章节无页面 / 页面无 Region', desc: '第13话无页；或页内 0 Region', where: '资料柜 / 工位' },
    { id: 'running', no: '§9-04', name: '流水线运行中', desc: 'Run #R-8831 · 62% · 当前 021.jpg 翻译', where: '工位 · 流水线带' },
    { id: 'paused', no: '§9-05', name: '暂停中', desc: '等待当前步骤安全结束后暂停', where: '工位 · 流水线带' },
    { id: 'completed-with-failures', no: '§9-06', name: '完成但有失败', desc: '21 完成 / 2 失败 · 成果已保留', where: '工位 · 流水线带' },
    { id: 'blocked', no: '§9-07', name: '阻塞', desc: 'Provider 认证失效，需修复配置', where: '工位 · 横幅' },
    { id: 'interrupted', no: '§9-08', name: '中断恢复', desc: '继续 / 重新开始 / 放弃', where: '模态' },
    { id: 'partial-region', no: '§9-09', name: 'Region 部分完成', desc: 'OCR 完成、翻译失败', where: '工位 · 检查器' },
    { id: 'stale', no: '§9-10', name: '过期 stale', desc: '上游几何变更，渲染结果已过期', where: '工位 · 画布 + 带' },
    { id: 'review-queue', no: '§9-11', name: '待确认队列', desc: '3 条 needs_review 积压 · 逐条确认', where: '工位 · 审阅条' },
    { id: 'danger-confirm', no: '§9-12', name: '危险确认', desc: '将覆盖 2 条人工译文 · 不可撤销', where: '模态' }
  ];

  var CONSOLE_SECTIONS = [
    { id: 'queue', name: '任务队列', count: '3', icon: 'queue' },
    { id: 'provider', name: 'Provider 与凭据', count: '3', icon: 'plug' },
    { id: 'network', name: '网络代理', count: '1', icon: 'globe' },
    { id: 'model', name: '模型与设备', count: '4', icon: 'spark' },
    { id: 'cache', name: '缓存与版本', count: '2.1 GiB', icon: 'db' },
    { id: 'backup', name: '备份 .nmbak', count: '3', icon: 'archive' },
    { id: 'plugin', name: '插件与 Hooks', count: '2/3', icon: 'plugin' }
  ];

  /* ---------------------------------------------------------------------------
     1. 工具
     ------------------------------------------------------------------------ */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function ico(id, cls) { return '<svg class="ico ' + (cls || '') + '" aria-hidden="true"><use href="#i-' + id + '"></use></svg>'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function pad(n) { return String(n).padStart(3, '0'); }

  var MARK = {
    ok:       { cls: 'mark--ok',     ch: '✓' },
    review:   { cls: 'mark--review', ch: '●' },
    fail:     { cls: 'mark--err',    ch: '!' },
    stale:    { cls: 'mark--stale',  ch: '▨' },
    run:      { cls: 'mark--run',    ch: '◐' },
    todo:     { cls: 'mark--idle',   ch: '·' },
    locked:   { cls: 'mark--locked', ch: '🔒' },
    skip:     { cls: 'mark--skip',   ch: '–' }
  };
  function mark(st) { var m = MARK[st] || MARK.todo; return '<span class="mark ' + m.cls + '" title="' + st + '"></span>'; }

  /* ---------------------------------------------------------------------------
     2. 页面示意图（纯 SVG，抽象漫画页：分格 + 气泡 + 网点）
     ------------------------------------------------------------------------ */
  function pageArt(seed, opts) {
    opts = opts || {};
    var w = 120, h = 180, s = seed || 1;
    var panels = [
      [0, 0, 120, 62], [0, 62, 58, 60], [58, 62, 62, 60],
      [0, 122, 120, 58]
    ];
    var out = '<svg class="page-svg" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="xMidYMid meet" aria-hidden="true">';
    out += '<rect width="' + w + '" height="' + h + '" fill="#F2EFE8"/>';
    panels.forEach(function (p, i) {
      var x = p[0], y = p[1], pw = p[2], ph = p[3];
      out += '<rect x="' + (x + 1) + '" y="' + (y + 1) + '" width="' + (pw - 2) + '" height="' + (ph - 2) + '" fill="' + (i % 2 ? '#E7E2D8' : '#EFEBE3') + '" stroke="#C9C2B4" stroke-width="0.6"/>';
      // 网点纹理
      if (!opts.thumbs && (i + s) % 3 === 0) {
        for (var gy = y + 5; gy < y + ph - 5; gy += 4) {
          for (var gx = x + 5; gx < x + pw - 5; gx += 4) {
            out += '<circle cx="' + gx + '" cy="' + gy + '" r="0.45" fill="#B8B0A1" opacity="0.55"/>';
          }
        }
      }
      // 气泡
      if (!opts.thumbs && (i + s) % 2 === 1) {
        var cx = x + pw * 0.5, cy = y + ph * 0.42;
        out += '<ellipse cx="' + cx + '" cy="' + cy + '" rx="' + Math.min(pw, ph) * 0.3 + '" ry="' + Math.min(pw, ph) * 0.26 + '" fill="#FFFFFF" stroke="#B9B2A4" stroke-width="0.6"/>';
        out += '<path d="M' + (cx - 4) + ' ' + (cy + Math.min(pw, ph) * 0.24) + ' l-3 7 l8 -4 z" fill="#FFFFFF" stroke="#B9B2A4" stroke-width="0.6"/>';
        for (var l = 0; l < 3; l++) {
          out += '<rect x="' + (cx - 13) + '" y="' + (cy - 5 + l * 4) + '" width="' + (26 - l * 5) + '" height="1.5" fill="#9E9789"/>';
        }
      }
      // 人物线条
      if (!opts.thumbs && i === 0) {
        out += '<path d="M' + (x + pw * 0.18) + ' ' + (y + ph * 0.9) + ' q' + (pw * 0.2) + ' -' + (ph * 0.5) + ' ' + (pw * 0.42) + ' 0" fill="none" stroke="#8F8878" stroke-width="3"/>';
        out += '<circle cx="' + (x + pw * 0.27) + '" cy="' + (y + ph * 0.42) + '" r="' + (ph * 0.1) + '" fill="#EDE8DE" stroke="#8F8878" stroke-width="1.2"/>';
      }
    });
    out += '</svg>';
    return out;
  }

  /* ---------------------------------------------------------------------------
     3. 全局状态
     ------------------------------------------------------------------------ */
  var S = {
    space: 'studio',
    page: 7,
    region: 1,
    inspTab: 'text',
    filmExpanded: false,
    inspOpen: true,       // 检查器展开（>0 时显示面板）
    bandExpanded: false,
    state: '',
    theme: document.documentElement.getAttribute('data-theme') || 'dark',
    libChapter: 12,
    consoleSection: 'queue',
    cmdIndex: 0,
    cmdItems: []
  };

  /* ---------------------------------------------------------------------------
     4. 渲染 · 顶带
     ------------------------------------------------------------------------ */
  function renderCrumb() {
    var el = $('#crumb');
    el.innerHTML =
      '<button class="crumb-item" data-goto-space="library">' + esc(BOOK.title) + '</button>' +
      '<span class="crumb-sep">' + ico('chevron-right', 'ico--sm') + '</span>' +
      '<button class="crumb-item" data-goto-space="library">第 12 话 · 雨の停車場</button>' +
      '<span class="crumb-sep">' + ico('chevron-right', 'ico--sm') + '</span>' +
      '<span class="crumb-item crumb-item--file">' + pad(S.page) + '.jpg</span>';
  }

  function renderScope() {
    $('#scopeText').textContent = '本章 23 页';
    var menu = $('#scopeMenu');
    menu.innerHTML = [
      ['本章 23 页', 'chapter', true],
      ['当前页 1 页', 'page', false],
      ['当前 Region 1 个', 'region', false],
      ['选中 5 页', 'selection', false]
    ].map(function (r) {
      return '<button class="menu-item' + (r[2] ? ' is-on' : '') + '" data-scope="' + r[1] + '">' + r[0] + '</button>';
    }).join('');
  }

  /* ---------------------------------------------------------------------------
     5. 渲染 · 胶片条
     ------------------------------------------------------------------------ */
  function renderFilm() {
    var list = $('#filmList');
    list.innerHTML = PAGES.map(function (p) {
      var cur = p.no === S.page ? ' is-current' : '';
      return '<li class="film' + cur + '" data-page="' + p.no + '" tabindex="-1">' +
        '<span class="film-thumb">' + pageArt(p.no, { thumbs: true }) + '</span>' +
        '<span class="film-foot">' +
          '<span class="film-no">' + pad(p.no) + '</span>' + mark(p.status) +
        '</span>' +
        (S.filmExpanded ? '<span class="film-name">' + esc(p.file) + '</span>' : '') +
        (p.err ? '<span class="film-flag" title="' + esc(p.err) + '">' + ico('warn', 'ico--sm') + '</span>' : '') +
      '</li>';
    }).join('');
    var strip = $('#filmStrip');
    if (strip) {
      strip.classList.toggle('is-split', S.filmExpanded);
      strip.style.width = S.filmExpanded ? '200px' : '';
    }
    var studio = $('#space-studio');
    if (studio) studio.setAttribute('data-film', S.filmExpanded ? 'open' : 'collapsed');
    $('#filmMeta').textContent = S.filmExpanded ? '23 页 · 完成 18' : '';
  }

  /* ---------------------------------------------------------------------------
     6. 渲染 · 画布
     ------------------------------------------------------------------------ */
  function renderStage() {
    var page = PAGES[S.page - 1] || PAGES[6];
    $('#vpPageChip').innerHTML = ico('page', 'ico--sm') + '<span class="vpchip' + (page.status === 'fail' ? ' is-fail' : '') + '">' + pad(S.page) + '.jpg</span>' +
      '<span class="pill pill--state">' + statusLabel(page.status) + '</span>';

    $('#vpViewSeg').innerHTML = [
      ['page', '页面'], ['result', '成品'], ['split', '分屏']
    ].map(function (v) {
      return '<button class="segbtn' + (S.view === v[0] ? ' is-on' : '') + '" data-view="' + v[0] + '">' + v[1] + '</button>';
    }).join('');

    $('#vpZoom').innerHTML = '<button class="icobtn icobtn--sm" data-zoom="out" title="缩小">' + ico('zoom-out', 'ico--sm') + '</button>' +
      '<span class="track-meta">86%</span>' +
      '<button class="icobtn icobtn--sm" data-zoom="in" title="放大">' + ico('zoom-in', 'ico--sm') + '</button>' +
      '<button class="icobtn icobtn--sm" data-zoom="fit" title="适应窗口 F">' + ico('corner', 'ico--sm') + '</button>';

    $('#vpTracks').innerHTML = '<button class="trackchip' + (S.tracks === 'on' ? ' is-on' : '') + '" data-tracks="1" title="显示可收纳轨道">' + ico('layers', 'ico--sm') + '四轨</button>';

    var stage = $('#stage');
    var showRegions = S.state !== 'no-regions';
    var html = '<div class="pagelayer" style="position:relative;height:100%;aspect-ratio:2/3;max-height:100%;max-width:100%">' +
      '<div style="position:absolute;inset:0">' +
        pageArt(S.page) +
        '<div class="regionlayer">' +
          (showRegions ? REGIONS.map(function (r) {
            var sel = (r.no === S.region) ? ' is-sel' : '';
            var hasErr = (S.state === 'partial-region' && r.no === 3);
            return '<button class="rg' + sel + (hasErr ? ' is-err' : '') + '" data-region="' + r.no + '" ' +
              'style="left:' + r.x + '%;top:' + r.y + '%;width:' + r.w + '%;height:' + r.h + '%" ' +
              'title="' + r.type + ' · ' + esc(r.jp) + '">' +
              '<span class="rg-tagline">' + r.no + ' ' + r.type + (r.lock ? ' ' + (r.lock === 'translation' ? '译锁' : '区锁') : '') + '</span>' +
            '</button>';
          }).join('') : '') +
        '</div>' +
        hudHTML() +
      '</div>' +
    '</div>';
    stage.innerHTML = html;

    var rail = $('#reviewRail');
    if (S.state === 'stale') {
      rail.hidden = false;
      rail.innerHTML = '<span class="reviewrail-label">stale</span><span>渲染结果因上游几何变更而过期（Region 1 尺寸已改）</span><span class="reviewrail-spacer"></span><button class="btn btn--sm" data-act="rerender">重跑过期项</button>';
    } else if (page.status === 'fail') {
      rail.hidden = false;
      rail.innerHTML = '<span class="reviewrail-label" style="color:var(--c-danger)">失败</span><span>' + esc(page.err) + ' · 翻译被限流，2 次重试后停止</span><span class="reviewrail-spacer"></span><button class="btn btn--sm" data-act="retry-fail">只重试失败</button>';
    } else if (S.state === 'review-queue') {
      rail.hidden = false;
      rail.innerHTML = '<span class="reviewrail-label">待确认 3</span><span>第 017 页 · 3 条 needs_review 待逐条确认（本章共 3 条）</span><span class="reviewrail-spacer"></span><button class="btn btn--sm" data-act="next-review">下一条待确认</button>';
    } else {
      rail.hidden = true;
      rail.innerHTML = '';
    }
  }

  function hudHTML() {
    if (S.state === 'no-regions') return '';
    var r = REGIONS.filter(function (x) { return x.no === S.region; })[0] || REGIONS[0];
    var slots = [
      ['n', 'check', '确认 Enter'], ['ne', 'retry', '重渲染 Shift+Enter'],
      ['e', 'text', '编辑译文 E'], ['se', 'history', '版本历史'],
      ['s', 'lock', '锁定 L'], ['sw', 'spark', '重跑全链路'],
      ['w', 'text', '编辑原文 O'], ['nw', 'more', '更多动作']
    ];
    return '<div class="hud" style="position:absolute;left:' + r.x + '%;top:' + r.y + '%;width:' + r.w + '%;height:' + r.h + '%;pointer-events:none">' +
      slots.map(function (s) {
        return '<button class="hud-slot hud-slot--' + s[0] + '" data-hud="' + s[1] + '" title="' + s[2] + '" style="pointer-events:auto">' + ico(s[1], 'ico--sm') + '</button>';
      }).join('') +
      '<span class="hud-corner hud-corner--tl"></span><span class="hud-corner hud-corner--tr"></span>' +
      '<span class="hud-corner hud-corner--bl"></span><span class="hud-corner hud-corner--br"></span>' +
      '<span class="hud-info">' + r.type + ' · #' + r.no + '</span>' +
    '</div>';
  }

  /* ---------------------------------------------------------------------------
     7. 渲染 · 检查器
     ------------------------------------------------------------------------ */
  var INSP_TABS = [
    ['text', 'text', '文本'], ['style', 'type', '样式'], ['inpaint', 'layers', '修复'],
    ['lock', 'lock', '锁定'], ['history', 'history', '历史']
  ];

  function renderInspector() {
    var studio = $('#space-studio');
    if (studio) studio.setAttribute('data-insp', S.inspOpen ? 'open' : 'collapsed');
    $('#inspRail').innerHTML = INSP_TABS.map(function (t) {
      return '<button class="insp-tab' + (S.inspTab === t[0] ? ' is-on' : '') + '" data-insp="' + t[0] + '" title="' + t[2] + '">' + ico(t[1], 'ico--sm') + '</button>';
    }).join('') + '<span class="insp-rail-sep"></span>' +
      '<button class="insp-tab" data-insp-toggle="1" title="展开 / 收起检查器">' + ico(S.inspOpen ? 'panel-right' : 'panel-right', 'ico--sm') + '</button>';

    var r = REGIONS.filter(function (x) { return x.no === S.region; })[0] || REGIONS[0];
    var body = '';
    if (!S.inspOpen) { $('#inspPane').innerHTML = ''; return; }

    if (S.inspTab === 'text') {
      body = '<div class="ip-head">Region ' + r.no + ' · ' + r.type + '</div>' +
        '<div class="ip"><div class="ip-head">原文（OCR）</div>' +
          '<div class="txtbox txtbox--jp' + (S.state === 'partial-region' ? '' : '') + '">' + esc(r.jp) + '</div>' +
          '<div class="txtmeta">置信度 0.94 · 竖排 · 来源 detect#12/ocr#7</div></div>' +
        '<div class="ip"><div class="ip-head">机器译文</div>' +
          '<div class="txtbox txtbox--ro">' + esc(r.mt) + '</div>' +
          '<div class="txtmeta">deepseek-v3 · r4 · 14:05</div></div>' +
        '<div class="ip"><div class="ip-head">人工译文</div>' +
          (S.state === 'partial-region' && r.no === 3
            ? '<div class="pill pill--err">翻译失败 · ProviderRateLimitError</div><div class="txtmeta">OCR 已完成，翻译未产出；可换 Provider 后重试</div>'
            : '<div class="txtbox txtbox--edit">' + esc(r.et || r.mt) + '</div>') +
          '</div>' +
        '<div class="ip"><div class="ip-head">审阅</div>' +
          '<div class="kv"><span>review_state</span><span class="mono">' + r.state + '</span></div>' +
          '<div class="kv"><span>final_translation</span><span class="mono">' + esc(r.et || r.mt) + '</span></div>' +
        '</div>' +
        '<div class="insp-actions"><button class="btn btn--accent btn--sm" data-act="confirm">' + ico('check', 'ico--sm') + '确认 Enter</button>' +
        '<button class="btn btn--sm" data-act="rerender">重渲染</button>' +
        '<button class="btn btn--ghost btn--sm" data-act="history">历史</button></div>';
    } else if (S.inspTab === 'style') {
      body = '<div class="ip-head">排版样式 · Region ' + r.no + '</div>' +
        '<div class="ip"><div class="ip-head">字号</div>' +
          '<div class="kv"><span>自动基准</span><span class="mono">22.0 px</span></div>' +
          '<div class="kv"><span>人工偏移</span><span class="mono">+1 px</span></div>' +
          '<div class="kv"><span>溢出策略</span><span class="mono">shrink</span></div></div>' +
        '<div class="ip"><div class="ip-head">颜色</div>' +
          '<div class="kv"><span>文字色</span><span class="mono">#141414</span></div>' +
          '<div class="kv"><span>来源</span><span class="mono">color step · 0.88</span></div></div>' +
        '<div class="insp-actions"><button class="btn btn--sm" data-act="rerender">应用并重渲染</button></div>';
    } else if (S.inspTab === 'inpaint') {
      body = '<div class="ip-head">修复 · Region ' + r.no + '</div>' +
        '<div class="ip"><div class="trackgrid">' +
          '<div class="trackcell"><span>Mask 面积</span><span>6.2%</span></div>' +
          '<div class="trackcell"><span>路线</span><span>anime_lama_v2</span></div>' +
          '<div class="trackcell"><span>背景</span><span>线稿</span></div>' +
          '<div class="trackcell"><span>耗时</span><span>1.8s</span></div>' +
        '</div></div>' +
        '<div class="ip"><div class="ip-head">选项</div>' +
          '<div class="kv"><span>inpaint_locked</span><span class="mono">' + (r.lock ? 'true' : 'false') + '</span></div></div>' +
        '<div class="insp-actions"><button class="btn btn--sm" data-act="reinpaint">重新修复</button>' +
        '<button class="btn btn--ghost btn--sm">切换路线</button></div>';
    } else if (S.inspTab === 'lock') {
      body = '<div class="ip-head">锁定 · Region ' + r.no + '</div>' +
        '<div class="ip"><div class="kv"><span>Region Lock</span><span class="mono">' + (r.lock === 'region' ? 'ON' : 'off') + '</span></div>' +
        '<div class="kv"><span>Translation Lock</span><span class="mono">' + (r.lock === 'translation' ? 'ON（人工编辑）' : 'off') + '</span></div>' +
        '<div class="kv"><span>Inpaint Lock</span><span class="mono">off</span></div>' +
        '<div class="kv"><span>Page Lock</span><span class="mono">off</span></div></div>' +
        '<div class="hint">人工修改译文后会自动加 Translation Lock，自动流程不再覆盖。</div>' +
        '<div class="insp-actions"><button class="btn btn--sm" data-act="toggle-lock">' + (r.lock ? '解除锁定' : '加锁') + '</button></div>';
    } else {
      body = '<div class="ip-head">版本历史 · Region ' + r.no + '</div>' +
        '<div class="rail-ledger">' +
          [['r5', '14:22', '人工', '译文改为「这场雨，恐怕要下三天」', 'is-cur'],
           ['r4', '14:05', 'pipeline', 'translate 覆盖（machine）', ''],
           ['r3', '13:58', '人工', '字号 +1，溢出 shrink', ''],
           ['r2', '13:40', 'pipeline', 'inpaint 完成（anime_lama_v2）', ''],
           ['r1', '13:31', 'pipeline', 'OCR 初识别', '']].map(function (v) {
            return '<div class="rev ' + v[4] + '"><span class="rev-id">' + v[0] + '</span><span class="rev-time">' + v[1] + '</span>' +
              '<span class="rev-src">' + v[2] + '</span><span class="rev-desc">' + v[3] + '</span></div>';
          }).join('') +
        '</div>' +
        '<div class="hint">恢复旧版本会新建 current 指针；下游 render 可能再次 stale。</div>';
    }
    $('#inspPane').innerHTML = body;
  }

  /* ---------------------------------------------------------------------------
     8. 渲染 · 流水线带
     ------------------------------------------------------------------------ */
  function renderPipeline() {
    var pipe = $('#pipeline');
    var page = PAGES[S.page - 1];
    var globalState = S.state === 'running' || S.state === 'paused' || S.state === 'completed-with-failures' ? S.state : 'running';
    var runStatus = { running: 'running', paused: 'paused', 'completed-with-failures': 'completed_with_failures' }[globalState] || 'running';
    var pct = globalState === 'completed-with-failures' ? 100 : (globalState === 'paused' ? 62 : RUN.pct);

    var steps = STEPS.map(function (s) {
      var st = STAGE_STATE[s.key] || 'todo';
      if (S.state === 'stale' && (s.key === 'render' || s.key === 'save')) st = 'stale';
      var cls = st === 'ok' ? '' : (st === 'stale' ? ' is-stale' : (st === 'fail' ? ' is-err' : ''));
      var ch = st === 'ok' ? '●' : (st === 'stale' ? '▨' : (st === 'fail' ? '✗' : '○'));
      if (globalState === 'running' && s.key === 'translate' && S.state !== 'stale') { cls = ' is-run'; ch = '◐'; }
      return '<button class="bstep' + cls + '" data-step="' + s.key + '"><span>' + ch + '</span><span class="bstep-name">' + s.name + '</span></button>';
    }).join('');

    var bandCls = globalState === 'paused' ? 'is-paused' : (globalState === 'completed-with-failures' ? 'is-err' : 'is-run');
    pipe.classList.remove('is-paused', 'is-blocked', 'is-run', 'is-err');
    pipe.classList.add(bandCls);
    var studio = $('#space-studio');
    if (studio) studio.setAttribute('data-band', S.bandExpanded ? 'open' : 'collapsed');

    var html = '<div class="band-row">' +
      '<div class="band-steps">' + steps + '</div>' +
      '<span class="band-sep"></span>' +
      '<div class="band-now">' +
        '<b>' + pad(S.page) + '.jpg</b>' +
        '<span>· 翻译 · step 5/10</span>' +
      '</div>' +
      '<div class="band-progress"><span class="band-bar"><i style="width:' + pct + '%"></i></span><span>' + pct + '%</span></div>' +
      '<div class="band-counts">完成 <b>' + (globalState === 'completed-with-failures' ? 21 : RUN.counts.ok) + '</b> · 失败 <b>' + RUN.counts.fail + '</b></div>' +
      '<span class="band-spacer"></span>' +
      '<div class="band-actions">' +
        (globalState === 'paused'
          ? '<button class="btn btn--sm" data-run="resume">继续</button>'
          : '<button class="btn btn--sm" data-run="pause">暂停</button>') +
        (globalState === 'completed-with-failures'
          ? '<button class="btn btn--sm" data-act="retry-fail">只重试失败</button>'
          : '<button class="btn btn--ghost btn--sm" data-run="stop">停止</button>') +
      '</div>' +
      '<button class="band-toggle" data-band-toggle="1" title="展开任务面板">' + ico(S.bandExpanded ? 'chevron-down' : 'chevron-up', 'ico--sm') + '任务</button>' +
    '</div>';

    if (S.bandExpanded) {
      html += '<div class="taskpanel">' +
        '<div class="tp-head"><span class="mono">Run #' + RUN.id + '</span><span class="t-dim">' + RUN.cmd + ' · 第 12 话 · 23 页</span>' +
        '<span class="band-spacer"></span><span class="pill pill--state">' + runStatus + '</span></div>' +
        '<div class="tp-body">' +
          '<div class="tp-col"><div class="up">页状态</div><div class="pgrid">' +
            PAGES.slice(0, 24).map(function (p) {
              return '<button class="pcell-sm" data-page="' + p.no + '" title="' + pad(p.no) + ' · ' + statusLabel(p.status) + '">' + mark(p.status) + '</button>';
            }).join('') + '</div></div>' +
          '<div class="tp-col"><div class="up">失败聚合</div>' +
            '<div class="aggrow"><span>ProviderRateLimitError</span><span class="num">1</span></div>' +
            '<div class="aggrow"><span>ModelLoadError</span><span class="num">1</span></div>' +
            '<div class="hint">改配置后可批量重试这 2 个单元，无需整章重跑。</div></div>' +
        '</div>' +
      '</div>';
    }
    pipe.innerHTML = html;
  }

  function statusLabel(st) {
    return { ok: '已完成', review: '待确认', fail: '失败', stale: '过期', run: '处理中', todo: '未处理' }[st] || st;
  }

  /* ---------------------------------------------------------------------------
     9. 渲染 · 资料柜
     ------------------------------------------------------------------------ */
  function renderLibrary() {
    $('#libStat').textContent = '4 个作品 · 92 章 · 2 个待处理';
    $('#chapterMeta').textContent = '第 12 话 · 23 页';
    $('#pagesMeta').textContent = '完成 18 · 失败 2 · 过期 1';
    $('#pagesTitle').textContent = '第 12 话 · 雨の停車場';

    var works = [
      { t: '夜光列车', m: '日漫 · 日→中 · 14 话', s: '处理中', x: 1 },
      { t: '雨の停車場', m: '日漫 · 日→中 · 单话', s: '待处理', x: 0 },
      { t: '汉江之夜', m: '韩漫 Webtoon · 韩→中 · 60 话', s: '待处理', x: 0 },
      { t: '旧校舍的夏天', m: '日漫 · 日→中 · 8 话', s: '已完成', x: 0 }
    ];
    $('#shelf').innerHTML = works.map(function (w, i) {
      var cur = i === 0 ? ' is-current' : '';
      return '<button class="work' + cur + '" data-book="' + i + '">' +
        '<span class="work-cover">' + pageArt(3 + i, { thumbs: true }) + '</span>' +
        '<span class="work-main"><span class="work-title">' + esc(w.t) + '</span>' +
        '<span class="work-meta">' + esc(w.m) + '</span>' +
        '<span class="work-stat">' + esc(w.s) + '</span></span></button>';
    }).join('');

    var chapters = [
      { no: 10, name: '第 10 话 · 灯を消すな', pages: 21, st: 'ok' },
      { no: 11, name: '第 11 话 · 始発', pages: 20, st: 'ok' },
      { no: 12, name: '第 12 话 · 雨の停車場', pages: 23, st: 'review' },
      { no: 13, name: '第 13 话 · 車掌の記憶', pages: 0, st: 'todo' },
      { no: 14, name: '第 14 话 · 終着', pages: 0, st: 'todo' }
    ];
    $('#chapterTable').innerHTML =
      '<thead><tr><th class="c-pages">话</th><th>标题</th><th class="c-pages ta-r">页数</th><th class="c-state">状态</th></tr></thead><tbody>' +
      chapters.map(function (c) {
        var cur = c.no === S.libChapter ? ' is-cur' : '';
        return '<tr class="' + cur + '" data-chapter="' + c.no + '"><td class="c-pages mono">' + String(c.no).padStart(2, '0') + '</td>' +
          '<td class="t-main">' + esc(c.name) + '</td><td class="c-pages t-num ta-r">' + (c.pages || '—') + '</td>' +
          '<td class="c-state">' + mark(c.st) + '</td></tr>';
      }).join('') + '</tbody>';

    renderPageSheet();
  }

  function renderPageSheet() {
    var sheet = $('#pageSheet');
    if (S.state === 'no-pages') {
      sheet.innerHTML = '<div class="sheet-empty">' + ico('page') + '<div>第 13 话还没有页面</div>' +
        '<div class="hint">拖入文件夹或选择图片；识别为本章页序，不清空现有数据。</div>' +
        '<button class="btn btn--accent btn--sm">' + ico('import', 'ico--sm') + '导入页面</button></div>';
      return;
    }
    sheet.innerHTML = '<div class="pgrid" style="grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:var(--sp2)">' +
      PAGES.map(function (p) {
        var cur = p.no === S.page ? ' is-current' : '';
        return '<button class="pcell' + cur + '" data-page="' + p.no + '" title="' + esc(p.file) + ' · ' + statusLabel(p.status) + '">' +
          '<span class="pcell-thumb">' + pageArt(p.no, { thumbs: true }) + '</span>' +
          '<span class="pcell-foot"><span class="pcell-no">' + pad(p.no) + '</span>' +
            (p.err ? '<span class="pcell-badge pcell-badge--err" title="' + esc(p.err) + '">!</span>' : '') +
            (p.status === 'stale' ? '<span class="pcell-badge pcell-badge--stale" title="stale">▨</span>' : '') +
            (p.status === 'review' ? '<span class="pcell-badge pcell-badge--warn" title="待确认">●</span>' : '') +
          '</span></button>';
      }).join('') + '</div>';
  }

  /* ---------------------------------------------------------------------------
     10. 渲染 · 控制台
     ------------------------------------------------------------------------ */
  function renderConsole() {
    $('#consoleIndex').innerHTML = CONSOLE_SECTIONS.map(function (s) {
      return '<button class="cindex-item' + (S.consoleSection === s.id ? ' is-on' : '') + '" data-console="' + s.id + '">' +
        ico(s.icon, 'ico--sm') + '<span>' + s.name + '</span><span class="cindex-count">' + s.count + '</span></button>';
    }).join('');

    var panes = {
      queue: '<div class="cp-head"><span class="cp-title">任务队列</span><span class="t-dim">3 个 Run · 1 运行中</span></div>' +
        '<div class="cp-sect"><div class="cp-sect-head">运行中</div>' +
        '<div class="setrow"><span class="mono">R-8831</span><span>translate_untranslated · 第12话</span><span class="up">62%</span></div></div>' +
        '<div class="cp-sect"><div class="cp-sect-head">最近</div>' +
        '<div class="setrow"><span class="mono">R-8830</span><span>reinpaint_selected · 第11话 5 页</span><span class="up">完成</span></div>' +
        '<div class="setrow"><span class="mono">R-8829</span><span>rerender_all · 第10话</span><span class="up">完成（1 失败）</span></div>' +
        '<div class="setrow"><span class="mono">R-8828</span><span>translate_all · 第9话</span><span class="up">阻塞</span></div>' +
        '<div class="setrow"><span class="mono">R-8827</span><span>translate_all · 第8话</span><span class="up">已中断</span></div></div>',
      provider: '<div class="cp-head"><span class="cp-title">Provider 与凭据</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>翻译</span><span class="mono">deepseek-v3</span><span class="up">已连通</span></div>' +
        '<div class="setrow"><span>识别</span><span class="mono">manga_ocr</span><span class="up">本地</span></div>' +
        '<div class="setrow"><span>修复</span><span class="mono">anime_lama_v2</span><span class="up">本地</span></div>' +
        '<div class="setrow"><span>凭据</span><span class="mono">sk-****9f2c</span><span class="up">已保存</span></div></div>',
      network: '<div class="cp-head"><span class="cp-title">网络代理</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>模式</span><span class="mono">HTTP 代理</span></div>' +
        '<div class="setrow"><span>地址</span><span class="mono">socks5://127.0.0.1:1080</span></div>' +
        '<div class="setrow"><span>Provider 覆盖</span><span class="mono">deepseek-v3 → 直连</span></div>' +
        '<div class="setrow"><span>最近测试</span><span class="up">成功 · 46ms</span></div></div>',
      model: '<div class="cp-head"><span class="cp-title">模型与设备</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>设备</span><span class="mono">CUDA 0 · RTX 4070</span></div>' +
        '<div class="setrow"><span>并发</span><span class="mono">翻译 4 · 修复 1 · 网络 8</span></div>' +
        '<div class="setrow"><span>缺失</span><span class="mono">anime_lama_v2 权重</span><span class="up">需安装</span></div></div>',
      cache: '<div class="cp-head"><span class="cp-title">缓存与版本</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>ArtifactRevision</span><span class="mono">2.1 GiB / 8 GiB</span></div>' +
        '<div class="meter"><span class="meter-bar" style="width:26%"></span></div>' +
        '<div class="setrow"><span>保留策略</span><span class="mono">30 天</span></div></div>',
      backup: '<div class="cp-head"><span class="cp-title">备份 .nmbak</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>最近</span><span class="mono">2026-10-24 22:10</span><span class="up">3 份</span></div>' +
        '<div class="setrow"><span>大小</span><span class="mono">184 MiB</span></div></div>',
      plugin: '<div class="cp-head"><span class="cp-title">插件与 Hooks</span></div>' +
        '<div class="cp-sect"><div class="setrow"><span>glossary-sync</span><span class="up">启用</span></div>' +
        '<div class="setrow"><span>batch-rename</span><span class="up">启用</span></div>' +
        '<div class="setrow"><span>legacy-exporter</span><span class="up">停用</span></div></div>'
    };
    $('#consolePane').innerHTML = panes[S.consoleSection] || panes.queue;
  }

  /* ---------------------------------------------------------------------------
     11. 渲染 · 状态面板 & 命令面板
     ------------------------------------------------------------------------ */
  function renderStates() {
    $('#stateList').innerHTML = STATES.map(function (s, i) {
      var on = S.state === s.id ? ' is-on' : '';
      return '<button class="state-row' + on + '" data-state="' + s.id + '">' +
        '<span class="state-no">' + (s.no || (i + 1)) + '</span>' +
        '<span class="state-main"><span class="state-name">' + s.name + '</span>' +
        '<span class="state-desc">' + s.desc + '</span></span>' +
        '<span class="state-where">' + s.where + '</span></button>';
    }).join('');
    $('#stateBadge').textContent = '12';
  }

  function renderCmd(q) {
    q = (q || '').toLowerCase();
    var items = COMMANDS.filter(function (c) { return !q || c.name.toLowerCase().indexOf(q) >= 0 || c.scope.toLowerCase().indexOf(q) >= 0; });
    S.cmdItems = items;
    if (S.cmdIndex >= items.length) S.cmdIndex = 0;
    $('#cmdList').innerHTML = items.length ? items.map(function (c, i) {
      return '<button class="cmd-item' + (i === S.cmdIndex ? ' is-focus' : '') + '" data-cmd="' + i + '">' +
        ico(c.icon, 'ico--sm') +
        '<span class="cmd-item-name">' + esc(c.name) + '</span>' +
        '<span class="cmd-scope-tag">' + esc(c.scope) + '</span>' +
        (c.key ? '<kbd class="kbd">' + esc(c.key) + '</kbd>' : '') +
      '</button>';
    }).join('') : '<div class="hint" style="padding:12px">没有匹配的命令</div>';
    $('#cmdScope').textContent = '作用域 · 本章 23 页';
  }

  /* ---------------------------------------------------------------------------
     12. 模态 / 横幅
     ------------------------------------------------------------------------ */
  function openModal(title, bodyHTML, choices, tone) {
    var m = $('#modal');
    m.className = 'modal';
    m.innerHTML = '<div class="modal-head modal-head--' + (tone || 'info') + '"><span class="modal-title">' + title + '</span>' +
      '<button class="icobtn icobtn--sm" data-modal-close="1">' + ico('close', 'ico--sm') + '</button></div>' +
      '<div class="modal-body">' + bodyHTML + '</div>' +
      '<div class="modal-foot">' + choices.map(function (c, i) {
        return '<button class="btn ' + (i === 0 ? 'btn--accent' : 'btn--ghost') + '" data-modal-choice="' + i + '">' + c + '</button>';
      }).join('') + '</div>';
    m.hidden = false; $('#modalScrim').hidden = false;
  }
  function closeModal() { $('#modal').hidden = true; $('#modalScrim').hidden = true; }

  function renderBanner() {
    var slot = $('#bannerSlot');
    if (S.state === 'blocked') {
      slot.hidden = false;
      slot.innerHTML = '<div class="banner banner--danger"><span class="banner-desc"><strong>任务阻塞</strong> · Provider 认证失效（deepseek-v3），受影响 23 页。数据未损坏，修复后可直接恢复。</span>' +
        '<span class="banner-spacer"></span><div class="banner-actions"><button class="btn btn--sm" data-act="fix-provider">修复配置</button>' +
        '<button class="btn btn--ghost btn--sm" data-act="resume-run">恢复队列</button></div></div>';
    } else if (S.state === 'stale') {
      slot.hidden = false;
      slot.innerHTML = '<div class="banner banner--stale"><span class="banner-desc">Region 1 几何已改，4 项下游结果过期（render / save）。历史版本保留。</span>' +
        '<span class="banner-spacer"></span><div class="banner-actions"><button class="btn btn--sm" data-act="rerender">重跑过期项</button></div></div>';
    } else {
      slot.hidden = true; slot.innerHTML = '';
    }
  }

  /* ---------------------------------------------------------------------------
     13. 状态应用
     ------------------------------------------------------------------------ */
  function applyState(id) {
    S.state = id || '';
    if (S.state === 'empty') { S.space = 'library'; }
    else if (S.state === 'no-pages' || S.state === 'importing' || S.state === 'import-partial') { S.space = 'library'; }
    else if (S.state === 'interrupted') { S.space = 'studio'; }
    else if (S.state === 'review-queue' || S.state === 'danger-confirm') { S.space = 'studio'; }
    else { if (S.space !== 'console') S.space = 'studio'; }

    if (S.state === 'empty') {
      $('#shelf').innerHTML = '<div class="empty-workspace"><div class="ew-title">还没有作品</div>' +
        '<div class="ew-desc">数据根：<span class="mono">%APPDATA%\\NewManga\\library</span></div>' +
        '<div class="ew-facts"><span class="ew-fact">导入不会修改你的原始文件</span><span class="ew-fact">所有修改保存在 Managed Copy</span></div>' +
        '<div class="ew-actions"><button class="btn btn--accent">' + ico('import', 'ico--sm') + '导入文件夹</button>' +
        '<button class="btn">导入文件</button><button class="btn btn--ghost">打开设置</button></div></div>';
      $('#chapterTable').innerHTML = '';
      $('#pageSheet').innerHTML = '';
    } else {
      renderLibrary();
    }

    if (S.state === 'importing' || S.state === 'import-partial') {
      var dock = $('#importDock');
      dock.hidden = false;
      var rows = S.state === 'importing'
        ? [['第12话 · 23 页', 'run'], ['第13话 · 0 页', 'run'], ['封面.jpg', 'ok']]
        : [['第12话 · 23 页', 'ok'], ['第13话 · 18 页', 'ok'], ['cover.cbz', 'skip'], ['broken.png', 'skip']];
      dock.innerHTML = '<div class="import-head"><span>导入</span><span class="up">' + (S.state === 'importing' ? '进行中 · 2/3' : '完成 · 2 项跳过') + '</span></div>' +
        '<div class="import-list">' + rows.map(function (r) {
          return '<div class="import-row"><span class="mono">' + r[0] + '</span>' + mark(r[1]) + '</div>';
        }).join('') + '</div>';
    } else { $('#importDock').hidden = true; }

    if (S.state === 'interrupted') {
      openModal('上次任务被中断', '<div class="modal-impact">Run <span class="mono">#R-8827</span> 在 <span class="mono">translate_all · 第8话</span> 期间异常退出。已完成 14 页的成果与 Revision 均已保留。</div>' +
        '<div class="modal-choice-list"><div class="modal-choice"><strong>继续</strong><span>从断点恢复，不重跑已完成步骤</span></div>' +
        '<div class="modal-choice"><strong>重新开始</strong><span>丢弃本 Run 的未完成单元，从头跑</span></div>' +
        '<div class="modal-choice"><strong>放弃</strong><span>保留已有成果，把 Run 标记结束</span></div></div>', ['继续（推荐）', '重新开始', '放弃'], 'warn');
    } else if (S.state === 'danger-confirm') {
      openModal('覆盖 2 条人工译文？', '<div class="modal-impact">Region 2 与 Region 5 存在人工译文且已 <span class="mono">translation_locked</span>。继续将使 2 条人工成果被机器译文覆盖，<strong>不可撤销</strong>（但旧 Revision 仍可在历史中恢复）。</div>', ['取消', '仍要覆盖'], 'warn');
    } else { closeModal(); }

    renderCrumb(); renderFilm(); renderStage(); renderInspector(); renderPipeline(); renderConsole(); renderStates(); renderBanner();
    if (S.state === 'empty') renderCrumb();
  }

  /* ---------------------------------------------------------------------------
     14. 空间切换
     ------------------------------------------------------------------------ */
  function goSpace(name) {
    S.space = name;
    $$('.space').forEach(function (el) { el.hidden = true; });
    var el = $('#space-' + name);
    if (el) el.hidden = false;
    $$('.spacetab').forEach(function (b) { b.classList.toggle('is-on', b.getAttribute('data-goto-space') === name); });
    if (name === 'library') renderLibrary();
    if (name === 'console') renderConsole();
  }

  /* ---------------------------------------------------------------------------
     15. 交互绑定（事件委托）
     ------------------------------------------------------------------------ */
  function bind() {
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('button, [data-goto-space]');
      if (!t) return;

      if (t.hasAttribute('data-goto-space')) { goSpace(t.getAttribute('data-goto-space')); return; }
      if (t.hasAttribute('data-page')) { S.page = +t.getAttribute('data-page'); renderFilm(); renderStage(); renderPipeline(); renderCrumb(); return; }
      if (t.hasAttribute('data-region')) { S.region = +t.getAttribute('data-region'); renderStage(); renderInspector(); return; }
      if (t.hasAttribute('data-insp')) { S.inspTab = t.getAttribute('data-insp'); S.inspOpen = true; renderInspector(); return; }
      if (t.hasAttribute('data-insp-toggle')) { S.inspOpen = !S.inspOpen; renderInspector(); return; }
      if (t.hasAttribute('data-console')) { S.consoleSection = t.getAttribute('data-console'); renderConsole(); return; }
      if (t.hasAttribute('data-state')) { applyState(t.getAttribute('data-state')); return; }
      if (t.hasAttribute('data-chapter')) { S.libChapter = +t.getAttribute('data-chapter'); renderLibrary(); return; }
      if (t.hasAttribute('data-band-toggle')) { S.bandExpanded = !S.bandExpanded; renderPipeline(); return; }
      if (t.hasAttribute('data-cmd')) { runCmd(+t.getAttribute('data-cmd')); return; }
      if (t.hasAttribute('data-modal-close') || t.id === 'modalScrim') { closeModal(); return; }

      if (t.hasAttribute('data-act')) {
        var a = t.getAttribute('data-act');
        if (a === 'confirm') { confirmRegion(); }
        else if (a === 'rerender') { openModal('重跑过期项？', '<div class="modal-impact">将重跑 <span class="mono">4</span> 个过期单元（render / save），不影响已确认译文。</div>', ['开始重跑', '取消'], 'warn'); }
        else if (a === 'retry-fail') { openModal('只重试失败单元？', '<div class="modal-impact">2 个失败页：<span class="mono">ProviderRateLimitError</span> ×1、<span class="mono">ModelLoadError</span> ×1。已成功成果不受影响。</div>', ['重试这 2 个', '取消'], 'warn'); }
        else if (a === 'toggle-lock') { var r = REGIONS[S.region - 1]; r.lock = r.lock ? '' : 'translation'; renderInspector(); renderStage(); }
        else if (a === 'fix-provider') { goSpace('console'); S.consoleSection = 'provider'; renderConsole(); }
        else if (a === 'resume-run') { applyState('running'); }
        else if (a === 'reinpaint') { openModal('重新修复 Region 3？', '<div class="modal-impact">将使用 <span class="mono">anime_lama_v2</span> 重新生成 clean artifact，并使 render 过期。译文不受影响。</div>', ['重新修复', '取消'], 'info'); }
        else if (a === 'history') { S.inspTab = 'history'; S.inspOpen = true; renderInspector(); }
        return;
      }
      if (t.hasAttribute('data-run')) {
        var act = t.getAttribute('data-run');
        if (act === 'pause') applyState('paused');
        else if (act === 'resume') applyState('running');
        else if (act === 'stop') openModal('停止当前任务？', '<div class="modal-impact">剩余 <span class="mono">2</span> 页不再处理；已完成的 18 页成果与版本全部保留，不回滚。</div>', ['停止', '取消'], 'warn');
        return;
      }
      if (t.hasAttribute('data-hud')) {
        var hk = t.getAttribute('data-hud');
        if (hk === 'check') confirmRegion();
        else if (hk === 'lock') { var rr = REGIONS[S.region - 1]; rr.lock = rr.lock ? '' : 'region'; renderStage(); renderInspector(); }
        else if (hk === 'text') { S.inspTab = 'text'; S.inspOpen = true; renderInspector(); }
        else if (hk === 'history') { S.inspTab = 'history'; S.inspOpen = true; renderInspector(); }
        else if (hk === 'spark') { openModal('重跑当前 Region 全链路？', '<div class="modal-impact">Region ' + S.region + '：OCR → 配色 → 术语 → 翻译 → Mask → 修复 → 渲染。仅作用于该 Region，不修改同页其他 Region。</div>', ['开始', '取消'], 'warn'); }
        else if (hk === 'retry') { S.inspTab = 'style'; S.inspOpen = true; renderInspector(); }
        else if (hk === 'more') { openCmd(); }
        return;
      }
      if (t.id === 'btnCmd') { openCmd(); return; }
      if (t.id === 'btnStates') { var d = $('#stateDrawer'); d.hidden = !d.hidden; return; }
      if (t.id === 'btnStateClose') { $('#stateDrawer').hidden = true; return; }
      if (t.id === 'btnStateReset') { applyState(''); return; }
      if (t.id === 'btnTheme') { toggleTheme(); return; }
      if (t.id === 'btnFilm') { S.filmExpanded = !S.filmExpanded; renderFilm(); return; }
      if (t.id === 'scopeBtn') { var sm = $('#scopeMenu'); sm.hidden = !sm.hidden; return; }
      if (t.hasAttribute('data-scope')) { $('#scopeMenu').hidden = true; $('#scopeText').textContent = t.textContent; return; }
      if (t.hasAttribute('data-view')) { S.view = t.getAttribute('data-view'); renderStage(); return; }
      if (t.hasAttribute('data-zoom')) { return; }
      if (t.hasAttribute('data-step')) { return; }
    });

    $('#cmdInput').addEventListener('input', function (e) { renderCmd(e.target.value); });
    $('#libSearch').addEventListener('input', function () { });
    $('#modalScrim').addEventListener('click', closeModal);

    document.addEventListener('keydown', function (ev) {
      var tag = (ev.target.tagName || '').toLowerCase();
      var typing = tag === 'input' || tag === 'textarea' || ev.target.isContentEditable;

      if (ev.key === 'Escape') {
        if (!$('#cmd').hidden) { closeCmd(); ev.preventDefault(); return; }
        if (!$('#modal').hidden) { closeModal(); ev.preventDefault(); return; }
        if (!$('#stateDrawer').hidden) { $('#stateDrawer').hidden = true; ev.preventDefault(); return; }
        return;
      }
      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') { ev.preventDefault(); openCmd(); return; }
      if (!$('#cmd').hidden) {
        if (ev.key === 'ArrowDown') { ev.preventDefault(); S.cmdIndex = Math.min(S.cmdIndex + 1, S.cmdItems.length - 1); renderCmd($('#cmdInput').value); }
        else if (ev.key === 'ArrowUp') { ev.preventDefault(); S.cmdIndex = Math.max(S.cmdIndex - 1, 0); renderCmd($('#cmdInput').value); }
        else if (ev.key === 'Enter') { ev.preventDefault(); runCmd(S.cmdIndex); }
        return;
      }
      if (typing) return;

      if ((ev.ctrlKey || ev.metaKey) && ['1', '2', '3'].indexOf(ev.key) >= 0) {
        ev.preventDefault(); goSpace(['library', 'studio', 'console'][+ev.key - 1]); return;
      }
      if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && ev.key.toLowerCase() === 'e') { ev.preventDefault(); S.bandExpanded = !S.bandExpanded; renderPipeline(); return; }
      if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') { ev.preventDefault(); confirmAll(); return; }

      if (ev.key === 'j' || ev.key === 'J') { moveRegion(1); ev.preventDefault(); return; }
      if (ev.key === 'k' || ev.key === 'K') { moveRegion(-1); ev.preventDefault(); return; }
      if (ev.key === ']') { nextPage(1); ev.preventDefault(); return; }
      if (ev.key === '[') { nextPage(-1); ev.preventDefault(); return; }
      if (ev.key === 'Enter') { confirmRegion(); ev.preventDefault(); return; }
      if (ev.key.toLowerCase() === 'e') { S.inspTab = 'text'; S.inspOpen = true; renderInspector(); return; }
      if (ev.key.toLowerCase() === 'o') { S.inspTab = 'text'; S.inspOpen = true; renderInspector(); return; }
      if (ev.key.toLowerCase() === 'l') { var r2 = REGIONS[S.region - 1]; r2.lock = r2.lock ? '' : 'region'; renderStage(); renderInspector(); return; }
      if (ev.key.toLowerCase() === 'f') { return; }
    });
  }

  function moveRegion(d) {
    var idx = REGIONS.findIndex(function (r) { return r.no === S.region; });
    var n = (idx + d + REGIONS.length) % REGIONS.length;
    S.region = REGIONS[n].no;
    renderStage(); renderInspector();
  }
  function nextPage(d) {
    S.page = Math.min(23, Math.max(1, S.page + d));
    renderFilm(); renderStage(); renderPipeline(); renderCrumb();
  }
  function confirmRegion() {
    var r = REGIONS[S.region - 1];
    r.state = 'confirmed';
    var p = PAGES[S.page - 1];
    if (p.status === 'review') {
      var any = REGIONS.some(function (x) { return x.state !== 'confirmed' && x.state !== 'unreviewed'; });
      if (!any) p.status = 'ok';
    }
    renderStage(); renderInspector(); renderFilm();
  }
  function confirmAll() {
    REGIONS.forEach(function (r) { r.state = 'confirmed'; });
    PAGES[S.page - 1].status = 'ok';
    renderStage(); renderInspector(); renderFilm();
    openModal('本页已全部确认', '<div class="modal-impact">第 ' + pad(S.page) + ' 页 6 个 Region 的 review_state 已置为 <span class="mono">confirmed</span>，自动流程不会再覆盖。</div>', ['知道了'], 'info');
  }
  function openCmd() {
    $('#cmd').hidden = false; $('#cmdScrim').hidden = false;
    $('#cmdInput').value = ''; S.cmdIndex = 0; renderCmd('');
    setTimeout(function () { $('#cmdInput').focus(); }, 0);
  }
  function closeCmd() { $('#cmd').hidden = true; $('#cmdScrim').hidden = true; }
  function runCmd(i) {
    var c = S.cmdItems[i]; if (!c) return;
    closeCmd();
    if (/导出/.test(c.name)) openModal('导出本章', '<div class="modal-impact">范围 <span class="mono">本章 23 页</span>；格式 CBZ / ZIP / 单图 / PDF / 文本。预检：1 页未确认、1 页 stale 将被标记警告。</div>', ['导出 CBZ', '改选格式', '取消'], 'info');
    else if (/失败/.test(c.name)) { S.page = 18; renderFilm(); renderStage(); renderPipeline(); renderCrumb(); }
    else if (/确认/.test(c.name)) confirmRegion();
    else if (/切换资料柜/.test(c.name)) goSpace('library');
    else if (/切换控制台/.test(c.name)) goSpace('console');
    else if (/Provider/.test(c.name)) { goSpace('console'); S.consoleSection = 'provider'; renderConsole(); }
    else if (/第 7 页/.test(c.name)) { S.page = 7; renderFilm(); renderStage(); renderPipeline(); renderCrumb(); }
    else { openModal(c.name, '<div class="modal-impact">作用域：<span class="mono">' + esc(c.scope) + '</span>。这是一个演示动作——真实实现会创建 PipelineRun 并在流水线带显示进度。</div>', ['执行', '取消'], 'info'); }
  }
  function toggleTheme() {
    S.theme = S.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', S.theme);
    try { localStorage.setItem('nm.theme', S.theme); } catch (e) {}
  }

  /* ---------------------------------------------------------------------------
     16. 启动
     ------------------------------------------------------------------------ */
  function init() {
    var q = new URLSearchParams(location.search);
    if (q.get('space') && ['library', 'studio', 'console'].indexOf(q.get('space')) >= 0) S.space = q.get('space');
    if (q.get('state')) S.state = q.get('state');
    if (q.get('page')) S.page = Math.min(23, Math.max(1, parseInt(q.get('page'), 10) || 7));
    if (q.get('region')) S.region = Math.min(6, Math.max(1, parseInt(q.get('region'), 10) || 1));
    if (q.get('tab')) S.inspTab = q.get('tab');
    if (q.get('band') === '1') S.bandExpanded = true;
    if (q.get('film') === '1') S.filmExpanded = true;
    S.view = 'page';

    renderScope();
    renderCmd('');
    bind();

    if (S.state) applyState(S.state);
    else {
      goSpace(S.space);
      renderCrumb(); renderFilm(); renderStage(); renderInspector(); renderPipeline(); renderStates(); renderBanner();
    }
    goSpace(S.space);
    renderCrumb();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
