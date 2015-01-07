#
FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER ccg <ccgdevops@googlegroups.com>

ENV DEBIAN_FRONTEND noninteractive

# Project specific deps
RUN apt-get update && apt-get install -y \
  libldap2-dev \
  libpcre3 \
  libpcre3-dev \
  libpq-dev \
  libssl-dev \
  libxml2-dev \
  libxslt1-dev

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN env --unset=DEBIAN_FRONTEND

RUN addgroup ccg-user
RUN adduser --disabled-password --home /data --no-create-home --system -q --ingroup ccg-user ccg-user
RUN mkdir /data && chown ccg-user:ccg-user /data

COPY yabiadmin/setup.py /app/yabiadmin/setup.py
WORKDIR /app/yabiadmin

# Install only dependencies first to use the build cache more efficiently
# This will be redone only if setup.py changes
RUN INSTALL_ONLY_DEPENDENCIES=True pip install --process-dependency-links .
# Python deps not in setup.py
RUN pip install psycopg2==2.5.4

COPY . /app
RUN pip install --process-dependency-links --no-deps -e .

WORKDIR /app/yabish
RUN pip install --process-dependency-links -e .

EXPOSE 8000 9000 9001 9100 9101
VOLUME ["/app", "/data"]

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

USER ccg-user
ENV HOME /data
WORKDIR /data

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]
