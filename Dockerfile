FROM ubuntu:20.04 AS builder
RUN apt-get update -y && apt-get install -y python3 python3-pip
COPY . /app
RUN (cd /app && pip3 install -r requirements.txt)
EXPOSE 8080
ENTRYPOINT ["python3", "/app/main.py"]
