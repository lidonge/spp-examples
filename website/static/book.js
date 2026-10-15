const contents = document.querySelector('.book-toc');
if (contents && matchMedia('(max-width: 960px)').matches) contents.open = false;
const search = document.querySelector('#chapter-search');
if (search) {
  search.addEventListener('input', () => {
    const term = search.value.trim().toLowerCase();
    let matches = 0;
    document.querySelectorAll('.toc-link').forEach(link => {
      link.hidden = term !== '' && !link.dataset.title.includes(term);
      if (!link.hidden) matches += 1;
    });
    document.querySelector('#chapter-search-empty').hidden = matches > 0;
  });
}
