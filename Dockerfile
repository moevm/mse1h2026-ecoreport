FROM python:3.14-alpine


WORKDIR /src/app

COPY ./requirements.txt /src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /src/app

RUN adduser -D appuser && chown -R appuser:appuser /src

USER appuser

EXPOSE 80
ENV PYTHONPATH=/src

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]