FROM python:3.14-alpine

WORKDIR /app

EXPOSE 80

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app

RUN useradd appuser && chown -R appuser /app
USER appuser

CMD ["fastapi", "run", "main.py", "--port", "80"]