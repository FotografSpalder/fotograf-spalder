(() => {
  'use strict';

  const GA_ID = 'G-FHTXJM4638';
  const STORAGE_KEY = 'fotografSpalderConsentV1';
  const ALLOW = 'analytics-allowed';
  const REJECT = 'analytics-rejected';
  let analyticsLoaded = false;

  // Gjør gtag trygt å kalle fra øvrig sidekode også når analyse ikke er tillatt.
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () {
    window.dataLayer.push(arguments);
  };

  function getChoice() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function saveChoice(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (_) {
      // Hvis lagring er blokkert, brukes valget bare for denne sidevisningen.
    }
  }

  function loadAnalytics() {
    if (analyticsLoaded || document.querySelector('script[data-fs-google-analytics]')) {
      window['ga-disable-' + GA_ID] = false;
      return;
    }

    analyticsLoaded = true;
    window['ga-disable-' + GA_ID] = false;

    window.gtag('consent', 'default', {
      analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    script.dataset.fsGoogleAnalytics = 'true';
    document.head.appendChild(script);
  }

  function clearAnalyticsCookies() {
    const cookieNames = document.cookie
      .split(';')
      .map(cookie => cookie.split('=')[0].trim())
      .filter(name => /^(_ga|_gid|_gat)/.test(name));

    const host = window.location.hostname;
    const domains = ['', host, '.' + host, 'fotograf-spalder.com', '.fotograf-spalder.com'];

    cookieNames.forEach(name => {
      domains.forEach(domain => {
        const domainPart = domain ? '; domain=' + domain : '';
        document.cookie = name + '=; Max-Age=0; path=/' + domainPart + '; SameSite=Lax';
      });
    });
  }

  function disableAnalytics() {
    window['ga-disable-' + GA_ID] = true;
    window.gtag('consent', 'update', {
      analytics_storage: 'denied'
    });
    clearAnalyticsCookies();
  }

  function addStyles() {
    if (document.getElementById('fs-consent-styles')) return;

    const style = document.createElement('style');
    style.id = 'fs-consent-styles';
    style.textContent = `
      #fs-consent-overlay {
        position: fixed;
        inset: 0;
        z-index: 2147483645;
        background: rgba(2, 6, 23, .62);
        display: flex;
        align-items: flex-end;
        justify-content: center;
        padding: 1rem;
      }
      #fs-consent-panel {
        width: min(100%, 760px);
        background: #111827;
        color: #f8fafc;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 20px;
        box-shadow: 0 24px 70px rgba(0,0,0,.45);
        padding: 1.25rem;
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.5;
      }
      #fs-consent-panel h2 {
        margin: 0 0 .65rem;
        font-size: 1.35rem;
        color: #fff;
      }
      #fs-consent-panel p {
        margin: .5rem 0;
        color: #cbd5e1;
      }
      #fs-consent-panel a {
        color: #fde68a;
        text-decoration: underline;
        text-underline-offset: 2px;
      }
      .fs-consent-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .75rem;
        margin-top: 1rem;
      }
      .fs-consent-button {
        min-height: 48px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.22);
        padding: .75rem 1rem;
        font: inherit;
        font-weight: 800;
        cursor: pointer;
      }
      .fs-consent-button.allow {
        background: #f59e0b;
        color: #111827;
        border-color: #f59e0b;
      }
      .fs-consent-button.reject {
        background: transparent;
        color: #f8fafc;
      }
      #fs-privacy-settings {
        position: fixed;
        right: .8rem;
        bottom: .8rem;
        z-index: 2147483644;
        border: 1px solid rgba(255,255,255,.22);
        border-radius: 999px;
        background: rgba(17,24,39,.94);
        color: #fde68a;
        padding: .55rem .8rem;
        font: 700 .82rem Arial, Helvetica, sans-serif;
        cursor: pointer;
        box-shadow: 0 10px 28px rgba(0,0,0,.3);
      }
      @media (max-width: 560px) {
        #fs-consent-overlay { padding: .65rem; }
        #fs-consent-panel { border-radius: 16px; padding: 1rem; }
        .fs-consent-actions { grid-template-columns: 1fr; }
        #fs-privacy-settings { right: .55rem; bottom: .55rem; }
      }
    `;
    document.head.appendChild(style);
  }

  function closePanel() {
    const overlay = document.getElementById('fs-consent-overlay');
    if (overlay) overlay.remove();
  }

  function showPanel() {
    addStyles();
    closePanel();

    const overlay = document.createElement('div');
    overlay.id = 'fs-consent-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'fs-consent-title');

    const panel = document.createElement('div');
    panel.id = 'fs-consent-panel';
    panel.innerHTML = `
      <h2 id="fs-consent-title">Personvern og analyse</h2>
      <p>Nettsiden bruker nødvendige teknologier for grunnleggende funksjon og for å huske personvernvalget ditt.</p>
      <p>Med ditt samtykke bruker Fotograf Spalder også Google Analytics for å forstå hvordan nettsiden brukes. Google Analytics lastes ikke inn før du aktivt tillater analyse.</p>
      <p><a href="personvern.html">Les personvernerklæringen</a></p>
      <div class="fs-consent-actions">
        <button type="button" class="fs-consent-button reject" data-consent-reject>Kun nødvendige</button>
        <button type="button" class="fs-consent-button allow" data-consent-allow>Tillat analyse</button>
      </div>
    `;

    overlay.appendChild(panel);
    document.body.appendChild(overlay);

    panel.querySelector('[data-consent-allow]').addEventListener('click', () => {
      saveChoice(ALLOW);
      loadAnalytics();
      closePanel();
    });

    panel.querySelector('[data-consent-reject]').addEventListener('click', () => {
      saveChoice(REJECT);
      disableAnalytics();
      closePanel();
    });

    const firstButton = panel.querySelector('[data-consent-reject]');
    if (firstButton) firstButton.focus();
  }

  function addSettingsButton() {
    if (document.getElementById('fs-privacy-settings')) return;
    addStyles();

    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'fs-privacy-settings';
    button.textContent = 'Personvernvalg';
    button.setAttribute('aria-label', 'Endre valg for personvern og analyse');
    button.addEventListener('click', showPanel);
    document.body.appendChild(button);

    document.querySelectorAll('[data-open-privacy-settings]').forEach(el => {
      el.addEventListener('click', showPanel);
    });
  }

  function init() {
    addSettingsButton();
    const choice = getChoice();

    if (choice === ALLOW) {
      loadAnalytics();
    } else if (choice === REJECT) {
      disableAnalytics();
    } else {
      disableAnalytics();
      showPanel();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
