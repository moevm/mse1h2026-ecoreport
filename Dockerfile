FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Настройка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY src .

# Копируем конфигурацию миграций
COPY alembic.ini .
COPY alembic ./alembic

# Создаем пользователя для безопасности
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

# Открываем порт
EXPOSE 8080

# Запускаем миграции и приложение
CMD ["sh", "-c", "alembic upgrade head && python main.py"]