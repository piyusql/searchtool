#!/bin/bash

# some of the env needed
APP_NAME="${APP_NAME:-searchtool}"
APP_DIR=/piyusg/code/searchtool
STATIC_DIR=${APP_DIR}/static
MEDIA_DIR=${APP_DIR}/media

mkdir -p /piyusg/code /piyusg/service/logs

# run the db sync if need it will create tables
cd ${APP_DIR}
python manage.py migrate

echo "Configuring the weservice to run with uwsgi+nginx..."
cp ${APP_DIR}/conf/searchtool.conf /etc/nginx/conf.d/searchtool.conf
sed -i '1i daemon off;' /etc/nginx/nginx.conf

uwsgi --ini ${APP_DIR}/conf/uwsgi.ini &

# forward nginx request and error logs to docker log collector
ln -sf /dev/stdout /var/log/nginx/access.log
ln -sf /dev/stderr /var/log/nginx/error.log

exec nginx
