FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor

RUN useradd --no-create-home nginx

RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache

EXPOSE 8080

COPY server-conf/nginx.conf /etc/nginx/
COPY server-conf/uwsgi.ini /etc/uwsgi/
COPY server-conf/supervisord.conf /etc/

COPY . /api
WORKDIR /api
RUN pip install -r requirements.txt
CMD ["/usr/local/bin/supervisord"]