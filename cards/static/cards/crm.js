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

const attendanceChart = document.querySelector('.attendance-chart');
if (attendanceChart && window.Chart) {
  const { present, absent, excused } = attendanceChart.dataset;
  new window.Chart(attendanceChart, {
    type: 'doughnut',
    data: {
      labels: ['Kelgan', 'Kelmagan', 'Sababli'],
      datasets: [{
        data: [Number(present), Number(absent), Number(excused)],
        backgroundColor: ['#635bdf', '#f3a33b', '#31a79b'],
        borderWidth: 0,
      }],
    },
    options: {
      cutout: '74%',
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (item) => `${item.label} — ${item.raw}%` } },
      },
    },
  });
  attendanceChart.parentElement.classList.add('chart-ready');
}

