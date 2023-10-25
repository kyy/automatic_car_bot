# temp stage
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN pip install -r requirements.txt


# final stage
FROM python:3.9-slim

COPY --from=builder . .

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"