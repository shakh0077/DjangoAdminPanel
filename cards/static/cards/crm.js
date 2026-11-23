const menuButton = document.querySelector('.menu-toggle');
const sidebar = document.querySelector('.sidebar');

function setMenuOpen(isOpen) {
  sidebar.classList.toggle('open', isOpen);
  menuButton.setAttribute('aria-expanded', String(isOpen));
  menuButton.setAttribute('aria-label', isOpen ? 'Menyuni yopish' : 'Menyuni ochish');
}

menuButton.addEventListener('click', () => setMenuOpen(!sidebar.classList.contains('open')));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && sidebar.classList.contains('open')) {
    setMenuOpen(false);
    menuButton.focus();
  }
});
document.addEventListener('click', (event) => {
  if (!sidebar.contains(event.target) && !menuButton.contains(event.target)) {
    setMenuOpen(false);
  }
});

