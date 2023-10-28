FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential

WORKDIR /app
COPY src /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN flask db init; exit 0; flask db migrate; exit 0; flask db upgrade; exit 0

EXPOSE 8080

CMD ["python3", "app.py"]
