function filterBreeds(breeds, trait) {
  return trait === 'all' ? breeds : breeds.filter((breed) => breed.traits.includes(trait));
}

if (typeof module !== 'undefined') module.exports = { filterBreeds };

if (typeof document !== 'undefined') {
  const form = document.querySelector('#feedback-form');
  const status = document.querySelector('#feedback-status');
  if (form && location.protocol === 'file:') {
    const preview = document.createElement('a');
    preview.href = 'http://127.0.0.1:18743/#question';
    preview.textContent = 'Открыть форму в локальной версии сайта';
    form.replaceWith(preview);
  } else if (form) {
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const button = form.querySelector('button');
      button.disabled = true;
      status.textContent = 'Отправляем…';
      try {
        const result = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-Feedback': '1' },
          body: new URLSearchParams(new FormData(form))
        });
        if (result.status !== 204) throw new Error();
        form.reset();
        status.textContent = 'Спасибо! Ваше обращение получено.';
      } catch {
        status.textContent = 'Не удалось отправить. Попробуйте ещё раз или напишите в Telegram.';
      } finally {
        button.disabled = false;
      }
    });
  }
}

if (typeof document !== 'undefined') {
  const cards = Array.from(document.querySelectorAll('.breed-card')).map((element) => ({
    element,
    traits: element.dataset.traits.split(',')
  }));
  const buttons = Array.from(document.querySelectorAll('[data-filter]'));
  const count = document.querySelector('#result-count');

  function updateFilter(trait) {
    const visible = new Set(filterBreeds(cards, trait));
    cards.forEach((card) => { card.element.hidden = !visible.has(card); });
    buttons.forEach((button) => {
      const selected = button.dataset.filter === trait;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    count.textContent = `Показано пород: ${visible.size}`;
  }

  buttons.forEach((button) => button.addEventListener('click', () => updateFilter(button.dataset.filter)));
  updateFilter('all');

  const menuButton = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('#navigation');
  function setMenu(open) {
    navigation.classList.toggle('is-open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.querySelector('span').textContent = open ? '×' : '☰';
  }
  menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      menuButton.focus();
    }
  });
}
