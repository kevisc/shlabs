/* SHLabs — the view explorer.
 *
 * This is the only script on the site. Every page except /cadence/ is static
 * HTML: the nav is CSS-only, nothing reveals on scroll, nothing is measured.
 *
 * Progressive enhancement: without this file the four views render stacked,
 * each a plate with its own note, and the tab row stays hidden (see
 * .explore__tabs in css/shlabs.css). The page adds the `js` class itself
 * before this runs, so the two layouts never flash against each other.
 *
 * The ARIA tab roles are stamped on here rather than written into the HTML,
 * so that with no script there is no tablist and no tabpanel left orphaned
 * in the accessibility tree — just four figures in document order.
 *
 * It is an explorer, not a slideshow: nothing advances on its own.
 */
(function () {
  'use strict';

  var wrap = document.querySelector('[data-explore]');
  if (!wrap) return;

  var bar    = wrap.querySelector('[data-explore-tabs]');
  var tabs   = Array.prototype.slice.call(wrap.querySelectorAll('[data-explore-tab]'));
  var panels = Array.prototype.slice.call(wrap.querySelectorAll('[data-explore-panel]'));
  if (!bar || tabs.length < 2 || tabs.length !== panels.length) return;

  bar.setAttribute('role', 'tablist');
  bar.setAttribute('aria-label', wrap.getAttribute('data-explore') || 'Views');

  tabs.forEach(function (tab, k) {
    var panel = panels[k];
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panel.id);
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', tab.id);
    panel.setAttribute('tabindex', '0');   // the panel holds nothing focusable

    tab.addEventListener('click', function () { select(k); });

    tab.addEventListener('keydown', function (e) {
      var to = -1;
      if (e.key === 'ArrowRight' || e.key === 'Right')     to = (k + 1) % tabs.length;
      else if (e.key === 'ArrowLeft' || e.key === 'Left')  to = (k - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home')                           to = 0;
      else if (e.key === 'End')                            to = tabs.length - 1;
      if (to < 0) return;
      e.preventDefault();
      select(to);
      tabs[to].focus();
    });
  });

  /* roving tabindex: only the selected tab is in the tab order, the arrow
     keys move between them from there */
  function select(k) {
    tabs.forEach(function (tab, j) {
      var on = j === k;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.tabIndex = on ? 0 : -1;
      panels[j].classList.toggle('on', on);
    });
  }

  select(0);

  // Only now does the CSS switch from four stacked plates to the explorer.
  // If this file never loads, the page keeps all four in flow.
  wrap.classList.add('is-ready');
})();
