FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y

RUN apt install -y ffmpeg

COPY . .

RUN pip install -r requirements.txt
RUN playwright install firefox

CMD ["bash", "-c", "python main.py"]

