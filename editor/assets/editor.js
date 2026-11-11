/* Live-Editor – nur im Editor-Build (python3 editor.py), nie auf der Live-Seite */
(function () {
  'use strict';
  var E = window.__ED__, d = document;
  if (!E) return;

  function el(tag, attrs, kids) {
    var n = d.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'class') n.className = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else if (k.indexOf('on') === 0) n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? d.createTextNode(c) : c); });
    return n;
  }

  function api(method, url, body) {
    return fetch(url, {
      method: method,
      headers: { 'X-Editor-Token': E.token, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) { return r.json(); });
  }

  /* --- Hinweise --------------------------------------------------------- */
  var toastEl;
  function toast(msg, opts) {
    opts = opts || {};
    if (toastEl) toastEl.remove();
    toastEl = el('div', { class: 'ed-ui ed-toast' + (opts.err ? ' ed-toast--err' : '') }, [msg, opts.small ? el('small', { text: opts.small }) : null]);
    d.body.appendChild(toastEl);
    var t = toastEl;
    setTimeout(function () { if (t.parentNode) t.remove(); }, opts.ms || 4200);
  }

  /* --- Dialog ------------------------------------------------------------ */
  var open = null; // { close() }
  function closeDialog() { if (open) { open.close(); open = null; } }

  function niceHint(file, path) {
    var parts = path.slice(), out = [];
    if (parts[0] === 'sections' && typeof parts[1] === 'number') { out.push('Abschnitt ' + (parts[1] + 1)); parts = parts.slice(2); }
    return file.replace('/', ' / ') + '  ›  ' + out.concat(parts.map(String)).join(' › ');
  }

  function fieldsDialog(opts) {
    closeDialog();
    var anchor = opts.anchor, modal = !anchor;
    var dim = modal ? el('div', { class: 'ed-ui ed-dim', onclick: closeDialog }) : null;
    var pop = el('div', { class: 'ed-ui ed-pop' + (modal ? ' ed-center' : ''), role: 'dialog', 'aria-label': opts.title });
    var inputs = [];
    var head = [el('h3', { text: opts.title }), el('p', { class: 'ed-hint', text: opts.hint || '' })];
    head.forEach(function (n) { pop.appendChild(n); });
    var status = el('p', { class: 'ed-hint', text: 'Lade …' });
    pop.appendChild(status);
    var actions = el('div', { class: 'ed-actions' });
    var saveBtn = el('button', { class: 'ed-btn ed-btn--primary', type: 'button', text: 'Speichern' });
    var cancelBtn = el('button', { class: 'ed-btn', type: 'button', text: 'Abbrechen', onclick: closeDialog });
    saveBtn.disabled = true;
    actions.appendChild(cancelBtn); actions.appendChild(saveBtn);

    if (dim) d.body.appendChild(dim);
    d.body.appendChild(pop);
    if (anchor) anchor.classList.add('ed-active');
    open = { close: function () { if (dim) dim.remove(); pop.remove(); if (anchor) anchor.classList.remove('ed-active'); } };

    function place() {
      if (!anchor) return;
      var r = anchor.getBoundingClientRect(), h = pop.offsetHeight, w = pop.offsetWidth;
      var below = r.bottom + 12 + h <= window.innerHeight - 12;
      var top = below ? r.bottom + 12 : Math.max(12, r.top - 12 - h);
      var left = Math.min(Math.max(12, r.left + r.width / 2 - w / 2), window.innerWidth - w - 12);
      pop.style.top = top + 'px'; pop.style.left = left + 'px';
    }

    Promise.all(opts.fields.map(function (f) {
      return api('GET', '/__api/get?file=' + encodeURIComponent(f.file) + '&path=' + encodeURIComponent(JSON.stringify(f.path)));
    })).then(function (res) {
      status.remove();
      res.forEach(function (r, i) {
        var f = opts.fields[i];
        if (!r.ok || r.value === null) { pop.appendChild(el('p', { class: 'ed-hint', text: 'Dieses Feld ist nicht bearbeitbar.' })); return; }
        var ta = el('textarea', { rows: Math.min(8, Math.max(2, r.value.split('\n').length + 1)) });
        ta.value = r.value;
        inputs.push({ ta: ta, file: f.file, path: f.path, orig: r.value });
        pop.appendChild(el('div', { class: 'ed-field' }, [el('label', {}, [el('span', { text: f.label || (f.file.split('/')[0].toUpperCase()) })]), ta]));
        (r.others || []).forEach(function (o) {
          var ta2 = el('textarea', { rows: Math.min(8, Math.max(2, o.value.split('\n').length + 1)) });
          ta2.value = o.value;
          inputs.push({ ta: ta2, file: o.file, path: f.path, orig: o.value });
          pop.appendChild(el('details', { class: 'ed-other' }, [
            el('summary', { text: 'Gegenstück ' + o.lang.toUpperCase() + ' ansehen / mitändern' }),
            el('div', { class: 'ed-field' }, [el('label', {}, [el('span', { text: o.lang.toUpperCase() })]), ta2])
          ]));
        });
      });
      if (opts.markup !== false) pop.appendChild(el('p', { class: 'ed-hint', text: '**fett** · [[Rahmen-Hervorhebung]] · neue Zeile = Zeilenumbruch · ⌘↵ speichert' }));
      pop.appendChild(actions);
      saveBtn.disabled = false;
      place();
      if (inputs[0]) { inputs[0].ta.focus(); inputs[0].ta.setSelectionRange(inputs[0].ta.value.length, inputs[0].ta.value.length); }
    });

    function save() {
      var changes = inputs.filter(function (i) { return i.ta.value !== i.orig; })
        .map(function (i) { return { file: i.file, path: i.path, value: i.ta.value }; });
      if (!changes.length) { closeDialog(); return; }
      saveBtn.disabled = true; saveBtn.textContent = 'Speichere …';
      api('POST', '/__api/save', { changes: changes }).then(function (r) {
        if (!r.ok) { toast('Speichern fehlgeschlagen: ' + r.error, { err: true }); saveBtn.disabled = false; saveBtn.textContent = 'Speichern'; return; }
        var issues = (r.errors || []).slice(0, 3).join('\n');
        toast('Gespeichert ✓', issues ? { small: 'Hinweis der Inhaltsprüfung:\n' + issues, ms: 6000 } : {});
        setTimeout(function () { location.reload(); }, issues ? 2400 : 700);
      }).catch(function (e) { toast('Speichern fehlgeschlagen: ' + e, { err: true }); saveBtn.disabled = false; });
    }
    saveBtn.addEventListener('click', save);
    pop.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); save(); }
      if (e.key === 'Escape') { e.preventDefault(); closeDialog(); }
    });
    window.addEventListener('resize', place);
  }

  /* --- Veröffentlichen ---------------------------------------------------- */
  function publishDialog() {
    closeDialog();
    var dim = el('div', { class: 'ed-ui ed-dim', onclick: closeDialog });
    var pop = el('div', { class: 'ed-ui ed-pop ed-center', role: 'dialog', 'aria-label': 'Veröffentlichen' });
    d.body.appendChild(dim); d.body.appendChild(pop);
    open = { close: function () { dim.remove(); pop.remove(); } };
    pop.appendChild(el('h3', { text: 'Änderungen veröffentlichen' }));
    var body = el('div', {}, [el('p', { class: 'ed-hint', text: 'Lade …' })]);
    pop.appendChild(body);
    api('GET', '/__api/status').then(function (s) {
      body.innerHTML = '';
      if (!s.changed.length) {
        body.appendChild(el('p', { class: 'ed-hint', text: 'Es gibt keine ungesicherten Änderungen an den Inhalten.' }));
        body.appendChild(el('div', { class: 'ed-actions' }, [el('button', { class: 'ed-btn', type: 'button', text: 'Schließen', onclick: closeDialog })]));
        return;
      }
      body.appendChild(el('p', { class: 'ed-hint', text: 'Geänderte Dateien (Branch „' + s.branch + '“). Beim Veröffentlichen wird geprüft, committet und gepusht – GitHub baut dann Staging. Produktion bleibt manuell.' }));
      var ul = el('ul', { class: 'ed-list' });
      s.changed.forEach(function (c) { ul.appendChild(el('li', {}, [el('b', { text: c.status || 'M' }), el('span', { text: c.file })])); });
      body.appendChild(ul);
      var msg = el('textarea', { class: 'ed-msg', rows: 2 });
      msg.value = 'Inhalte aktualisiert (Live-Editor)';
      body.appendChild(el('div', { class: 'ed-field' }, [el('label', {}, [el('span', { text: 'Beschreibung der Änderung' })]), msg]));
      var go = el('button', { class: 'ed-btn ed-btn--primary', type: 'button', text: 'Veröffentlichen' });
      var discard = el('button', { class: 'ed-btn ed-btn--danger', type: 'button', text: 'Alle verwerfen', onclick: function () {
        if (!confirm('Alle ungesicherten Textänderungen unwiderruflich verwerfen?')) return;
        api('POST', '/__api/discard', {}).then(function (r) { if (r.ok) { toast('Änderungen verworfen'); setTimeout(function () { location.reload(); }, 500); } else toast(r.error, { err: true }); });
      } });
      body.appendChild(el('div', { class: 'ed-actions' }, [discard, el('button', { class: 'ed-btn', type: 'button', text: 'Abbrechen', onclick: closeDialog }), go]));
      go.addEventListener('click', function () {
        go.disabled = true; go.textContent = 'Veröffentliche …';
        api('POST', '/__api/publish', { message: msg.value }).then(function (r) {
          if (r.ok) { closeDialog(); toast(r.message, { ms: 7000 }); refreshCount(); }
          else { go.disabled = false; go.textContent = 'Veröffentlichen'; toast(r.error + (r.errors ? '\n' + r.errors.slice(0, 3).join('\n') : ''), { err: true, ms: 9000 }); }
        });
      });
    });
  }

  /* --- Werkzeugleiste ----------------------------------------------------- */
  var on = true;
  var sw = el('span', { class: 'ed-switch', 'aria-hidden': 'true' });
  var toggle = el('button', { class: 'ed-btn', type: 'button', 'aria-pressed': 'true', title: 'Bearbeitungsmodus ein/aus (aus = Seite normal bedienen)' }, [sw, 'Bearbeiten']);
  var count = el('span', { class: 'ed-count', text: '0' });
  var pub = el('button', { class: 'ed-btn ed-btn--primary', type: 'button', onclick: publishDialog }, ['Veröffentlichen ', count]);
  var seo = el('button', { class: 'ed-btn', type: 'button', text: 'Seitentitel', title: 'Browser-Titel und Beschreibung dieser Seite', onclick: function () {
    fieldsDialog({ title: 'Seitentitel & Beschreibung', hint: 'Erscheint im Browser-Tab und in Suchergebnissen (' + E.file + ').', markup: false,
      fields: [{ file: E.file, path: ['title'], label: 'Titel (Browser-Tab)' }, { file: E.file, path: ['description'], label: 'Beschreibung (Suchmaschinen)' }] });
  } });
  var bar = el('div', { class: 'ed-ui ed-bar ed-on', role: 'toolbar', 'aria-label': 'Live-Editor' }, [toggle, el('span', { class: 'ed-sep' }), seo]);
  (E.others || []).forEach(function (o) { bar.appendChild(el('a', { class: 'ed-btn', href: o.url, text: o.lang.toUpperCase() + ' ansehen', title: 'Dieselbe Seite in der anderen Sprache bearbeiten' })); });
  bar.appendChild(el('span', { class: 'ed-sep' })); bar.appendChild(pub);
  d.body.appendChild(bar);

  function setOn(v) {
    on = v;
    d.body.classList.toggle('editing', on);
    bar.classList.toggle('ed-on', on);
    toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    if (!on) closeDialog();
    try { sessionStorage.setItem('ed-on', on ? '1' : '0'); } catch (e) {}
  }
  toggle.addEventListener('click', function () { setOn(!on); });
  try { setOn(sessionStorage.getItem('ed-on') !== '0'); } catch (e) { setOn(true); }

  function refreshCount() {
    api('GET', '/__api/status').then(function (s) {
      count.textContent = s.changed ? s.changed.length : 0;
      pub.title = s.changed && s.changed.length ? s.changed.length + ' Datei(en) mit Änderungen' : 'Keine ungesicherten Änderungen';
    });
  }
  refreshCount();

  /* --- Klicks auf Texte ---------------------------------------------------- */
  d.addEventListener('click', function (e) {
    if (!on) return;
    var t = e.target;
    if (t.closest && t.closest('.ed-ui')) return;
    var ed = t.closest && t.closest('.ed');
    if (ed) {
      e.preventDefault(); e.stopPropagation();
      var info; try { info = JSON.parse(ed.getAttribute('data-ed')); } catch (x) { return; }
      fieldsDialog({ title: 'Text bearbeiten', hint: niceHint(info[0], info[1]), anchor: ed, fields: [{ file: info[0], path: info[1] }] });
      return;
    }
    if (t.closest && t.closest('a, button[type="submit"]')) { e.preventDefault(); e.stopPropagation(); }
    else if (open && !(t.closest && t.closest('.ed-pop'))) closeDialog();
  }, true);
  d.addEventListener('submit', function (e) { if (on) e.preventDefault(); }, true);
})();
