(() => {
    const dialog = document.querySelector('[data-act-dialog]');
    if (dialog) {
        const frame = dialog.querySelector('iframe');
        const open = (link) => {
            frame.src = link.href;
            dialog.showModal();
        };
        document.querySelectorAll('[data-open-act]').forEach(link => link.addEventListener('click', event => {
            event.preventDefault();
            open(link);
        }));
        dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
        window.addEventListener('message', event => {
            if (event.origin !== location.origin || event.source !== frame.contentWindow) return;
            if (event.data?.type === 'close-act') dialog.close();
            if (event.data?.type === 'act-saved') {
                const link = [...document.querySelectorAll('[data-open-act]')].find(link => link.dataset.openAct === event.data.id);
                if (link) {
                    history.replaceState(null, '', '#act-' + event.data.id);
                    location.reload();
                }
            }
        });
        const active = [...document.querySelectorAll('[data-open-act]')].find(link => '#act-' + link.dataset.openAct === location.hash);
        if (active) open(active);
    }
    document.querySelector('[data-close-act]')?.addEventListener('click', () => {
        if (window.parent !== window) window.parent.postMessage({type: 'close-act'}, location.origin);
        else history.back();
    });
    const saved = document.querySelector('[data-act-saved]');
    if (saved && window.parent !== window) {
        window.parent.postMessage({type: 'act-saved', id: saved.dataset.actId}, location.origin);
    }
})();
