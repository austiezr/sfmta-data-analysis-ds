FROM ubuntu:20.04

MAINTAINER Austin Robinson "austinziech@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /app/requirements.txt

COPY application/schedule /app/schedule

COPY ./templates /app/templates

COPY application/app.py /app/app.py

WORKDIR /app

RUN pip3 install -r ./requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python3", "app.py" ]