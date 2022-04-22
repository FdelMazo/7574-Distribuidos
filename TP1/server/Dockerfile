FROM python:3.9.7-slim
ENV PYTHONUNBUFFERED 1
ENV TZ "America/Argentina/Buenos_Aires"
COPY server /
ENTRYPOINT ["python3", "./main.py"]
