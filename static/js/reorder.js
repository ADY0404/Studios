// LinkStudio Drag and Drop Links Reordering

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('draggableLinksList');
  if (!container) return;

  let draggedItem = null;

  const items = container.querySelectorAll('.draggable-link-card');
  items.forEach(item => {
    item.addEventListener('dragstart', handleDragStart);
    item.addEventListener('dragover', handleDragOver);
    item.addEventListener('drop', handleDrop);
    item.addEventListener('dragend', handleDragEnd);
  });

  function handleDragStart(e) {
    draggedItem = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const target = this;
    if (target !== draggedItem && target.classList.contains('draggable-link-card')) {
      const rect = target.getBoundingClientRect();
      const next = (e.clientY - rect.top) / (rect.bottom - rect.top) > 0.5;
      container.insertBefore(draggedItem, next && target.nextSibling || target);
    }
  }

  function handleDrop(e) {
    e.stopPropagation();
    return false;
  }

  function handleDragEnd() {
    this.classList.remove('dragging');
    draggedItem = null;
    saveLinkOrder();
  }

  function saveLinkOrder() {
    const currentItems = container.querySelectorAll('.draggable-link-card');
    const order = Array.from(currentItems).map(item => item.dataset.linkId);

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    fetch('/dashboard/links/api/reorder/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ order: order })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        showReorderToast('Links reordered successfully!');
      }
    })
    .catch(err => {
      console.error('Reorder error:', err);
      showReorderToast('Failed to save link order.', true);
    });
  }

  function showReorderToast(msg, isError = false) {
    let container = document.getElementById('globalToastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'globalToastContainer';
      container.className = 'toast-container position-fixed top-0 end-0 p-3';
      container.style.zIndex = '1090';
      document.body.appendChild(container);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast show align-items-center text-bg-${isError ? 'danger' : 'success'} border-0 shadow mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi ${isError ? 'bi-exclamation-triangle-fill' : 'bi-check-circle-fill'} me-2"></i>
          ${msg}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;
    container.appendChild(toastEl);

    setTimeout(() => {
      toastEl.classList.remove('show');
      setTimeout(() => toastEl.remove(), 400);
    }, 3000);
  }
});
