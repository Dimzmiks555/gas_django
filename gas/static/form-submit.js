// Kept separate from page-specific scripts so an unrelated JS error cannot disable it.
(() => {
    const pending = new Map();
    document.addEventListener('submit', (event) => {
        const form = event.target;
        if (pending.has(form)) {
            event.preventDefault();
            return;
        }
        if (event.defaultPrevented) return;
        const buttons = [...form.querySelectorAll('button, input[type="submit"], input[type="image"]')]
            .filter(button => ['submit', 'image'].includes(button.type) && !button.disabled);
        pending.set(form, buttons);
        form.setAttribute('aria-busy', 'true');
        // Delay disabling until the browser has included the clicked button's
        // name/value in the POST (Django admin uses _save / _continue / action).
        setTimeout(() => {
            if (event.defaultPrevented) {
                pending.delete(form);
                form.removeAttribute('aria-busy');
                form.querySelector('[data-submission-status]')?.remove();
                return;
            }
            if (!pending.has(form)) return;
            buttons.forEach(button => {
                button.disabled = true;
                button.classList.add('is-loading');
            });
        }, 0);
        const status = document.createElement('span');
        status.dataset.submissionStatus = '';
        status.setAttribute('role', 'status');
        status.textContent = ' Отправка…';
        form.appendChild(status);
    });
    // Back navigation may refetch a no-store page while restoring old inputs.
    // Keep its original submission tokens so that this is still a retry.
    window.addEventListener('pagehide', () => {
        const tokens = [...document.querySelectorAll('input[name="_submission_token"]')]
            .map(input => ({action: input.form.action, value: input.value}));
        history.replaceState({...history.state, gasSubmissionTokens: tokens}, '');
    });
    window.addEventListener('pageshow', (event) => {
        pending.forEach((buttons, form) => {
            buttons.forEach(button => {
                button.disabled = false;
                button.classList.remove('is-loading');
            });
            form.removeAttribute('aria-busy');
            form.querySelector('[data-submission-status]')?.remove();
        });
        pending.clear();
        const back = event.persisted || performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
        if (back && history.state?.gasSubmissionTokens) {
            document.querySelectorAll('input[name="_submission_token"]').forEach((input, index) => {
                const previous = history.state.gasSubmissionTokens[index];
                if (previous?.action === input.form.action) input.value = previous.value;
            });
        }
    });
})();
