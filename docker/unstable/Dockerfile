#
FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER https://bitbucket.org/ccgmurdoch/yabi/

ENV DEBIAN_FRONTEND noninteractive

# Project specific deps
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
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

ENV APP_RELEASE next_release

WORKDIR /app
RUN git clone --depth=1 --branch=$APP_RELEASE https://bitbucket.org/ccgmurdoch/yabi.git . \
  && cd /app/yabi \
  && pip install --process-dependency-links . \
  && cd /app/yabish \
  && pip install --process-dependency-links . \
  && cp /app/docker-entrypoint.sh / \
  && chmod +x /docker-entrypoint.sh \
  && mv /app/uwsgi / \
  && rm -rf /app \
  && mkdir /app \
  && mv /uwsgi /app/

# clean up any proxy settings during build
RUN rm -rf ${PIP_CONF_DIR} && rm -rf ${APT_PROXY_CONF}

EXPOSE 9100 9101
VOLUME ["/data"]

# Drop privileges, set home for ccg-user
USER ccg-user
ENV HOME /data
WORKDIR /data

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uwsgi"]
