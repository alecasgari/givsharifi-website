# راه‌اندازی ویدیوها با Cloudflare R2

این راهنما برای **۴ ویدیوی صفحه اصلی** است. بعداً همین الگو را برای تالار ویدیو (`/videos/`) تکرار می‌کنیم.

## وضعیت فعلی سایت

- ویدیوها داخل گیت نیستند (حجم ~۲۸۰ مگابایت).
- لیست ویدیوها در `assets/data/home-videos.json` است.
- صفحه اصلی با `assets/js/home-videos.js` این فایل را می‌خواند و `<video>` می‌سازد.
- تا وقتی R2 را وصل نکرده‌اید، می‌توانید فایل‌ها را لوکال در پوشه `video/` بگذارید (برای تست).

### نام ۴ فایل

| فایل | عنوان در سایت |
|------|----------------|
| `Cranial-Nerves-Problem.mp4` | Brain Tumor & Cranial Nerves |
| `Brain-Tumor-Surgery-with-panic-attack.mp4` | Brain Tumor Surgery |
| `Tumor-Affecting-Hearing-and-Balance.mp4` | Tumor Affecting Hearing & Balance |
| `brain-cyst.mp4` | Brain Cyst |

---

## بخش ۱ — آماده‌سازی فایل‌ها روی کامپیوتر

1. اگر هنوز ندارید، پوشه `video` را از بکاپ وردپرس کپی کنید:
   ```
   OLD-WP-Website/Wordpress-website/video/  →  givsharifi-website/video/
   ```
2. مطمئن شوید هر ۴ فایل بالا داخل `givsharifi-website/video/` هستند.
3. نام فایل‌ها را عوض نکنید (همان نام‌های انگلیسی با خط تیره).

---

## بخش ۲ — فعال‌سازی R2 در Cloudflare

1. وارد [dash.cloudflare.com](https://dash.cloudflare.com) شوید (همان اکانتی که `givsharifi.com` روی آن است).
2. از منوی چپ **R2 Object Storage** را بزنید.
   - اگر نمی‌بینید: از جستجوی بالا «R2» را تایپ کنید.
3. اولین بار ممکن است بخواهد **روش پرداخت** اضافه کنید.
   - R2 پلن رایگان دارد: **۱۰ گیگابایت** فضا + ترافیک egress رایگان از طریق Cloudflare.
   - برای ۴ ویدیوی تست معمولاً هزینه‌ای نمی‌شود.

---

## بخش ۳ — ساخت Bucket

1. **Create bucket** را بزنید.
2. تنظیمات پیشنهادی:
   - **Bucket name:** `givsharifi-videos` (یا هر نامی که دوست دارید؛ فقط یادداشت کنید)
   - **Location:** Automatic (پیش‌فرض)
3. **Create bucket**.

---

## بخش ۴ — آپلود ویدیوها

1. روی bucket جدید کلیک کنید.
2. **Upload** → **Upload files** (یا drag & drop).
3. قبل از آپلود، داخل bucket یک پوشه بسازید:
   - نام پوشه: `homepage`
4. وارد پوشه `homepage` شوید و **۴ فایل MP4** را آپلود کنید.
5. بعد از آپلود، مسیر هر فایل باید شبیه این باشد:
   ```
   givsharifi-videos / homepage / Cranial-Nerves-Problem.mp4
   ```

**نکته:** اگر Content-Type درست نبود، در تنظیمات object باید `video/mp4` باشد. آپلود از داشبورد معمولاً خودکار درست می‌کند.

---

## بخش ۵ — دامنه اختصاصی برای ویدیو (پیشنهادی)

به‌جای لینک‌های طولانی `r2.dev`، یک زیردامنه مثل **`media.givsharifi.com`** می‌سازیم.

### ۵.۱ اتصال دامنه به Bucket

1. داخل bucket → تب **Settings**.
2. بخش **Custom Domains** → **Connect Domain**.
3. بنویسید: `media.givsharifi.com`
4. **Continue** / **Connect**.
5. چون دامنه `givsharifi.com` همین الان روی Cloudflare است، معمولاً **خودکار** رکورد DNS را اضافه می‌کند.

### ۵.۲ بررسی DNS

1. بروید **DNS → Records** برای `givsharifi.com`.
2. باید رکورد جدیدی شبیه این ببینید:
   - **Type:** CNAME (یا R2-managed)
   - **Name:** `media`
   - **Target:** آدرسی که Cloudflare برای R2 داده
   - **Proxy:** معمولاً Proxied (ابر نارنجی)

اگر بعد از ۵–۱۰ دقیقه `media.givsharifi.com` باز نشد، صفحه Custom Domains bucket را دوباره چک کنید.

### ۵.۳ تست لینک مستقیم

در مرورگر این را باز کنید (بعد از اتصال دامنه):

```
https://media.givsharifi.com/homepage/Cranial-Nerves-Problem.mp4
```

- اگر ویدیو دانلود/پخش شد → درست است.
- اگر ۴۰۴ → مسیر پوشه یا نام فایل را چک کنید.
- اگر ۴۰۳ → Public access / Custom domain هنوز کامل نشده.

---

## بخش ۶ — CORS (اختیاری ولی مفید)

برای پخش از `www.givsharifi.com` گاهی CORS لازم می‌شود.

1. داخل bucket → **Settings** → **CORS Policy**.
2. این JSON را بگذارید:

```json
[
  {
    "AllowedOrigins": [
      "https://www.givsharifi.com",
      "https://givsharifi.com",
      "https://alecasgari.github.io"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

3. Save.

---

## بخش ۷ — به‌روزرسانی سایت

فایل `assets/data/home-videos.json` را باز کنید و این دو خط را عوض کنید:

**قبل (تست لوکال):**
```json
"baseUrl": "",
"pathPrefix": "video"
```

**بعد (R2 با دامنه media):**
```json
"baseUrl": "https://media.givsharifi.com",
"pathPrefix": "homepage"
```

بقیه فایل را دست نزنید. سپس commit و push کنید تا GitHub Pages دوباره deploy شود.

---

## بخش ۸ — تست نهایی

1. صفحه اصلی را باز کنید: `https://www.givsharifi.com/` (یا آدرس GitHub Pages).
2. به بخش **Neurosurgery Education Videos** بروید.
3. هر ۴ ویدیو باید poster داشته باشند و با Play پخش شوند.
4. DevTools → Network: درخواست‌ها باید به `media.givsharifi.com` بروند، نه `givsharifi.com/video/...`.

---

## روش سریع تست (بدون دامنه اختصاصی)

اگر فقط می‌خواهید سریع تست کنید:

1. Bucket → Settings → **Public Development URL** را Enable کنید.
2. آدرسی مثل `https://pub-xxxxxxxx.r2.dev` می‌گیرید.
3. در JSON بنویسید:
   ```json
   "baseUrl": "https://pub-xxxxxxxx.r2.dev",
   "pathPrefix": "homepage"
   ```
4. لینک تست:
   `https://pub-xxxxxxxx.r2.dev/homepage/Cranial-Nerves-Problem.mp4`

**توجه:** برای پروداکشن حتماً `media.givsharifi.com` را جایگزین کنید.

---

## عیب‌یابی

| مشکل | احتمال |
|------|--------|
| ویدیو سیاه، بدون پخش | فایل آپلود نشده یا مسیر `homepage/` اشتباه |
| ۴۰۴ روی media.givsharifi.com | Custom domain هنوز propagate نشده (۵–۳۰ دقیقه صبر) |
| فقط ۲ ویدیو | کش مرورگر — Hard Refresh (`Ctrl+Shift+R`) |
| کار نمی‌کند روی GitHub Pages | `baseUrl` باید کامل `https://...` باشد، خالی نماند |
| هزینه نگرانم | در R2 → Analytics مصرف را ببینید؛ ۴ ویدیو در free tier جا می‌شود |

---

## مرحله بعد: تالار ویدیو (`/videos/`)

وقتی این ۴ تا درست شد:

1. پوشه جدید در bucket: مثلاً `library/`
2. بقیه ویدیوها را آنجا آپلود کنید
3. صفحه `/videos/` را با JSON مشابه `home-videos.json` می‌سازیم

---

## چک‌لیست شما

- [ ] ۴ فایل MP4 روی کامپیوتر آماده است
- [ ] Bucket `givsharifi-videos` ساخته شد
- [ ] فایل‌ها در `homepage/` آپلود شدند
- [ ] `media.givsharifi.com` وصل شد
- [ ] لینک مستقیم یک ویدیو در مرورگر کار می‌کند
- [ ] `home-videos.json` با `baseUrl` جدید به‌روز شد
- [ ] سایت deploy شد و ۴ ویدیو روی صفحه اصلی پخش می‌شوند

وقتی تا مرحله آپلود R2 پیش رفتی، بگو تا `home-videos.json` را با آدرس واقعی‌ات تنظیم و push کنیم.
