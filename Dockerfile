FROM python:3.14-alpine

WORKDIR /workspace

EXPOSE 80

COPY ./requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN addgroup -S appgroup \
    && adduser -S -G appgroup appuser \
    && chown -R appuser:appgroup /workspace
USER appuser

CMD ["fastapi", "run", "app/main.py", "--port", "80"]