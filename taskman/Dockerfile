FROM python:3.10.7-slim-buster

ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y gcc netcat && apt-get -y dist-upgrade
RUN pip3 install pipenv==2022.7.4

COPY gateway/Pipfile .
COPY gateway/Pipfile.lock .

RUN pipenv install --deploy --clear --system --ignore-pipfile;

# Transfer code
WORKDIR /app

COPY common common
COPY taskman/docker-entrypoint.sh .
COPY taskman/taskman taskman

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]