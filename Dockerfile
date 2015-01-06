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

# snippet from postgres dockerfile
# grab gosu for easy step-down from root
RUN gpg --keyserver pgp.mit.edu --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4
RUN apt-get update && apt-get install -y curl \
        && curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture)" \
        && curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture).asc" \
        && gpg --verify /usr/local/bin/gosu.asc \
        && rm /usr/local/bin/gosu.asc \
        && chmod +x /usr/local/bin/gosu

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN env --unset=DEBIAN_FRONTEND

RUN addgroup celery
RUN adduser --disabled-password --home /app --no-create-home --system -q --ingroup celery celery

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ADD yabiadmin/setup.py /app/yabiadmin/
WORKDIR /app/yabiadmin

# Install only dependencies first to use the build cache more efficiently
# This will be redone only if setup.py changes
RUN INSTALL_ONLY_DEPENDENCIES=True pip install --process-dependency-links .
# Python deps not in setup.py
RUN pip install psycopg2==2.5.4

COPY . /app
WORKDIR /app/yabiadmin
RUN pip install --process-dependency-links --no-deps -e .

EXPOSE 8000 8001 9000 9001
VOLUME ["/app"]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]
