FROM python

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y
RUN apt install -y ffmpeg

COPY . .

RUN pip install -r requirements.txt
RUN playwright install firefox

