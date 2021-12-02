FROM python:3.8.0

ENV PROJECT_ROOT /app
RUN mkdir $PROJECT_ROOT

COPY . $PROJECT_ROOT
WORKDIR $PROJECT_ROOT

RUN apt-get update && apt-get install graphviz-dev -y && apt-get install graphviz -y
RUN pip install -r requirements.txt
