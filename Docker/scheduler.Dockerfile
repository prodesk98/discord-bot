FROM python:3.11.7-slim

WORKDIR /app

COPY . .

ENV TZ=America/Sao_Paulo

RUN apt-get update && apt install -y build-essential && \
    apt-get install -y ffmpeg

RUN apt update && pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt --verbose

ENTRYPOINT ["python", "scheduler.py"]
