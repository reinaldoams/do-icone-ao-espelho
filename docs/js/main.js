// Rolar até o corredor ao voltar de outra página
if (window.location.hash === '#salas') {
  window.addEventListener('load', () => {
    const alvo = document.getElementById('salas');
    if (alvo) setTimeout(() => alvo.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150);
  });
}

// Efeito de abertura ao clicar na porta
document.querySelectorAll('.porta-link, .porta-grande-link').forEach(link => {
  link.addEventListener('click', function (e) {
    const folha = this.querySelector('.porta-folha');
    if (folha) {
      e.preventDefault();
      folha.style.transform = 'rotateY(-75deg)';
      folha.style.transition = 'transform 0.7s cubic-bezier(0.4,0,0.2,1)';
      setTimeout(() => { window.location.href = this.href; }, 650);
    }
  });
});

// Fade-in ao rolar
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.style.opacity = '1';
  });
}, { threshold: 0.1 });

document.querySelectorAll('.obra-card, .porta-link').forEach(el => {
  el.style.opacity = '0';
  el.style.transition = 'opacity 0.6s ease';
  observer.observe(el);
});
