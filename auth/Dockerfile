FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential default-libmysqlclient-dev pkg-config

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN flask db init; exit 0
RUN flask db upgrade; exit 0
RUN flask db migrate; exit 0

EXPOSE 5000

CMD ["python3", "app.py"]
