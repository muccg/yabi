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

# create user so we can drop priviliges for entrypoint
RUN addgroup --gid 1000 ccg-user
RUN adduser --disabled-password --home /data --no-create-home --system -q --uid 1000 --ingroup ccg-user ccg-user
RUN mkdir /data && chown ccg-user:ccg-user /data

# Install dependencies only (not the app itself) to use the build cache more efficiently
# This will be redone only if setup.py changes
# INSTALL_ONLY_DEPENDENCIES stops the app installing inside setup.py (pip --deps-only ??)
COPY yabiadmin/setup.py /app/yabiadmin/setup.py
WORKDIR /app/yabiadmin
RUN INSTALL_ONLY_DEPENDENCIES=True pip install --process-dependency-links .

# Copy code and install the app
COPY . /app
RUN pip install --process-dependency-links --no-deps -e .

# Install yabish
WORKDIR /app/yabish
RUN pip install --process-dependency-links -e .

EXPOSE 8000 9000 9001 9100 9101
VOLUME ["/app", "/data"]

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Drop privileges, set home for ccg-user
USER ccg-user
ENV HOME /data
WORKDIR /data

# entrypoint shell script that by default starts runserver
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]
