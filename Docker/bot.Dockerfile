FROM python:3.11-slim

WORKDIR /app

COPY .. .

RUN apt update && pip install --no-cache-dir --upgrade -r requirements.txt --verbose

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
