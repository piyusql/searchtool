#!/bin/bash

# DATABASE specific variables from env

APP_NAME="${APP_NAME:-searchtool}"

DB_NAME="${DB_NAME:-searchtool}"
DB_USER="${DB_USER:-searchtool}"
DB_PASSWORD="${DB_PASSWORD:-searchtool}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
MEMCACHED="${MEMCACHED:-memcached:11211}"

mkdir -p /piyusg/code /piyusg/service/logs

APP_DIR=/piyusg/code/searchtool
STATIC_DIR=${APP_DIR}/static
MEDIA_DIR=${APP_DIR}/media

echo "Configuring the weservice to run with uwsgi+nginx..."
cp ${APP_DIR}/conf/searchtool.conf /etc/nginx/conf.d/searchtool.conf
sed -i '1i daemon off;' /etc/nginx/nginx.conf

uwsgi --ini ${APP_DIR}/conf/uwsgi.ini &

# forward nginx request and error logs to docker log collector
ln -sf /dev/stdout /var/log/nginx/access.log
ln -sf /dev/stderr /var/log/nginx/error.log

exec nginx
