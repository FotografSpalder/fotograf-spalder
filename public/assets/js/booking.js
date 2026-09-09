(() => {
  'use strict';

  const form = document.getElementById('bookingForm');
  const submitButton = document.getElementById('submitButton');
  const formStatus = document.getElementById('formStatus');
  if (!form || !submitButton || !formStatus) return;

  form.addEventListener('submit', async event => {
    event.preventDefault();
    submitButton.disabled = true;
    submitButton.textContent = 'Sender ...';
    formStatus.textContent = 'Sender forespørselen ...';

    try {
      const data = new FormData(form);
      const response = await fetch('https://formspree.io/f/xeepjwnb', {
        method: 'POST',
        body: data,
        headers: { Accept: 'application/json' }
      });
      if (!response.ok) throw new Error('Formspree returnerte feilstatus');

      if (typeof window.gtag === 'function') {
        window.gtag('event', 'booking_sent', {
          event_category: 'booking',
          event_label: 'booking_form'
        });
      }
      window.location.href = 'takk.html';
    } catch (_) {
      formStatus.textContent = 'Noe gikk galt. Prøv igjen, eller kontakt Fotograf Spalder på e-post eller SMS.';
      submitButton.disabled = false;
      submitButton.textContent = 'Send bookingforespørsel';
    }
  });
})();
