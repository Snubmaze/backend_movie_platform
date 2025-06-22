FROM postgres:15

# install the distro package that contains pg_cron
RUN apt-get update \
 && apt-get install -y postgresql-15-cron \
 && rm -rf /var/lib/apt/lists/*
