CREATE DATABASE gateway;
CREATE DATABASE taskman;

\c gateway;

CREATE TYPE SYSTEM_ROLE AS ENUM ('admin', 'manager', 'accountant', 'worker');

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    public_id     TEXT NOT NULL UNIQUE,
    role          SYSTEM_ROLE
);

\c taskman;

CREATE TYPE SYSTEM_ROLE AS ENUM ('admin', 'manager', 'accountant', 'worker');

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    public_id     TEXT NOT NULL UNIQUE,
    role          SYSTEM_ROLE
);

CREATE TYPE TASK_STATUS AS ENUM ('open', 'done');

CREATE TABLE tasks (
    id            SERIAL PRIMARY KEY,
    public_id     TEXT NOT NULL UNIQUE,
    assignee_id   TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TASK_STATUS
);

ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE gateway TO postgres;
GRANT ALL PRIVILEGES ON DATABASE taskman TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
