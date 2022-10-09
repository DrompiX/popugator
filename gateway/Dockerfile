FROM python:3.10.7-slim-buster

ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y netcat && apt-get -y dist-upgrade
RUN pip3 install pipenv==2022.7.4

COPY gateway/Pipfile .
COPY gateway/Pipfile.lock .

RUN pipenv install --deploy --clear --system --ignore-pipfile;

# Transfer code
WORKDIR /app

COPY common common
COPY gateway/docker-entrypoint.sh .
COPY gateway/app gateway/app

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]