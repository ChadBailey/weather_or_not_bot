FROM python:3-alpine

MAINTAINER Chad Bailey <chadbailey.me>

WORKDIR /weather_or_not
COPY ./src /weather_or_not

RUN apk add --no-cache gcc musl-dev libev-dev
RUN apk add --no-cache libressl-dev
RUN apk add --no-cache libffi-dev python-dev
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
