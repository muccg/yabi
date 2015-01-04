FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER ccg <ccgdevops@googlegroups.com>

ENV DEBIAN_FRONTEND noninteractive

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

ADD . /app
WORKDIR /app/yabiadmin

RUN pip install --process-dependency-links .
RUN pip install psycopg2==2.5.4

EXPOSE 8000 8001 9000 9001

ENTRYPOINT ["/usr/local/bin/uwsgi"]
CMD ["/app/uwsgi/docker.ini"]
