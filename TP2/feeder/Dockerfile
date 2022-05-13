FROM python:3.9.7-slim
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /
COPY feeder /
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]
