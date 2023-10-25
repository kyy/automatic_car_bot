# temp stage
FROM python:3.9-slim as builder

# рабочая директория
WORKDIR /app

# стандартный поток вывода без буферизации
ENV PYTHONDONTWRITEBYTECODE 1

# отключаем создание .pyc-файлов, чтобы избежать проблем с обновлением кода в контейнере
ENV PYTHONUNBUFFERED 1

# обновления
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# создаем и запускаем изолированную среду
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# копируем и устанавливаем зависимости
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# final stage
FROM python:3.9-slim

COPY --from=builder . .

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

# разрешение на чтение, запись и выполнение
#RUN chmod -R 777 .