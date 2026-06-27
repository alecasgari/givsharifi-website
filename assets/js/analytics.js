(function () {
  const GTM_ID = 'GTM-PSFDMJX9';

  function initGtm() {
    if (!document.body || !document.head) return;

    const noscript = document.createElement('noscript');
    noscript.innerHTML =
      '<iframe src="https://www.googletagmanager.com/ns.html?id=' +
      GTM_ID +
      '" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe>';
    document.body.insertBefore(noscript, document.body.firstChild);

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM_ID;
    document.head.appendChild(script);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGtm);
  } else {
    initGtm();
  }
})();
