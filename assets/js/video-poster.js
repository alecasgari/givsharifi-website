/**
 * Fallback: capture first video frame as poster when no poster image is set.
 * Requires crossOrigin on <video> and CORS on the media host (R2).
 */
(function (global) {
  function captureFrame(video) {
    if (video.poster || video.dataset.posterCaptured) return;
    const w = video.videoWidth;
    const h = video.videoHeight;
    if (!w || !h) return;

    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    try {
      ctx.drawImage(video, 0, 0, w, h);
      video.poster = canvas.toDataURL('image/jpeg', 0.82);
      video.dataset.posterCaptured = '1';
    } catch {
      /* cross-origin canvas blocked */
    }
  }

  function bindVideoPosterFallback(root) {
    const scope = root || document;
    const videos = scope.querySelectorAll('video:not([poster]), video[poster=""]');
    videos.forEach((video) => {
      if (video.dataset.posterFallback) return;
      video.dataset.posterFallback = '1';
      if (!video.crossOrigin) video.crossOrigin = 'anonymous';

      const onFrame = () => {
        if (video.readyState >= 2) captureFrame(video);
      };

      video.addEventListener('loadeddata', onFrame, { once: true });

      if (video.preload === 'none' && 'IntersectionObserver' in window) {
        const io = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (!entry.isIntersecting) return;
              video.preload = 'metadata';
              video.load();
              io.unobserve(video);
            });
          },
          { rootMargin: '120px' }
        );
        io.observe(video);
      }
    });
  }

  global.GivVideoPoster = { bindVideoPosterFallback };
})(window);
