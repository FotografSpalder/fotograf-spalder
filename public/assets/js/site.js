(() => {
  'use strict';

  const yearElement = document.getElementById('year');
  if (yearElement) yearElement.textContent = new Date().getFullYear();

  const mobileToggle = document.getElementById('mobileToggle');
  const mobileNav = document.getElementById('navLinks');

  if (mobileToggle && mobileNav) {
    const setMenuState = open => {
      mobileNav.classList.toggle('open', open);
      mobileToggle.setAttribute('aria-expanded', String(open));
      mobileToggle.setAttribute('aria-label', open ? 'Lukk meny' : 'Åpne meny');
      mobileToggle.textContent = open ? 'Lukk' : 'Meny';
    };

    setMenuState(false);
    mobileToggle.addEventListener('click', () => {
      setMenuState(!mobileNav.classList.contains('open'));
    });
    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => setMenuState(false));
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && mobileNav.classList.contains('open')) {
        setMenuState(false);
        mobileToggle.focus();
      }
    });
  }

  const tabList = document.querySelector('[role="tablist"]');
  if (tabList) {
    const tabs = Array.from(tabList.querySelectorAll('[role="tab"]'));
    const activateTab = (tab, moveFocus = false) => {
      tabs.forEach(button => {
        const selected = button === tab;
        button.classList.toggle('active', selected);
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
        const panel = document.getElementById(button.getAttribute('aria-controls'));
        if (panel) {
          panel.classList.toggle('active', selected);
          panel.hidden = !selected;
        }
      });
      if (moveFocus) tab.focus();
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activateTab(tab));
      tab.addEventListener('keydown', event => {
        let next = null;
        if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
        if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
        if (event.key === 'Home') next = tabs[0];
        if (event.key === 'End') next = tabs[tabs.length - 1];
        if (next) {
          event.preventDefault();
          activateTab(next, true);
        }
      });
    });
  }
})();
