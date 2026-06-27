# N8N Webhook — Consultation Form

**Endpoint:** `https://n8n.alecasgari.com/webhook/7d580876-f96b-4a1b-a829-3a7458caf881`

## Payload (POST JSON)

```json
{
  "name": "Patient Name",
  "phone": "+971501234567",
  "email": "patient@email.com",
  "country": "UAE",
  "message": "Optional message",
  "source": "website",
  "page": "/",
  "referrer": "https://google.com/...",
  "submitted_at": "2026-06-25T12:00:00.000Z",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "brand",
  "utm_term": "",
  "utm_content": ""
}
```

## Expected response (for tracking code on /done/)

Return JSON with one of these fields:

```json
{
  "tracking_number": "GS-2026-001234"
}
```

Also supported field names: `trackingNumber`, `reference_number`, `referenceNumber`, `ref`, `code`, `booking_id`, `id`

## CORS

N8N webhook must allow origin `https://www.givsharifi.com` (and `http://localhost:*` for local testing).

In N8N Webhook node → Options → Response Headers:
```
Access-Control-Allow-Origin: https://www.givsharifi.com
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Local testing

```bash
cd givsharifi-website
python -m http.server 8080
# Open http://localhost:8080
```

Note: webhook CORS may block localhost unless configured in N8N.
