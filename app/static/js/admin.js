const loginScreen = document.getElementById('login-screen');
const adminScreen = document.getElementById('admin-screen');
const loginForm = document.getElementById('login-form');
const loginMessage = document.getElementById('login-message');
const logoutBtn = document.getElementById('logout-btn');
const eventForm = document.getElementById('event-form');
const scheduleForm = document.getElementById('schedule-form');
const eventsList = document.getElementById('admin-events');
const scheduleList = document.getElementById('admin-schedule');
const trialRequestsList = document.getElementById('admin-trial-requests');

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[char]));

const jsonRequest = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
};

const setAuthState = (isAuthenticated) => {
  loginScreen.classList.toggle('hidden', isAuthenticated);
  adminScreen.classList.toggle('hidden', !isAuthenticated);
};

const fillEventForm = (item) => {
  eventForm.elements.id.value = item.id;
  eventForm.title.value = item.title;
  eventForm.description.value = item.description;
  eventForm.event_date.value = item.event_date.slice(0, 16);
  eventForm.location.value = item.location || '';
  eventForm.image.value = item.image || '';
};

const fillScheduleForm = (item) => {
  scheduleForm.elements.id.value = item.id;
  scheduleForm.title.value = item.title;
  scheduleForm.teacher.value = item.teacher;
  scheduleForm.weekday.value = item.weekday;
  scheduleForm.start_time.value = item.start_time;
  scheduleForm.end_time.value = item.end_time;
  scheduleForm.hall.value = item.hall || '';
  scheduleForm.level.value = item.level || '';
};

const resetForm = (form) => {
  form.reset();
  if (form.elements.id) {
    form.elements.id.value = '';
  }
};

async function loadEvents() {
  const items = await jsonRequest('/api/events');
  eventsList.innerHTML = items.length ? items.map((item) => `
    <article class="admin-list-item">
      <div>
        <strong>${item.title}</strong>
        <p>${item.description}</p>
        <span>${new Date(item.event_date).toLocaleString('ru-RU')} ${item.location ? '· ' + item.location : ''}</span>
      </div>
      <div class="admin-list-actions">
        <button type="button" data-edit-event="${item.id}">Редактировать</button>
        <button type="button" data-delete-event="${item.id}">Удалить</button>
      </div>
    </article>
  `).join('') : '<article class="empty-card"><p>Ивентов пока нет.</p></article>';

  eventsList.querySelectorAll('[data-edit-event]').forEach((button) => {
    button.addEventListener('click', () => {
      const item = items.find((entry) => entry.id === button.dataset.editEvent);
      if (item) fillEventForm(item);
    });
  });

  eventsList.querySelectorAll('[data-delete-event]').forEach((button) => {
    button.addEventListener('click', async () => {
      await jsonRequest(`/api/events/${button.dataset.deleteEvent}`, { method: 'DELETE' });
      await loadEvents();
    });
  });
}

async function loadSchedule() {
  const items = await jsonRequest('/api/schedule');
  scheduleList.innerHTML = items.length ? items.map((item) => `
    <article class="admin-list-item">
      <div>
        <strong>${item.title}</strong>
        <p>${item.weekday}, ${item.start_time} - ${item.end_time}</p>
        <span>${item.teacher}${item.hall ? ' · ' + item.hall : ''}${item.level ? ' · ' + item.level : ''}</span>
      </div>
      <div class="admin-list-actions">
        <button type="button" data-edit-schedule="${item.id}">Редактировать</button>
        <button type="button" data-delete-schedule="${item.id}">Удалить</button>
      </div>
    </article>
  `).join('') : '<article class="empty-card"><p>Расписание пока пустое.</p></article>';

  scheduleList.querySelectorAll('[data-edit-schedule]').forEach((button) => {
    button.addEventListener('click', () => {
      const item = items.find((entry) => entry.id === button.dataset.editSchedule);
      if (item) fillScheduleForm(item);
    });
  });

  scheduleList.querySelectorAll('[data-delete-schedule]').forEach((button) => {
    button.addEventListener('click', async () => {
      await jsonRequest(`/api/schedule/${button.dataset.deleteSchedule}`, { method: 'DELETE' });
      await loadSchedule();
    });
  });
}

async function loadTrialRequests() {
  const items = await jsonRequest('/api/trial-requests');
  trialRequestsList.innerHTML = items.length ? items.map((item) => `
    <article class="admin-list-item">
      <div>
        <strong>${escapeHtml(item.name)}</strong>
        <p>${escapeHtml(item.phone)}${item.direction ? ' · ' + escapeHtml(item.direction) : ''}</p>
        <span>${new Date(item.created_at).toLocaleString('ru-RU')}${item.source ? ' · ' + escapeHtml(item.source) : ''}</span>
        ${item.comment ? `<p>${escapeHtml(item.comment)}</p>` : ''}
      </div>
      <div class="admin-list-actions">
        <button type="button" data-delete-trial-request="${item.id}">Удалить</button>
      </div>
    </article>
  `).join('') : '<article class="empty-card"><p>Заявок пока нет.</p></article>';

  trialRequestsList.querySelectorAll('[data-delete-trial-request]').forEach((button) => {
    button.addEventListener('click', async () => {
      await jsonRequest(`/api/trial-requests/${button.dataset.deleteTrialRequest}`, { method: 'DELETE' });
      await loadTrialRequests();
    });
  });
}

async function bootstrap() {
  try {
    await jsonRequest('/api/auth/me');
    setAuthState(true);
    await Promise.all([loadEvents(), loadSchedule(), loadTrialRequests()]);
  } catch (error) {
    setAuthState(false);
  }
}

loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginMessage.textContent = '';
  const formData = new FormData(loginForm);

  try {
    await jsonRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: formData.get('username'),
        password: formData.get('password'),
      }),
    });
    setAuthState(true);
    resetForm(loginForm);
    await Promise.all([loadEvents(), loadSchedule(), loadTrialRequests()]);
  } catch (error) {
    loginMessage.textContent = error.message;
  }
});

logoutBtn?.addEventListener('click', async () => {
  await jsonRequest('/api/auth/logout', { method: 'POST' });
  setAuthState(false);
});

eventForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(eventForm);
  const id = formData.get('id');
  const payload = {
    title: formData.get('title'),
    description: formData.get('description'),
    event_date: new Date(formData.get('event_date')).toISOString(),
    location: formData.get('location') || null,
    image: formData.get('image') || null,
  };

  await jsonRequest(id ? `/api/events/${id}` : '/api/events', {
    method: id ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  });

  resetForm(eventForm);
  await loadEvents();
});

scheduleForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(scheduleForm);
  const id = formData.get('id');
  const payload = {
    title: formData.get('title'),
    teacher: formData.get('teacher'),
    weekday: formData.get('weekday'),
    start_time: formData.get('start_time'),
    end_time: formData.get('end_time'),
    hall: formData.get('hall') || null,
    level: formData.get('level') || null,
  };

  await jsonRequest(id ? `/api/schedule/${id}` : '/api/schedule', {
    method: id ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  });

  resetForm(scheduleForm);
  await loadSchedule();
});

document.getElementById('event-reset')?.addEventListener('click', () => resetForm(eventForm));
document.getElementById('schedule-reset')?.addEventListener('click', () => resetForm(scheduleForm));

bootstrap();
