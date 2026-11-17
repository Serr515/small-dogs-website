function filterBreeds(breeds, trait) {
  return trait === 'all' ? breeds : breeds.filter((breed) => breed.traits.includes(trait));
}

if (typeof module !== 'undefined') module.exports = { filterBreeds };

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
