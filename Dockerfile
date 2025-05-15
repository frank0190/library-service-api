FROM python:3.11.6-alpine3.18
LABEL maintainer="vadimkaliupa90@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user:my_user /app
RUN chmod -R 750 /app

USER my_user
