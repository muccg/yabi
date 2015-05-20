#
FROM muccg/python-base:ubuntu14.04-2.7
MAINTAINER ccg <ccgdevops@googlegroups.com>

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

# Deps for tests
RUN pip install \
  lettuce \
  lettuce_webdriver \
  nose \
  selenium

# Install dependencies only (not the app itself) to use the build cache more efficiently
# This will be redone only if setup.py changes
# INSTALL_ONLY_DEPENDENCIES stops the app installing inside setup.py (pip --deps-only ??)
COPY yabi/setup.py /app/yabi/setup.py
WORKDIR /app/yabi
RUN INSTALL_ONLY_DEPENDENCIES=True pip install --process-dependency-links .

# Copy code and install the app
COPY . /app
RUN pip install --process-dependency-links --no-deps -e .

# Install yabish
WORKDIR /app/yabish
RUN pip install --process-dependency-links -e .

# now that we have installed everything globally purge /app
# /app gets added as a volume at run time
WORKDIR /app
RUN rm -rf ..?* .[!.]* *

EXPOSE 8000 9000 9001 9100 9101
VOLUME ["/app", "/data"]

COPY krb5.conf /etc/krb5.conf

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Drop privileges, set home for ccg-user
USER ccg-user
ENV HOME /data
WORKDIR /data

# entrypoint shell script that by default starts runserver
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]
