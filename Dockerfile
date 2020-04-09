FROM python:3-alpine

RUN apk update && apk add --no-cache bash gcc python3-dev musl-dev git openssh-client

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apk update && apk add -qU openssh
RUN apk add openssl-dev python3-dev libffi-dev
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

COPY . /app

CMD ["python", "zbot.py"]
