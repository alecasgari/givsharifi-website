/**
 * Ensure only one <video> plays at a time within a container (or document).
 */
(function (global) {
  function bindSingleVideoPlayback(root) {
    const scope = root || document;
    const videos = scope.querySelectorAll('video');
    videos.forEach((video) => {
      if (video.dataset.singlePlayBound) return;
      video.dataset.singlePlayBound = '1';
      video.addEventListener('play', () => {
        videos.forEach((other) => {
          if (other !== video && !other.paused) other.pause();
        });
      });
    });
  }

  global.GivVideoPlayback = { bindSingleVideoPlayback };
})(window);
