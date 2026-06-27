(function () {
  const homeHref = typeof window.siteUrl === 'function' ? window.siteUrl('./') : '/';
  const box = document.getElementById('thank-you-content');
  if (!box) return;

  let data = null;
  try {
    data = JSON.parse(sessionStorage.getItem('giv_booking_result') || 'null');
  } catch {
    data = null;
  }

  if (!data) {
    box.innerHTML = `
      <div class="pg-thanks__box">
        <div class="pg-thanks__icon" aria-hidden="true">✓</div>
        <h1>Thank You</h1>
        <p>Your request has been received. Our team will contact you shortly.</p>
        <div class="pg-thanks__actions">
          <a href="${homeHref}" class="btn btn--primary">Back to Home</a>
        </div>
      </div>
    `;
    return;
  }

  const tracking = data.tracking && data.tracking !== '—' ? data.tracking : null;

  box.innerHTML = `
    <div class="pg-thanks__box">
      <div class="pg-thanks__icon" aria-hidden="true">✓</div>
      <h1>Thank You${data.name ? ', ' + escapeHtml(data.name.split(' ')[0]) : ''}!</h1>
      <p>Your consultation request has been received successfully.</p>
      ${tracking ? `
        <p>Your tracking reference:</p>
        <div class="pg-thanks__tracking" id="tracking-code">${escapeHtml(tracking)}</div>
        <p style="font-size:0.875rem">Please save this reference for follow-up.</p>
      ` : '<p>We will be in touch soon.</p>'}
      <div class="pg-thanks__actions">
        <button type="button" class="btn btn--whatsapp" data-open-whatsapp>Chat on WhatsApp</button>
        <a href="${homeHref}" class="btn btn--secondary">Back to Home</a>
      </div>
    </div>
  `;
})();

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
