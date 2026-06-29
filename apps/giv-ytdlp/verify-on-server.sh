#!/bin/bash
# Run on VPS: bash verify-on-server.sh [youtube-or-instagram-url]
# Default URL: short YouTube test video
set -euo pipefail

URL="${1:-https://youtu.be/cuomkatlVtg}"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=== 1) Container ==="
docker compose ps

echo ""
echo "=== 2) cookies.txt ==="
if docker exec giv-ytdlp test -f /data/cookies.txt; then
  docker exec giv-ytdlp ls -la /data/cookies.txt
else
  echo "MISSING: /data/cookies.txt"
  echo "Fix: docker cp $DIR/cookies.txt giv-ytdlp:/data/cookies.txt && docker compose restart"
  exit 1
fi

echo ""
echo "=== 3) Deno + yt-dlp ==="
docker exec giv-ytdlp deno --version
docker exec giv-ytdlp yt-dlp --version

echo ""
echo "=== 4) HTTP health ==="
docker exec giv-ytdlp python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:9876/health').read().decode())"

echo ""
echo "=== 5) yt-dlp CLI (no upload) ==="
echo "URL: $URL"
docker exec giv-ytdlp sh -c "yt-dlp --remote-components ejs:github --cookies /data/cookies.txt -f 'bv*+ba/b' --merge-output-format mp4 -o '/tmp/cli-test-%(id)s.%(ext)s' --no-playlist --write-info-json '$URL'"
docker exec giv-ytdlp sh -c "ls -lh /tmp/cli-test-* 2>/dev/null || true"

echo ""
echo "=== 6) HTTP POST /download (upload_r2=false, no R2) ==="
docker exec giv-ytdlp python -c "
import json, urllib.request
url = '''$URL'''
req = urllib.request.Request(
    'http://127.0.0.1:9876/download',
    data=json.dumps({'url': url, 'work_id': 'verify-script', 'upload_r2': False}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
resp = urllib.request.urlopen(req, timeout=600)
body = resp.read().decode()
print(body[:800])
data = json.loads(body)
assert data.get('ok'), data
assert data.get('video_id'), data
print('OK: video_id =', data['video_id'])
"

echo ""
echo "=== 7) HTTP POST /download (upload_r2=true → R2) ==="
read -r -p "Upload to R2 now? [y/N] " ans
if [[ "${ans,,}" == "y" ]]; then
  docker exec giv-ytdlp python -c "
import json, urllib.request
url = '''$URL'''
req = urllib.request.Request(
    'http://127.0.0.1:9876/download',
    data=json.dumps({'url': url, 'work_id': 'verify-r2', 'upload_r2': True}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
resp = urllib.request.urlopen(req, timeout=600)
body = resp.read().decode()
print(body)
"
else
  echo "Skipped R2 upload."
fi

echo ""
echo "=== DONE ==="
