#
FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER https://bitbucket.org/ccgmurdoch/yabi/

ENV DEBIAN_FRONTEND noninteractive

# Project specific deps
RUN apt-get update && apt-get install -y --no-install-recommends \
  libpcre3 \
  libpcre3-dev \
  libpq-dev \
  libssl-dev \
  libxml2-dev \
  libxslt1-dev \
  krb5-config \
  krb5-user \
  libkrb5-dev \
  libssl-dev \
  libsasl2-dev \
  libldap2-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN env --unset=DEBIAN_FRONTEND

COPY krb5.conf /etc/krb5.conf

# install python deps
WORKDIR /app
COPY yabi/*requirements.txt /app/yabi/
COPY yabish/*requirements.txt /app/yabish/
RUN pip install -r yabish/requirements.txt
RUN pip install -r yabi/requirements.txt

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copy code and install the app itself
COPY . /app
RUN pip install -e yabi
RUN pip install -e yabish

EXPOSE 8000 9000 9001 9100 9101
VOLUME ["/app", "/data"]

# Allow celery to run as root for dev
ENV C_FORCE_ROOT=1
ENV HOME /data
WORKDIR /data

# entrypoint shell script that by default starts runserver
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]
