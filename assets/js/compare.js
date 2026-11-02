(function () {
  var D = JSON.parse(document.getElementById('cmp-data').textContent);
  var T = D.t, lang = D.lang, rel = D.rel;
  var by = {};
  D.classes.forEach(function (c) { by[c.slug] = c; });
  var picks = Array.prototype.slice.call(document.querySelectorAll('[data-pick]'));
  var spotSel = document.getElementById('spot');
  var defaults = ['storm_blaster', 'sagittarius', 'orc_rider_3'];

  function fmt(v, dec) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    var s = Number(v).toLocaleString(lang === 'en' ? 'en-US' : (lang === 'ru' ? 'ru-RU' : 'uk-UA'),
      { maximumFractionDigits: dec || 0, minimumFractionDigits: 0 });
    return s;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (ch) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]; }); }
  function pps(c) { var s = c.spam; return s && s.pw && s.cd ? s.pw * s.h / s.cd : null; }

  function sel() { return picks.map(function (p) { return by[p.value]; }).filter(Boolean); }

  function head(cs) {
    return '<thead><tr><th></th>' + cs.map(function (c) {
      return '<th><a href="' + rel + lang + '/class/' + c.slug + '/" style="display:flex;gap:10px;align-items:center;color:var(--text);white-space:normal">' +
        '<img class="ico" src="' + rel + 'assets/icons/classes/' + c.slug + '.webp" alt="" width="32" height="32">' + esc(c.name) + '</a></th>';
    }).join('') + '</tr></thead>';
  }

  function render() {
    var cs = sel();
    var archs = {}; cs.forEach(function (c) { archs[c.arch] = 1; });
    document.getElementById('mix').hidden = Object.keys(archs).length < 2;
    var max = Math.max.apply(null, cs.map(function (c) { return pps(c) || 0; }).concat([1]));
    var rows = [
      [T.cmp_race, function (c) { return esc(c.race); }],
      [T.cmp_spam, function (c) {
        var s = c.spam; if (!s) return '—';
        return '<b>' + esc(s.name) + '</b><div class="muted small">' + s.h + ' × ' + fmt(s.pw) + ' · ' + fmt(s.cd, 2) + ' ' + T.sec + '</div>';
      }],
      [T.cmp_pps, function (c) {
        var v = pps(c); if (!v) return '—';
        return '<div style="display:flex;align-items:center;gap:10px"><span style="width:64px">' + fmt(v) + '</span><span class="bar"><i style="width:' + Math.round(100 * v / max) + '%"></i></span></div>';
      }],
      [T.cmp_aoe, function (c) {
        var a = c.aoe; if (!a) return '—';
        return '<b>' + esc(a.name) + '</b><div class="muted small">' + a.h + ' × ' + fmt(a.pw) + ' · ' + T.targets_n.replace('{n}', a.lim || '—') + ' · ' + fmt(a.cd) + ' ' + T.sec + '</div>';
      }],
      [T.cmp_mp, function (c) { return c.spam && c.spam.mp ? fmt(c.spam.mp) : '—'; }],
      [T.cmp_books, function (c) { return c.books['1'] + ' / ' + c.books['2'] + ' / ' + c.books['3']; }]
    ];
    document.getElementById('cmp-skills').innerHTML = head(cs) + '<tbody>' + rows.map(function (r) {
      return '<tr><th scope="row" style="white-space:normal">' + r[0] + '</th>' + cs.map(function (c) { return '<td>' + r[1](c) + '</td>'; }).join('') + '</tr>';
    }).join('') + '</tbody>';

    var spot = spotSel.value;
    var mrows = [[T.m_exp, 'exp'], [T.m_adena, 'adena'], [T.m_lcoin, 'lcoin'], [T.m_mobs, 'kills'], [T.m_gs, 'gs'], [T.m_n, 'n']];
    var anyData = cs.some(function (c) { return c.farm[spot]; });
    var body = anyData ? mrows.map(function (r) {
      return '<tr><th scope="row">' + r[0] + '</th>' + cs.map(function (c) {
        var f = c.farm[spot]; return '<td class="num">' + (f ? fmt(f[r[1]]) : '—') + '</td>';
      }).join('') + '</tr>';
    }).join('') : '<tr><td colspan="' + (cs.length + 1) + '" class="muted" style="text-align:center;padding:20px 8px">' + T.no_meas_short + '</td></tr>';
    document.getElementById('cmp-meas').innerHTML = head(cs) + '<tbody>' + body + '</tbody>';

    try {
      var u = new URL(location.href);
      u.searchParams.set('c', cs.map(function (c) { return c.slug; }).join(','));
      u.searchParams.set('spot', spot);
      history.replaceState(null, '', u);
    } catch (e) {}
  }

  var params = new URLSearchParams(location.search);
  var init = (params.get('c') || '').split(',').filter(function (s) { return by[s]; });
  picks.forEach(function (p, i) { p.value = init[i] || defaults[i]; p.addEventListener('change', render); });
  if (params.get('spot')) spotSel.value = params.get('spot');
  spotSel.addEventListener('change', render);
  render();
})();
