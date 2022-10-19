FROM python:3.10.7-slim-buster

ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y gcc netcat && apt-get -y dist-upgrade
RUN pip3 install pipenv==2022.7.4

COPY accounting/Pipfile .
COPY accounting/Pipfile.lock .

RUN pipenv install --deploy --clear --system --ignore-pipfile;

# Transfer code
WORKDIR /app

COPY accounting/docker-entrypoint.sh .
COPY common common
COPY accounting/accounting accounting

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]