/* Früh im <head> geladen: markiert „JS aktiv“ und entscheidet über das Intro (eigene Datei, damit die CSP kein Inline-Skript erlauben muss) */
var h = document.documentElement;
h.className += ' js';
try {
  if (h.hasAttribute('data-intro') && (!sessionStorage.getItem('site-intro') || /[?&]loader=1/.test(location.search)) && !matchMedia('(prefers-reduced-motion: reduce)').matches) h.className += ' intro';
} catch (e) {}
