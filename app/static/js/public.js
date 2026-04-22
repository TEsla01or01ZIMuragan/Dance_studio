const formatDateTime = (value) => {
  const date = new Date(value);
  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'long',
    timeStyle: 'short',
  }).format(date);
};

const emptyCard = (text) => `<article class="empty-card"><p>${text}</p></article>`;

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function renderEvents() {
  const upcomingContainer = document.getElementById('upcoming-events');
  const pastContainer = document.getElementById('past-events');
  if (!upcomingContainer || !pastContainer) return;

  try {
    const [upcoming, past] = await Promise.all([
      fetchJson('/api/events?scope=upcoming'),
      fetchJson('/api/events?scope=past'),
    ]);

    upcomingContainer.innerHTML = upcoming.length
      ? upcoming.map((event) => `
          <article class="content-card">
            <div class="content-card-meta">${formatDateTime(event.event_date)}</div>
            <h3>${event.title}</h3>
            <p>${event.description}</p>
            ${event.location ? `<div class="content-card-foot">${event.location}</div>` : ''}
          </article>
        `).join('')
      : emptyCard('Предстоящих ивентов пока нет.');

    pastContainer.innerHTML = past.length
      ? past.reverse().map((event) => `
          <article class="content-card content-card-muted">
            <div class="content-card-meta">${formatDateTime(event.event_date)}</div>
            <h3>${event.title}</h3>
            <p>${event.description}</p>
            ${event.location ? `<div class="content-card-foot">${event.location}</div>` : ''}
          </article>
        `).join('')
      : emptyCard('Прошедших ивентов пока нет.');
  } catch (error) {
    upcomingContainer.innerHTML = emptyCard('Не удалось загрузить ивенты. Проверьте backend и MongoDB.');
    pastContainer.innerHTML = '';
  }
}

async function renderSchedule() {
  const scheduleContainer = document.getElementById('schedule-list');
  if (!scheduleContainer) return;

  try {
    const items = await fetchJson('/api/schedule');
    scheduleContainer.innerHTML = items.length
      ? items.map((item) => `
          <article class="content-card schedule-card">
            <div class="content-card-meta">${item.weekday} · ${item.start_time} - ${item.end_time}</div>
            <h3>${item.title}</h3>
            <p>Преподаватель: ${item.teacher}</p>
            <div class="content-card-foot">
              ${item.hall ? `<span>Зал: ${item.hall}</span>` : ''}
              ${item.level ? `<span>Уровень: ${item.level}</span>` : ''}
            </div>
          </article>
        `).join('')
      : emptyCard('Расписание пока пустое.');
  } catch (error) {
    scheduleContainer.innerHTML = emptyCard('Не удалось загрузить расписание. Проверьте backend и MongoDB.');
  }
}

async function submitTrialRequest(form) {
  const message = form.querySelector('[data-trial-message]');
  const submitButton = form.querySelector('button[type="submit"]');
  const formData = new FormData(form);
  const payload = {
    name: formData.get('name'),
    phone: formData.get('phone'),
    direction: formData.get('direction') || null,
    comment: formData.get('comment') || null,
    source: formData.get('source') || document.title,
  };

  if (message) {
    message.textContent = '';
    message.classList.remove('trial-message-error');
  }
  if (submitButton) submitButton.disabled = true;

  try {
    await fetchJson('/api/trial-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    form.reset();
    if (message) message.textContent = 'Заявка отправлена. Мы скоро свяжемся с вами.';
  } catch (error) {
    if (message) {
      message.textContent = 'Не удалось отправить заявку. Проверьте backend и MongoDB.';
      message.classList.add('trial-message-error');
    }
  } finally {
    if (submitButton) submitButton.disabled = false;
  }
}

document.querySelectorAll('[data-trial-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    submitTrialRequest(form);
  });
});

renderEvents();
renderSchedule();
