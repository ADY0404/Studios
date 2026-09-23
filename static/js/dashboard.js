// LinkStudio Bootstrap 5 Dashboard Interactions

document.addEventListener('DOMContentLoaded', () => {
  // Mobile sidebar toggle
  const sidebar = document.getElementById('dashboardSidebar');
  const toggleBtn = document.getElementById('sidebarToggleBtn');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });

    // Close on clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 992 && sidebar.classList.contains('show') && !sidebar.contains(e.target) && e.target !== toggleBtn) {
        sidebar.classList.remove('show');
      }
    });
  }

  // Auto initialize all Bootstrap tooltips & toasts
  const toastElList = document.querySelectorAll('.toast');
  toastElList.forEach(toastEl => {
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
  });
});
