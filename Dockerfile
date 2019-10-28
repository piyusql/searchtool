# This docker file is generated for serving a searchtool test application
# @Author: Piyus Gupta
# @Date  : Oct, 26th 2019

FROM centos:7.6.1810

MAINTAINER piyusgupta01@gmail.com

ADD py3-installer.sh /

RUN yum install -y epel-release && \
    yum install -y wget gcc gcc-c++ make \
        nginx uwsgi-plugin-common \
        openssl-devel openldap-devel postgresql-devel bzip2-devel libffi-devel && \
	chmod a+x py3-installer.sh && \
        bash -x py3-installer.sh && \
    yum clean all

ADD requirements.txt /

RUN pip3.7 install -U pip && pip3 install -r requirements.txt

ADD . /piyusg/code/searchtool

RUN chmod a+x /piyusg/code/searchtool/start.sh

EXPOSE 8000

CMD /piyusg/code/searchtool/start.sh
