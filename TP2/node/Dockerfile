FROM python:3.9.7-slim
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /
# One might argue that copying the whole node directory to each separate node is
# useless, as each node only consist of itself and the base_node file, instead of having
# to store every other node type

# One might be right.
COPY node /
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]
