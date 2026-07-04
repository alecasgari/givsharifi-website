/**
 * Skeleton placeholder HTML for async-loaded sections.
 */
(function () {
  function repeat(n, fn) {
    return Array.from({ length: n }, (_, i) => fn(i)).join("");
  }

  window.GivSkeleton = {
    galleryGrid(count) {
      return repeat(count, () => '<div class="skeleton skeleton-card" aria-hidden="true"></div>');
    },

    homeBlog(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-blog-card" aria-hidden="true">
          <div class="skeleton skeleton--dark skeleton-blog-card__img"></div>
          <div class="skeleton-blog-card__body">
            <div class="skeleton skeleton--dark skeleton-line skeleton-line--short"></div>
            <div class="skeleton skeleton--dark skeleton-line skeleton-line--title"></div>
            <div class="skeleton skeleton--dark skeleton-line"></div>
            <div class="skeleton skeleton--dark skeleton-line"></div>
          </div>
        </div>
      `
      );
    },

    homeVideos(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-vid-card" aria-hidden="true">
          <div class="skeleton skeleton--dark skeleton-vid-card__media"></div>
          <div class="skeleton skeleton--dark skeleton-line skeleton-line--title"></div>
          <div class="skeleton skeleton--dark skeleton-line"></div>
        </div>
      `
      );
    },

    homeGalleryStrip(count) {
      return repeat(count, () => '<div class="skeleton skeleton--dark skeleton-strip-item" aria-hidden="true"></div>');
    },

    videoPage(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-vid-page" aria-hidden="true">
          <div class="skeleton skeleton-vid-page__media"></div>
          <div class="skeleton skeleton-line skeleton-line--short"></div>
          <div class="skeleton skeleton-line skeleton-line--title"></div>
          <div class="skeleton skeleton-line"></div>
        </div>
      `
      );
    },

    publications(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-pub-card" aria-hidden="true">
          <div class="skeleton skeleton-line skeleton-line--short"></div>
          <div class="skeleton skeleton-line skeleton-line--title"></div>
          <div class="skeleton skeleton-line"></div>
        </div>
      `
      );
    },

    blogList(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-blog-index" aria-hidden="true">
          <div class="skeleton skeleton-blog-index__thumb"></div>
          <div>
            <div class="skeleton skeleton-line skeleton-line--short"></div>
            <div class="skeleton skeleton-line skeleton-line--title"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line"></div>
          </div>
        </div>
      `
      );
    },

    congress(count) {
      return repeat(
        count,
        () => `
        <div class="skeleton-cong-card" aria-hidden="true">
          <div class="skeleton skeleton-cong-card__media"></div>
          <div class="skeleton-cong-card__body">
            <div class="skeleton skeleton-line skeleton-line--short"></div>
            <div class="skeleton skeleton-line skeleton-line--title"></div>
            <div class="skeleton skeleton-line"></div>
          </div>
        </div>
      `
      );
    },
  };
})();
