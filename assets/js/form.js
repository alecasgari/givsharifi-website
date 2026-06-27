(function () {
  const WEBHOOK = 'https://n8n.alecasgari.com/webhook/7d580876-f96b-4a1b-a829-3a7458caf881';
  const STORAGE_KEY = 'giv_booking_result';

  function getUtmParams() {
    const params = new URLSearchParams(window.location.search);
    const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
    const utm = {};
    keys.forEach((k) => {
      const v = params.get(k);
      if (v) utm[k] = v;
    });
    return utm;
  }

  function persistUtm() {
    const utm = getUtmParams();
    if (Object.keys(utm).length) {
      sessionStorage.setItem('giv_utm', JSON.stringify(utm));
    }
  }

  function getStoredUtm() {
    try {
      return JSON.parse(sessionStorage.getItem('giv_utm') || '{}');
    } catch {
      return {};
    }
  }

  function extractTrackingCode(data) {
    if (!data || typeof data !== 'object') return null;
    const keys = [
      'tracking_number', 'trackingNumber', 'reference_number', 'referenceNumber',
      'ref', 'code', 'booking_id', 'bookingId', 'id'
    ];
    for (const k of keys) {
      if (data[k]) return String(data[k]);
    }
    if (Array.isArray(data) && data[0]) return extractTrackingCode(data[0]);
    if (data.data && typeof data.data === 'object') return extractTrackingCode(data.data);
    return null;
  }

  function onlyDigits(value) {
    return String(value || '').replace(/\D/g, '');
  }

  function parsePastedPhone(raw, countryCode) {
    let digits = onlyDigits(raw);
    const cc = onlyDigits(countryCode);
    if (!digits) return { countryCode: cc, local: '' };

    if (raw.trim().startsWith('+') || digits.startsWith('00')) {
      const withoutPlus = raw.trim().startsWith('+') ? digits : digits.slice(2);
      const codes = [
        '971', '966', '965', '974', '968', '973', '962', '961', '964',
        '98', '93', '92', '91', '90', '86', '61', '49', '47', '46',
        '45', '41', '39', '34', '33', '31', '30', '20', '7', '1', '44', '351'
      ].sort((a, b) => b.length - a.length);

      for (const code of codes) {
        if (withoutPlus.startsWith(code) && withoutPlus.length > code.length + 6) {
          return { countryCode: code, local: withoutPlus.slice(code.length).replace(/^0+/, '') };
        }
      }
    }

    if (cc && digits.startsWith(cc) && digits.length > cc.length + 6) {
      digits = digits.slice(cc.length);
    }

    return { countryCode: cc, local: digits.replace(/^0+/, '') };
  }

  function normalizePhone(countryCode, rawPhone) {
    return parsePastedPhone(rawPhone, countryCode).local;
  }

  function validatePhone(countryCode, rawPhone) {
    const parsed = parsePastedPhone(rawPhone, countryCode);
    const local = parsed.local;

    if (!local) {
      return { ok: false, message: 'Please enter your WhatsApp mobile number.' };
    }
    if (local.length < 7) {
      return { ok: false, message: 'This number looks too short. Check and try again.' };
    }
    if (local.length > 15) {
      return { ok: false, message: 'This number looks too long. Enter mobile number without country code.' };
    }
    return { ok: true, countryCode: parsed.countryCode, local };
  }

  function showFieldError(form, message) {
    const msg = form.querySelector('.form-message');
    const phoneWrap = form.querySelector('.phone-field');
    if (phoneWrap) phoneWrap.classList.add('is-invalid');
    if (msg) {
      msg.className = 'form-message is-error';
      msg.textContent = message;
    }
  }

  function clearFieldError(form) {
    const msg = form.querySelector('.form-message');
    const phoneWrap = form.querySelector('.phone-field');
    if (phoneWrap) phoneWrap.classList.remove('is-invalid');
    if (msg) {
      msg.className = 'form-message';
      msg.textContent = '';
    }
  }

  function bindPhoneField(form) {
    const codeEl = form.querySelector('[name="patient_number_copy_country"]');
    const phoneEl = form.querySelector('[name="patient_number"]');
    if (!codeEl || !phoneEl || phoneEl.dataset.phoneBound) return;
    phoneEl.dataset.phoneBound = '1';

    phoneEl.addEventListener('input', () => {
      clearFieldError(form);
    });

    phoneEl.addEventListener('paste', (e) => {
      const pasted = (e.clipboardData || window.clipboardData).getData('text');
      if (!pasted || !/[+\d]/.test(pasted)) return;

      e.preventDefault();
      const parsed = parsePastedPhone(pasted, codeEl.value);
      if (parsed.countryCode) codeEl.value = parsed.countryCode;
      phoneEl.value = parsed.local;
      clearFieldError(form);
    });

    phoneEl.addEventListener('blur', () => {
      const parsed = parsePastedPhone(phoneEl.value, codeEl.value);
      if (parsed.countryCode && parsed.countryCode !== codeEl.value) {
        codeEl.value = parsed.countryCode;
      }
      phoneEl.value = parsed.local;
    });
  }

  function isHoneypotTripped(form) {
    const website = form.querySelector('[name="website"]');
    return Boolean(website && website.value.trim());
  }

  function bindCharCounter(form) {
    const issue = form.querySelector('[name="issue"]');
    const counter = form.querySelector('[data-char-count]');
    if (!issue || !counter || issue.dataset.counterBound) return;
    issue.dataset.counterBound = '1';

    const max = Number(issue.getAttribute('maxlength')) || 300;

    function update() {
      const len = issue.value.length;
      counter.textContent = len + ' / ' + max;
      counter.classList.toggle('is-near-limit', len >= max - 30 && len < max);
      counter.classList.toggle('is-at-limit', len >= max);
    }

    issue.addEventListener('input', update);
    update();
  }

  function setLoading(form, on) {
    const overlay = form.querySelector('.form-loading');
    const btn = form.querySelector('[type="submit"]');
    if (overlay) overlay.classList.toggle('is-visible', on);
    if (btn) {
      btn.disabled = on;
      btn.textContent = on ? 'Sending…' : 'Get Free Consultation';
    }
  }

  async function submitForm(form) {
    const msg = form.querySelector('.form-message');
    if (isHoneypotTripped(form)) return;

    const fd = new FormData(form);
    const countryCode = fd.get('patient_number_copy_country') || '';
    const phoneRaw = fd.get('patient_number') || '';
    const phoneCheck = validatePhone(countryCode, phoneRaw);

    if (!phoneCheck.ok) {
      showFieldError(form, phoneCheck.message);
      return;
    }

    const normalizedCountry = phoneCheck.countryCode;
    const phone = phoneCheck.local;

    const payload = {
      patient_name: fd.get('patient_name') || '',
      patient_number_copy_country: normalizedCountry,
      patient_number: phone,
      issue: (fd.get('issue') || '').slice(0, 300),
      phone_full: '+' + normalizedCountry + phone,
      source: 'website',
      page: window.location.pathname,
      referrer: document.referrer || '',
      submitted_at: new Date().toISOString(),
      ...getStoredUtm(),
      ...getUtmParams()
    };

    if (msg) {
      msg.className = 'form-message';
      msg.textContent = '';
    }
    setLoading(form, true);

    try {
      const res = await fetch(WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      });

      let data = {};
      const text = await res.text();
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { raw: text };
      }

      if (!res.ok) {
        throw new Error(data.message || data.error || 'Submission failed');
      }

      const tracking = extractTrackingCode(data) || '—';
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
        tracking,
        name: payload.patient_name,
        phone: payload.phone_full,
        response: data
      }));

      window.location.href = typeof window.siteUrl === 'function' ? window.siteUrl('done/') : '/done/';
    } catch (err) {
      setLoading(form, false);
      if (msg) {
        msg.className = 'form-message is-error';
        msg.textContent = err.message || 'Something went wrong. Please try WhatsApp or call us directly.';
      }
    }
  }

  function initForms() {
    persistUtm();
    document.querySelectorAll('[data-consultation-form]').forEach((form) => {
      bindPhoneField(form);
      bindCharCounter(form);
      if (form.dataset.bound) return;
      form.dataset.bound = '1';
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(form);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initForms);
  } else {
    initForms();
  }
  document.addEventListener('giv:forms-ready', initForms);
})();
