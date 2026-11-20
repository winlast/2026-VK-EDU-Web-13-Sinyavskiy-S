const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
const loginLink = document.querySelector('[data-forum-login]');

async function postAction(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfInput.value},
        body: new URLSearchParams(data),
    });
    if (response.status === 401) {
        const loginUrl = new URL(loginLink.dataset.forumLogin, window.location.origin);
        loginUrl.searchParams.set('next', window.location.pathname + window.location.search);
        window.location.assign(loginUrl);
        throw new Error('Войдите, чтобы продолжить.');
    }
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
        const fallback = response.status === 403
            ? 'Запрос отклонён. Обновите страницу и попробуйте снова.'
            : 'Не удалось выполнить действие.';
        throw new Error(body.error || fallback);
    }
    return body;
}

function showError(feedback, error) {
    feedback.classList.remove('visually-hidden');
    feedback.textContent = error.message || 'Не удалось отправить запрос.';
}

for (const vote of document.querySelectorAll('[data-vote-url]')) {
    const buttons = [...vote.querySelectorAll('button[data-value]')];
    const feedback = vote.querySelector('[data-feedback]');
    for (const button of buttons) {
        button.addEventListener('click', async () => {
            const value = button.getAttribute('aria-pressed') === 'true' ? 0 : Number(button.dataset.value);
            buttons.forEach(control => { control.disabled = true; });
            feedback.textContent = '';
            try {
                const result = await postAction(vote.dataset.voteUrl, {value});
                vote.querySelector('.vote__count').textContent = result.rating;
                for (const control of buttons) {
                    const active = Number(control.dataset.value) === result.value;
                    const color = Number(control.dataset.value) > 0 ? 'success' : 'danger';
                    control.setAttribute('aria-pressed', String(active));
                    control.classList.toggle('btn-' + color, active);
                    control.classList.toggle('btn-outline-' + color, !active);
                }
            } catch (error) {
                showError(feedback, error);
            } finally {
                buttons.forEach(control => { control.disabled = false; });
            }
        });
    }
}

const marks = [...document.querySelectorAll('[data-correct-url]')];
for (const mark of marks) {
    mark.addEventListener('change', async () => {
        const requested = mark.checked;
        const feedback = mark.closest('.form-check').querySelector('[data-feedback]');
        marks.forEach(input => { input.disabled = true; });
        feedback.textContent = '';
        try {
            const result = await postAction(mark.dataset.correctUrl, {correct: requested});
            for (const input of marks) {
                input.checked = Number(input.dataset.answerId) === result.correct_answer_id;
                input.closest('.answer-card').classList.toggle('answer-card--correct', input.checked);
            }
        } catch (error) {
            mark.checked = !requested;
            showError(feedback, error);
        } finally {
            marks.forEach(input => { input.disabled = false; });
        }
    });
}
