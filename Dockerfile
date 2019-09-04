FROM python:3-alpine

MAINTAINER Chad Bailey <chadbailey.me>

WORKDIR /weather_or_not
COPY ./src /weather_or_not

RUN apk add libressl-dev
RUN apk add --no-cache gcc musl-dev libev-dev libssl-dev 
RUN apk add --no-cache libffi-dev python-dev
RUN apk add --no-cache build-essential
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
