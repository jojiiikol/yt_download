FROM python

WORKDIR /app

COPY . .

RUN apt-get update -y && apt-get upgrade -y
RUN apt install -y ffmpeg


RUN pip install -r requirements.txt
RUN playwright install firefox

