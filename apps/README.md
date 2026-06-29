# Apps

Self-hosted services that support the givsharifi-website automation stack (n8n, GitHub Actions, etc.). Each app lives in its own folder with its own `docker-compose.yml` so it can run on the VPS **without** modifying the n8n container or compose.

| App | Purpose |
|-----|---------|
| [giv-ytdlp](giv-ytdlp/) | Download Instagram / YouTube videos via yt-dlp; optional upload to Cloudflare R2 |

Deploy apps on the server under e.g. `/home/alecadmin/giv-ytdlp/` (copy or clone the app folder). See each app's `README.md` for steps.
