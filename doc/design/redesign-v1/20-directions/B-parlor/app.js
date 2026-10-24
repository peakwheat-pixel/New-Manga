/* =============================================================================
   方向 B · 校阅台（Parlor） — 交互层
   纯原生 JS，零依赖。驱动 index.html 的 DOM 骨架。
   ============================================================================= */
(function () {
  'use strict';

  var BOOK = '夜光列车';
  var CH = '第12话「雨の停車場」';

  var REGIONS = [
    { no: 1, type: '对白', jp: 'おはよう、また会えたね', mt: '早上好，又见面了呢', et: '', st: 'ok', lock: '' },
    { no: 2, type: '对白', jp: 'この雨、三日は止まないらしい', mt: '这场雨，好像三天都不会停', et: '这场雨，恐怕要下三天', st: 'ok', lock: 'translation' },
    { no: 3, type: '旁白', jp: '三日後の朝', mt: '三天后的早晨', et: '', st: 'review', lock: '' },
    { no: 4, type: '拟声词', jp: 'ザァァァ', mt: '—（跳过）', et: '', st: 'skip', lock: 'region' },
    { no: 5, type: '对白', jp: '切符をなくした', mt: '我把车票弄丢了', et: '', st: 'ok', lock: '' },
    { no: 6, type: '注释', jp: '※時刻表は変更されています', mt: '※时刻表已更改', et: '', st: 'review', lock: '' }
  ];

  var PAGES = [
    { no: 9, name: '第9话 · 灯台守', pages: 21, st: 'ok' },
    { no: 10, name: '第10话 · 終電', pages: 20, st: 'ok' },
    { no: 11, name: '第11话 · 始発', pages: 20, st: 'ok' },
    { no: 12, name: '第12话 · 雨の停車場', pages: 23, st: 'review' },
    { no: 13, name: '第13话 · 車掌の記憶', pages: 19, st: 'todo' }
  ];

  var STATES = [
    ['空工作区', '首次启动，无作品', 'empty'],
    ['导入中', '3 个文件夹 · 可取消', 'importing'],
    ['导入部分失败', '2 个格式不支持', 'import-failed'],
    ['章节无页面', '第13话还没有页面', 'no-pages'],
    ['页面无 Region', '未检测到文字区域', 'no-regions'],
    ['流水线运行中', 'Run #R-8831 · 62%', 'running'],
    ['暂停中', '等待安全边界', 'paused'],
    ['完成但有失败', '21 完成 / 2 失败', 'done-failed'],
    ['阻塞', 'Provider 认证失效', 'blocked'],
    ['中断恢复', '继续 / 重开 / 放弃', 'interrupted'],
    ['Region 部分完成', 'OCR 完成、翻译失败', 'partial'],
    ['过期 stale', '上游几何变更', 'stale']
  ];

  var ST = { row: 0, view: 'proof', theme: 'light', filter: 'all', zoom: 100, state: '', sel: [] };

  function $(s) { return document.querySelector(s); }
  function $$(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function pad(n) { return String(n).padStart(3, '0'); }
  function ico(id, cls) { return '<svg class="icon ' + (cls || '') + '" aria-hidden="true"><use href="#i-' + id + '"></use></svg>'; }

  var GLYPH = { ok: '✓', review: '●', fail: '!', skip: '⊘', stale: '◌', todo: '·', locked: '▮' };

  /* ---- 工程树 ---- */
  function renderTree() {
    var rows = '';
    rows += '<div class="tree-row tree-row--book" aria-selected="true">' +
      '<span class="tree-row__caret">' + ico('caret-down', 'icon--sm') + '</span>' +
      '<span class="tree-row__name">' + BOOK + '</span><span class="tree-row__meta">14 话</span></div>';
    PAGES.forEach(function (p) {
      var cur = p.no === 12 ? ' is-current' : '';
      rows += '<div class="tree-row tree-row--chapter' + cur + '" role="treeitem" data-ch="' + p.no + '">' +
        '<span class="tree-row__caret">' + ico(p.no === 12 ? 'caret-down' : 'caret-right', 'icon--sm') + '</span>' +
        '<span class="tree-row__name">' + esc(p.name) + '</span>' +
        '<span class="tree-row__num mono">' + (p.pages || '—') + '</span>' +
        '<span class="sq sq--' + (p.st === 'ok' ? 'ok' : p.st === 'review' ? 'warn' : 'muted') + '"></span></div>';
      if (p.no === 12) {
        rows += '<div class="tree-row tree-row--page is-current" data-page="7">' +
          '<span class="tree-row__num mono">007</span>' +
          '<span class="tree-row__name">007.jpg</span>' +
          '<span class="tree-row__meta">6 Region</span></div>';
      }
    });
    $('#tree').innerHTML =
      '<div class="tree__head"><span>工程</span><span class="mono">3 作品</span></div>' +
      '<div class="tree__scroll">' + rows + '</div>' +
      '<div class="tree__foot">' +
        '<div class="tree__foot-head">本章 · 第12话</div>' +
        '<div class="tree__foot-line"><span>完成</span><b class="mono">18</b></div>' +
        '<div class="tree__foot-line"><span>待确认</span><b class="mono">3</b></div>' +
        '<div class="tree__foot-line"><span>失败 / 过期</span><b class="mono">2 / 1</b></div>' +
      '</div>';
  }

  /* ---- 对照表 ---- */
  function renderProof() {
    var body = REGIONS.map(function (r, i) {
      var cur = i === ST.row ? ' is-current' : '';
      var diff = r.et && r.et !== r.mt ? ' <span class="diff" title="与机器译文不同"></span>' : '';
      var term = r.no === 2 ? ' <span class="term-warn" title="术语冲突：車掌 → 列车长">术语</span>' : '';
      return '<tr class="row' + cur + '" data-i="' + i + '" aria-selected="' + (i === ST.row) + '">' +
        '<td class="c-cursor"><span class="mark mark__glyph">' + (i === ST.row ? '›' : '') + '</span></td>' +
        '<td class="c-seq"><span class="mono">' + r.no + '</span>' + (r.lock ? '<span class="seq-lock">' + ico('lock', 'icon--sm icon--lock') + '</span>' : '') + '</td>' +
        '<td class="c-type">' + r.type + '</td>' +
        '<td class="c-ocr serif">' + esc(r.jp) + '</td>' +
        '<td class="c-trans serif">' + (r.st === 'skip' ? '<span class="entry__val--blank">—</span>' : esc(r.et || r.mt)) + diff + term + '</td>' +
        '<td class="c-status"><span class="mark mark__glyph">' + (GLYPH[r.st] || '·') + '</span></td>' +
      '</tr>';
    }).join('');

    return '<div class="sheet-scroll"><table class="proof">' +
      '<colgroup><col class="c-cursor"><col class="c-seq"><col class="c-type"><col class="c-ocr"><col class="c-trans"><col class="c-status"></colgroup>' +
      '<thead><tr><th class="h-cursor"></th><th class="h-seq">#</th><th class="h-type">类型</th>' +
      '<th>原文（OCR）</th><th>译文</th><th class="h-status">状态</th></tr></thead>' +
      '<tbody>' + body + '</tbody></table></div>';
  }

  /* ---- 画布呈现 ---- */
  function renderCanvas() {
    var boxes = REGIONS.map(function (r, i) {
      var sel = i === ST.row ? ' is-selected' : '';
      var pos = [
        [12, 12, 27, 15], [51, 10, 25, 14], [12, 31, 53, 6],
        [58, 36, 22, 10], [36, 54, 25, 13], [10, 87, 35, 7]
      ][i];
      return '<span class="region-box' + sel + '" data-i="' + i + '" style="left:' + pos[0] + '%;top:' + pos[1] + '%;width:' + pos[2] + '%;height:' + pos[3] + '%">' +
        '<span class="region-box__tag">' + r.no + ' ' + r.type + '</span></span>';
    }).join('');

    return '<div class="sheet-scroll"><div class="plate-area">' +
      '<div class="plate">' +
        '<span class="crop crop--tl"></span><span class="crop crop--tr"></span>' +
        '<span class="crop crop--bl"></span><span class="crop crop--br"></span>' +
        '<div class="plate__regions">' + boxes + '</div>' +
        '<span class="plate-area__guides"></span>' +
      '</div>' +
      '<div class="plate-foot"><span class="mono">007.jpg</span><span>1200 × 1800</span><span>6 Region</span><span>86%</span></div>' +
    '</div></div>';
  }

  /* ---- 成品呈现 ---- */
  function renderFinal() {
    return '<div class="sheet-scroll"><div class="final-plate">' +
      '<div class="plate" style="border:0">' +
        '<div class="plate__regions">' + REGIONS.map(function (r, i) {
          var pos = [[12, 12, 27, 15], [51, 10, 25, 14], [12, 31, 53, 6], [58, 36, 22, 10], [36, 54, 25, 13], [10, 87, 35, 7]][i];
          return '<span class="region-box" style="left:' + pos[0] + '%;top:' + pos[1] + '%;width:' + pos[2] + '%;height:' + pos[3] + '%">' +
            '<span class="entry__val serif" style="font-size:11px">' + esc(r.st === 'skip' ? r.jp : (r.et || r.mt)) + '</span></span>';
        }).join('') + '</div>' +
      '</div>' +
      '<div class="final-foot"><span class="final-foot__no mono">007 / 023</span>' +
        '<span>第12话 · 雨の停車場</span><span class="final-foot__nav">← →</span></div>' +
    '</div></div>';
  }

  /* ---- 边注 ---- */
  function renderMargin() {
    var r = REGIONS[ST.row] || REGIONS[0];
    var expanded = function (label, val) {
      return '<div class="kv"><span>' + label + '</span><span class="mono">' + esc(val) + '</span></div>';
    };
    var stName = { ok: '已确认', review: '待确认', skip: '跳过', stale: '过期', fail: '失败' }[r.st] || r.st;

    var html = '<div class="margin__head"><span class="margin__head-title">边注</span>' +
      '<span class="margin__head-meta mono">R' + r.no + ' · ' + r.type + '</span></div>' +
      '<div class="margin__scroll">' +
      '<div class="note"><div class="note__head"><span class="note__title">条目</span>' +
        '<span class="note__aside mono">' + stName + '</span></div>' +
        '<div class="kv"><span>review_state</span><span class="mono">' + (r.st === 'ok' ? 'confirmed' : 'needs_review') + '</span></div>' +
        expanded('锁定', r.lock === 'translation' ? 'translation' : r.lock === 'region' ? 'region' : '—') +
        expanded('字号', '22 px · shrink') +
      '</div>' +
      (r.no === 2 ? '<div class="note"><div class="note__head"><span class="note__title">术语冲突</span>' +
        '<span class="note__aside term-warn">1 处</span></div>' +
        '<div class="annotation"><div class="annotation__title">車掌 → 列车长</div>' +
        '<div class="annotation__body">本页 Region 2 的机器译文中出现「乘务员」，与作品术语表不一致。</div>' +
        '<div class="annotation__meta">来源：术语表 · 人工维护 · 14:02</div>' +
        '<div class="annotation__actions"><button class="btn btn--sm btn--solid" data-act="apply-term">应用术语并重渲染</button>' +
        '<button class="btn btn--sm btn--quiet">忽略</button></div></div>' +
        '<div class="annotation"><div class="annotation__title">替代表述</div>' +
        '<div class="annotation__body">「列车长」与上下文（车掌巡视车厢）一致，建议采用。</div></div></div>' : '') +
      '<div class="note"><div class="note__head"><span class="note__title">版本</span>' +
        '<span class="note__aside mono">5 条</span></div>' +
        '<div class="revs">' +
          [['r5', '14:22', '人工', '译文改为「恐怕要下三天」'], ['r4', '14:05', 'pipeline', 'translate 覆盖'], ['r3', '13:58', '人工', '字号 +1']].map(function (v) {
            return '<div class="rev"><span class="rev__no mono">' + v[0] + '</span><span class="rev__time mono">' + v[1] + '</span>' +
              '<span class="rev__src">' + v[2] + '</span><span class="rev__what">' + v[3] + '</span></div>';
          }).join('') +
        '</div></div>' +
      '<div class="note"><div class="note__head"><span class="note__title">四轨</span></div>' +
        '<div class="tracks">' +
          [['原图', 'done'], ['文本', 'done'], ['修复', 'done'], ['排版', r.st === 'stale' ? 'stale' : 'done']].map(function (t) {
            return '<div class="track"><span class="track__label">' + t[0] + '</span>' +
              '<span class="track__thumb sq sq--' + (t[1] === 'done' ? 'ok' : 'stale') + '"></span></div>';
          }).join('') + '</div></div>' +
      '</div>';
    return html;
  }

  /* ---- 底栏 ---- */
  function renderBottom() {
    var ok = REGIONS.filter(function (r) { return r.st === 'ok'; }).length;
    $('#bottombar').innerHTML =
      '<span class="bottombar__chapter">' + esc(CH) + ' · 第 007 页</span>' +
      '<span class="bottombar__group"><span>已确认 <b class="mono">' + (9 + ok) + '</b>/23</span>' +
      '<span>待确认 <b class="mono">3</b></span>' +
      '<span>失败 <b class="mono">2</b></span>' +
      '<span>过期 <b class="mono">1</b></span></span>' +
      '<span class="bottombar__spacer"></span>' +
      '<span class="bottombar__demo">本页 6 条 · 光标第 ' + (ST.row + 1) + ' 条</span>' +
      '<button class="btn btn--sm" id="btnNextReview">下一个待确认 →</button>';
  }

  /* ---- 命令面板 ---- */
  var CMDS = [
    ['确认并下一条', 'Ctrl+Enter', '当前条目'],
    ['进入编辑', 'Enter', '当前条目'],
    ['编辑原文（OCR）', 'O', '当前条目'],
    ['切换画布呈现', 'V', '视图'],
    ['切换成品呈现', 'V', '视图'],
    ['确认本页全部', '', '第007页 · 6条'],
    ['重渲染当前 Region', 'Shift+Enter', '当前条目'],
    ['打开导出抽屉', 'Ctrl+E', '本章 23 页'],
    ['导出 CBZ', '', '本章 23 页'],
    ['查看任务队列', '', '全局'],
    ['设置', 'Ctrl+,', '全局'],
    ['跳到下一个失败', 'Ctrl+Shift+F', '本章 · 2 个']
  ];
  function renderPalette(q) {
    q = (q || '').trim().toLowerCase();
    var items = CMDS.filter(function (c) { return !q || c[0].toLowerCase().indexOf(q) >= 0 || c[2].toLowerCase().indexOf(q) >= 0; });
    $('#paletteList').innerHTML = items.length ? items.map(function (c, i) {
      return '<button class="palette__item' + (i === 0 ? ' is-current' : '') + '">' + ico('arrow-right', 'icon--sm') +
        '<span class="palette__label">' + esc(c[0]) + '</span>' +
        '<span class="palette__scope">' + esc(c[2]) + '</span>' +
        (c[1] ? '<span class="palette__keys"><kbd class="kbd">' + esc(c[1]) + '</kbd></span>' : '') +
      '</button>';
    }).join('') : '<div class="palette__foot">没有匹配项</div>';
    $('#paletteCount').textContent = items.length + ' 项';
  }

  /* ---- 状态面板 ---- */
  function renderStates() {
    $('#statesList').innerHTML = STATES.map(function (s, i) {
      return '<button class="state-item" data-state="' + s[2] + '">' +
        '<span class="state-item__no mono">' + (i + 1) + '</span>' +
        '<span class="state-item__name">' + s[0] + '</span>' +
        '<span class="state-item__expr">' + s[1] + '</span>' +
        '<span class="state-item__apply">应用</span></button>';
    }).join('');
  }

  /* ---- 主渲染 ---- */
  function render() {
    $$('.segmented__item').forEach(function (b) {
      b.setAttribute('aria-selected', b.getAttribute('data-view') === ST.view ? 'true' : 'false');
    });
    var slot = $('#viewSlot');
    if (ST.state === 'empty') {
      slot.innerHTML = '<div class="empty-workspace"><div class="empty-workspace__title">还没有作品</div>' +
        '<div class="empty-workspace__sub">数据根：%APPDATA%\\NewManga\\library</div>' +
        '<div class="empty-workspace__root mono">Managed Copy · 原始文件只读</div>' +
        '<div class="empty-workspace__actions"><button class="btn btn--solid">导入文件夹</button>' +
        '<button class="btn">导入文件</button><button class="btn btn--quiet">设置</button></div></div>';
    } else if (ST.state === 'no-pages') {
      slot.innerHTML = '<div class="page-empty"><div class="page-empty__box">' + ico('page', 'icon--sm') + '</div>' +
        '<div class="page-empty__title">第13话还没有页面</div>' +
        '<div class="page-empty__hint">拖入文件夹或选择图片；识别为本章页序，不清空现有数据。</div>' +
        '<div class="page-empty__actions"><button class="btn btn--solid">导入页面</button></div></div>';
    } else if (ST.view === 'canvas') slot.innerHTML = renderCanvas();
    else if (ST.view === 'final') slot.innerHTML = renderFinal();
    else slot.innerHTML = renderProof();

    $('#margin').innerHTML = renderMargin();
    renderBottom();
    renderBanner();
  }

  function renderBanner() {
    var slot = $('#bannerSlot');
    if (ST.state === 'blocked') {
      slot.innerHTML = '<div class="banner"><span class="banner__tag">BLOCK</span>' +
        '<span class="banner__text">Provider 认证失效（deepseek-v3）· 受影响 23 页 · 数据未损坏</span>' +
        '<span class="banner__actions"><button class="btn btn--sm btn--solid">修复配置</button>' +
        '<button class="btn btn--sm btn--quiet">恢复队列</button></span></div>';
    } else if (ST.state === 'stale') {
      slot.innerHTML = '<div class="banner"><span class="banner__tag">STALE</span>' +
        '<span class="banner__text">Region 1 几何变更，render 结果已过期（历史版本保留）</span>' +
        '<span class="banner__actions"><button class="btn btn--sm">重跑过期项</button></span></div>';
    } else if (ST.state === 'interrupted') {
      slot.innerHTML = '<div class="banner"><span class="banner__tag">INTERRUPTED</span>' +
        '<span class="banner__text">上次任务 #R-8827 在第8话中断，已完成 14 页成果保留</span>' +
        '<span class="banner__actions"><button class="btn btn--sm btn--solid">继续</button>' +
        '<button class="btn btn--sm">重新开始</button><button class="btn btn--sm btn--quiet">放弃</button></span></div>';
    } else slot.innerHTML = '';
  }

  /* ---- 交互 ---- */
  function setRow(i) {
    ST.row = Math.max(0, Math.min(REGIONS.length - 1, i));
    render();
  }

  function bind() {
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('button,[data-i],[data-view],[data-state],[data-ch],[data-page]');
      if (!t) return;
      if (t.hasAttribute('data-view')) { ST.view = t.getAttribute('data-view'); ST.state = ''; render(); return; }
      if (t.hasAttribute('data-i')) { setRow(+t.getAttribute('data-i')); return; }
      if (t.hasAttribute('data-state')) { applyState(t.getAttribute('data-state')); $('#states').classList.add('is-hidden'); return; }
      if (t.id === 'btnCmd') { openPalette(); return; }
      if (t.id === 'btnStates') { $('#states').classList.remove('is-hidden'); renderStates(); return; }
      if (t.id === 'statesClose') { $('#states').classList.add('is-hidden'); return; }
      if (t.id === 'btnTheme') { toggleTheme(); return; }
      if (t.id === 'btnKeys') { openSheet('keys'); return; }
      if (t.id === 'btnExport') { openSheet('export'); return; }
      if (t.id === 'btnTools') { openSheet('tools'); return; }
      if (t.id === 'btnSettings') { openSheet('settings'); return; }
      if (t.id === 'sheetClose') { $('#sheet').classList.add('is-hidden'); return; }
      if (t.id === 'btnNextReview') { var nx = REGIONS.findIndex(function (r) { return r.st === 'review'; }); setRow(nx >= 0 ? nx : ST.row + 1); return; }
      if (t.hasAttribute('data-filter')) {
        $$('.chip[data-filter]').forEach(function (c) { c.setAttribute('aria-pressed', c === t ? 'true' : 'false'); });
        ST.filter = t.getAttribute('data-filter'); return;
      }
      if (t.hasAttribute('data-act')) {
        openDialog('应用术语并重渲染？', '将把 Region 2 的译文改为「列车长」并重渲染该 Region；其他 Region 不受影响。', ['应用', '取消']);
        return;
      }
    });

    $('#paletteInput').addEventListener('input', function (e) { renderPalette(e.target.value); });
    $('#scrim').addEventListener('click', function () { closeAll(); });
    $('#zoomIn').addEventListener('click', function () { ST.zoom = Math.min(140, ST.zoom + 10); $('#zoomVal').textContent = ST.zoom + '%'; document.documentElement.style.setProperty('--proof-size', (14 * ST.zoom / 100) + 'px'); });
    $('#zoomOut').addEventListener('click', function () { ST.zoom = Math.max(80, ST.zoom - 10); $('#zoomVal').textContent = ST.zoom + '%'; document.documentElement.style.setProperty('--proof-size', (14 * ST.zoom / 100) + 'px'); });

    document.addEventListener('keydown', function (ev) {
      var tag = (ev.target.tagName || '').toLowerCase();
      var typing = tag === 'input' || tag === 'textarea';
      if (ev.key === 'Escape') { closeAll(); return; }
      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') { ev.preventDefault(); openPalette(); return; }
      if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') { ev.preventDefault(); confirmRow(); return; }
      if (typing) return;
      if (ev.key === 'j' || ev.key === 'J' || ev.key === 'ArrowDown') { ev.preventDefault(); setRow(ST.row + 1); return; }
      if (ev.key === 'k' || ev.key === 'K' || ev.key === 'ArrowUp') { ev.preventDefault(); setRow(ST.row - 1); return; }
      if (ev.key === 'Enter') { ev.preventDefault(); confirmRow(); return; }
      if (ev.key.toLowerCase() === 'v') { ST.view = ST.view === 'proof' ? 'canvas' : ST.view === 'canvas' ? 'final' : 'proof'; render(); return; }
      if (ev.key.toLowerCase() === 'o') { openDialog('编辑原文', '修改 OCR 文本会使下游 translate / render 过期。当前条目：' + REGIONS[ST.row].jp, ['保存并标记过期', '取消']); return; }
    });
  }

  function confirmRow() {
    var r = REGIONS[ST.row];
    r.st = 'ok';
    render();
    flash('已确认 R' + r.no + ' · 下一个待确认已就位');
  }

  function flash(msg) {
    var el = $('#flash');
    el.textContent = msg;
    el.classList.remove('is-hidden');
    clearTimeout(flash._t);
    flash._t = setTimeout(function () { el.classList.add('is-hidden'); }, 2200);
  }

  function openPalette() {
    $('#palette').classList.remove('is-hidden'); $('#scrim').classList.remove('is-hidden');
    $('#paletteInput').value = ''; renderPalette('');
    setTimeout(function () { $('#paletteInput').focus(); }, 0);
  }

  function openSheet(kind) {
    var title = { keys: '键位速查', export: '导出', tools: '工具', settings: '设置' }[kind];
    $('#sheetTitle').textContent = title;
    $('#sheet').classList.remove('is-hidden'); $('#scrim').classList.remove('is-hidden');
    var tabs = kind === 'export' ? ['范围', '格式', '预检'] : kind === 'tools' ? ['任务', '术语', '设置'] : ['说明'];
    $('#sheetTabs').innerHTML = tabs.map(function (t, i) {
      return '<button class="sheet__tab' + (i === 0 ? ' is-current' : '') + '">' + t + '</button>';
    }).join('');
    var body = '';
    if (kind === 'export') {
      body = '<div class="sheet__section"><div class="sheet__section-head"><span class="sheet__section-title">导出范围与格式</span></div>' +
        '<div class="preflight">' +
        '<div class="preflight__row"><span>本章页数</span><b class="mono">23</b></div>' +
        '<div class="preflight__row"><span>已确认</span><b class="mono">18</b></div>' +
        '<div class="preflight__row"><span>未确认（将标记警告）</span><b class="mono">3</b></div>' +
        '<div class="preflight__row"><span>过期（将标记警告）</span><b class="mono">1</b></div>' +
        '<div class="preflight__row"><span>失败（将跳过）</span><b class="mono">2</b></div>' +
        '</div><div class="sheet__foot"><button class="btn btn--solid">导出 CBZ</button>' +
        '<button class="btn">导出 ZIP</button><button class="btn">导出文本</button></div></div>';
    } else if (kind === 'keys') {
      body = '<div class="sheet__section"><div class="sheet__section-head"><span class="sheet__section-title">常用键位</span></div>' +
        '<table class="grid-table"><tbody>' +
        [['J / K', '下一条 / 上一条'], ['Enter', '确认并下一条'], ['Ctrl+Enter', '确认本页全部'],
         ['O', '编辑原文'], ['V', '切换呈现（对照/画布/成品）'], ['[ ]', '上/下一页'],
         ['Ctrl+K', '命令面板'], ['Ctrl+E', '导出抽屉'], ['F1', '键位速查']].map(function (k) {
          return '<tr><td class="mono">' + k[0] + '</td><td>' + k[1] + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    } else if (kind === 'tools') {
      body = '<div class="sheet__section"><div class="sheet__section-head"><span class="sheet__section-title">任务</span>' +
        '<span class="sheet__section-meta mono">3 个 Run</span></div>' +
        [['R-8831', 'translate_untranslated · 第12话', '62%', 'run'],
         ['R-8830', 'reinpaint_selected · 第11话 5页', '完成', 'ok'],
         ['R-8829', 'rerender_all · 第10话', '完成（1 失败）', 'warn'],
         ['R-8828', 'translate_all · 第9话', '阻塞', 'danger']].map(function (r) {
          return '<div class="run-row"><div class="run-row__top"><span class="run-row__id mono">' + r[0] + '</span>' +
            '<span class="run-row__scope">' + r[1] + '</span></div>' +
            '<div class="run-row__state"><span class="sq sq--' + r[3] + '"></span>' + r[2] + '</div></div>';
        }).join('') + '</div>';
    } else {
      body = '<div class="sheet__section"><div class="sheet__section-head"><span class="sheet__section-title">本稿设置</span></div>' +
        '<table class="grid-table"><tbody>' +
        '<tr><td>阅读方向</td><td class="mono">RTL（章节属性）</td></tr>' +
        '<tr><td>字体</td><td class="mono">Noto Serif SC</td></tr>' +
        '<tr><td>字号</td><td class="mono">' + ST.zoom + '%</td></tr>' +
        '<tr><td>差异标记</td><td class="mono">开</td></tr>' +
        '</tbody></table></div>';
    }
    $('#sheetBody').innerHTML = body;
    $('#sheetFoot').innerHTML = '';
  }

  function openDialog(title, body, choices) {
    $('#dialogTitle').textContent = title;
    $('#dialogBody').innerHTML = '<div class="dialog__impact">' + esc(body) + '</div>';
    $('#dialogFoot') || ($('#dialog').insertAdjacentHTML('beforeend', '<div class="dialog__foot" id="dialogFoot"></div>'));
    var f = $('#dialogFoot');
    f.innerHTML = '<span class="dialog__foot-spacer"></span>' + choices.map(function (c, i) {
      return '<button class="btn ' + (i === 0 ? 'btn--solid' : 'btn--quiet') + '">' + c + '</button>';
    }).join('');
    $('#dialog').classList.remove('is-hidden'); $('#scrim').classList.remove('is-hidden');
    f.querySelectorAll('button').forEach(function (b, i) {
      b.addEventListener('click', function () { closeAll(); if (i === 0) flash('已应用'); });
    });
  }

  function closeAll() {
    ['#palette', '#sheet', '#states', '#dialog'].forEach(function (s) { $(s).classList.add('is-hidden'); });
    $('#scrim').classList.add('is-hidden');
  }

  function toggleTheme() {
    ST.theme = ST.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', ST.theme);
    try { localStorage.setItem('nm.parlor.theme', ST.theme); } catch (e) {}
  }

  function applyState(id) {
    ST.state = id;
    if (id === 'empty' || id === 'no-pages') { /* view 内呈现空态 */ }
    else if (id === 'running' || id === 'paused' || id === 'done-failed') { ST.state = id; }
    render();
  }

  /* ---- 启动 ---- */
  function init() {
    var q = new URLSearchParams(location.search);
    if (q.get('view')) ST.view = q.get('view');
    if (q.get('theme')) ST.theme = q.get('theme');
    if (q.get('state')) ST.state = q.get('state');
    document.documentElement.setAttribute('data-theme', ST.theme);

    renderTree();
    renderStates();
    renderPalette('');
    bind();
    render();
    if (ST.state === 'interrupted') renderBanner();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
