#
FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER ccg <ccgdevops@googlegroups.com>

# Determine build host
RUN netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}' > /data/build_host.txt

# squid proxy if available
ENV APT_PROXY_CONF /etc/apt/apt.conf.d/30proxy
RUN echo "HEAD /" | nc -q -1 -n -v  `cat /data/build_host.txt` 3128 | grep squid-deb-proxy \
  && (echo "Acquire::http::Proxy \"http://$(cat /data/build_host.txt):3128\";" > ${APT_PROXY_CONF}) \
  && (echo "Acquire::http::Proxy::ppa.launchpad.net DIRECT;" >> ${APT_PROXY_CONF}) \
  || echo "No squid-deb-proxy detected on docker host"

# devpi if available
ENV PIP_CONF /root/.config/pip
RUN echo -en "HEAD /\n\n\n" | nc -q 1 -v `cat /data/build_host.txt` 3141 | grep Devpi \
  && mkdir -p ${PIP_CONF} \
  && (echo "[global]" > ${PIP_CONF}/pip.conf) \
  && (echo "timeout = 60" >> ${PIP_CONF}/pip.conf) \
  && (echo "index-url = http://$(cat /data/build_host.txt):3141/root/pypi/" >> ${PIP_CONF}/pip.conf) \
  && (echo "trusted-host = $(cat /data/build_host.txt)" >> ${PIP_CONF}/pip.conf) \
  && (echo "no-cache-dir = true" >> ${PIP_CONF}/pip.conf) \
  && (echo "cache-dir = none" >> ${PIP_CONF}/pip.conf) \
  || echo "No devpi detected on docker host"

ENV DEBIAN_FRONTEND noninteractive

# Project specific deps
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  libldap2-dev \
  libpcre3 \
  libpcre3-dev \
  libpq-dev \
  libssl-dev \
  libxml2-dev \
  libxslt1-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN env --unset=DEBIAN_FRONTEND

ENV APP_RELEASE next_release

WORKDIR /app
RUN date > /data/build.txt && echo $APP_RELEASE >> /data/build.txt
RUN git clone --depth=1 --branch=$APP_RELEASE https://bitbucket.org/ccgmurdoch/yabi.git .

# install yabi
WORKDIR /app/yabiadmin
RUN pip install --process-dependency-links .

# install yabi shell
WORKDIR /app/yabish
RUN pip install --process-dependency-links .

# save docker-entry-point.sh prior to cleanup
RUN cp /app/docker-entrypoint.sh /
  && chmod +x /docker-entrypoint.sh

# save uwsgi config prior to cleanup
RUN mv /app/uwsgi / \
  && rm -rf /app \
  && mkdir /app \
  && mv /uwsgi /app/

# clean up any proxy settings during build
RUN rm -rf ${PIP_CONF} && rm -rf ${APT_PROXY_CONF}

EXPOSE 9100 9101
VOLUME ["/data"]

# Drop privileges, set home for ccg-user
USER ccg-user
ENV HOME /data
WORKDIR /data

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uwsgi"]
