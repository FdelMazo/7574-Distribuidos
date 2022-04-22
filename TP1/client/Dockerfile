FROM python:3.9.7-slim
ENV PYTHONUNBUFFERED 1
ENV TZ "America/Argentina/Buenos_Aires"
COPY client /
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]
