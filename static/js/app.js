document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('#site-search');
  if (searchInput) {
    searchInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        const value = searchInput.value.trim();
        if (value) {
          window.location.href = '/buscar?q=' + encodeURIComponent(value);
        }
      }
    });
  }
});
