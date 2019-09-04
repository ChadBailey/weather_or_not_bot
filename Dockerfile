FROM python:3-alpine

MAINTAINER Chad Bailey <chadbailey.me>

WORKDIR /weather_or_not
COPY ./src /weather_or_not

RUN apk add --no-cache gcc musl-dev libev-dev libssl-dev libffi-dev python-dev build-essential  
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
