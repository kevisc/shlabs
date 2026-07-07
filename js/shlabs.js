/* SHLabs — shared site interactions (progressive enhancement). */
(function () {
  'use strict';
  window.__shlabsJS = 1; // signals the inline reveal failsafe that this script ran

  // mobile nav toggle
  var burger = document.querySelector('.nav__burger');
  var links = document.querySelector('.nav__links');
  if (burger && links) {
    burger.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        links.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // products dropdown: hover on desktop (CSS), click/tap toggles + ARIA
  var menu = document.querySelector('.menu');
  var menuBtn = menu && menu.querySelector('[data-menu-toggle]');
  if (menu && menuBtn) {
    var setExpanded = function (v) { menuBtn.setAttribute('aria-expanded', v ? 'true' : 'false'); };
    menuBtn.addEventListener('click', function (e) {
      e.preventDefault();
      setExpanded(menu.classList.toggle('open'));
    });
    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target)) { menu.classList.remove('open'); setExpanded(false); }
    });
  }

  // reveal on scroll
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // current year in footer
  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
