#
FROM muccg/yabi:docker1.9
MAINTAINER https://github.com/muccg/yabi/

ARG PIP_OPTS="--no-cache-dir"

USER root

COPY krb5.conf /etc/krb5.conf

# install python deps
COPY yabi/*requirements.txt /app/yabi/
COPY yabish/*requirements.txt /app/yabish/
WORKDIR /app

RUN /env/bin/pip freeze
RUN /env/bin/pip ${PIP_OPTS} uninstall -y yabish
RUN /env/bin/pip ${PIP_OPTS} uninstall -y yabi
RUN /env/bin/pip ${PIP_OPTS} install --upgrade -r yabi/requirements.txt
RUN /env/bin/pip ${PIP_OPTS} install --upgrade -r yabish/requirements.txt

# Copy code and install the app
COPY . /app
RUN /env/bin/pip ${PIP_OPTS} install -e yabi
RUN /env/bin/pip ${PIP_OPTS} install -e yabish

EXPOSE 8000 9000 9001 9100 9101
VOLUME ["/app", "/data"]

# Allow celery to run as root for dev
ENV C_FORCE_ROOT=1
ENV HOME /data
WORKDIR /data

# entrypoint shell script that by default starts runserver
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["runserver"]
