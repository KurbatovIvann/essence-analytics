(function () {
  // tier tabs
  var tabs = document.querySelectorAll('[role=tab][data-tab]');
  function pick(id, focus) {
    tabs.forEach(function (b) {
      var on = b.getAttribute('data-tab') === id;
      b.setAttribute('aria-selected', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
      document.getElementById('panel-' + b.getAttribute('data-tab')).hidden = !on;
      if (on && focus) b.focus();
    });
    try { history.replaceState(null, '', '#' + id); } catch (e) {}
  }
  tabs.forEach(function (b, i) {
    b.addEventListener('click', function () { pick(b.getAttribute('data-tab')); });
    b.addEventListener('keydown', function (ev) {
      var d = ev.key === 'ArrowRight' ? 1 : ev.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      var n = tabs[(i + d + tabs.length) % tabs.length];
      pick(n.getAttribute('data-tab'), true);
    });
  });
  var h = location.hash.slice(1);
  if (h && document.getElementById('panel-' + h)) pick(h);

  // class search
  var q = document.getElementById('cls-search');
  if (!q) return;
  var empty = document.getElementById('cls-empty');
  q.addEventListener('input', function () {
    var v = q.value.trim().toLowerCase(), any = false;
    document.querySelectorAll('[data-race]').forEach(function (r) {
      var shown = 0;
      r.querySelectorAll('a[data-name]').forEach(function (a) {
        var ok = !v || a.getAttribute('data-name').indexOf(v) !== -1;
        a.hidden = !ok; if (ok) shown++;
      });
      r.hidden = shown === 0; if (shown) any = true;
    });
    empty.hidden = any;
  });
})();
