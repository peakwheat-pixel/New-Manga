/* =============================================================================
   New Manga · 方向 C「工坊 Atelier」· views.js
   只做"数据 → HTML 字符串"，不绑定事件（事件全部在 app.js 委托）。
   所有 class 名严格对应 styles.css 已定义的约定；不新增裸值样式（仅用 var()）。
   ============================================================================= */
'use strict';

(function (NM) {
  var V = (NM.v = {});

  /* ---------- 0. 基础 ---------- */
  function ic(name, cls) {
    return '<svg class="icon' + (cls ? ' ' + cls : '') + '" aria-hidden="true"><use href="#' + name + '"></use></svg>';
  }
  V.ic = ic;

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  V.esc = esc;

  /* ---------- 1. 抽象页图（纯 CSS 自绘，无任何图片） ---------- */
  var arts = 0;
  function art(o) {
    o = o || {};
    var rnd = mulberry(o.seed || 11);
    var isClean = !!o.clean;
    var h = '<div class="art' + (isClean ? ' is-clean' : '') + (o.cls ? ' ' + o.cls : '') + '">';
    // 分格线（3 横 2 竖，固定节奏，像真实漫画页的格子）
    h += '<span class="panel-line h" style="top:30%"></span>';
    h += '<span class="panel-line h" style="top:58%"></span>';
    h += '<span class="panel-line h" style="top:80%"></span>';
    h += '<span class="panel-line v" style="left:50%;top:3%;bottom:62%"></span>';
    h += '<span class="panel-line v" style="left:38%;top:62%;bottom:3%"></span>';
    // 网点块
    var tones = o.tones != null ? o.tones : 2;
    for (var t = 0; t < tones; t++) {
      var tl = 5 + rnd() * 55, tt = 6 + rnd() * 30;
      h += '<span class="tone" style="left:' + tl.toFixed(1) + '%;top:' + tt.toFixed(1) + '%;width:' + (18 + rnd() * 22).toFixed(1) + '%;height:' + (10 + rnd() * 14).toFixed(1) + '%"></span>';
    }
    // 文字块（原图）
    var txts = o.txts != null ? o.txts : 3;
    for (var i = 0; i < txts; i++) {
      var l = 8 + rnd() * 60, tp = 8 + rnd() * 74;
      h += '<span class="txt" style="left:' + l.toFixed(1) + '%;top:' + tp.toFixed(1) + '%;width:' + (16 + rnd() * 16).toFixed(1) + '%;height:' + (7 + rnd() * 8).toFixed(1) + '%"></span>';
    }
    // Region 覆盖框（真实功能：检测框）
    (o.regions || []).forEach(function (rg) {
      h += '<span class="rgn" data-n="' + rg.n + '" data-t="' + rg.type + '"' + (rg.state === 'needs_review' ? ' data-state="needs_review"' : '') +
        ' style="left:' + rg.geo[0] + '%;top:' + rg.geo[1] + '%;width:' + rg.geo[2] + '%;height:' + rg.geo[3] + '%"></span>';
    });
    // Mask 叠加（修复轨）
    (o.masks || []).forEach(function (m) {
      h += '<span class="mask" style="left:' + m[0] + '%;top:' + m[1] + '%;width:' + m[2] + '%;height:' + m[3] + '%"></span>';
    });
    if (o.safe) h += '<span class="safe"></span>';
    if (o.trim !== false) h += '<span class="trim"><i></i></span>';
    if (o.rtxt) {
      for (var k = 0; k < 7; k++) {
        var rl = 10 + (k % 3) * 26 + Math.round(rnd() * 6);
        h += '<span class="rtxt" style="left:' + rl + '%;top:' + (10 + k * 11) + '%;width:' + (10 + Math.round(rnd() * 8)) + '%"></span>';
      }
    }
    if (o.bub) {
      for (var b = 0; b < 3; b++) {
        h += '<span class="bub" style="left:' + (12 + b * 28) + '%;top:' + (14 + b * 18) + '%;width:' + (18 + b * 4) + '%;height:' + (12 + b * 3) + '%"></span>';
      }
    }
    return h + '</div>';
  }
  V.art = art;

  function mulberry(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ---------- 2. 阶段轨道 + 门禁条 ---------- */
  V.tabs = function (stage) {
    return NM.TABS.map(function (t) {
      var on = t.k === stage;
      return '<button class="tab" role="tab" data-stage="' + t.k + '" aria-selected="' + (on ? 'true' : 'false') + '"' +
        ' title="' + esc(t.name + ' · ' + t.cn + '（' + (t.idx === 'Q' ? 'Q' : t.idx + ' 的对应数字键') + '）') + '">' +
        '<span class="tab-idx">' + t.idx + '</span>' +
        '<span class="tab-name">' + ic(t.icon) + t.name + '</span>' +
        '<span class="tab-cn">' + t.cn + (t.ab ? ' · 异常 ' + t.ab : '') + '</span>' +
        '</button>';
    }).join('');
  };

  V.gate = function (stage) {
    var h = '<div class="gate-seg" style="width:var(--w-tree);min-width:var(--w-tree);border-right:1px solid var(--line-hair);padding-right:var(--sp-2)">' +
      '<span class="lbl" style="white-space:nowrap">阶段门禁</span></div>';
    h += NM.TABS.map(function (t) {
      var q = t.k === 'queue';
      return '<button class="gate-seg" data-gate="' + (q ? 'ok' : t.gate) + '" data-stage="' + t.k + '" title="' + esc(t.cn + ' 阶段门禁') + '">' +
        '<span class="g-bar"><span class="g-fill" style="width:' + t.pct + '%"></span>' +
        '<span class="g-tick" style="left:100%"></span></span>' +
        '<span class="g-pct">' + (q ? '7 待' : t.pct + '%') + '</span>' +
        (t.ab ? '<span class="g-ab" data-zero="' + (t.ab ? 0 : 1) + '">' + t.ab + '</span>' : '') +
        '</button>';
    }).join('');
    h += '<button class="gate-note" data-action="gate-render" title="RENDER 门禁：12 页未修复">' +
      ic('i-warn') + 'RENDER 门禁：<b style="font-family:var(--font-data);font-weight:400">12</b> 页未修复 · 导出将缺失成品</button>';
    return h;
  };

  /* ---------- 3. 资源树 ---------- */
  V.tree = function (ui) {
    var h = '<div class="tree-scroll">';

    /* 作品 */
    h += '<div class="tree-group"><div class="lbl"><span>作品</span><span>' + NM.BATCH.chapters + ' 话</span></div>';
    ['夜光列车', '雨の停車場', '汉江之夜', '旧校舍的夏天'].forEach(function (b, i) {
      var cur = i === 0;
      h += '<button class="tree-row indent-1" data-book="' + i + '"' + (cur ? ' aria-current="true"' : '') + '>' +
        ic(i === 2 ? 'i-split' : 'i-folder') +
        '<span class="tw">' + b + '</span>' +
        '<span class="cnt">' + (i === 0 ? '11/14' : i === 1 ? '1' : i === 2 ? '12/60' : '8/8') + '</span></button>';
      if (cur) {
        NM.CHAPTERS.forEach(function (c) {
          var on = ui.chapter === c.id;
          h += '<button class="tree-row indent-2" data-chapter="' + c.id + '"' + (on ? ' aria-current="true"' : '') + '>' +
            ic('i-page') + '<span class="tw">' + esc(c.title) + '</span>' +
            '<span class="cnt">' + c.pages + '</span></button>';
        });
      }
    });
    h += '</div>';

    /* 批次 */
    h += '<div class="tree-group"><div class="lbl"><span>批次</span><span>2</span></div>';
    var batches = [
      { id: 'B-012', t: '第1–10章', n: 240, badge: 'running', btxt: '1' },
      { id: 'B-011', t: '第1–9章', n: 216, badge: 'failed', btxt: '2' }
    ];
    batches.forEach(function (b) {
      var on = b.id === NM.BATCH.id;
      h += '<button class="tree-row indent-1" data-batch="' + b.id + '"' + (on ? ' aria-current="true"' : '') + '>' +
        ic('i-grid') + '<span class="tw">' + b.id + ' · ' + b.t + '</span>' +
        '<span class="badge ' + b.badge + '">' + b.btxt + '</span>' +
        '<span class="cnt">' + b.n + '</span></button>';
    });
    h += '</div>';

    /* 队列 */
    h += '<div class="tree-group"><div class="lbl"><span>队列</span><span>7</span></div>';
    NM.RUNS.forEach(function (r) {
      var on = r.state === 'running';
      h += '<button class="tree-row indent-1" data-run="' + r.id + '"' + (on ? ' aria-current="true"' : '') + ' title="' + esc(r.task + ' · ' + r.scope) + '">' +
        ic('i-clock') + '<span class="tw mono">' + r.id + '</span>' +
        '<span class="badge ' + (r.state === 'blocked' ? 'failed' : r.state === 'running' ? 'running' : '') + '">' +
        (r.state === 'running' ? r.pct + '%' : r.state === 'blocked' ? '阻塞' : r.state === 'interrupted' ? '中断' : '完成') + '</span></button>';
    });
    h += '</div></div>';

    /* 底部摘要 */
    h += '<div class="tree-foot">' +
      '<div class="kv"><span>本章</span><b>' + NM.CHAPTER.pages + ' 页</b></div>' +
      '<div class="kv"><span>完成</span><b>' + NM.CHAPTER.done + '</b></div>' +
      '<div class="kv"><span>失败 / 过期</span><b>' + NM.CHAPTER.failed + ' / ' + NM.CHAPTER.stale + '</b></div>' +
      '<div class="kv"><span>待确认</span><b>' + NM.CHAPTER.review + '</b></div>' +
      '</div>';
    return h;
  };

  /* ---------- 4. 概览计数胶囊 ---------- */
  V.chips = function (ui) {
    var h = NM.CHIPS.map(function (c) {
      var on = ui.filter === c.k;
      return '<button class="chip" data-chip="' + c.k + '" data-kind="' + c.kind + '" aria-pressed="' + (on ? 'true' : 'false') + '">' +
        '<span class="n">' + c.n + '</span><span>' + c.label + '</span>' +
        (c.unit ? '<span class="u">' + c.unit + '</span>' : '') + '</button>';
    }).join('');
    h += '<span class="spacer"></span>';
    if (ui.filter !== 'all') {
      var d = NM.CHIPS.filter(function (c) { return c.k === ui.filter; })[0];
      h += '<span class="filter-flag">筛选：' + esc(d.label) + ' · 全批 ' + d.n + ' 页' + ic('i-close') + '</span>';
    }
    h += '<span class="sel-note">本章 <b>' + NM.CHAPTER.pages + '</b> 页 · 待确认 <b>' + NM.CHAPTER.review + '</b></span>';
    return h;
  };

  /* ---------- 5. Page × Stage 矩阵 ---------- */
  var LEGEND = [
    { st: 'completed', label: '完成', key: 'completed' },
    { st: 'not_started', label: '未开始', key: 'not_started' },
    { st: 'running', label: '进行中', key: 'running' },
    { st: 'stale', label: '过期', key: 'stale' },
    { st: 'failed', label: '失败', key: 'failed' },
    { st: 'skipped', label: '跳过/不适用', key: 'skipped' },
    { st: 'pending', label: '等待中', key: 'pending' }
  ];

  V.matrix = function (ui, pages) {
    var h = '';

    /* 头 */
    h += '<div class="mx-head">' +
      '<span class="mx-title">页 × 阶段</span>' +
      '<span class="mx-count">' + pages.length + '/' + NM.BATCH.pages + ' 页 · ' + (pages.length * 11) + ' 单元 · ' + esc(NM.CHAPTER.title) + '</span>' +
      '<span class="mx-head-tools">' +
      '<button class="btn sm" data-action="matrix-max" title="矩阵最大化（隐藏右侧工作面）">' + ic('i-grid', 'icon-12') + '最大化</button>' +
      '<button class="btn sm" data-action="only-abnormal" title="只显示有异常的行">' + ic('i-filter', 'icon-12') + '仅异常</button>' +
      '</span></div>';

    /* 列头 */
    h += '<div class="mx-scroll"><div class="mx-colhead">' +
      '<div class="ch0">页 / PAGE</div>' +
      NM.STAGES.map(function (s, i) {
        return '<button class="ch" data-col="' + i + '" title="' + esc(s.full + ' · ' + s.cn) + '" data-active="' + (ui.activeCol === i ? 1 : 0) + '">' + s.ab + '</button>';
      }).join('') +
      '<div class="chd">汇总</div><div class="chr">RGN</div><div class="che">事件</div>' +
      '</div><div class="mx-rows">';

    /* 行 */
    pages.forEach(function (p, r) {
      var dim = ui.filter !== 'all' && p.derived !== ui.filter ? 1 : 0;
      var focusRow = ui.focus.r === r ? 1 : 0;
      h += '<div class="mx-row" data-r="' + r + '" data-dim="' + dim + '" data-focus="' + focusRow + '"' +
        (focusRow ? ' aria-current="true"' : '') + '>' +
        '<div class="mx-page"><span class="th"></span><span class="pid">' + p.pid + '</span></div>' +
        p.states.map(function (st, c) {
          var sel = ui.sel[cellKey(r, c)] ? 1 : 0;
          var foc = ui.focus.r === r && ui.focus.c === c ? 1 : 0;
          return '<button class="cell" data-r="' + r + '" data-c="' + c + '" data-st="' + st + '"' +
            ' data-selected="' + sel + '" data-focus="' + foc + '"' +
            ' aria-label="' + esc('第 ' + p.pid + ' 页 · ' + NM.STAGES[c].full + ' · ' + st) + '">' +
            '<span class="mk" data-st="' + st + '"></span></button>';
        }).join('') +
        '<div class="mx-derived"><span class="dt" data-k="' + p.derived + '">' + derivedLabel(p.derived) + '</span></div>' +
        '<div class="mx-reg">' + (p.regions || '—') + '</div>' +
        '<div class="mx-event" data-k="' + p.derived + '">' + esc(p.event) + '</div>' +
        '</div>';
    });

    /* 汇总行（其余 217 页，聚合到批次口径） */
    h += aggregateRow(pages.length);

    h += '</div></div>';

    /* 底部：图例 + 门禁 + 选中摘要 */
    h += '<div class="mx-foot">';
    h += '<div class="legend"><div class="legend-head"><span class="lbl">状态符号 · 形状 + 色相 + 明度三重编码</span>' +
      '<span class="lbl">7 种</span></div><div class="legend-grid">' +
      LEGEND.map(function (l) {
        return '<div class="legend-item"><span class="mk" data-st="' + l.st + '"></span><span>' + l.label + '</span>' +
          '<span class="lg-st">' + l.key + '</span></div>';
      }).join('') + '</div></div>';

    h += '<div class="mx-gate">' +
      gateLine('fail', 'block', 'INPAINT', '2 单元失败 · ModelLoadError（anime_lama_v2）') +
      gateLine('warn', 'warn', 'REVIEW', '3 页待确认 · 其中 2 页有 needs_review Region') +
      gateLine('ok', 'ok', 'DETECT', '23/23 页已检测 · 0 页无 Region') +
      '</div>';

    h += '<div class="mx-sel">' + selSummary(ui) +
      '<span class="keyhint">点击选中 · Shift 框选 · Enter 下钻 · 空格切换</span></div>';
    h += '</div>';
    return h;
  };

  function gateLine(tone, tag, k, text) {
    return '<div class="gate-line" data-tone="' + tone + '"><span class="tag">' + tag.toUpperCase() + '</span>' +
      '<span class="mono">' + k + '</span><span class="grow">' + esc(text) + '</span>' +
      '<button class="btn sm" data-action="gate-' + k.toLowerCase() + '">处置</button></div>';
  }

  function aggregateRow(n) {
    var rest = NM.BATCH.pages - n;
    var stageAgg = ['completed', 'completed', 'completed', 'completed', 'failed', 'skipped', 'skipped', 'failed', 'stale', 'pending', 'skipped'];
    var h = '<div class="mx-row" data-sum="1" data-dim="0" data-focus="0">' +
      '<div class="mx-page"><span class="th"></span><span class="pid">Σ' + rest + '</span></div>';
    h += stageAgg.map(function (st, i) {
      return '<div class="cell" data-sum="1" data-c="' + i + '" title="' + esc('其余 ' + rest + ' 页 · ' + NM.STAGES[i].full + ' 聚合') + '">' +
        '<span class="mk" data-st="' + st + '"></span></div>';
    }).join('');
    h += '<div class="mx-derived"><span class="dt" data-k="partial">聚合</span></div>' +
      '<div class="mx-reg">—</div>' +
      '<div class="mx-event">其余 ' + rest + ' 页 · 8 章（批次 ' + NM.BATCH.id + ' 口径）</div></div>';
    return h;
  }

  function derivedLabel(k) {
    return ({
      done: '完成', review: '待确认', failed: '失败', stale: '过期', running: '处理中',
      not_started: '未处理', partial: '部分'
    })[k] || k;
  }

  function cellKey(r, c) { return r + ':' + c; }
  V.cellKey = cellKey;

  function selSummary(ui) {
    var n = Object.keys(ui.sel).length;
    if (!n) return '<span>已选</span><b>0</b><span>单元 · 点击矩阵任意单元开始（Shift 框选 · Enter 下钻）</span>';
    var mix = { failed: 0, stale: 0, other: 0 };
    Object.keys(ui.sel).forEach(function (k) {
      var st = ui.statesOf(k);
      if (st === 'failed') mix.failed++;
      else if (st === 'stale') mix.stale++;
      else mix.other++;
    });
    return '<span>已选</span><b>' + n + '</b><span>单元 · 失败 <b>' + mix.failed + '</b> · 过期 <b>' + mix.stale +
      '</b> · 其他 <b>' + mix.other + '</b></span>';
  }
  V.selSummary = selSummary;

  /* ---------- 6. 批量动作条 ---------- */
  V.bulk = function (ui) {
    var n = Object.keys(ui.sel).length;
    var rows = {}, cols = {};
    Object.keys(ui.sel).forEach(function (k) {
      var a = k.split(':');
      rows[a[0]] = 1; cols[a[1]] = 1;
    });
    var scope = n ? ('作用域：' + Object.keys(rows).length + ' 页 × ' + Object.keys(cols).length + ' 阶段') : '';
    return '<span class="bcount">' + ic('i-target', 'icon-12') + '选中 <b>' + n + '</b><span class="bscope">单元</span></span>' +
      '<span class="bscope">' + esc(scope) + '</span>' +
      '<span class="sep"></span>' +
      '<button class="btn" data-action="retry" data-tone="danger">' + ic('i-retry', 'icon-12') + '重试失败 <span class="scope">Ctrl+Shift+R</span></button>' +
      '<button class="btn" data-action="advance">' + ic('i-arrow', 'icon-12') + '推进到下一阶段 <span class="scope">Ctrl+Enter</span></button>' +
      '<button class="btn" data-action="switch-provider">' + ic('i-settings', 'icon-12') + '换 Provider</button>' +
      '<button class="btn" data-action="skip">' + ic('i-skip', 'icon-12') + '跳过</button>' +
      '<button class="btn" data-action="detail">' + ic('i-eye', 'icon-12') + '查看详情 <span class="scope">Enter</span></button>' +
      '<span class="spacer"></span>' +
      '<button class="btn sm" data-action="clear-sel">' + ic('i-close', 'icon-12') + '取消选择 <span class="scope">Esc</span></button>';
  };

  /* ---------- 7. 阶段工作面 ---------- */
  V.surface = function (ui, pages) {
    var t = NM.TABS.filter(function (x) { return x.k === ui.stage; })[0];
    var body = '';
    switch (ui.stage) {
      case 'detect': body = surfDetect(pages); break;
      case 'ocr': body = surfOcr(pages); break;
      case 'verify': body = surfVerify(ui); break;
      case 'inpaint': body = surfInpaint(ui); break;
      case 'render': body = surfRender(pages); break;
      default: body = surfQueue(ui); break;
    }
    var head = '<div class="surf-head"><span class="surf-title">' + t.name + '<span class="mono">' + t.cn + ' · ' + t.pct + '%</span></span>' +
      '<span class="surf-meta">' + surfMeta(ui) + '</span>' + surfTools(ui) + '</div>';
    return head + '<div class="surf-body">' + body + '</div>';
  };

  function surfMeta(ui) {
    switch (ui.stage) {
      case 'detect': return 'Region 几何与越界检查 · 23 页 / 152 Region · 越界 2 · 空页 0';
      case 'ocr': return '识别质量桶 · 低置信 ' + 6 + ' 页 · 无文本 2 页 · 平均置信 0.91';
      case 'verify': return '对照复核 · 待确认 ' + NM.CHAPTER.review + ' 条 · 术语冲突 1 · 已确认 182';
      case 'inpaint': return '原图 / 修复对比 · 路线 anime_lama_v2 · 失败 1 · Mask 覆盖 152 Region';
      case 'render': return '成品预览 · 已渲染 ' + (NM.CHAPTER.pages - 5) + '/' + NM.CHAPTER.pages + ' · 溢出 2 · 缺失 3';
      default: return 'Run 列表 · 运行 1 · 阻塞 1 · 中断 1 · 已完成 2';
    }
  }

  function surfTools(ui) {
    var byStage = {
      detect: [['i-target', '重检测', 'redetect'], ['i-filter', '仅越界', 'only-overflow']],
      ocr: [['i-ocr', '重 OCR', 'reocr'], ['i-list', '按置信排序', 'sort-conf']],
      verify: [['i-check', '确认本页', 'confirm-page'], ['i-lock', '加锁', 'lock']],
      inpaint: [['i-retry', '重修复', 'reinpaint'], ['i-split', '换路线', 'route']],
      render: [['i-render', '重渲染', 'rerender'], ['i-export', '导出批次', 'export']],
      queue: [['i-pause', '暂停', 'pause'], ['i-play', '继续', 'resume'], ['i-stop', '停止', 'stop']]
    }[ui.stage] || [];
    return '<span class="surf-tools">' + byStage.map(function (b, i) {
      return (i ? '<span class="sep"></span>' : '') + '<button class="btn sm" data-action="' + b[2] + '">' + ic(b[0], 'icon-12') + b[1] + '</button>';
    }).join('') + '</span>';
  }

  function surfDetect(pages) {
    var h = '<div class="detect-grid">';
    pages.forEach(function (p, i) {
      var flag = i === 18;
      h += '<div class="tile" role="button" tabindex="0" data-page="' + p.pid + '" aria-selected="' + (i === 6 ? 'true' : 'false') + '">' +
        art({ seed: 100 + i, tones: 2, txts: 3, safe: true }) +
        '<div class="tile-foot"><span class="pid">' + p.pid + '</span><span>' + p.regions + ' RGN</span>' +
        '<span class="n">' + (flag ? '越界 2' : '0.9' + (2 + (i % 7))) + '</span></div>' +
        '<div class="tile-caption">' + (flag ? 'Region 越出安全区 <b>2</b>' : '几何正常 · 安全区内') + '</div>' +
        '</div>';
    });
    h += '</div>';
    h += '<div class="surf-foot"><span>Region 命中率</span><b>0.94</b><span>· 平均 6.6 Region/页</span>' +
      '<span>· 越界</span><b>2</b><span>· 无 Region</span><b>0</b>' +
      '<span style="margin-left:auto">双击单元 → 详情抽屉 · Enter 下钻</span></div>';
    return h;
  }

  function surfOcr(pages) {
    var rows = NM.ocrRows(pages);
    var legend = '<div class="bucket-legend">' + '<span class="lbl" style="margin-right:var(--sp-2)">质量桶</span>' +
      NM.OCR_BUCKETS.slice().reverse().map(function (b) {
        return '<span class="bk"><i data-lv="' + b.lv + '" style="background:' + bucketColor(b.lv) + '"></i>' + b.cn + ' · ' + esc(b.label) + '</span>';
      }).join('') + '</div>';
    var h = legend + '<div class="qt-wrap"><table class="qt"><thead><tr>' +
      '<th>页</th><th class="r">Region</th><th class="r">平均置信</th><th class="r">低置信</th><th>质量桶</th><th class="c">处置</th>' +
      '</tr></thead><tbody>';
    rows.forEach(function (r) {
      h += '<tr data-flag="' + (r.flag ? 1 : 0) + '" data-page="' + r.pid + '">' +
        '<td><span class="pid">' + r.pid + '</span></td>' +
        '<td class="r num">' + r.regions + '</td>' +
        '<td class="r num">' + r.conf + '</td>' +
        '<td class="r num">' + (r.low || '—') + '</td>' +
        '<td><span class="bar">' + NM.OCR_BUCKETS.slice().reverse().map(function (b) {
          return '<span class="seg" data-lv="' + b.lv + '" title="' + esc(b.label) + '"><i style="width:' +
            (b.lv === r.lv ? 100 : b.lv < r.lv ? 100 : 0) + '%"></i></span>';
        }).join('') + '</span>' +
        (r.flag ? ' <span class="dot ' + (r.lv === 1 ? 'bad' : 'warn') + '"></span>' : '') + '</td>' +
        '<td class="c"><button class="act" data-action="' + (r.flag ? 'reocr-one' : 'view-region') + '" data-page="' + r.pid + '">' + r.act + '</button></td>' +
        '</tr>';
    });
    h += '</tbody></table></div>';
    return h;
  }
  function bucketColor(lv) {
    return lv === 4 ? 'var(--st-done)' : lv === 3 ? 'var(--st-running)' : lv === 2 ? 'var(--st-blocked)' : lv === 1 ? 'var(--st-failed)' : 'var(--st-skipped)';
  }

  function surfVerify(ui) {
    var h = '<div class="vf">';
    /* 左：页面 + Region 叠加 + 页切换 + Region 检查清单 */
    h += '<div class="vf-page is-stack">' +
      '<div class="vf-page-head"><span>PAGE</span><b>007.jpg</b><span class="mono">1200×1800 · RTL</span></div>' +
      art({ seed: 7, regions: NM.REGIONS, safe: true, tones: 3, txts: 2 }) +
      '<div class="vf-page-foot">' + [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 17, 18, 19, 21].map(function (n) {
        var f = n === 18 ? 'failed' : n === 20 ? 'stale' : n === 17 ? 'review' : '';
        return '<button class="pg" data-page="' + NM.pad3(n) + '" data-f="' + f + '"' + (n === 7 ? ' aria-current="true"' : '') + '>' + n + '</button>';
      }).join('') + '</div>' +
      '<div class="vf-chk"><div class="vf-chk-head">Region 检查<span class="mono" style="margin-left:auto">6 / 6</span></div>' +
      '<div class="vf-chk-list">' + NM.REGIONS.map(function (r) {
        return '<button class="vf-chk-row" data-region="' + r.n + '">' +
          '<span class="k">' + r.n + '</span><span class="k">' + r.cn + '</span>' +
          '<span class="t">' + esc(r.ocr) + '</span>' +
          '<span>' + stText(r.state) + (r.lock ? '·锁' : '') + '</span></button>';
      }).join('') + '</div></div></div>';

    /* 右：对照行 */
    h += '<div class="vf-list"><div class="vf-list-head">' +
      '<span>#</span><span>类型</span><span>原文 OCR</span><span>机器译文</span><span class="c-ed">人工译文</span><span>状态</span>' +
      '</div><div class="vf-rows">';
    h += '<div class="vf-callout">' + ic('i-warn', 'icon-12') +
      '术语冲突：第 008 页 Region 2 机器译文把「車掌」译为「乘务员」，与术语表「列车长」冲突 · <b>1 条</b></div>';
    NM.REGIONS.forEach(function (r, i) {
      var cur = i === 2;
      h += '<button class="vf-row" data-region="' + r.n + '"' + (cur ? ' aria-current="true"' : '') + '>' +
        '<span class="r-idx">' + r.n + '</span>' +
        '<span class="r-type">' + r.cn + '</span>' +
        '<span class="r-src">' + esc(r.ocr) + '</span>' +
        '<span class="r-mt">' + esc(r.mt) + '</span>' +
        '<span class="r-ed"' + (r.ed ? '' : ' data-empty="1"') + '>' + esc(r.ed || '—') + '</span>' +
        '<span class="r-st"><span class="st-txt">' + stText(r.state) + (r.lock ? '·锁' : '') + '</span>' +
        '<span class="mk" data-st="' + stMap(r.state) + '"></span></span>' +
        '</button>';
    });
    h += '</div><div class="vf-hint"><span>Enter 确认</span><span>E 改译文</span><span>O 改原文</span>' +
      '<span>Ctrl+Enter 整页确认</span>' +
      '<span style="margin-left:auto">007 · 6 Region · 已确认 3 · 待确认 2 · 未审 1</span></div></div>';
    return h + '</div>';
  }

  function stMap(s) {
    return s === 'confirmed' ? 'completed' : s === 'needs_review' ? 'pending' : 'not_started';
  }
  function stText(s) {
    return s === 'confirmed' ? '已确认' : s === 'needs_review' ? '待确认' : '未审';
  }

  function surfInpaint(ui) {
    var masks = NM.REGIONS.map(function (r) { return r.geo; });
    var h = '<div class="ip">';

    h += '<div class="ip-pane"><div class="ip-pane-head">原图 ORIGINAL<span class="chip-route">source · 只读</span></div>' +
      '<div class="ip-canvas">' + art({ seed: 19, regions: NM.REGIONS, safe: true, tones: 3, txts: 3 }) + '</div>' +
      '<div class="ip-strip"><span class="lbl">页</span>' +
      [7, 17, 18, 19, 20, 21].map(function (n) {
        return '<button class="pg" data-page="' + NM.pad3(n) + '" data-f="' + (n === 19 ? 'failed' : '') + '"' + (n === 19 ? ' aria-current="true"' : '') + '>' + n + '</button>';
      }).join('') + '</div></div>';

    h += '<div class="ip-pane"><div class="ip-pane-head">修复后 CLEAN<span class="chip-route">anime_lama_v2</span></div>' +
      '<div class="ip-canvas">' + art({ seed: 19, clean: true, masks: masks, txts: 3 }) + '</div>' +
      '<div class="ip-strip"><span class="lbl">Mask</span>' +
      '<button class="pg" data-action="toggle-mask" aria-current="true">叠加</button>' +
      '<button class="pg" data-action="toggle-diff">差分</button>' +
      '<span class="lbl" style="margin-left:auto">覆盖 6/6</span></div></div>';

    h += '<div class="ip-side"><div class="ip-side-head">REGION · MASK</div><div class="ip-side-list">' +
      NM.REGIONS.map(function (r, i) {
        var stTxt = r.state === 'confirmed' ? 'OK' : r.state === 'needs_review' ? '检查' : '未审';
        return '<button class="ip-rgn" data-region="' + r.n + '"' + (i === 0 ? ' aria-current="true"' : '') + '>' +
          '<span class="k">' + r.n + '</span>' +
          '<span class="v">' + r.cn + '</span>' +
          '<span class="k">' + stTxt + '</span>' +
          '<span class="sub">' + r.geo.map(function (x) { return Math.round(x); }).join(', ') + ' %</span></button>';
      }).join('') + '</div>' +
      '<div class="ip-err">' + ic('i-warn', 'icon-12') +
      'p019 · <b>ModelLoadError</b>' +
      '<button class="btn sm" data-action="install-model">安装模型</button></div>' +
      '</div>';

    return h + '</div>';
  }

  function surfRender(pages) {
    var h = '<div class="gate-banner" data-tone="fail">' + ic('i-warn', 'icon-12') +
      'RENDER 门禁：<b>12</b> 页未修复，导出将缺失成品。' +
      '<button class="btn sm" data-action="gate-render">先修复</button>' +
      '<button class="btn sm" data-action="export-anyway">仍然导出</button></div>';
    h += '<div class="render-grid">';
    pages.forEach(function (p, i) {
      var missing = p.derived === 'failed' || (i >= 21);
      var overflow = i === 5 || i === 10;
      h += '<div class="rtile" role="button" tabindex="0" data-page="' + p.pid + '" data-missing="' + (missing ? 1 : 0) + '" aria-selected="' + (i === 6 ? 'true' : '') + '">' +
        art({ seed: 300 + i, txts: 1, tones: 1, rtxt: true, bub: true }) +
        '<div class="rt-foot"><span>' + p.pid + '</span><span>2×</span>' +
        (missing ? '<span class="na">缺失</span>' : overflow ? '<span class="ov">溢出</span>' : '<span style="margin-left:auto;color:var(--st-done)">OK</span>') +
        '</div></div>';
    });
    h += '</div>';
    h += '<div class="surf-foot"><span>已渲染</span><b>' + (NM.CHAPTER.pages - 5) + '/' + NM.CHAPTER.pages + '</b>' +
      '<span>· 缺失</span><b>3</b><span>· 溢出</span><b>2</b><span>· 字号自适应 shrink</span>' +
      '<span style="margin-left:auto">成品尺寸 1200×1800 · 输出 PNG</span></div>';
    return h;
  }

  function surfQueue(ui) {
    var h = '<div class="q-wrap">';
    h += '<div class="q-banner" data-tone="blocked"><span class="bar"></span>' +
      ic('i-lock', 'icon-12') + '<b>R-8828 blocked</b><span>Provider 认证失效（401）</span>' +
      '<span class="mono">影响 21 页 · 第9话</span>' +
      '<span class="acts"><button class="btn sm" data-action="open-provider">修复配置</button>' +
      '<button class="btn sm" data-action="resume-queue">修复后恢复</button></span></div>';
    h += '<div class="q-banner" data-tone="interrupted"><span class="bar"></span>' +
      ic('i-warn', 'icon-12') + '<b>R-8827 interrupted</b><span>异常退出 · 已完成 7/20 页</span>' +
      '<span class="mono">可继续</span>' +
      '<span class="acts"><button class="btn sm" data-action="resume-run">继续</button>' +
      '<button class="btn sm" data-action="discard-run">放弃</button></span></div>';

    h += '<div class="q-table-wrap"><table class="q-table"><thead><tr>' +
      '<th>Run</th><th>任务</th><th>范围</th><th>状态</th><th>进度</th><th>统计</th><th>耗时</th><th>当前</th>' +
      '</tr></thead><tbody>';
    NM.RUNS.forEach(function (r) {
      var cur = r.id === 'R-8831';
      h += '<tr data-run="' + r.id + '"' + (cur ? ' aria-current="true"' : '') + '>' +
        '<td class="id">' + r.id + '</td>' +
        '<td class="mono">' + r.task + '</td>' +
        '<td>' + esc(r.scope) + '</td>' +
        '<td><span class="q-state" data-s="' + r.state + '"><i class="m"></i>' + r.state + '</span></td>' +
        '<td><div class="q-prog"><span class="rail"><i data-s="' + r.state + '" style="width:' + r.pct + '%"></i></span>' +
        '<span class="pct">' + r.pct + '%</span></div></td>' +
        '<td class="num">' + r.completed + ' / ' + r.failed + ' / ' + r.waiting + '</td>' +
        '<td class="num">' + r.elapsed + '</td>' +
        '<td class="mono" style="max-width:180px;overflow:hidden;text-overflow:ellipsis">' + esc(r.current) + '</td>' +
        '</tr>';
    });
    h += '</tbody></table></div>';

    h += '<div class="q-foot">' +
      '<div class="q-block"><div class="lbl">当前 Run</div>' +
      '<div class="q-kv"><span>任务</span><b>translate_untranslated</b></div>' +
      '<div class="q-kv"><span>Step</span><b>5/9 · translate</b></div>' +
      '<div class="q-kv"><span>当前页</span><b>021.jpg</b></div></div>' +
      '<div class="q-block"><div class="lbl">计数</div>' +
      '<div class="q-kv"><span>完成</span><b class="ok">18</b></div>' +
      '<div class="q-kv"><span>失败</span><b class="bad">2</b></div>' +
      '<div class="q-kv"><span>跳过 / 等待</span><b class="warn">1 / 2</b></div></div>' +
      '<div class="q-block"><div class="lbl">并发与网络</div>' +
      '<div class="q-kv"><span>翻译 / 修复 / 网络</span><b>4 / 1 / 8</b></div>' +
      '<div class="q-kv"><span>代理</span><b>socks5://127.0.0.1:1080</b></div>' +
      '<div class="q-kv"><span>ETA</span><b>4m12s</b></div></div>' +
      '</div>';

    return h + '</div>';
  }

  /* ---------- 8. Run 状态带 ---------- */
  V.runstrip = function (ui) {
    var r = NM.RUNS[0];
    var paused = ui.runState === 'paused';
    return '<span class="rs-state"><span class="m"' + (paused ? ' style="animation:none;background:var(--st-blocked)"' : '') + '></span>' +
      'Run #' + r.id + ' · ' + (paused ? 'paused' : r.state) + '</span>' +
      '<span class="rs-meta"><b>' + r.pct + '%</b><span>· ' + r.elapsed + '</span>' +
      '<span>· 18/23 页</span><span class="warn">· failed ' + r.failed + '</span>' +
      '<span>· ETA ' + r.eta + 's</span><span>· ' + esc(r.current) + '</span></span>' +
      '<span class="rs-prog"><span class="bar"><i style="width:' + r.pct + '%"></i>' +
      '<span class="tick" style="left:78%"></span></span></span>' +
      '<span class="rs-acts">' +
      '<button class="iconbtn" data-action="' + (paused ? 'resume' : 'pause') + '" title="' + (paused ? '继续' : '暂停') + '">' +
      ic(paused ? 'i-play' : 'i-pause') + '</button>' +
      '<button class="iconbtn" data-action="stop" title="停止（已完成成果保留）">' + ic('i-stop') + '</button>' +
      '</span>' +
      '<button class="rs-exp" data-action="toggle-runpanel">' + ic('i-chev') + (ui.runOpen ? '收起' : '详情') + '</button>';
  };

  /* ---------- 9. Run 展开面板 ---------- */
  V.runpanel = function (ui) {
    var r = NM.RUNS[0];
    var h = '<div class="rp-block"><div class="rp-head">' + ic('i-list', 'icon-12') + '步骤 · step 5/9</div><div class="rp-body">' +
      '<div class="rp-steps">' + r.steps.map(function (s, i) {
        return '<div class="rp-step" data-s="' + s.s + '"><span class="k">' + ('0' + (i + 1)).slice(-2) + '</span>' +
          '<span>' + s.k + '</span><span class="mono">' + s.t + '</span></div>';
      }).join('') + '</div></div></div>';

    h += '<div class="rp-block"><div class="rp-head">' + ic('i-grid', 'icon-12') + '页状态 · 23</div><div class="rp-body">' +
      '<div class="rp-fail-grid">' + NM.PAGES.map(function (p) {
        return '<span class="rp-fail-cell" data-s="' + (p.derived === 'done' ? 'completed' : p.derived === 'review' ? 'pending' : p.derived) + '" title="' + p.pid + '">' +
          p.pid.slice(1) + '</span>';
      }).join('') + '</div>' +
      '<div class="rp-note" style="margin-top:var(--sp-2)">失败聚合（按错误码）</div>' +
      '<div class="rp-agg">' +
      '<div class="rp-agg-row"><span>ProviderRateLimitError · 018</span><b>1</b></div>' +
      '<div class="rp-agg-row"><span>ModelLoadError · 019</span><b>1</b></div>' +
      '<div class="rp-agg-row"><span>stale · render 020</span><b>1</b></div>' +
      '</div></div></div>';

    h += '<div class="rp-block"><div class="rp-head">' + ic('i-settings', 'icon-12') + '控制</div><div class="rp-body">' +
      '<div class="q-kv"><span>can_pause / can_continue / can_stop</span><b>true / false / true</b></div>' +
      '<div class="q-kv"><span>并发（翻译/修复）</span><b>4 / 1</b></div>' +
      '<div class="q-kv"><span>Provider</span><b>deepseek-v3</b></div>' +
      '<div class="q-kv"><span>修复模型</span><b>anime_lama_v2</b></div>' +
      '<div class="rp-note">暂停将在当前步骤（translate）安全结束后生效；停止会保留已完成成果并给出剩余未处理计数。</div>' +
      '<button class="btn" data-action="pause" style="margin-top:var(--sp-2)">' + ic('i-pause', 'icon-12') + '暂停（本步结束后）</button>' +
      '</div></div>';
    return h;
  };

  /* ---------- 10. 详情抽屉 ---------- */
  V.drawer = function (ui) {
    var d = ui.drawer;
    if (!d) return { head: '', body: '', foot: '' };
    var p = ui.pages[d.r];
    var st = p.states[d.c];
    var stage = NM.STAGES[d.c];
    var err = st === 'failed' ? (p.pid === '018' ? 'ProviderRateLimitError' : 'ModelLoadError') : '';
    var track = NM.TRACKS;

    var head = '<div class="dr-head"><div class="t"><b>' + p.pid + '.jpg · ' + stage.cn + '</b>' +
      '<span>' + stage.full + ' · ' + st + (err ? ' · ' + err : '') + '</span></div>' +
      '<span class="acts"><button class="iconbtn" data-action="drawer-close" title="关闭 (Esc)">' + ic('i-close') + '</button></span></div>';

    var body = '';

    /* 单元事实 */
    body += '<div class="dr-sec"><div class="lbl">单元事实<span class="mono">' + NM.CHAPTER.title + '</span></div>' +
      '<dl class="kv-grid">' +
      '<dt>页 / 阶段</dt><dd>' + p.pid + ' · ' + stage.full + '</dd>' +
      '<dt>状态</dt><dd>' + st + '</dd>' +
      '<dt>错误码</dt><dd' + (err ? ' style="color:var(--st-failed)"' : '') + '>' + (err || '—') + '</dd>' +
      '<dt>重试次数</dt><dd>' + (err ? '2 / 2（已放弃）' : '0 / 2') + '</dd>' +
      '<dt>Provider</dt><dd>' + (stage.k === 'ocr' ? 'manga_ocr' : stage.k === 'inpaint' || stage.k === 'mask_refine' ? 'anime_lama_v2' : 'deepseek-v3') + '</dd>' +
      '<dt>耗时</dt><dd>' + (st === 'running' ? '8.4s（进行中）' : st === 'not_started' ? '—' : '1.2s') + '</dd>' +
      '<dt>Revision</dt><dd>' + (st === 'completed' ? 'r5（current）' : '—') + '</dd>' +
      '<dt>Lock</dt><dd>' + (p.pid === '007' ? 'translation（R2）' : '—') + '</dd>' +
      '</dl>' +
      (err ? '<div class="rp-note" style="margin-top:var(--sp-2);color:var(--st-failed)">' + esc(NM.ERRORS[err].cn) + ' · 建议：' + esc(NM.ERRORS[err].fix) + '</div>' : '') +
      '</div>';

    /* 四轨 */
    body += '<div class="dr-sec"><div class="lbl">四轨完成度<span class="mono">原图 / 文本 / 修复 / 排版</span></div>' +
      '<div class="tracks">' + track.map(function (t) {
        return '<div class="track"><span class="tname">' + t.name + '</span>' +
          '<span class="tbar"><i data-s="' + t.st + '" style="width:' + t.pct + '%"></i></span>' +
          '<span class="tst" data-s="' + t.st + '">' + t.st + '</span></div>';
      }).join('') + '</div></div>';

    /* Region 明细（仅第 007 页有真实数据） */
    if (p.pid === '007') {
      body += '<div class="dr-sec"><div class="lbl">Region<span class="mono">6 个 · 命中 0.94</span></div>' +
        '<table class="dr-rgn"><thead><tr><th>#</th><th>类型</th><th>原文</th><th style="text-align:right">审阅</th></tr></thead><tbody>' +
        NM.REGIONS.map(function (r) {
          return '<tr' + (r.n === 3 ? ' aria-current="true"' : '') + '><td class="n">' + r.n + '</td>' +
            '<td class="t">' + r.cn + '</td><td>' + esc(r.ocr) + '</td>' +
            '<td class="s">' + stText(r.state) + '</td></tr>';
        }).join('') + '</tbody></table></div>';

      body += '<div class="dr-sec"><div class="lbl">Revision<span class="mono">Region 2</span></div>' +
        '<div class="rev-list">' + NM.REVS.map(function (r) {
          return '<div class="rev"' + (r.cur ? ' aria-current="true"' : '') + '>' +
            '<span class="r">' + r.r + '</span><span class="tm">' + r.t + '</span>' +
            '<span class="sd">' + esc(r.what) + '</span>' +
            '<span class="tag">' + (r.tag || r.from) + '</span></div>';
        }).join('') + '</div></div>';
    } else {
      body += '<div class="dr-sec"><div class="lbl">Region<span class="mono">' + (p.regions || 0) + ' 个</span></div>' +
        '<div class="rp-note">该页 Region 明细按需加载（原型内仅第 007 页提供完整 Region 数据，见 00_SAMPLE_DATA §3）。</div>' +
        '<div class="rev-list" style="margin-top:var(--sp-2)">' +
        '<div class="rev"><span class="r">r3</span><span class="tm">14:05</span><span class="sd">translate 覆盖</span><span class="tag">pipeline</span></div>' +
        '<div class="rev"><span class="r">r2</span><span class="tm">13:40</span><span class="sd">' + stage.full + ' 完成</span><span class="tag">pipeline</span></div>' +
        '<div class="rev"><span class="r">r1</span><span class="tm">13:31</span><span class="sd">初识别</span><span class="tag">pipeline</span></div>' +
        '</div></div>';
    }

    var foot = '<div class="dr-foot">' +
      (err ? '<button class="btn" data-action="retry-one" data-tone="danger">' + ic('i-retry', 'icon-12') + '重试该阶段</button>' : '') +
      '<button class="btn" data-action="advance-one">' + ic('i-arrow', 'icon-12') + '推进</button>' +
      '<button class="btn" data-action="skip-one">' + ic('i-skip', 'icon-12') + '跳过</button>' +
      '<button class="btn" data-action="switch-provider">' + ic('i-settings', 'icon-12') + '换 Provider</button>' +
      '<button class="btn" data-action="open-log">' + ic('i-list', 'icon-12') + '日志</button>' +
      '</div>';

    return { head: head, body: body, foot: foot };
  };

  /* ---------- 11. 状态演示面板 ---------- */
  V.states = function (ui) {
    var head = '<div class="st-head"><span class="t">状态真相</span><span class="mono">12 / 12</span>' +
      '<button class="iconbtn" data-action="states-close" style="margin-left:auto" title="关闭">' + ic('i-close') + '</button></div>';
    var body = '<div class="st-body">' + NM.STATES.map(function (s) {
      var on = ui.state === s.key;
      return '<button class="st-item" data-state="' + s.key + '"' + (on ? ' aria-current="true"' : '') + '>' +
        '<span class="n">' + s.n + '</span>' +
        '<span><span class="tt">' + s.t + '</span><span class="dd">' + esc(s.d) + '<br>' +
        '<code>' + esc(s.act) + '</code></span></span>' +
        '<span class="n">' + (on ? '●' : '') + '</span></button>';
    }).join('') + '</div>';
    var foot = '<div class="st-foot">' +
      '<button class="btn sm" data-action="state-next">' + ic('i-arrow', 'icon-12') + '下一个</button>' +
      '<button class="btn sm" data-action="state-clear">' + ic('i-close', 'icon-12') + '复位</button>' +
      '<span class="lbl" style="margin-left:auto">URL ?state=</span></div>';
    return { head: head, body: body, foot: foot };
  };

  /* ---------- 12. 命令面板 ---------- */
  V.palette = function (ui) {
    var q = (ui.palQ || '').toLowerCase();
    var items = NM.CMD.filter(function (c) {
      return !q || (c.label + ' ' + c.g + ' ' + c.kk).toLowerCase().indexOf(q) >= 0;
    });
    var h = '<div class="pal-input">' + ic('i-search') +
      '<input id="palInput" type="text" placeholder="搜索或执行：阶段 / 批量 / 筛选 / 视图 / 运行" value="' + esc(ui.palQ || '') + '" autocomplete="off" spellcheck="false">' +
      '<span class="scope-tag">' + esc(NM.BATCH.id) + ' · ' + NM.CHAPTER.pages + ' 页</span></div>';
    h += '<div class="pal-list">';
    var lastG = '';
    if (!items.length) h += '<div class="pal-group">无匹配命令</div>';
    items.forEach(function (c, i) {
      if (c.g !== lastG) { h += '<div class="pal-group">' + c.g + '</div>'; lastG = c.g; }
      var on = i === ui.palActive;
      h += '<button class="pal-item" data-cmd="' + esc(c.label) + '" data-active="' + (on ? 1 : 0) + '">' +
        ic(c.icon) + '<span>' + c.label + '</span>' +
        '<span class="sc">' + c.g + '</span><span class="kk">' + (c.kk || '') + '</span></button>';
    });
    h += '</div>';
    h += '<div class="pal-foot"><span>↑↓ 移动</span><span>Enter 执行</span><span>Esc 关闭</span>' +
      '<span style="margin-left:auto">' + items.length + ' / ' + NM.CMD.length + '</span></div>';
    return h;
  };

  /* ---------- 13. 对话框 ---------- */
  V.dialog = function (spec) {
    var head = '<div class="dlg-head"><div class="kicker' + (spec.ok ? ' ok' : '') + '">' + esc(spec.kicker) + '</div>' +
      '<h2>' + esc(spec.title) + '</h2></div>';
    var body = '<div class="dlg-body">' + spec.body + '</div>';
    var foot = '<div class="dlg-foot">' +
      (spec.actions || []).map(function (a, i) {
        return '<button class="btn' + (i === 0 ? '' : '') + '" data-dlg="' + a.act + '"' +
          (a.tone ? ' data-tone="' + a.tone + '"' : '') + '>' + a.label + '</button>';
      }).join('') +
      '<span class="spacer"></span><button class="btn sm" data-dlg="cancel">取消 (Esc)</button></div>';
    return { head: head, body: body, foot: foot };
  };

})(window.NM);
