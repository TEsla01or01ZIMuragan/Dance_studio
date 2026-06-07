# Dance_studio

## CI/CD

CI/CD настроен через GitHub Actions в `.github/workflows/ci.yml`.

### CI

CI запускается при `push` в любую ветку, при `pull_request`, а также вручную через `workflow_dispatch`.

Проверки:

- установка Python 3.12;
- установка зависимостей из `requirements.txt`;
- компиляция Python-файлов из `app`;
- проверка импорта FastAPI-приложения.

### CD

CD запускается только после успешного CI и только при `push` в ветку `main`.

Деплой выполняется по SSH на сервер. Workflow:

1. заходит на сервер;
2. переходит в папку проекта;
3. подтягивает свежий код из `main`;
4. пересоздает/обновляет виртуальное окружение;
5. устанавливает зависимости;
6. перезапускает `systemd`-сервис `dance-studio`.

### GitHub Secrets

В репозитории GitHub нужно добавить секреты:

- `DEPLOY_HOST` - IP или домен сервера;
- `DEPLOY_USER` - пользователь на сервере;
- `DEPLOY_SSH_KEY` - приватный SSH-ключ для подключения;
- `DEPLOY_PORT` - SSH-порт, обычно `22`;
- `DEPLOY_PATH` - путь к проекту на сервере, например `/var/www/dance-studio`.

Секреты добавляются в GitHub: `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`.

### Сервер

На сервере проект должен быть склонирован в папку из `DEPLOY_PATH`, например:

```bash
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
cd /var/www
git clone <URL_РЕПОЗИТОРИЯ> dance-studio
```

Пример `systemd`-сервиса `/etc/systemd/system/dance-studio.service`.
В `User` укажите того же пользователя, который указан в секрете `DEPLOY_USER`.

```ini
[Unit]
Description=Dance Studio FastAPI app
After=network.target

[Service]
User=deploy
WorkingDirectory=/var/www/dance-studio
EnvironmentFile=/var/www/dance-studio/.env
ExecStart=/var/www/dance-studio/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

После создания сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dance-studio
sudo systemctl start dance-studio
```
