(() => {
  const search = document.querySelector('[data-resource-search]');
  if (!search) return;
  const chapter = document.querySelector('[data-chapter-filter]');
  const buttons = [...document.querySelectorAll('[data-type-filter]')];
  const resources = [...document.querySelectorAll('[data-resource]')];
  const count = document.querySelector('[data-result-count]');
  const empty = document.querySelector('[data-empty-state]');
  let kind = 'all';
  const normalize = value => value.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const update = () => {
    const query = normalize(search.value.trim());
    let visible = 0;
    resources.forEach(row => {
      const matches = (kind === 'all' || row.dataset.type === kind)
        && (!chapter.value || row.dataset.chapter === chapter.value)
        && normalize(row.textContent).includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = `${visible} ${visible === 1 ? 'resource' : 'resources'}`;
    empty.hidden = visible > 0;
  };
  buttons.forEach(button => button.addEventListener('click', () => {
    kind = button.dataset.typeFilter;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    update();
  }));
  search.addEventListener('input', update);
  chapter.addEventListener('change', update);
  const params = new URLSearchParams(window.location.search);
  if (params.has('chapter') && [...chapter.options].some(option => option.value === params.get('chapter'))) chapter.value = params.get('chapter');
  if (params.has('q')) search.value = params.get('q');
  update();
})();
