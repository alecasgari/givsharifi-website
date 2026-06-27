# Video Files for Homepage

See **[r2-videos-setup.md](./r2-videos-setup.md)** for the full Cloudflare R2 guide (Persian).

## Config

Video list and R2 base URL: `assets/data/home-videos.json`  
Renderer: `assets/js/home-videos.js`

## Files (upload to R2 folder `homepage/`)

- `Cranial-Nerves-Problem.mp4`
- `Brain-Tumor-Surgery-with-panic-attack.mp4`
- `Tumor-Affecting-Hearing-and-Balance.mp4`
- `brain-cyst.mp4`

## Local test (before R2)

Copy from WordPress backup:

```
OLD-WP-Website/Wordpress-website/video/  →  givsharifi-website/video/
```

Keep `baseUrl` empty and `pathPrefix` as `video` in `home-videos.json`.
