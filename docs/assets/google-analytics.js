(() => {
  const canonical = document.querySelector('link[rel="canonical"]');
  if (new URL(canonical.href).origin !== location.origin) return;

  const { measurementId, contentGroup } = document.currentScript.dataset;
  const panel = document.getElementById('analytics-consent');
  const settings = document.querySelector('.analytics-settings');
  const preference = 'baml_analytics';
  const disableFlag = 'ga-disable-' + measurementId;
  let loaded = false;

  function readChoice() {
    const match = document.cookie.match(/(?:^|; )baml_analytics=(granted|denied)(?:;|$)/);
    return match ? match[1] : '';
  }

  function gtag() {
    window.dataLayer.push(arguments);
  }

  function applyChoice(choice) {
    const allowed = choice === 'granted';
    window[disableFlag] = !allowed;
    panel.hidden = Boolean(choice);
    if (!allowed) {
      if (loaded) gtag('consent', 'update', { analytics_storage: 'denied' });
      for (const name of ['_ga', '_ga_' + measurementId.slice(2)]) {
        const expired = name + '=; Max-Age=0; Path=/; SameSite=Lax; Secure';
        document.cookie = expired;
        document.cookie = expired + '; Domain=' + location.hostname;
      }
      return;
    }
    if (loaded) {
      gtag('consent', 'update', { analytics_storage: 'granted' });
      return;
    }
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = gtag;
    gtag('consent', 'default', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    gtag('js', new Date());
    gtag('config', measurementId, {
      content_group: contentGroup,
      cookie_domain: 'none',
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.append(tag);
  }

  settings.hidden = false;
  settings.addEventListener('click', () => {
    panel.hidden = false;
    panel.querySelector('button').focus();
  });
  panel.addEventListener('click', event => {
    const button = event.target.closest('button[data-choice]');
    if (!button) return;
    const choice = button.dataset.choice;
    document.cookie = preference + '=' + choice + '; Max-Age=15552000; Path=/; SameSite=Lax; Secure';
    applyChoice(choice);
    settings.focus({ preventScroll: true });
  });

  function trackResource(event) {
    if (!loaded || window[disableFlag]) return;
    if (event.type === 'auxclick' && event.button !== 1) return;
    const link = event.target.closest('a[data-resource-chapter]');
    if (!link) return;
    gtag('event', 'resource_click', {
      content_group: 'Chapter ' + link.dataset.resourceChapter,
      link_url: link.href,
      link_domain: link.hostname
    });
  }
  document.addEventListener('click', trackResource);
  document.addEventListener('auxclick', trackResource);
  applyChoice(readChoice());
  // Recheck after another tab changes the preference or a page returns from the back/forward cache.
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) applyChoice(readChoice());
  });
})();
