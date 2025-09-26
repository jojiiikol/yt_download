FROM python:3.13

WORKDIR /app

COPY . .

RUN apt-get update -y && apt-get upgrade -y
RUN apt install -y ffmpeg

RUN pip install -r requirements.txt

