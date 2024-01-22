FROM python:3.11.7-slim

WORKDIR /app

COPY .. .

RUN apt-get update && apt install -y build-essential && \
    apt-get install -y ffmpeg

RUN apt update && pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt --verbose

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
