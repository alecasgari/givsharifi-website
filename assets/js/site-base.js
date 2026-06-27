(function () {
  var root = '/';
  if (/\.github\.io$/i.test(location.hostname)) {
    var seg = location.pathname.split('/').filter(Boolean)[0];
    if (seg) root = '/' + seg + '/';
  }
  window.__SITE_ROOT__ = root;

  window.siteUrl = function (path) {
    if (path == null || path === '') return root;
    if (/^https?:\/\//i.test(path) || path.startsWith('tel:') || path.startsWith('mailto:')) return path;
    return root + String(path).replace(/^\//, '');
  };

  var base = document.createElement('base');
  base.id = 'site-base';
  base.href = root;
  document.head.appendChild(base);
})();
