(function () {
  var D = JSON.parse(document.getElementById('lv-data').textContent);
  var loc = D.lang === 'en' ? 'en-US' : (D.lang === 'ru' ? 'ru-RU' : 'uk-UA');
  var rate = document.getElementById('rate'), trials = document.getElementById('trials');
  function fmt(v, d) { return Number(v).toLocaleString(loc, { maximumFractionDigits: d || 0 }); }
  function load() {
    try { var s = JSON.parse(localStorage.getItem('lv') || '{}'); if (s.rate) rate.value = s.rate; if (s.trials != null) trials.value = s.trials; } catch (e) {}
  }
  function render() {
    var r = Math.max(0.1, parseFloat(rate.value) || 0) * 1e6;
    var total = 0;
    document.querySelectorAll('#lv tbody tr').forEach(function (tr) {
      var g = +tr.getAttribute('data-grind'); total += g;
      tr.querySelector('[data-hours]').textContent = g ? fmt(g / r, 1) : '—';
    });
    var n = +trials.value, bonus = 0;
    for (var i = 0; i < n; i++) bonus += D.trials[i] * 1e6;
    var left = Math.max(0, total - bonus);
    document.getElementById('r-total').textContent = fmt(left / 1e6);
    document.getElementById('r-hours').textContent = fmt(left / r, 1);
    try { localStorage.setItem('lv', JSON.stringify({ rate: rate.value, trials: trials.value })); } catch (e) {}
  }
  load();
  rate.addEventListener('input', render);
  trials.addEventListener('change', render);
  render();
})();
