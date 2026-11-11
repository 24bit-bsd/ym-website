/* Leichtes Vanilla-JS, keine Abhängigkeiten, keine Cookies, keine externen Aufrufe */
(function () {
  'use strict';
  var d = document;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Mobile-Menü ------------------------------------------------------------ */
  var btn = d.querySelector('.menu-btn');
  var menu = d.getElementById('mobile-menu');
  function setMenu(open) {
    if (!btn) return;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', btn.getAttribute(open ? 'data-label-close' : 'data-label-open'));
    d.body.classList.toggle('menu-open', open);
    d.body.classList.toggle('no-scroll', open);
    if (menu) menu.setAttribute('aria-hidden', open ? 'false' : 'true');
  }
  if (btn && menu) {
    setMenu(false);
    btn.addEventListener('click', function () { setMenu(btn.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
    var mq = window.matchMedia('(min-width: 1100px)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(function (m) { if (m.matches) setMenu(false); });
  }

  /* Intro: Logo + Ring, nur beim ersten Aufruf je Sitzung (?loader=1 erzwingt es) ---- */
  var root = d.documentElement;
  var intro = d.getElementById('intro');
  if (intro && root.classList.contains('intro')) {
    var started = Date.now();
    var finished = false;
    var finish = function () {
      if (finished) return;
      finished = true;
      var wait = Math.max(0, 1500 - (Date.now() - started));
      setTimeout(function () {
        intro.classList.add('done');
        root.classList.add('intro-done');
        try { sessionStorage.setItem('site-intro', '1'); } catch (e) {}
      }, wait);
    };
    if (d.readyState === 'complete') finish(); else window.addEventListener('load', finish);
    setTimeout(finish, 4000); /* Notausgang */
  }

  /* Nach-oben-Button: erscheint nach etwa einer Bildschirmhöhe (mindestens 400 px) */
  var toTop = d.querySelector('[data-to-top]');
  if (toTop) {
    var updateTop = function () {
      var threshold = Math.max(400, window.innerHeight);
      toTop.classList.toggle('is-visible', (window.pageYOffset || d.documentElement.scrollTop) > threshold);
    };
    window.addEventListener('scroll', updateTop, { passive: true });
    window.addEventListener('resize', updateTop);
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
      var first = d.querySelector('.skip') || d.querySelector('.site-header a');
      if (first && first.focus) first.focus({ preventScroll: true });
    });
    updateTop();
  }

  /* Slider (Referenz-Cases): Pfeile blättern um eine Karte; ohne JS bleibt der Bereich per Wischen/Scrollen bedienbar */
  [].forEach.call(d.querySelectorAll('[data-slider]'), function (s) {
    var track = s.querySelector('.slider-track');
    var prev = s.querySelector('[data-slider-prev]');
    var next = s.querySelector('[data-slider-next]');
    if (!track || !prev || !next) return;
    s.classList.add('is-js');
    function stepWidth() {
      var sl = track.querySelector('.slide');
      var gap = parseFloat(window.getComputedStyle(track).columnGap) || 0;
      return sl ? sl.getBoundingClientRect().width + gap : track.clientWidth;
    }
    function update() {
      var max = track.scrollWidth - track.clientWidth - 2;
      s.classList.toggle('is-static', max <= 0);
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max;
    }
    prev.addEventListener('click', function () { track.scrollBy({ left: -stepWidth(), behavior: reduce ? 'auto' : 'smooth' }); });
    next.addEventListener('click', function () { track.scrollBy({ left: stepWidth(), behavior: reduce ? 'auto' : 'smooth' }); });
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* Team-Profile: <dialog> mit sanftem Ein-/Ausblenden */
  [].forEach.call(d.querySelectorAll('[data-team-open]'), function (b) {
    var dlg = d.getElementById(b.getAttribute('data-team-open'));
    if (!dlg || !dlg.showModal) return;
    function close() {
      if (reduce) { dlg.close(); return; }
      dlg.classList.add('closing');
      setTimeout(function () { dlg.classList.remove('closing'); dlg.close(); }, 200);
    }
    b.addEventListener('click', function () { dlg.showModal(); d.body.classList.add('no-scroll'); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.closest('[data-team-close]')) close(); });
    dlg.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    dlg.addEventListener('close', function () { d.body.classList.remove('no-scroll'); b.focus(); });
  });

  /* Formular im Fenster: <a data-embed="https://…"> öffnet einen Dialog mit iframe (erst beim Klick geladen, DSGVO) */
  [].forEach.call(d.querySelectorAll('[data-embed]'), function (a) {
    if (!d.createElement('dialog').showModal) return;
    var dlg = null;
    function build() {
      dlg = d.createElement('dialog');
      dlg.className = 'embed-dialog';
      dlg.setAttribute('aria-label', a.getAttribute('data-embed-title') || '');
      var bar = d.createElement('div'); bar.className = 'embed-bar';
      var open = d.createElement('a'); open.href = a.getAttribute('data-embed'); open.target = '_blank'; open.rel = 'noopener noreferrer'; open.className = 'embed-new'; open.textContent = a.getAttribute('data-embed-new') || '';
      var x = d.createElement('button'); x.type = 'button'; x.className = 'embed-close'; x.setAttribute('aria-label', a.getAttribute('data-embed-close') || 'Close'); x.innerHTML = '<span aria-hidden="true">&times;</span>';
      bar.appendChild(open); bar.appendChild(x);
      var f = d.createElement('iframe'); f.className = 'embed-frame'; f.title = a.getAttribute('data-embed-title') || ''; f.src = a.getAttribute('data-embed'); f.setAttribute('allow', 'payment');
      dlg.appendChild(bar); dlg.appendChild(f);
      function close() {
        if (reduce) { dlg.close(); return; }
        dlg.classList.add('closing');
        setTimeout(function () { dlg.classList.remove('closing'); dlg.close(); }, 200);
      }
      x.addEventListener('click', close);
      dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
      dlg.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
      dlg.addEventListener('close', function () { d.body.classList.remove('no-scroll'); a.focus(); });
      d.body.appendChild(dlg);
    }
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      if (!dlg) build();
      dlg.showModal(); d.body.classList.add('no-scroll');
    });
  });

  /* Mobile Untermenü (Akkordeon) */
  [].forEach.call(d.querySelectorAll('.m-chev'), function (b) {
    b.addEventListener('click', function () {
      var sub = d.getElementById(b.getAttribute('aria-controls'));
      var open = b.getAttribute('aria-expanded') !== 'true';
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (sub) sub.classList.toggle('open', open);
    });
  });

  /* Sticky Header: transparent oben, Glas + Schatten nach dem Scrollen ------- */
  var header = d.querySelector('[data-header]');
  if (header) {
    var ticking = false;
    var onScroll = function () {
      ticking = false;
      var on = (window.pageYOffset || d.documentElement.scrollTop) > 8;
      header.classList.toggle('is-scrolled', on);
      d.body.classList.toggle('scrolled', on);
    };
    onScroll();
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
    }, { passive: true });
  }

  /* Mega-Menü: Hover (Maus), Klick auf den Pfeil (Touch/Tastatur), Esc, Klick daneben */
  var megas = [].slice.call(d.querySelectorAll('.has-mega'));
  function setMega(li, open) {
    var chev = li.querySelector('.nav-chev');
    var panel = li.querySelector('.mega-wrap');
    li.classList.toggle('open', open);
    if (chev) chev.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (panel) panel.hidden = !open;
  }
  function closeMegas(except) { megas.forEach(function (li) { if (li !== except) setMega(li, false); }); }
  megas.forEach(function (li) {
    var timer;
    var chev = li.querySelector('.nav-chev');
    li.addEventListener('mouseenter', function () { clearTimeout(timer); closeMegas(li); setMega(li, true); });
    li.addEventListener('mouseleave', function () { timer = setTimeout(function () { setMega(li, false); }, 160); });
    if (chev) chev.addEventListener('click', function () { var o = !li.classList.contains('open'); closeMegas(li); setMega(li, o); });
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) setMega(li, false); });
    li.querySelector('.mega-wrap').addEventListener('click', function (e) { if (e.target.closest('a')) setMega(li, false); });
  });
  d.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    megas.forEach(function (li) { if (li.classList.contains('open')) { setMega(li, false); var c = li.querySelector('.nav-chev'); if (c) c.focus(); } });
  });
  d.addEventListener('click', function (e) { if (!e.target.closest('.has-mega')) closeMegas(); });

  /* Sprach-Dropdown */
  var lm = d.querySelector('.lang-menu');
  if (lm) {
    var lb = lm.querySelector('.lang-btn'), ll = lm.querySelector('.lang-list');
    var setLang = function (open) { lb.setAttribute('aria-expanded', open ? 'true' : 'false'); ll.hidden = !open; };
    lb.addEventListener('click', function () { setLang(lb.getAttribute('aria-expanded') !== 'true'); });
    d.addEventListener('click', function (e) { if (!lm.contains(e.target)) setLang(false); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setLang(false); } });
    window.addEventListener('scroll', function () { if (!ll.hidden) setLang(false); }, { passive: true });
    lm.addEventListener('focusout', function (e) { if (!lm.contains(e.relatedTarget)) setLang(false); });
  }

  /* Drei Ebenen: Ring und Eintrag gemeinsam hervorheben ---------------------- */
  var ringItems = [].slice.call(d.querySelectorAll('.ring-item'));
  if (ringItems.length) {
    var ringEls = [].slice.call(d.querySelectorAll('.ring'));
    var setRing = function (i) {
      ringItems.forEach(function (el) { el.classList.toggle('is-active', el.getAttribute('data-ring') === i); });
      ringEls.forEach(function (el) { el.classList.toggle('is-active', el.getAttribute('data-ring') === i); });
    };
    ringItems.forEach(function (el) {
      var i = el.getAttribute('data-ring');
      ['mouseenter', 'focus', 'click'].forEach(function (ev) { el.addEventListener(ev, function () { setRing(i); }); });
    });
    ringEls.forEach(function (el) {
      el.addEventListener('mouseenter', function () { setRing(el.getAttribute('data-ring')); });
    });
    setRing('0');
  }

  /* Einblend-Animationen --------------------------------------------------- */
  var items = [].slice.call(d.querySelectorAll('[data-reveal]'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  /* Wechselnde Wörter im Hero ---------------------------------------------- */
  var rot = d.querySelector('.rot');
  if (rot && !reduce) {
    var words = [].slice.call(rot.querySelectorAll('.rot-w'));
    var idx = 0;
    setInterval(function () {
      if (d.hidden) return;
      words[idx].classList.remove('on');
      idx = (idx + 1) % words.length;
      words[idx].classList.add('on');
    }, 2800);
  }

  /* Subnav: aktiven Abschnitt hervorheben ---------------------------------- */
  var sublinks = [].slice.call(d.querySelectorAll('.subnav ul a'));
  if (sublinks.length && 'IntersectionObserver' in window) {
    var map = {};
    sublinks.forEach(function (a) {
      var id = (a.getAttribute('href') || '').replace('#', '');
      var sec = id && d.getElementById(id);
      if (sec) map[id] = a;
    });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        sublinks.forEach(function (a) { a.removeAttribute('aria-current'); });
        var a = map[en.target.id];
        if (a) {
          a.setAttribute('aria-current', 'true');
          var ul = a.closest('ul');
          if (ul && ul.scrollWidth > ul.clientWidth) { ul.scrollTo({ left: a.offsetLeft - 24, behavior: reduce ? 'auto' : 'smooth' }); }
        }
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    Object.keys(map).forEach(function (id) { spy.observe(d.getElementById(id)); });
  }

  /* E-Mail: Anzeige „name[at]domain“; die echte mailto:-Adresse wird erst bei Interaktion gesetzt (Spam-Schutz) */
  [].forEach.call(d.querySelectorAll('a[data-mu]'), function (a) {
    var arm = function () { a.setAttribute('href', 'mailto:' + a.getAttribute('data-mu') + '@' + a.getAttribute('data-md')); };
    ['pointerenter', 'focus', 'touchstart'].forEach(function (ev) { a.addEventListener(ev, arm, { passive: true }); });
    a.addEventListener('click', function (e) { e.preventDefault(); arm(); window.location.href = a.getAttribute('href'); });
  });

  /* Copyright-Jahr automatisch */
  [].forEach.call(d.querySelectorAll('[data-year]'), function (el) { el.textContent = new Date().getFullYear(); });

  /* Kontaktformular -------------------------------------------------------- */
  var form = d.getElementById('formular');
  if (form) {
    var status = form.querySelector('.form-status');
    var submit = form.querySelector('button[type="submit"]');
    var ts = form.querySelector('input[name="ts"]');
    var sig = form.querySelector('input[name="sig"]');
    /* Zeitstempel kommt signiert vom Server (api/token.php) – so lässt er sich nicht fälschen */
    function loadToken() {
      if (!ts || !sig || !window.fetch || form.hasAttribute('data-preview')) return;
      fetch(form.action.replace(/contact\.php.*$/, 'token.php'), { headers: { Accept: 'application/json' }, cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (j) { if (j && j.ts && j.sig) { ts.value = j.ts; sig.value = j.sig; } })
        .catch(function () {});
    }
    loadToken();

    var topic = form.querySelector('select[name="topic"]');
    var param = new URLSearchParams(window.location.search).get('thema');
    if (topic && param) {
      for (var i = 0; i < topic.options.length; i++) {
        if (topic.options[i].value === param) { topic.selectedIndex = i; break; }
      }
    }

    function say(msg, cls) { status.textContent = msg; status.className = 'form-status ' + (cls || ''); }

    form.addEventListener('submit', function (e) {
      form.classList.add('was-validated');
      if (!form.checkValidity()) {
        e.preventDefault();
        say(form.getAttribute('data-invalid'), 'err');
        var bad = form.querySelector(':invalid');
        if (bad) bad.focus();
        return;
      }
      if (form.hasAttribute('data-preview')) {
        e.preventDefault();
        say(form.getAttribute('data-preview-msg'), '');
        return;
      }
      if (!window.fetch || !window.FormData) return; // ohne JS/Fetch: normaler POST
      e.preventDefault();
      submit.disabled = true;
      say(form.getAttribute('data-sending'), '');
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (j) {
          if (j && j.ok) { form.reset(); form.classList.remove('was-validated'); say(form.getAttribute('data-ok'), 'ok'); }
          else { say(form.getAttribute('data-err'), 'err'); }
          loadToken();
        })
        .catch(function () { say(form.getAttribute('data-err'), 'err'); })
        .then(function () { submit.disabled = false; });
    });
  }
})();
