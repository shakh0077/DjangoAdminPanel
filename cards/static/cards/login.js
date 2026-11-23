const passwordToggle = document.querySelector('.password-toggle');
const password = document.getElementById(passwordToggle.getAttribute('aria-controls'));

passwordToggle.hidden = false;
passwordToggle.addEventListener('click', () => {
  const visible = password.type === 'password';
  password.type = visible ? 'text' : 'password';
  passwordToggle.setAttribute('aria-pressed', String(visible));
  passwordToggle.setAttribute('aria-label', visible ? 'Parolni yashirish' : 'Parolni ko‘rsatish');
});
