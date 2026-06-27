# Video Files for Homepage

The homepage surgery video section uses files from `/video/`:

- `Cranial-Nerves-Problem.mp4`
- `Brain-Tumor-Surgery-with-panic-attack.mp4`
- `Tumor-Affecting-Hearing-and-Balance.mp4`
- `brain-cyst.mp4`

## Before deploy

Copy the `video` folder from the old WordPress backup:

```
OLD-WP-Website/Wordpress-website/video/  →  givsharifi-website/video/
```

Total size is ~280 MB. These files are not included in git by default due to size.

## GitHub Pages

Upload the `video/` folder to your repo or host videos on a CDN and update `index.html` video `src` paths.
