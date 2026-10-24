/* =============================================================================
   New Manga · 方向 C「工坊 Atelier」· data.js
   唯一假数据源：严格对齐 30-prototype/00_SAMPLE_DATA.md（第1/2/3/5/6/7/8/9 节）。
   本文件不含任何 DOM 操作，只导出 window.NM.* 数据与纯函数。
   ============================================================================= */
'use strict';

window.NM = window.NM || {};

/* ---------- 1. 阶段（11 个，取自 10_UX_FOUNDATION §4.1） ---------- */
NM.STAGES = [
  { k: 'detect', ab: 'DET', cn: '检测', full: 'detect' },
  { k: 'ocr', ab: 'OCR', cn: '识别', full: 'ocr' },
  { k: 'color', ab: 'CLR', cn: '色彩', full: 'color' },
  { k: 'term', ab: 'TERM', cn: '术语', full: 'term_extract' },
  { k: 'translate', ab: 'TRAN', cn: '翻译', full: 'translate' },
  { k: 'segment', ab: 'SEG', cn: '切分', full: 'segment' },
  { k: 'mask_refine', ab: 'MASK', cn: '掩膜', full: 'mask_refine' },
  { k: 'inpaint', ab: 'INP', cn: '修复', full: 'inpaint' },
  { k: 'render', ab: 'REND', cn: '渲染', full: 'render' },
  { k: 'review', ab: 'REV', cn: '确认', full: 'review' },
  { k: 'export', ab: 'EXP', cn: '导出', full: 'export' }
];

/* ---------- 2. 阶段轨道（6 个工作面 Tab） ---------- */
NM.TABS = [
  { k: 'detect', idx: '01', name: 'DETECT', cn: '检测', icon: 'i-detect', pct: 92, ab: 0, gate: 'ok' },
  { k: 'ocr', idx: '02', name: 'OCR', cn: '识别', icon: 'i-ocr', pct: 78, ab: 2, gate: 'warn' },
  { k: 'verify', idx: '03', name: 'VERIFY', cn: '校对', icon: 'i-verify', pct: 41, ab: 3, gate: 'warn' },
  { k: 'inpaint', idx: '04', name: 'INPAINT', cn: '修复', icon: 'i-inpaint', pct: 63, ab: 4, gate: 'fail' },
  { k: 'render', idx: '05', name: 'RENDER', cn: '排版', icon: 'i-render', pct: 52, ab: 9, gate: 'fail' },
  { k: 'queue', idx: 'Q', name: 'QUEUE', cn: '队列', icon: 'i-queue', pct: 100, ab: 0, gate: 'ok' }
];

/* ---------- 3. 批次与概览计数（范围=批次 B-012；允许类别重叠） ---------- */
NM.BATCH = {
  id: 'B-012',
  scope: '第1–10章',
  pages: 240,
  chapters: 10,
  done: 182,
  failed: 12,
  stale: 6,
  review: 40,
  blocked: 0,
  running: 1
};

NM.CHIPS = [
  { k: 'all', label: '页', n: 240, unit: '页', kind: '' },
  { k: 'done', label: '完成', n: 182, unit: '', kind: 'done' },
  { k: 'failed', label: '失败', n: 12, unit: '', kind: 'failed' },
  { k: 'stale', label: '过期', n: 6, unit: '', kind: 'stale' },
  { k: 'review', label: '待确认', n: 40, unit: '', kind: 'review' },
  { k: 'blocked', label: '阻塞', n: 0, unit: '', kind: 'running' }
];

/* ---------- 4. 第12话 23 页 × 11 阶段（00_SAMPLE_DATA §2 的真实分布） ---------- */
var D = 'completed', N = 'not_started', R = 'running', S = 'stale', F = 'failed', K = 'skipped', P = 'pending';

function allDone(regions, review) {
  var a = [];
  for (var i = 0; i < 11; i++) a.push(D);
  if (review === 'needs_review') a[9] = P, a[10] = K;
  return { states: a, regions: regions, review: review };
}

NM.PAGES = [];
(function buildPages() {
  var regionsOf = [6, 7, 5, 8, 6, 7, 9, 6, 5, 8, 7, 6, 8, 5, 7, 6];
  for (var i = 1; i <= 16; i++) {
    var p = allDone(regionsOf[i - 1], 'confirmed');
    NM.PAGES.push({
      pid: pad3(i), states: p.states, regions: p.regions,
      review: 'confirmed', derived: 'done', event: '已确认 · r' + (2 + (i % 4)),
      note: '第' + (i <= 8 ? '一' : '二') + '批'
    });
  }
  // 017 已完成 · 待确认（3 条 needs_review）
  var p17 = allDone(7, 'needs_review');
  NM.PAGES.push({ pid: '017', states: p17.states, regions: 7, review: 'needs_review', derived: 'review', event: '待确认 3 条 · needs_review' });
  // 018 翻译失败 ProviderRateLimitError（2 次重试后放弃）
  NM.PAGES.push({
    pid: '018', states: [D, D, D, D, F, K, K, K, K, P, K], regions: 7, review: 'unreviewed',
    derived: 'failed', event: 'translate · ProviderRateLimitError'
  });
  // 019 修复失败 ModelLoadError（anime_lama_v2 权重缺失）
  NM.PAGES.push({
    pid: '019', states: [D, D, D, D, D, D, D, F, K, P, K], regions: 8, review: 'unreviewed',
    derived: 'failed', event: 'inpaint · ModelLoadError'
  });
  // 020 过期：用户在 019 改了 Region 几何 → 该页 render 过期
  NM.PAGES.push({
    pid: '020', states: [D, D, D, D, D, D, D, D, S, P, K], regions: 6, review: 'unreviewed',
    derived: 'stale', event: 'render 过期 ← p019 geometry'
  });
  // 021 处理中：translate 62%
  NM.PAGES.push({
    pid: '021', states: [D, D, D, D, R, N, N, N, N, N, N], regions: 9, review: 'unreviewed',
    derived: 'running', event: 'translate step 5/9 · 62%'
  });
  // 022–023 未处理
  NM.PAGES.push({ pid: '022', states: [N, N, N, N, N, N, N, N, N, N, N], regions: 0, review: 'unreviewed', derived: 'not_started', event: '—' });
  NM.PAGES.push({ pid: '023', states: [N, N, N, N, N, N, N, N, N, N, N], regions: 0, review: 'unreviewed', derived: 'not_started', event: '—' });
})();

/* 本章汇总（与 00_SAMPLE_DATA §2 一致；类别允许重叠：完成含过期/待确认） */
NM.CHAPTER = {
  id: 'c12', title: '第12话「雨の停車場」', book: '夜光列车', pages: 23,
  done: 18, failed: 2, stale: 1, review: 3, running: 1, notStart: 2
};

/* ---------- 5. 其余章节（次要条目，仅用于资源树 / 矩阵切换的真实感） ---------- */
NM.CHAPTERS = [
  { id: 'c09', title: '第9话「灯台守」', pages: 21, under: '夜光列车' },
  { id: 'c10', title: '第10话「終電」', pages: 22, under: '夜光列车' },
  { id: 'c11', title: '第11话「踏切」', pages: 20, under: '夜光列车' },
  { id: 'c12', title: '第12话「雨の停車場」', pages: 23, under: '夜光列车' },
  { id: 'c13', title: '第13话「回送」', pages: 19, under: '夜光列车' }
];

/* 确定性伪随机：为次要章节生成"可信但不参与演示"的状态分布 */
NM.genChapter = function (ch) {
  var seed = 7;
  for (var i = 0; i < ch.id.length; i++) seed = (seed * 33 + ch.id.charCodeAt(i)) % 99991;
  function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
  var out = [];
  for (var p = 1; p <= ch.pages; p++) {
    var states = [], r = rnd(), x;
    for (x = 0; x < 11; x++) {
      if (r < 0.74) states.push(D);
      else if (r < 0.80) states.push(rnd() < 0.5 ? F : S);
      else if (r < 0.90) states.push(N);
      else if (r < 0.95) states.push(K);
      else states.push(P);
    }
    out.push({
      pid: pad3(p), states: states, regions: 4 + Math.floor(rnd() * 6),
      review: 'confirmed', derived: derive(states), event: '—'
    });
  }
  return out;
};

/* ---------- 6. 派生状态（行级"主状态"） ---------- */
function derive(states) {
  var has = function (v) { return states.indexOf(v) >= 0; };
  if (has(F)) return 'failed';
  if (has(S)) return 'stale';
  if (has(R)) return 'running';
  if (has(P) && !has(N)) return 'review';
  if (!has(N)) return 'done';
  if (states.every(function (s) { return s === N; })) return 'not_started';
  return 'partial';
}
NM.derive = derive;

/* ---------- 7. Region（00_SAMPLE_DATA §3，第 007 页核心演示数据） ---------- */
/* geo = 相对页面 1200×1800 的百分比 [left, top, width, height] */
NM.REGIONS = [
  { n: 1, type: 'speech', cn: '对白', geo: [12.33, 11.67, 26.83, 14.89], ocr: 'おはよう、また会えたね', mt: '早上好，又见面了呢', ed: '', state: 'confirmed', lock: '' },
  { n: 2, type: 'speech', cn: '对白', geo: [51.0, 10.33, 25.0, 13.56], ocr: 'この雨、三日は止まないらしい', mt: '这场雨，好像三天都不会停', ed: '这场雨，恐怕要下三天', state: 'confirmed', lock: 'translation' },
  { n: 3, type: 'narration', cn: '旁白', geo: [11.67, 31.11, 53.33, 5.33], ocr: '三日後の朝', mt: '三天后的早晨', ed: '', state: 'needs_review', lock: '' },
  { n: 4, type: 'sfx', cn: '拟声', geo: [58.33, 35.56, 21.67, 10.0], ocr: 'ザァァァ', mt: '—（SFX 策略 skip）', ed: '', state: 'unreviewed', lock: 'region' },
  { n: 5, type: 'speech', cn: '对白', geo: [35.83, 54.44, 24.67, 12.89], ocr: '切符をなくした', mt: '我把车票弄丢了', ed: '', state: 'confirmed', lock: '' },
  { n: 6, type: 'note', cn: '注释', geo: [10.0, 86.67, 35.0, 6.67], ocr: '※時刻表は変更されています', mt: '※时刻表已更改', ed: '', state: 'needs_review', lock: '' }
];

/* 四轨（10_UX_FOUNDATION §3） */
NM.TRACKS = [
  { name: '原图轨', cn: 'Original', pct: 100, st: 'completed', txt: 'source' },
  { name: '文本轨', cn: 'Text', pct: 86, st: 'running', txt: 'needs_review' },
  { name: '修复轨', cn: 'Inpaint', pct: 100, st: 'completed', txt: 'clean' },
  { name: '排版轨', cn: 'Render', pct: 62, st: 'stale', txt: 'stale' }
];

/* ---------- 8. OCR 质量桶（桶值 4/3/2/1/0 = 置信度区间） ---------- */
NM.OCR_BUCKETS = [
  { lv: 4, label: '≥0.95 可直接用', cn: '高' },
  { lv: 3, label: '0.80–0.95 建议抽查', cn: '中' },
  { lv: 2, label: '0.60–0.80 需人工', cn: '低' },
  { lv: 1, label: '<0.60 多半错', cn: '可疑' },
  { lv: 0, label: '无文本 / 跳过', cn: '空' }
];

NM.ocrRows = function (pages) {
  return pages.map(function (p, i) {
    var lv = p.states[1] === D ? (i % 5 === 3 ? 3 : 4) : (p.states[1] === F ? 1 : p.states[1] === N ? 0 : 2);
    return {
      pid: p.pid,
      regions: p.regions,
      conf: lv === 4 ? '0.97' : lv === 3 ? '0.88' : lv === 2 ? '0.71' : lv === 1 ? '0.43' : '—',
      lv: lv,
      low: lv <= 2 ? 1 + (i % 3) : 0,
      flag: lv <= 2,
      act: lv <= 2 ? '重 OCR' : '查看'
    };
  });
};

/* ---------- 9. Run / 队列（00_SAMPLE_DATA §5） ---------- */
NM.RUNS = [
  {
    id: 'R-8831', task: 'translate_untranslated', scope: '第12话 · 23 页', state: 'running', pct: 62,
    elapsed: '12:07', eta: '4m12', total: 23, completed: 18, failed: 2, skipped: 1, waiting: 2,
    current: '021 translate 5/9', canPause: true, canStop: true,
    steps: [
      { k: 'detect', s: 'completed', t: '0.4s' }, { k: 'ocr', s: 'completed', t: '1.1s' },
      { k: 'color', s: 'completed', t: '0.2s' }, { k: 'term', s: 'completed', t: '0.3s' },
      { k: 'translate', s: 'running', t: '8.4s' }, { k: 'segment', s: 'pending', t: '—' },
      { k: 'mask_refine', s: 'pending', t: '—' }, { k: 'inpaint', s: 'pending', t: '—' },
      { k: 'render', s: 'pending', t: '—' }
    ]
  },
  { id: 'R-8830', task: 'reinpaint_selected', scope: '第11话 · 5 页', state: 'completed', pct: 100, elapsed: '1:52', eta: '—', total: 5, completed: 5, failed: 0, skipped: 0, waiting: 0, current: '—' },
  { id: 'R-8829', task: 'rerender_all', scope: '第10话', state: 'completed_with_failures', pct: 100, elapsed: '3:41', eta: '—', total: 22, completed: 21, failed: 1, skipped: 0, waiting: 0, current: 'OutputMappingError p014' },
  { id: 'R-8828', task: 'translate_all', scope: '第9话', state: 'blocked', pct: 0, elapsed: '0:00', eta: '—', total: 21, completed: 0, failed: 0, skipped: 0, waiting: 21, current: 'Provider 认证失效（401）' },
  { id: 'R-8827', task: 'translate_all', scope: '第8话', state: 'interrupted', pct: 37, elapsed: '5:19', eta: '—', total: 20, completed: 7, failed: 0, skipped: 0, waiting: 13, current: '异常退出 · 可继续' }
];

/* ---------- 10. 错误码（00_SAMPLE_DATA §6） ---------- */
NM.ERRORS = {
  ProviderRateLimitError: { cn: 'Provider 限流，重试 2 次后失败', fix: '降低并发 / 换 Provider / 稍后重试' },
  ModelLoadError: { cn: '修复模型权重缺失：anime_lama_v2', fix: '安装模型 / 换修复路线' },
  MissingOCRText: { cn: '该 Region 无有效 OCR 文本', fix: '先重 OCR 再翻译' },
  LockBlocked: { cn: '目标被 Region Lock 阻止', fix: '解锁或改用显式覆盖' },
  INPUT_REVISION_CHANGED: { cn: '输入版本已变更（乐观锁冲突）', fix: '刷新后重试' },
  ProxyConnectionError: { cn: '代理连接失败（socks5://127.0.0.1:1080）', fix: '检查代理 / 切直连' },
  OutputMappingError: { cn: '成品页映射失败：页码与输出不一致', fix: '重渲染该页 / 检查输出模板' }
};

/* ---------- 11. 术语表（§7） ---------- */
NM.GLOSSARY = [
  { src: '夜光列車', dst: '夜光列车', type: '术语 · 专名', scope: '作品', from: '人工' },
  { src: '車掌', dst: '列车长', type: '术语 · 职业', scope: '作品', from: '人工' },
  { src: '停留所', dst: '站点', type: '术语 · 场所', scope: '作品', from: '自动识别' },
  { src: 'ザァァァ', dst: '（不译）', type: '不译 · 拟声', scope: '章节', from: '人工' }
];

/* ---------- 12. Revision（§8，第 007 页 Region 2） ---------- */
NM.REVS = [
  { r: 'r5', t: '14:22', from: '人工', what: '译文改为「这场雨，恐怕要下三天」', tag: 'current', cur: true },
  { r: 'r4', t: '14:05', from: 'pipeline', what: 'translate 覆盖（machine）', tag: 'needs_review', cur: false },
  { r: 'r3', t: '13:58', from: '人工', what: '字号 +1，溢出策略 → shrink', tag: '', cur: false },
  { r: 'r2', t: '13:40', from: 'pipeline', what: 'inpaint 完成（BrushNet）', tag: '', cur: false },
  { r: 'r1', t: '13:31', from: 'pipeline', what: 'OCR 初识别', tag: '', cur: false }
];

/* ---------- 13. 12 状态真相（13_STATE_MODELS §3） ---------- */
NM.STATES = [
  { n: '01', key: 'empty', t: '空工作区', d: '数据根路径 + 导入入口 + 首次引导', act: '导入文件 / 导入文件夹 / 打开设置' },
  { n: '02', key: 'importing', t: '导入中 / 部分失败', d: '每文件状态 + 总进度 + 成功/失败计数', act: '取消 / 查看失败文件 / 重试失败项' },
  { n: '03', key: 'chapter_empty', t: '章节无页面 / 页面无 Region', d: '本章还没有页面；或页内未检测到文字区域', act: '导入页面 / 手动新建 Region / 重检测' },
  { n: '04', key: 'running', t: '流水线运行中', d: 'Run #R-8831 · step 5/9 · 18/23 页', act: '暂停 / 停止 / 查看失败' },
  { n: '05', key: 'paused', t: '暂停中', d: '当前步骤安全结束后暂停 · 已完成 18', act: '继续 / 停止' },
  { n: '06', key: 'done_with_fail', t: '完成但有失败', d: 'completed_with_failures · 成果已保留 · 失败 2', act: '只重试失败 / 查看报告' },
  { n: '07', key: 'blocked', t: '阻塞', d: 'blocked · Provider 认证失效 · 影响 21 页', act: '跳转修复配置 / 修复后恢复' },
  { n: '08', key: 'resume', t: '中断恢复', d: '上次中断的 Run R-8827 与范围（第8话 20 页）', act: '继续 / 重新开始 / 放弃' },
  { n: '09', key: 'partial', t: 'Region 部分完成', d: '同一页 9 个 Region：OCR 全完成，1 个翻译失败', act: '只重试该 Region / 换 Provider' },
  { n: '10', key: 'stale', t: '过期 stale', d: '上游几何变更 → render/save 过期，历史版本保留', act: '重跑过期项 / 查看过期原因' },
  { n: '11', key: 'review_backlog', t: '待确认积压', d: '40 条待确认 · 按页/章分布 · 当前位置', act: '逐条确认 / 批量确认（显示影响面）' },
  { n: '12', key: 'danger', t: '危险确认', d: '影响对象数量 + 可撤销性 + 不可逆警告', act: '确认执行 / 取消（Esc 可退）' },
  /* 补充（13_STATE_MODELS §3 标准 12 状态中，被 #02/#03 合并的三项在此单列，保证规范可逐项演示） */
  { n: '补1', key: 'import_part_fail', sup: true, t: '导入部分失败', d: '失败文件列表与原因（格式不支持 / 重复页）', act: '重试失败项 / 跳过继续' },
  { n: '补2', key: 'page_no_region', sup: true, t: '页面无 Region', d: '未检测到文字区域 · 置信阈值 0.30', act: '手动新建 Region / 降低阈值重检测' }
];

/* ---------- 14. 工具 ---------- */
function pad3(n) { return ('000' + n).slice(-3); }
NM.pad3 = pad3;

NM.CMD = [
  { g: '阶段', icon: 'i-detect', label: '切到 DETECT 检测', kk: '1' },
  { g: '阶段', icon: 'i-ocr', label: '切到 OCR 识别', kk: '2' },
  { g: '阶段', icon: 'i-verify', label: '切到 VERIFY 校对', kk: '3' },
  { g: '阶段', icon: 'i-inpaint', label: '切到 INPAINT 修复', kk: '4' },
  { g: '阶段', icon: 'i-render', label: '切到 RENDER 排版', kk: '5' },
  { g: '阶段', icon: 'i-queue', label: '切到 QUEUE 队列', kk: 'Q' },
  { g: '批量', icon: 'i-retry', label: '重试选中失败单元', kk: 'Ctrl+Shift+R' },
  { g: '批量', icon: 'i-skip', label: '跳过选中单元', kk: 'Ctrl+Shift+K' },
  { g: '批量', icon: 'i-arrow', label: '推进所选到下一阶段', kk: 'Ctrl+Enter' },
  { g: '批量', icon: 'i-export', label: '导出批次 B-012', kk: 'Ctrl+E' },
  { g: '筛选', icon: 'i-filter', label: '矩阵筛选：只看失败', kk: '' },
  { g: '筛选', icon: 'i-filter', label: '矩阵筛选：只看过期', kk: '' },
  { g: '视图', icon: 'i-grid', label: '矩阵最大化', kk: '' },
  { g: '视图', icon: 'i-eye', label: '打开状态演示面板（12 状态真相）', kk: 'S' },
  { g: '视图', icon: 'i-sun', label: '切换深/浅主题', kk: 'T' },
  { g: '运行', icon: 'i-pause', label: '暂停当前 Run', kk: '' },
  { g: '运行', icon: 'i-stop', label: '停止当前 Run', kk: '' },
  { g: '运行', icon: 'i-play', label: '恢复队列', kk: '' }
];
