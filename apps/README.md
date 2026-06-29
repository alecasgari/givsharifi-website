# Apps (external repositories)

Self-hosted services for the givsharifi automation stack live in **separate GitHub repos** and deploy independently on the VPS. They are not tracked in this website repository.

| Service | Repository | VPS path (example) |
|---------|------------|-------------------|
| YouTube / Instagram downloader (yt-dlp + R2 + UI) | [youtube-instagram-downloader](https://github.com/alecasgari/youtube-instagram-downloader) | `/home/alecadmin/youtube-instagram-downloader` |

n8n workflow `02-publish-video` calls the Docker service at `http://giv-ytdlp:9876/download` on network `giv-ytdlp-net`. See the downloader repo README for setup.
