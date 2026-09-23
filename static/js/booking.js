// LinkStudio Bootstrap 5 Public Booking Modal & Slot Picker

let bookingModalInstance = null;

function openBookingModal(serviceId, serviceTitle, serviceDuration, servicePrice) {
  const modalEl = document.getElementById('bookingModal');
  if (!modalEl) return;

  const titleEl = document.getElementById('bookingModalServiceTitle');
  if (titleEl) titleEl.textContent = serviceTitle;
  
  const metaEl = document.getElementById('bookingModalMeta');
  if (metaEl) {
    const priceText = parseFloat(servicePrice) > 0 ? `$${servicePrice}` : 'Free';
    metaEl.textContent = `${serviceDuration} mins · ${priceText}`;
  }
  
  const srvInput = document.getElementById('bookingFormServiceId');
  if (srvInput) srvInput.value = serviceId;

  // Set action on form
  const username = modalEl.dataset.username;
  const formEl = document.getElementById('bookingSubmissionForm');
  if (formEl) formEl.action = `/${username}/book/${serviceId}/`;

  // Set min date to local today
  const dateInput = document.getElementById('bookingDateInput');
  const d = new Date();
  const todayStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  if (dateInput) {
    dateInput.min = todayStr;
    if (!dateInput.value || dateInput.value < todayStr) {
      dateInput.value = todayStr;
    }
  }

  loadAvailableSlots(serviceId, dateInput ? dateInput.value : todayStr);

  if (!bookingModalInstance) {
    bookingModalInstance = new bootstrap.Modal(modalEl);
  }
  bookingModalInstance.show();
}

function loadAvailableSlots(serviceId, dateStr) {
  const modalEl = document.getElementById('bookingModal');
  const username = modalEl.dataset.username;
  const container = document.getElementById('slotsContainer');
  const submitBtn = document.getElementById('submitBookingBtn');
  const timeInput = document.getElementById('selectedTimeInput');

  timeInput.value = '';
  submitBtn.disabled = true;
  container.innerHTML = '<div class="text-center text-muted small py-3 col-12">Loading available times...</div>';

  fetch(`/${username}/api/slots/?service_id=${serviceId}&date=${dateStr}`)
    .then(res => res.json())
    .then(data => {
      container.innerHTML = '';
      if (!data.slots || data.slots.length === 0) {
        container.innerHTML = '<div class="text-center text-muted small py-3 col-12">No available times on this date. Please select another date.</div>';
        return;
      }

      data.slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-outline-primary btn-sm slot-pill';
        btn.textContent = slot;
        btn.addEventListener('click', () => {
          container.querySelectorAll('.slot-pill').forEach(p => {
            p.classList.remove('btn-primary', 'active');
            p.classList.add('btn-outline-primary');
          });
          btn.classList.remove('btn-outline-primary');
          btn.classList.add('btn-primary', 'active');
          timeInput.value = slot;
          submitBtn.disabled = false;
        });
        container.appendChild(btn);
      });
    })
    .catch(err => {
      console.error('Error fetching slots:', err);
      container.innerHTML = '<div class="text-center text-danger small py-3 col-12">Unable to load times.</div>';
    });
}

document.addEventListener('DOMContentLoaded', () => {
  // Delegate click for Book Now buttons
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.book-service-btn');
    if (btn) {
      e.preventDefault();
      openBookingModal(
        btn.dataset.serviceId,
        btn.dataset.serviceTitle,
        btn.dataset.serviceDuration,
        btn.dataset.servicePrice
      );
    }
  });

  const dateInput = document.getElementById('bookingDateInput');
  if (dateInput) {
    const handleDateUpdate = (e) => {
      const serviceId = document.getElementById('bookingFormServiceId').value;
      if (serviceId && e.target.value) {
        loadAvailableSlots(serviceId, e.target.value);
      }
    };
    dateInput.addEventListener('change', handleDateUpdate);
    dateInput.addEventListener('input', handleDateUpdate);
  }
});
