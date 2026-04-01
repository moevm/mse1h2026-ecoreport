# EcoReport

Система автоматизированной генерации экологических отчетов.

## Основной стек технологий
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (SQLAlchemy + Alembic)
- **Message Broker:** RabbitMQ (FastStream)
- **Object Storage:** MinIO
- **UI:** Jinja2 + HTML/CSS/JS (Leaflet for maps)
- **Deployment:** Docker & Docker Compose

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <url_репозитория>
   cd mse1h2026-ecoreport
   ```

2. **Запустите проект через Docker Compose:**
   В корневой директории проекта выполните команду:
   ```bash
   docker-compose up -d --build
   ```
   Эта команда поднимет все необходимые сервисы (приложение, базу данных, брокер сообщений и хранилище файлов). 

3. **Миграции:**
   Миграции применяются автоматически при старте контейнера `app`.

## Проверка работоспособности

После успешного запуска проект будет доступен по адресу:
- **Веб-интерфейс:** [http://localhost:8080](http://localhost:8080)
- **Документация API (Swagger):** [http://localhost:8080/docs](http://localhost:8080/docs)
- **MinIO Console:** [http://localhost:9001](http://localhost:9001)
- **RabbitMQ Management:** [http://localhost:15672](http://localhost:15672)
