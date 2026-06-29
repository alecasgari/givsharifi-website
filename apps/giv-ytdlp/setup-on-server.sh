#!/bin/bash
# Run on the VPS inside /home/alecadmin/giv-ytdlp (after copying app files).
# Creates .env with a random GIV_YTDLP_TOKEN — nothing sensitive is printed.
set -euo pipefail

cd "$(dirname "$0")"

if [[ -f .env ]]; then
  echo "ERROR: .env already exists. Remove or rename it first." >&2
  exit 1
fi

: "${R2_ACCOUNT_ID:?Set R2_ACCOUNT_ID}"
: "${R2_ACCESS_KEY_ID:?Set R2_ACCESS_KEY_ID}"
: "${R2_SECRET_ACCESS_KEY:?Set R2_SECRET_ACCESS_KEY}"

TOKEN=$(openssl rand -hex 32)

cat > .env <<EOF
GIV_YTDLP_HOST=0.0.0.0
GIV_YTDLP_PORT=9876
GIV_YTDLP_TOKEN=${TOKEN}
GIV_YTDLP_DATA_DIR=/data

R2_ACCOUNT_ID=${R2_ACCOUNT_ID}
R2_ACCESS_KEY_ID=${R2_ACCESS_KEY_ID}
R2_SECRET_ACCESS_KEY=${R2_SECRET_ACCESS_KEY}
R2_BUCKET=givsharifi-videos
R2_PREFIX=library
R2_PUBLIC_BASE_URL=https://media.givsharifi.com
EOF

chmod 600 .env
echo "OK: .env created (chmod 600). GIV_YTDLP_TOKEN is inside .env — use it in n8n later."
echo "Next: docker compose build && docker compose up -d"
