# giv-ytdlp

سرویس داخلی برای دانلود ویدیو از **اینستاگرام** و **یوتیوب** با [yt-dlp](https://github.com/yt-dlp/yt-dlp)، و آپلود خودکار به **Cloudflare R2**.

n8n (داخل Docker) با یک درخواست HTTP به این سرویس وصل می‌شود — **بدون** دست زدن به کانتینر یا compose خود n8n.

## API

| Method | Path | توضیح |
|--------|------|--------|
| `GET` | `/health` | وضعیت سرویس |
| `POST` | `/download` | دانلود (+ آپلود R2 در حالت پیش‌فرض) |

### POST `/download`

```json
{
  "url": "https://www.instagram.com/reel/XXXX/",
  "work_id": "optional-unique-id",
  "token": "only-if-GIV_YTDLP_TOKEN-set",
  "upload_r2": true
}
```

پاسخ موفق (با R2):

```json
{
  "ok": true,
  "video_id": "DZ455nVtZ30",
  "source": "instagram",
  "video_meta": { "...": "yt-dlp metadata" },
  "r2": {
    "mp4_key": "library/DZ455nVtZ30.mp4",
    "poster_key": "library/DZ455nVtZ30.jpg",
    "mp4_url": "https://media.givsharifi.com/library/DZ455nVtZ30.mp4",
    "poster_url": "https://media.givsharifi.com/library/DZ455nVtZ30.jpg"
  },
  "work_dir": null
}
```

فقط یک دانلود هم‌زمان — درخواست دوم تا تمام شدن اولی `503` می‌گیرد.

---

## راه‌اندازی روی سرور (قدم‌به‌قدم)

این مراحل را **یکی‌یکی** روی VPS (`vmi2779817`) انجام بده. هر قدم را تمام کن، بعد برو بعدی.

### قدم ۱ — فولدر روی سرور

SSH به سرور. فولدر جدا از n8n بساز:

```bash
mkdir -p /home/alecadmin/giv-ytdlp
cd /home/alecadmin/giv-ytdlp
```

### قدم ۲ — کپی فایل‌های اپ از پروژه

روی **کامپیوتر خودت** (جایی که ریپو را داری)، محتویات `apps/giv-ytdlp/` را به سرور بفرست:

```bash
scp -r apps/giv-ytdlp/* alecadmin@YOUR_SERVER_IP:/home/alecadmin/giv-ytdlp/
```

یا اگر ریپو روی سرور clone شده:

```bash
cd /path/to/givsharifi-website
cp -r apps/giv-ytdlp/* /home/alecadmin/giv-ytdlp/
```

روی سرور چک کن این فایل‌ها باشند:

```bash
ls /home/alecadmin/giv-ytdlp
# Dockerfile  docker-compose.yml  main.py  server.py  config.py  download.py  r2_upload.py  requirements.txt  .env.example
```

### قدم ۳ — کلید R2

1. Cloudflare → **R2** → bucket `givsharifi-videos`
2. **Manage R2 API Tokens** → Create token با دسترسی Read & Write روی همین bucket
3. یادداشت کن: **Account ID**, **Access Key ID**, **Secret Access Key**

(همان کلیدی که در n8n برای S3/R2 استفاده می‌کنی — می‌توانی همان را بگذاری.)

### قدم ۴ — فایل `.env`

```bash
cd /home/alecadmin/giv-ytdlp
cp .env.example .env
nano .env
```

مقادیر را پر کن (مثال):

```env
GIV_YTDLP_HOST=0.0.0.0
GIV_YTDLP_PORT=9876
GIV_YTDLP_TOKEN=یک-رمز-طولانی-تصادفی
GIV_YTDLP_DATA_DIR=/data

R2_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_BUCKET=givsharifi-videos
R2_PREFIX=library
R2_PUBLIC_BASE_URL=https://media.givsharifi.com
```

ذخیره و خروج (`Ctrl+O`, `Enter`, `Ctrl+X`).

### قدم ۵ — بیلد و اجرا

```bash
cd /home/alecadmin/giv-ytdlp
docker compose build
docker compose up -d
docker compose ps
```

باید `giv-ytdlp` با وضعیت `running` ببینی.

### قدم ۶ — تست health (روی خود سرور)

```bash
docker exec giv-ytdlp python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:9876/health').read().decode())"
```

انتظار: `"ok": true` و `"r2_configured": true`.

### قدم ۷ — وصل کردن n8n به شبکه (بدون تغییر compose n8n)

فقط یک بار — قابل برگشت:

```bash
docker network connect giv-ytdlp-net n8n-app
```

بررسی:

```bash
docker inspect n8n-app --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
```

باید `giv-ytdlp-net` را ببینی (کنار `web-network` و بقیه).

**برگشت (در صورت نیاز):**

```bash
docker network disconnect giv-ytdlp-net n8n-app
```

### قدم ۸ — تست از داخل کانتینر n8n

```bash
docker exec n8n-app wget -qO- http://giv-ytdlp:9876/health
```

اگر `ok: true` دیدی، n8n می‌تواند به سرویس وصل شود.

### قدم ۹ — تست دانلود (اختیاری ولی توصیه می‌شود)

یک ریل کوتاه اینستا یا ویدیوی یوتیوب — **فقط برای تست**:

```bash
docker exec giv-ytdlp python -c "
import json, urllib.request
req = urllib.request.Request(
    'http://127.0.0.1:9876/download',
    data=json.dumps({'url': 'PASTE_URL_HERE', 'work_id': 'smoke-test'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
print(urllib.request.urlopen(req, timeout=600).read().decode())
"
```

`PASTE_URL_HERE` را با لینک واقعی عوض کن. اگر موفق بود، در R2 باید `library/<video_id>.mp4` و `.jpg` ببینی.

---

## بعد از deploy

وقتی قدم‌های بالا تمام شد، به من بگو تا:

1. workflow n8n را به `http://giv-ytdlp:9876/download` به‌روز کنیم
2. nodeهای Read File / Upload R2 را حذف کنیم (چون سرویس خودش آپلود می‌کند)
3. workflow را import کنی

---

## امنیت

- پورت **روی host باز نمی‌شود** — فقط شبکه Docker داخلی
- `GIV_YTDLP_TOKEN` را ست کن تا فقط n8n (با token در body) بتواند دانلود بزند
- compose و volume مربوط به `/home/alecadmin/n8n` **دست نخورده** می‌ماند

## YouTube روی سرور (cookies + Node)

از ۲۰۲۶، yt-dlp برای یوتیوب به **Node.js** (داخل Docker نصب می‌شود) و معمولاً **cookies مرورگر** نیاز دارد — مخصوصاً روی IP دیتاسنتر (Contabo).

**اینستاگرام** اغلب بدون cookies کار می‌کند. **یوتیوب** بدون `cookies.txt` روی VPS معمولاً خطای bot می‌دهد.

### ۱) Rebuild بعد از به‌روزرسانی کد

```bash
cd /home/alecadmin/giv-ytdlp
# فایل‌های جدید Dockerfile, download.py, config.py را کپی کن
docker compose build --no-cache
docker compose up -d --force-recreate
docker exec giv-ytdlp node --version
```

### ۲) ساخت cookies.txt روی کامپیوتر خودت

1. در Chrome/Edge با اکانت Google لاگین باش (همان اکانتی که یوتیوب باز می‌شود)
2. افزونه **Get cookies.txt LOCALLY** را نصب کن (فقط locally — نسخه‌ای که cookies را upload نمی‌کند)
3. برو `youtube.com` → از افزونه Export → فایل `cookies.txt` ذخیره کن

### ۳) کپی به کانتینر

```bash
docker cp cookies.txt giv-ytdlp:/data/cookies.txt
docker exec giv-ytdlp ls -la /data/cookies.txt
```

سرویس خودکار `/data/cookies.txt` را می‌خواند (نیازی به تغییر `.env` نیست).

### ۴) تست یوتیوب

```bash
docker exec giv-ytdlp yt-dlp --js-runtimes node --cookies /data/cookies.txt -f bv*+ba/b --merge-output-format mp4 -o /tmp/test-%(id)s.%(ext)s "YOUTUBE_URL_HERE"
```

---

## عیب‌یابی

| مشکل | کار |
|------|-----|
| `ECONNREFUSED` از n8n | قدم ۷ را انجام بده؛ URL باید `http://giv-ytdlp:9876` باشد نه `127.0.0.1` |
| `R2 not configured` | `.env` را چک کن؛ `docker compose up -d` دوباره |
| `yt-dlp failed` برای YouTube | `cookies.txt` را بگذار در `/data/cookies.txt` و image را rebuild کن (Node.js) |
| `Sign in to confirm you're not a bot` | cookies منقضی شده — دوباره export کن |
| `503 another download` | صبر کن تا دانلود قبلی تمام شود |
| لاگ | `docker compose logs -f giv-ytdlp` |

## لوکال (بدون Docker)

```bash
cd apps/giv-ytdlp
pip install -r requirements.txt
# ffmpeg باید نصب باشد
export GIV_YTDLP_DATA_DIR=/tmp/giv-ytdlp
python main.py
```

## فایل قدیمی

`scripts/n8n-ytdlp-service.py` نسخه ساده بدون Docker/R2 بود. برای production از همین پوشه `apps/giv-ytdlp` استفاده کن.
