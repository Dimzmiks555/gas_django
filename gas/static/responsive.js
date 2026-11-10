(() => {
    const button = document.querySelector('.navbar-burger');
    const menu = document.getElementById('main-menu');
    if (button && menu) {
        const setOpen = open => {
            button.classList.toggle('is-active', open);
            menu.classList.toggle('is-active', open);
            button.setAttribute('aria-expanded', String(open));
            button.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
        };
        button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
                setOpen(false);
                button.focus();
            }
        });
    }
    const filters = document.querySelector('.filter-panel');
    if (filters) {
        const desktop = matchMedia('(min-width: 1024px)');
        const sync = () => { filters.open = desktop.matches || Boolean(filters.querySelector('.errorlist')); };
        sync();
        desktop.addEventListener('change', sync);
    }
})();
