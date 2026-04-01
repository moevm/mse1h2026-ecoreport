FROM python:3.12.13-alpine3.23

# Устанавливаем рабочую директорию
WORKDIR /app

# Настройка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    build-base

# Копируем requirements.txt и устанавливаем зависимости
COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

# Копируем исходный код приложения
COPY src ./src

# Копируем конфигурацию миграций
COPY alembic.ini .
COPY alembic ./alembic

# Создаем пользователя
RUN addgroup -S appgroup \
    && adduser -S -G appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

# Сообщаем порт
EXPOSE 8080

# Запускаем миграции и приложение
CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]