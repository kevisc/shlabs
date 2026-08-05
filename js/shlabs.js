/* SHLabs — the screenshot cycler.
 *
 * This is the only script on the site. Every page except /cadence/ is static
 * HTML: the nav is CSS-only, nothing reveals on scroll, nothing is measured.
 *
 * Progressive enhancement: without this file the figures render stacked, each
 * with its own caption, and the control bar stays hidden (see .shotbar in
 * css/shlabs.css). The page adds the `js` class itself before this runs, so
 * the two layouts never flash against each other.
 */
(function () {
  'use strict';

  var wrap = document.querySelector('[data-shotcycle]');
  if (!wrap) return;

  var deck = wrap.querySelector('.shot__slides');
  if (!deck) return;

  var slides = Array.prototype.slice.call(deck.children);
  if (slides.length < 2) return;

  // Only now does the CSS switch from "first plate visible" to "cycler".
  // If this file never loads, the page keeps the static first plate.
  deck.classList.add('is-ready');

  var cap  = wrap.querySelector('[data-shot-cap]');
  var dots = wrap.querySelector('[data-shot-dots]');
  var prev = wrap.querySelector('[data-shot-prev]');
  var next = wrap.querySelector('[data-shot-next]');

  var i = 0;
  var timer = null;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function capOf(el) {
    var fc = el.querySelector('figcaption');
    return fc ? fc.textContent.trim() : '';
  }

  slides.forEach(function (slide, k) {
    var d = document.createElement('button');
    d.type = 'button';
    d.setAttribute('aria-label', 'Screenshot ' + (k + 1) + ' of ' + slides.length);
    d.addEventListener('click', function () { go(k); hold(); });
    dots.appendChild(d);
  });

  function paint() {
    slides.forEach(function (s, k) { s.classList.toggle('on', k === i); });
    Array.prototype.forEach.call(dots.children, function (d, k) {
      if (k === i) d.setAttribute('aria-current', 'true');
      else d.removeAttribute('aria-current');
    });
    if (cap) cap.textContent = capOf(slides[i]);
  }

  function go(k) { i = (k + slides.length) % slides.length; paint(); }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  function start(ms) { if (still || timer) return; timer = setInterval(function () { go(i + 1); }, ms || 6000); }
  function hold() { stop(); start(12000); }

  if (prev) prev.addEventListener('click', function () { go(i - 1); hold(); });
  if (next) next.addEventListener('click', function () { go(i + 1); hold(); });
  wrap.addEventListener('mouseenter', stop);
  wrap.addEventListener('mouseleave', function () { start(); });
  wrap.addEventListener('focusin', stop);

  paint();
  start();
})();
