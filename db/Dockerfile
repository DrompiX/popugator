FROM postgres:13
COPY sql/* /docker-entrypoint-initdb.d/
RUN chown postgres:postgres /var/log/postgresql/